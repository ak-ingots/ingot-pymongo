import contextlib
import io
import os
import socket
import typing as t
import unittest
from unittest import mock

from ingot_pymongo import MongoDbProject
from ingot_pymongo.mongodb.clients import DefaultMongoDbClient, base
from ingots.puer.cli import CommandRunner
from pymongo import AsyncMongoClient
from pymongo.asynchronous.database import AsyncDatabase
from pymongo.errors import ServerSelectionTimeoutError


def find_closed_port() -> int:
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        port: int = sock.getsockname()[1]
    return port


class ClientTestCase(unittest.IsolatedAsyncioTestCase):
    @t.override
    async def asyncSetUp(self) -> None:
        self.enterContext(
            mock.patch.dict(
                os.environ,
                {
                    "INGOT_MONGODB_DEFAULT_HOST": "127.0.0.1",
                    "INGOT_MONGODB_DEFAULT_PORT": str(find_closed_port()),
                    "INGOT_MONGODB_DEFAULT_SERVER_SELECTION_TIMEOUT": "0.1",
                    "INGOT_IS_PRINT_CONFIGS": "off",
                },
                clear=True,
            )
        )
        # the logging is not under test: keep the handlers of the test run
        self.enterContext(mock.patch("logging.config.dictConfig"))
        self.created = self.enterContext(
            mock.patch.object(base, "AsyncMongoClient", wraps=AsyncMongoClient)
        )

    async def start(self) -> tuple[MongoDbProject, DefaultMongoDbClient]:
        project = MongoDbProject()
        await project._configure()
        self.addAsyncCleanup(project._do_shut_down)
        return project, await project.mongodb.clients.default

    async def test_an_unreachable_server_fails_the_start(self) -> None:
        with (
            mock.patch.object(AsyncMongoClient, "close", autospec=True) as close,
            self.assertRaises(ServerSelectionTimeoutError),
        ):
            await self.start()
        close.assert_awaited_once()

    async def test_the_ping_on_start_connects(self) -> None:
        # a server of its own is in tests.test_server; the ping alone here
        ping = mock.AsyncMock(return_value={"ok": 1.0})
        with (
            mock.patch.object(AsyncDatabase, "command", ping),
            self.assertLogs("ingot_pymongo", "INFO") as logs,
        ):
            _, mongodb = await self.start()
        ping.assert_awaited_once_with("ping")
        self.assertIn(f"{mongodb!r}: connected", logs.output[0])

    async def test_without_the_ping_the_client_connects_later(self) -> None:
        os.environ["INGOT_MONGODB_DEFAULT_IS_PING_ON_START"] = "off"
        with self.assertLogs("ingot_pymongo", "INFO") as logs:
            _, mongodb = await self.start()
        self.assertIn("to connect at the first query", logs.output[0])
        self.assertIsInstance(mongodb.client, AsyncMongoClient)
        database = mongodb.get_database("shop")
        self.assertEqual(database.name, "shop")
        self.assertIs(database.client, mongodb.client)

    async def test_the_configs_reach_the_client(self) -> None:
        os.environ.update(
            {
                "INGOT_MONGODB_DEFAULT_IS_PING_ON_START": "off",
                "INGOT_MONGODB_DEFAULT_USER": "app",
                "INGOT_MONGODB_DEFAULT_PASSWORD": "p@ss:w/rd",
            }
        )
        with self.assertLogs("ingot_pymongo", "INFO") as logs:
            _, mongodb = await self.start()
        self.created.assert_called_once_with(
            host="127.0.0.1",
            port=int(os.environ["INGOT_MONGODB_DEFAULT_PORT"]),
            username="app",
            password="p@ss:w/rd",
            serverSelectionTimeoutMS=100.0,
        )
        self.assertIn(
            f"{mongodb!r}: to connect at the first query as app", logs.output[0]
        )
        self.assertNotIn("p@ss", "".join(logs.output))

    async def test_without_a_user_there_is_no_authentication(self) -> None:
        os.environ.update(
            {
                "INGOT_MONGODB_DEFAULT_IS_PING_ON_START": "off",
                "INGOT_MONGODB_DEFAULT_PASSWORD": "unused",
            }
        )
        await self.start()
        kwargs = self.created.call_args.kwargs
        self.assertIsNone(kwargs["username"])
        self.assertIsNone(kwargs["password"])

    async def test_the_options_hook_adds_options_of_pymongo(self) -> None:
        os.environ["INGOT_MONGODB_DEFAULT_IS_PING_ON_START"] = "off"
        with mock.patch.object(
            DefaultMongoDbClient, "_get_options", return_value={"appname": "app"}
        ):
            _, mongodb = await self.start()
        self.assertEqual(self.created.call_args.kwargs["appname"], "app")
        self.assertEqual(
            mongodb.client.options.pool_options.metadata["application"], {"name": "app"}
        )

    async def test_the_shutdown_closes_the_client(self) -> None:
        os.environ["INGOT_MONGODB_DEFAULT_IS_PING_ON_START"] = "off"
        project, mongodb = await self.start()
        with (
            mock.patch.object(
                mongodb.client, "close", wraps=mongodb.client.close
            ) as close,
            self.assertLogs("ingot_pymongo", "INFO") as logs,
        ):
            await project._do_shut_down()
        close.assert_awaited_once_with()
        self.assertIn(f"{mongodb!r}: closed", logs.output[-1])

    async def test_the_client_tells_its_server(self) -> None:
        os.environ["INGOT_MONGODB_DEFAULT_IS_PING_ON_START"] = "off"
        _, mongodb = await self.start()
        port = os.environ["INGOT_MONGODB_DEFAULT_PORT"]
        self.assertEqual(repr(mongodb), f"<DefaultMongoDbClient 127.0.0.1:{port}>")


class ComponentTestCase(unittest.TestCase):
    def run_project(self, *argv: str) -> str:
        with (
            mock.patch.dict(os.environ, clear=True),
            mock.patch("logging.config.dictConfig"),
            contextlib.redirect_stdout(io.StringIO()) as out,
        ):
            code = CommandRunner(
                MongoDbProject, ["--config", "IS_PRINT_CONFIGS=off", *argv]
            ).run()
        self.assertEqual(code, 0)
        return out.getvalue()

    def test_the_client_is_a_component_of_the_project(self) -> None:
        self.assertIn(
            "mongodb.clients.default: DefaultMongoDbClient, shutdown order 8\n",
            self.run_project("components", "list"),
        )

    def test_the_password_is_a_secret(self) -> None:
        out = self.run_project(
            "--config", "MONGODB_DEFAULT_PASSWORD=p@ss", "settings", "list"
        )
        self.assertIn("MONGODB_DEFAULT_PASSWORD = ***\n", out)
        self.assertNotIn("p@ss", out)
