<!-- proto-gear:header
purpose: vulnerability reporting + supported versions + threat model for proto-gear
read-when: before reporting a security issue or auditing the package
priority: optional
defines:
  - supported-versions
  - reporting-a-vulnerability
  - threat-model
  - what-is-not-a-vulnerability
links:
  - CONTRIBUTING.md
  - docs/dev/branching-strategy.md
-->

# Security Policy

## Supported Versions

Proto Gear ships from a single `main` branch. Only the latest minor release receives security patches; older minor versions are not maintained.

| Version | Supported |
|---------|-----------|
| Latest minor (currently 0.9.x) | Yes |
| Older minor releases | No — upgrade required |

## Reporting a Vulnerability

If you believe you've found a security issue in Proto Gear:

- **Preferred**: Open a [GitHub Security Advisory](https://github.com/) on this repository (private, coordinated disclosure).
- **Alternative**: Email **team@protogear.dev** with a description, reproduction steps, and your assessment of severity.

Please do not file public GitHub issues for security problems.

We aim to acknowledge reports within 5 business days and to coordinate a fix or mitigation within 30 days for confirmed high-severity issues. Reporters who follow responsible disclosure will be credited in the release notes unless they request otherwise.

## Threat Model

Proto Gear is a developer-facing CLI that generates markdown documentation templates and indexes capability metadata. It is not a server, daemon, or runtime. The package's attack surface is intentionally small:

- **What `pg` does**: reads YAML metadata, writes markdown files, executes git status checks for project detection.
- **What `pg` does not do**: execute user-supplied capability code, fetch remote content, evaluate template expressions as code, escalate privileges, or open network connections during normal operation.

Capabilities (`.proto-gear/`) are inert markdown and YAML. Proto Gear parses metadata.yaml with PyYAML's safe loader. Capabilities are documentation that AI agents read; they are not executed by `pg` itself.

### In scope for security review

- The `pg` CLI (`core/proto_gear_pkg/proto_gear.py` and all imported modules).
- Template rendering and placeholder substitution.
- Capability metadata parsing (`capability_metadata.py`, `metadata_parser.py`).
- File writes in user projects (path traversal, permission issues).
- Dependency vulnerabilities surfaced by `pip-audit` against `pyproject.toml`.

### Out of scope

- Vulnerabilities in user-authored or third-party capabilities that ship outside this repository.
- Vulnerabilities in generated `AGENTS.md` / `PROJECT_STATUS.md` / etc. when consumed by downstream AI agents (those are the agent host's responsibility).
- Misconfiguration of a downstream project's git workflow (e.g., direct pushes to `main`).
- The `--dangerously-allow-*` flags exposed by AI agent hosts (e.g. Claude Code's bypass modes) — these are governed by the host, not by Proto Gear.

## What is *not* a Vulnerability

The following behaviors are by design and will not be patched as security issues:

- **`pg init` overwrites existing files in `--force` mode** — documented, explicit user opt-in.
- **`pg sync-context` rewrites managed regions in host config files** — opt-in, region is fenced by `<!-- proto-gear:agent-context begin/end -->` markers.
- **Generated templates include the project directory name** — `os.path.basename(cwd)` is treated as untrusted-but-self-supplied input.
- **Capability metadata files in a project's `.proto-gear/` directory are loaded if present** — this is the intended behavior; vet third-party capability bundles before installing them.

## Security-Relevant Files

| Path | Why it matters |
|------|----------------|
| `core/proto_gear_pkg/capability_metadata.py` | YAML loading boundary — uses `yaml.safe_load` |
| `core/proto_gear_pkg/metadata_parser.py` | Frontmatter + `proto-gear:header` parsing |
| `core/proto_gear_pkg/proto_gear.py` | CLI entry point; argument handling |
| `core/proto_gear_pkg/sync_context.py` | File write boundary for host configs |
| `pyproject.toml` | Declared runtime dependencies |

If you discover a regression in any of the above that increases the attack surface (e.g., a switch to `yaml.load` without a SafeLoader, a path that no longer normalizes user input), please report it.

## Acknowledgements

We thank security researchers who help keep Proto Gear's users safe. Past credits will appear in `CHANGELOG.md` under the relevant release.
