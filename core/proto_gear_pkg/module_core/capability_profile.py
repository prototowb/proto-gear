"""
Capability output profiles (steering-plan Phase 2+3).

Proto-gear ships one canonical capability source (the verbose ``*.template.md``
bodies) and renders it at different verbosity per consumer:

- ``verbose``  — the full scaffolding: methodology, worked examples, checklists.
  For small / local / older models that still benefit from the training wheels,
  or for humans who want the whole playbook.
- ``frontier`` — the slim delta: title, one-line description, when-to-use and a
  pointer back to the host docs where the *non-derivable* specifics live
  (coverage targets, conventions, supervision gates). The generic methodology is
  omitted because a frontier model already knows it, and every retained line is a
  per-session attention tax.

Nothing is lost by choosing ``frontier`` — the verbose corpus is one
``pg init --profile verbose`` away. This module is the durable machinery; the
capability content stays a single source of truth.
"""

from pathlib import Path, PurePath
from typing import List, Optional

CAPABILITY_PROFILES = ("frontier", "verbose")

# New inits default to the slim profile (plan Phase 3); ``copy_capability_templates``
# keeps ``verbose`` as its own default so existing library callers are unchanged.
DEFAULT_PROFILE = "frontier"

# Capability *body* files — the verbose methodology docs a frontier profile stubs.
# Metadata / INDEX files are always copied verbatim (routing + `pg suggest` need them).
_BODY_STEMS = {"SKILL", "WORKFLOW", "COMMAND"}


def normalize_profile(value: Optional[str]) -> str:
    """Return a valid profile name, defaulting to DEFAULT_PROFILE on None/unknown."""
    if not value:
        return DEFAULT_PROFILE
    v = str(value).strip().lower()
    return v if v in CAPABILITY_PROFILES else DEFAULT_PROFILE


def is_capability_body(rel_path) -> bool:
    """True for SKILL/WORKFLOW/COMMAND template bodies (the stub-able files)."""
    name = PurePath(rel_path).name
    if not name.endswith(".template.md"):
        return False
    stem = name[: -len(".template.md")]
    return stem in _BODY_STEMS


def render_frontier_stub(
    name: str,
    cap_type: str,
    description: str,
    triggers: Optional[List[str]] = None,
) -> str:
    """Render the slim body a frontier profile ships in place of the full doc.

    Kept deliberately short: the routing signal lives in the description, the
    non-derivable specifics live in the host docs, and the methodology is left to
    the model. Every line here is paid on every session that loads the capability.
    """
    title = name or cap_type or "Capability"
    use_when = ", ".join(triggers[:6]) if triggers else ""
    lines = [f"# {title}", ""]
    if description:
        lines.append(description)
        lines.append("")
    if use_when:
        lines.append(f"**Use when:** {use_when}")
        lines.append("")
    lines.append(
        "> **Frontier profile.** The generic methodology for this "
        f"{cap_type or 'capability'} is intentionally omitted — a modern agent "
        "already knows it, and every retained line taxes attention. The "
        "non-derivable, project-specific specifics (coverage targets, "
        "conventions, release gates) live in the host docs — PROJECT_STATUS.md, "
        "TESTING.md, BRANCHING.md, and the supervision gates. Reinstall with "
        "`pg init --profile verbose` for the full playbook."
    )
    return "\n".join(lines) + "\n"


def frontier_stub_for_capability(source_body_path: Path) -> Optional[str]:
    """Build a frontier stub from the sibling ``metadata.yaml``.

    Returns None when metadata can't be read, so the caller can fall back to
    copying the verbose body rather than shipping an empty stub.
    """
    meta_path = Path(source_body_path).parent / "metadata.yaml"
    if not meta_path.exists():
        return None
    try:
        import yaml

        data = yaml.safe_load(meta_path.read_text(encoding="utf-8")) or {}
    except Exception:
        return None

    relevance = data.get("relevance") or {}
    triggers = relevance.get("triggers") or []
    return render_frontier_stub(
        name=str(data.get("name", "")).strip(),
        cap_type=str(data.get("type", "")).strip(),
        description=str(data.get("description", "")).strip(),
        triggers=[str(t) for t in triggers],
    )
