import pytest
from pyvcc.semver import SemVer


def test_bump_major(feat_breaking_with_text: tuple[str, str]):
    version = SemVer(0, 1, 0)
    message = feat_breaking_with_text[1]
    version.bump_version(message)
    assert str(version) == "1.0.0"


def test_bump_major_2(feat_breaking_with_exclamation: tuple[str, str]):
    version = SemVer(0, 1, 0)
    message = feat_breaking_with_exclamation[1]
    version.bump_version(message)
    assert str(version) == "1.0.0"


def test_bump_minor(feat_commit: tuple[str, str]):
    version = SemVer(0, 1, 0)
    message = feat_commit[1]
    version.bump_version(message)
    assert str(version) == "0.2.0"


def test_bump_patch(fix_commit: tuple[str, str]):
    version = SemVer(0, 1, 0)
    message = fix_commit[1]
    version.bump_version(message)
    assert str(version) == "0.1.1"


def test_no_bump(docs_commit: tuple[str, str]):
    version = SemVer(0, 1, 0)
    message = docs_commit[1]
    version.bump_version(message)
    assert str(version) == "0.1.0"


def test_no_bump_not_conventional(no_cc_bug_number_commit: tuple[str, str]):
    version = SemVer(1, 0, 0)
    message = no_cc_bug_number_commit[1]
    version.bump_version(message)
    assert str(version) == "1.0.0"


def test_no_bump_no_type(no_cc_simple_commit: tuple[str, str]):
    version = SemVer(1, 0, 0)
    message = no_cc_simple_commit[1]
    version.bump_version(message)
    assert str(version) == "1.0.0"


def test_bump_merge():
    version = SemVer(1, 0, 0)
    message = "Merged feat!(xyz): break"
    version.bump_version(message)
    assert str(version) == "2.0.0"


def test_bump_merge2():
    version = SemVer(1, 0, 0)
    message = "Merged feat(xyz): break"
    version.bump_version(message)
    assert str(version) == "1.1.0"


def test_bump_multiple():
    """patch -> minor -> major"""
    version = SemVer(0, 1, 0)

    version.bump_version("fix: Fix login bug")
    assert str(version) == "0.1.1"

    version.bump_version("feat: Add new feature")
    assert str(version) == "0.2.0"

    version.bump_version("feat!: Complete API redesign")
    assert str(version) == "1.0.0"


def test_bump_multiple2():
    """patch -> patch -> major"""
    version = SemVer(0, 1, 0)

    version.bump_version("fix: Fix login bug")
    assert str(version) == "0.1.1"

    version.bump_version("fix: Fix logout bug")
    assert str(version) == "0.1.2"

    version.bump_version("feat: New API\n\nBREAKING CHANGE: Complete API redesign")
    assert str(version) == "1.0.0"


def test_bump_multiple3():
    """patch -> major -> minor"""
    version = SemVer(0, 1, 0)

    version.bump_version("fix: Fix login bug")
    assert str(version) == "0.1.1"

    version.bump_version("feat!: Complete API redesign")
    assert str(version) == "1.0.0"

    version.bump_version("feat: Add new feature")
    assert str(version) == "1.1.0"


def test_bump_multiple4():
    """patch -> patch -> minor"""
    version = SemVer(0, 1, 0)

    version.bump_version("fix: Fix login bug")
    assert str(version) == "0.1.1"

    version.bump_version("fix: Fix logout bug")
    assert str(version) == "0.1.2"

    version.bump_version("feat: Add new feature")
    assert str(version) == "0.2.0"


def test_bump_multiple5():
    """patch -> patch -> minor"""
    version = SemVer(0, 1, 0)

    version.bump_version("fix: Fix login bug")
    assert str(version) == "0.1.1"

    version.bump_version("fix: Fix logout bug")
    assert str(version) == "0.1.2"

    version.bump_version("Fix logout bug")
    assert str(version) == "0.1.2"

    version.bump_version("feat(asdf): Add new feature")
    assert str(version) == "0.2.0"

    version.bump_version("Merge feat!(asdf): break new feature")
    assert str(version) == "1.0.0"


def test_parse_semver_str():
    version = SemVer.semver_from_string("1.1.0")
    assert str(version) == "1.1.0"


def test_parse_semver_invalid_str():
    with pytest.raises(Exception) as excinfo:
        SemVer.semver_from_string("1.1.0.2")
    assert "invalid string" in str(excinfo)
