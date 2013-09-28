.PHONY: bootstrap clean commentor distclean explorer pep8 star_wars test travis

PROJECT = rororo

ENV ?= env
VENV = $(shell echo $(VIRTUAL_ENV))

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

COVERAGE_DIR ?= /tmp/$(PROJECT)-coverage
TEST_ARGS ?= -xv

bootstrap:
	[ ! -d "$(ENV)/" ] && python -m virtualenv --distribute "$(ENV)" || :
	$(ENV)/bin/pip install -U -e .
	$(ENV)/bin/pip install "WebTest>=1.4.3" coverage==3.6 flake8==2.0 \
	nose==1.3.0 pep8==1.4.6 pyflakes==0.7.3 redis==2.8.0

clean:
	find . -name "*.pyc" -delete

commentor:
	$(PYTHON) examples/commentor/app.py $(COMMAND)

distclean: clean
	-find . -name "*.egg*" -depth 1 -exec rm -rf {} \;
	-rm -rf build/ dist/ $(ENV)*/

explorer:
	$(PYTHON) examples/explorer/app.py $(COMMAND)

pep8:
	$(PEP8) --statistics $(PROJECT)/

star_wars:
	$(PYTHON) examples/star_wars/manage.py $(COMMAND)

test: bootstrap pep8 clean
	$(COVERAGE) run --branch $(NOSETESTS) $(TEST_ARGS) -w $(PROJECT)/
	$(COVERAGE) run -a --branch $(NOSETESTS) $(TEST_ARGS) -w examples/explorer/
	$(COVERAGE) run -a --branch $(NOSETESTS) $(TEST_ARGS) -w examples/star_wars/
	$(COVERAGE) report -m --include=$(PROJECT)/*.py --omit=$(PROJECT)/tests.py
	$(COVERAGE) html -d $(COVERAGE_DIR) --include=$(PROJECT)/*.py --omit=$(PROJECT)/tests.py
