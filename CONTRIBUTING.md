<!-- proto-gear:header
purpose: dev environment setup + branch/commit conventions + PR checklist for proto-gear contributors
read-when: before opening a PR or first time setting up the repo locally
priority: optional
defines:
  - getting-started
  - branching
  - commits
  - testing
  - pull-requests
  - dogfooding
  - release-process
links:
  - SECURITY.md
  - CODE_OF_CONDUCT.md
  - docs/dev/branching-strategy.md
  - docs/dev/project-structure.md
  - docs/dev/release-workflow.md
-->

# Contributing to Proto Gear

Thanks for your interest in contributing. Proto Gear is a small Python CLI that generates AI-agent collaboration templates; contributions of any size are welcome. This page is the *quick path*. Authoritative process docs live in `docs/dev/` and are linked inline.

## Getting Started

```bash
git clone https://github.com/<your-fork>/proto-gear
cd proto-gear
pip install -e .[dev]    # editable install + dev deps
pytest                    # run the test suite
pg init --dry-run         # smoke test the CLI
```

Editable install means changes to `core/proto_gear_pkg/**` take effect immediately — no reinstall needed.

### Project layout

The canonical reference is `docs/dev/project-structure.md`. Short version:

| Path | Contents |
|------|----------|
| `core/proto_gear_pkg/` | All shippable Python + templates. **Edit here.** |
| `tests/` | Pytest suite |
| `docs/user/` | End-user guides |
| `docs/dev/` | Contributor and design docs |
| `dev/` | Local scripts, archived analyses |

Do not create files directly in `core/` — only `core/proto_gear_pkg/` ships in the package.

## Branching

Proto Gear uses a `main` + `development` model for new work, with hotfixes branching from `main`. See `docs/dev/branching-strategy.md` for the full spec; the rules below are the minimum to start.

- **Branch from**: `development` for features and bugfixes; `main` for hotfixes.
- **Never commit directly** to `main` or `development`.
- **Branch naming**:
  - `feature/PROTO-XXX-short-description`
  - `bugfix/PROTO-XXX-short-description`
  - `hotfix/vX.Y.Z-short-description`
  - `docs/topic`
  - `refactor/component-description`

Ticket IDs use the `PROTO-` prefix and live in `PROJECT_STATUS.md`. Create one with:

```bash
pg ticket create "Title" --type feature
```

## Commits

Conventional Commits format, enforced by review:

```
<type>(<scope>): <subject>

<optional body>

<optional footer>
```

- **types**: `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `build`, `ci`, `chore`, `revert`
- **scopes**: `cli`, `agent`, `git`, `test`, `state`, `config`, `docs`, `setup`, `structure`
- **subject**: imperative mood, lowercase, no trailing period, ≤72 chars
- **footer**: `Closes PROTO-XXX` when a commit completes a ticket

Atomic commits are preferred — one logical change per commit. Avoid "fix stuff" / "wip" messages.

## Testing

- **Run**: `pytest` (or `pytest -q` for terse output)
- **Coverage**: `pytest --cov=core --cov-report=term-missing`
- **Lint**: `python -m flake8 core/`
- **Type-check** (optional): `python -m mypy core/`

The bar for new code is: tests added for the new path, full suite still green, and `pg init --dry-run` exits cleanly. Pre-existing failures in `tests/test_template_generation.py` (27 of them) are tracked as a follow-up and can be ignored for unrelated PRs.

### Test layout

- **Unit tests**: `tests/test_<module>.py` — match the module name in `core/proto_gear_pkg/`.
- **Integration tests**: `tests/test_cli_integration.py`, `tests/test_essential_integration.py`.
- Fixtures use `tmp_path` from pytest; do not write to the real working directory.

## Pull Requests

PR checklist:

- [ ] Branch name follows the convention above
- [ ] Title matches commit format: `<type>(<scope>): <subject>`
- [ ] `PROJECT_STATUS.md` updated if the change closes or advances a ticket
- [ ] Tests added or updated
- [ ] `pytest -q` is green locally
- [ ] No direct edits inside `<!-- proto-gear:agent-context begin/end -->` regions — regenerate via `pg sync-context` instead
- [ ] If you changed any template (`core/proto_gear_pkg/*.template.md`), `pg init --dry-run` still works in a scratch directory
- [ ] PR description references the ticket: `Closes PROTO-XXX`

PRs land squashed by default. Force-pushes to a feature branch during review are fine; force-pushes to `main` or `development` are not.

## Dogfooding

Proto Gear uses itself for project management. This means:

- `pg status` shows our current sprint and active tickets.
- `pg suggest "<task>"` ranks our installed skills/workflows/commands against any prose description.
- `pg doctor` audits our own AGENT_CONTEXT.md and host configs for drift.
- `pg sync-context` regenerates AGENT_CONTEXT.md plus the managed regions in `CLAUDE.md`, `.cursorrules`, `.windsurfrules`, `.github/copilot-instructions.md`.

When you modify a template under `core/proto_gear_pkg/*.template.md`, run `pg sync-context` so our own dogfood files stay current. Commit the regenerated files alongside the template change in the same PR.

## Release Process

Releases are coordinated by maintainers, but contributors should know the rough shape:

1. Bump version in `pyproject.toml` and `core/proto_gear_pkg/__init__.py` (single source of truth — see `CLAUDE.md` for the version management contract).
2. Update `CHANGELOG.md`.
3. Tag and create a GitHub release with notes.
4. Update `PROJECT_STATUS.md`.

Full procedure: `docs/dev/release-workflow.md`. **Every tagged release must have a corresponding GitHub release**; this is non-negotiable.

## Reporting Issues

- **Bugs / feature requests**: GitHub issues.
- **Security**: see `SECURITY.md` — do not file public issues for vulnerabilities.
- **Behaviour you'd like to discuss**: GitHub Discussions or open a draft PR with notes.

## Code of Conduct

By participating you agree to abide by `CODE_OF_CONDUCT.md` (Contributor Covenant 2.1). Report violations to team@protogear.dev.

## License

Proto Gear is MIT-licensed. By submitting a PR you agree your contribution is licensed under the same terms. No CLA is required.
