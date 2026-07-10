"""Tests for the cross-discipline supervision pipeline (PROTO-060, Phase D).

`module_core.pipeline` composes every discipline's declared supervision gates
into the org's path to production — grouped by the action each gate guards, so
cross-discipline convergence points (e.g. `deploy`, gated by both devops and
engineering) are visible. Generic: it reads bundled multi-source, so a new
discipline's gates join with no code change here.
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "core"))

from proto_gear_pkg.module_core import pipeline


def _args(**kw):
    return argparse.Namespace(**kw)


class TestCollectSupervisionGates:
    def test_collects_gates_from_all_disciplines(self):
        records = pipeline.collect_supervision_gates()
        by_gate = {r["gate"]: r for r in records}
        # one gate per shipped discipline is present, attributed correctly.
        assert by_gate["qa-signoff"]["discipline"] == "qa"
        assert by_gate["prod-approval"]["discipline"] == "devops"
        assert by_gate["release-approval"]["discipline"] == "engineering"

    def test_module_gate_workflow_is_namespaced(self):
        records = pipeline.collect_supervision_gates()
        deploy = next(r for r in records if r["gate"] == "prod-approval")
        assert deploy["workflow"] == "devops/workflows/deploy"
        assert deploy["before"] == "deploy"
        assert deploy["approver"] == "human"


class TestBuildPipeline:
    def test_stages_in_flow_order(self):
        stages = pipeline.build_pipeline()
        actions = [s["action"] for s in stages]
        # known pipeline actions render front-to-back.
        assert actions.index("merge") < actions.index("release")
        assert actions.index("release") < actions.index("deploy")
        assert actions.index("deploy") < actions.index("announce")

    def test_deploy_is_a_convergence_point(self):
        stages = pipeline.build_pipeline()
        deploy = next(s for s in stages if s["action"] == "deploy")
        disciplines = {g["discipline"] for g in deploy["gates"]}
        # both devops and engineering gate the road to prod.
        assert {"devops", "engineering"} <= disciplines

    def test_qa_signoff_guards_release(self):
        stages = pipeline.build_pipeline()
        release = next(s for s in stages if s["action"] == "release")
        assert any(g["gate"] == "qa-signoff" for g in release["gates"])


class TestPipelineCLI:
    def test_pipeline_renders(self, capsys):
        from proto_gear_pkg import cli_commands

        rc = cli_commands.cmd_pipeline(_args(json=False))
        out = capsys.readouterr().out
        assert rc == 0
        assert "Supervision pipeline" in out
        assert "prod-approval" in out
        assert "qa-signoff" in out
        assert "converge" in out  # the deploy convergence annotation

    def test_pipeline_json(self, capsys):
        from proto_gear_pkg import cli_commands

        rc = cli_commands.cmd_pipeline(_args(json=True))
        data = json.loads(capsys.readouterr().out)
        assert rc == 0
        gates = [g["gate"] for s in data["stages"] for g in s["gates"]]
        assert "prod-approval" in gates and "qa-signoff" in gates
