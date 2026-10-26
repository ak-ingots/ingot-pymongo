"""The base of the MongoDB clients: a component holding a client of PyMongo."""

__all__ = ("BaseMongoDbClient",)

import logging
import typing as t

from ingots.puer import Component
from pymongo import AsyncMongoClient

if t.TYPE_CHECKING:
    from pymongo.asynchronous.database import AsyncDatabase

logger = logging.getLogger(__name__)

Document: t.TypeAlias = dict[str, t.Any]


class BaseMongoDbClient(Component):
    """
    A client of a MongoDB server: the connection pool of PyMongo's
    asynchronous :class:`~pymongo.AsyncMongoClient`, given as it is. Await
    it before use, as any component of the project::

        mongodb = await self.project.mongodb.clients.default
        await mongodb.get_database("shop").orders.insert_one({...})

    Configured, it creates the client and, unless told otherwise, pings the
    server, so that a server out of reach fails the start and not the first
    query; shut down, it closes the client.

    A client takes its settings from the hooks, which a subclass implements:
    :meth:`_get_host`, :meth:`_get_port`, :meth:`_get_user`,
    :meth:`_get_password`, :meth:`_get_server_selection_timeout` and
    :meth:`_is_ping_on_start`; :meth:`_get_options` adds options of PyMongo.
    """

    SHUTDOWN_ORDER = 8

    _client: AsyncMongoClient[Document]

    @t.final
    @property
    def client(self) -> AsyncMongoClient[Document]:
        """The client of PyMongo, once configured."""
        return self._client

    @t.override
    def __repr__(self) -> str:
        return f"<{type(self).__qualname__} {self._get_host()}:{self._get_port()}>"

    def get_database(self, name: str) -> "AsyncDatabase[Document]":
        """
        A database of the server by its name; ``admin`` for the commands of
        the server itself.
        """
        return self._client.get_database(name)

    @t.override
    async def _configure(self) -> None:
        user = self._get_user()
        client: AsyncMongoClient[Document] = AsyncMongoClient(
            host=self._get_host(),
            port=self._get_port(),
            username=user or None,
            password=self._get_password() if user else None,
            serverSelectionTimeoutMS=self._get_server_selection_timeout() * 1000,
            **self._get_options(),
        )
        as_user = f" as {user}" if user else ""
        if self._is_ping_on_start():
            try:
                await client.admin.command("ping")
            except Exception:
                await client.close()
                raise
            logger.info("%r: connected%s", self, as_user)
        else:
            logger.info("%r: to connect at the first query%s", self, as_user)
        self._client = client

    @t.override
    async def _shut_down(self) -> None:
        await self._client.close()
        logger.info("%r: closed", self)

    def _get_host(self) -> str:
        """The host of the server."""
        raise NotImplementedError(f"{type(self).__qualname__}._get_host")

    def _get_port(self) -> int:
        """The port of the server."""
        raise NotImplementedError(f"{type(self).__qualname__}._get_port")

    def _get_user(self) -> str:
        """The user to authenticate as; empty for no authentication."""
        raise NotImplementedError(f"{type(self).__qualname__}._get_user")

    def _get_password(self) -> str:
        """The password of the user."""
        raise NotImplementedError(f"{type(self).__qualname__}._get_password")

    def _get_server_selection_timeout(self) -> float:
        """The seconds a query waits for a server to reach before it fails."""
        raise NotImplementedError(
            f"{type(self).__qualname__}._get_server_selection_timeout"
        )

    def _is_ping_on_start(self) -> bool:
        """Whether to ping the server when configured."""
        raise NotImplementedError(f"{type(self).__qualname__}._is_ping_on_start")

    def _get_options(self) -> dict[str, t.Any]:
        """
        Other options of :class:`~pymongo.AsyncMongoClient`, such as
        ``authSource`` or ``tls``: none by default.
        """
        return {}
