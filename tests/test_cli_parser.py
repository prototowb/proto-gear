"""Tests for the pg argparse surface (PROTO-050 coverage).

build_parser() is pure command-line definition; these tests parse representative
argv for every command group and assert the resulting namespace, including the
global --module flag (engineering departments) and the init-surface command
(PROTO-048).
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "core"))

from proto_gear_pkg.cli.parser import build_parser


@pytest.fixture
def parser():
    return build_parser()


class TestTopLevel:
    def test_no_args(self, parser):
        args = parser.parse_args([])
        assert args.command is None
        assert args.module is None

    def test_global_module_flag(self, parser):
        args = parser.parse_args(["--module", "qa", "init-surface"])
        assert args.module == "qa"
        assert args.command == "init-surface"

    def test_version_exits(self, parser):
        with pytest.raises(SystemExit):
            parser.parse_args(["--version"])


class TestInit:
    def test_init_flags(self, parser):
        args = parser.parse_args(
            ["init", "--dry-run", "--force", "--with-branching", "--with-capabilities"]
        )
        assert args.command == "init"
        assert args.dry_run and args.force
        assert args.with_branching and args.with_capabilities

    def test_init_ticket_prefix(self, parser):
        args = parser.parse_args(["init", "--ticket-prefix", "APP"])
        assert args.ticket_prefix == "APP"

    def test_init_profile_defaults_to_frontier(self, parser):
        # Plan Phase 3: new inits default to the slim profile.
        args = parser.parse_args(["init"])
        assert args.profile == "frontier"

    def test_init_profile_verbose(self, parser):
        args = parser.parse_args(["init", "--profile", "verbose"])
        assert args.profile == "verbose"

    def test_init_profile_rejects_unknown(self, parser):
        with pytest.raises(SystemExit):
            parser.parse_args(["init", "--profile", "nonsense"])


class TestGuardAndHooks:
    def test_guard_defaults_to_branch(self, parser):
        args = parser.parse_args(["guard"])
        assert args.command == "guard"
        assert args.aspect == "branch"

    def test_guard_protected_repeatable(self, parser):
        args = parser.parse_args(
            ["guard", "branch", "--protected", "main", "--protected", "release"]
        )
        assert args.protected == ["main", "release"]

    def test_hooks_install(self, parser):
        args = parser.parse_args(["hooks", "install", "--force"])
        assert args.command == "hooks"
        assert args.hooks_command == "install"
        assert args.force is True


class TestInitSurface:
    def test_defaults(self, parser):
        args = parser.parse_args(["init-surface"])
        assert args.command == "init-surface"
        assert args.force is False
        assert args.dry_run is False

    def test_flags(self, parser):
        args = parser.parse_args(
            ["--module", "qa", "init-surface", "--force", "--dry-run"]
        )
        assert args.force and args.dry_run


class TestCapabilities:
    def test_list_filters(self, parser):
        args = parser.parse_args(["capabilities", "list", "--type", "skill", "--json"])
        assert args.capabilities_command == "list"
        assert args.type == "skill"
        assert args.json

    def test_show(self, parser):
        args = parser.parse_args(["capabilities", "show", "testing"])
        assert args.capabilities_command == "show"
        assert args.name == "testing"

    def test_tree(self, parser):
        args = parser.parse_args(["capabilities", "tree", "skills/testing"])
        assert args.capability_id == "skills/testing"

    def test_bad_type_rejected(self, parser):
        with pytest.raises(SystemExit):
            parser.parse_args(["capabilities", "list", "--type", "bogus"])


class TestAgent:
    def test_create(self, parser):
        args = parser.parse_args(
            ["agent", "create", "my-agent", "--template", "backend-developer"]
        )
        assert args.agent_command == "create"
        assert args.name == "my-agent"
        assert args.template == "backend-developer"

    def test_clone(self, parser):
        args = parser.parse_args(["agent", "clone", "src", "dst"])
        assert args.source == "src" and args.destination == "dst"


class TestOrchestration:
    def test_list_json(self, parser):
        args = parser.parse_args(["orchestration", "list", "--json"])
        assert args.orchestration_command == "list" and args.json

    def test_show(self, parser):
        args = parser.parse_args(["orchestration", "show", "driver-reviewer"])
        assert args.orchestration_command == "show"
        assert args.id == "driver-reviewer"

    def test_install(self, parser):
        args = parser.parse_args(["orchestration", "install", "core-flex"])
        assert args.orchestration_command == "install" and args.id == "core-flex"

    def test_paradigm_alias(self, parser):
        args = parser.parse_args(["paradigm", "list"])
        assert args.command in ("orchestration", "paradigm")
        assert args.orchestration_command == "list"

    def test_bare_group(self, parser):
        args = parser.parse_args(["orchestration"])
        assert args.orchestration_command is None


class TestTicket:
    def test_create(self, parser):
        args = parser.parse_args(["ticket", "create", "Fix bug", "--type", "bugfix"])
        assert args.ticket_command == "create"
        assert args.title == "Fix bug"
        assert args.type == "bugfix"

    def test_update_requires_status(self, parser):
        with pytest.raises(SystemExit):
            parser.parse_args(["ticket", "update", "PROTO-1"])

    def test_update(self, parser):
        args = parser.parse_args(
            ["ticket", "update", "PROTO-1", "--status", "COMPLETED"]
        )
        assert args.status == "COMPLETED"

    def test_list(self, parser):
        args = parser.parse_args(["ticket", "list", "--status", "PENDING", "--json"])
        assert args.status == "PENDING" and args.json


class TestModule:
    def test_list(self, parser):
        args = parser.parse_args(["module", "list", "--json"])
        assert args.module_command == "list" and args.json

    def test_show(self, parser):
        args = parser.parse_args(["module", "show", "engineering"])
        assert args.module_command == "show" and args.name == "engineering"


class TestMiscCommands:
    def test_status_json(self, parser):
        assert parser.parse_args(["status", "--json"]).json

    def test_suggest(self, parser):
        args = parser.parse_args(["suggest", "fix", "login", "bug", "--limit", "5"])
        assert args.prose == ["fix", "login", "bug"]
        assert args.limit == 5

    def test_doctor(self, parser):
        args = parser.parse_args(["doctor", "--fix", "--all", "--json"])
        assert args.fix and args.all and args.json

    def test_sync_context(self, parser):
        assert parser.parse_args(["sync-context", "--dry-run"]).dry_run

    def test_sync_indexes(self, parser):
        assert parser.parse_args(["sync-indexes", "--dry-run"]).dry_run

    def test_context(self, parser):
        assert parser.parse_args(["context", "--regenerate"]).regenerate

    def test_update(self, parser):
        args = parser.parse_args(["update", "PROJECT_STATUS.md", "--dry-run"])
        assert args.templates == ["PROJECT_STATUS.md"]
        assert args.dry_run
