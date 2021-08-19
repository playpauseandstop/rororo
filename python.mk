.PHONY: \
	build-python \
	build-python-only \
	clean-egg-info \
	clean-python \
	distclean-python \
	ensure-venv \
	install-python \
	install-python-only \
	lint-python \
	lint-python-only \
	list-outdated-python \
	python-version \
	test-python \
	test-python-only \
	test-python-setup \
	test-python-teardown

PYTHON_DIST_DIR = ./dist
PYTHON_VERSION = $(shell cat .python-version)
VENV_DIR = ./.venv
PYTHON_BIN = $(VENV_DIR)/bin/python3

LEVEL ?= dev
POETRY ?= poetry
PRE_COMMIT ?= pre-commit

build-python: install-python build-python-only
build-python-only:
	$(POETRY) build -vv -f wheel

clean-egg-info:
	find . \( -name *.egg-info -a -type d -not -path '$(VENV_DIR)/*' \) -exec rm -rf {} + 2> /dev/null

clean-python:
	find . \( -name __pycache__ -o -type d -empty \) -exec rm -rf {} + 2> /dev/null

distclean-python: clean-egg-info
	-rm -rf ./.coverage ./.install-python $(VENV_DIR)/ $(PYTHON_DIST_DIR)/

ensure-venv: .python-version
	if [ ! -f "$(PYTHON_BIN)" ]; then $(POETRY) env use $(PYTHON_VERSION); fi
	if [ -f "$(PYTHON_BIN)" ]; then if [ "$$("$(PYTHON_BIN)" -V)" != "Python $(PYTHON_VERSION)" ]; then $(POETRY) env use $(PYTHON_VERSION); fi; fi

install-python: .install-python
.install-python: poetry.toml $(PYTHON_BIN) poetry.lock
	touch $@

install-python-only:
	if [ "$(LEVEL)" = "prod" ]; then $(POETRY) install --no-dev; else $(POETRY) install; fi

lint-python: install-python lint-python-only
lint-python-only:
	SKIP=$(SKIP) $(PRE_COMMIT) run --all $(HOOK)

list-outdated-python: install-python
	$(POETRY) show -o

poetry.lock: pyproject.toml
	@$(MAKE) -s clean-egg-info ensure-venv install-python-only
	touch $@

poetry.toml:
	$(POETRY) config --local virtualenvs.create true
	$(POETRY) config --local virtualenvs.in-project true

python-version:
	@echo "Expected: Python $(PYTHON_VERSION)"
	@if [ -f "$(PYTHON_BIN)" ]; then echo "Virtual env: $$("$(PYTHON_BIN)" -V)"; else echo "Virtual env: -"; fi

test-python: install-python lint-python clean-python test-python-only

test-python-only: test-python-setup
	$(PYTHON_BIN) -m pytest
	@$(MAKE) -s test-python-teardown

test-python-setup:
test-python-teardown:

$(PYTHON_BIN): .python-version poetry.lock
	@$(MAKE) -s clean-egg-info ensure-venv install-python-only
	touch $@
