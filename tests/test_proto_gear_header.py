"""
Tests for parse_proto_gear_header — multi-line structured HTML-comment
header parser (PROTO-032).
"""

from pathlib import Path

import pytest

from proto_gear_pkg.module_core.metadata_parser import parse_proto_gear_header


VALID_HEADER = """<!-- proto-gear:header
purpose: Agent orchestration
read-when: First session
priority: required
defines:
  - mandatory-reading-list
  - critical-rules
links:
  - PROJECT_STATUS.md
  - BRANCHING.md
-->
# AGENTS.md
"""


class TestParseProtoGearHeader:
    def test_parses_full_header(self):
        result = parse_proto_gear_header(VALID_HEADER)
        assert result is not None
        assert result["purpose"] == "Agent orchestration"
        assert result["read-when"] == "First session"
        assert result["priority"] == "required"
        assert result["defines"] == ["mandatory-reading-list", "critical-rules"]
        assert result["links"] == ["PROJECT_STATUS.md", "BRANCHING.md"]

    def test_returns_none_when_missing(self):
        assert parse_proto_gear_header("# Just a header\n\nSome content.") is None

    def test_handles_minimal_header(self):
        minimal = "<!-- proto-gear:header\npurpose: x\npriority: optional\n-->\n# Title"
        result = parse_proto_gear_header(minimal)
        assert result == {"purpose": "x", "priority": "optional"}

    def test_returns_none_on_malformed_yaml(self):
        malformed = "<!-- proto-gear:header\npurpose: [unclosed\n-->"
        assert parse_proto_gear_header(malformed) is None

    def test_ignores_content_beyond_search_limit(self):
        late_header = ("filler line\n" * 5000) + VALID_HEADER
        # Default 8 KiB limit — the header is far past it.
        assert parse_proto_gear_header(late_header) is None

    def test_finds_header_when_not_on_first_line(self):
        with_preamble = "<!-- some other comment -->\n\n" + VALID_HEADER
        result = parse_proto_gear_header(with_preamble)
        assert result is not None
        assert result["purpose"] == "Agent orchestration"

    def test_priority_values_accepted(self):
        for prio in ("required", "recommended", "optional", "required-if-exists"):
            header = f"<!-- proto-gear:header\npurpose: x\npriority: {prio}\n-->"
            result = parse_proto_gear_header(header)
            assert result["priority"] == prio


class TestAllPackagedTemplatesHaveHeader:
    """All shipped template files must carry a parsable proto-gear:header."""

    REQUIRED_TEMPLATES = [
        "AGENTS.template.md",
        "PROJECT_STATUS.template.md",
        "BRANCHING.template.md",
        "TESTING.template.md",
        "CONTRIBUTING.template.md",
        "SECURITY.template.md",
        "ARCHITECTURE.template.md",
        "CODE_OF_CONDUCT.template.md",
    ]

    REQUIRED_FIELDS = ("purpose", "read-when", "priority")

    @pytest.mark.parametrize("filename", REQUIRED_TEMPLATES)
    def test_template_has_valid_header(self, filename):
        pkg_dir = Path(__file__).parent.parent / "core" / "proto_gear_pkg"
        path = pkg_dir / filename
        text = path.read_text(encoding="utf-8")
        header = parse_proto_gear_header(text)

        assert header is not None, f"{filename}: missing proto-gear:header"
        for field in self.REQUIRED_FIELDS:
            assert field in header, f"{filename}: header missing '{field}'"
        assert header["priority"] in {
            "required", "recommended", "optional", "required-if-exists"
        }, f"{filename}: invalid priority '{header['priority']}'"
