"""
Guard — enforce repo invariants outside the prompt (steering-plan Phase 5).

The framework repeats one hard invariant everywhere: *never commit directly to
`main`.* Prose compliance is model-dependent; a check that exits non-zero is not.
This module is that check — a small, deterministic primitive a git hook, CI job,
or agent can call. It fits Principle 4 (*agents act, `pg` audits*): `pg guard`
reports a violation and returns a non-zero code; it never rewrites history.

Keep the prose NEVER-line as documentation of the rule; this is its enforcement.
"""

import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

# Only `main` (and the common `master` alias) is protected. `development` is
# deliberately open — see BRANCHING.md / the project conventions.
DEFAULT_PROTECTED_BRANCHES = ("main", "master")


@dataclass
class GuardResult:
    ok: bool
    message: str
    branch: Optional[str] = None

    @property
    def exit_code(self) -> int:
        return 0 if self.ok else 1


def current_branch(cwd: str = ".") -> Optional[str]:
    """Return the current git branch name, or None (not a repo / detached HEAD)."""
    try:
        result = subprocess.run(
            ["git", "symbolic-ref", "--quiet", "--short", "HEAD"],
            capture_output=True,
            text=True,
            timeout=5,
            cwd=str(cwd),
        )
    except (OSError, subprocess.SubprocessError):
        return None
    if result.returncode != 0:
        return None  # not a repo, or detached HEAD (no symbolic ref)
    branch = result.stdout.strip()
    return branch or None


def check_protected_branch(
    protected: Optional[List[str]] = None, cwd: str = "."
) -> GuardResult:
    """Fail when HEAD is on a protected branch.

    Passes (ok=True) when the branch can't be determined — no git repo or a
    detached HEAD — so the guard never blocks a legitimate action it can't reason
    about (e.g. a rebase). It only fails on a *known* protected branch.
    """
    names = [n for n in (protected or DEFAULT_PROTECTED_BRANCHES) if n]
    branch = current_branch(cwd)
    if branch is None:
        return GuardResult(
            ok=True,
            message="No branch to check (not a git repo or detached HEAD).",
            branch=None,
        )
    if branch in names:
        return GuardResult(
            ok=False,
            branch=branch,
            message=(
                f"Refusing to proceed on protected branch '{branch}'. "
                f"It lands only via a reviewed PR — branch off first "
                f"(e.g. `git switch -c feature/TICKET-XXX-desc`)."
            ),
        )
    return GuardResult(
        ok=True, branch=branch, message=f"On '{branch}' (not protected)."
    )
