# ingot-pymongo Changelog

ingot-pymongo is rewritten from scratch starting with 0.10.0; versions
up to 0.9.0 on TestPyPI are the previous implementation.

<!-- towncrier release notes start -->

## [0.10.0] - 2026-10-23
### Added
- Started ingot-pymongo, an addon of Ingots for PyMongo, for `ingots` 0.30.1 and later 0.30 releases. Its skeleton: `Project`, the project of the defaults with the addon's `Settings`, whose `Configs` add `MONGODB_LOGGING_LEVEL`, and `Logging`, which adds the logger `ingot_pymongo` at that level; `python -m ingot_pymongo` runs it on its own. The development automation of the ecosystem comes with it: `make check` (lint, tests on the working tree and on the built wheel for every supported Python, coverage, changelog check), towncrier news fragments, and the `ci` and `release` workflows.
