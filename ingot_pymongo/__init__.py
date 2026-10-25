"""
ingot-pymongo: Integration of PyMongo, the official driver of MongoDB, into
Ingots applications, on its asynchronous API. An application inherits from
:class:`MongoDbProject`, or joins the units of the addon, ``settings`` and
``logging``, with those of its other addons.
"""

__all__ = ("MongoDbProject",)

from .project import MongoDbProject
