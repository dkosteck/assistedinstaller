# assistedinstaller ansible module

## Requirements

- Red Hat account in https://console.redhat.com
- Offline token from  https://console.redhat.com/openshift/token
- ocm-cli client from https://github.com/openshift-online/ocm-cli/releases or https://console.redhat.com/openshift/downloads#tool-ocm-api-token

## Modules

This collection provides the following modules for interacting with the OpenShift Assisted Installer API:

### clusters
Handle AssistedInstall clusters - create, list, and delete clusters.

### events
Query events from the Assisted Installer API.

### infra_envs
Manage infrastructure environments.

### openshift_versions
Query supported OpenShift versions.

### support_levels
Query OpenShift support levels for architectures and features.

### supported_operators
List supported operators.

## Development and Testing
<!-- Testing framework section assisted-by: Claude 3.5 Sonnet (Cursor) -->

### Testing Framework

This project includes a comprehensive testing framework with:
- **Unit Tests**: Full coverage for all modules
- **Mocking Framework**: Consistent mocking of external dependencies  
- **Coverage Reporting**: Detailed test coverage analysis
- **CI/CD Integration**: Automated testing in GitHub Actions

#### Running Tests

```bash
# Install test dependencies
make setup-dev

# Run all tests
make test

# Run tests with coverage
make test-coverage

# Run specific module tests
make test-module MODULE=clusters

# Run quick smoke test
make smoke-test
```

#### Test Structure
```
tests/
├── unit/                      # Unit tests
│   ├── conftest.py           # Pytest configuration and fixtures
│   ├── base_test.py          # Base test classes and utilities
│   └── test_clusters.py      # Example test (clusters module)
└── sanity/                   # Ansible sanity test configurations
```

For detailed testing information, see [tests/README.md](tests/README.md).

### Contributing

1. **Add tests** for new modules following existing patterns
2. **Maintain coverage** above 80% (target 90%+)
3. **Mock external dependencies** - no real API calls in unit tests
4. **Follow naming conventions** for consistency

## References
- Swagger UI -> https://api.openshift.com/?urls.primaryName=assisted-service%20service (next select the `assisted-service service` from the top right drop down menu)
