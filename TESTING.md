# Testing Guide for assistedinstaller
<!-- assisted-by: Claude 3.5 Sonnet (Cursor) -->

This guide provides comprehensive information about testing the assistedinstaller Ansible collection.

## Quick Start

```bash
# 1. Install test dependencies
make setup-dev

# 2. Run all tests
make test

# 3. Run with coverage
make test-coverage

# 4. View coverage report
open htmlcov/index.html
```

## Test Framework Architecture

### Design Principles

1. **Comprehensive Coverage** - Every module has full test coverage
2. **Consistent Patterns** - All tests follow the same structure
3. **Mock External Dependencies** - No real API calls in unit tests
4. **Easy to Extend** - Adding tests for new modules is straightforward
5. **CI/CD Ready** - Automated testing in GitHub Actions

### Framework Components

#### Base Classes (`tests/unit/base_test.py`)

**BaseModuleTest**
- Common test infrastructure
- Mock setup utilities
- Standard assertion methods
- Request/response validation

**ModuleTestMixin**
- Common test methods for all modules
- Authentication header validation
- Missing dependency handling
- Extensible for additional common tests

#### Fixtures (`tests/unit/conftest.py`)

**Common Fixtures**
- `mock_ansible_module` - Mock AnsibleModule instance
- `mock_api_token` - Mock API authentication token
- `mock_api_response` - Mock successful API response
- `mock_api_error_response` - Mock error API response
- `mock_requests_*` - Mock HTTP request methods

**Module-Specific Fixtures**
- Parameter fixtures for each module type
- API header fixtures
- Response data fixtures

## Test Coverage by Module

### ✅ clusters
- ✅ List clusters (with/without hosts)
- ✅ Create cluster (with pull secret validation)
- ✅ Delete cluster
- ✅ API error handling
- ✅ Parameter validation
- ✅ Utility function testing (`remove_module_fields`)

### ✅ events
- ✅ List events (all parameters)
- ✅ Pagination (limit, offset, order)
- ✅ Severity filtering (single/multiple)
- ✅ Cluster ID filtering
- ✅ List parameter handling (comma-separated)
- ✅ Default parameter inclusion

### ✅ infra_envs
- ✅ Create infra-env
- ✅ Pull secret handling (no_log validation)
- ✅ Required parameter validation
- ✅ API error handling
- ✅ Utility function testing

### ✅ openshift_versions
- ✅ List all versions
- ✅ Version filtering
- ✅ Latest version filtering
- ✅ Parameter combination testing
- ✅ Empty parameter exclusion

### ✅ support_levels
- ✅ Query architectures
- ✅ Query features (all parameters)
- ✅ External platform handling
- ✅ Parameter filtering by resource type
- ✅ None value exclusion

### ✅ supported_operators
- ✅ List supported operators
- ✅ JSON/text response handling
- ✅ Empty response handling
- ✅ No parameter module testing

## Running Tests

### Make Commands

```bash
# Setup development environment
make setup-dev

# Run all tests
make test

# Run unit tests specifically
make test-unit

# Run tests with coverage
make test-coverage

# Run specific test file
make test-file FILE=test_clusters.py

# Run tests for specific module
make test-module MODULE=clusters

# Run quick smoke test
make smoke-test

# Clean up generated files
make clean

# Validate module imports
make validate-imports

# Run linting
make lint
```

### Python Test Runner

```bash
# Basic usage
./run_tests.py

# With coverage
./run_tests.py --coverage

# Specific module
./run_tests.py --module clusters

# Specific test file
./run_tests.py --file test_events.py

# Smoke test only
./run_tests.py --smoke

# Validate imports only
./run_tests.py --validate

# Verbose output
./run_tests.py --verbose
```

### Direct pytest Usage

```bash
# Run all tests
pytest tests/unit/

# Run with coverage
pytest tests/unit/ --cov=plugins/modules --cov-report=term-missing

# Run specific test
pytest tests/unit/test_clusters.py::TestClustersModule::test_list_clusters_success

# Run tests matching pattern
pytest tests/unit/ -k "test_api_error"

# Run with verbose output and show local variables
pytest tests/unit/ -v -l --tb=long
```

## Writing Tests for New Modules

### 1. Create Test File

```bash
# Copy existing test as template
cp tests/unit/test_supported_operators.py tests/unit/test_new_module.py
```

### 2. Update Test Class

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unit tests for new_module module
"""

import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Add the plugins directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'plugins', 'modules'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'plugins', 'module_utils'))

from base_test import BaseModuleTest, ModuleTestMixin

try:
    import new_module
except ImportError:
    new_module = None


class TestNewModuleModule(BaseModuleTest, ModuleTestMixin):
    """Test cases for new_module module"""

    def setUp(self):
        """Set up test fixtures"""
        super().setUp()
        if new_module is None:
            self.skipTest("new_module module not available")
        
        self.module_class = new_module
        self.default_params = {
            # Define module-specific default parameters
            'param1': None,
            'param2': 'default_value',
        }

    def get_default_params(self):
        return self.default_params.copy()

    # Add module-specific tests here
    @patch('new_module.apitoken.GetToken')
    @patch('new_module.requests.get')  # or post/delete as appropriate
    @patch('new_module.AnsibleModule')
    def test_module_specific_functionality(self, mock_ansible_module, mock_requests, mock_get_token):
        """Test module-specific functionality"""
        # Test implementation
        pass


if __name__ == '__main__':
    unittest.main()
```

### 3. Required Test Methods

Every module test should include:

**✅ Authentication Testing** (inherited from ModuleTestMixin)
- `test_missing_requests_library()` - Tests missing requests dependency
- `test_api_authentication_headers()` - Validates auth headers

**✅ Success Path Testing**
- Test successful API calls with expected responses
- Test parameter passing and query construction
- Test response processing and exit_json calls

**✅ Error Handling Testing**
- Test API error responses
- Test invalid parameters
- Test network failures

**✅ Module-Specific Testing**
- Test unique module functionality
- Test parameter validation rules
- Test utility functions

### 4. Test Patterns

#### Standard Success Test
```python
@patch('module.apitoken.GetToken')
@patch('module.requests.get')  # or appropriate HTTP method
@patch('module.AnsibleModule')
def test_success_scenario(self, mock_ansible_module, mock_requests, mock_get_token):
    # Setup mocks
    mock_get_token.return_value = self.mock_api_token
    mock_response = MagicMock()
    mock_response.ok = True
    mock_response.json.return_value = {"expected": "data"}
    mock_requests.return_value = mock_response
    
    # Create module instance with test parameters
    params = self.get_default_params()
    params.update({"test_param": "test_value"})
    mock_module_instance = self.create_mock_module(params)
    mock_ansible_module.return_value = mock_module_instance
    
    # Run the module
    module.run_module()
    
    # Verify API call
    mock_requests.assert_called_once()
    call_args = mock_requests.call_args
    self.assertIn('headers', call_args.kwargs)
    self.assertEqual(call_args.kwargs['headers']['Authorization'], f'Bearer {self.mock_api_token}')
    
    # Verify success response
    self.assert_exit_json_called_with_success(mock_module_instance, 'expected_key')
```

#### Standard Error Test
```python
@patch('module.apitoken.GetToken')
@patch('module.requests.get')
@patch('module.AnsibleModule')
def test_error_scenario(self, mock_ansible_module, mock_requests, mock_get_token):
    # Setup mocks for error
    mock_get_token.return_value = self.mock_api_token
    mock_response = MagicMock()
    mock_response.ok = False
    mock_response.text = "Error message"
    mock_requests.return_value = mock_response
    
    mock_module_instance = self.create_mock_module(self.get_default_params())
    mock_ansible_module.return_value = mock_module_instance
    
    # Run the module
    module.run_module()
    
    # Verify error handling
    self.assert_fail_json_called_with_error(mock_module_instance, "Expected error message")
```

## Coverage Requirements

### Minimum Coverage: 80%
- Enforced by pytest configuration
- Fails CI if not met

### Target Coverage: 90%+
- Aim for comprehensive coverage
- Critical paths should have 100% coverage

### Coverage Exclusions
- Import statements
- `if __name__ == '__main__'` blocks
- Defensive error handling that's hard to trigger

## Continuous Integration

### GitHub Actions Workflow

The `.github/workflows/tests.yml` workflow runs:

**Unit Tests**
- Python versions: 3.8, 3.9, 3.10, 3.11
- Full test suite with coverage reporting
- Coverage uploaded to Codecov

**Ansible Sanity Tests**
- ansible-test sanity validation
- Module documentation validation

**Code Quality**
- flake8 linting
- pylint static analysis

## Best Practices

### Test Organization
- One test file per module (`test_<module>.py`)
- One test class per module (`Test<Module>Module`)
- Descriptive test method names (`test_<function>_<scenario>`)

### Mock Usage
- Always mock external dependencies
- Use fixtures for common setups
- Verify mock calls to ensure correct API usage
- Don't mock the code under test

### Assertions
- Use base class assertion helpers
- Test both positive and negative cases
- Verify all important aspects (headers, params, responses)
- Include meaningful error messages

### Documentation
- Document complex test scenarios
- Use descriptive test names
- Add comments for non-obvious logic
- Keep docstrings up to date

## Troubleshooting

### Common Issues

**ImportError: No module named 'module_name'**
```bash
# Solution: Check module exists and path is correct
ls plugins/modules/module_name.py
```

**Mock not being called**
```python
# Solution: Verify patch target matches module import
# Wrong: @patch('requests.get')
# Right: @patch('module_name.requests.get')
```

**Tests pass locally but fail in CI**
```bash
# Solution: Check dependencies and Python version
pip install -r tests/unit/requirements.txt
python --version
```

### Debugging Commands

```bash
# Run with verbose output and stop on first failure
pytest tests/unit/ -v -x

# Run with debugger on failure
pytest tests/unit/ --pdb

# Show local variables on failure
pytest tests/unit/ -l --tb=long

# Run specific test with maximum verbosity
pytest tests/unit/test_clusters.py::TestClustersModule::test_list_clusters_success -v -s
```

## Future Enhancements

### Planned Improvements
- **Integration Tests** - Tests against real API endpoints
- **Performance Tests** - Module execution time measurement
- **Security Tests** - Credential handling validation
- **Property-Based Testing** - Hypothesis for edge cases
- **Mutation Testing** - Test quality validation

### Contributing Guidelines
1. Follow existing patterns and conventions
2. Test both success and failure paths
3. Mock all external dependencies
4. Maintain or improve coverage
5. Document complex scenarios
6. Update this guide for new patterns

## Support

For questions about the testing framework:
1. Check this documentation
2. Look at existing test examples
3. Review the base test classes
4. Open an issue with questions
