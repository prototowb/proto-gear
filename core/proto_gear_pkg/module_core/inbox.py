"""Supervision inbox — "what needs a human right now?" (Phase D).

`pg pipeline` shows the *declared* approval surface; `pg trace <ticket>` and
`pg release <label>` follow one change or one release through it. This is the
complementary cockpit: a single cross-discipline queue of every change that is
**sitting at a pending human gate** — the supervisor's actionable to-do list.

Model (a single pass over state surfaces, no per-id checklist):

* Take every **required** supervision gate whose clearer must be a human
  (``authority != "auto"`` — a machine gate is not a human inbox item), from
  :func:`pipeline.collect_supervision_gates`. A gate belongs to exactly one
  discipline.
* Scan that discipline's declared ``state_surface`` and, for each row, read the
  cell that evidences the gate — its named ``evidence`` column when the gate
  declares one (so a discipline carrying several gates evidences each
  independently), else the generic Signed-off/Approved-by cell.
* A row is **pending** for that gate when it is still in flight (not a terminal
  / already-shipped row — see :func:`_is_terminal`) and the evidence cell is
  present-but-unsigned (empty or literally "pending"). Reusing
  :func:`trace._approval_state`, this is the ``pending`` state ``gate_checklist``
  reports, minus historical rows — and keyed by the row itself, so a downstream
  row carrying both an ``ID`` and a ``Ref`` is counted once, not twice.

Generic by construction: a new discipline's required human gates join the inbox
with zero code here, exactly like the pipeline and the doctor gate audit. Read
only — it parses the surfaces and reports; it executes and signs nothing.
"""

from pathlib import Path
from typing import Dict, List, Optional

from . import trace as _trace
from . import pipeline as _pipeline

_TITLE_HEADERS = {"title"}

# A row whose Stage/Status is one of these has moved *past* active supervision:
# a still-empty evidence cell on it is historical, not an actionable "awaiting
# sign-off" (e.g. a long-shipped completed ticket that predates an evidence
# column). Deliberately excludes in-flight-then-signable stages like ``verified``
# (qa: tests passed, human sign-off still pending) — those must stay in the inbox.
# Soft convention, matched case-insensitively, like the header roles in ``trace``.
_TERMINAL_STAGES = {
    "done",
    "completed",
    "complete",
    "closed",
    "cancelled",
    "canceled",
    "wontfix",
    "won't fix",
    "archived",
}
# A filled completion-date column (the completed-tickets convention) is the other
# "this is history, not a queue item" signal — completed-ticket tables carry no
# Stage column, so the terminal-stage set alone can't catch them.
_DONE_DATE_HEADERS = {"completed", "done"}


def _is_terminal(row: Dict[str, str]) -> bool:
    """Has this row moved past active supervision (done/shipped/closed)?

    True when its Stage/Status is a terminal value, or it carries a filled
    completion-date column. Such rows are historical: the inbox skips them so a
    long-closed change with an unsigned legacy evidence cell isn't mistaken for
    work awaiting a human right now.
    """
    stage = (_trace._role_value(row, _trace._STAGE_HEADERS) or "").strip().lower()
    if stage in _TERMINAL_STAGES:
        return True
    return bool((_trace._role_value(row, _DONE_DATE_HEADERS) or "").strip())


def _row_evidence_cell(row: Dict[str, str], evidence_spec: str) -> Optional[str]:
    """The cell under the header matching ``evidence_spec`` (case-insensitive
    substring), or ``None`` when no header matches (the column is absent here —
    ``untracked``, never pending). Mirrors :func:`trace._column_cells` selection.
    """
    spec = evidence_spec.strip().lower()
    if not spec:
        return None
    for header, cell in row.items():
        if spec in header.strip().lower():
            return cell
    return None


def _is_pending(row: Dict[str, str], gate: dict) -> bool:
    """Is ``row`` awaiting this gate's human sign-off?

    A gate with a named ``evidence`` column is judged against that column; a
    comparison predicate (ADR-002 §2) is pending until the declared claim holds.
    A gate without one falls back to the generic approval cell. In every case
    'pending' means: the evidence exists as a column/cell but is not yet cleared.
    """
    if gate.get("evidence"):
        cell = _row_evidence_cell(row, gate["evidence"])
        if cell is None:
            return False  # column absent → untracked, not the inbox's concern
        predicate = gate.get("evidence_predicate", "non-empty")
        if predicate == "non-empty":
            return _trace._approval_state(cell) == "pending"
        # Comparison predicate: pending until the measurement satisfies the claim.
        return not _trace._predicate_holds(
            cell, predicate, gate.get("evidence_value", "")
        )
    cell = _trace._approval_cell(row)
    if cell is None:
        return False  # no approval column on this surface → nothing to await
    return _trace._approval_state(cell) == "pending"


def collect_inbox(project_dir: Path, modules_root: Optional[Path] = None) -> List[dict]:
    """Every required human gate currently pending, across all disciplines.

    Returns a list of item dicts, ordered along the path to production (by the
    guarded action, then discipline, then change id):

      * ``change`` — the row's own id (or its ``Ref`` when it has none).
      * ``ref`` — the upstream correlation id the row carries, if any.
      * ``discipline`` / ``gate`` / ``action`` (the guarded ``before`` action).
      * ``scope`` (``change`` / ``release``), ``authority`` (the rung the gate
        demands), ``approver``, ``workflow`` (namespaced id).
      * ``surface`` / ``stage`` / ``title`` — context for the supervisor.

    Empty list means nothing is awaiting a human — the clean cockpit.
    """
    from .module_manifest import discover_modules

    gates_by_disc: Dict[str, List[dict]] = {}
    for g in _pipeline.collect_supervision_gates(modules_root):
        if not g["required"] or g.get("authority") == "auto":
            continue
        gates_by_disc.setdefault(g["discipline"], []).append(g)

    items: List[dict] = []
    for manifest in discover_modules(modules_root):
        gates = gates_by_disc.get(manifest.module)
        if not gates:
            continue
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
                if _is_terminal(row):
                    continue  # historical/closed — not awaiting a human now
                row_id = (_trace._role_value(row, _trace._ID_HEADERS) or "").strip()
                ref = (_trace._role_value(row, _trace._REF_HEADERS) or "").strip()
                stage = (_trace._role_value(row, _trace._STAGE_HEADERS) or "").strip()
                title = (_trace._role_value(row, _TITLE_HEADERS) or "").strip()
                for g in gates:
                    if not _is_pending(row, g):
                        continue
                    items.append(
                        {
                            "change": row_id or ref or "(no id)",
                            "ref": ref,
                            "discipline": manifest.module,
                            "gate": g["gate"],
                            "action": g["before"],
                            "scope": g.get("scope", "change"),
                            "authority": g.get("authority", "human"),
                            "approver": g.get("approver", ""),
                            "workflow": g["workflow"],
                            "surface": surface,
                            "stage": stage,
                            "title": title,
                        }
                    )

    items.sort(
        key=lambda it: (
            _pipeline._action_sort_key(it["action"]),
            it["discipline"],
            it["change"],
        )
    )
    return items
