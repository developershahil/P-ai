#!/usr/bin/env python3
"""Create and push a safe backup branch using the next semantic version.

Flow:
1) Detect current git branch and working status.
2) Compute next semantic version and create branch: safe/vX.Y.Z.
3) If there are staged changes and no unstaged/untracked changes, commit staged changes.
4) Push backup branch to origin.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from dataclasses import dataclass
from typing import Iterable, List, Optional, Tuple

SEMVER_RE = re.compile(r"^v?(\d+)\.(\d+)\.(\d+)$")


class GitCommandError(RuntimeError):
    """Raised when a git command fails."""


@dataclass
class WorkingStatus:
    staged: List[str]
    unstaged: List[str]
    untracked: List[str]

    @property
    def is_clean(self) -> bool:
        return not self.staged and not self.unstaged and not self.untracked


def run_git(args: Iterable[str], *, check: bool = True) -> subprocess.CompletedProcess[str]:
    """Run a git command and optionally raise a rich error on failure."""
    cmd = ["git", *args]
    result = subprocess.run(cmd, text=True, capture_output=True)
    if check and result.returncode != 0:
        stderr = result.stderr.strip() or "(no stderr)"
        raise GitCommandError(f"Command failed: {' '.join(cmd)}\n{stderr}")
    return result


def current_branch() -> str:
    """Return current branch name."""
    result = run_git(["rev-parse", "--abbrev-ref", "HEAD"])
    branch = result.stdout.strip()
    if not branch:
        raise GitCommandError("Could not detect current branch.")
    return branch


def get_working_status() -> WorkingStatus:
    """Parse `git status --porcelain` into staged/unstaged/untracked groups."""
    result = run_git(["status", "--porcelain"])
    staged: List[str] = []
    unstaged: List[str] = []
    untracked: List[str] = []

    for line in result.stdout.splitlines():
        if not line:
            continue
        code = line[:2]
        path = line[3:] if len(line) > 3 else ""
        if code == "??":
            untracked.append(path)
            continue
        if code[0] != " ":
            staged.append(path)
        if code[1] != " ":
            unstaged.append(path)

    return WorkingStatus(staged=staged, unstaged=unstaged, untracked=untracked)


def parse_semver(tag: str) -> Optional[Tuple[int, int, int]]:
    """Parse vX.Y.Z or X.Y.Z into numeric tuple."""
    m = SEMVER_RE.match(tag.strip())
    if not m:
        return None
    return int(m.group(1)), int(m.group(2)), int(m.group(3))


def next_version_tag() -> str:
    """Find next patch version based on existing semantic tags, defaulting to v0.0.1."""
    result = run_git(["tag", "--list"])
    versions = [v for t in result.stdout.splitlines() if (v := parse_semver(t)) is not None]
    if not versions:
        return "v0.0.1"
    major, minor, patch = max(versions)
    return f"v{major}.{minor}.{patch + 1}"


def branch_exists(branch_name: str) -> bool:
    """Check if a local branch exists."""
    result = run_git(["show-ref", "--verify", f"refs/heads/{branch_name}"], check=False)
    return result.returncode == 0


def create_backup_branch(branch_name: str) -> None:
    """Create and switch to backup branch if not already present."""
    if branch_exists(branch_name):
        raise GitCommandError(f"Backup branch already exists locally: {branch_name}")
    run_git(["checkout", "-b", branch_name])


def commit_staged_if_safe(message: str, status: WorkingStatus) -> None:
    """Commit staged changes when there are no unstaged/untracked changes.

    This keeps backup commits predictable and avoids accidentally mixing incomplete work.
    """
    if not status.staged:
        print("ℹ️ No staged changes to commit.")
        return

    if status.unstaged or status.untracked:
        print("⚠️ Skipping commit: unstaged or untracked files are present.")
        return

    run_git(["commit", "-m", message])
    print("✅ Staged changes committed.")


def push_branch(branch_name: str) -> None:
    """Push backup branch to origin."""
    run_git(["push", "-u", "origin", branch_name])


def print_status(branch: str, status: WorkingStatus) -> None:
    """Print clear summary for users."""
    print(f"📌 Current branch: {branch}")
    if status.is_clean:
        print("✅ Working tree is clean.")
        return

    print("📂 Working tree status:")
    if status.staged:
        print(f"  - staged: {len(status.staged)} file(s)")
    if status.unstaged:
        print(f"  - unstaged: {len(status.unstaged)} file(s)")
    if status.untracked:
        print(f"  - untracked: {len(status.untracked)} file(s)")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create and push safe backup branch with semver.")
    parser.add_argument(
        "--message",
        default="chore: safe backup snapshot",
        help="Commit message used when committing staged changes.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    original_branch = ""
    try:
        original_branch = current_branch()
        status = get_working_status()
        print_status(original_branch, status)

        version = next_version_tag()
        backup_branch = f"safe/{version}"
        print(f"🧾 Next semantic version: {version}")
        print(f"🌿 Backup branch to create: {backup_branch}")

        create_backup_branch(backup_branch)
        print(f"✅ Created branch {backup_branch}")

        # Re-check status after branch switch.
        status_on_backup = get_working_status()
        commit_staged_if_safe(args.message, status_on_backup)

        push_branch(backup_branch)
        print(f"🚀 Pushed {backup_branch} to origin")
        return 0

    except GitCommandError as exc:
        print(f"❌ {exc}")
        if original_branch:
            # Best effort to go back.
            run_git(["checkout", original_branch], check=False)
        return 1
    except Exception as exc:  # fallback for unexpected errors
        print(f"❌ Unexpected error: {exc}")
        if original_branch:
            run_git(["checkout", original_branch], check=False)
        return 1


if __name__ == "__main__":
    sys.exit(main())
