# Makefile for PyLLM

.PHONY: all setup clean test lint format run help venv docker-test docker-build docker-clean build publish test-package update-version publish-test

# Default values
PORT ?= 8001
HOST ?= 0.0.0.0

# Default target
all: help

# Create virtual environment if it doesn't exist
venv:
	@test -d venv || python3 -m venv venv

# Setup project
setup: venv
	@echo "Setting up PyLLM..."
	@. venv/bin/activate && pip install -e .
	@. venv/bin/activate && pip install setuptools wheel twine build

# Clean project
clean:
	@echo "Cleaning PyLLM..."
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type d -name *.egg-info -exec rm -rf {} +
	find . -type d -name .pytest_cache -exec rm -rf {} +

# Run tests
test: setup
	@echo "Testing PyLLM..."
	@. venv/bin/activate && python -m unittest discover

# Lint code
lint: setup
	@echo "Linting PyLLM..."
	@. venv/bin/activate && flake8 getllm

# Format code
format: setup
	@echo "Formatting PyLLM..."
	@. venv/bin/activate && black getllm

# Run the API server
run: setup
	@echo "Running PyLLM API server on port $(PORT)..."
	@. venv/bin/activate && uvicorn getllm.api:app --host $(HOST) --port $(PORT)

# Run with custom port (for backward compatibility)
run-port: setup
	@echo "Running PyLLM API server on port $(PORT)..."
	@. venv/bin/activate && uvicorn getllm.api:app --host $(HOST) --port $(PORT)

# Docker testing targets
docker-build:
	@echo "Building Docker test images..."
	@./run_docker_tests.sh --build

docker-test: docker-build
	@echo "Running tests in Docker..."
	@./run_docker_tests.sh --run-tests

docker-interactive: docker-build
	@echo "Starting interactive Docker test environment..."
	@./run_docker_tests.sh --interactive

docker-mock: docker-build
	@echo "Starting PyLLM mock service in Docker..."
	@./run_docker_tests.sh --mock-service

docker-clean:
	@echo "Cleaning Docker test environment..."
	@./run_docker_tests.sh --clean


# Build package
build: setup
	@echo "Building package..."
	@. venv/bin/activate && pip install -e . && pip install wheel twine build
	@. venv/bin/activate && rm -rf dist/* && python setup.py sdist bdist_wheel

# Update version
update-version:
	@echo "Updating package version..."
	@python ../scripts/update_version.py

# Publish package to PyPI
publish: build update-version
	@echo "Publishing package to PyPI..."
	@. venv/bin/activate && twine check dist/* && twine upload dist/*

# Publish package to TestPyPI
publish-test: build update-version
	@echo "Publishing package to TestPyPI..."
	@. venv/bin/activate && twine check dist/* && twine upload --repository testpypi dist/*

# Publish package to TestPyPI with token
publish-test-token: build
	@echo "Publishing PyLLM package to TestPyPI using token..."
	@echo "Enter your TestPyPI token when prompted"
	@. venv/bin/activate && twine check dist/* && twine upload --non-interactive --repository testpypi dist/*

# Publish using the publish script
publish-script: build
	@echo "Publishing PyLLM package using the publish script..."
	@. venv/bin/activate && python scripts/publish.py

# Publish to TestPyPI using the publish script
publish-script-test: build
	@echo "Publishing PyLLM package to TestPyPI using the publish script..."
	@. venv/bin/activate && python scripts/publish.py --test

# Help
help:
	@echo "PyLLM Makefile"
	@echo ""
	@echo "Available targets:"
	@echo "  setup     - Set up the project"
	@echo "  clean     - Clean the project"
	@echo "  test      - Run tests"
	@echo "  lint      - Lint the code"
	@echo "  format    - Format the code with black"
	@echo "  run       - Run the API server"
	@echo "  run-port PORT=8001 - Run the API server on a custom port"
	@echo "  build     - Build the package"
	@echo "  publish   - Publish the package to PyPI (requires .pypirc)"
	@echo "  publish-token - Publish the package to PyPI using a token"
	@echo "  publish-test - Publish the package to TestPyPI (requires .pypirc)"
	@echo "  publish-test-token - Publish the package to TestPyPI using a token"
	@echo "  publish-script - Publish using the publish script"
	@echo "  publish-script-test - Publish to TestPyPI using the publish script"
	@echo "  docker-build      - Build Docker test images"
	@echo "  docker-test       - Run tests in Docker"
	@echo "  docker-interactive - Start interactive Docker test environment"
	@echo "  docker-mock       - Start PyLLM mock service in Docker"
	@echo "  docker-clean      - Clean Docker test environment"
	@echo "  help      - Show this help message"
