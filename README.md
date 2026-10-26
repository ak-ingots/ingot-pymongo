# ingot-pymongo

[![ci](https://github.com/ak-ingots/ingot-pymongo/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/ak-ingots/ingot-pymongo/actions/workflows/ci.yml)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](https://github.com/ak-ingots/ingot-pymongo/blob/main/LICENSE)

<!-- Links must be absolute: this README also renders on PyPI. -->

Integration of PyMongo, the official driver of MongoDB, into Ingots
applications, on its asynchronous API. An addon of
[Ingots](https://github.com/ak-ingots/ingots).

**Status:** pre-alpha, on ingots 0.31: the clients of MongoDB servers, as
components.

## For Consumers

### Install

```sh
uv add ingot-pymongo
```

### Integrate

An application of Ingots has its own configs, settings, logging and project;
each takes the class of the addon among its bases:

```python
# app/project.py
import typing as t

from ingot_pymongo import MongoDbProject
from ingot_pymongo.logging import MongoDbLogging
from ingot_pymongo.settings import MongoDbSettings
from ingot_pymongo.settings.configs import MongoDbConfigs
from ingots.puer import Slot


class AppConfigs(MongoDbConfigs):
    pass


class AppSettings(MongoDbSettings):
    configs = Slot(AppConfigs)


class AppLogging(MongoDbLogging):
    project: "AppProject"


class AppProject(MongoDbProject):
    env_configs_prefix = "APP"
    settings = Slot(AppSettings)
    logging = Slot(AppLogging)
```

With other addons, their classes join the same bases:
`class AppConfigs(HttpConfigs, MongoDbConfigs)`, and so on, as the
[addon guide](https://github.com/ak-ingots/ingots/blob/main/docs/defaults/addon.md)
of Ingots shows. An application with this addon alone may inherit
`MongoDbProject` and nothing more.

The application runs through its own `__main__.py`:

```python
# app/__main__.py
import sys

from ingots.defaults.logging import configure_startup_logging
from ingots.puer.cli import CommandRunner

from .project import AppProject

configure_startup_logging()
sys.exit(CommandRunner(AppProject).run())
```

```sh
uv run python -m app settings list    # the configs, MONGODB_* among them
uv run python -m app components list  # the clients, mongodb.clients.default among them
```

### Use the clients

`project.mongodb.clients.default` is a component holding PyMongo's
asynchronous client on `MONGODB_DEFAULT_*`. Awaited, it creates the client
and pings the server, so that a server out of reach fails the start and not
the first query; the project closes it at the shutdown. It gives PyMongo as
it is: `client`, the `AsyncMongoClient`, and `get_database(name)`.

```python
mongodb = await self.project.mongodb.clients.default
await mongodb.get_database("shop").orders.insert_one({"item": "ingot"})
info = await mongodb.get_database("admin").command("buildInfo")
```

Another server to reach is another client next to the default one: a
subclass of `BaseMongoDbClient` implementing its hooks on configs of its own,
`MONGODB_<NAME>_*`, in a slot of a subclass of `MongoDbClients`, set in a
subclass of `MongoDbUnit` as `clients`; the project takes it as `mongodb`.
The options of PyMongo the configs do not cover, such as `authSource` or
`tls`, come from the hook `_get_options()`. The extras of PyMongo are the
extras of the addon too: `uv add "ingot-pymongo[aws,snappy]"`.

### Configs

Set as environment variables with the prefix of the project
(`APP_MONGODB_DEFAULT_HOST`), in a `--configs-file` or with `--config`.

| Name | Default | Meaning |
|---|---|---|
| `MONGODB_LOGGING_LEVEL` | `INFO` | the level of the logger of the addon, `ingot_pymongo` |
| `MONGODB_DEFAULT_HOST` | `localhost` | the host of the server |
| `MONGODB_DEFAULT_PORT` | `27017` | the port of the server |
| `MONGODB_DEFAULT_USER` | | the user to authenticate as; empty for none |
| `MONGODB_DEFAULT_PASSWORD` | | the password of the user, a secret |
| `MONGODB_DEFAULT_SERVER_SELECTION_TIMEOUT` | `30.0` | the seconds a query waits for the server before it fails |
| `MONGODB_DEFAULT_IS_PING_ON_START` | `True` | whether to ping the server on start |

## Development

Requires [uv](https://docs.astral.sh/uv/), `make` and Docker, for the
MongoDB of the tests; uv fetches the interpreters it needs.

```sh
make                 # the target list
make check           # everything CI runs: lint, test, coverage, wheel-test, integration, cl-check
make format          # black
make all             # build the sdist and the wheel into dist/
```

- Every change users should know about adds a news fragment to `changelog.d/`
  (see [its README](https://github.com/ak-ingots/ingot-pymongo/blob/main/changelog.d/README.md)).
- A release is a pull request setting the version (`uv version X.Y.Z`) and
  collating the changelog (`make cl-build VERSION=X.Y.Z`), then the tag
  `vX.Y.Z` on `main`: the `release` workflow publishes the tested build to
  TestPyPI, tests it as installed from there (`make index-test`), then
  publishes it to PyPI. Run by hand, it rehearses on TestPyPI only.
