"""Cross-discipline supervision pipeline — Phase D (ADR-001).

The disciplines don't need to be wired together imperatively: each already
*declares* its human control points as supervision gates in workflow
``metadata.yaml`` (``gates[].before`` = the action a gate guards, ``approver``,
``required``). Read across every discipline, those gates form the org's
**path to production** — and the interesting structure is where disciplines
*converge* on the same guarded action (e.g. ``deploy`` is gated by both
engineering's ``release-approval`` and devops's ``prod-approval``).

This module composes that view generically from what modules already declare —
so a new discipline's gates join the pipeline with zero code here, exactly like
the doctor gate audit and the S1 listings. It is read-only: it reports the
declared approval surface, it does not execute anything.
"""

from pathlib import Path
from typing import Dict, List, Optional

# A soft, engineering-flavoured ordering for the common guarded actions, so the
# rendered pipeline reads front-to-back (code → ship). Actions not listed here
# are appended alphabetically — nothing is hidden, ordering is presentation only.
_ACTION_ORDER = [
    "merge",
    "release",
    "tag-and-deploy",
    "deploy",
    "announce",
]


def collect_supervision_gates(modules_root: Optional[Path] = None) -> List[dict]:
    """Return every supervision gate across all disciplines as flat records.

    Each record: ``discipline``, ``workflow`` (namespaced id), ``workflow_name``,
    ``gate``, ``before`` (guarded action), ``approver``, ``required``,
    ``description``, ``evidence`` (the state-surface column that records this
    gate's sign-off, or ``""``) with ``evidence_predicate``/``evidence_value``
    (the declarative claim that column must satisfy — ADR-002 §2), ``scope``
    (``"change"`` per-ticket or ``"release"`` per-release), ``actor`` (who is
    accountable for the guarded work, or ``""``) and ``authority`` (the minimum
    authority required to clear — ADR-002 graded-authority ladder). The
    shared/engineering bundle reports discipline ``"engineering"``; a module's
    own caps report the module id.
    """
    from . import module_host
    from .capability_metadata import load_all_capabilities, CapabilityType

    records: List[dict] = []
    for module, caps_dir in module_host.iter_capability_sources(modules_root):
        discipline = module or "engineering"
        try:
            caps = load_all_capabilities(caps_dir)
        except Exception:
            continue
        for cap_id, meta in caps.items():
            if (
                getattr(meta, "type", None) != CapabilityType.WORKFLOW
                or not meta.workflow
            ):
                continue
            full_id = cap_id if module is None else f"{module}/{cap_id}"
            for g in meta.workflow.gates:
                records.append(
                    {
                        "discipline": discipline,
                        "workflow": full_id,
                        "workflow_name": meta.name,
                        "gate": g.id,
                        "before": g.before or "",
                        "approver": g.approver,
                        "required": g.required,
                        "description": g.description,
                        "evidence": g.evidence,
                        "evidence_predicate": g.evidence_predicate,
                        "evidence_value": g.evidence_value,
                        "scope": g.scope,
                        "actor": g.actor,
                        "authority": g.authority,
                    }
                )
    return records


def _action_sort_key(action: str):
    """Known pipeline actions first (in flow order), then the rest alphabetically."""
    if action in _ACTION_ORDER:
        return (0, _ACTION_ORDER.index(action), action)
    return (1, 0, action)


def build_pipeline(modules_root: Optional[Path] = None) -> List[dict]:
    """Group supervision gates by the action they guard (``before``).

    Returns an ordered list of stages, each ``{"action", "gates":[...]}``, where
    the gates guarding a shared action across disciplines sit together — the
    cross-discipline convergence points. Stages are ordered by a soft pipeline
    flow (see :data:`_ACTION_ORDER`), unknown actions appended alphabetically;
    gates within a stage are sorted by discipline then gate id.
    """
    by_action: Dict[str, List[dict]] = {}
    for r in collect_supervision_gates(modules_root):
        by_action.setdefault(r["before"] or "(unspecified)", []).append(r)

    stages: List[dict] = []
    for action in sorted(by_action, key=_action_sort_key):
        gates = sorted(by_action[action], key=lambda r: (r["discipline"], r["gate"]))
        stages.append({"action": action, "gates": gates})
    return stages
