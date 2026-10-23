# ingot-pymongo

[![ci](https://github.com/ak-ingots/ingot-pymongo/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/ak-ingots/ingot-pymongo/actions/workflows/ci.yml)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](https://github.com/ak-ingots/ingot-pymongo/blob/main/LICENSE)

<!-- Links must be absolute: this README also renders on PyPI. -->

Integration of PyMongo, the official driver of MongoDB, into Ingots
applications, on its asynchronous API. An addon of
[Ingots](https://github.com/ak-ingots/ingots).

```python
import ingot_pymongo


class AppProject(ingot_pymongo.Project):
    env_configs_prefix = "APP"
```

An application with other addons joins the configs, the settings and the
logging instead: `class AppConfigs(HttpConfigs,
ingot_pymongo.settings.configs.Configs)`, and so on, as the addon guide of
Ingots shows. The configs of the addon are named `MONGODB_*`:
`MONGODB_LOGGING_LEVEL` sets the level of its logger, `ingot_pymongo`.

**Status:** pre-alpha. The skeleton of the addon: its project, configs,
settings and logging. Next, the clients of MongoDB servers, as components.

## Development

Requires [uv](https://docs.astral.sh/uv/) and `make`; uv fetches the
interpreters it needs.

```sh
make                 # the target list
make check           # everything CI runs: lint, test, coverage, wheel-test, cl-check
make format          # black
make all             # build the sdist and the wheel into dist/
```

- Every change users should know about adds a news fragment to `changelog.d/`
  (see [its README](https://github.com/ak-ingots/ingot-pymongo/blob/main/changelog.d/README.md)).
- A release is a pull request setting the version (`uv version X.Y.Z`) and
  collating the changelog (`make cl-build VERSION=X.Y.Z`), then the tag
  `vX.Y.Z` on `main`: the `release` workflow publishes the tested build to
  TestPyPI, then to PyPI. Run by hand, it rehearses on TestPyPI only.

## License

[Apache 2.0](https://github.com/ak-ingots/ingot-pymongo/blob/main/LICENSE).
