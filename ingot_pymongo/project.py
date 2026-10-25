"""The project of the addon: what an application inherits from."""

__all__ = ("MongoDbProject",)

from ingots.defaults import Project
from ingots.puer import Slot

from .logging import MongoDbLogging
from .settings import MongoDbSettings


class MongoDbProject(Project):
    """
    The project of the defaults with the addon's :class:`MongoDbSettings` and
    :class:`MongoDbLogging`. An application inherits from it and sets its own
    ``env_configs_prefix``; the addon run on its own (``python -m ingot_pymongo``)
    keeps the prefix of the defaults, ``INGOT``.
    """

    settings = Slot(MongoDbSettings)
    logging = Slot(MongoDbLogging)
