.PHONY: clean \
	coveralls \
	deploy \
	distclean \
	docs \
	install \
	lint \
	test \
	update-setup-py

# Project settings
PROJECT = rororo

# Python commands
POETRY ?= poetry
PRE_COMMIT ?= pre-commit
PYTHON ?= $(POETRY) run python
SPHINXBUILD ?= $(POETRY) run sphinx-build

all: install

clean:
	find . \( -name __pycache__ -o -type d -empty \) -exec rm -rf {} + 2> /dev/null

coveralls:
	-$(PYTHON) -m coveralls

deploy:
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

lint: .install
	SKIP=$(SKIP) $(PRE_COMMIT) run --all $(HOOK)

list-outdated: .install
	$(POETRY) show -o

test: .install clean lint
	TOXENV=$(TOXENV) $(PYTHON) -m tox $(TOX_ARGS) -- $(TEST_ARGS)

update-setup-py: .install
	rm -rf dist/
	$(POETRY) build
	tar -xzf dist/$(PROJECT)-*.tar.gz --directory dist/
	cp dist/$(PROJECT)-*/setup.py .
	rm -rf dist/
