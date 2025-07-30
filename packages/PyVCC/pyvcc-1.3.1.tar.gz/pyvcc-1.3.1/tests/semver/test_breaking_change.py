from pyvcc.semver import SemVer


def test_feat_normal(feat_commit):
    commit_type, message = feat_commit
    assert SemVer.is_breaking_change(commit_type, message) is False


def test_fix_normal(fix_commit):
    commit_type, message = fix_commit
    assert SemVer.is_breaking_change(commit_type, message) is False


def test_feat_with_exclamation(feat_breaking_with_exclamation):
    commit_type, message = feat_breaking_with_exclamation
    assert SemVer.is_breaking_change(commit_type, message) is True


def test_fix_with_exclamation(fix_breaking_with_exclamation):
    commit_type, message = fix_breaking_with_exclamation
    assert SemVer.is_breaking_change(commit_type, message) is True


def test_with_breaking_change_text(feat_breaking_with_text):
    commit_type, message = feat_breaking_with_text
    assert SemVer.is_breaking_change(commit_type, message) is True


def test_chore_normal(chore_commit):
    commit_type, message = chore_commit
    assert SemVer.is_breaking_change(commit_type, message) is False


def test_docs_normal(docs_commit):
    commit_type, message = docs_commit
    assert SemVer.is_breaking_change(commit_type, message) is False


def test_chore_with_exclamation():
    commit_type, message = ("chore!", "Major dependency update")
    assert SemVer.is_breaking_change(commit_type, message) is True
