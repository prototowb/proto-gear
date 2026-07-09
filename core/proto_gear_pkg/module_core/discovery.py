"""
Runtime capability discovery — match user prose against the
``relevance.triggers`` of each installed (or built-in) capability.

Used by ``pg suggest <prose>``: an agent (or human) describes a task in
free text; we return the top N capabilities whose triggers overlap the
prose.
"""

import re
from pathlib import Path
from typing import Dict, List

from .capability_metadata import load_all_capabilities, CapabilityMetadata


def _project_caps_dir(project_dir: Path) -> Path:
    """Project-local capabilities directory (.proto-gear/)."""
    return project_dir / ".proto-gear"


def _package_caps_dir() -> Path:
    """Built-in capabilities shipped with the package."""
    from ..paths import package_root
    return package_root() / "capabilities"


def load_capabilities_for_suggest(project_dir: Path) -> Dict[str, CapabilityMetadata]:
    """
    Prefer project-installed capabilities; fall back to package built-ins
    so ``pg suggest`` still produces useful output before ``pg init``.
    """
    project_caps = _project_caps_dir(project_dir)
    if project_caps.exists():
        try:
            caps = load_all_capabilities(project_caps)
            if caps:
                return caps
        except Exception:
            pass

    package_caps = _package_caps_dir()
    if package_caps.exists():
        try:
            return load_all_capabilities(package_caps)
        except Exception:
            return {}
    return {}


_TOKEN_RE = re.compile(r"[a-z0-9\-/]+")


def _tokenize(text: str) -> List[str]:
    """Lowercase, split on non-word chars; keep hyphens and slashes."""
    return _TOKEN_RE.findall(text.lower())


def _score_capability(prose_tokens: List[str], prose_lower: str,
                      cap: CapabilityMetadata) -> tuple:
    """
    Return (score, matched_triggers).

    A trigger contributes its full string-match weight if it appears as a
    substring of the prose, plus 1 for each token overlap. This lets both
    multi-word phrases ("write tests") and single keywords ("bug") rank.
    """
    if not cap.relevance or not cap.relevance.triggers:
        return 0, []

    score = 0
    matched: List[str] = []
    prose_token_set = set(prose_tokens)

    for trigger in cap.relevance.triggers:
        trigger_lower = trigger.lower().strip()
        if not trigger_lower:
            continue

        substring_hit = trigger_lower in prose_lower
        trigger_tokens = _tokenize(trigger_lower)
        token_overlap = sum(1 for t in trigger_tokens if t in prose_token_set)

        if substring_hit:
            # Multi-word triggers get higher weight than single-word.
            score += 3 + len(trigger_tokens)
            matched.append(trigger)
        elif token_overlap >= max(1, len(trigger_tokens) // 2):
            score += token_overlap
            matched.append(trigger)

    return score, matched


def suggest(project_dir: Path, prose: str, limit: int = 3) -> List[dict]:
    """
    Score capabilities against ``prose`` and return up to ``limit`` matches.

    Each match is a dict:
        {
            "id":               "skills/testing",
            "type":             "skill",
            "name":             "Test-Driven Development",
            "description":      "...",
            "score":            7,
            "matched_triggers": ["write tests", "tdd"],
        }
    """
    if not prose or not prose.strip():
        return []

    capabilities = load_capabilities_for_suggest(project_dir)
    if not capabilities:
        return []

    prose_lower = prose.lower()
    prose_tokens = _tokenize(prose_lower)

    scored = []
    for cap_id, cap in capabilities.items():
        score, matched = _score_capability(prose_tokens, prose_lower, cap)
        if score <= 0:
            continue
        scored.append({
            "id": cap_id,
            "type": cap.type.value if hasattr(cap.type, "value") else str(cap.type),
            "name": cap.name,
            "description": cap.description,
            "score": score,
            "matched_triggers": matched,
        })

    scored.sort(key=lambda m: (-m["score"], m["id"]))
    return scored[:limit]
