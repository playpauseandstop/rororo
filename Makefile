.PHONY: bootstrap clean distclean pep8

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
	PIP = $(ENV)/bin/pip
	TOX = $(ENV)/bin/tox
endif

# Tox args
ifneq ($(TOXENV),)
	tox_args = -e $(TOXENV)
endif

bootstrap:
	bootstrapper -e $(ENV)/
	$(PIP) install tox==1.9.2

clean:
	find . -name "*.pyc" -delete
	-find . -name "__pycache__" -type d -exec rm -rf {} 2> /dev/null +
	find . -type d -empty -delete

distclean: clean
	rm -rf build/ dist/ *.egg*/ $(ENV)/

test: bootstrap clean
	$(TOX) $(tox_args) $(TOX_ARGS) -- $(TEST_ARGS)
