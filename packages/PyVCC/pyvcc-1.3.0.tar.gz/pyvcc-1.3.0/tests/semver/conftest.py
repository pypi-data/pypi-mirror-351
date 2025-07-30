import pytest
from pyvcc import SemVer


@pytest.fixture
def initial_version() -> SemVer:
    return SemVer(0, 1, 0)


# Conventional feature commits
@pytest.fixture
def feat_commit():
    return ("feat", "feat: Add new user authentication API")


@pytest.fixture
def feat_breaking_with_exclamation():
    return ("feat!", "feat!: Redesign API endpoint structure")


@pytest.fixture
def feat_breaking_with_text():
    return (
        "feat",
        """feat: Migrate to new database schema

BREAKING CHANGE: Database schema has changed and requires migration""",
    )


# Conventional fix commits
@pytest.fixture
def fix_commit():
    return ("fix", "fix: Resolve login error on Safari")


@pytest.fixture
def fix_commit_with_body():
    return (
        "fix",
        """fix: Fix memory leak in background process

The background process was not properly releasing resources
when tasks completed.""",
    )


@pytest.fixture
def fix_breaking_with_exclamation():
    return ("fix!", "fix!: Change authentication flow completely")


# Other conventional commits
@pytest.fixture
def chore_commit():
    return ("chore", "chore: Update dependencies")


@pytest.fixture
def docs_commit():
    return ("docs", "docs: Update README installation instructions")


@pytest.fixture
def style_commit():
    return ("style", "style: Format code according to new style guide")


@pytest.fixture
def refactor_commit():
    return ("refactor", "refactor: Simplify user management functions")


@pytest.fixture
def test_commit():
    return ("test", "test: Add new test cases for payment processing")


@pytest.fixture
def ci_commit():
    return ("ci", "ci: Update GitHub Actions workflow")


@pytest.fixture
def build_commit():
    return ("build", "build: Migrate to Webpack 5")


@pytest.fixture
def perf_commit():
    return ("perf", "perf: Optimize image loading process")


@pytest.fixture
def chore_breaking_commit():
    return (
        "chore!",
        """chore!: Drop support for legacy browsers

This removes polyfills and workarounds for older browsers.""",
    )


# Non-conventional commits
@pytest.fixture
def no_cc_simple_commit():
    return (None, "Added new feature")


@pytest.fixture
def no_cc_bug_number_commit():
    return ("Fixed bug", "Fixed bug: #123")


@pytest.fixture
def no_cc_doc_commit_non_conventional():
    return (None, "Updated documentation")
