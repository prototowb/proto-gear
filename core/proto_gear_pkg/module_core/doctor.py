"""
pg doctor — proto-gear drift detector.

Audits the project for sync drift across:
  1. AGENT_CONTEXT.md vs. live-generated content
  2. host config files (CLAUDE.md, .cursorrules, etc.) managed blocks
  3. proto-gear:header presence on core docs (AGENTS.md, etc.)
  4. capability metadata validity
  5. departmental module manifests (module.yaml) validity
  6. supervision gates declared in workflow metadata (contract item 5)

Each check produces a list of Finding records. The dispatcher in proto_gear.py
turns these into human-readable output or JSON.
"""

import re
from dataclasses import dataclass, asdict, field
from pathlib import Path
from typing import List, Optional

from . import sync_context as sync_context_module
from . import capability_index_builder
from . import module_manifest
from .metadata_parser import parse_proto_gear_header


# Same set the templates ship — kept local so doctor doesn't import from tests.
CORE_DOC_FILES = [
    "AGENTS.md",
    "PROJECT_STATUS.md",
    "BRANCHING.md",
    "TESTING.md",
    "CONTRIBUTING.md",
    "SECURITY.md",
    "ARCHITECTURE.md",
    "CODE_OF_CONDUCT.md",
]

# Timestamp line in AGENT_CONTEXT changes every regeneration; ignore for drift.
_GENERATED_LINE = re.compile(r"^- \*\*Generated\*\*:.*$", re.MULTILINE)


@dataclass
class Finding:
    id: str            # short slug: "agent-context-drift", "host-block-missing", ...
    severity: str      # "ok" | "warning" | "error"
    target: str        # file path or capability id
    message: str
    fix_hint: str = ""

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class DiagnosticsReport:
    findings: List[Finding] = field(default_factory=list)

    @property
    def errors(self) -> int:
        return sum(1 for f in self.findings if f.severity == "error")

    @property
    def warnings(self) -> int:
        return sum(1 for f in self.findings if f.severity == "warning")

    @property
    def ok(self) -> int:
        return sum(1 for f in self.findings if f.severity == "ok")

    def to_dict(self) -> dict:
        return {
            "summary": {"ok": self.ok, "warnings": self.warnings, "errors": self.errors},
            "findings": [f.to_dict() for f in self.findings],
        }


def _normalize(text: str) -> str:
    """Strip the volatile Generated: timestamp before comparing."""
    return _GENERATED_LINE.sub("", text).strip()


# ---------- individual checks ----------

def check_agent_context_sync(project_dir: Path) -> List[Finding]:
    canon = project_dir / "AGENT_CONTEXT.md"
    if not canon.exists():
        return [Finding(
            id="agent-context-missing",
            severity="error",
            target="AGENT_CONTEXT.md",
            message="AGENT_CONTEXT.md not found — agents have no index to read.",
            fix_hint="Run `pg sync-context` to generate it",
        )]
    existing = canon.read_text(encoding="utf-8")
    regenerated = sync_context_module.generate_agent_context(project_dir)
    if _normalize(existing) == _normalize(regenerated):
        return [Finding(id="agent-context-sync", severity="ok",
                        target="AGENT_CONTEXT.md", message="In sync.")]
    return [Finding(
        id="agent-context-drift",
        severity="warning",
        target="AGENT_CONTEXT.md",
        message="AGENT_CONTEXT.md does not match current project state.",
        fix_hint="Run `pg sync-context` to regenerate",
    )]


def check_host_files(project_dir: Path) -> List[Finding]:
    findings: List[Finding] = []
    regenerated = sync_context_module.generate_agent_context(project_dir)
    canon_block = sync_context_module._extract_managed_block(regenerated)
    if not canon_block:
        return [Finding(
            id="agent-context-template-broken",
            severity="error",
            target="AGENT_CONTEXT.template.md",
            message="Template missing BEGIN/END markers — sync is impossible.",
        )]
    canon_norm = _normalize(canon_block)

    for hf in sync_context_module.HOST_FILES:
        path = project_dir / hf
        if not path.exists():
            findings.append(Finding(
                id="host-file-missing",
                severity="warning",
                target=hf,
                message=f"{hf} not present — agents reading this host won't see the index.",
                fix_hint="Run `pg sync-context` to create it",
            ))
            continue
        block = sync_context_module._extract_managed_block(
            path.read_text(encoding="utf-8")
        )
        if not block:
            findings.append(Finding(
                id="host-block-missing",
                severity="warning",
                target=hf,
                message=f"{hf} exists but has no managed proto-gear block.",
                fix_hint="Run `pg sync-context` to insert it",
            ))
            continue
        if _normalize(block) != canon_norm:
            findings.append(Finding(
                id="host-block-drift",
                severity="warning",
                target=hf,
                message=f"{hf} managed block does not match AGENT_CONTEXT.",
                fix_hint="Run `pg sync-context` to refresh",
            ))
        else:
            findings.append(Finding(
                id="host-block-sync", severity="ok",
                target=hf, message="In sync.",
            ))
    return findings


def check_core_doc_headers(project_dir: Path) -> List[Finding]:
    findings: List[Finding] = []
    for fname in CORE_DOC_FILES:
        path = project_dir / fname
        if not path.exists():
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except Exception as e:
            findings.append(Finding(
                id="core-doc-read-error",
                severity="error",
                target=fname,
                message=f"Could not read {fname}: {e}",
            ))
            continue
        header = parse_proto_gear_header(text)
        if header is None:
            findings.append(Finding(
                id="missing-proto-gear-header",
                severity="warning",
                target=fname,
                message=f"{fname} is missing the proto-gear:header block.",
                fix_hint=(
                    "Add a `<!-- proto-gear:header ... -->` block "
                    "(see core/proto_gear_pkg/*.template.md for shape)"
                ),
            ))
        else:
            findings.append(Finding(
                id="proto-gear-header-ok",
                severity="ok",
                target=fname,
                message="Header present.",
            ))
    return findings


def check_capabilities(project_dir: Path) -> List[Finding]:
    caps_dir = project_dir / ".proto-gear"
    if not caps_dir.exists():
        return []  # not initialized — silent
    findings: List[Finding] = []
    try:
        from .capability_metadata import load_all_capabilities
        caps = load_all_capabilities(caps_dir)
    except Exception as e:
        return [Finding(
            id="capabilities-load-error",
            severity="error",
            target=".proto-gear/",
            message=f"Capability load failed: {e}",
        )]
    if not caps:
        return [Finding(
            id="capabilities-empty",
            severity="warning",
            target=".proto-gear/",
            message="Capabilities directory present but empty — no skills, workflows, or commands loaded.",
        )]
    for cap_id, cap in caps.items():
        if not cap.relevance or not cap.relevance.triggers:
            findings.append(Finding(
                id="capability-no-triggers",
                severity="warning",
                target=cap_id,
                message="Capability declares no triggers — won't match `pg suggest`.",
                fix_hint=f"Add `relevance.triggers: [...]` to {cap_id}/metadata.yaml",
            ))
    return findings


def check_capability_indexes(project_dir: Path) -> List[Finding]:
    """Each INDEX.md under .proto-gear/ must match what the builder produces."""
    caps_root = project_dir / ".proto-gear"
    if not caps_root.exists():
        return []  # not initialized
    findings: List[Finding] = []
    try:
        results = capability_index_builder.sync_capability_indexes(
            caps_root, dry_run=True
        )
    except Exception as e:
        return [Finding(
            id="capability-index-error",
            severity="error",
            target=".proto-gear/INDEX.md",
            message=f"INDEX render failed: {e}",
        )]
    if "error" in results:
        return [Finding(
            id="capability-index-error",
            severity="error",
            target=".proto-gear/",
            message=str(results["error"]),
        )]
    for rel, action in results.items():
        target = f".proto-gear/{rel}"
        if action == "would_update":
            findings.append(Finding(
                id="capability-index-drift",
                severity="warning",
                target=target,
                message="INDEX.md managed block is stale.",
                fix_hint="Run `pg sync-indexes` to regenerate",
            ))
        elif action == "missing-file":
            # Top-level INDEX missing is a real concern; per-type can be
            # legitimately absent (e.g. no agents/INDEX.md before agents ship).
            severity = "warning" if rel == "INDEX.md" else "ok"
            findings.append(Finding(
                id="capability-index-file-missing",
                severity=severity,
                target=target,
                message=("Top-level INDEX.md not present in .proto-gear/."
                         if rel == "INDEX.md"
                         else f"Optional INDEX.md not present ({rel})."),
                fix_hint="Run `pg sync-indexes` or `pg init --with-capabilities`",
            ))
        elif action == "missing-markers":
            findings.append(Finding(
                id="capability-index-no-markers",
                severity="ok",
                target=target,
                message="No proto-gear:capability-index markers — auto-sync skipped.",
            ))
        elif action == "unchanged":
            findings.append(Finding(
                id="capability-index-sync",
                severity="ok",
                target=target,
                message="In sync.",
            ))
        # 'updated' / 'created' shouldn't appear under dry_run=True
    return findings


def check_modules(project_dir: Path) -> List[Finding]:
    """Validate every bundled departmental module manifest (module.yaml).

    Enforces the module contract at the manifest level: each module's manifest
    must load and declare its required fields. Surface-existence against a host
    project is intentionally out of scope here — an uninitialised project is
    already flagged by the context/capability checks — so a synced project with
    valid manifests reports no drift.
    """
    findings: List[Finding] = []
    root = module_manifest.default_modules_root()
    if not root.is_dir():
        return findings

    manifest_files = sorted(root.glob(f"*/{module_manifest.MANIFEST_FILENAME}"))
    for mpath in manifest_files:
        target = f"modules/{mpath.parent.name}/{mpath.name}"
        try:
            manifest = module_manifest.load_module_manifest(mpath)
        except module_manifest.ModuleManifestError as exc:
            findings.append(Finding(
                id="module-manifest-invalid",
                severity="error",
                target=target,
                message=str(exc),
                fix_hint="Declare required fields (module, name) in module.yaml",
            ))
            continue
        findings.append(Finding(
            id="module-manifest-valid",
            severity="ok",
            target=target,
            message=f"Module '{manifest.module}' v{manifest.version} manifest OK.",
        ))
    return findings


# Workflow outputs that denote an irreversible / externally-visible effect and
# therefore warrant an explicit human supervision gate (contract item 5).
_RISK_OUTPUT_TOKENS = ("release", "deploy", "publish")


def check_supervision_gates(project_dir: Path) -> List[Finding]:
    """Audit supervision gates declared in bundled workflow capabilities.

    Two rules (PROJECT_SPECIFICATIONS.md §4, contract item 5):
      * structural — every declared gate must have an id + description;
      * coverage — a workflow that produces a release/deployment/publish output
        must declare at least one gate, so approval points are never implied.
    Validates the package-bundled capabilities (the committed source of truth),
    mirroring check_modules.
    """
    from ..paths import package_root
    from .capability_metadata import load_all_capabilities, CapabilityType

    findings: List[Finding] = []
    caps_dir = package_root() / "capabilities"
    try:
        caps = load_all_capabilities(caps_dir)
    except Exception:
        # capability load failures are reported by check_capabilities
        return findings

    for cap_id, meta in sorted(caps.items()):
        if getattr(meta, "type", None) != CapabilityType.WORKFLOW or not meta.workflow:
            continue
        gates = meta.workflow.gates

        for g in gates:
            if not g.id or not g.description:
                findings.append(Finding(
                    id="gate-malformed",
                    severity="error",
                    target=cap_id,
                    message="supervision gate missing id and/or description.",
                    fix_hint="Give every gates: entry an id and a description",
                ))

        risky = any(
            any(tok in str(o).lower() for tok in _RISK_OUTPUT_TOKENS)
            for o in meta.workflow.outputs
        )
        if risky and not gates:
            findings.append(Finding(
                id="gate-missing",
                severity="warning",
                target=cap_id,
                message="produces a release/deployment but declares no supervision gate.",
                fix_hint="Declare the human approval point under workflow.gates (contract item 5)",
            ))
        elif gates:
            findings.append(Finding(
                id="gate-ok",
                severity="ok",
                target=cap_id,
                message=f"{len(gates)} supervision gate(s) declared.",
            ))
    return findings


# ---------- driver ----------

def run_diagnostics(project_dir: Path) -> DiagnosticsReport:
    report = DiagnosticsReport()
    report.findings.extend(check_agent_context_sync(project_dir))
    report.findings.extend(check_host_files(project_dir))
    report.findings.extend(check_core_doc_headers(project_dir))
    report.findings.extend(check_capabilities(project_dir))
    report.findings.extend(check_capability_indexes(project_dir))
    report.findings.extend(check_modules(project_dir))
    report.findings.extend(check_supervision_gates(project_dir))
    return report


_SYNC_FIXABLE_IDS = {
    "agent-context-missing",
    "agent-context-drift",
    "host-file-missing",
    "host-block-missing",
    "host-block-drift",
    "capability-index-drift",
}


def fixable_by_sync(report: DiagnosticsReport) -> bool:
    return any(f.id in _SYNC_FIXABLE_IDS for f in report.findings)
