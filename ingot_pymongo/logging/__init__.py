"""The logging unit of the defaults with the logger of the addon."""

__all__ = ("MongoDbLogging",)

import typing as t

from ingots.defaults.logging import Logging

if t.TYPE_CHECKING:
    from ..project import MongoDbProject


class MongoDbLogging(Logging):
    """
    The logging unit, with the logger of the addon, ``ingot_pymongo``, at
    ``MONGODB_LOGGING_LEVEL``.
    """

    project: "MongoDbProject"

    @t.override
    def build_loggers(self) -> dict[str, dict[str, t.Any]]:
        level = self.project.settings.configs.MONGODB_LOGGING_LEVEL
        addon = {"level": level, "handlers": ["default"], "propagate": False}
        return {**super().build_loggers(), "ingot_pymongo": addon}
