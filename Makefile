.PHONY: clean deploy distclean install lint setup-pyenv test

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

deploy:
ifeq ($(PYPI_USERNAME),)
	# PYPI_USERNAME env var should be supplied
	exit 1
endif
ifeq ($(PYPI_PASSWORD),)
	# PYPI_PASSWORD env var should be supplied
	exit 1
endif
ifeq ($(CIRCLECI),)
	$(MAKE) test
endif
	rm -rf build/ dist/
	python setup.py sdist bdist_wheel
	twine upload -u $(PYPI_USERNAME) -p $(PYPI_PASSWORD) dist/*

distclean: clean
	rm -rf build/ dist/ *.egg*/ $(ENV)/

install: .install

.install: setup.py requirements-dev.txt
	bootstrapper -d -e $(ENV)/ $(bootstrapper_args)
	touch $@

lint:
	TOXENV=flake8 $(MAKE) test

setup-pyenv:
	pyenv local 3.4.4 3.5.1

test: .install clean
	$(TOX) $(tox_args) $(TOX_ARGS) -- $(TEST_ARGS)
