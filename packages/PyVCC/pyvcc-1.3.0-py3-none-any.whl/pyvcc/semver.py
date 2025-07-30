import re
import sys
import structlog

from enum import Enum, auto

# Python 3.11+ has Self in typing module
if sys.version_info >= (3, 11):
    from typing import Self
else:
    from typing_extensions import Self


log = structlog.get_logger()


class CommitEnum(Enum):
    FEAT = auto()
    FIX = auto()
    BUILD = auto()
    CHORE = auto()
    CI = auto()
    DOCS = auto()
    STYLE = auto()
    REFACTOR = auto()
    PERF = auto()
    TEST = auto()


class BumpEnum(Enum):
    MAJOR = auto()
    MINOR = auto()
    PATCH = auto()
    NO_BUMP = auto()


class SemVer:
    def __init__(self, major: int, minor: int, patch: int):
        self.major = major
        self.minor = minor
        self.patch = patch

        self.log = log

    def __repr__(self):
        return f"{self.major}.{self.minor}.{self.patch}"

    @staticmethod
    def is_breaking_change(type: str, message: str) -> bool:
        """
        SemVer defines that a breaking change is a commit with a type ending in '!'
        OR that contains 'BREAKING CHANGE:' in the messsage body

        # Parameters:
        type (str): Commit message type (feat, fix, chore, etc)
        message (str): commit message content
        """
        return type[-1] == "!" or "BREAKING CHANGE:" in message

    @classmethod
    def semver_from_string(cls, str_version: str) -> Self:
        # TODO: regex?
        list_version = str_version.split(".")
        if len(list_version) != 3:
            # TODO: custom exception
            raise Exception("invalid string formating for semantic versioning")

        major = int(list_version[0])
        minor = int(list_version[1])
        patch = int(list_version[2])
        return cls(major, minor, patch)

    @classmethod
    def bump_type(cls, message: str) -> BumpEnum:
        """
        Given a version number MAJOR.MINOR.PATCH, increment the:

        - MAJOR: version when you make incompatible API changes
        - MINOR: version when you add functionality in a backward compatible manner
        - PATCH: version when you make backward compatible bug fixes
        Additional labels for pre-release and build metadata are available as
        extensions to the MAJOR.MINOR.PATCH format.

        fix: a commit of the type fix patches a bug in your codebase
             (this correlates with PATCH in Semantic Versioning).

        feat: a commit of the type feat introduces a new feature to the codebase
            (this correlates with MINOR in Semantic Versioning).

        BREAKING CHANGE: a commit that has a footer BREAKING CHANGE:, or appends a !
                         after the type/scope, introduces a breaking API change
                         (correlating with MAJOR in Semantic Versioning).
                         A BREAKING CHANGE can be part of commits of any type.

        # Parameters:
        message (str): commit message content
        """

        regex = re.compile(r"[.*]?([a-z]*!?)(\(.*\))?:\s(.*)$")
        bump = BumpEnum.NO_BUMP
        head = message.split("\n")[0]

        parsed_head = regex.search(head)

        if parsed_head is not None:
            commit_type = parsed_head.groups()[0].upper()
            log.debug("trying bump", type=commit_type, message=head)

            if cls.is_breaking_change(commit_type, message):
                bump = BumpEnum.MAJOR
            elif commit_type == CommitEnum.FEAT.name:
                bump = BumpEnum.MINOR
            elif commit_type == CommitEnum.FIX.name:
                bump = BumpEnum.PATCH
            else:
                bump = BumpEnum.NO_BUMP
        else:
            log.error("not in conventional commit spec", message=head)

        return bump

    def bump_version(self, message: str) -> None:
        self.log = self.log.bind(message=message)

        match self.bump_type(message):
            case BumpEnum.MAJOR:
                self.major += 1
                self.minor = 0
                self.patch = 0
                self.log.debug("bump Major")
            case BumpEnum.MINOR:
                self.minor += 1
                self.patch = 0
                self.log.debug("bump Minor")
            case BumpEnum.PATCH:
                self.patch += 1
                self.log.debug("bump Patch")
            case BumpEnum.NO_BUMP:
                self.log.debug("no bump")
