"""The settings unit of the defaults with the configs of the addon."""

__all__ = ("MongoDbSettingsUnit",)

from ingots.defaults.settings import SettingsUnit
from ingots.puer import Slot

from .configs import MongoDbConfigs


class MongoDbSettingsUnit(SettingsUnit):
    """The settings unit, with the addon's :class:`MongoDbConfigs`."""

    configs = Slot(MongoDbConfigs)
