# Project constants
PROJECT = rororo
DOCS_DIR = docs
EXAMPLES_DIR = examples
TESTS_DIR = tests

# Setup PYTHONPATH to have all examples
EXAMPLES_SRC_DIRS = $(addsuffix src, $(wildcard $(EXAMPLES_DIR)/*/))
PYTHONPATH = $(shell echo "$(EXAMPLES_SRC_DIRS)" | tr ' ' ':')

# Project vars
PIP_COMPILE ?= pip-compile
TOX ?= tox

# Docs vars
DOCS_HOST ?= localhost
DOCS_PORT ?= 8240

include python.mk

all: install

.PHONY: clean
clean: clean-python

.PHONY: distclean
distclean: clean distclean-python

.PHONY: docs
docs: install $(DOCS_DIR)/requirements.txt $(DOCS_DIR)/requirements-sphinx.txt
	$(PYTHON_BIN) -m pip install -r $(DOCS_DIR)/requirements-sphinx.txt
	$(PYTHON_BIN) -m sphinx_autobuild --host $(DOCS_HOST) --port $(DOCS_PORT) -b html $(DOCS_DIR)/ $(DOCS_DIR)/_build/

$(DOCS_DIR)/requirements.txt: poetry.lock
	$(POETRY) export -f requirements.txt -o $(DOCS_DIR)/requirements.txt --without-hashes

$(DOCS_DIR)/requirements-sphinx.txt: $(DOCS_DIR)/requirements-sphinx.in
	$(PIP_COMPILE) -Ur --allow-unsafe $(DOCS_DIR)/requirements-sphinx.in

.PHONY: example
example: install
ifeq ($(EXAMPLE),)
	@echo "USAGE: make $@ EXAMPLE=(hobotnica|petstore|simulations|todobackend)"
	@exit 1
else
	PYTHONPATH=$(PYTHONPATH) $(PYTHON_BIN) -m aiohttp.web $(EXAMPLE).app:create_app
endif

.PHONY: install
install: install-python

.PHONY: lint
lint: lint-python

.PHONY: lint-and-test
lint-and-test: lint test

.PHONY: lint-only
lint-only: lint-python-only

.PHONY: list-outdated
list-outdated: list-outdated-python

.PHONY: test
test: install clean validate test-only

.PHONY: test-only
test-only:
	PYTHONPATH=$(PYTHONPATH) TOXENV=$(TOXENV) LEVEL=test $(TOX) $(TOX_ARGS) -- $(TEST_ARGS)

.PHONY: test-%
test-%: install clean
	PYTHONPATH=$(PYTHONPATH) TOXENV=$(subst test-,,$@) LEVEL=test $(TOX) $(TOX_ARGS) -- $(TEST_ARGS)

validate: install
	$(PYTHON_BIN) -m openapi_spec_validator $(EXAMPLES_DIR)/hobotnica/src/hobotnica/openapi.yaml
	$(PYTHON_BIN) -m openapi_spec_validator $(EXAMPLES_DIR)/petstore/src/petstore/petstore-expanded.yaml
	$(PYTHON_BIN) -m openapi_spec_validator $(EXAMPLES_DIR)/simulations/src/simulations/openapi.yaml
	$(PYTHON_BIN) -m openapi_spec_validator $(EXAMPLES_DIR)/todobackend/src/todobackend/openapi.yaml
	$(PYTHON_BIN) -m openapi_spec_validator $(TESTS_DIR)/$(PROJECT)/openapi.json
	$(PYTHON_BIN) -m openapi_spec_validator $(TESTS_DIR)/$(PROJECT)/openapi.yaml
