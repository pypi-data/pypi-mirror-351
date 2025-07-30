from pygit2 import Commit
import pytest
from pygit2.repository import Repository

from pyvcc.cli import run, validate_args
from pyvcc.semver import BumpEnum, SemVer


class MockCommit:
    def __init__(self, message, id, short_id):
        self.message = message
        self.id = id
        self.short_id = short_id


def test_run_invalid_path():
    with pytest.raises(Exception):
        run("/(7", "1.0.0")


def test_run_invalid_semver():
    with pytest.raises(Exception):
        run(".", "1.0.0.2")


def test_validate_version():
    assert validate_args(".", "1.0.a") is False


def test_validate_path():
    assert validate_args("/(??", "1.1.1") is False


def test_validate_true():
    assert validate_args(".", "1.2.3") is True


def test_single_commit(monkeypatch):
    def mock_walk(*args, **kwargs):  # noqa
        return [MockCommit(message="feat: x", id="123456789", short_id="1234567")]

    monkeypatch.setattr(Repository, "walk", mock_walk)

    assert run(".", "1.0.0") == "1.1.0"


def test_two_commits(monkeypatch):
    def mock_walk(*args, **kwargs):  # noqa
        return [
            MockCommit(message="feat: x", id="123456789", short_id="1234567"),
            MockCommit(message="feat: y", id="234456789", short_id="2344567"),
        ]

    monkeypatch.setattr(Repository, "walk", mock_walk)

    assert run(".", "1.0.0") == "1.2.0"


def test_head_bump_commit():
    repo = Repository(".git")
    commit = repo[repo.head.target]

    if isinstance(commit, Commit):
        message = commit.message
        match SemVer.bump_type(message):
            case BumpEnum.MAJOR:
                assert run(".", "1.0.0", str(repo.head.target)) == "2.0.0"
            case BumpEnum.MINOR:
                assert run(".", "1.0.0", str(repo.head.target)) == "1.1.0"
            case BumpEnum.PATCH:
                assert run(".", "1.0.0", str(repo.head.target)) == "1.0.1"
            case BumpEnum.NO_BUMP:
                assert run(".", "1.0.0", str(repo.head.target)) == "1.0.0"
