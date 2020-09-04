.PHONY: \
	clean \
	clean-egg-info \
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
PYTHON_VERSION = $(shell cat ".python-version")
DOCS_DIR = ./docs
VENV_DIR = ./.venv

# Project vars
PIP_COMPILE ?= pip-compile
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

clean-egg-info:
	find . \( -name *.egg-info -a -type d \) -exec rm -rf {} + 2> /dev/null

distclean: clean
	rm -rf build/ dist/ *.egg*/ .venv/

docs: $(DOCS_DIR)/requirements.txt $(DOCS_DIR)/requirements-sphinx.txt
	$(PYTHON) -m pip install -r $(DOCS_DIR)/requirements-sphinx.txt
	$(PYTHON) -m sphinx_autobuild --host $(DOCS_HOST) --port $(DOCS_PORT) -b html $(DOCS_DIR)/ $(DOCS_DIR)/_build/

$(DOCS_DIR)/requirements.txt: poetry.lock
	$(POETRY) export -f requirements.txt -o $(DOCS_DIR)/requirements.txt

$(DOCS_DIR)/requirements-sphinx.txt: $(DOCS_DIR)/requirements-sphinx.in
	$(PIP_COMPILE) -Ur --allow-unsafe --generate-hashes $(DOCS_DIR)/requirements-sphinx.in

ensure-venv: .python-version
	if [ -d "$(VENV_DIR)" -a "$$('$(VENV_DIR)/bin/python3' --version)" != "Python $(PYTHON_VERSION)" ]; then rm -rf $(VENV_DIR)/; fi

example: install
ifeq ($(EXAMPLE),)
	# USAGE: make EXAMPLE=(hobotnica|petstore) example
	@exit 1
else
	PYTHONPATH=examples $(PYTHON) -m aiohttp.web $(EXAMPLE).app:create_app
endif

install: .install
.install: .python-version poetry.toml poetry.lock
	touch $@

lint: install lint-only

lint-only:
	SKIP=$(SKIP) $(PRE_COMMIT) run --all $(HOOK)

list-outdated: install
	$(POETRY) show -o

poetry.lock: pyproject.toml
	@$(MAKE) -s clean-egg-info ensure-venv
	$(POETRY) install
	touch $@

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
