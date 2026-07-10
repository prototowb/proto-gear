"""Tests for engineering project detection (PROTO-050 coverage).

detect_project_structure inspects marker files to classify a project's stack and
framework. These tests drop the relevant marker(s) in a temp dir and assert the
detected type/framework across the supported ecosystems.
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "core"))

from proto_gear_pkg.modules.engineering import detection


def _mk(tmp_path, files):
    for name, content in files.items():
        p = tmp_path / name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")
    return tmp_path


@pytest.mark.parametrize(
    "files,exp_type,exp_framework",
    [
        ({"angular.json": "{}"}, "Node.js Project", "Angular"),
        ({"svelte.config.js": "export default {}"}, "Node.js Project", "SvelteKit"),
        (
            {"Cargo.toml": '[dependencies]\nactix-web = "4"'},
            "Rust Project",
            "Actix Web",
        ),
        ({"Cargo.toml": '[dependencies]\nrocket = "0.5"'}, "Rust Project", "Rocket"),
        ({"Cargo.toml": '[dependencies]\naxum = "0.7"'}, "Rust Project", "Axum"),
        ({"Cargo.toml": '[dependencies]\ntauri = "1"'}, "Rust Project", "Tauri"),
        ({"go.mod": "require github.com/gin-gonic/gin v1"}, "Go Project", "Gin"),
        ({"go.mod": "require github.com/labstack/echo v4"}, "Go Project", "Echo"),
        (
            {"package.json": '{"dependencies":{"next":"14"}}'},
            "Node.js Project",
            "Next.js",
        ),
        (
            {"package.json": '{"dependencies":{"react":"18"}}'},
            "Node.js Project",
            "React",
        ),
        (
            {"package.json": '{"dependencies":{"express":"4"}}'},
            "Node.js Project",
            "Express.js",
        ),
        (
            {"package.json": '{"dependencies":{"@nestjs/core":"10"}}'},
            "Node.js Project",
            "NestJS",
        ),
        (
            {"pom.xml": "<project><dependency>spring-boot</dependency></project>"},
            "Java Project",
            "Spring Boot",
        ),
        ({"build.gradle.kts": "// kotlin\nio.ktor"}, "Kotlin Project", "Ktor"),
        ({"manage.py": "# django", "app.py": "x=1"}, "Python Project", "Django"),
        ({"requirements.txt": "flask==3.0"}, "Python Project", "Flask"),
    ],
)
def test_detect_stack(tmp_path, files, exp_type, exp_framework):
    info = detection.detect_project_structure(_mk(tmp_path, files))
    assert info["detected"] is True
    assert info["type"] == exp_type
    assert info["framework"] == exp_framework


def test_ruby_rails(tmp_path):
    _mk(tmp_path, {"Gemfile": "gem 'rails'", "config/application.rb": "Rails"})
    info = detection.detect_project_structure(tmp_path)
    assert info["type"] == "Ruby Project"
    assert info["framework"] == "Ruby on Rails"


def test_csharp_aspnet(tmp_path):
    _mk(
        tmp_path,
        {
            "app.csproj": "<Project><PackageReference Include='Microsoft.AspNetCore'/></Project>"
        },
    )
    info = detection.detect_project_structure(tmp_path)
    assert info["type"] == "C# Project"
    assert info["framework"] == "ASP.NET"


def test_undetected_empty(tmp_path):
    info = detection.detect_project_structure(tmp_path)
    assert info["detected"] is False
    assert "Basic project structure" in info["structure_summary"]


def test_directories_listed(tmp_path):
    (tmp_path / "src").mkdir()
    (tmp_path / ".hidden").mkdir()
    info = detection.detect_project_structure(tmp_path)
    assert "src" in info["directories"]
    assert ".hidden" not in info["directories"]


class TestExistingEnvironment:
    def test_fresh_project(self, tmp_path):
        env = detection.detect_existing_environment(tmp_path)
        assert env["is_existing"] is False

    def test_existing_with_agents(self, tmp_path):
        (tmp_path / "AGENTS.md").write_text("x", encoding="utf-8")
        env = detection.detect_existing_environment(tmp_path)
        assert env["is_existing"] is True


class TestGitConfig:
    def test_returns_dict(self):
        cfg = detection.detect_git_config()
        assert isinstance(cfg, dict)
