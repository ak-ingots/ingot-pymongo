"""The configs of the addon, named ``MONGODB_*``."""

__all__ = ("MongoDbConfigs",)

import logging

from ingots.defaults.settings.configs import Configs, LogLevelConfig


class MongoDbConfigs(Configs):
    """The configs of the defaults with those of PyMongo."""

    MONGODB_LOGGING_LEVEL = LogLevelConfig(logging.INFO)
