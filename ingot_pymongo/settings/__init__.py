"""The settings unit of the defaults with the configs of the addon."""

__all__ = ("MongoDbSettings",)

from ingots.defaults.settings import Settings
from ingots.puer import Slot

from .configs import MongoDbConfigs


class MongoDbSettings(Settings):
    """The settings unit, with the addon's :class:`MongoDbConfigs`."""

    configs = Slot(MongoDbConfigs)
