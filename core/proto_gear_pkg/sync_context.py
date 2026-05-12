"""
Agent Context generator and sync.

Builds AGENT_CONTEXT.md (the auto-loaded skim every agent reads at session
start) and mirrors its content into host config files (CLAUDE.md,
.cursorrules, .windsurfrules, .github/copilot-instructions.md) inside a
managed BEGIN/END region. Content outside the managed region is preserved.
"""

import re
from pathlib import Path
from typing import Dict, List, Tuple
from datetime import datetime

from . import __version__


BEGIN_MARKER = "<!-- proto-gear:agent-context begin -->"
END_MARKER = "<!-- proto-gear:agent-context end -->"

HOST_FILES = [
    "CLAUDE.md",
    ".cursorrules",
    ".windsurfrules",
    ".github/copilot-instructions.md",
]

# (filename, purpose, read-when)
CORE_FILES: List[Tuple[str, str, str]] = [
    ("AGENTS.md", "Agent orchestration, roles, pre-flight checklist",
     "First session or unclear on process"),
    ("PROJECT_STATUS.md", "Current sprint, active tickets, project state",
     "Every session before starting work"),
    ("PROJECT_SPECIFICATIONS.md", "Project planning doc — source for architecture",
     "Starting features or design work (if exists)"),
    ("PROJECT_ARCHITECTURE.md", "Project-specific architecture (agent-extracted)",
     "Design decisions (if exists)"),
    ("BRANCHING.md", "Git workflow, branch naming, commit format",
     "Before any git operations"),
    ("TESTING.md", "TDD patterns, test pyramid, coverage targets",
     "When writing tests"),
    (".proto-gear/INDEX.md", "Capability catalog (full reference)",
     "When the skim below is insufficient"),
]

CRITICAL_RULES = [
    "NEVER commit directly to `main` or `development` — always branch from `development`",
    "Run `pg status` before starting work to see active tickets and current sprint",
    "Use `pg ticket create \"title\" --type feature` to register new work",
    "Use `pg ticket update ID --status IN_PROGRESS` when starting a ticket",
]

CLI_COMMANDS: List[Tuple[str, str]] = [
    ("pg status", "Current project state — version, sprint, active tickets"),
    ("pg ticket create/update/list", "Manage tickets in PROJECT_STATUS.md"),
    ("pg capabilities list [--type skill|workflow|command]", "Browse installed capabilities"),
    ("pg capabilities show <name>", "Show full details of a capability"),
    ("pg capabilities tree <name>", "Show dependency tree of a capability"),
    ("pg agent list", "List configured custom agents (if any)"),
    ("pg sync-context", "Regenerate Agent Context in all host files"),
    ("pg help", "Full CLI help"),
]


# ---------- builders ----------

def _load_capabilities(proto_gear_dir: Path) -> dict:
    """Return Dict[cap_id, CapabilityMetadata]; empty on missing dir or load error."""
    if not proto_gear_dir.exists():
        return {}
    try:
        from .capability_metadata import load_all_capabilities
        return load_all_capabilities(proto_gear_dir)
    except Exception:
        return {}


def _build_reference_index(project_dir: Path) -> str:
    rows = ["| File | Purpose | Read When |", "|------|---------|-----------|"]
    for filename, purpose, when in CORE_FILES:
        present = (project_dir / filename).exists()
        marker = "" if present else " *(not present)*"
        rows.append(f"| `{filename}`{marker} | {purpose} | {when} |")
    return "\n".join(rows)


def _cap_type(cap) -> str:
    return cap.type.value if hasattr(cap.type, "value") else str(cap.type)


def _build_capabilities_skim(capabilities: dict) -> str:
    if not capabilities:
        return ("_No capabilities installed. Run `pg init --with-capabilities` "
                "to add them, or check `.proto-gear/`._")

    by_type: Dict[str, list] = {"skill": [], "workflow": [], "command": []}
    for cap_id, cap in capabilities.items():
        t = _cap_type(cap)
        if t in by_type:
            by_type[t].append((cap_id, cap))

    type_labels = {
        "skill": "**Skills** — apply to any task",
        "workflow": "**Workflows** — multi-step processes",
        "command": "**Commands** — slash-command-style actions",
    }

    sections = []
    for t, label in type_labels.items():
        items = sorted(by_type[t])
        if not items:
            continue
        sections.append(f"\n### {label}\n")
        for cap_id, cap in items:
            triggers = []
            if cap.relevance and cap.relevance.triggers:
                triggers = cap.relevance.triggers[:4]
            trigger_str = f" · _triggers:_ {', '.join(triggers)}" if triggers else ""
            sections.append(f"- `{cap_id}` — {cap.description}{trigger_str}")

    return "\n".join(sections).strip() or "_No capabilities loaded._"


def _build_trigger_map(capabilities: dict) -> str:
    if not capabilities:
        return "_No triggers — install capabilities to enable trigger routing._"

    rows = []
    for cap_id, cap in sorted(capabilities.items()):
        if not cap.relevance or not cap.relevance.triggers:
            continue
        rows.append((cap_id, cap.relevance.triggers))

    if not rows:
        return "_No triggers declared in installed capability metadata._"

    lines = ["| If user says... | Load |", "|-----------------|------|"]
    for cap_id, triggers in rows:
        trig_str = ", ".join(f"`{t}`" for t in triggers[:6])
        lines.append(f"| {trig_str} | `{cap_id}` |")
    return "\n".join(lines)


def _build_critical_rules() -> str:
    return "\n".join(f"- {r}" for r in CRITICAL_RULES)


def _build_cli_commands() -> str:
    return "\n".join(f"- `{cmd}` — {desc}" for cmd, desc in CLI_COMMANDS)


def _read_project_status(project_dir: Path) -> Dict[str, str]:
    info = {
        "project_type": "Unknown",
        "version": "n/a",
        "last_release": "n/a",
    }
    status_file = project_dir / "PROJECT_STATUS.md"
    if not status_file.exists():
        return info
    try:
        text = status_file.read_text(encoding="utf-8")
    except Exception:
        return info

    for key, target in [
        ("project_type", "project_type"),
        ("protogear_version", "version"),
        ("release_date", "last_release"),
    ]:
        m = re.search(rf'{key}:\s*"?([^"\n]+?)"?\s*$', text, re.MULTILINE)
        if m:
            info[target] = m.group(1).strip().strip('"')
    return info


def _build_project_meta(project_dir: Path, capabilities: dict) -> str:
    info = _read_project_status(project_dir)
    counts = {"skill": 0, "workflow": 0, "command": 0}
    for cap in capabilities.values():
        t = _cap_type(cap)
        if t in counts:
            counts[t] += 1

    project_name = project_dir.name or project_dir.resolve().name
    return "\n".join([
        f"- **Project**: {project_name}",
        f"- **Tech / type**: {info['project_type']}",
        f"- **Proto Gear version**: {info['version']}",
        f"- **Last release**: {info['last_release']}",
        f"- **Capabilities installed**: "
        f"{counts['skill']} skills, {counts['workflow']} workflows, {counts['command']} commands",
        f"- **Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
    ])


# ---------- generation + sync ----------

def generate_agent_context(project_dir: Path) -> str:
    """Render the full AGENT_CONTEXT.md content from current project state."""
    capabilities = _load_capabilities(project_dir / ".proto-gear")

    template_file = Path(__file__).parent / "AGENT_CONTEXT.template.md"
    template = template_file.read_text(encoding="utf-8")

    project_name = project_dir.name or project_dir.resolve().name

    replacements = {
        "{{PROJECT_NAME}}": project_name,
        "{{REFERENCE_INDEX}}": _build_reference_index(project_dir),
        "{{CAPABILITIES_SKIM}}": _build_capabilities_skim(capabilities),
        "{{TRIGGER_MAP}}": _build_trigger_map(capabilities),
        "{{CRITICAL_RULES}}": _build_critical_rules(),
        "{{CLI_COMMANDS}}": _build_cli_commands(),
        "{{PROJECT_META}}": _build_project_meta(project_dir, capabilities),
    }
    for k, v in replacements.items():
        template = template.replace(k, v)
    return template


def _extract_managed_block(content: str) -> str:
    """Return BEGIN..END (inclusive), or empty string if missing."""
    pattern = re.compile(
        re.escape(BEGIN_MARKER) + r".*?" + re.escape(END_MARKER),
        re.DOTALL,
    )
    m = pattern.search(content)
    return m.group(0) if m else ""


def _update_host_file(path: Path, managed_block: str, dry_run: bool = False) -> str:
    """
    Insert or replace the managed block in a host file. Unmanaged content
    is preserved. Returns one of: 'created', 'updated', 'unchanged',
    'would_create', 'would_update'.
    """
    pattern = re.compile(
        re.escape(BEGIN_MARKER) + r".*?" + re.escape(END_MARKER),
        re.DOTALL,
    )

    if path.exists():
        existing = path.read_text(encoding="utf-8")
        if pattern.search(existing):
            new_content = pattern.sub(managed_block, existing)
        else:
            new_content = managed_block + "\n\n" + existing

        if new_content == existing:
            return "unchanged"
        if dry_run:
            return "would_update"
        path.write_text(new_content, encoding="utf-8")
        return "updated"
    else:
        if dry_run:
            return "would_create"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(managed_block + "\n", encoding="utf-8")
        return "created"


def sync_context(project_dir: Path, dry_run: bool = False) -> Dict[str, str]:
    """
    Regenerate AGENT_CONTEXT.md and mirror its managed block into all
    known host config files. Returns a {relative_path: action} map.
    """
    content = generate_agent_context(project_dir)
    managed_block = _extract_managed_block(content)
    if not managed_block:
        return {"error": "AGENT_CONTEXT template is missing BEGIN/END markers"}

    results: Dict[str, str] = {}

    # 1. Canonical AGENT_CONTEXT.md
    canon = project_dir / "AGENT_CONTEXT.md"
    if canon.exists():
        existing = canon.read_text(encoding="utf-8")
        if existing == content:
            results["AGENT_CONTEXT.md"] = "unchanged"
        elif dry_run:
            results["AGENT_CONTEXT.md"] = "would_update"
        else:
            canon.write_text(content, encoding="utf-8")
            results["AGENT_CONTEXT.md"] = "updated"
    else:
        if dry_run:
            results["AGENT_CONTEXT.md"] = "would_create"
        else:
            canon.write_text(content, encoding="utf-8")
            results["AGENT_CONTEXT.md"] = "created"

    # 2. Host config files (mirror managed block only)
    for hf in HOST_FILES:
        path = project_dir / hf
        results[hf] = _update_host_file(path, managed_block, dry_run=dry_run)

    return results
