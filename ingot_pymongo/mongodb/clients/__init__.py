"""The clients: the MongoDB clients of the project, each a component."""

__all__ = ("BaseMongoDbClient", "DefaultMongoDbClient", "MongoDbClients")

from ingots.puer import Slot, Unit

from .base import BaseMongoDbClient
from .default import DefaultMongoDbClient


class MongoDbClients(Unit):
    """
    The MongoDB clients of the project: :attr:`default` for a start. An
    application with more servers to reach adds clients in a subclass, each
    a subclass of :class:`BaseMongoDbClient` with configs of its own.
    """

    default = Slot(DefaultMongoDbClient)
