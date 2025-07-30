"""
Entry point for running the package as a module.
"""

import logging
import os
import structlog
import sys
import argparse
from pyvcc.cli import main, validate_args


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="PyVC", description=__doc__)
    parser.add_argument("--root", type=str, default=".", required=False)
    parser.add_argument("--initial-version", type=str, required=False, default="0.1.0")
    parser.add_argument("--initial-commit", type=str, required=False, default="")
    parser.add_argument("--verbose", "-v", action="store_true", required=False)
    parser.add_argument("--silent", "-s", action="store_true", required=False)

    args = parser.parse_args()
    root = os.getenv(key="PYVC_REPO_ROOT", default=args.root)
    version = os.getenv(key="PYVC_INITIAL_VERSION", default=args.initial_version)
    commit = os.getenv(key="PYVC_INITIAL_COMMIT", default=args.initial_commit)
    if not validate_args(root=root, version=version):
        sys.exit(1)

    log_level = logging.INFO
    if args.verbose:
        log_level = logging.DEBUG
    if args.silent:
        log_level = logging.CRITICAL
    structlog.configure(
        processors=[
            structlog.dev.set_exc_info,
            structlog.processors.add_log_level,
            structlog.processors.StackInfoRenderer(),
            structlog.dev.ConsoleRenderer(colors=True),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(log_level),
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )

    version = main(root, version, commit)
    sys.stdout.write(version)
