.PHONY: clean distclean server

ENV ?= env
PROJECT = .
PYTHON = $(ENV)/bin/python

TEST_ARGS ?= -fv

bootstrap:
	bootstrapper -e $(ENV)

clean:
	find . -name "*.pyc" -delete

distclean: clean
	rm -rf $(ENV)/

server:
	$(ENV)/bin/python app.py

shell:
	$(ENV)/bin/ipython --pprint

test: clean
	$(ENV)/bin/python -m unittest discover $(TEST_ARGS) -s $(PROJECT)
