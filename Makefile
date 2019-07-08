.PHONY: clean clean-test clean-pyc clean-build docs help current-version next-version tag-version
.DEFAULT_GOAL := help

define BROWSER_PYSCRIPT
import os, webbrowser, sys

try:
	from urllib import pathname2url
except:
	from urllib.request import pathname2url

webbrowser.open("file://" + pathname2url(os.path.abspath(sys.argv[1])))
endef
export BROWSER_PYSCRIPT

define PRINT_HELP_PYSCRIPT
import re, sys

for line in sys.stdin:
	match = re.match(r'^([a-zA-Z_-]+):.*?## (.*)$$', line)
	if match:
		target, help = match.groups()
		print("%-20s %s" % (target, help))
endef
export PRINT_HELP_PYSCRIPT

BROWSER := python -c "$$BROWSER_PYSCRIPT"

help:
	@python -c "$$PRINT_HELP_PYSCRIPT" < $(MAKEFILE_LIST)

clean: clean-build clean-pyc clean-test ## remove all build, test, coverage and Python artifacts

clean-build: ## remove build artifacts
    rm -rf docs_src/rse_api*.rst
	rm -fr build/
	rm -fr dist/
	rm -fr .eggs/
	find . -name '*.egg-info' -exec rm -fr {} +
	find . -name '*.egg' -exec rm -f {} +

clean-pyc: ## remove Python file artifacts
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

clean-test: ## remove test and coverage artifacts
	rm -fr .tox/
	rm -f .coverage
	rm -fr htmlcov/
	rm -fr .pytest_cache

lint: ## check style with flake8
	flake8 --ignore=E501 rse_api tests

test: ## run tests quickly with the default Python
	PYTHONPATH=${PWD}:${PYTHONPATH} \
	py.test

test-all: ## run tests on every Python version with tox
	tox

coverage: ## check code coverage quickly with the default Python
	PYTHONPATH=${PWD}:${PYTHONPATH} \
	coverage run --source rse_api -m pytest
	coverage report -m
	coverage html
	$(BROWSER) htmlcov/index.html

docs: ## generate Sphinx HTML documentation, including API docs
	rm -f docs_src/rse_api.rst
	rm -f docs_src/modules.rst
	sphinx-apidoc -o docs_src/ rse_api
	$(MAKE) -C docs_src clean
	$(MAKE) -C docs_src html
	cp -r docs_src/_build/html/* docs
	touch docs/.nojekyll
	$(BROWSER) docs_src/_build/html/index.html

servedocs: docs ## compile the docs watching for changes
	watchmedo shell-command -p '*.rst' -c '$(MAKE) -C docs html' -R -D .

release-staging: dist ## package and upload a release
	twine upload -r staging dist/*

do-production-upload:
	twine upload -r production dist/*

prepare-version:
	#TODO check for version info in HISTORY.rst and exit if not found
	echo Version: $(VERSION)
	sed -i -e 's|$(shell git describe --tags --abbrev=0)|$(VERSION)|g' setup.py
	sed -i -e 's|$(shell git describe --tags --abbrev=0)|$(VERSION)|g' rse_api/__init__.py
	git add setup.py
	git commit -m "Increment Version from $(shell git describe --tags --abbrev=0) to $(VERSION)"

release-production: docs next-version prepare-version dist do-production-upload tag-next## package and upload a release

dist: clean ## builds source and wheel package
	python setup.py sdist

install: clean ## install the package to the active Python's site-packages
	python setup.py install

current-version:
	@echo Current version is $(shell git describe --tags --abbrev=0)

next-version:
	$(eval VERSION=$(shell git describe --tags --abbrev=0 | awk -F. -v OFS=. 'NF==1{print ++$$NF}; NF>1{if(length($$NF+1)>length($$NF))$$(NF-1)++; $$NF=sprintf("%0*d", length($$NF), ($$NF+1)%(10^length($$NF))); print}'))

tag-next: next-version
	git tag -a $(VERSION) -m "New Version $(VERSION)"
	git push
	git push --tags