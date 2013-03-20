.PHONY: clean test

PROJECT = rororo

ENV ?= env
VENV = $(shell echo $(VIRTUAL_ENV))

ifneq ($(VENV),)
	COVERAGE = coverage
	PEP8 = pep8
	PYTHON = python -W ignore::UserWarning
else
	COVERAGE = $(ENV)/bin/coverage
	PEP8 = $(ENV)/bin/pep8
	PYTHON = $(ENV)/bin/python -W ignore::UserWarning
endif

COVERAGE_DIR ?= /tmp/$(PROJECT)-coverage
TEST_ARGS ?=

bootstrap:
	[ ! -d "$(ENV)/" ] && virtualenv --distribute $(ENV) || :
	$(ENV)/bin/pip install --download-cache=$(ENV)/src/ --use-mirrors .
	$(ENV)/bin/pip install --download-cache=$(ENV)/src/ --use-mirrors WebTest==1.4.3 coverage==3.6 pep8==1.4.5 wdb==0.9.3

clean:
	find . -name "*.pyc" -delete
	-find . -name "*.egg*" -depth 1 -exec rm -rf {} \;

distclean: clean
	-rm -rf build/ dist/ $(ENV)/

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
