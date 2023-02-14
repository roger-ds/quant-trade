.PHONY: install virtualenv ipython clean lint fmt pflake8

install:
	echo "Installing for dev envitronment"
	@.venv/Scripts/python -m pip install -e '.[dev]'

virtualenv:
	@.venv/Scripts/python -m venv .venv

ipython:
	@.venv/Scripts/ipython

lint: 
	@.venv/Scripts/pflake8 --exclude=.venv,build

fmt:
	@.venv/Scripts/isort trade
	@.venv/Scripts/black trade


clean:            ## Clean unused files.
	@find ./ -name '*.pyc' -exec rm -f {} \;
	@find ./ -name '__pycache__' -exec rm -rf {} \;
	@find ./ -name 'Thumbs.db' -exec rm -f {} \;
	@find ./ -name '*~' -exec rm -f {} \;
	@rm -rf .cache
	@rm -rf .pytest_cache
	@rm -rf .mypy_cache
	@rm -rf build
	@rm -rf dist
	@rm -rf *.egg-info
	@rm -rf htmlcov
	@rm -rf .tox/
	@rm -rf docs/_build
