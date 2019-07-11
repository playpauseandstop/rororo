.PHONY: ci-deploy \
	ci-lint \
	ci-test \
	clean \
	coveralls \
	distclean \
	docs \
	install \
	lint \
	list-outdated \
	test \
	update-setup-py

# Project settings
PROJECT = rororo

# Python commands
POETRY ?= poetry
PRE_COMMIT ?= pre-commit
PYTHON ?= $(POETRY) run python
SPHINXBUILD ?= $(POETRY) run sphinx-build
TOX ?= tox

all: install

ci-deploy:
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

ci-lint:
	SKIP=$(SKIP) $(PRE_COMMIT) run --all $(HOOK)

ci-test:
	TOXENV=$(TOXENV) $(TOX) $(TOX_ARGS) -- $(TEST_ARGS)

clean:
	find . \( -name __pycache__ -o -type d -empty \) -exec rm -rf {} + 2> /dev/null

coveralls:
	-$(PYTHON) -m coveralls

distclean: clean
	rm -rf build/ dist/ *.egg*/ .venv/

docs: .install
	$(PYTHON) -m pip install -r docs/requirements.txt
	$(MAKE) -C docs/ SPHINXBUILD="$(SPHINXBUILD)" html

install: .install
.install: pyproject.toml poetry.lock
ifneq ($(CIRCLECI),)
	$(POETRY) config settings.virtualenvs.create true
endif
	$(POETRY) config settings.virtualenvs.in-project true
	$(POETRY) install
	touch $@

lint: install
	SKIP=update-setup-py $(MAKE) ci-lint

list-outdated: install
	$(POETRY) show -o

test: install clean lint ci-test

update-setup-py: .install
	rm -rf dist/
	$(POETRY) build
	tar -xzf dist/$(PROJECT)-*.tar.gz --directory dist/
	cp dist/$(PROJECT)-*/setup.py .
	rm -rf dist/
	$(PYTHON) -c 'from pathlib import Path; setup_py = Path("setup.py"); setup_py.write_text(setup_py.read_text().replace("from distutils.core import setup", "from setuptools import setup"))'
