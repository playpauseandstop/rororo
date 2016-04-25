.PHONY: clean distclean install test

# Project settings
PROJECT = rororo

# Virtual environment settings
ENV ?= env
VENV = $(shell python -c "import sys; print(int(hasattr(sys, 'real_prefix')));")

# Python commands
ifeq ($(VENV),1)
	PIP = pip
	TOX = tox
else
ifeq ($(CIRCLECI),true)
	PIP = pip
	TOX = tox
else
	PIP = $(ENV)/bin/pip
	TOX = $(ENV)/bin/tox
endif
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
	bootstrapper -d -e $(ENV)/
	touch $@

test: .install clean
	$(TOX) $(tox_args) $(TOX_ARGS) -- $(TEST_ARGS)
