GIT_DIR = .git

PYTHON_VERISON = $(shell cat .python-version)
VENV_DIR = .venv
PYTHON_BIN = $(VENV_DIR)/bin/python3

STAGE ?= dev
DOTENV ?= $(shell if [ -f dotenv.sh ]; then echo "./dotenv.sh"; fi)
POETRY ?= $(DOTENV) poetry
POETRY_INSTALL_ARGS ?=
PRE_COMMIT ?= pre-commit
PYENV ?= $(shell if [ -z "${CI}" ]; then echo "pyenv"; fi)
PYTHON ?= $(DOTENV) $(PYTHON_BIN)
PYTHON_DIST_DIR ?= dist

.PHONY: build-python
build-python: install-python build-python-only

.PHONY: build-python-only
build-python-only:
	$(POETRY) build -vv -f wheel

.PHONY: clean-egg-info
clean-egg-info:
	find . \( -name *.egg-info -a -type d -not -path '$(VENV_DIR)/*' \) -exec rm -rf {} + 2> /dev/null

.PHONY: clean-python
clean-python:
	find . \( -name __pycache__ -o -type d -empty -not -path '$(GIT_DIR)/*' \) -exec rm -rf {} + 2> /dev/null

.PHONY: distclean-python
distclean-python: clean-egg-info
	-rm -rf .coverage .install-python $(VENV_DIR)/ $(PYTHON_DIST_DIR)/

.PHONY: ensure-venv
ensure-venv: .python-version
	if [ -f "$(PYTHON_BIN)" ]; then \
		if [ "$$("$(PYTHON_BIN)" -V)" != "Python $(PYTHON_VERISON)" ]; then \
			echo "[python.mk] Updating virtualenv as venv version of $$("$(PYTHON_BIN)" -V) != $(PYTHON_VERISON)"; \
			$(POETRY) env use $$($(PYENV) which python3); \
		fi; \
	else \
		echo "[python.mk] Tell poetry to use Python $(PYTHON_VERISON) for creating virtual env"; \
		$(POETRY) env use $$($(PYENV) which python3); \
	fi

.PHONY: install-python
install-python: .install-python
.install-python: poetry.toml $(PYTHON_BIN) poetry.lock
	touch $@

.PHONY: install-python-only
install-python-only:
	if [ "$(STAGE)" = "prod" ]; then $(POETRY) install $(POETRY_INSTALL_ARGS) --no-dev; else $(POETRY) install $(POETRY_INSTALL_ARGS); fi

.PHONY: lint-and-test-python
lint-and-test-python: lint-python test-python

.PHONY: lint-python
lint-python: install-python lint-python-only

.PHONY: lint-python-only
lint-python-only:
	SKIP=$(SKIP) $(PRE_COMMIT) run --all $(HOOK)

.PHONY: list-outdated-python
list-outdated-python: install-python
	$(POETRY) show -o

.PHONY: poetry
poetry:
	$(POETRY) $(ARGS)

poetry.lock: pyproject.toml
	@$(MAKE) -s clean-egg-info ensure-venv install-python-only
	touch $@

poetry.toml:
	$(POETRY) config --local virtualenvs.create true
	$(POETRY) config --local virtualenvs.in-project true
	$(POETRY) config --local virtualenvs.prefer-active-python true

.PHONY: python-version
python-version:
	@echo "Expected: Python $(PYTHON_VERISON)"
	@if [ -f "$(PYTHON_BIN)" ]; then echo "Virtual env: $$("$(PYTHON_BIN)" -V)"; else echo "Virtual env: -"; fi

.PHONY: test-python
test-python: install-python clean-python test-python-only

.PHONY: test-python-only
test-python-only: STAGE = test
test-python-only: test-python-setup
	STAGE=$(STAGE) $(PYTHON) -m pytest $(TEST_ARGS)
	@$(MAKE) -s test-python-teardown

.PHONY: test-python-setup
test-python-setup: STAGE = test
test-python-setup:

.PHONY: test-python-teardown
test-python-teardown: STAGE = test
test-python-teardown:

$(PYTHON_BIN): .python-version poetry.lock
	@$(MAKE) -s clean-egg-info ensure-venv install-python-only
	touch $@
