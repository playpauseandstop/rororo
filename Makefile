.PHONY: bootstrap clean distclean pep8 star_wars test travis

PROJECT = rororo

ENV ?= env
VENV = $(shell echo $(VIRTUAL_ENV))
VERSION ?= 2.7

ifneq ($(VENV),)
	COVERAGE = coverage
	NOSETESTS = nosetests
	PEP8 = pep8
	PYTHON = python -W ignore::UserWarning
else
	COVERAGE = $(ENV)/bin/coverage
	NOSETESTS = $(ENV)/bin/nosetests
	PEP8 = $(ENV)/bin/pep8
	PYTHON = $(ENV)/bin/python -W ignore::UserWarning
endif

ifeq ($(VERSION),3.3)
	TEST_REQUIREMENTS = "WebTest>=1.4.3" coverage==3.6 nose==1.3.0 pep8==1.4.5
else
	TEST_REQUIREMENTS = "WebTest>=1.4.3" coverage==3.6 nose==1.3.0 pep8==1.4.5 wdb==0.9.3
endif

COVERAGE_DIR ?= /tmp/$(PROJECT)-coverage
TEST_ARGS ?= -cb

bootstrap:
	[ ! -d "$(ENV)/" ] && virtualenv-$(VERSION) --distribute "$(ENV)" || :
	$(ENV)/bin/pip install -U -e .
	$(ENV)/bin/pip install $(TEST_REQUIREMENTS)

clean:
	find . -name "*.pyc" -delete

distclean: clean
	-find . -name "*.egg*" -depth 1 -exec rm -rf {} \;
	-rm -rf build/ dist/ $(ENV)*/

explorer:
	$(PYTHON) examples/explorer/app.py $(COMMAND)

pep8:
	$(PEP8) --statistics $(PROJECT)/

star_wars:
	$(PYTHON) examples/star_wars/manage.py $(COMMAND)

test: bootstrap clean pep8
	$(COVERAGE) run --branch -m unittest discover $(TEST_ARGS) -s $(PROJECT)/
	$(COVERAGE) run -a --branch -m unittest discover $(TEST_ARGS) -s examples/explorer/
	$(COVERAGE) run -a --branch -m unittest discover $(TEST_ARGS) -s examples/star_wars/
	$(COVERAGE) report -m --include=$(PROJECT)/*.py --omit=$(PROJECT)/tests.py
	$(COVERAGE) html -d $(COVERAGE_DIR) --include=$(PROJECT)/*.py --omit=$(PROJECT)/tests.py

travis: bootstrap clean pep8
	$(NOSETESTS) $(TEST_ARGS) -w $(PROJECT)/
	$(NOSETESTS) $(TEST_ARGS) -w examples/explorer/
	$(NOSETESTS) $(TEST_ARGS) -w examples/star_wars/
