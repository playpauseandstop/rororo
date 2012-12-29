.PHONY: clean distclean

clean:
	find . -name "*.pyc" -delete
	-find . -name "*.egg*" -depth 1 -exec rm -rf {} \;

distclean: clean
	rm -rf $(ENV)/

test: clean
	python setup.py test
