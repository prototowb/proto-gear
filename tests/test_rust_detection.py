"""
Tests for Rust project detection functionality.
Tests coverage for Cargo.toml and various Rust frameworks.
"""

import pytest
from pathlib import Path
from core.proto_gear_pkg.proto_gear import detect_project_structure


class TestRustDetection:
    """Tests for Rust project detection."""

    def test_rust_cargo_toml_detection(self, tmp_path):
        """Should detect Rust via Cargo.toml file."""
        cargo_toml = """
[package]
name = "my-rust-project"
version = "0.1.0"
edition = "2021"

[dependencies]
"""
        (tmp_path / 'Cargo.toml').write_text(cargo_toml)

        result = detect_project_structure(tmp_path)

        assert result['detected'] is True
        assert result['type'] == 'Rust Project'
        assert result['framework'] is None

    def test_rust_actix_web_detection(self, tmp_path):
        """Should detect Actix Web framework."""
        cargo_toml = """
[package]
name = "actix-app"
version = "0.1.0"
edition = "2021"

[dependencies]
actix-web = "4.0"
"""
        (tmp_path / 'Cargo.toml').write_text(cargo_toml)

        result = detect_project_structure(tmp_path)

        assert result['detected'] is True
        assert result['type'] == 'Rust Project'
        assert result['framework'] == 'Actix Web'

    def test_rust_rocket_detection(self, tmp_path):
        """Should detect Rocket framework."""
        cargo_toml = """
[package]
name = "rocket-app"
version = "0.1.0"
edition = "2021"

[dependencies]
rocket = "0.5"
"""
        (tmp_path / 'Cargo.toml').write_text(cargo_toml)

        result = detect_project_structure(tmp_path)

        assert result['detected'] is True
        assert result['type'] == 'Rust Project'
        assert result['framework'] == 'Rocket'

    def test_rust_axum_detection(self, tmp_path):
        """Should detect Axum framework."""
        cargo_toml = """
[package]
name = "axum-app"
version = "0.1.0"
edition = "2021"

[dependencies]
axum = "0.7"
tokio = { version = "1", features = ["full"] }
"""
        (tmp_path / 'Cargo.toml').write_text(cargo_toml)

        result = detect_project_structure(tmp_path)

        assert result['detected'] is True
        assert result['type'] == 'Rust Project'
        assert result['framework'] == 'Axum'

    def test_rust_warp_detection(self, tmp_path):
        """Should detect Warp framework."""
        cargo_toml = """
[package]
name = "warp-app"
version = "0.1.0"
edition = "2021"

[dependencies]
warp = "0.3"
tokio = { version = "1", features = ["full"] }
"""
        (tmp_path / 'Cargo.toml').write_text(cargo_toml)

        result = detect_project_structure(tmp_path)

        assert result['detected'] is True
        assert result['type'] == 'Rust Project'
        assert result['framework'] == 'Warp'

    def test_rust_tauri_detection(self, tmp_path):
        """Should detect Tauri framework."""
        cargo_toml = """
[package]
name = "tauri-app"
version = "0.1.0"
edition = "2021"

[dependencies]
tauri = { version = "1.0", features = ["api-all"] }
serde_json = "1.0"
serde = { version = "1.0", features = ["derive"] }
"""
        (tmp_path / 'Cargo.toml').write_text(cargo_toml)

        result = detect_project_structure(tmp_path)

        assert result['detected'] is True
        assert result['type'] == 'Rust Project'
        assert result['framework'] == 'Tauri'

    def test_rust_yew_detection(self, tmp_path):
        """Should detect Yew framework."""
        cargo_toml = """
[package]
name = "yew-app"
version = "0.1.0"
edition = "2021"

[dependencies]
yew = "0.21"
"""
        (tmp_path / 'Cargo.toml').write_text(cargo_toml)

        result = detect_project_structure(tmp_path)

        assert result['detected'] is True
        assert result['type'] == 'Rust Project'
        assert result['framework'] == 'Yew'

    def test_rust_priority_over_package_json(self, tmp_path):
        """Cargo.toml should take priority over package.json (wasm-pack scenario)."""
        # Create both Cargo.toml (Rust) and package.json (wasm tooling)
        cargo_toml = """
[package]
name = "wasm-rust-project"
version = "0.1.0"
edition = "2021"

[dependencies]
wasm-bindgen = "0.2"
"""
        (tmp_path / 'Cargo.toml').write_text(cargo_toml)
        (tmp_path / 'package.json').write_text('{"name": "wasm-pack-project"}')

        result = detect_project_structure(tmp_path)

        # Should be detected as Rust, not Node.js
        assert result['type'] == 'Rust Project'

    def test_rust_workspace(self, tmp_path):
        """Should detect Rust workspace."""
        cargo_toml = """
[workspace]
members = ["crate1", "crate2", "crate3"]

[workspace.dependencies]
serde = "1.0"
"""
        (tmp_path / 'Cargo.toml').write_text(cargo_toml)

        result = detect_project_structure(tmp_path)

        assert result['detected'] is True
        assert result['type'] == 'Rust Project'

    def test_rust_framework_precedence(self, tmp_path):
        """First matching framework should be detected."""
        cargo_toml = """
[package]
name = "multi-framework"
version = "0.1.0"
edition = "2021"

[dependencies]
actix-web = "4.0"
rocket = "0.5"
"""
        (tmp_path / 'Cargo.toml').write_text(cargo_toml)

        result = detect_project_structure(tmp_path)

        # Actix Web should be detected first (order in elif chain)
        assert result['framework'] == 'Actix Web'

    def test_rust_malformed_cargo_toml(self, tmp_path):
        """Should handle malformed Cargo.toml gracefully."""
        (tmp_path / 'Cargo.toml').write_text('[ invalid toml )')

        result = detect_project_structure(tmp_path)

        # File exists, so detected as Rust, but framework parsing failed
        assert result['detected'] is True
        assert result['type'] == 'Rust Project'
        assert result['framework'] is None


class TestRustProjectStructure:
    """Tests for Rust project structure detection."""

    def test_rust_with_src_directory(self, tmp_path):
        """Should detect Rust project with src directory."""
        cargo_toml = """
[package]
name = "my-app"
version = "0.1.0"
edition = "2021"
"""
        (tmp_path / 'Cargo.toml').write_text(cargo_toml)
        (tmp_path / 'src').mkdir()
        (tmp_path / 'src' / 'main.rs').write_text('fn main() {}')

        result = detect_project_structure(tmp_path)

        assert result['detected'] is True
        assert 'src' in result['directories']

    def test_rust_with_tests_directory(self, tmp_path):
        """Should detect Rust project with tests directory."""
        cargo_toml = """
[package]
name = "my-lib"
version = "0.1.0"
edition = "2021"
"""
        (tmp_path / 'Cargo.toml').write_text(cargo_toml)
        (tmp_path / 'src').mkdir()
        (tmp_path / 'tests').mkdir()

        result = detect_project_structure(tmp_path)

        assert 'src' in result['directories']
        assert 'tests' in result['directories']

    def test_rust_with_examples_directory(self, tmp_path):
        """Should detect Rust project with examples directory."""
        cargo_toml = """
[package]
name = "my-crate"
version = "0.1.0"
edition = "2021"
"""
        (tmp_path / 'Cargo.toml').write_text(cargo_toml)
        (tmp_path / 'src').mkdir()
        (tmp_path / 'examples').mkdir()
        (tmp_path / 'benches').mkdir()

        result = detect_project_structure(tmp_path)

        assert 'src' in result['directories']
        assert 'examples' in result['directories']
        assert 'benches' in result['directories']


class TestRustEdgeCases:
    """Tests for Rust detection edge cases."""

    def test_empty_cargo_toml(self, tmp_path):
        """Should handle empty Cargo.toml."""
        (tmp_path / 'Cargo.toml').write_text('')

        result = detect_project_structure(tmp_path)

        assert result['detected'] is True
        assert result['type'] == 'Rust Project'

    def test_cargo_toml_with_only_package_section(self, tmp_path):
        """Should detect minimal Cargo.toml."""
        cargo_toml = """
[package]
name = "minimal"
version = "0.1.0"
"""
        (tmp_path / 'Cargo.toml').write_text(cargo_toml)

        result = detect_project_structure(tmp_path)

        assert result['detected'] is True
        assert result['type'] == 'Rust Project'

    def test_rust_binary_vs_library(self, tmp_path):
        """Detection should work for both binary and library crates."""
        # Binary crate
        cargo_toml_bin = """
[package]
name = "my-binary"
version = "0.1.0"
edition = "2021"

[[bin]]
name = "my-app"
path = "src/main.rs"
"""
        (tmp_path / 'Cargo.toml').write_text(cargo_toml_bin)

        result = detect_project_structure(tmp_path)

        assert result['type'] == 'Rust Project'
