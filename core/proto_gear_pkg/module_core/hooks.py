"""
Git hook installation (steering-plan Phase 5).

Installs the bundled branch-guard ``pre-commit`` hook so the "never commit to
`main`" invariant is enforced locally, not just documented. No-clobber by
default: an existing pre-commit hook is never silently overwritten — the caller
is told to chain ``pg guard branch`` into it (or pass ``force``).
"""

import stat
import subprocess
from pathlib import Path
from typing import Optional

# Marker string present in the bundled hook; used to detect prior installs.
BRANCH_GUARD_MARKER = "proto-gear:branch-guard"


def bundled_hook_path() -> Path:
    """Path to the packaged pre-commit hook script."""
    from ..paths import package_root

    return package_root() / "hooks" / "pre-commit"


def git_hooks_dir(cwd: str = ".") -> Optional[Path]:
    """Resolve the repo's git hooks directory, or None when not a git repo."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--git-path", "hooks"],
            capture_output=True,
            text=True,
            timeout=5,
            cwd=str(cwd),
        )
    except (OSError, subprocess.SubprocessError):
        return None
    if result.returncode != 0:
        return None
    rel = result.stdout.strip()
    if not rel:
        return None
    hooks = Path(rel)
    if not hooks.is_absolute():
        hooks = Path(cwd) / hooks
    return hooks


def _make_executable(path: Path) -> None:
    try:
        path.chmod(path.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    except (OSError, NotImplementedError):
        pass  # Windows / restricted filesystems — git still runs sh hooks


def install_pre_commit(cwd: str = ".", force: bool = False) -> dict:
    """Install the bundled branch-guard pre-commit hook.

    Returns ``{"status": ..., "path": <str|None>}``:
      - ``not-a-repo``      — no git repo here
      - ``installed``       — hook created
      - ``already-present`` — an existing hook already contains the guard
      - ``exists-different``— a different pre-commit hook exists (chain it or --force)
      - ``overwritten``     — existing hook replaced (force=True; backup written)
    """
    hooks_dir = git_hooks_dir(cwd)
    if hooks_dir is None:
        return {"status": "not-a-repo", "path": None}

    dest = hooks_dir / "pre-commit"
    bundled = bundled_hook_path().read_text(encoding="utf-8")

    if dest.exists():
        existing = dest.read_text(encoding="utf-8", errors="replace")
        if BRANCH_GUARD_MARKER in existing:
            return {"status": "already-present", "path": str(dest)}
        if not force:
            return {"status": "exists-different", "path": str(dest)}
        backup = dest.with_suffix(".pre-guard.bak")
        backup.write_text(existing, encoding="utf-8")
        dest.write_text(bundled, encoding="utf-8")
        _make_executable(dest)
        return {"status": "overwritten", "path": str(dest)}

    hooks_dir.mkdir(parents=True, exist_ok=True)
    dest.write_text(bundled, encoding="utf-8")
    _make_executable(dest)
    return {"status": "installed", "path": str(dest)}
