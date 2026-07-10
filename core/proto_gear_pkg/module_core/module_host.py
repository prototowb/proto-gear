"""Multi-module hosting — resolve and operate a *selected* engineering department.

PROTO-048 (ADR-001 Phase B → C). The CLI's ``--module <name>`` flag names which
engineering department a command targets (engineering disciplines such as QA,
DevOps, or docs); this module turns that name into a :class:`ModuleManifest` and
provides the department-agnostic seam a command needs to *materialise a module's
declared state surface* into a host project.

Previously ``pg init`` and template rendering lived entirely inside
``modules/engineering/`` with no neutral path to lay down *another* department's
state surface. The render here knows nothing department-specific — it copies a
module's declared template to its declared surface, applying whatever
substitution mapping the caller supplies (none → verbatim). Engineering keeps
its own richer ``pg init``; a manifest-only department works through this seam
alone.
"""

from pathlib import Path
from typing import TYPE_CHECKING, Dict, List, Optional, Tuple

from .module_manifest import (
    ModuleManifest,
    ModuleManifestError,
    discover_modules,
)

if TYPE_CHECKING:
    from .capability_metadata import CapabilityMetadata

# The department a bare ``pg <cmd>`` (no --module) targets. Engineering is
# module #1 and the historical default, so the single-module case needs no flag.
DEFAULT_MODULE = "engineering"

# A bundled capability directory and the module that owns it (None = the shared
# package-root capabilities/ home). See :func:`iter_capability_sources`.
CapabilitySource = Tuple[Optional[str], Path]


def resolve_module(
    name: Optional[str], modules_root: Optional[Path] = None
) -> ModuleManifest:
    """Return the manifest for module ``name`` (default :data:`DEFAULT_MODULE`).

    Raises :class:`ModuleManifestError` naming the available modules when
    ``name`` doesn't match a discovered module — so an unknown ``--module`` is a
    clear error, never a silent fallback.
    """
    target = name or DEFAULT_MODULE
    by_id = {m.module: m for m in discover_modules(modules_root)}
    manifest = by_id.get(target)
    if manifest is None:
        available = ", ".join(sorted(by_id)) or "(none)"
        raise ModuleManifestError(f"unknown module '{target}'. Available: {available}")
    return manifest


def iter_capability_sources(
    modules_root: Optional[Path] = None,
) -> List["CapabilitySource"]:
    """Return every *bundled* capability directory, across all modules (seam S1).

    Historically the package shipped one shared ``capabilities/`` directory at
    the package root, and every loader (doctor gate audit, discovery, sync) read
    only that. A departmental module could not ship its *own* capabilities and
    have them discovered — the falsifier seam **S1** from
    ``docs/dev/content-module-design.md``.

    This is the source-side counterpart to the manifest's ``capabilities_root``:
    the package-root ``capabilities/`` is the shared/engineering home (source
    ``None``), and each ``modules/<name>/capabilities/`` that exists contributes
    that module's own bundle (source ``<name>``). Callers that must audit or list
    *all* bundled capabilities iterate this instead of hard-coding one directory.

    Returns a list of ``(module, dir)`` pairs; ``module`` is ``None`` for the
    shared root. Order is shared-first, then modules sorted by id.
    """
    from ..paths import package_root

    sources: List["CapabilitySource"] = []
    shared = package_root() / "capabilities"
    if shared.is_dir():
        sources.append((None, shared))

    for manifest in discover_modules(modules_root):
        if manifest.source_path is None:
            continue
        caps_dir = Path(manifest.source_path).parent / "capabilities"
        if caps_dir.is_dir():
            sources.append((manifest.module, caps_dir))
    return sources


def merge_capability_sources(
    sources: List["CapabilitySource"],
) -> Dict[str, "CapabilityMetadata"]:
    """Merge ``(module, dir)`` capability sources into one id → metadata dict.

    Namespacing follows the gate audit's convention exactly (see
    :func:`doctor.check_supervision_gates`): the shared root (source ``None``)
    keeps each capability's bare id (``skills/testing``), while a module-owned
    capability is namespaced ``<module>/<cap_id>`` (``qa/workflows/release-signoff``)
    so two disciplines can ship the same cap id without colliding. Shared is
    iterated first, so a module can never clobber a shared capability.

    This is the *bundled* (package-side) counterpart to what the host-install
    layout gets for free: capabilities laid out under ``.proto-gear/<module>/``
    already yield ``<module>/<cap_id>`` from a single
    :func:`load_all_capabilities` call, because ids are the path relative to the
    root. Bundled sources live in physically separate trees
    (``capabilities/`` + ``modules/<name>/capabilities/``), so they need this
    explicit merge.
    """
    from .capability_metadata import load_all_capabilities

    merged: Dict[str, "CapabilityMetadata"] = {}
    for module, caps_dir in sources:
        for cap_id, meta in load_all_capabilities(caps_dir).items():
            key = cap_id if module is None else f"{module}/{cap_id}"
            merged[key] = meta
    return merged


def load_bundled_capabilities(
    modules_root: Optional[Path] = None,
) -> Dict[str, "CapabilityMetadata"]:
    """Every bundled capability across the shared root and all modules (seam S1).

    The multi-source listing counterpart to the doctor gate audit: where a
    single ``load_all_capabilities(package_root()/'capabilities')`` sees only the
    shared/engineering bundle, this also includes each discipline's own
    ``modules/<name>/capabilities/``, namespaced ``<module>/<cap_id>``. Callers
    that browse or suggest across *all* disciplines use this instead of reading
    one directory.
    """
    return merge_capability_sources(iter_capability_sources(modules_root))


def state_surface_template_path(manifest: ModuleManifest) -> Optional[Path]:
    """Locate the template that renders a module's declared state surface.

    Convention: for ``state_surface: FOO.md`` the template is
    ``FOO.template.md``, looked up first in the module's own directory
    (``modules/<name>/``) and then in the package root (where engineering's
    shared templates live). Returns ``None`` if the module declares no state
    surface or no template is found.
    """
    if not manifest.state_surface:
        return None

    template_name = Path(manifest.state_surface).stem + ".template.md"

    # 1) The module's own directory (manifest.source_path is its module.yaml).
    if manifest.source_path is not None:
        candidate = Path(manifest.source_path).parent / template_name
        if candidate.is_file():
            return candidate

    # 2) Package-root shared templates (engineering's PROJECT_STATUS.template.md).
    from ..paths import package_root

    candidate = package_root() / template_name
    if candidate.is_file():
        return candidate
    return None


def _apply_substitutions(text: str, substitutions: Optional[Dict[str, str]]) -> str:
    if not substitutions:
        return text
    for key, value in substitutions.items():
        text = text.replace("{{" + key + "}}", value)
    return text


def _unresolved_placeholders(text: str) -> List[str]:
    """Return distinct ``{{PLACEHOLDER}}`` tokens still present after render."""
    import re

    return sorted(set(re.findall(r"\{\{[^}]+\}\}", text)))


def render_state_surface(
    manifest: ModuleManifest,
    project_dir: Path,
    substitutions: Optional[Dict[str, str]] = None,
    force: bool = False,
    dry_run: bool = False,
) -> dict:
    """Materialise ``manifest``'s state surface into ``project_dir``.

    Returns a result dict with a ``status`` of one of:
      * ``no-state-surface``  — the module declares none (nothing to do)
      * ``no-template``       — declared, but no matching template found
      * ``exists``            — target present and ``force`` is False
      * ``would-create`` / ``would-overwrite`` — ``dry_run`` preview
      * ``created`` / ``overwritten`` — file written
    plus ``target`` (relative surface name) and ``unresolved`` (list of
    ``{{...}}`` tokens the supplied substitutions didn't fill, so a caller can
    warn that a richer, module-specific init is needed).
    """
    project_dir = Path(project_dir)
    surface = manifest.state_surface
    if not surface:
        return {"status": "no-state-surface", "target": None, "unresolved": []}

    template_path = state_surface_template_path(manifest)
    if template_path is None:
        return {"status": "no-template", "target": surface, "unresolved": []}

    dest = project_dir / surface
    exists = dest.exists()
    if exists and not force:
        return {"status": "exists", "target": surface, "unresolved": []}

    content = _apply_substitutions(
        template_path.read_text(encoding="utf-8"), substitutions
    )
    unresolved = _unresolved_placeholders(content)

    if dry_run:
        status = "would-overwrite" if exists else "would-create"
        return {"status": status, "target": surface, "unresolved": unresolved}

    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(content, encoding="utf-8")
    status = "overwritten" if exists else "created"
    return {"status": status, "target": surface, "unresolved": unresolved}
