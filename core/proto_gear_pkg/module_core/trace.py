"""Cross-discipline change trace — Phase D-2 (ADR-001).

`pg pipeline` (Phase D) shows the declared *approval surface* — which gates guard
which action, across disciplines. This traces a *specific change* through it: an
engineering ticket id is the correlation key, carried downstream by a ``Ref``
column each discipline's state surface may add. Given a ticket id, we read every
discipline's declared ``state_surface`` and return the rows that reference it —
the change's journey (engineering ticket → qa sign-off → prod deploy) and where
each stands.

Generic by construction: a discipline joins tracing simply by carrying a ``Ref``
column in its state surface — no code here changes. Read-only; parses the
surfaces, executes nothing.
"""

import re
from pathlib import Path
from typing import Dict, List, Optional

# Header roles, matched case-insensitively. Soft convention, shared across
# disciplines — a new surface opts in by naming its columns the same way.
_ID_HEADERS = {"id"}
_REF_HEADERS = {"ref", "refs", "ticket", "tickets"}
_STAGE_HEADERS = {"stage", "status"}


def _split_row(line: str) -> List[str]:
    return [c.strip() for c in line.strip().strip("|").split("|")]


def _is_separator(line: str) -> bool:
    body = line.strip().strip("|")
    if not body:
        return False
    return all(set(c.strip()) <= set("-: ") and "-" in c for c in body.split("|"))


def parse_markdown_tables(text: str) -> List[List[Dict[str, str]]]:
    """Parse every GfM pipe-table in ``text`` into a list of row dicts.

    Each table becomes a ``List[{header: cell}]``; the header row and the
    ``|---|`` separator are consumed, not returned. Robust to surrounding prose.
    """
    tables: List[List[Dict[str, str]]] = []
    lines = text.splitlines()
    i, n = 0, len(lines)
    while i < n:
        line = lines[i].strip()
        if line.startswith("|") and i + 1 < n and _is_separator(lines[i + 1]):
            headers = _split_row(line)
            rows: List[Dict[str, str]] = []
            j = i + 2
            while j < n and lines[j].strip().startswith("|"):
                if not _is_separator(lines[j]):
                    cells = _split_row(lines[j])
                    rows.append(
                        {
                            headers[k]: (cells[k] if k < len(cells) else "")
                            for k in range(len(headers))
                        }
                    )
                j += 1
            tables.append(rows)
            i = j
        else:
            i += 1
    return tables


def _role_value(row: Dict[str, str], roles: set) -> Optional[str]:
    for header, cell in row.items():
        if header.strip().lower() in roles:
            return cell
    return None


def _approval_cell(row: Dict[str, str]) -> Optional[str]:
    for header, cell in row.items():
        h = header.strip().lower()
        if "signed off" in h or "approved by" in h or h == "approver":
            return cell
    return None


def _refs(cell: Optional[str]) -> List[str]:
    if not cell:
        return []
    return [t.strip() for t in cell.split(",") if t.strip()]


def _approval_state(cell: Optional[str]) -> Optional[str]:
    """Interpret a Signed-off/Approved-by cell: 'cleared', 'pending', or None."""
    if cell is None:
        return None
    val = cell.strip().strip("_*").strip()
    if not val or "pending" in val.lower():
        return "pending"
    return "cleared"


def _iter_change_rows(
    change_id: str, project_dir: Path, modules_root: Optional[Path] = None
):
    """Yield ``(discipline, surface, row)`` for every state-surface row that
    references ``change_id`` — by its own ``ID`` or via a ``Ref`` column.

    ``row`` is the full header→cell dict, so callers can read arbitrary columns
    (e.g. a gate-specific evidence column), not just the detected approval cell.
    """
    from .module_manifest import discover_modules

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

        for table in parse_markdown_tables(text):
            for row in table:
                row_id = (_role_value(row, _ID_HEADERS) or "").strip()
                refs = _refs(_role_value(row, _REF_HEADERS))
                if row_id != change_id and change_id not in refs:
                    continue
                yield manifest.module, surface, row


def trace_change(
    change_id: str, project_dir: Path, modules_root: Optional[Path] = None
) -> List[dict]:
    """Return every state-surface row across disciplines referencing ``change_id``.

    A row matches when its ``ID`` equals ``change_id`` (the change itself, in the
    engineering surface) or a ``Ref`` column lists it (downstream disciplines).
    Each hit: ``discipline``, ``surface``, ``id``, ``ref``, ``stage``,
    ``approval`` (raw cell or None), ``approval_state`` ('cleared'/'pending'/None).
    Ordered engineering-first, then disciplines alphabetically.
    """
    hits: List[dict] = []
    for discipline, surface, row in _iter_change_rows(
        change_id, project_dir, modules_root
    ):
        approval = _approval_cell(row)
        hits.append(
            {
                "discipline": discipline,
                "surface": surface,
                "id": (_role_value(row, _ID_HEADERS) or "").strip(),
                "ref": _role_value(row, _REF_HEADERS) or "",
                "stage": (_role_value(row, _STAGE_HEADERS) or "").strip(),
                "approval": approval,
                "approval_state": _approval_state(approval),
            }
        )

    hits.sort(key=lambda h: (h["discipline"] != "engineering", h["discipline"]))
    return hits


def _column_cells(rows: List[Dict[str, str]], column_spec: str) -> List[str]:
    """Cells under any header matching ``column_spec`` (case-insensitive substring).

    An empty list means the column is absent from every row — distinct from a
    present-but-empty cell (which is returned as ``""``).
    """
    spec = column_spec.strip().lower()
    cells: List[str] = []
    for row in rows:
        for header, cell in row.items():
            if spec and spec in header.strip().lower():
                cells.append(cell)
    return cells


def _best_state(states) -> Optional[str]:
    """The strongest approval state in ``states`` (cleared > pending > None)."""
    best: Optional[str] = None
    for st in states:
        if _EVIDENCE_RANK[st] >= _EVIDENCE_RANK[best]:
            best = st
    return best


# Approval evidence strength, so a discipline with several rows for one change
# is judged by its best (a cleared row wins over a still-pending one).
_EVIDENCE_RANK = {"cleared": 2, "pending": 1, None: 0}

_NUMBER_RE = re.compile(r"-?\d+(?:\.\d+)?")


def _agent_identities(modules_root: Optional[Path] = None) -> set:
    """Every bundled agent identity a signer cell might carry, lowercased.

    The signer-identity convention (ADR-002, action item 3): an agent signs a
    state-surface cell with its agent id — the filename stem of its config
    (``code-review-agent``), optionally module-namespaced
    (``qa/qa-release-agent``). Cells may also mark an agent signer explicitly
    with an ``agent:`` prefix (checked by :func:`_is_agent_signer`, not listed
    here). Anything else in a sign-off cell is presumed a human name.
    """
    from . import module_host

    ids = set()
    for module, agents_dir in module_host.iter_agent_sources(modules_root):
        for f in sorted(agents_dir.glob("*.yaml")):
            ids.add(f.stem.lower())
            if module:
                ids.add(f"{module}/{f.stem}".lower())
    return ids


def _is_agent_signer(cell: str, agent_ids: set) -> bool:
    """Is this sign-off cell an *agent* identity rather than a human name?"""
    norm = cell.strip().strip("_*").strip().lower()
    return norm.startswith("agent:") or norm in agent_ids


def _predicate_holds(cell: str, predicate: str, value: str) -> bool:
    """Does the evidence ``cell`` satisfy a comparison ``predicate``?

    The declarative vocabulary of ADR-002 §2 (``GATE_EVIDENCE_PREDICATES``,
    minus ``non-empty`` which keeps the graded cleared/pending semantics in the
    caller). Pure string/number comparison — reads a markdown cell, executes
    nothing. Unknown predicates never hold: the doctor flags them, and an
    unverifiable claim must not clear a gate.
    """
    norm = cell.strip().strip("_*").strip()
    if predicate == "equals":
        return norm.lower() == value.strip().lower()
    if predicate == "at-least":
        m = _NUMBER_RE.search(norm)
        if not m:
            return False
        try:
            return float(m.group()) >= float(value)
        except ValueError:
            return False
    return False


def gate_checklist(
    change_id: str, project_dir: Path, modules_root: Optional[Path] = None
) -> List[dict]:
    """Fold the pipeline gate chain (Phase D) into the change trace (Phase D-2).

    Answers "which required approvals does this change still lack?" — not just the
    rows it has. Walks every supervision gate on the path to production (from
    :func:`pipeline.build_pipeline`) and marks each against the change's trace
    evidence in that gate's discipline:

      * ``cleared``     — the discipline's row for this change has its
                          Signed-off/Approved-by column filled.
      * ``pending``     — the change has reached the discipline, approval pending.
      * ``outstanding`` — the change has not reached this discipline yet (no row).
      * ``untracked``   — the change is in the discipline, but its state surface
                          records no approval column for this gate (e.g.
                          engineering's PROJECT_STATUS). Distinguished from
                          ``outstanding`` so a DONE ticket isn't misread as "not
                          started"; still not counted as cleared.

    A gate that declares an ``evidence`` column (workflow metadata) is matched
    against **that specific column** in its discipline's rows — so a discipline
    carrying several gates (engineering) can evidence each one independently
    instead of collapsing to a single approval cell. The gate's evidence
    *predicate* (ADR-002 §2) decides what the cell must satisfy: ``non-empty``
    (default — filled and not 'pending') keeps the historical behaviour, while
    ``equals``/``at-least`` clear only when the declared comparison holds
    (:func:`_predicate_holds`). A gate with no ``evidence`` keeps the
    discipline-level generic approval-column behaviour.

    Each entry: ``action``, ``gate``, ``discipline``, ``required``, ``status``,
    ``scope`` (``"change"`` per-ticket or ``"release"`` per-release — a
    release-scoped gate is cleared once for the whole release, so evaluating it
    against a single ticket id is only meaningful when the id *is* the release
    label; ``pg release`` does exactly that), ``authority`` (the minimum
    authority the gate demands of its clearer — ADR-002), ``signed_by`` (the
    signature cells that cleared it) and ``authority_ok`` (ADR-002 action item
    3: ``True`` — cleared with sufficient authority; ``False`` — cleared, but
    every signer is an agent identity while the gate demands a human;
    ``None`` — not cleared, or cleared without a signature to judge). Order
    follows the pipeline.
    """
    from . import pipeline

    rows_by_disc: Dict[str, List[Dict[str, str]]] = {}
    for disc, _surface, row in _iter_change_rows(change_id, project_dir, modules_root):
        rows_by_disc.setdefault(disc, []).append(row)
    reached = set(rows_by_disc)

    # Discipline-level generic evidence — the fallback for gates that don't name
    # their own evidence column (works for single-gate disciplines: qa/devops/…).
    disc_evidence: Dict[str, Optional[str]] = {
        disc: _best_state(_approval_state(_approval_cell(row)) for row in rows)
        for disc, rows in rows_by_disc.items()
    }

    checklist: List[dict] = []
    agent_ids: Optional[set] = None  # resolved lazily, only if a signer is judged
    for stage in pipeline.build_pipeline(modules_root):
        for g in stage["gates"]:
            disc = g["discipline"]
            # signers: the signature-style cells that actually cleared the gate
            # (non-empty evidence or the generic approval fallback). Comparison
            # predicates clear on a measurement, not a signature — no signers.
            signers: List[str] = []
            if disc not in reached:
                status = "outstanding"  # change hasn't reached this discipline
            elif g.get("evidence"):
                cells = _column_cells(rows_by_disc[disc], g["evidence"])
                predicate = g.get("evidence_predicate", "non-empty")
                if not cells:
                    status = "untracked"  # gate's evidence column absent here
                elif predicate == "non-empty":
                    signers = [c for c in cells if _approval_state(c) == "cleared"]
                    status = "cleared" if signers else "pending"
                else:
                    # Comparison predicate (ADR-002 §2): the gate clears iff some
                    # row's evidence cell satisfies the declared claim; a filled
                    # cell that fails the claim is still pending, never cleared.
                    status = (
                        "cleared"
                        if any(
                            _predicate_holds(c, predicate, g.get("evidence_value", ""))
                            for c in cells
                        )
                        else "pending"
                    )
            else:
                state = disc_evidence.get(disc)
                if state == "cleared":
                    status = "cleared"
                    for row in rows_by_disc[disc]:
                        cell = _approval_cell(row)
                        if cell is not None and _approval_state(cell) == "cleared":
                            signers.append(cell)
                elif state == "pending":
                    status = "pending"
                else:
                    status = "untracked"  # reached, but no approval evidence recorded

            # Authority sufficiency (ADR-002, action item 3): was a cleared gate
            # cleared by a signer of adequate authority? `auto` needs no signer;
            # human rungs need at least one signer that is not an agent identity.
            # A signature-less clear (comparison predicate) can't be judged: None.
            authority = g.get("authority", "human")
            if status != "cleared":
                authority_ok = None
            elif authority == "auto":
                authority_ok = True
            elif not signers:
                authority_ok = None  # cleared without a signature to judge
            else:
                if agent_ids is None:
                    agent_ids = _agent_identities(modules_root)
                authority_ok = any(not _is_agent_signer(s, agent_ids) for s in signers)

            checklist.append(
                {
                    "action": stage["action"],
                    "gate": g["gate"],
                    "discipline": disc,
                    "required": g["required"],
                    "status": status,
                    "scope": g.get("scope", "change"),
                    "authority": authority,
                    "signed_by": [s.strip().strip("_*").strip() for s in signers],
                    "authority_ok": authority_ok,
                }
            )
    return checklist
