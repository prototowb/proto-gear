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
    from .module_manifest import discover_modules

    hits: List[dict] = []
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
                approval = _approval_cell(row)
                hits.append(
                    {
                        "discipline": manifest.module,
                        "surface": surface,
                        "id": row_id,
                        "ref": _role_value(row, _REF_HEADERS) or "",
                        "stage": (_role_value(row, _STAGE_HEADERS) or "").strip(),
                        "approval": approval,
                        "approval_state": _approval_state(approval),
                    }
                )

    hits.sort(key=lambda h: (h["discipline"] != "engineering", h["discipline"]))
    return hits
