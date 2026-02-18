"""
pg status and pg ticket command handlers.

Design:
  - PROJECT_STATUS.md is the single source of truth (no side-car state files)
  - All commands are non-interactive — safe for AI agents calling via shell
  - Pure stdlib — no new dependencies
  - stdout carries data (ticket IDs, JSON); stderr carries errors
  - Exit 0 on success, 1 on error
"""

import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

STATUS_FILE = "PROJECT_STATUS.md"
VALID_TYPES = {"feature", "bugfix", "hotfix", "task", "chore"}
VALID_STATUSES = {"PENDING", "IN_PROGRESS", "COMPLETED", "BLOCKED", "CANCELLED"}


# ─────────────────────────────────────────────────────────────────────────────
# File location
# ─────────────────────────────────────────────────────────────────────────────

def _find_status_file():
    # type: () -> Optional[Path]
    path = Path.cwd() / STATUS_FILE
    return path if path.is_file() else None


# ─────────────────────────────────────────────────────────────────────────────
# Parsing
# ─────────────────────────────────────────────────────────────────────────────

class ProjectState:
    """
    Parsed snapshot of PROJECT_STATUS.md.
    Constructed fresh from disk on every call — agents always see current state.
    """

    def __init__(self, path):
        # type: (Path) -> None
        self.path = path
        self.text = path.read_text(encoding="utf-8")
        self._parse()

    def _extract(self, key, default=""):
        # type: (str, str) -> str
        m = re.search(
            r"^" + re.escape(key) + r":\s*[\"']?([^\"'#\n]+?)[\"']?\s*$",
            self.text,
            re.MULTILINE,
        )
        return m.group(1).strip() if m else default

    def _parse(self):
        self.ticket_prefix = self._extract("ticket_prefix", "")
        try:
            self.last_ticket_id = int(self._extract("last_ticket_id", "0"))
        except ValueError:
            self.last_ticket_id = 0

        # If ticket_prefix not in YAML block, infer from existing ticket IDs
        if not self.ticket_prefix:
            m = re.search(r'\|\s*([A-Z][A-Z0-9]+)-(\d+)\s*\|', self.text)
            if m:
                self.ticket_prefix = m.group(1)
                # Also infer last_ticket_id from highest seen number
                nums = [int(n) for n in re.findall(
                    r'\|\s*' + re.escape(m.group(1)) + r'-(\d+)\s*\|', self.text)]
                if nums and self.last_ticket_id == 0:
                    self.last_ticket_id = max(nums)
            else:
                self.ticket_prefix = "TICKET"
        self.project_phase = self._extract("project_phase", "Development")
        self.current_sprint = self._extract("current_sprint", "1")
        self.sprint_type = self._extract("sprint_type", "feature_development")
        self.active = self._parse_table("Active Tickets")
        self.completed = self._parse_table("Completed Tickets")
        self.blocked = self._parse_table("Blocked Tickets")

    def _parse_table(self, section_name):
        # type: (str) -> List[Dict[str, str]]
        m = re.search(
            r"##[^\n]*" + re.escape(section_name) + r".*?\n(.*?)(?=\n##\s|\Z)",
            self.text,
            re.DOTALL,
        )
        if not m:
            return []

        header = None
        rows = []
        for line in m.group(1).splitlines():
            line = line.strip()
            if not line.startswith("|"):
                continue
            cells = [c.strip() for c in line.split("|")[1:-1]]
            if not cells:
                continue
            if header is None:
                header = cells
                continue
            if all(set(c) <= set("-: ") for c in cells):
                continue  # separator row
            if not cells[0] or cells[0].startswith("(") or cells[0].startswith("{{") or cells[0] == "-":
                continue  # placeholder / empty row
            if header and len(cells) >= len(header):
                rows.append(dict(zip(header, cells[: len(header)])))
        return rows


# ─────────────────────────────────────────────────────────────────────────────
# Mutation helpers — operate on raw text, return updated text
# ─────────────────────────────────────────────────────────────────────────────

def _set_last_ticket_id(text, new_id):
    # type: (str, int) -> str
    return re.sub(r"(last_ticket_id:\s*)\S+", r"\g<1>" + str(new_id), text)


def _find_insert_point(lines, section_name):
    # type: (List[str], str) -> Optional[int]
    """Return line index after which a new row should be inserted."""
    in_section = False
    sep_idx = None
    last_row_idx = None

    for i, line in enumerate(lines):
        s = line.strip()
        if re.match(r"##[^\n]*" + re.escape(section_name), s):
            in_section = True
            continue
        if in_section:
            if s.startswith("## "):
                break
            if s.startswith("|"):
                cells = [c.strip() for c in s.split("|")[1:-1]]
                if all(set(c) <= set("-: ") for c in cells if c):
                    sep_idx = i
                elif sep_idx is not None:
                    if cells and not cells[0].startswith("(") and not cells[0].startswith("{{"):
                        last_row_idx = i

    return last_row_idx if last_row_idx is not None else sep_idx


def _append_row(text, section_name, row):
    # type: (str, str, str) -> str
    lines = text.splitlines(keepends=True)
    idx = _find_insert_point(lines, section_name)
    if idx is None:
        return text
    lines.insert(idx + 1, row + "\n")
    return "".join(lines)


def _remove_active_row(text, ticket_id):
    # type: (str, str) -> Tuple[str, Optional[Dict[str, str]]]
    lines = text.splitlines(keepends=True)
    in_section = False
    header = None
    sep_seen = False
    removed = None

    for i, line in enumerate(lines):
        s = line.strip()
        if re.match(r"##[^\n]*Active Tickets", s):
            in_section = True
            continue
        if in_section:
            if s.startswith("## "):
                break
            if s.startswith("|"):
                cells = [c.strip() for c in s.split("|")[1:-1]]
                if header is None:
                    header = cells
                elif all(set(c) <= set("-: ") for c in cells if c):
                    sep_seen = True
                elif sep_seen and cells and cells[0] == ticket_id:
                    removed = dict(zip(header, cells[: len(header)])) if header else {}
                    lines[i] = ""
                    break

    return "".join(lines), removed


def _update_status_inline(text, ticket_id, new_status):
    # type: (str, str, str) -> str
    pattern = re.compile(
        r"(\|\s*" + re.escape(ticket_id) + r"\s*\|[^|]+\|[^|]+\|)\s*\S+\s*(\|)"
    )
    return pattern.sub(r"\g<1> " + new_status + r" \2", text)


def _write(path, text):
    # type: (Path, str) -> None
    path.write_text(text, encoding="utf-8")


# ─────────────────────────────────────────────────────────────────────────────
# Command handlers
# ─────────────────────────────────────────────────────────────────────────────

def cmd_status(args):
    # type: (...) -> int
    """pg status — summarise PROJECT_STATUS.md."""
    path = _find_status_file()
    if not path:
        print("Error: PROJECT_STATUS.md not found. Run 'pg init' first.", file=sys.stderr)
        return 1

    state = ProjectState(path)
    next_id = "{}-{:03d}".format(state.ticket_prefix, state.last_ticket_id + 1)

    if getattr(args, "json", False):
        print(json.dumps({
            "project_phase": state.project_phase,
            "current_sprint": state.current_sprint,
            "sprint_type": state.sprint_type,
            "ticket_prefix": state.ticket_prefix,
            "last_ticket_id": state.last_ticket_id,
            "next_ticket_id": next_id,
            "active": state.active,
            "completed_count": len(state.completed),
            "blocked": state.blocked,
        }, indent=2))
        return 0

    from .ui_helper import Colors
    print("\n{}=== Project Status ==={}".format(Colors.CYAN, Colors.ENDC))
    print("  Phase:   {}".format(state.project_phase))
    print("  Sprint:  {}  ({})".format(state.current_sprint, state.sprint_type))
    print("  Prefix:  {}".format(state.ticket_prefix))
    print("  Next ID: {}".format(next_id))
    print()

    if state.blocked:
        print("{}BLOCKED ({}){}".format(Colors.FAIL, len(state.blocked), Colors.ENDC))
        for t in state.blocked:
            print("  {}{}{}  {}".format(
                Colors.BOLD, t.get("ID", "?"), Colors.ENDC,
                t.get("Title", t.get("Blocker", "?"))))
        print()

    if state.active:
        print("{}ACTIVE ({}){}".format(Colors.CYAN, len(state.active), Colors.ENDC))
        for t in state.active:
            print("  {}{}{}  [{}]  {}".format(
                Colors.BOLD, t.get("ID", "?"), Colors.ENDC,
                t.get("Status", "?"), t.get("Title", "?")))
        print()
    else:
        print("{}No active tickets.{}\n".format(Colors.GRAY, Colors.ENDC))

    print("{}Completed: {}{}\n".format(Colors.GREEN, len(state.completed), Colors.ENDC))
    return 0


def cmd_ticket_create(args):
    # type: (...) -> int
    """
    pg ticket create "title" [--type TYPE] [--assignee NAME]

    Prints only the ticket ID to stdout for shell capture:
        ID=$(pg ticket create "Fix login" --type bugfix)
    """
    path = _find_status_file()
    if not path:
        print("Error: PROJECT_STATUS.md not found. Run 'pg init' first.", file=sys.stderr)
        return 1

    ticket_type = (getattr(args, "type", None) or "task").lower()
    if ticket_type not in VALID_TYPES:
        print(
            "Error: --type must be one of: {}".format(", ".join(sorted(VALID_TYPES))),
            file=sys.stderr,
        )
        return 1

    state = ProjectState(path)
    new_num = state.last_ticket_id + 1
    ticket_id = "{}-{:03d}".format(state.ticket_prefix, new_num)
    slug = re.sub(r"[^a-z0-9]+", "-", args.title.lower()).strip("-")[:40]
    branch = "{}/{}-{}".format(ticket_type, ticket_id.lower(), slug)
    assignee = getattr(args, "assignee", None) or ""

    row = "| {} | {} | {} | PENDING | {} | {} |".format(
        ticket_id, args.title, ticket_type, branch, assignee)

    text = _set_last_ticket_id(state.text, new_num)
    text = _append_row(text, "Active Tickets", row)
    _write(path, text)

    print(ticket_id)  # stdout only — clean for $(pg ticket create ...)
    return 0


def cmd_ticket_update(args):
    # type: (...) -> int
    """pg ticket update TICKET-ID --status STATUS"""
    path = _find_status_file()
    if not path:
        print("Error: PROJECT_STATUS.md not found. Run 'pg init' first.", file=sys.stderr)
        return 1

    new_status = args.status.upper()
    if new_status not in VALID_STATUSES:
        print(
            "Error: --status must be one of: {}".format(", ".join(sorted(VALID_STATUSES))),
            file=sys.stderr,
        )
        return 1

    ticket_id = args.ticket_id.upper()
    state = ProjectState(path)

    ticket = next((t for t in state.active if t.get("ID") == ticket_id), None)
    if not ticket:
        print(
            "Error: Ticket {} not found in Active Tickets.".format(ticket_id),
            file=sys.stderr,
        )
        return 1

    text = state.text
    if new_status == "COMPLETED":
        text, removed = _remove_active_row(text, ticket_id)
        if removed:
            today = datetime.now().strftime("%Y-%m-%d")
            comp_row = "| {} | {} | {} | |".format(
                ticket_id, removed.get("Title", ""), today)
            text = _append_row(text, "Completed Tickets", comp_row)
    else:
        text = _update_status_inline(text, ticket_id, new_status)

    _write(path, text)
    print("{} -> {}".format(ticket_id, new_status))
    return 0


def cmd_ticket_list(args):
    # type: (...) -> int
    """pg ticket list [--status STATUS] [--json]"""
    path = _find_status_file()
    if not path:
        print("Error: PROJECT_STATUS.md not found. Run 'pg init' first.", file=sys.stderr)
        return 1

    state = ProjectState(path)
    filter_status = (getattr(args, "status", None) or "").upper()

    if filter_status == "COMPLETED":
        tickets = state.completed
    elif filter_status:
        tickets = [t for t in state.active + state.blocked
                   if t.get("Status", "").upper() == filter_status]
    else:
        tickets = state.active + state.blocked

    if getattr(args, "json", False):
        print(json.dumps(tickets, indent=2))
        return 0

    if not tickets:
        print("No tickets found.")
        return 0

    from .ui_helper import Colors
    STATUS_COLORS = {
        "IN_PROGRESS": Colors.CYAN,
        "PENDING": Colors.GRAY,
        "BLOCKED": Colors.FAIL,
        "COMPLETED": Colors.GREEN,
    }
    for t in tickets:
        status = t.get("Status", "")
        color = STATUS_COLORS.get(status, Colors.ENDC)
        print("{}{}{}  {}{:<12}{}  {}".format(
            Colors.BOLD, t.get("ID", "?"), Colors.ENDC,
            color, status, Colors.ENDC,
            t.get("Title", "?")))

    return 0
