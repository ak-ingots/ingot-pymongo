# Development entrypoint (uv):
#
#   make              show the target list
#   make check        everything the `ci` workflow runs
#   make all          build the distributions into dist/

SHELL := /bin/bash
.SHELLFLAGS := -eu -o pipefail -c
.DEFAULT_GOAL := help
.DELETE_ON_ERROR:

SRC := ingot_pymongo tests

# Supported interpreters: keep in step with the classifiers and the `wheel`
# matrix in .github/workflows/ci.yml.
PYTHONS ?= 3.14 3.15

# What `cl-check` compares the branch with.
AGAINST ?= origin/main

# Where `index-test` takes the published package from.
INDEX ?= https://test.pypi.org/simple/


##@ Checks

# The `ci` workflow runs exactly these targets, one per job.
.PHONY: check
check: lint test coverage wheel-test integration cl-check  ## Every check: lint, test, coverage, wheel-test, integration, cl-check

.PHONY: lint
lint:  ## black --check, flake8, mypy --strict
	uv run black --check --diff $(SRC)
	uv run flake8 $(SRC)
	uv run mypy $(SRC)

.PHONY: test
test:  ## unittest on the working tree
	uv run python -m unittest discover -s tests -t .

.PHONY: coverage
coverage:  ## unittest on the working tree under coverage; fails below 99%
	uv run coverage run -m unittest discover -s tests -t .
	uv run coverage report

# It needs Docker; a contributor without it runs the other targets of `check`.
.PHONY: integration
integration:  ## tests.test_server against the MongoDB of docker-compose.yml [INGOT_PYMONGO_TEST_PORT=27117]
	trap 'docker compose down --volumes' EXIT; \
		docker compose up --detach --wait --quiet-pull; \
		INGOT_PYMONGO_TEST_PORT=$${INGOT_PYMONGO_TEST_PORT:-27117} \
		uv run python -m unittest -v tests.test_server

# ADR 0003: the tests run against the built wheel, installed into a fresh
# virtualenv, from a copy of tests/ outside the repository, so the package can
# be imported only from the wheel.
.PHONY: wheel-test
wheel-test: all  ## unittest on the built wheel, once per interpreter in PYTHONS
	@$(MAKE) --no-print-directory installed-test WHEEL="$$(echo dist/*.whl)"

# Not a part of `check`: it needs a published version. The `release` workflow
# runs it between TestPyPI and PyPI, on the files it has just published. The
# package alone comes from INDEX, its dependencies from PyPI: anyone may take
# the name of a dependency on TestPyPI. A wheel of the same name in dist/, the
# build the workflow tested, must be the same file. The MongoDB of
# docker-compose.yml runs tests.test_server too.
.PHONY: index-test
index-test:  ## unittest on the wheel of VERSION as INDEX gives it, against MongoDB too (VERSION=X.Y.Z) [INDEX=TestPyPI]
	@test -n "$(VERSION)" || { echo "VERSION=X.Y.Z is required"; exit 1; }
	@tmp=$$(mktemp -d); \
		trap 'rm -rf "$$tmp"; docker compose down --volumes --timeout 1' EXIT; \
		for attempt in $$(seq 30); do \
			uvx --quiet --python $(firstword $(PYTHONS)) pip download --quiet --no-deps --only-binary :all: \
				--index-url $(INDEX) --dest "$$tmp" "ingot-pymongo==$(VERSION)" \
				&& break; \
			[ $$attempt -lt 30 ] || exit 1; \
			echo "== waiting for ingot-pymongo $(VERSION) on $(INDEX)"; \
			sleep 10; \
		done; \
		wheel=$$(echo "$$tmp"/*.whl); \
		if [ -f "dist/$${wheel##*/}" ]; then \
			cmp "$$wheel" "dist/$${wheel##*/}"; \
			echo "== $${wheel##*/} is the build of dist/"; \
		fi; \
		docker compose up --detach --wait --quiet-pull; \
		INGOT_PYMONGO_TEST_PORT=$${INGOT_PYMONGO_TEST_PORT:-27117} \
			$(MAKE) --no-print-directory installed-test WHEEL="$$wheel"

# The tests of tests/ on WHEEL, once per interpreter in PYTHONS.
.PHONY: installed-test
installed-test:
	@test -n "$(WHEEL)" || { echo "WHEEL=path/to.whl is required"; exit 1; }
	@for py in $(PYTHONS); do \
		echo "== $(notdir $(WHEEL)) on Python $$py"; \
		tmp=$$(mktemp -d); \
		trap 'rm -rf "$$tmp"' EXIT; \
		uv venv --quiet --python $$py "$$tmp/venv"; \
		uv pip install --quiet --python "$$tmp/venv/bin/python" "$(WHEEL)"; \
		cp -r tests README.md "$$tmp/"; \
		(cd "$$tmp" && INGOT_PYMONGO_WHEEL_TEST=1 venv/bin/python -m unittest discover -s tests -t .); \
		rm -rf "$$tmp"; \
	done

.PHONY: format
format:  ## Format code with black
	uv run black $(SRC)


##@ Build

.PHONY: all
all:  ## Build the sdist and the wheel into dist/
	rm -rf dist
	uv build --quiet


##@ Changelog

.PHONY: cl-check
cl-check:  ## Fail if the branch adds no news fragment [AGAINST=origin/main]
	uv run --group changelog towncrier check --compare-with $(AGAINST)

.PHONY: cl-preview
cl-preview:  ## Preview the collated changelog [VERSION=X.Y.Z]
	uv run --group changelog towncrier build --draft --version $(or $(VERSION),UNRELEASED)

.PHONY: cl-build
cl-build:  ## Collate changelog.d/ into CHANGELOG.md (VERSION=X.Y.Z)
	@test -n "$(VERSION)" || { echo "VERSION=X.Y.Z is required"; exit 1; }
	uv run --group changelog towncrier build --version $(VERSION) --yes


##@ Housekeeping

.PHONY: clean
clean:  ## Remove build artefacts and caches (keeps the virtualenv)
	rm -rf build dist .mypy_cache .coverage
	find . -name '__pycache__' -type d -prune -exec rm -rf {} +

.PHONY: help
help:  ## Show this help
	@echo "ingot-pymongo - make targets:"
	@awk 'BEGIN {FS = ":.*## "} \
		/^##@ / {printf "\n%s\n", substr($$0, 5); next} \
		/^[a-z][a-zA-Z0-9_-]*:.*## / {printf "  %-12s %s\n", $$1, $$2}' $(MAKEFILE_LIST)
	@echo
	@echo "Variables: PYTHONS, AGAINST, VERSION, INDEX"
