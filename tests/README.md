# Testing Framework for assistedinstaller
<!-- assisted-by: Claude 3.5 Sonnet (Cursor) -->

This directory contains the comprehensive testing framework for the assistedinstaller Ansible collection.

## Overview

The testing framework provides:
- **Unit Tests**: Comprehensive test coverage for all modules
- **Base Test Classes**: Reusable test infrastructure
- **Mocking Framework**: Consistent mocking of external dependencies
- **Coverage Reporting**: Detailed test coverage analysis
- **CI/CD Integration**: Automated testing in GitHub Actions

## Structure

```
tests/
├── __init__.py                 # Test package initialization
├── README.md                   # This file
├── unit/                       # Unit tests
│   ├── __init__.py
│   ├── conftest.py            # Pytest configuration and fixtures
│   ├── base_test.py           # Base test classes and utilities
│   ├── requirements.txt       # Test dependencies
│   └── test_clusters.py       # Example test for clusters module
└── sanity/                    # Ansible sanity test configurations
    ├── ignore-2.17.txt
    ├── ignore-2.18.txt
    └── ignore-2.19.txt
```

## Running Tests

### Prerequisites

Install test dependencies:
```bash
pip install -r tests/unit/requirements.txt
```

### Basic Test Execution

```bash
# Run all unit tests
make test-unit

# Run with coverage
make test-coverage

# Run the example test file
make test-file FILE=test_clusters.py

# Run tests for the clusters module
make test-module MODULE=clusters

# Quick smoke test
make smoke-test
```

### Using pytest directly

```bash
# Run all tests
pytest tests/unit/

# Run with coverage
pytest tests/unit/ --cov=plugins/modules --cov-report=term-missing

# Run specific test
pytest tests/unit/test_clusters.py::TestClustersModule::test_list_clusters_success

# Run tests matching pattern
pytest tests/unit/ -k "test_api_error"
```

## Test Framework Components

### Base Test Classes

#### `BaseModuleTest`
Provides common test infrastructure:
- Mock setup for API responses
- Standard header validation
- Common assertion methods
- Request/response validation utilities

#### `ModuleTestMixin`
Provides common test methods:
- `test_missing_requests_library()` - Tests handling of missing dependencies
- `test_api_authentication_headers()` - Validates authentication headers
- Extensible framework for additional common tests

### Fixtures (conftest.py)

Common fixtures available to all tests:
- `mock_ansible_module` - Mock AnsibleModule instance
- `mock_api_token` - Mock API token
- `mock_api_response` - Mock successful API response
- `mock_api_error_response` - Mock error API response
- `mock_requests_*` - Mock HTTP request methods
- Module-specific parameter fixtures

### Test Patterns

#### Standard Test Structure
```python
class TestModuleNameModule(BaseModuleTest, ModuleTestMixin):
    def setUp(self):
        super().setUp()
        self.module_class = module_name
        self.default_params = {...}

    def test_specific_functionality(self):
        # Test implementation
        pass
```

#### API Call Testing
```python
@patch('module.apitoken.GetToken')
@patch('module.requests.get')
@patch('module.AnsibleModule')
def test_api_call(self, mock_ansible_module, mock_requests_get, mock_get_token):
    # Setup mocks
    mock_get_token.return_value = self.mock_api_token
    mock_response = MagicMock()
    mock_response.ok = True
    mock_response.json.return_value = {...}
    mock_requests_get.return_value = mock_response
    
    # Create mock module instance
    mock_module_instance = self.create_mock_module(params)
    mock_ansible_module.return_value = mock_module_instance
    
    # Run module
    module.run_module()
    
    # Verify results
    self.assert_exit_json_called_with_success(mock_module_instance)
```

## Test Coverage

### Current Coverage

The test suite provides comprehensive coverage for:
- ✅ **API Authentication** - Test authentication headers
- ✅ **Error Handling** - API errors, missing dependencies, invalid responses
- ✅ **Parameter Validation** - Required parameters, parameter filtering
- ✅ **Request Construction** - URL construction, query parameters, request bodies
- ✅ **Response Processing** - Success and error response handling
- ✅ **Module-Specific Logic** - Module's unique functionality (demonstrated with clusters)

### Coverage Goals

- **Minimum Coverage**: 80% (enforced by pytest configuration)
- **Target Coverage**: 90%+ for all modules
- **Critical Paths**: 100% coverage for error handling and authentication

### Generating Coverage Reports

```bash
# Generate HTML coverage report
make test-coverage

# View coverage report
open htmlcov/index.html
```

## Adding Tests for New Modules

### 1. Create Test File
```bash
cp tests/unit/test_clusters.py tests/unit/test_new_module.py
```

### 2. Update Test Class
```python
class TestNewModuleModule(BaseModuleTest, ModuleTestMixin):
    def setUp(self):
        super().setUp()
        if new_module is None:
            self.skipTest("new_module module not available")
        
        self.module_class = new_module
        self.default_params = {
            # Module-specific parameters
        }
```

### 3. Add Module-Specific Tests
- Test successful API calls (see clusters example)
- Test error handling
- Test parameter validation
- Test any unique module functionality

### 4. Update Sanity Ignore Files
Add the new module to `tests/sanity/ignore-*.txt` files if needed.

## Continuous Integration

### GitHub Actions

The `.github/workflows/tests.yml` workflow runs:
- Unit tests across multiple Python versions (3.8-3.11)
- Ansible sanity tests
- Code linting with flake8 and pylint
- Coverage reporting to Codecov

### Local CI Simulation

```bash
# Run the same checks as CI
make test-coverage
make lint
make ansible-test-sanity  # Requires Docker
```

## Best Practices

### Test Naming
- Test files: `test_<module_name>.py`
- Test classes: `Test<ModuleName>Module`
- Test methods: `test_<functionality>_<scenario>`

### Mock Usage
- Always mock external dependencies (requests, apitoken, etc.)
- Use fixtures for common mock setups
- Verify mock calls to ensure correct API usage

### Assertions
- Use the base class assertion methods for consistency
- Test both success and failure scenarios
- Verify all important aspects (headers, parameters, responses)

### Documentation
- Document complex test scenarios
- Add comments for non-obvious test logic
- Keep test names descriptive

## Troubleshooting

### Common Issues

**ImportError: No module named 'module_name'**
- Ensure the module file exists
- Check that the plugins path is correctly added to sys.path

**Mock not being called**
- Verify the patch target matches the import in the module
- Check that the module function is actually being called

**Test failures in CI but not locally**
- Check Python version compatibility
- Ensure all dependencies are in requirements.txt
- Verify environment-specific assumptions

### Debugging Tests

```bash
# Run with verbose output
pytest tests/unit/ -v -s

# Run with pdb debugger
pytest tests/unit/ --pdb

# Show local variables on failure
pytest tests/unit/ -l --tb=long
```

## Contributing

When contributing tests:

1. **Follow the established patterns** - Use the base classes and fixtures
2. **Test both success and failure paths** - Don't just test the happy path
3. **Mock external dependencies** - Never make real API calls in unit tests
4. **Maintain coverage** - Ensure new code is well-tested
5. **Document complex scenarios** - Help future maintainers understand the tests

## Future Enhancements

Planned improvements:
- **Integration Tests** - Tests against real API (with proper credentials)
- **Performance Tests** - Measure module execution time
- **Security Tests** - Validate credential handling
- **End-to-End Tests** - Full playbook execution tests
