"""Release trace — Phase D-4 (ADR-001).

`pg trace <ticket>` (Phase D-2/D-3) follows one change to production and reports
which required approvals it still lacks. A *release* bundles many tickets, and is
shippable only when **every** ticket in it has cleared **every** required gate on
the path to production. This aggregates the per-ticket gate checklists into one
release-level readiness verdict: which tickets belong to the release, and which
gates each still blocks on.

Three design points, all to stay honest rather than convenient:

* **Membership is read, not passed.** A ticket belongs to a release when its row
  in a discipline's state surface carries the release label in a release column
  (``PR/Commit`` / ``Release`` / ``Version``). Engineering owns the ticket list,
  so in practice that is ``PROJECT_STATUS.md`` — but the selection is by *column
  name*, not by discipline name, so it stays generic like the rest of trace.
* **Change- vs release-scoped gates.** Most gates are per-change: every ticket
  must clear them. But some (``release-approval``, ``announcement-approval``) are
  per-*release* — cleared once for the whole candidate, not per ticket. Those
  declare ``scope: release`` and are evaluated once, against the release label
  itself (which a ``Releases`` table records, keyed by the label) — reusing
  :func:`trace.gate_checklist` with the label as the id.
* **Unverifiable ≠ cleared.** A required gate whose discipline records no evidence
  column reads ``untracked``. We cannot verify it from data, so we neither count
  it as cleared (false confidence) nor as blocking (it would wedge every
  release). It is reported separately as *unverified*, and the verdict says so.

Generic by construction: the per-ticket verdict reuses
:func:`trace.gate_checklist`, so any discipline that joins the pipeline joins the
release roll-up too — no code here changes. Read-only.
"""

from pathlib import Path
from typing import List, Optional

from . import trace as _trace

# Columns that name the release/version a ticket shipped in, matched
# case-insensitively against exact header text. Deliberately excludes ``Target``
# (qa/devops use it for a *targeted* version, not release membership) and never
# substring-matches (``approver`` contains ``pr``), keeping selection precise.
_RELEASE_HEADERS = {
    "pr/commit",
    "pr / commit",
    "pr",
    "release",
    "version",
}

# A required gate in one of these states is definitively not cleared and blocks
# the release; ``untracked`` is unverifiable (reported, not blocking) and
# ``cleared`` passes.
_BLOCKING_STATES = {"pending", "outstanding"}


def find_release_tickets(
    release_id: str, project_dir: Path, modules_root: Optional[Path] = None
) -> List[str]:
    """Return the ticket ids that belong to ``release_id``.

    Scans every discipline's declared ``state_surface`` and collects the ``ID`` of
    each row whose release column (``PR/Commit`` / ``Release`` / ``Version``)
    references ``release_id`` (exact token match, comma-tolerant). Order is
    surface order, first occurrence wins; duplicates are dropped.
    """
    from .module_manifest import discover_modules

    tickets: List[str] = []
    seen = set()
    for manifest in discover_modules(modules_root):
        surface = manifest.state_surface
        if not surface:
            continue
        surface_path = Path(project_dir) / surface
        if not surface_path.is_file():
            continue
        try:
            text = surface_path.read_text(encoding="utf-8")
        except Exception:
            continue

        for table in _trace.parse_markdown_tables(text):
            for row in table:
                rel = _trace._role_value(row, _RELEASE_HEADERS)
                if release_id not in _trace._refs(rel):
                    continue
                tid = (_trace._role_value(row, _trace._ID_HEADERS) or "").strip()
                if tid and tid not in seen:
                    seen.add(tid)
                    tickets.append(tid)
    return tickets


def trace_release(
    release_id: str, project_dir: Path, modules_root: Optional[Path] = None
) -> dict:
    """Aggregate the release's gate checklists into one readiness verdict.

    Gates are evaluated at two scopes (see ``Gate.scope``):

      * **change-scoped** gates (``pr-review-approval``, ``qa-signoff``,
        ``prod-approval``, …) are checked **per ticket** — every member ticket
        (:func:`find_release_tickets`) must clear them.
      * **release-scoped** gates (``release-approval``, ``announcement-approval``)
        are cleared **once for the whole release** — evaluated against the
        release label itself (:func:`trace.gate_checklist` with the label as the
        id), which reads the Releases table keyed by that label.

    Each gate is classified ``cleared`` / ``blocking`` (pending or outstanding:
    definitively not cleared) / ``unverified`` (``untracked``: no evidence column
    recorded, so it can't be judged from data).

    Returns a dict:

      * ``release`` / ``ticket_count``.
      * ``tickets`` — per-ticket ``{ticket, gates, required_total, cleared,
                       blocking, unverified, ready}`` (change-scoped gates only).
      * ``release_gates`` — the release-scoped ``{cleared, blocking, unverified}``
                       evaluated once for the whole release.
      * ``ready`` — ``True`` iff ≥1 ticket was found, no ticket has a blocking
                       change-scoped gate, and no release-scoped gate is blocking.
                       Unverified gates never flip this to ``False`` but are
                       counted in ``unverified_total``.
      * ``unverified_total`` / ``blocking_total`` — across tickets *and* the
                       release-scoped gates.
      * ``authority_insufficient_total`` — cleared gates whose every signer is
                       an agent identity while the gate demands a human rung
                       (ADR-002 action item 3). Reported, never blocking.
    """

    def _classify(gates):
        return {
            "cleared": [g for g in gates if g["status"] == "cleared"],
            "blocking": [g for g in gates if g["status"] in _BLOCKING_STATES],
            "unverified": [g for g in gates if g["status"] == "untracked"],
            # ADR-002 action item 3: cleared, but every signer is an agent
            # identity while the gate demands a human rung. Reported (a signer
            # of insufficient authority is a supervision violation worth eyes),
            # not blocking — the verdict semantics stay unchanged.
            "insufficient": [g for g in gates if g.get("authority_ok") is False],
        }

    entries: List[dict] = []
    unverified_total = 0
    blocking_total = 0
    insufficient_total = 0
    for tid in find_release_tickets(release_id, project_dir, modules_root):
        checklist = _trace.gate_checklist(tid, project_dir, modules_root)
        # Per ticket, only the change-scoped required gates are that ticket's to
        # clear; release-scoped gates are handled once, below.
        required = [g for g in checklist if g["required"] and g["scope"] != "release"]
        c = _classify(required)
        unverified_total += len(c["unverified"])
        blocking_total += len(c["blocking"])
        insufficient_total += len(c["insufficient"])
        entries.append(
            {
                "ticket": tid,
                "gates": checklist,
                "required_total": len(required),
                "cleared": c["cleared"],
                "blocking": c["blocking"],
                "unverified": c["unverified"],
                "insufficient": c["insufficient"],
                "ready": not c["blocking"],
            }
        )

    # Release-scoped gates: evaluated once, against the release label itself.
    release_checklist = _trace.gate_checklist(release_id, project_dir, modules_root)
    release_required = [
        g for g in release_checklist if g["required"] and g["scope"] == "release"
    ]
    release_gates = _classify(release_required)
    unverified_total += len(release_gates["unverified"])
    blocking_total += len(release_gates["blocking"])
    insufficient_total += len(release_gates["insufficient"])

    ready = (
        bool(entries)
        and all(e["ready"] for e in entries)
        and not release_gates["blocking"]
    )
    return {
        "release": release_id,
        "ticket_count": len(entries),
        "tickets": entries,
        "release_gates": release_gates,
        "ready": ready,
        "unverified_total": unverified_total,
        "blocking_total": blocking_total,
        "authority_insufficient_total": insufficient_total,
    }
