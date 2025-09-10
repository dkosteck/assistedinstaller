# -*- coding: utf-8 -*-
"""
Pytest configuration and fixtures for unit tests

assisted-by: Claude 3.5 Sonnet (Cursor)
"""

import pytest
import sys
import os
from unittest.mock import MagicMock, patch

# Add the plugins directory to the path for module imports
PLUGINS_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'plugins')
sys.path.insert(0, os.path.join(PLUGINS_PATH, 'modules'))
sys.path.insert(0, os.path.join(PLUGINS_PATH, 'module_utils'))


@pytest.fixture
def mock_ansible_module():
    """Fixture providing a mock AnsibleModule instance"""
    mock_module = MagicMock()
    mock_module.params = {}
    mock_module.exit_json = MagicMock()
    mock_module.fail_json = MagicMock()
    return mock_module


@pytest.fixture
def mock_api_token():
    """Fixture providing a mock API token"""
    return "mock-api-token-12345"


@pytest.fixture
def mock_api_response():
    """Fixture providing a mock successful API response"""
    mock_response = MagicMock()
    mock_response.ok = True
    mock_response.status_code = 200
    mock_response.json.return_value = {"test": "data"}
    mock_response.text = '{"test": "data"}'
    return mock_response


@pytest.fixture
def mock_api_error_response():
    """Fixture providing a mock error API response"""
    mock_response = MagicMock()
    mock_response.ok = False
    mock_response.status_code = 400
    mock_response.json.return_value = {"error": "Bad Request"}
    mock_response.text = '{"error": "Bad Request"}'
    return mock_response


@pytest.fixture
def mock_requests_get():
    """Fixture providing a mock requests.get function"""
    with patch('requests.get') as mock_get:
        yield mock_get


@pytest.fixture
def mock_requests_post():
    """Fixture providing a mock requests.post function"""
    with patch('requests.post') as mock_post:
        yield mock_post


@pytest.fixture
def mock_requests_delete():
    """Fixture providing a mock requests.delete function"""
    with patch('requests.delete') as mock_delete:
        yield mock_delete


@pytest.fixture
def mock_apitoken_get_token(mock_api_token):
    """Fixture providing a mock apitoken.GetToken function"""
    with patch('apitoken.GetToken', return_value=mock_api_token) as mock_get_token:
        yield mock_get_token


@pytest.fixture
def mock_apiurl_get_url():
    """Fixture providing a mock apiurl.GetURL function"""
    with patch('apiurl.GetURL') as mock_get_url:
        mock_get_url.side_effect = lambda path: f"https://api.openshift.com/api/assisted-install/v2{path}"
        yield mock_get_url


@pytest.fixture
def mock_ansible_module_class():
    """Fixture providing a mock AnsibleModule class"""
    with patch('AnsibleModule') as mock_class:
        yield mock_class


@pytest.fixture
def api_headers(mock_api_token):
    """Fixture providing standard API headers"""
    return {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {mock_api_token}'
    }


@pytest.fixture
def cluster_module_params():
    """Fixture providing cluster module specific parameters"""
    return {
        'state': None,
        'cluster_id': None,
        'with_hosts': False,
        'name': None,
        'openshift_version': None,
    }


@pytest.fixture(autouse=True)
def mock_missing_requests_lib():
    """Auto-used fixture to ensure HAS_REQUESTS is True for tests"""
    # This ensures that all modules can be imported for testing
    # Individual tests can override this if they need to test missing requests
    patches = []
    
    # Patch all known modules that check for requests
    module_names = [
        'clusters'  # Only keeping clusters as our example module
    ]
    
    for module_name in module_names:
        try:
            patch_target = f'{module_name}.HAS_REQUESTS'
            patches.append(patch(patch_target, True))
        except ImportError:
            # Module might not be available yet, skip
            pass
    
    # Start all patches
    started_patches = []
    for p in patches:
        try:
            started_patches.append(p.start())
        except:
            pass
    
    yield
    
    # Stop all patches
    for p in patches:
        try:
            p.stop()
        except:
            pass
