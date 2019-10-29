.PHONY: \
	clean \
	coveralls \
	deploy-ci \
	distclean \
	docs \
	install \
	lint \
	lint-ci \
	list-outdated \
	open-docs \
	test \
	test-ci

# Project settings
PROJECT = rororo
DOCS_DIR = ./docs

# Python commands
POETRY ?= poetry
PRE_COMMIT ?= pre-commit
PYTHON ?= $(POETRY) run python
SPHINXBUILD ?= $(POETRY) run sphinx-build
TOX ?= tox

all: install

clean:
	find . \( -name __pycache__ -o -type d -empty \) -exec rm -rf {} + 2> /dev/null

coveralls:
	-$(PYTHON) -m coveralls

deploy-ci:
ifeq ($(TWINE_USERNAME),)
	# TWINE_USERNAME env var should be supplied
	exit 1
endif
ifeq ($(TWINE_PASSWORD),)
	# TWINE_PASSWORD env var should be supplied
	exit 1
endif
ifeq ($(CIRCLECI),)
	$(MAKE) test
endif
	-rm -rf build/ dist/
	$(POETRY) build
	$(POETRY) publish -u $(TWINE_USERNAME) -p $(TWINE_PASSWORD)

distclean: clean
	rm -rf build/ dist/ *.egg*/ .venv/

docs: install
	$(PYTHON) -m pip install -r docs/requirements.txt
	$(MAKE) -C $(DOCS_DIR)/ SPHINXBUILD="$(SPHINXBUILD)" html

install: .install
.install: pyproject.toml poetry.lock
	$(POETRY) config settings.virtualenvs.in-project true
	$(POETRY) install
	touch $@

lint: install lint-ci

lint-ci:
	SKIP=$(SKIP) $(PRE_COMMIT) run --all $(HOOK)

list-outdated: install
	$(POETRY) show -o

open-docs: docs
	open $(DOCS_DIR)/_build/html/index.html

test: install clean lint test-ci

test-ci:
	TOXENV=$(TOXENV) $(TOX) $(TOX_ARGS) -- $(TEST_ARGS)
