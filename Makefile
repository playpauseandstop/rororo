.PHONY: clean coveralls deploy distclean docs install lint setup-pyenv test

# Project settings
PROJECT = rororo

# Python commands
POETRY ?= poetry
PYTHON ?= $(POETRY) run python
SPHINXBUILD ?= $(POETRY) run sphinx-build

# Tox args
ifneq ($(TOXENV),)
	tox_args = -e $(TOXENV)
endif

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
	rm -rf build/ dist/
	$(POETRY) build
	$(PYTHON) -m twine upload dist/*

distclean: clean
	rm -rf build/ dist/ *.egg*/ .venv/

docs: .install
	$(MAKE) -C docs/ SPHINXBUILD="$(SPHINXBUILD)" html

install: .install
.install: pyproject.toml poetry.lock
	$(POETRY) install
	touch $@

lint:
	TOXENV=lint $(MAKE) test

poetry.lock:
	$(POETRY) install

test: .install clean
	$(PYTHON) -m tox $(tox_args) $(TOX_ARGS) -- $(TEST_ARGS)
