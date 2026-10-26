"""The configs of the addon, named ``MONGODB_*``."""

__all__ = ("MongoDbConfigs",)

import logging

from ingots.defaults.settings.configs import (
    BoolConfig,
    Configs,
    FloatConfig,
    IntConfig,
    LogLevelConfig,
    SecureStrConfig,
    StrConfig,
)


class MongoDbConfigs(Configs):
    """
    The configs of the defaults with those of PyMongo. ``MONGODB_DEFAULT_*``
    are the configs of the default client: another client takes configs of
    its own, ``MONGODB_<NAME>_*``.
    """

    MONGODB_LOGGING_LEVEL = LogLevelConfig(logging.INFO)

    # the default client
    MONGODB_DEFAULT_HOST = StrConfig("localhost")
    MONGODB_DEFAULT_PORT = IntConfig(27017)
    MONGODB_DEFAULT_USER = StrConfig("")  # empty: no authentication
    MONGODB_DEFAULT_PASSWORD = SecureStrConfig("")
    MONGODB_DEFAULT_SERVER_SELECTION_TIMEOUT = FloatConfig(30.0)  # seconds
    MONGODB_DEFAULT_IS_PING_ON_START = BoolConfig(True)
