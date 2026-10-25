"""Runs the addon on its own: ``python -m ingot_pymongo logging info``."""

import sys

from ingots.defaults.logging import configure_startup_logging
from ingots.puer.cli import CommandRunner

from .project import MongoDbProject


def main() -> None:
    configure_startup_logging()
    sys.exit(CommandRunner(MongoDbProject).run())


if __name__ == "__main__":
    main()
