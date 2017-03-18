.PHONY: clean-pyc clean-build docs clean
define BROWSER_PYSCRIPT
import os, webbrowser, sys
try:
	from urllib import pathname2url
except:
	from urllib.request import pathname2url

webbrowser.open("file://" + pathname2url(os.path.abspath(sys.argv[1])))
endef
export BROWSER_PYSCRIPT
BROWSER := python -c "$$BROWSER_PYSCRIPT"

# Docker Configurations
JUPYTER_PORT := 8888:8888
BIND_DIR := .
GIT_BRANCH := $(shell git rev-parse --abbrev-ref HEAD 2>/dev/null)
GIT_BRANCH_CLEAN := $(shell echo $(GIT_BRANCH) | sed -e "s/[^[:alnum:]]/-/g")
DOCKER_IMAGE := mpkernel$(if $(GIT_BRANCH_CLEAN),:$(GIT_BRANCH_CLEAN))
DOCKER_PORT_FORWARD := $(if $(JUPYTER_PORT),-p "$(JUPYTER_PORT)",)
DOCKER_MOUNT := $(if $(BIND_DIR),-v "$(CURDIR)/$(BIND_DIR):/work/mpkernel/$(BIND_DIR)")
DOCKER_FLAGS := docker run --rm -it $(DOCKER_MOUNT) $(DOCKER_PORT_FORWARD)
DOCKER_RUN_DOCKER := $(DOCKER_FLAGS) "$(DOCKER_IMAGE)"

help:
	@echo "clean        - remove all build, test, coverage and Python artifacts"
	@echo "clean-build  - remove build artifacts"
	@echo "clean-pyc    - remove Python file artifacts"
	@echo "clean-test   - remove test and coverage artifacts"
	@echo "lint         - check style with flake8"
	@echo "test         - run tests quickly with the default Python"
	@echo "test-all     - run tests on every Python version with tox"
	@echo "coverage     - check code coverage quickly with the default Python"
	@echo "docs         - generate Sphinx HTML documentation, including API docs"
	@echo "release      - package and upload a release"
	@echo "dist         - package"
	@echo "install      - install the package to the active Python's site-packages"
	@echo "docker-build - build the docker image"
	@echo "docker-run   - run the docker image"

clean: clean-build clean-pyc clean-test

clean-build:
	rm -fr build/
	rm -fr dist/
	rm -fr .eggs/
	find . -name '*.egg-info' -exec rm -fr {} +
	find . -name '*.egg' -exec rm -f {} +

clean-pyc:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

clean-test:
	rm -fr .tox/
	rm -f .coverage
	rm -fr htmlcov/

lint:
	flake8 stmhal tests
	flake8 unix tests

test:
	python setup.py test

test-all:
	tox

coverage:
	coverage run --source stmhal setup.py test
	coverage run --source unix setup.py test
	coverage report -m
	coverage html
	$(BROWSER) htmlcov/index.html

docs:
	rm -f docs/mpkernel.rst
	rm -f docs/modules.rst
	sphinx-apidoc -o docs/ stmhal
	sphinx-apidoc -o docs/ unix
	$(MAKE) -C docs clean
	$(MAKE) -C docs html
	$(BROWSER) docs/_build/html/index.html

release: clean
	python setup.py sdist upload
	python setup.py bdist_wheel upload

dist: clean
	python setup.py sdist
	python setup.py bdist_wheel
	ls -l dist

install: clean
	python setup.py install

docker-build:
	docker build -t "$(DOCKER_IMAGE)" .

docker-run: docker-build
	$(DOCKER_RUN_DOCKER) bash
