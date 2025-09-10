# Makefile for assistedinstaller Ansible collection
# assisted-by: Claude 3.5 Sonnet (Cursor)

.PHONY: help install test test-unit test-coverage lint clean setup-dev docs

# Default target
help: ## Show this help message
	@echo "Available targets:"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-20s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

# Setup development environment
setup-dev: ## Set up development environment
	@echo "Setting up development environment..."
	pip install -r tests/unit/requirements.txt
	@echo "Development environment ready!"

# Install dependencies
install: ## Install required dependencies
	pip install -r tests/unit/requirements.txt

# Run all tests
test: test-unit ## Run all tests

# Run unit tests
test-unit: ## Run unit tests
	@echo "Running unit tests..."
	python -m pytest tests/unit/ -v

# Run tests with coverage
test-coverage: ## Run tests with coverage report
	@echo "Running tests with coverage..."
	python -m pytest tests/unit/ -v --cov=plugins/modules --cov-report=term-missing --cov-report=html

# Run specific test file
test-file: ## Run specific test file (usage: make test-file FILE=test_clusters.py)
	@echo "Running test file: $(FILE)"
	python -m pytest tests/unit/$(FILE) -v

# Run tests for specific module
test-module: ## Run tests for specific module (usage: make test-module MODULE=clusters)
	@echo "Running tests for module: $(MODULE)"
	python -m pytest tests/unit/test_$(MODULE).py -v

# Lint code
lint: ## Run linting checks
	@echo "Running linting checks..."
	python -m flake8 plugins/ tests/ --max-line-length=120 --ignore=E501,W503
	python -m pylint plugins/modules/*.py --disable=C0111,C0103,R0903

# Clean up generated files
clean: ## Clean up generated files
	@echo "Cleaning up..."
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf coverage.xml
	rm -rf .pytest_cache/
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete

# Generate documentation
docs: ## Generate documentation
	@echo "Generating documentation..."
	@echo "Documentation generation not implemented yet"

# Run ansible-test sanity
ansible-test-sanity: ## Run ansible-test sanity checks
	@echo "Running ansible-test sanity checks..."
	ansible-test sanity --docker

# Run integration tests (placeholder)
test-integration: ## Run integration tests (requires cluster setup)
	@echo "Integration tests require a configured cluster environment"
	@echo "Please ensure AI_API_TOKEN or AI_OFFLINE_TOKEN is set"
	@echo "Integration tests not implemented yet"

# Check test coverage and generate report
coverage-report: test-coverage ## Generate detailed coverage report
	@echo "Coverage report generated in htmlcov/index.html"

# Run tests in watch mode (requires pytest-watch)
test-watch: ## Run tests in watch mode
	@echo "Running tests in watch mode..."
	python -m pytest tests/unit/ -v --tb=short -f

# Validate all modules can be imported
validate-imports: ## Validate all modules can be imported
	@echo "Validating module imports..."
	@for module in plugins/modules/*.py; do \
		echo "Checking $$module..."; \
		python -c "import sys; sys.path.insert(0, 'plugins/modules'); sys.path.insert(0, 'plugins/module_utils'); import $$(basename $$module .py)" || exit 1; \
	done
	@echo "All modules can be imported successfully!"

# Run quick smoke test
smoke-test: ## Run quick smoke test
	@echo "Running smoke tests..."
	python -m pytest tests/unit/ -v -k "test_missing_requests_library or test_api_authentication_headers" --tb=short
