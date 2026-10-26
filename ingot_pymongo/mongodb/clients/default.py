"""The default MongoDB client of the project."""

__all__ = ("DefaultMongoDbClient",)

import typing as t

from .base import BaseMongoDbClient

if t.TYPE_CHECKING:
    from ingot_pymongo.project import MongoDbProject


class DefaultMongoDbClient(BaseMongoDbClient):
    """The client of the configs ``MONGODB_DEFAULT_*``."""

    project: "MongoDbProject"

    @t.override
    def _get_host(self) -> str:
        return self.project.settings.configs.MONGODB_DEFAULT_HOST

    @t.override
    def _get_port(self) -> int:
        return self.project.settings.configs.MONGODB_DEFAULT_PORT

    @t.override
    def _get_user(self) -> str:
        return self.project.settings.configs.MONGODB_DEFAULT_USER

    @t.override
    def _get_password(self) -> str:
        return self.project.settings.configs.MONGODB_DEFAULT_PASSWORD

    @t.override
    def _get_server_selection_timeout(self) -> float:
        return self.project.settings.configs.MONGODB_DEFAULT_SERVER_SELECTION_TIMEOUT

    @t.override
    def _is_ping_on_start(self) -> bool:
        return self.project.settings.configs.MONGODB_DEFAULT_IS_PING_ON_START
