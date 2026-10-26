"""The MongoDB unit: the clients of the project."""

__all__ = ("MongoDbUnit",)

from ingots.puer import Slot, Unit

from .clients import MongoDbClients


class MongoDbUnit(Unit):
    """
    MongoDB in the project: :attr:`clients`, the clients of its servers. An
    application with more clients declares ``clients = Slot(AppMongoDbClients)``
    in a subclass of this unit.
    """

    clients = Slot(MongoDbClients)
