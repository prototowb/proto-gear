"""Orchestration paradigm configurations.

An **orchestration paradigm** is a named, declarative pattern for *how* the
overseer distributes and coordinates sub-agents for a piece of work — solo, a
driver+reviewer pair, a persistent core plus situational flex, a discipline
pipeline, a parallel fan-out, or fully dynamic composition. Proto Gear ships a
**pool** of them; the orchestrating party (a human via the interactive UI, or
the overseeing AI agent) **selects and switches paradigms on the fly** as
circumstances change, always aiming for efficiency.

Paradigms are declarations the core *audits and surfaces*, never executes
(ADR-002/003, Principle 4): they guide the overseer; they do not spawn models.
A paradigm composes nothing (unlike an agent's capabilities), so this parser is
deliberately small and independent of the capability composition engine.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field

import yaml


class ParadigmValidationError(Exception):
    """Raised when an orchestration-paradigm manifest fails validation."""


# Which model tier a paradigm role defaults to. Mirrors agent_config.MODEL_TIERS.
ROLE_MODEL_TIERS = ("fast", "balanced", "deep")

# Who may select/switch to a paradigm. Both by default.
SELECTORS = ("user", "agent")


@dataclass
class ParadigmRole:
    """One role a paradigm coordinates (e.g. driver, reviewer).

    ``agent`` optionally slots a specific ``pg agent`` id into the role;
    ``model_tier`` is the tier that role's work wants (the efficiency lever).
    """

    role: str
    responsibility: str = ""
    agent: Optional[str] = None
    model_tier: str = "balanced"

    def to_dict(self) -> Dict[str, Any]:
        data: Dict[str, Any] = {"role": self.role}
        if self.responsibility:
            data["responsibility"] = self.responsibility
        if self.agent:
            data["agent"] = self.agent
        data["model_tier"] = self.model_tier
        return data


@dataclass
class OrchestrationParadigm:
    """A single orchestration paradigm from the pool."""

    id: str
    name: str
    description: str
    version: str = "1.0.0"
    created: str = ""
    author: str = ""

    when_to_use: List[str] = field(default_factory=list)
    avoid_when: List[str] = field(default_factory=list)
    roles: List[ParadigmRole] = field(default_factory=list)
    coordination: str = ""
    efficiency: str = ""
    selectable_by: List[str] = field(default_factory=lambda: list(SELECTORS))
    status: str = "active"

    source_file: Optional[Path] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "created": self.created,
            "author": self.author,
            "when_to_use": self.when_to_use,
            "avoid_when": self.avoid_when,
            "roles": [r.to_dict() for r in self.roles],
            "coordination": self.coordination,
            "efficiency": self.efficiency,
            "selectable_by": self.selectable_by,
            "status": self.status,
        }


def _parse_roles(raw: Any, source: str) -> List[ParadigmRole]:
    if raw is None:
        return []
    if not isinstance(raw, list):
        raise ParadigmValidationError(f"'roles' must be a list in {source}")
    roles: List[ParadigmRole] = []
    for i, item in enumerate(raw):
        if not isinstance(item, dict) or not item.get("role"):
            raise ParadigmValidationError(
                f"Role #{i + 1} must be a mapping with a 'role' key in {source}"
            )
        tier = item.get("model_tier", "balanced")
        if tier not in ROLE_MODEL_TIERS:
            raise ParadigmValidationError(
                f"Invalid model_tier '{tier}' for role '{item['role']}' in {source}. "
                f"Must be one of: {list(ROLE_MODEL_TIERS)}"
            )
        agent = item.get("agent")
        roles.append(
            ParadigmRole(
                role=str(item["role"]),
                responsibility=str(item.get("responsibility", "") or ""),
                agent=str(agent) if agent else None,
                model_tier=tier,
            )
        )
    return roles


def parse_paradigm_dict(
    data: Dict[str, Any], source: str = ""
) -> OrchestrationParadigm:
    """Parse and validate a paradigm manifest dictionary."""
    if not isinstance(data, dict):
        raise ParadigmValidationError(f"Paradigm manifest must be a mapping: {source}")

    for required in ("id", "name", "description"):
        if not data.get(required):
            raise ParadigmValidationError(
                f"Missing required field '{required}' in {source}"
            )

    selectable_by = data.get("selectable_by", list(SELECTORS))
    if not isinstance(selectable_by, list) or not selectable_by:
        raise ParadigmValidationError(
            f"'selectable_by' must be a non-empty list in {source}"
        )
    for who in selectable_by:
        if who not in SELECTORS:
            raise ParadigmValidationError(
                f"Invalid selectable_by entry '{who}' in {source}. "
                f"Must be one of: {list(SELECTORS)}"
            )

    return OrchestrationParadigm(
        id=str(data["id"]),
        name=str(data["name"]),
        description=str(data["description"]),
        version=str(data.get("version", "1.0.0")),
        created=str(data.get("created", "") or ""),
        author=str(data.get("author", "") or ""),
        when_to_use=list(data.get("when_to_use", []) or []),
        avoid_when=list(data.get("avoid_when", []) or []),
        roles=_parse_roles(data.get("roles"), source),
        coordination=str(data.get("coordination", "") or ""),
        efficiency=str(data.get("efficiency", "") or ""),
        selectable_by=list(selectable_by),
        status=str(data.get("status", "active") or "active"),
    )


def parse_paradigm_file(file_path: Path) -> OrchestrationParadigm:
    """Parse an orchestration paradigm from a YAML file."""
    file_path = Path(file_path)
    if not file_path.exists():
        raise FileNotFoundError(f"Paradigm manifest not found: {file_path}")
    data = yaml.safe_load(file_path.read_text(encoding="utf-8"))
    paradigm = parse_paradigm_dict(data, str(file_path))
    paradigm.source_file = file_path
    return paradigm


def load_paradigms(
    project_dir: Optional[Path] = None, modules_root: Optional[Path] = None
) -> List[OrchestrationParadigm]:
    """Load the full paradigm pool: bundled + any installed project overrides.

    An installed project paradigm (``.proto-gear/orchestration/<id>.yaml``) wins
    over a bundled one with the same id, so a project can customise a paradigm
    without losing it from the pool.
    """
    from .module_core import module_host

    by_id: Dict[str, OrchestrationParadigm] = {}

    for record in module_host.list_bundled_paradigms(modules_root):
        try:
            by_id[record["name"]] = parse_paradigm_file(Path(record["path"]))
        except Exception:
            continue  # a broken bundled manifest shouldn't sink the pool

    if project_dir is not None:
        installed = Path(project_dir) / ".proto-gear" / "orchestration"
        if installed.is_dir():
            for path in sorted(installed.glob("*.yaml")):
                if path.stem.upper() == "INDEX":
                    continue
                try:
                    by_id[path.stem] = parse_paradigm_file(path)
                except Exception:
                    continue

    return sorted(by_id.values(), key=lambda p: p.id)
