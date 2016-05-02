.PHONY: clean distclean install setup-pyenv test

# Project settings
PROJECT = rororo

# Virtual environment settings
ENV ?= env
VENV = $(shell python -c "import sys; print(int(hasattr(sys, 'real_prefix')));")

# Python commands
ifeq ($(VENV),1)
	TOX = tox
else
	TOX = $(ENV)/bin/tox
endif

# Bootstrapper args
ifneq ($(CIRCLECI),)
	bootstrapper_args = --ignore-activated
endif

# Tox args
ifneq ($(TOXENV),)
	tox_args = -e $(TOXENV)
endif

all: install

clean:
	find . \( -name __pycache__ -o -type d -empty \) -exec rm -rf {} + 2> /dev/null

distclean: clean
	rm -rf build/ dist/ *.egg*/ $(ENV)/

install: .install

.install: setup.py requirements-dev.txt
	bootstrapper -d -e $(ENV)/ $(bootstrapper_args)
	touch $@

pep8:
	TOXENV=flake8 $(MAKE) test

setup-pyenv:
	pyenv local 3.4.3 3.5.1

test: .install clean
	$(TOX) $(tox_args) $(TOX_ARGS) -- $(TEST_ARGS)
