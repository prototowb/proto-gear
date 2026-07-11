"""Release trace — Phase D-4 (ADR-001).

`pg trace <ticket>` (Phase D-2/D-3) follows one change to production and reports
which required approvals it still lacks. A *release* bundles many tickets, and is
shippable only when **every** ticket in it has cleared **every** required gate on
the path to production. This aggregates the per-ticket gate checklists into one
release-level readiness verdict: which tickets belong to the release, and which
gates each still blocks on.

Two design points, both to stay honest rather than convenient:

* **Membership is read, not passed.** A ticket belongs to a release when its row
  in a discipline's state surface carries the release label in a release column
  (``PR/Commit`` / ``Release`` / ``Version``). Engineering owns the ticket list,
  so in practice that is ``PROJECT_STATUS.md`` — but the selection is by *column
  name*, not by discipline name, so it stays generic like the rest of trace.
* **Unverifiable ≠ cleared.** A required gate whose discipline records no approval
  column (engineering's ``PROJECT_STATUS`` has none) reads ``untracked`` in the
  per-ticket checklist. We cannot verify it from data, so we neither count it as
  cleared (false confidence) nor as blocking (it would wedge every release). It
  is reported separately as *unverified*, and the verdict says so.

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
    """Aggregate the per-ticket gate checklists for ``release_id``.

    For every ticket in the release (:func:`find_release_tickets`) we compute its
    required-gate checklist (:func:`trace.gate_checklist`) and classify the gates:

      * ``cleared``   — approval recorded in the discipline's surface.
      * ``blocking``  — pending or outstanding: definitively not cleared.
      * ``unverified``— ``untracked``: the discipline records no approval column,
                        so the gate can't be evidenced from data.

    Returns a dict:

      * ``release``      — the label traced.
      * ``ticket_count`` — number of member tickets found.
      * ``tickets``      — per-ticket ``{ticket, gates, required_total,
                           cleared, blocking, unverified, ready}``.
      * ``ready``        — ``True`` iff at least one ticket was found and no ticket
                           has a blocking gate. Unverified gates do *not* flip this
                           to ``False`` (see module docstring) but are surfaced via
                           ``unverified_total`` so callers can caveat the verdict.
      * ``unverified_total`` — count of required gates across all tickets that are
                           unverifiable.
      * ``blocking_total``   — count of blocking required gates across all tickets.
    """
    entries: List[dict] = []
    unverified_total = 0
    blocking_total = 0
    for tid in find_release_tickets(release_id, project_dir, modules_root):
        checklist = _trace.gate_checklist(tid, project_dir, modules_root)
        required = [g for g in checklist if g["required"]]
        blocking = [g for g in required if g["status"] in _BLOCKING_STATES]
        unverified = [g for g in required if g["status"] == "untracked"]
        cleared = [g for g in required if g["status"] == "cleared"]
        unverified_total += len(unverified)
        blocking_total += len(blocking)
        entries.append(
            {
                "ticket": tid,
                "gates": checklist,
                "required_total": len(required),
                "cleared": cleared,
                "blocking": blocking,
                "unverified": unverified,
                "ready": not blocking,
            }
        )

    ready = bool(entries) and all(e["ready"] for e in entries)
    return {
        "release": release_id,
        "ticket_count": len(entries),
        "tickets": entries,
        "ready": ready,
        "unverified_total": unverified_total,
        "blocking_total": blocking_total,
    }
