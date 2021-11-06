.PHONY: \
	clean \
	distclean \
	docs \
	example \
	install \
	lint \
	lint-and-test \
	lint-only \
	list-outdated \
	test \
	test-only \
	validate

# Project constants
PROJECT = rororo
DOCS_DIR = ./docs
EXAMPLES_DIR = ./examples
TESTS_DIR = ./tests

# Setup PYTHONPATH to have all examples
EXAMPLES_SRC_DIRS = $(addsuffix src, $(wildcard $(EXAMPLES_DIR)/*/))
PYTHONPATH = $(shell echo "$(EXAMPLES_SRC_DIRS)" | tr ' ' ':')

# Project vars
PIP_COMPILE ?= pip-compile
TOX ?= python3 -m tox

# Docs vars
DOCS_HOST ?= localhost
DOCS_PORT ?= 8240

include python.mk

all: install

clean: clean-python

distclean: clean distclean-python

docs: install $(DOCS_DIR)/requirements.txt $(DOCS_DIR)/requirements-sphinx.txt
	$(PYTHON_BIN) -m pip install -r $(DOCS_DIR)/requirements-sphinx.txt
	$(PYTHON_BIN) -m sphinx_autobuild --host $(DOCS_HOST) --port $(DOCS_PORT) -b html $(DOCS_DIR)/ $(DOCS_DIR)/_build/

$(DOCS_DIR)/requirements.txt: poetry.lock
	$(POETRY) export -f requirements.txt -o $(DOCS_DIR)/requirements.txt --without-hashes

$(DOCS_DIR)/requirements-sphinx.txt: $(DOCS_DIR)/requirements-sphinx.in
	$(PIP_COMPILE) -Ur --allow-unsafe $(DOCS_DIR)/requirements-sphinx.in

example: install
ifeq ($(EXAMPLE),)
	@echo "USAGE: make EXAMPLE=(hobotnica|petstore|simulations|todobackend) example"
	@exit 1
else
	PYTHONPATH=$(PYTHONPATH) $(PYTHON_BIN) -m aiohttp.web $(EXAMPLE).app:create_app
endif

install: install-python

lint: lint-python

lint-and-test: lint test

lint-only: lint-python-only

list-outdated: list-outdated-python

test: install clean validate test-only

test-only:
	PYTHONPATH=$(PYTHONPATH) TOXENV=$(TOXENV) $(TOX) $(TOX_ARGS) -- $(TEST_ARGS)

validate: install
	$(PYTHON_BIN) -m openapi_spec_validator $(EXAMPLES_DIR)/hobotnica/src/hobotnica/openapi.yaml
	$(PYTHON_BIN) -m openapi_spec_validator $(EXAMPLES_DIR)/petstore/src/petstore/petstore-expanded.yaml
	$(PYTHON_BIN) -m openapi_spec_validator $(EXAMPLES_DIR)/simulations/src/simulations/openapi.yaml
	$(PYTHON_BIN) -m openapi_spec_validator $(EXAMPLES_DIR)/todobackend/src/todobackend/openapi.yaml
	$(PYTHON_BIN) -m openapi_spec_validator $(TESTS_DIR)/$(PROJECT)/openapi.json
	$(PYTHON_BIN) -m openapi_spec_validator $(TESTS_DIR)/$(PROJECT)/openapi.yaml
