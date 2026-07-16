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


def install_module_capabilities(
    proto_gear_dir: Path,
    replacements: Optional[Dict[str, str]] = None,
    dry_run: bool = False,
    modules_root: Optional[Path] = None,
    profile: str = "verbose",
) -> dict:
    """Copy every module's own bundled capabilities into ``.proto-gear/<module>/``.

    The on-disk counterpart to :func:`load_bundled_capabilities` (seam S1): where
    the shared/engineering bundle installs flat under ``.proto-gear/``, each
    discipline's own ``modules/<name>/capabilities/`` installs under its namespace
    ``.proto-gear/<name>/``. A capability under the subtree therefore keeps its
    ``<module>/<cap_id>`` identity for free — ids are the path relative to
    ``.proto-gear/`` — matching both the gate audit and the listing loader.

    Generic by design: a new discipline is picked up here with no edit, because
    the sources come from :func:`iter_capability_sources`. Applies the same
    hardening as the engineering installer — rejects symlinks and path-traversal,
    enforces UTF-8, renames ``*.template.md`` → ``*.md``, and substitutes
    ``{{KEY}}`` placeholders from ``replacements``.

    Returns ``{"files_created": [...], "errors": [...]}`` (paths relative to
    ``proto_gear_dir``'s parent, matching ``copy_capability_templates``).
    """
    import os
    from . import capability_profile

    replacements = replacements or {}
    profile = capability_profile.normalize_profile(profile)
    result: dict = {"files_created": [], "errors": []}
    proto_gear_dir = Path(proto_gear_dir)
    project_dir = proto_gear_dir.parent

    for module, caps_dir in iter_capability_sources(modules_root):
        if module is None:
            continue  # shared root is the engineering installer's job
        module_dest = proto_gear_dir / module
        for source_path in caps_dir.rglob("*"):
            if source_path.is_dir():
                continue
            if source_path.is_symlink():
                result["errors"].append(f"Skipped symlink: {source_path}")
                continue

            rel_path = source_path.relative_to(caps_dir)
            normalized = Path(os.path.normpath(rel_path))
            if ".." in normalized.parts or normalized.is_absolute():
                result["errors"].append(f"Security: Invalid path detected: {rel_path}")
                continue

            dest_path = module_dest / normalized
            if dest_path.suffix == ".md" and dest_path.stem.endswith(".template"):
                dest_path = dest_path.parent / (
                    dest_path.stem.replace(".template", "") + ".md"
                )

            try:
                dest_path.resolve().relative_to(proto_gear_dir.resolve())
            except ValueError:
                result["errors"].append(
                    f"Security: Destination path escapes .proto-gear/: {dest_path}"
                )
                continue

            if dry_run:
                result["files_created"].append(str(dest_path.relative_to(project_dir)))
                continue

            stub = None
            if profile == "frontier" and capability_profile.is_capability_body(
                rel_path
            ):
                stub = capability_profile.frontier_stub_for_capability(source_path)

            if stub is not None:
                content = stub
            else:
                try:
                    content = source_path.read_text(encoding="utf-8")
                except UnicodeDecodeError as e:
                    result["errors"].append(f"Encoding error in {source_path}: {e}")
                    continue
            for key, value in replacements.items():
                content = content.replace("{{" + key + "}}", value)

            dest_path.parent.mkdir(parents=True, exist_ok=True)
            dest_path.write_text(content, encoding="utf-8")
            result["files_created"].append(str(dest_path.relative_to(project_dir)))

    return result


def iter_agent_sources(
    modules_root: Optional[Path] = None,
) -> List["CapabilitySource"]:
    """Return every *bundled* agent-config directory across all modules (seam S1).

    The agent-side counterpart to :func:`iter_capability_sources`: where the
    package ships shared/engineering agents under ``capabilities/agents/`` (source
    ``None``), each discipline may ship its own ``modules/<name>/agents/`` (source
    ``<name>``). A department could not previously ship an agent and have it
    discovered/installed — the same S1 gap capabilities had, one layer up.

    Returns ``(module, dir)`` pairs; ``module`` is ``None`` for the shared root.
    Order is shared-first, then modules sorted by id.
    """
    from ..paths import package_root

    sources: List["CapabilitySource"] = []
    shared = package_root() / "capabilities" / "agents"
    if shared.is_dir():
        sources.append((None, shared))

    for manifest in discover_modules(modules_root):
        if manifest.source_path is None:
            continue
        agents_dir = Path(manifest.source_path).parent / "agents"
        if agents_dir.is_dir():
            sources.append((manifest.module, agents_dir))
    return sources


def list_bundled_agents(modules_root: Optional[Path] = None) -> List[dict]:
    """Every bundled agent the package could install, across all sources.

    The browse view over :func:`iter_agent_sources` (PROTO-076): before this,
    a discipline's agent was visible only *after* ``pg init`` installed it.
    Each record: ``name`` (the agent id — filename stem), ``module`` (``None``
    for the shared root), ``qualified`` (``<module>/<name>``, or the bare name
    for shared), ``path`` (source file), ``description`` (from the YAML, best
    effort — a config that fails to parse still lists, with an empty one).
    Order follows the sources: shared first, then modules alphabetically.
    """
    import yaml

    records: List[dict] = []
    for module, agents_dir in iter_agent_sources(modules_root):
        for source_path in sorted(agents_dir.glob("*.yaml")):
            description = ""
            try:
                data = yaml.safe_load(source_path.read_text(encoding="utf-8"))
                if isinstance(data, dict):
                    description = str(data.get("description", "") or "")
            except Exception:
                pass  # unparseable config still deserves to be listed
            name = source_path.stem
            records.append(
                {
                    "name": name,
                    "module": module,
                    "qualified": name if module is None else f"{module}/{name}",
                    "path": str(source_path),
                    "description": description,
                }
            )
    return records


def install_bundled_agent(
    name: str,
    proto_gear_dir: Path,
    replacements: Optional[Dict[str, str]] = None,
    modules_root: Optional[Path] = None,
) -> dict:
    """Install ONE bundled agent by name into ``.proto-gear/agents/``.

    The on-demand counterpart to :func:`install_module_agents` (which runs the
    full sweep at ``pg init``): pull a single discovered agent — shared or
    discipline-shipped — into an already-initialised host. ``name`` is the
    agent id (filename stem) or the qualified ``<module>/<id>`` form; a bare id
    matching agents in more than one source is ambiguous and must be qualified.

    Same hardening as the sweep installer: rejects symlinks, refuses a
    destination outside ``.proto-gear/``, enforces UTF-8, substitutes
    ``{{KEY}}`` placeholders, and never overwrites an existing agent file.

    Returns ``{"installed": <path str or None>, "errors": [...]}``.
    """
    replacements = replacements or {}
    result: dict = {"installed": None, "errors": []}

    matches = [
        r
        for r in list_bundled_agents(modules_root)
        if name in (r["name"], r["qualified"])
    ]
    if not matches:
        result["errors"].append(f"No bundled agent named '{name}'.")
        return result
    if len(matches) > 1:
        options = ", ".join(r["qualified"] for r in matches)
        result["errors"].append(
            f"Ambiguous agent name '{name}' — qualify it: {options}"
        )
        return result

    source_path = Path(matches[0]["path"])
    if source_path.is_symlink():
        result["errors"].append(f"Skipped symlink: {source_path}")
        return result

    proto_gear_dir = Path(proto_gear_dir)
    dest_path = proto_gear_dir / "agents" / source_path.name
    try:
        dest_path.resolve().relative_to(proto_gear_dir.resolve())
    except ValueError:
        result["errors"].append(
            f"Security: Destination path escapes .proto-gear/: {dest_path}"
        )
        return result
    if dest_path.exists():
        result["errors"].append(
            f"Agent already installed, kept existing: {dest_path.name}"
        )
        return result

    try:
        content = source_path.read_text(encoding="utf-8")
    except UnicodeDecodeError as e:
        result["errors"].append(f"Encoding error in {source_path}: {e}")
        return result
    for key, value in replacements.items():
        content = content.replace("{{" + key + "}}", value)

    dest_path.parent.mkdir(parents=True, exist_ok=True)
    dest_path.write_text(content, encoding="utf-8")
    result["installed"] = str(dest_path)
    return result


def iter_paradigm_sources(
    modules_root: Optional[Path] = None,
) -> List["CapabilitySource"]:
    """Return every *bundled* orchestration-paradigm directory (seam S1).

    The paradigm-pool counterpart to :func:`iter_agent_sources`. The package
    ships shared paradigms under ``orchestration/`` (source ``None``); each
    discipline may ship its own ``modules/<name>/orchestration/`` (source
    ``<name>``). Paradigms are *declarative* orchestration patterns the user or
    the overseeing agent selects from — the core audits them, never executes
    them (ADR-002/003, Principle 4).

    Returns ``(module, dir)`` pairs; ``module`` is ``None`` for the shared root.
    Order is shared-first, then modules sorted by id.
    """
    from ..paths import package_root

    sources: List["CapabilitySource"] = []
    shared = package_root() / "orchestration"
    if shared.is_dir():
        sources.append((None, shared))

    for manifest in discover_modules(modules_root):
        if manifest.source_path is None:
            continue
        paradigms_dir = Path(manifest.source_path).parent / "orchestration"
        if paradigms_dir.is_dir():
            sources.append((manifest.module, paradigms_dir))
    return sources


def list_bundled_paradigms(modules_root: Optional[Path] = None) -> List[dict]:
    """Every bundled orchestration paradigm the package could install.

    The browse view over :func:`iter_paradigm_sources`. Each record: ``name``
    (paradigm id — filename stem), ``module`` (``None`` for the shared root),
    ``qualified`` (``<module>/<name>`` or the bare name for shared), ``path``
    (source file), ``description`` (from the YAML, best effort). Order follows
    the sources: shared first, then modules alphabetically. ``INDEX.*`` files
    are skipped — they are catalog output, not paradigms.
    """
    import yaml

    records: List[dict] = []
    for module, paradigms_dir in iter_paradigm_sources(modules_root):
        for source_path in sorted(paradigms_dir.glob("*.yaml")):
            if source_path.stem.upper() == "INDEX":
                continue
            description = ""
            try:
                data = yaml.safe_load(source_path.read_text(encoding="utf-8"))
                if isinstance(data, dict):
                    description = str(data.get("description", "") or "")
            except Exception:
                pass  # unparseable manifest still deserves to be listed
            name = source_path.stem
            records.append(
                {
                    "name": name,
                    "module": module,
                    "qualified": name if module is None else f"{module}/{name}",
                    "path": str(source_path),
                    "description": description,
                }
            )
    return records


def install_bundled_paradigm(
    name: str,
    proto_gear_dir: Path,
    replacements: Optional[Dict[str, str]] = None,
    modules_root: Optional[Path] = None,
) -> dict:
    """Install ONE bundled paradigm by name into ``.proto-gear/orchestration/``.

    The on-demand counterpart to :func:`install_bundled_agent` for the paradigm
    pool: pull a single discovered paradigm — shared or discipline-shipped —
    into an already-initialised host so a project can customise it. ``name`` is
    the paradigm id (filename stem) or the qualified ``<module>/<id>`` form; an
    ambiguous bare id must be qualified.

    Same hardening as the agent installer: rejects symlinks, refuses a
    destination outside ``.proto-gear/``, enforces UTF-8, substitutes
    ``{{KEY}}`` placeholders, and never overwrites an existing file.

    Returns ``{"installed": <path str or None>, "errors": [...]}``.
    """
    replacements = replacements or {}
    result: dict = {"installed": None, "errors": []}

    matches = [
        r
        for r in list_bundled_paradigms(modules_root)
        if name in (r["name"], r["qualified"])
    ]
    if not matches:
        result["errors"].append(f"No bundled paradigm named '{name}'.")
        return result
    if len(matches) > 1:
        options = ", ".join(r["qualified"] for r in matches)
        result["errors"].append(
            f"Ambiguous paradigm name '{name}' — qualify it: {options}"
        )
        return result

    source_path = Path(matches[0]["path"])
    if source_path.is_symlink():
        result["errors"].append(f"Skipped symlink: {source_path}")
        return result

    proto_gear_dir = Path(proto_gear_dir)
    dest_path = proto_gear_dir / "orchestration" / source_path.name
    try:
        dest_path.resolve().relative_to(proto_gear_dir.resolve())
    except ValueError:
        result["errors"].append(
            f"Security: Destination path escapes .proto-gear/: {dest_path}"
        )
        return result
    if dest_path.exists():
        result["errors"].append(
            f"Paradigm already installed, kept existing: {dest_path.name}"
        )
        return result

    try:
        content = source_path.read_text(encoding="utf-8")
    except UnicodeDecodeError as e:
        result["errors"].append(f"Encoding error in {source_path}: {e}")
        return result
    for key, value in replacements.items():
        content = content.replace("{{" + key + "}}", value)

    dest_path.parent.mkdir(parents=True, exist_ok=True)
    dest_path.write_text(content, encoding="utf-8")
    result["installed"] = str(dest_path)
    return result


def install_module_agents(
    proto_gear_dir: Path,
    replacements: Optional[Dict[str, str]] = None,
    dry_run: bool = False,
    modules_root: Optional[Path] = None,
) -> dict:
    """Install every discipline's own bundled agents into ``.proto-gear/agents/``.

    The on-disk counterpart to :func:`iter_agent_sources` and the agent-side of
    :func:`install_module_capabilities`. Agents are read *flat* from
    ``.proto-gear/agents/`` (``AgentManager`` globs ``*.yaml`` non-recursively),
    so a module's agents install flat there too. The shared root (source ``None``)
    is skipped — the engineering installer's recursive sweep already lays down
    ``capabilities/agents/``; this handles only ``modules/<name>/agents/``.

    Generic by design: a new discipline is picked up here with no edit, because
    the sources come from :func:`iter_agent_sources`. Applies the same hardening
    as the capability installer — rejects symlinks and path-traversal, enforces
    UTF-8, substitutes ``{{KEY}}`` placeholders, and refuses to overwrite an
    existing agent file (so a discipline can never clobber a host-created or
    another discipline's agent — a name collision is reported, never silent).

    Returns ``{"files_created": [...], "errors": [...]}`` (paths relative to
    ``proto_gear_dir``'s parent, matching :func:`install_module_capabilities`).
    """
    import os

    replacements = replacements or {}
    result: dict = {"files_created": [], "errors": []}
    proto_gear_dir = Path(proto_gear_dir)
    project_dir = proto_gear_dir.parent
    agents_dest = proto_gear_dir / "agents"

    for module, agents_dir in iter_agent_sources(modules_root):
        if module is None:
            continue  # shared agents ride the engineering installer's sweep
        for source_path in sorted(agents_dir.glob("*.yaml")):
            if source_path.is_symlink():
                result["errors"].append(f"Skipped symlink: {source_path}")
                continue

            dest_path = agents_dest / source_path.name
            try:
                dest_path.resolve().relative_to(proto_gear_dir.resolve())
            except ValueError:
                result["errors"].append(
                    f"Security: Destination path escapes .proto-gear/: {dest_path}"
                )
                continue

            if dest_path.exists() and not dry_run:
                result["errors"].append(
                    f"Agent name collision, kept existing: {dest_path.name} "
                    f"(from module '{module}')"
                )
                continue

            if dry_run:
                result["files_created"].append(str(dest_path.relative_to(project_dir)))
                continue

            try:
                content = source_path.read_text(encoding="utf-8")
            except UnicodeDecodeError as e:
                result["errors"].append(f"Encoding error in {source_path}: {e}")
                continue
            for key, value in replacements.items():
                content = content.replace("{{" + key + "}}", value)

            dest_path.parent.mkdir(parents=True, exist_ok=True)
            dest_path.write_text(content, encoding="utf-8")
            result["files_created"].append(str(dest_path.relative_to(project_dir)))

    return result


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
