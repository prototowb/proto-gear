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

from .. import __version__

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
    (
        "AGENTS.md",
        "Agent orchestration, roles, pre-flight checklist",
        "First session or unclear on process",
    ),
    (
        "SESSION_HANDOFF.md",
        "Rolling session handoff — what just shipped, what's pending",
        "Start of every session — before anything else",
    ),
    (
        "PROJECT_STATUS.md",
        "Current sprint, active tickets, project state",
        "Every session before starting work",
    ),
    (
        "PROJECT_SPECIFICATIONS.md",
        "Project planning doc — source for architecture",
        "Starting features or design work (if exists)",
    ),
    (
        "PROJECT_ARCHITECTURE.md",
        "Project-specific architecture (agent-extracted)",
        "Design decisions (if exists)",
    ),
    (
        "BRANCHING.md",
        "Git workflow, branch naming, commit format",
        "Before any git operations",
    ),
    (
        "TESTING.md",
        "TDD patterns, test pyramid, coverage targets",
        "When writing tests",
    ),
    (
        ".proto-gear/INDEX.md",
        "Capability catalog (full reference)",
        "When the skim below is insufficient",
    ),
    (
        ".proto-gear/lessons/",
        "Accumulated agent-written lessons (corrections, confirmed approaches)",
        "When relevant; write one when you learn something worth keeping",
    ),
]

# Heading in PROJECT_SPECIFICATIONS.md whose bullets are project-specific
# boundaries. `pg init`'s planning intake writes them (see
# modules/engineering/init_planning.py) and _build_critical_rules folds them
# into the generated Critical Rules — so a boundary stated once at init (or
# added by hand later) steers every future session via the host mirrors.
BOUNDARIES_HEADING = "## Boundaries & Invariants"

CRITICAL_RULES = [
    "NEVER commit directly to `main` — it lands only via a reviewed PR",
    "`development` is open: commit to it directly when it helps; feature branch + PR is still the norm for substantial or shared work, not a requirement",
    "Run `pg status` before starting work to see active tickets and current sprint",
    'Use `pg ticket create "title" --type feature` to register new work',
    "Use `pg ticket update ID --status IN_PROGRESS` when starting a ticket",
]

# Long-run grounding (steering-plan Phase 4, item 8) — small, high-leverage lines
# straight from the Fable 5 guidance. They keep autonomous runs honest without
# re-teaching the model how to work.
WORKING_AGREEMENT = [
    "Audit progress claims against tool results — don't report something done, "
    "passing, or fixed without checking the actual output.",
    "When the user is describing a problem rather than requesting a change, "
    "report what you find and stop; don't jump straight to editing.",
    "Pause for input only on destructive/irreversible actions, a scope change, "
    "or a decision only the user can make — otherwise keep moving.",
]

CLI_COMMANDS: List[Tuple[str, str]] = [
    ("pg status", "Version, sprint, active tickets"),
    ("pg context [--regenerate]", "Print this Agent Context to stdout"),
    ('pg suggest "<task prose>" [--json]', "Match task prose to capabilities"),
    ("pg ticket create/update/list", "Manage tickets in PROJECT_STATUS.md"),
    (
        "pg capabilities list [--type ...] [--json]",
        "List capabilities (--json for agents)",
    ),
    ("pg capabilities show <name>", "Show a capability's details"),
    ("pg capabilities tree <name>", "Show a capability's dependency tree"),
    ("pg lessons [list|show <name>]", "Browse accumulated lessons"),
    ("pg agent list [--available]", "List configured + installable agents"),
    ("pg agent install <name>", "Install a bundled agent"),
    ("pg orchestration list [--json]", "Browse orchestration paradigms"),
    ("pg orchestration show <id>", "Show a paradigm's roles + model tiers"),
    ("pg module list/show [<name>]", "List/inspect department modules"),
    ("pg --module <name> init-surface", "Render a module's state surface"),
    ("pg pipeline [--json]", "Show the supervision pipeline"),
    ("pg trace <ticket-id> [--json]", "Trace a ticket across disciplines"),
    ("pg release <label> [--json]", "Aggregate a release's readiness verdict"),
    ("pg inbox [--json]", "Cross-discipline pending sign-offs"),
    ("pg sync-context", "Regenerate Agent Context + host files"),
    ("pg sync-indexes", "Regenerate capability INDEX.md files"),
    ("pg doctor [--fix] [--json]", "Audit for sync drift (--fix repairs)"),
    ("pg guard branch", "Fail on a protected branch (hooks/CI)"),
    ("pg hooks install", "Install the branch-guard pre-commit hook"),
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
        return (
            "_No capabilities installed. Run `pg init --with-capabilities` "
            "to add them, or check `.proto-gear/`._"
        )

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
            sections.append(f"- `{cap_id}` — {cap.description}")

    return "\n".join(sections).strip() or "_No capabilities loaded._"


def read_project_boundaries(project_dir: Path) -> List[str]:
    """Bullets under :data:`BOUNDARIES_HEADING` in PROJECT_SPECIFICATIONS.md.

    Returns the boundary lines (bullet markers stripped), or ``[]`` when the
    file, the section, or any bullets are absent. HTML-comment placeholder
    lines are not bullets and never match.
    """
    specs = project_dir / "PROJECT_SPECIFICATIONS.md"
    if not specs.exists():
        return []
    try:
        text = specs.read_text(encoding="utf-8")
    except Exception:
        return []

    boundaries: List[str] = []
    in_section = False
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("## "):
            in_section = stripped.lower() == BOUNDARIES_HEADING.lower()
            continue
        if in_section and stripped.startswith(("- ", "* ")):
            item = stripped[2:].strip()
            if item:
                boundaries.append(item)
    return boundaries


def _build_critical_rules(project_dir: Path) -> str:
    rules = list(CRITICAL_RULES)
    seen = {r.lower() for r in rules}
    for boundary in read_project_boundaries(project_dir):
        if boundary.lower() not in seen:
            rules.append(boundary)
            seen.add(boundary.lower())
    return "\n".join(f"- {r}" for r in rules)


def _build_working_agreement() -> str:
    return "\n".join(f"- {r}" for r in WORKING_AGREEMENT)


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
    return "\n".join(
        [
            f"- **Project**: {project_name}",
            f"- **Tech / type**: {info['project_type']}",
            f"- **Proto Gear version**: {info['version']}",
            f"- **Last release**: {info['last_release']}",
            f"- **Capabilities installed**: "
            f"{counts['skill']} skills, {counts['workflow']} workflows, {counts['command']} commands",
            f"- **Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        ]
    )


# ---------- generation + sync ----------


def generate_agent_context(project_dir: Path) -> str:
    """Render the full AGENT_CONTEXT.md content from current project state."""
    capabilities = _load_capabilities(project_dir / ".proto-gear")

    from ..paths import package_root

    template_file = package_root() / "AGENT_CONTEXT.template.md"
    template = template_file.read_text(encoding="utf-8")

    project_name = project_dir.name or project_dir.resolve().name

    replacements = {
        "{{PROJECT_NAME}}": project_name,
        "{{REFERENCE_INDEX}}": _build_reference_index(project_dir),
        "{{CAPABILITIES_SKIM}}": _build_capabilities_skim(capabilities),
        "{{CRITICAL_RULES}}": _build_critical_rules(project_dir),
        "{{WORKING_AGREEMENT}}": _build_working_agreement(),
        "{{CLI_COMMANDS}}": _build_cli_commands(),
        "{{PROJECT_META}}": _build_project_meta(project_dir, capabilities),
    }
    for k, v in replacements.items():
        template = template.replace(k, v)
    return template


# Soft budget for the generated agent-context block (the managed BEGIN..END
# region mirrored into every host file). Every line here is a per-session
# attention tax on every agent in every downstream project, so the block is
# kept lean; `doctor.check_agent_context_budget` warns (never errors) when it is
# exceeded. Calibrated for a fully-loaded project: the reference index, the
# working agreement, the rules and the CLI cheatsheet are near-fixed (~1000
# tokens); the capability skim scales with how many capabilities are installed
# (~25 tokens each) and is the real growth vector — the budget is a nudge to keep
# that list a skim, not a manual.
AGENT_CONTEXT_TOKEN_BUDGET = 1800


def estimate_tokens(text: str) -> int:
    """Rough, offline token estimate for a piece of text.

    Uses the standard ~4-chars-per-token English heuristic, floored at the
    word count so punctuation-dense markdown is never underestimated too far.
    Deliberately dependency-free and network-free so `pg doctor` stays hermetic
    — this is an estimate, not the exact `count_tokens` API figure.
    """
    return max(len(text) // 4, len(text.split()))


def managed_block(project_dir: Path) -> str:
    """Return only the generated BEGIN..END agent-context block for a project."""
    return _extract_managed_block(generate_agent_context(project_dir))


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
