"""
pg doctor — proto-gear drift detector.

Audits the project for sync drift across:
  1. AGENT_CONTEXT.md vs. live-generated content
  2. host config files (CLAUDE.md, .cursorrules, etc.) managed blocks
  3. proto-gear:header presence on core docs (AGENTS.md, etc.)
  4. capability metadata validity
  5. departmental module manifests (module.yaml) validity
  6. supervision gates declared in workflow metadata (contract item 5)
  7. agent-context token budget (the generated block stays a skim, not a manual)
  8. lessons layer — malformed lesson files + stale lessons/INDEX.md (Phase 4)
  9. branch-guard pre-commit hook installed (Phase 5; advisory nudge)

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
    id: str  # short slug: "agent-context-drift", "host-block-missing", ...
    severity: str  # "ok" | "warning" | "error"
    target: str  # file path or capability id
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
            "summary": {
                "ok": self.ok,
                "warnings": self.warnings,
                "errors": self.errors,
            },
            "findings": [f.to_dict() for f in self.findings],
        }


def _normalize(text: str) -> str:
    """Strip the volatile Generated: timestamp before comparing."""
    return _GENERATED_LINE.sub("", text).strip()


# ---------- individual checks ----------


def check_agent_context_sync(project_dir: Path) -> List[Finding]:
    canon = project_dir / "AGENT_CONTEXT.md"
    if not canon.exists():
        return [
            Finding(
                id="agent-context-missing",
                severity="error",
                target="AGENT_CONTEXT.md",
                message="AGENT_CONTEXT.md not found — agents have no index to read.",
                fix_hint="Run `pg sync-context` to generate it",
            )
        ]
    existing = canon.read_text(encoding="utf-8")
    regenerated = sync_context_module.generate_agent_context(project_dir)
    if _normalize(existing) == _normalize(regenerated):
        return [
            Finding(
                id="agent-context-sync",
                severity="ok",
                target="AGENT_CONTEXT.md",
                message="In sync.",
            )
        ]
    return [
        Finding(
            id="agent-context-drift",
            severity="warning",
            target="AGENT_CONTEXT.md",
            message="AGENT_CONTEXT.md does not match current project state.",
            fix_hint="Run `pg sync-context` to regenerate",
        )
    ]


def check_agent_context_budget(project_dir: Path) -> List[Finding]:
    """Warn when the generated agent-context block outgrows its token budget.

    The managed block is mirrored into every host file and re-read on every
    agent session across every downstream project, so its size is a recurring
    attention tax. Estimated locally (no network) — see
    `sync_context.estimate_tokens`.
    """
    block = sync_context_module.managed_block(project_dir)
    if not block:
        return []  # template breakage is already reported by check_host_files
    budget = sync_context_module.AGENT_CONTEXT_TOKEN_BUDGET
    tokens = sync_context_module.estimate_tokens(block)
    if tokens > budget:
        return [
            Finding(
                id="agent-context-over-budget",
                severity="warning",
                target="AGENT_CONTEXT.md",
                message=(
                    f"Generated agent-context block is ~{tokens} tokens, over the "
                    f"{budget}-token budget — every line taxes every agent session."
                ),
                fix_hint=(
                    "Trim capability descriptions/rules, or move detail behind a "
                    "pointer; the block is meant to be a skim, not a manual."
                ),
            )
        ]
    return [
        Finding(
            id="agent-context-budget",
            severity="ok",
            target="AGENT_CONTEXT.md",
            message=f"~{tokens}/{budget} token budget.",
        )
    ]


def check_host_files(project_dir: Path) -> List[Finding]:
    findings: List[Finding] = []
    regenerated = sync_context_module.generate_agent_context(project_dir)
    canon_block = sync_context_module._extract_managed_block(regenerated)
    if not canon_block:
        return [
            Finding(
                id="agent-context-template-broken",
                severity="error",
                target="AGENT_CONTEXT.template.md",
                message="Template missing BEGIN/END markers — sync is impossible.",
            )
        ]
    canon_norm = _normalize(canon_block)

    for hf in sync_context_module.HOST_FILES:
        path = project_dir / hf
        if not path.exists():
            findings.append(
                Finding(
                    id="host-file-missing",
                    severity="warning",
                    target=hf,
                    message=f"{hf} not present — agents reading this host won't see the index.",
                    fix_hint="Run `pg sync-context` to create it",
                )
            )
            continue
        block = sync_context_module._extract_managed_block(
            path.read_text(encoding="utf-8")
        )
        if not block:
            findings.append(
                Finding(
                    id="host-block-missing",
                    severity="warning",
                    target=hf,
                    message=f"{hf} exists but has no managed proto-gear block.",
                    fix_hint="Run `pg sync-context` to insert it",
                )
            )
            continue
        if _normalize(block) != canon_norm:
            findings.append(
                Finding(
                    id="host-block-drift",
                    severity="warning",
                    target=hf,
                    message=f"{hf} managed block does not match AGENT_CONTEXT.",
                    fix_hint="Run `pg sync-context` to refresh",
                )
            )
        else:
            findings.append(
                Finding(
                    id="host-block-sync",
                    severity="ok",
                    target=hf,
                    message="In sync.",
                )
            )
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
            findings.append(
                Finding(
                    id="core-doc-read-error",
                    severity="error",
                    target=fname,
                    message=f"Could not read {fname}: {e}",
                )
            )
            continue
        header = parse_proto_gear_header(text)
        if header is None:
            findings.append(
                Finding(
                    id="missing-proto-gear-header",
                    severity="warning",
                    target=fname,
                    message=f"{fname} is missing the proto-gear:header block.",
                    fix_hint=(
                        "Add a `<!-- proto-gear:header ... -->` block "
                        "(see core/proto_gear_pkg/*.template.md for shape)"
                    ),
                )
            )
        else:
            findings.append(
                Finding(
                    id="proto-gear-header-ok",
                    severity="ok",
                    target=fname,
                    message="Header present.",
                )
            )
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
        return [
            Finding(
                id="capabilities-load-error",
                severity="error",
                target=".proto-gear/",
                message=f"Capability load failed: {e}",
            )
        ]
    if not caps:
        return [
            Finding(
                id="capabilities-empty",
                severity="warning",
                target=".proto-gear/",
                message="Capabilities directory present but empty — no skills, workflows, or commands loaded.",
            )
        ]
    for cap_id, cap in caps.items():
        if not cap.relevance or not cap.relevance.triggers:
            findings.append(
                Finding(
                    id="capability-no-triggers",
                    severity="warning",
                    target=cap_id,
                    message="Capability declares no triggers — won't match `pg suggest`.",
                    fix_hint=f"Add `relevance.triggers: [...]` to {cap_id}/metadata.yaml",
                )
            )
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
        return [
            Finding(
                id="capability-index-error",
                severity="error",
                target=".proto-gear/INDEX.md",
                message=f"INDEX render failed: {e}",
            )
        ]
    if "error" in results:
        return [
            Finding(
                id="capability-index-error",
                severity="error",
                target=".proto-gear/",
                message=str(results["error"]),
            )
        ]
    for rel, action in results.items():
        target = f".proto-gear/{rel}"
        if action == "would_update":
            findings.append(
                Finding(
                    id="capability-index-drift",
                    severity="warning",
                    target=target,
                    message="INDEX.md managed block is stale.",
                    fix_hint="Run `pg sync-indexes` to regenerate",
                )
            )
        elif action == "missing-file":
            # Top-level INDEX missing is a real concern; per-type can be
            # legitimately absent (e.g. no agents/INDEX.md before agents ship).
            severity = "warning" if rel == "INDEX.md" else "ok"
            findings.append(
                Finding(
                    id="capability-index-file-missing",
                    severity=severity,
                    target=target,
                    message=(
                        "Top-level INDEX.md not present in .proto-gear/."
                        if rel == "INDEX.md"
                        else f"Optional INDEX.md not present ({rel})."
                    ),
                    fix_hint="Run `pg sync-indexes` or `pg init --with-capabilities`",
                )
            )
        elif action == "missing-markers":
            findings.append(
                Finding(
                    id="capability-index-no-markers",
                    severity="ok",
                    target=target,
                    message="No proto-gear:capability-index markers — auto-sync skipped.",
                )
            )
        elif action == "unchanged":
            findings.append(
                Finding(
                    id="capability-index-sync",
                    severity="ok",
                    target=target,
                    message="In sync.",
                )
            )
        elif action == "would_create":
            # A module subtree ships no INDEX.md; sync will materialise it.
            findings.append(
                Finding(
                    id="capability-index-will-create",
                    severity="ok",
                    target=target,
                    message="Module INDEX.md will be generated by sync.",
                    fix_hint="Run `pg sync-indexes` to generate it",
                )
            )
        # 'updated' / 'created' shouldn't appear under dry_run=True
    return findings


def check_lessons(project_dir: Path) -> List[Finding]:
    """Validate the agent-writable lessons layer (Phase 4).

    Silent when no lessons directory exists (it's optional). When present:
    flags malformed lesson files and a stale lessons/INDEX.md, both fixable by
    `pg sync-context`.
    """
    from . import lessons as lessons_module

    caps_root = project_dir / ".proto-gear"
    lessons_dir = caps_root / lessons_module.LESSONS_DIRNAME
    if not lessons_dir.exists():
        return []

    findings: List[Finding] = []
    for path, problem in lessons_module.validate_lessons(lessons_dir):
        rel = path.relative_to(project_dir) if path.is_absolute() else path
        findings.append(
            Finding(
                id="lesson-malformed",
                severity="warning",
                target=str(rel),
                message=f"Malformed lesson: {problem}.",
                fix_hint="Lead with `# Title` then a `> summary` line",
            )
        )

    try:
        status = lessons_module.sync_lessons_index(caps_root, dry_run=True)["status"]
    except Exception as e:
        return findings + [
            Finding(
                id="lessons-index-error",
                severity="error",
                target=".proto-gear/lessons/INDEX.md",
                message=f"Lessons index render failed: {e}",
            )
        ]

    if status == "would-update":
        findings.append(
            Finding(
                id="lessons-index-drift",
                severity="warning",
                target=".proto-gear/lessons/INDEX.md",
                message="Lessons index is stale.",
                fix_hint="Run `pg sync-context` to regenerate",
            )
        )
    elif status in ("unchanged", "no-dir", "missing-markers", "would-create"):
        findings.append(
            Finding(
                id="lessons-ok",
                severity="ok",
                target=".proto-gear/lessons/",
                message=f"{len(lessons_module.load_lessons(lessons_dir))} lesson(s), index in sync.",
            )
        )
    return findings


def check_branch_guard_hook(project_dir: Path) -> List[Finding]:
    """Audit local enforcement of the "never commit to `main`" invariant (Phase 5).

    Advisory, never an error — the invariant is also enforced by `pg guard
    branch` in CI, so a missing local hook is a nudge, not a failure. Silent
    outside a git repo, and silent when the repo already has *some* pre-commit
    hook that isn't ours: the user manages their own hooks and `pg hooks
    install` is deliberately no-clobber, so nagging would be noise. Emits:

      - ``ok``      when the bundled branch-guard hook is installed;
      - ``warning`` when a git repo has no pre-commit hook at all — nothing
        stops a local commit to a protected branch.
    """
    from . import hooks as hooks_module

    hooks_dir = hooks_module.git_hooks_dir(str(project_dir))
    if hooks_dir is None:
        return []  # not a git repo — local hook enforcement is N/A

    pre_commit = hooks_dir / "pre-commit"
    if pre_commit.exists():
        existing = pre_commit.read_text(encoding="utf-8", errors="replace")
        if hooks_module.BRANCH_GUARD_MARKER in existing:
            return [
                Finding(
                    id="branch-guard-hook-ok",
                    severity="ok",
                    target=str(pre_commit),
                    message="Branch-guard pre-commit hook installed.",
                )
            ]
        # A non-guard pre-commit hook exists — the user runs their own hooks.
        return []

    return [
        Finding(
            id="branch-guard-hook-missing",
            severity="warning",
            target="pre-commit",
            message='"never commit to `main`" is not enforced locally — no pre-commit hook.',
            fix_hint="Run `pg hooks install` to add the branch-guard hook",
        )
    ]


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
            findings.append(
                Finding(
                    id="module-manifest-invalid",
                    severity="error",
                    target=target,
                    message=str(exc),
                    fix_hint="Declare required fields (module, name) in module.yaml",
                )
            )
            continue
        findings.append(
            Finding(
                id="module-manifest-valid",
                severity="ok",
                target=target,
                message=f"Module '{manifest.module}' v{manifest.version} manifest OK.",
            )
        )
    return findings


# Workflow outputs that denote an irreversible / externally-visible effect and
# therefore warrant an explicit human supervision gate (contract item 5).
_RISK_OUTPUT_TOKENS = ("release", "deploy", "publish")


def _bundled_agent_actors() -> set:
    """Every discipline-shipped agent id (``<module>/<agent-slug>``).

    The vocabulary a gate's namespaced ``actor:`` may reference — an agent slug
    is its filename stem in ``modules/<name>/agents/`` (the id the PROTO-067
    seam installs it under). Shared-root agents are not namespaced and a human
    role actor carries no ``/``, so neither appears here.
    """
    from . import module_host

    actors = set()
    for module, agents_dir in module_host.iter_agent_sources():
        if module is None:
            continue
        for f in sorted(agents_dir.glob("*.yaml")):
            actors.add(f"{module}/{f.stem}")
    return actors


def check_supervision_gates(project_dir: Path) -> List[Finding]:
    """Audit supervision gates declared in bundled workflow capabilities.

    Rules (PROJECT_SPECIFICATIONS.md §4, contract item 5, ADR-002):
      * structural — every declared gate must have an id + description;
      * coverage — a workflow that produces a release/deployment/publish output
        must declare at least one gate, so approval points are never implied;
      * authority — a gate's ``authority`` must be a rung of the adopted ladder
        (the deferred ``agent`` clearing rung is rejected per the PROTO-069
        amendment), and an ``auto`` gate must declare an ``evidence`` column —
        it clears by the evidence predicate alone, so without one it would be
        unverifiable;
      * evidence predicate — a gate's ``evidence`` predicate must come from the
        declarative vocabulary (``GATE_EVIDENCE_PREDICATES``), and a comparison
        predicate must be fully specified: an evidence column, a value operand,
        and a numeric operand for ``at-least``;
      * actor — a namespaced ``actor`` (``<module>/<agent>``) must reference an
        agent some discipline actually ships (warning: accountability that
        points at nobody).
    Audits the package-bundled capabilities (the committed source of truth) —
    the shared root AND every module's own ``capabilities/`` bundle, so a module
    that ships its own gated workflow (e.g. qa's release-signoff) is enforced the
    same as engineering's (seam S1). Module-owned capabilities are targeted as
    ``<module>/<cap_id>`` to disambiguate.
    """
    from .capability_metadata import (
        load_all_capabilities,
        CapabilityType,
        GATE_AUTHORITY_LADDER,
        GATE_DEFERRED_AUTHORITIES,
        GATE_EVIDENCE_PREDICATES,
    )
    from . import module_host

    findings: List[Finding] = []
    known_actors: Optional[set] = None  # resolved lazily, only if referenced

    for module, caps_dir in module_host.iter_capability_sources():
        try:
            caps = load_all_capabilities(caps_dir)
        except Exception:
            # capability load failures are reported by check_capabilities
            continue

        for cap_id, meta in sorted(caps.items()):
            if (
                getattr(meta, "type", None) != CapabilityType.WORKFLOW
                or not meta.workflow
            ):
                continue
            gates = meta.workflow.gates
            target = cap_id if module is None else f"{module}/{cap_id}"

            for g in gates:
                if not g.id or not g.description:
                    findings.append(
                        Finding(
                            id="gate-malformed",
                            severity="error",
                            target=target,
                            message="supervision gate missing id and/or description.",
                            fix_hint="Give every gates: entry an id and a description",
                        )
                    )

                authority = getattr(g, "authority", "human")
                if authority in GATE_DEFERRED_AUTHORITIES:
                    findings.append(
                        Finding(
                            id="gate-authority-deferred",
                            severity="error",
                            target=target,
                            message=(
                                f"gate '{g.id}' declares authority '{authority}' — "
                                "the agent clearing rung is deferred (ADR-002, "
                                "PROTO-069 amendment); the ceiling is "
                                "'human-on-recommendation'."
                            ),
                            fix_hint="Use human-on-recommendation (agent verifies + recommends, human ratifies)",
                        )
                    )
                elif authority not in GATE_AUTHORITY_LADDER:
                    findings.append(
                        Finding(
                            id="gate-authority-invalid",
                            severity="error",
                            target=target,
                            message=(
                                f"gate '{g.id}' declares unknown authority "
                                f"'{authority}'."
                            ),
                            fix_hint=f"Use one of: {', '.join(GATE_AUTHORITY_LADDER)}",
                        )
                    )
                elif authority == "auto" and not g.evidence:
                    findings.append(
                        Finding(
                            id="gate-auto-needs-evidence",
                            severity="error",
                            target=target,
                            message=(
                                f"gate '{g.id}' is authority 'auto' but names no "
                                "evidence column — an auto gate clears by its "
                                "evidence predicate alone."
                            ),
                            fix_hint="Declare evidence: <state-surface column> or raise the authority",
                        )
                    )

                # Evidence predicate (ADR-002 §2) — must stay within the small
                # declarative vocabulary, and a comparison predicate must be
                # fully specified (column + operand) or it is theater.
                predicate = getattr(g, "evidence_predicate", "non-empty")
                ev_value = getattr(g, "evidence_value", "")
                if predicate not in GATE_EVIDENCE_PREDICATES:
                    findings.append(
                        Finding(
                            id="gate-evidence-predicate-invalid",
                            severity="error",
                            target=target,
                            message=(
                                f"gate '{g.id}' declares unknown evidence "
                                f"predicate '{predicate}'."
                            ),
                            fix_hint=f"Use one of: {', '.join(GATE_EVIDENCE_PREDICATES)}",
                        )
                    )
                elif predicate != "non-empty":
                    if not g.evidence:
                        findings.append(
                            Finding(
                                id="gate-evidence-column-missing",
                                severity="error",
                                target=target,
                                message=(
                                    f"gate '{g.id}' declares evidence predicate "
                                    f"'{predicate}' but no evidence column to "
                                    "check it against."
                                ),
                                fix_hint="Declare evidence: {column: <state-surface column>, predicate: ..., value: ...}",
                            )
                        )
                    if not ev_value:
                        findings.append(
                            Finding(
                                id="gate-evidence-value-missing",
                                severity="error",
                                target=target,
                                message=(
                                    f"gate '{g.id}' evidence predicate "
                                    f"'{predicate}' requires a value operand."
                                ),
                                fix_hint="Add value: to the evidence mapping",
                            )
                        )
                    elif predicate == "at-least":
                        try:
                            float(ev_value)
                        except ValueError:
                            findings.append(
                                Finding(
                                    id="gate-evidence-value-not-numeric",
                                    severity="error",
                                    target=target,
                                    message=(
                                        f"gate '{g.id}' at-least predicate needs "
                                        f"a numeric value, got '{ev_value}'."
                                    ),
                                    fix_hint="Use a number, e.g. value: 90",
                                )
                            )

                actor = getattr(g, "actor", "")
                if actor and "/" in actor:
                    if known_actors is None:
                        known_actors = _bundled_agent_actors()
                    if actor not in known_actors:
                        findings.append(
                            Finding(
                                id="gate-actor-unknown",
                                severity="warning",
                                target=target,
                                message=(
                                    f"gate '{g.id}' names actor '{actor}' but no "
                                    "discipline ships that agent."
                                ),
                                fix_hint="Reference a modules/<name>/agents/ file as <module>/<agent-slug>",
                            )
                        )

            risky = any(
                any(tok in str(o).lower() for tok in _RISK_OUTPUT_TOKENS)
                for o in meta.workflow.outputs
            )
            if risky and not gates:
                findings.append(
                    Finding(
                        id="gate-missing",
                        severity="warning",
                        target=target,
                        message="produces a release/deployment but declares no supervision gate.",
                        fix_hint="Declare the human approval point under workflow.gates (contract item 5)",
                    )
                )
            elif gates:
                findings.append(
                    Finding(
                        id="gate-ok",
                        severity="ok",
                        target=target,
                        message=f"{len(gates)} supervision gate(s) declared.",
                    )
                )
    return findings


# ---------- driver ----------


def run_diagnostics(project_dir: Path) -> DiagnosticsReport:
    report = DiagnosticsReport()
    report.findings.extend(check_agent_context_sync(project_dir))
    report.findings.extend(check_agent_context_budget(project_dir))
    report.findings.extend(check_host_files(project_dir))
    report.findings.extend(check_core_doc_headers(project_dir))
    report.findings.extend(check_capabilities(project_dir))
    report.findings.extend(check_capability_indexes(project_dir))
    report.findings.extend(check_lessons(project_dir))
    report.findings.extend(check_branch_guard_hook(project_dir))
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
    "lessons-index-drift",
}


def fixable_by_sync(report: DiagnosticsReport) -> bool:
    return any(f.id in _SYNC_FIXABLE_IDS for f in report.findings)
