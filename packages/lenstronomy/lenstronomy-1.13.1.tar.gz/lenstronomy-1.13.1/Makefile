.PHONY: help clean clean-pyc clean-build list test test-all coverage docs release sdist

help:
	@echo "clean-build - remove build artifacts"
	@echo "clean-pyc - remove Python file artifacts"
	@echo "lint - check style with flake8"
	@echo "test - run tests quickly with the default Python"
	@echo "test-all - run tests on every Python version with tox"
	@echo "coverage - check code coverage quickly with the default Python"
	@echo "docs - generate Sphinx HTML documentation, including API docs"
	@echo "sdist - package"
	@echo "black - autoformat code"
	@echo "docformatter - autoformat docstrings"

clean: clean-build clean-pyc

clean-build:
	rm -fr build/
	rm -fr dist/
	rm -fr *.egg-info
	rm -fr docs/_build

clean-pyc:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -rf {} +

lint:
	flake8 lenstronomy test
	black .
	docformatter -r ./* --black --in-place

test:
	py.test

test-all:
	tox

coverage:
	coverage run --source lenstronomy setup.py test
	coverage report -m
	coverage html
	open htmlcov/index.html

docs:
	rm -f docs/lenstronomy.rst
	rm -f docs/modules.rst
	sphinx-apidoc -o docs/ lenstronomy
	MAKE -C docs clean
	MAKE -C docs html
	open docs/_build/html/index.html

sdist: clean
	pip freeze > requirements.rst
	python setup.py sdist
	ls -l dist

pypi-upload:
	python setup.py sdist
	twine upload --repository-url https://test.pypi.org/legacy/ dist/*
	twine upload dist/*

conda-upload:
	grayskull pypi lenstronomy