"""
The client against a real MongoDB: run by ``make integration``, which starts
the server of ``docker-compose.yml`` and sets ``INGOT_PYMONGO_TEST_PORT``;
skipped without it.
"""

import os
import typing as t
import unittest
from unittest import mock

from ingot_pymongo import MongoDbProject
from ingot_pymongo.mongodb.clients import DefaultMongoDbClient
from pymongo.errors import OperationFailure

PORT = os.environ.get("INGOT_PYMONGO_TEST_PORT")


@unittest.skipUnless(PORT, "no MongoDB: run make integration")
class ServerTestCase(unittest.IsolatedAsyncioTestCase):
    @t.override
    async def asyncSetUp(self) -> None:
        self.enterContext(
            mock.patch.dict(
                os.environ,
                {
                    "INGOT_MONGODB_DEFAULT_HOST": "127.0.0.1",
                    "INGOT_MONGODB_DEFAULT_PORT": str(PORT),
                    "INGOT_MONGODB_DEFAULT_USER": "ingot",
                    "INGOT_MONGODB_DEFAULT_PASSWORD": "p@ss:w/rd",
                    "INGOT_MONGODB_DEFAULT_SERVER_SELECTION_TIMEOUT": "5",
                    "INGOT_IS_PRINT_CONFIGS": "off",
                },
                clear=True,
            )
        )
        # the logging is not under test: keep the handlers of the test run
        self.enterContext(mock.patch("logging.config.dictConfig"))

    async def start(self) -> DefaultMongoDbClient:
        project = MongoDbProject()
        await project._configure()
        self.addAsyncCleanup(project._do_shut_down)
        return await project.mongodb.clients.default

    async def test_the_server_tells_its_build(self) -> None:
        mongodb = await self.start()
        info = await mongodb.get_database("admin").command("buildInfo")
        self.assertRegex(info["version"], r"^\d+\.\d+\.\d+")

    async def test_the_server_tells_its_status(self) -> None:
        mongodb = await self.start()
        status = await mongodb.get_database("admin").command("serverStatus")
        self.assertEqual(status["ok"], 1.0)
        self.assertGreaterEqual(status["connections"]["current"], 1)

    async def test_a_document_is_written_and_read(self) -> None:
        mongodb = await self.start()
        orders = mongodb.get_database("ingot_pymongo_test").orders
        self.addAsyncCleanup(mongodb.client.drop_database, "ingot_pymongo_test")
        await orders.insert_one({"item": "ingot"})
        self.assertEqual((await orders.find_one({}, {"_id": 0})), {"item": "ingot"})

    async def test_a_wrong_password_fails_the_start(self) -> None:
        os.environ["INGOT_MONGODB_DEFAULT_PASSWORD"] = "wrong"
        with self.assertRaises(OperationFailure):
            await self.start()
