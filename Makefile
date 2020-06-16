.PHONY: \
	clean \
	distclean \
	docs \
	example \
	install \
	lint \
	lint-only \
	list-outdated \
	test \
	test-only \
	validate

# Project constants
PROJECT = rororo
DOCS_DIR = ./docs

# Project vars
POETRY ?= poetry
PRE_COMMIT ?= pre-commit
PYTHON ?= $(POETRY) run python
TOX ?= tox

# Docs vars
DOCS_HOST ?= localhost
DOCS_PORT ?= 8240

all: install

clean:
	find . \( -name __pycache__ -o -type d -empty \) -exec rm -rf {} + 2> /dev/null

distclean: clean
	rm -rf build/ dist/ *.egg*/ .venv/

docs: install
	$(PYTHON) -m pip install -r docs/requirements.txt
	$(POETRY) run sphinx-autobuild -B -H $(DOCS_HOST) -p $(DOCS_PORT) -b html $(DOCS_DIR)/ $(DOCS_DIR)/_build/

example: install
ifeq ($(EXAMPLE),)
	# USAGE: make EXAMPLE=(hobotnica|petstore) example
	@exit 1
else
	PYTHONPATH=examples $(PYTHON) -m aiohttp.web $(EXAMPLE).app:create_app
endif

install: .install
.install: pyproject.toml poetry.toml poetry.lock
	$(POETRY) install
	touch $@

lint: install lint-only

lint-only:
	SKIP=$(SKIP) $(PRE_COMMIT) run --all $(HOOK)

list-outdated: install
	$(POETRY) show -o

poetry.toml:
	$(POETRY) config --local virtualenvs.create true
	$(POETRY) config --local virtualenvs.in-project true

test: install clean lint validate test-only

test-only:
	TOXENV=$(TOXENV) $(TOX) $(TOX_ARGS) -- $(TEST_ARGS)

validate: install
	$(PYTHON) -m openapi_spec_validator examples/hobotnica/openapi.yaml
	$(PYTHON) -m openapi_spec_validator examples/petstore/petstore-expanded.yaml
	$(PYTHON) -m openapi_spec_validator examples/simulations/openapi.yaml
	$(PYTHON) -m openapi_spec_validator examples/todobackend/openapi.yaml
	$(PYTHON) -m openapi_spec_validator tests/openapi.json
	$(PYTHON) -m openapi_spec_validator tests/openapi.yaml
