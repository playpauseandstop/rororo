.PHONY: clean test

PROJECT = rororo

ENV ?= env
VENV = $(shell echo $(VIRTUAL_ENV))

ifneq ($(VENV),)
	COVERAGE = coverage
	PYTHON = python
else
	COVERAGE = $(ENV)/bin/coverage
	PYTHON = $(ENV)/bin/python
endif

COVERAGE_DIR ?= /tmp/$(PROJECT)-coverage
TEST_ARGS ?=

bootstrap:
	[ ! -d "$(ENV)/" ] && virtualenv --use-distribute $(ENV) || :
	$(ENV)/bin/pip install --download-cache=$(ENV)/src/ --use-mirrors .
	$(ENV)/bin/pip install --download-cache=$(ENV)/src/ --use-mirrors WebTest==1.4.3 coverage==3.6 wdb==0.9.3

clean:
	find . -name "*.pyc" -delete
	-find . -name "*.egg*" -depth 1 -exec rm -rf {} \;

distclean: clean
	-rm -rf build/ dist/ $(ENV)/

test: clean
	$(COVERAGE) run --branch -m unittest discover $(TEST_ARGS) -s $(PROJECT)/
	$(COVERAGE) run -a --branch -m unittest discover $(TEST_ARGS) -s examples/explorer/
	$(COVERAGE) report -m --include=$(PROJECT)/*.py --omit=$(PROJECT)/tests.py
	$(COVERAGE) html -d $(COVERAGE_DIR) --include=$(PROJECT)/*.py --omit=$(PROJECT)/tests.py
