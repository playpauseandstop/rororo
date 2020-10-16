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
PIP_COMPILE ?= pip-compile
TOX ?= tox

# Docs vars
DOCS_HOST ?= localhost
DOCS_PORT ?= 8240

include python.mk

all: install

clean: clean-python

distclean: clean distclean-python

docs: $(DOCS_DIR)/requirements.txt $(DOCS_DIR)/requirements-sphinx.txt
	$(PYTHON_BIN) -m pip install -r $(DOCS_DIR)/requirements-sphinx.txt
	$(PYTHON_BIN) -m sphinx_autobuild --host $(DOCS_HOST) --port $(DOCS_PORT) -b html $(DOCS_DIR)/ $(DOCS_DIR)/_build/

$(DOCS_DIR)/requirements.txt: poetry.lock
	$(POETRY) export -f requirements.txt -o $(DOCS_DIR)/requirements.txt

$(DOCS_DIR)/requirements-sphinx.txt: $(DOCS_DIR)/requirements-sphinx.in
	$(PIP_COMPILE) -Ur --allow-unsafe --generate-hashes $(DOCS_DIR)/requirements-sphinx.in

example: install
ifeq ($(EXAMPLE),)
	@echo "USAGE: make EXAMPLE=(hobotnica|petstore) example"
	@exit 1
else
	PYTHON_BINPATH=examples $(PYTHON_BIN) -m aiohttp.web $(EXAMPLE).app:create_app
endif

install: install-python

lint: lint-python

lint-only: lint-python-only

list-outdated: list-outdated-python

test: install lint clean test-only

test-only:
	TOXENV=$(TOXENV) $(TOX) $(TOX_ARGS) -- $(TEST_ARGS)

validate: install
	$(PYTHON_BIN) -m openapi_spec_validator examples/hobotnica/openapi.yaml
	$(PYTHON_BIN) -m openapi_spec_validator examples/petstore/petstore-expanded.yaml
	$(PYTHON_BIN) -m openapi_spec_validator examples/simulations/openapi.yaml
	$(PYTHON_BIN) -m openapi_spec_validator examples/todobackend/openapi.yaml
	$(PYTHON_BIN) -m openapi_spec_validator tests/openapi.json
	$(PYTHON_BIN) -m openapi_spec_validator tests/openapi.yaml
