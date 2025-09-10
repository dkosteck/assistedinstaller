# -*- coding: utf-8 -*-
"""
Base test class for assistedinstaller module tests

assisted-by: Claude 3.5 Sonnet (Cursor)
"""

import unittest
from unittest.mock import MagicMock, patch
import sys
import os

# Add the plugins directory to the path
PLUGINS_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'plugins')
sys.path.insert(0, os.path.join(PLUGINS_PATH, 'modules'))
sys.path.insert(0, os.path.join(PLUGINS_PATH, 'module_utils'))


class BaseModuleTest(unittest.TestCase):
    """Base test class for Ansible module testing"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.mock_api_token = "test-token-12345"
        self.mock_api_url = "https://api.openshift.com/api/assisted-install/v2"
        
        # Default successful response
        self.mock_success_response = MagicMock()
        self.mock_success_response.ok = True
        self.mock_success_response.status_code = 200
        self.mock_success_response.json.return_value = {"test": "data"}
        
        # Default error response
        self.mock_error_response = MagicMock()
        self.mock_error_response.ok = False
        self.mock_error_response.status_code = 400
        self.mock_error_response.json.return_value = {"error": "Bad Request"}
        self.mock_error_response.text = "Bad Request"
    
    def create_mock_module(self, params=None):
        """Create a mock AnsibleModule instance"""
        mock_module = MagicMock()
        mock_module.params = params or {}
        mock_module.exit_json = MagicMock()
        mock_module.fail_json = MagicMock()
        return mock_module
    
    def get_standard_headers(self):
        """Get standard API headers"""
        return {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.mock_api_token}'
        }
    
    def assert_exit_json_called_with_success(self, mock_module, expected_key=None, expected_changed=False):
        """Assert that exit_json was called with success parameters"""
        mock_module.exit_json.assert_called_once()
        call_args = mock_module.exit_json.call_args[1]
        
        if 'changed' in call_args:
            self.assertEqual(call_args['changed'], expected_changed)
        
        if expected_key:
            self.assertIn(expected_key, call_args)
    
    def assert_fail_json_called_with_error(self, mock_module, expected_msg=None):
        """Assert that fail_json was called with error parameters"""
        mock_module.fail_json.assert_called_once()
        call_args = mock_module.fail_json.call_args[1]
        
        if expected_msg:
            self.assertIn(expected_msg, call_args['msg'])
    
    def patch_requests_and_auth(self, response=None):
        """Context manager to patch requests and authentication"""
        if response is None:
            response = self.mock_success_response
        
        return patch.multiple(
            'requests',
            get=MagicMock(return_value=response),
            post=MagicMock(return_value=response),
            delete=MagicMock(return_value=response)
        )
    
    def patch_ansible_module(self, mock_module):
        """Context manager to patch AnsibleModule"""
        return patch('AnsibleModule', return_value=mock_module)
    
    def patch_apitoken(self):
        """Context manager to patch apitoken.GetToken"""
        return patch('apitoken.GetToken', return_value=self.mock_api_token)
    
    def patch_apiurl(self):
        """Context manager to patch apiurl.GetURL"""
        def mock_get_url(path):
            if not path.startswith("/"):
                path = "/" + path
            return f"{self.mock_api_url}{path}"
        
        return patch('apiurl.GetURL', side_effect=mock_get_url)


class ModuleTestMixin:
    """Mixin class providing common test methods for modules"""
    
    def test_missing_requests_library(self):
        """Test handling of missing requests library"""
        if not hasattr(self, 'module_class'):
            self.skipTest("module_class not defined")
        
        mock_module = self.create_mock_module()
        
        with patch(f'{self.module_class.__name__}.HAS_REQUESTS', False):
            with self.patch_ansible_module(mock_module):
                self.module_class.run_module()
        
        self.assert_fail_json_called_with_error(mock_module, "requests")
    
    def test_api_authentication_headers(self):
        """Test that API calls include proper authentication headers"""
        if not hasattr(self, 'module_class'):
            self.skipTest("module_class not defined")
        
        mock_module = self.create_mock_module(self.get_default_params())
        
        with self.patch_requests_and_auth() as mock_requests:
            with self.patch_ansible_module(mock_module):
                with self.patch_apitoken():
                    with self.patch_apiurl():
                        self.module_class.run_module()
        
        # Check that at least one request was made with auth headers
        request_made = False
        for method in ['get', 'post', 'delete']:
            mock_method = getattr(mock_requests[method], 'return_value', None)
            if mock_method and mock_requests[method].called:
                call_args = mock_requests[method].call_args
                if 'headers' in call_args.kwargs:
                    headers = call_args.kwargs['headers']
                    self.assertIn('Authorization', headers)
                    self.assertIn('Bearer', headers['Authorization'])
                    request_made = True
                    break
        
        self.assertTrue(request_made, "No authenticated request was made")
    
    def get_default_params(self):
        """Override in subclasses to provide default module parameters"""
        return {}


def create_test_case_for_module(module_name, module_class, default_params=None, 
                                expected_result_key=None, test_scenarios=None):
    """
    Factory function to create test cases for modules
    
    Args:
        module_name: Name of the module
        module_class: The module class to test
        default_params: Default parameters for the module
        expected_result_key: Expected key in successful results
        test_scenarios: List of test scenarios with params and expected results
    """
    
    class GeneratedModuleTest(BaseModuleTest, ModuleTestMixin):
        
        def setUp(self):
            super().setUp()
            self.module_class = module_class
            self.module_name = module_name
            self.default_params = default_params or {}
            self.expected_result_key = expected_result_key
            self.test_scenarios = test_scenarios or []
        
        def get_default_params(self):
            return self.default_params.copy()
        
        def test_successful_api_call(self):
            """Test successful API call"""
            mock_module = self.create_mock_module(self.get_default_params())
            
            with self.patch_requests_and_auth():
                with self.patch_ansible_module(mock_module):
                    with self.patch_apitoken():
                        with self.patch_apiurl():
                            self.module_class.run_module()
            
            self.assert_exit_json_called_with_success(
                mock_module, 
                expected_key=self.expected_result_key
            )
        
        def test_api_error_handling(self):
            """Test API error handling"""
            mock_module = self.create_mock_module(self.get_default_params())
            
            with self.patch_requests_and_auth(response=self.mock_error_response):
                with self.patch_ansible_module(mock_module):
                    with self.patch_apitoken():
                        with self.patch_apiurl():
                            self.module_class.run_module()
            
            self.assert_fail_json_called_with_error(mock_module, "Error")
        
        def test_scenarios(self):
            """Test various scenarios if provided"""
            for i, scenario in enumerate(self.test_scenarios):
                with self.subTest(scenario=i):
                    params = scenario.get('params', {})
                    expected_response = scenario.get('response', self.mock_success_response)
                    should_fail = scenario.get('should_fail', False)
                    
                    mock_module = self.create_mock_module(params)
                    
                    with self.patch_requests_and_auth(response=expected_response):
                        with self.patch_ansible_module(mock_module):
                            with self.patch_apitoken():
                                with self.patch_apiurl():
                                    self.module_class.run_module()
                    
                    if should_fail:
                        self.assert_fail_json_called_with_error(mock_module)
                    else:
                        self.assert_exit_json_called_with_success(mock_module)
    
    # Set a meaningful class name
    GeneratedModuleTest.__name__ = f'Test{module_name.title().replace("_", "")}Module'
    GeneratedModuleTest.__qualname__ = GeneratedModuleTest.__name__
    
    return GeneratedModuleTest
