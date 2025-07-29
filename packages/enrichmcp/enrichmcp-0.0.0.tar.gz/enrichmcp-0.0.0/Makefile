.PHONY: setup format format-docs lint test build clean docs install dev venv

# Check for command existence
UV_EXISTS := $(shell command -v uv 2> /dev/null)
VENV_EXISTS := $(shell test -d .venv && echo 1 || echo 0)

# Get OS info for venv activation
ifeq ($(OS),Windows_NT)
    VENV_ACTIVATE = .venv\Scripts\activate
    PYTHON = .venv\Scripts\python
else
    VENV_ACTIVATE = source .venv/bin/activate
    PYTHON = .venv/bin/python
endif

setup: ensure-venv
	@echo "Setting up development environment..."
ifndef UV_EXISTS
	@echo "Installing UV package installer..."
	curl -LsSf https://astral.sh/uv/install.sh | sh
else
	@echo "UV is already installed."
endif
	@echo "Installing Python dependencies..."
	uv pip install -r requirements-dev.txt
	uv pip install -e .
	@echo "Setting up pre-commit hooks..."
	$(PYTHON) -m pre_commit install
	@echo "Setup complete!"
	@echo "Your virtual environment is ready at .venv/"
	@echo "You can activate it with: $(VENV_ACTIVATE)"

ensure-venv:
ifeq ($(VENV_EXISTS),0)
	@echo "Creating virtual environment..."
	uv venv
else
	@echo "Virtual environment already exists."
endif

venv: ensure-venv
	@echo "Virtual environment is ready at .venv/"
	@echo "Activate with: $(VENV_ACTIVATE)"

format:
	$(PYTHON) -m ruff format .

format-docs:
	@echo "Formatting Python code blocks in documentation..."
	$(PYTHON) scripts/format_docs.py

lint:
	@echo "Running ruff linter with auto-fix..."
	$(PYTHON) -m ruff check --fix .
	@echo "Running pyright type checker..."
	$(PYTHON) -m pyright

lint-check:
	@echo "Running ruff linter (check only, no fixes)..."
	$(PYTHON) -m ruff check .
	@echo "Running pyright type checker..."
	$(PYTHON) -m pyright

test:
	$(PYTHON) -m pytest --cov-branch --cov-report=term --cov-report=html --cov=src/enrichmcp

build:
	$(PYTHON) -m build

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf site/
	rm -rf htmlcov/
	rm -rf *.egg-info
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type d -name .pytest_cache -exec rm -rf {} +
	find . -type f -name .coverage -delete
	rm -rf .ruff_cache/

docs:
	$(PYTHON) -m mkdocs serve

docs-build:
	$(PYTHON) -m mkdocs build

install:
	uv pip install .

dev:
	uv pip install -e .

.DEFAULT_GOAL := help
help:
	@echo "Available commands:"
	@echo "setup       - Create venv and install dependencies and pre-commit hooks"
	@echo "venv        - Create a project-specific virtual environment"
	@echo "format      - Format code with ruff"
	@echo "format-docs - Format Python code blocks in markdown documentation"
	@echo "lint        - Run linters (ruff, pyright) with auto-fixing"
	@echo "lint-check  - Run linters in check-only mode (no fixes)"
	@echo "test        - Run tests with pytest"
	@echo "build       - Build the package"
	@echo "clean       - Remove build artifacts"
	@echo "docs        - Serve documentation locally"
	@echo "docs-build  - Build documentation for production"
	@echo "install     - Install the package"
	@echo "dev         - Install the package in development mode"
