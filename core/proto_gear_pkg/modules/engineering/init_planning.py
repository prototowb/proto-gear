"""Frontier-era init planning (PROTO-100 / ADR-004).

Pure helpers behind the fresh-``pg init`` state-elicitation intake. The old
wizard was a template configurator — it asked the operator to hand-pick files
and toggles a frontier model's harness can detect or default. This module
inverts that: *detect* the mechanical choices so the wizard can show a
confirmable plan instead of asking, and *render* the durable intent the
operator captures (project description, boundaries/invariants, house
conventions) into the artifacts init writes — the PROJECT_SPECIFICATIONS.md
stub and a seed lesson in ``.proto-gear/lessons/``.

No TTY, no questionary, no writes — every function here unit-tests directly.
The interactive surface lives in ``interactive_wizard.run_enhanced_wizard``;
the file writes live in ``proto_gear.setup_agent_framework_only``.
"""

from pathlib import Path
from typing import Dict, List, Optional, Tuple

# The specs-stub section heading that sync_context parses back into the
# generated Critical Rules. Imported from module_core so writer and reader can
# never drift.
from ...module_core.sync_context import BOUNDARIES_HEADING

# Directories / config files whose presence means "this project has tests" —
# enough signal to include TESTING.md in the detected plan.
_TEST_DIRS = ("tests", "test", "spec", "__tests__")
_TEST_CONFIG_FILES = (
    "pytest.ini",
    "tox.ini",
    "jest.config.js",
    "jest.config.ts",
    "vitest.config.js",
    "vitest.config.ts",
    "karma.conf.js",
    ".rspec",
    "phpunit.xml",
)


def derive_ticket_prefix(project_name: str) -> str:
    """Default ticket prefix from a project name (``proto-gear`` → ``PROTOG``)."""
    derived = project_name.upper().replace("-", "").replace("_", "")[:6]
    return derived if len(derived) >= 2 else "PROJ"


def detect_test_signals(project_path) -> bool:
    """True when the project visibly has tests (dir or runner config present)."""
    project_path = Path(project_path)
    for d in _TEST_DIRS:
        if (project_path / d).is_dir():
            return True
    for f in _TEST_CONFIG_FILES:
        if (project_path / f).exists():
            return True
    return False


def build_detected_plan(project_info: Dict, git_config: Dict, current_dir) -> Dict:
    """Detection-driven init plan: everything the harness can infer, inferred.

    Returns a config dict shaped for ``run_simple_protogear_init`` plus a
    ``reasons`` map (template → why it was included) for the plan summary.
    Mechanical choices are defaulted — git repo → BRANCHING, tests → TESTING,
    remote → CONTRIBUTING, capabilities always on, ``frontier`` profile — so
    the interaction can be spent on intent instead.
    """
    current_dir = Path(current_dir)
    git_detected = bool(git_config.get("is_git_repo"))
    has_remote = bool(git_config.get("has_remote"))
    has_tests = detect_test_signals(current_dir)

    reasons: Dict[str, str] = {}
    core_templates: Dict[str, bool] = {}

    if git_detected:
        reasons["BRANCHING"] = "git repo detected"
    if has_tests:
        core_templates["TESTING"] = True
        reasons["TESTING"] = "tests detected"
    if has_remote:
        core_templates["CONTRIBUTING"] = True
        reasons["CONTRIBUTING"] = "git remote detected (shared repo)"

    return {
        "with_branching": git_detected,
        "ticket_prefix": (
            derive_ticket_prefix(current_dir.resolve().name) if git_detected else None
        ),
        "with_capabilities": True,
        "profile": "frontier",
        "core_templates": core_templates,
        "reasons": reasons,
    }


def plan_files(plan: Dict) -> List[Tuple[str, str]]:
    """Ordered ``(filename, reason)`` rows for displaying a detected plan."""
    rows: List[Tuple[str, str]] = [
        ("AGENTS.md", "always — agent entry point"),
        ("SESSION_HANDOFF.md", "always — rolling session state"),
        ("PROJECT_STATUS.md", "always — tickets and sprint state"),
    ]
    reasons = plan.get("reasons", {})
    if plan.get("with_branching"):
        rows.append(("BRANCHING.md", reasons.get("BRANCHING", "git workflow")))
    for name in ("TESTING", "CONTRIBUTING"):
        if plan.get("core_templates", {}).get(name):
            rows.append((f"{name}.md", reasons.get(name, "detected")))
    if plan.get("with_capabilities"):
        rows.append(
            (
                ".proto-gear/",
                f"capabilities + lessons ({plan.get('profile', 'frontier')} profile)",
            )
        )
    rows.append(("AGENT_CONTEXT.md + host mirrors", "synced automatically"))
    return rows


def build_specs_stub(
    project_description: Optional[str] = None,
    boundaries: Optional[List[str]] = None,
    conventions: Optional[List[str]] = None,
) -> str:
    """Render the PROJECT_SPECIFICATIONS.md stub from captured intent.

    The Boundaries & Invariants section uses :data:`BOUNDARIES_HEADING` —
    ``sync_context`` parses its bullets back into the generated Critical
    Rules, so boundaries captured at init steer every future session.
    """
    overview = (
        project_description.strip()
        if project_description and project_description.strip()
        else "<!-- 1-3 sentences: what is this project? -->"
    )
    boundary_lines = (
        "\n".join(f"- {b}" for b in boundaries)
        if boundaries
        else "<!-- What must an agent never do here? One bullet per invariant. -->"
    )
    convention_lines = (
        "\n".join(f"- {c}" for c in conventions)
        if conventions
        else "<!-- Non-obvious house rules an agent could not derive from the code. -->"
    )

    return f"""# PROJECT_SPECIFICATIONS.md

## Project Overview

{overview}

{BOUNDARIES_HEADING}

<!-- Bullets here are mirrored into the Critical Rules of the generated
     agent context on every `pg sync-context`. Keep them short and absolute. -->
{boundary_lines}

## House Conventions

{convention_lines}

## Goals

<!-- What are the primary goals of this project? -->

## Architecture

<!-- High-level architecture decisions and patterns -->
<!-- See PROJECT_ARCHITECTURE.md for detailed architecture (extracted by AI agent) -->

## Key Features

<!-- List main features and user stories -->

## Tech Stack

<!-- Languages, frameworks, libraries, tools -->

## Constraints & Requirements

<!-- Non-functional requirements, limitations, compliance needs -->

---

> **Note for AI Agents**: This stub was generated by Proto Gear from the init
> planning intake. Before starting feature work, work with the user to fill in
> the sections above, then extract all architecture decisions into
> `PROJECT_ARCHITECTURE.md`. `PROJECT_ARCHITECTURE.md` supersedes any generic
> `ARCHITECTURE.md` template.
"""


def build_seed_lesson(
    boundaries: Optional[List[str]] = None,
    conventions: Optional[List[str]] = None,
) -> Optional[str]:
    """Render captured conventions/boundaries as a first lesson, or ``None``.

    Output satisfies ``module_core.lessons.parse_lesson`` (H1 title, then a
    ``>`` one-line summary) so it lands in the generated lessons index.
    """
    if not boundaries and not conventions:
        return None

    sections = []
    if boundaries:
        sections.append(
            "## Boundaries — never do\n\n" + "\n".join(f"- {b}" for b in boundaries)
        )
    if conventions:
        sections.append(
            "## House conventions\n\n" + "\n".join(f"- {c}" for c in conventions)
        )
    body = "\n\n".join(sections)

    return f"""# House conventions and boundaries (captured at init)

> Durable project facts the operator stated during `pg init` — verify against reality, refine as you learn.

{body}

---
*Seeded by `pg init`. Update or delete lines that prove wrong; split into
focused lessons as the project accumulates real ones.*
"""


def build_handoff_pending(intent_captured: bool, specs_written: bool) -> str:
    """The Pending section for a fresh SESSION_HANDOFF.md.

    Init ends by writing a task, not by pretending completeness (ADR-004): when
    the operator captured intent, the first agent session starts with an
    explicit expansion task instead of an empty file.
    """
    if not intent_captured:
        return "*Nothing pending.*"
    target = (
        "Expand `PROJECT_SPECIFICATIONS.md` from the init intake"
        if specs_written
        else "Fold the init intake (see `.proto-gear/lessons/`) into the project docs"
    )
    return (
        f"- **First agent task:** {target} — flesh out goals/architecture/tech "
        "stack with the user, then extract architecture decisions into "
        "`PROJECT_ARCHITECTURE.md`."
    )
