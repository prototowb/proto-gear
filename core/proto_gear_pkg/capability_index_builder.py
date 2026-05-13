"""
Capability INDEX.md generator.

Each capability has a `metadata.yaml` (canonical). The corresponding
INDEX.md files (top-level capabilities/INDEX.md + per-type INDEX.md)
contain a *managed block* fenced by:

    <!-- proto-gear:capability-index begin -->
    ... rendered content ...
    <!-- proto-gear:capability-index end -->

Everything outside the markers is hand-written prose that the generator
must preserve. Everything inside is regenerated from metadata.yaml.

Public API:
    render_top_index_block(caps) -> str
    render_type_index_block(caps, type) -> str
    sync_capability_indexes(capabilities_root, dry_run=False) -> dict
"""

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from .capability_metadata import (
    CapabilityMetadata,
    CapabilityType,
    load_all_capabilities,
)


BEGIN_MARKER = "<!-- proto-gear:capability-index begin -->"
END_MARKER = "<!-- proto-gear:capability-index end -->"

# Where the managed block lives in each INDEX file, relative to the
# capabilities root.
TOP_INDEX = Path("INDEX.md")
TYPE_INDEXES: Dict[CapabilityType, Path] = {
    CapabilityType.SKILL: Path("skills/INDEX.md"),
    CapabilityType.WORKFLOW: Path("workflows/INDEX.md"),
    CapabilityType.COMMAND: Path("commands/INDEX.md"),
    CapabilityType.AGENT: Path("agents/INDEX.md"),
}

_TYPE_LABEL: Dict[CapabilityType, str] = {
    CapabilityType.SKILL: "Skills",
    CapabilityType.WORKFLOW: "Workflows",
    CapabilityType.COMMAND: "Slash Commands",
    CapabilityType.AGENT: "Agents",
}

# Capability-type → content filename inside each capability folder.
_TYPE_FILENAME: Dict[CapabilityType, str] = {
    CapabilityType.SKILL: "SKILL.md",
    CapabilityType.WORKFLOW: "WORKFLOW.md",
    CapabilityType.COMMAND: "COMMAND.md",
    CapabilityType.AGENT: "AGENT.md",
}


# ---------- rendering helpers ----------

def _cap_dir_name(cap_id: str) -> str:
    """skills/testing -> testing"""
    if "/" in cap_id:
        return cap_id.split("/", 1)[1]
    return cap_id


def _format_triggers(cap: CapabilityMetadata) -> str:
    if not cap.relevance or not cap.relevance.triggers:
        return "_none declared_"
    return ", ".join(f'"{t}"' for t in cap.relevance.triggers)


def _format_contexts(cap: CapabilityMetadata) -> str:
    if not cap.relevance or not cap.relevance.contexts:
        return ""
    return "; ".join(cap.relevance.contexts)


def _format_deps(cap: CapabilityMetadata) -> str:
    parts: List[str] = []
    deps = cap.dependencies
    if deps.required:
        parts.append("required: " + ", ".join(f"`{d}`" for d in deps.required))
    if deps.optional:
        parts.append("optional: " + ", ".join(f"`{d}`" for d in deps.optional))
    if deps.suggested:
        parts.append("suggested: " + ", ".join(f"`{d}`" for d in deps.suggested))
    return "; ".join(parts) if parts else "_none_"


def _filter_by_type(
    capabilities: Dict[str, CapabilityMetadata], cap_type: CapabilityType
) -> List[Tuple[str, CapabilityMetadata]]:
    return sorted(
        ((cap_id, cap) for cap_id, cap in capabilities.items() if cap.type == cap_type),
        key=lambda kv: kv[0],
    )


# ---------- per-type INDEX block ----------

def render_type_index_block(
    capabilities: Dict[str, CapabilityMetadata], cap_type: CapabilityType
) -> str:
    """Render the managed block for a single per-type INDEX.md.

    The output is wrapped in BEGIN/END markers and includes a count header,
    one section per capability, and trailing source metadata.
    """
    rows = _filter_by_type(capabilities, cap_type)
    filename = _TYPE_FILENAME[cap_type]
    label = _TYPE_LABEL[cap_type]

    lines: List[str] = [BEGIN_MARKER, ""]
    lines.append(f"## Available {label} ({len(rows)})")
    lines.append("")
    lines.append(
        "_Auto-generated from `metadata.yaml`. Hand-edits inside this block "
        "are overwritten by `pg sync-indexes`._"
    )
    lines.append("")

    if not rows:
        lines.append(f"_No {label.lower()} installed._")
        lines.append("")
        lines.append(END_MARKER)
        return "\n".join(lines)

    for cap_id, cap in rows:
        dir_name = _cap_dir_name(cap_id)
        lines.append(f"### {cap.name}")
        lines.append("")
        lines.append(f"- **ID**: `{cap_id}`")
        lines.append(f"- **File**: `{dir_name}/{filename}`")
        lines.append(f"- **Version**: {cap.version}")
        lines.append(
            f"- **Status**: {cap.status.value if hasattr(cap.status, 'value') else cap.status}"
        )
        lines.append(f"- **Category**: {cap.category}")
        lines.append(f"- **Description**: {cap.description}")
        if cap.tags:
            lines.append(f"- **Tags**: {', '.join(cap.tags)}")
        lines.append(f"- **Triggers**: {_format_triggers(cap)}")
        ctx = _format_contexts(cap)
        if ctx:
            lines.append(f"- **Contexts**: {ctx}")
        lines.append(f"- **Dependencies**: {_format_deps(cap)}")
        if cap.agent_roles:
            lines.append(f"- **Agent roles**: {', '.join(cap.agent_roles)}")
        if cap_type == CapabilityType.WORKFLOW and cap.workflow:
            wf = cap.workflow
            if wf.steps:
                lines.append(f"- **Steps**: {wf.steps}")
            if wf.estimated_duration:
                lines.append(f"- **Estimated duration**: {wf.estimated_duration}")
        lines.append("")

    lines.append(END_MARKER)
    return "\n".join(lines)


# ---------- top-level INDEX block ----------

def render_top_index_block(capabilities: Dict[str, CapabilityMetadata]) -> str:
    """Render the managed block for the top-level capabilities/INDEX.md.

    Summary table per type plus counts. Avoids reproducing every capability
    field — that's what the per-type INDEX is for.
    """
    lines: List[str] = [BEGIN_MARKER, ""]
    lines.append("## Capability Summary")
    lines.append("")
    lines.append(
        "_Auto-generated from `metadata.yaml`. Hand-edits inside this block "
        "are overwritten by `pg sync-indexes`._"
    )
    lines.append("")

    for cap_type in (
        CapabilityType.SKILL,
        CapabilityType.WORKFLOW,
        CapabilityType.COMMAND,
        CapabilityType.AGENT,
    ):
        rows = _filter_by_type(capabilities, cap_type)
        label = _TYPE_LABEL[cap_type]
        type_dir = {
            CapabilityType.SKILL: "skills",
            CapabilityType.WORKFLOW: "workflows",
            CapabilityType.COMMAND: "commands",
            CapabilityType.AGENT: "agents",
        }[cap_type]

        lines.append(f"### {label} ({len(rows)})")
        lines.append("")
        if not rows:
            lines.append(f"_No {label.lower()} installed._")
            lines.append("")
            continue
        lines.append("| ID | Name | Description | Triggers |")
        lines.append("|----|------|-------------|----------|")
        for cap_id, cap in rows:
            triggers = ""
            if cap.relevance and cap.relevance.triggers:
                triggers = ", ".join(f"`{t}`" for t in cap.relevance.triggers[:4])
            lines.append(
                f"| `{cap_id}` | {cap.name} | {cap.description} | {triggers} |"
            )
        lines.append("")
        lines.append(f"**Detail**: [{type_dir}/INDEX.md]({type_dir}/INDEX.md)")
        lines.append("")

    lines.append(END_MARKER)
    return "\n".join(lines)


# ---------- file-level sync ----------

_BLOCK_RE = re.compile(
    re.escape(BEGIN_MARKER) + r".*?" + re.escape(END_MARKER),
    re.DOTALL,
)


@dataclass
class IndexSyncResult:
    path: Path
    action: str  # 'updated' | 'unchanged' | 'would_update' | 'would_create'
                 # | 'created' | 'missing-file' | 'missing-markers'


def _replace_or_warn(path: Path, new_block: str, dry_run: bool) -> str:
    """
    Replace the managed block in `path`. If the markers are absent we do
    NOT touch the file — that's a deliberate signal that someone hasn't
    yet opted this INDEX in to auto-generation. Returns the action string.
    """
    if not path.exists():
        return "missing-file"

    text = path.read_text(encoding="utf-8")
    if not _BLOCK_RE.search(text):
        return "missing-markers"

    updated = _BLOCK_RE.sub(new_block, text)
    if updated == text:
        return "unchanged"
    if dry_run:
        return "would_update"
    path.write_text(updated, encoding="utf-8")
    return "updated"


def sync_capability_indexes(
    capabilities_root: Path, dry_run: bool = False
) -> Dict[str, str]:
    """
    Regenerate the managed block of every INDEX.md under capabilities_root.

    `capabilities_root` should be the directory that contains skills/,
    workflows/, commands/, agents/ — i.e. `<project>/.proto-gear/` for a
    user project, or `core/proto_gear_pkg/capabilities/` for the package
    itself.

    Returns a {relative_path: action} map for every INDEX we attempted.
    """
    if not capabilities_root.exists():
        return {"error": f"Capabilities root not found: {capabilities_root}"}

    capabilities = load_all_capabilities(capabilities_root)

    results: Dict[str, str] = {}

    # Top-level
    top_block = render_top_index_block(capabilities)
    results[TOP_INDEX.as_posix()] = _replace_or_warn(
        capabilities_root / TOP_INDEX, top_block, dry_run
    )

    # Per-type
    for cap_type, rel_path in TYPE_INDEXES.items():
        block = render_type_index_block(capabilities, cap_type)
        results[rel_path.as_posix()] = _replace_or_warn(
            capabilities_root / rel_path, block, dry_run
        )

    return results


# ---------- introspection (used by doctor) ----------

def extract_managed_block(text: str) -> Optional[str]:
    """Return the BEGIN..END block (inclusive) or None if absent."""
    m = _BLOCK_RE.search(text)
    return m.group(0) if m else None
