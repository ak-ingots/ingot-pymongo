# ingot-pymongo Changelog

ingot-pymongo is rewritten from scratch starting with 0.10.0; versions
up to 0.9.0 on TestPyPI are the previous implementation.

<!-- towncrier release notes start -->

## [0.11.0] - 2026-10-26
### Added
- `MongoDbProject` holds `mongodb`, whose `clients.default` is a component holding PyMongo's `AsyncMongoClient` on `MONGODB_DEFAULT_HOST`, `_PORT`, `_USER`, `_PASSWORD` (a secret), `_SERVER_SELECTION_TIMEOUT` and `_IS_PING_ON_START`: awaited, it pings the server, so that a server out of reach fails the start; it gives `client` and `get_database(name)`. Another client extends `BaseMongoDbClient` with configs of its own. The extras of PyMongo are extras of the addon too.

### Changed
- Moved on to ingots 0.31 (`>=0.31.0,<0.32`).
- The classes of the addon take the prefix `MongoDb`: `MongoDbProject` from `ingot_pymongo`, `MongoDbSettings` from `ingot_pymongo.settings`, `MongoDbConfigs` from `ingot_pymongo.settings.configs` and `MongoDbLogging` from `ingot_pymongo.logging`, instead of `Project`, `Settings`, `Configs` and `Logging`.

## [0.10.0] - 2026-10-23
### Added
- Started ingot-pymongo, an addon of Ingots for PyMongo, for `ingots` 0.30.1 and later 0.30 releases. Its skeleton: `Project`, the project of the defaults with the addon's `Settings`, whose `Configs` add `MONGODB_LOGGING_LEVEL`, and `Logging`, which adds the logger `ingot_pymongo` at that level; `python -m ingot_pymongo` runs it on its own. The development automation of the ecosystem comes with it: `make check` (lint, tests on the working tree and on the built wheel for every supported Python, coverage, changelog check), towncrier news fragments, and the `ci` and `release` workflows.
