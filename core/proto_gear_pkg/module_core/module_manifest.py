"""Departmental module manifest — the module contract as data.

A *module* is a department — an engineering discipline (engineering, qa, …) —
whose way-of-working
is encoded as capabilities + templates + state surfaces. The manifest
(``module.yaml``) declares the contract surfaces from PROJECT_SPECIFICATIONS.md
§3 so the department-agnostic core can discover, load, and audit a module
without knowing anything engineering-specific.

This is the Phase B foundation (ADR-001): the core reads manifests; modules are
added by dropping a ``modules/<name>/module.yaml`` in — zero core edits (the
Phase B exit criterion, ADR-001 action item 6).

Contract surfaces (spec §3):
  1. capabilities_root  — skills/workflows/commands bundle (.proto-gear/)
  2. state_surface      — single source of truth for department state
  3. context_manifest   — auto-generated agent skim (AGENT_CONTEXT.md)
  6. handoff            — rolling session handoff file

Items 4 (drift) and 5 (gates) are provided by the core doctor and by workflow
metadata respectively, not declared here.
"""

from dataclasses import dataclass, asdict, field
from pathlib import Path
from typing import List, Optional

import yaml


class ModuleManifestError(ValueError):
    """Raised when a module.yaml is missing required fields or is malformed."""


# Required top-level keys every module.yaml must declare.
REQUIRED_FIELDS = ("module", "name")

MANIFEST_FILENAME = "module.yaml"


@dataclass
class ModuleManifest:
    """Parsed ``module.yaml``. ``source_path`` is where it was loaded from."""

    module: str
    name: str
    description: str = ""
    version: str = "0.0.0"
    # Contract surfaces (paths are relative to a host project's root)
    capabilities_root: str = ".proto-gear"
    state_surface: Optional[str] = None
    context_manifest: str = "AGENT_CONTEXT.md"
    handoff: Optional[str] = None
    source_path: Optional[Path] = None

    def to_dict(self) -> dict:
        d = asdict(self)
        d["source_path"] = str(self.source_path) if self.source_path else None
        return d


def parse_module_manifest(
    data: dict, source_path: Optional[Path] = None
) -> ModuleManifest:
    """Build a :class:`ModuleManifest` from a parsed mapping.

    Raises :class:`ModuleManifestError` if required fields are missing or the
    top-level document is not a mapping.
    """
    if not isinstance(data, dict):
        raise ModuleManifestError(
            f"module manifest must be a mapping, got {type(data).__name__}"
        )

    missing = [k for k in REQUIRED_FIELDS if not data.get(k)]
    if missing:
        where = f" in {source_path}" if source_path else ""
        raise ModuleManifestError(
            f"module manifest missing required field(s): {', '.join(missing)}{where}"
        )

    # Contract surfaces may be declared flat or nested under `contract:`.
    contract = data.get("contract") or {}
    if not isinstance(contract, dict):
        raise ModuleManifestError("`contract:` must be a mapping if present")

    def surface(key, default):
        return data.get(key, contract.get(key, default))

    return ModuleManifest(
        module=str(data["module"]),
        name=str(data["name"]),
        description=str(data.get("description", "")),
        version=str(data.get("version", "0.0.0")),
        capabilities_root=str(surface("capabilities_root", ".proto-gear")),
        state_surface=_opt_str(surface("state_surface", None)),
        context_manifest=str(surface("context_manifest", "AGENT_CONTEXT.md")),
        handoff=_opt_str(surface("handoff", None)),
        source_path=source_path,
    )


def _opt_str(value) -> Optional[str]:
    return None if value is None else str(value)


def load_module_manifest(path: Path) -> ModuleManifest:
    """Load and parse a single ``module.yaml`` file."""
    path = Path(path)
    if not path.exists():
        raise ModuleManifestError(f"module manifest not found: {path}")
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise ModuleManifestError(f"invalid YAML in {path}: {exc}") from exc
    if data is None:
        raise ModuleManifestError(f"empty module manifest: {path}")
    return parse_module_manifest(data, source_path=path)


def default_modules_root() -> Path:
    """The package-bundled modules/ directory (each subdir is a module)."""
    from ..paths import package_root

    return package_root() / "modules"


def discover_modules(modules_root: Optional[Path] = None) -> List[ModuleManifest]:
    """Discover every module under ``modules_root``.

    A module is any immediate subdirectory containing a ``module.yaml``.
    Returns manifests sorted by module id. Missing root yields an empty list —
    adding a module is dropping a directory in, never a core edit.
    """
    root = Path(modules_root) if modules_root is not None else default_modules_root()
    if not root.is_dir():
        return []

    manifests: List[ModuleManifest] = []
    for child in sorted(root.iterdir()):
        manifest_path = child / MANIFEST_FILENAME
        if child.is_dir() and manifest_path.is_file():
            manifests.append(load_module_manifest(manifest_path))
    return manifests


def validate_manifest_surfaces(
    manifest: ModuleManifest, project_dir: Path
) -> List[str]:
    """Return human-readable problems with a module's contract surfaces.

    Checks that the surfaces the manifest declares actually exist in the given
    host ``project_dir``. An empty list means the module's surfaces are present.
    ``state_surface`` and ``handoff`` are optional to declare, but if declared
    they must exist. ``capabilities_root`` and ``context_manifest`` are always
    expected once a module is initialised.
    """
    project_dir = Path(project_dir)
    problems: List[str] = []

    def _check(label: str, rel: Optional[str], required: bool):
        if rel is None:
            if required:
                problems.append(f"{label} is not declared")
            return
        if not (project_dir / rel).exists():
            problems.append(f"{label} '{rel}' declared but not found")

    _check("capabilities_root", manifest.capabilities_root, required=True)
    _check("context_manifest", manifest.context_manifest, required=True)
    _check("state_surface", manifest.state_surface, required=False)
    _check("handoff", manifest.handoff, required=False)
    return problems
