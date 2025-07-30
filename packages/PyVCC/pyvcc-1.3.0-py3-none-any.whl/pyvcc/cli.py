"""
CLI parsing for pyvc command.
"""

import structlog

from pathlib import Path, PurePath
from pygit2 import Commit
from pygit2.repository import Repository
from pygit2.enums import SortMode

from pyvcc.semver import SemVer


log = structlog.get_logger()


def validate_args(root: str, version: str) -> bool:
    is_valid = True
    repo_path = Path(root) / PurePath(".git")
    if not repo_path.exists():
        is_valid = False
        log.error("repo root does not exist", path=repo_path)

    try:
        SemVer.semver_from_string(version)
    except Exception as e:
        log.error("invalid initial version", error=str(e))
        is_valid = False

    return is_valid


def main(root: str, version: str, start_commit_id: str | None = None) -> str:
    repo_path = Path(root) / PurePath(".git")
    semver = SemVer.semver_from_string(version)

    repo = Repository(str(repo_path))

    log.debug("starting repo walk", start_commit_id=start_commit_id)
    commit_walker = repo.walk(repo.head.target, SortMode.TOPOLOGICAL | SortMode.REVERSE)

    # if start_commit is defined for versioning, skip parents on walk
    if start_commit_id:
        start_commit = repo[start_commit_id]
        if isinstance(start_commit, Commit):
            for parent in start_commit.parent_ids:
                commit_walker.hide(parent)

    for commit in commit_walker:
        message = commit.message
        log.debug("commit", id=commit.id, short=commit.short_id)
        semver.bump_version(message)

    log.debug(f"final version {str(semver)}")
    return str(semver)
