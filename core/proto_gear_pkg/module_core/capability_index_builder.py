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
    sync_capability_indexes(capabilities_root, dry_run=False, modules_root=None) -> dict
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


def _scaffold_and_replace(path: Path, new_block: str, dry_run: bool, title: str) -> str:
    """Like :func:`_replace_or_warn`, but CREATE the file (with a title + the
    managed block) when missing.

    Used for module-subtree indexes only: a module ships its capabilities but no
    ``INDEX.md``, so unlike the shared root — whose indexes are shipped and
    opt-in — a discipline's indexes are materialised here on demand.
    """
    if not path.exists():
        if dry_run:
            return "would_create"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(f"# {title}\n\n{new_block}\n", encoding="utf-8")
        return "created"
    return _replace_or_warn(path, new_block, dry_run)


def _partition_by_module(
    capabilities: Dict[str, CapabilityMetadata], module_ids: set
) -> Tuple[Dict[str, CapabilityMetadata], Dict[str, Dict[str, CapabilityMetadata]]]:
    """Split loaded caps into the shared root group and per-module groups.

    A cap id like ``qa/workflows/release-signoff`` (from a ``.proto-gear/qa/``
    subtree) belongs to module ``qa`` with its prefix stripped
    (``workflows/release-signoff``) so it renders correctly *inside* the subtree;
    everything else is shared. Type dirs (skills/workflows/commands/agents) are
    never module ids, so shared caps never mis-partition.
    """
    shared: Dict[str, CapabilityMetadata] = {}
    per_module: Dict[str, Dict[str, CapabilityMetadata]] = {}
    for cap_id, meta in capabilities.items():
        head = cap_id.split("/", 1)[0]
        if "/" in cap_id and head in module_ids:
            per_module.setdefault(head, {})[cap_id.split("/", 1)[1]] = meta
        else:
            shared[cap_id] = meta
    return shared, per_module


def sync_capability_indexes(
    capabilities_root: Path, dry_run: bool = False, modules_root: Optional[Path] = None
) -> Dict[str, str]:
    """
    Regenerate the managed block of every INDEX.md under capabilities_root.

    `capabilities_root` should be the directory that contains skills/,
    workflows/, commands/, agents/ — i.e. `<project>/.proto-gear/` for a
    user project, or `core/proto_gear_pkg/capabilities/` for the package
    itself.

    A discipline's own capabilities installed under ``.proto-gear/<module>/``
    (seam S1) are indexed *within that subtree* — the shared root index covers
    only shared/engineering caps, and each module gets its own INDEX set (top +
    the types it actually ships), created on demand since modules ship no
    INDEX.md. This keeps ``qa/workflows/release-signoff`` out of the root
    workflows index and gives each discipline a self-contained index.

    Returns a {relative_path: action} map for every INDEX we attempted.
    """
    if not capabilities_root.exists():
        return {"error": f"Capabilities root not found: {capabilities_root}"}

    from .module_manifest import discover_modules

    capabilities = load_all_capabilities(capabilities_root)
    module_ids = {m.module for m in discover_modules(modules_root)}
    shared, per_module = _partition_by_module(capabilities, module_ids)

    results: Dict[str, str] = {}

    # Shared root — shipped indexes, never auto-created (unchanged behavior).
    results[TOP_INDEX.as_posix()] = _replace_or_warn(
        capabilities_root / TOP_INDEX, render_top_index_block(shared), dry_run
    )
    for cap_type, rel_path in TYPE_INDEXES.items():
        block = render_type_index_block(shared, cap_type)
        results[rel_path.as_posix()] = _replace_or_warn(
            capabilities_root / rel_path, block, dry_run
        )

    # Per-module subtrees — index only the types a module actually ships,
    # scaffolding the INDEX.md files on demand.
    for module, caps in sorted(per_module.items()):
        mroot = capabilities_root / module
        results[f"{module}/{TOP_INDEX.as_posix()}"] = _scaffold_and_replace(
            mroot / TOP_INDEX,
            render_top_index_block(caps),
            dry_run,
            f"{module} capabilities",
        )
        for cap_type, rel_path in TYPE_INDEXES.items():
            if not _filter_by_type(caps, cap_type):
                continue
            block = render_type_index_block(caps, cap_type)
            results[f"{module}/{rel_path.as_posix()}"] = _scaffold_and_replace(
                mroot / rel_path, block, dry_run, _TYPE_LABEL[cap_type]
            )

    return results


# ---------- introspection (used by doctor) ----------


def extract_managed_block(text: str) -> Optional[str]:
    """Return the BEGIN..END block (inclusive) or None if absent."""
    m = _BLOCK_RE.search(text)
    return m.group(0) if m else None
