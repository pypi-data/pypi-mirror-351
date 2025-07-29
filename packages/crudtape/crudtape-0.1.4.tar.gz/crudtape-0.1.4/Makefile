.PHONY: help
help:
	@echo "Commands:"
	@echo "  make install  - install dependencies"
	@echo "  make lint     - run linting and type checking"
	@echo "  make test     - run tests (with coverage)"
	@echo "  make build    - build distribution packages"
	@echo "  make clean    - clean up build artifacts"

.PHONY: install
install:
	@pip install -e ".[dev]"

.PHONY: lint
lint:
	@ruff check src tests
	@mypy src

.PHONY: test
test:
	@pytest -vv --cov=src --cov-report=term-missing

.PHONY: build
build:
	@pip install build
	@python -m build

.PHONY: clean
clean:
	@rm -rf build dist
	@rm -rf .coverage
	@rm -rf .coverage.*
	@rm -rf .pytest_cache .mypy_cache .ruff_cache
	@find . -type d -name "*.egg-info" -exec rm -rf {} +
	@find . -type d -name __pycache__ -exec rm -rf {} +
	@find . -type f -name "*.pyc" -delete
