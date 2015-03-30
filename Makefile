.PHONY: bootstrap clean distclean pep8

# Project settings
PROJECT = rororo

# Virtual environment settings
ENV ?= env
VENV = $(shell python -c "import sys; print(int(hasattr(sys, 'real_prefix')));")

# Python commands
ifeq ($(VENV),1)
	PEP8 = flake8
	PIP = pip
	TOX = tox
else
	PEP8 = $(ENV)/bin/flake8
	PIP = $(ENV)/bin/pip
	TOX = $(ENV)/bin/tox
endif

bootstrap:
	bootstrapper -e $(ENV)/
	$(PIP) install tox

clean:
	find . -name "*.pyc" -delete

distclean: clean
	rm -rf build/ dist/ *.egg*/ $(ENV)/

pep8:
	$(PEP8) --statistics $(PROJECT)/

test: bootstrap clean
ifneq ($(TOXENV),)
	$(TOX) -e $(TOXENV) $(TOX_ARGS) -- $(TEST_ARGS)
else
	$(TOX) $(TOX_ARGS) -- $(TEST_ARGS)
endif
