#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unit tests for supported_operators module

assisted-by: Claude 3.5 Sonnet (Cursor)
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
    import supported_operators
except ImportError:
    supported_operators = None


class TestSupportedOperatorsModule(BaseModuleTest, ModuleTestMixin):
    """Test cases for supported_operators module"""

    def setUp(self):
        """Set up test fixtures"""
        super().setUp()
        if supported_operators is None:
            self.skipTest("supported_operators module not available")
        
        self.module_class = supported_operators
        self.default_params = {}

    def get_default_params(self):
        return self.default_params.copy()

    @patch('supported_operators.apitoken.GetToken')
    @patch('supported_operators.requests.get')
    @patch('supported_operators.AnsibleModule')
    def test_list_supported_operators_success(self, mock_ansible_module, mock_requests_get, mock_get_token):
        """Test successful listing of supported operators"""
        # Setup mocks
        mock_get_token.return_value = self.mock_api_token
        
        mock_response = MagicMock()
        mock_response.ok = True
        mock_response.json.return_value = ["lso", "odf", "cnv", "lvm", "mce"]
        mock_requests_get.return_value = mock_response
        
        mock_module_instance = self.create_mock_module(self.get_default_params())
        mock_ansible_module.return_value = mock_module_instance
        
        # Run the module
        supported_operators.run_module()
        
        # Verify API call was made correctly
        mock_requests_get.assert_called_once()
        call_args = mock_requests_get.call_args
        self.assertIn('supported-operators', call_args[0][0])
        self.assertIn('headers', call_args.kwargs)
        self.assertEqual(call_args.kwargs['headers']['Authorization'], f'Bearer {self.mock_api_token}')
        
        # Verify successful exit
        self.assert_exit_json_called_with_success(mock_module_instance, 'supported_operators', expected_changed=False)

    @patch('supported_operators.apitoken.GetToken')
    @patch('supported_operators.requests.get')
    @patch('supported_operators.AnsibleModule')
    def test_api_error_handling_with_json_response(self, mock_ansible_module, mock_requests_get, mock_get_token):
        """Test API error handling when response contains JSON"""
        # Setup mocks
        mock_get_token.return_value = self.mock_api_token
        
        mock_response = MagicMock()
        mock_response.ok = False
        mock_response.json.return_value = {"error": "Unauthorized", "code": 401}
        mock_requests_get.return_value = mock_response
        
        mock_module_instance = self.create_mock_module(self.get_default_params())
        mock_ansible_module.return_value = mock_module_instance
        
        # Run the module
        supported_operators.run_module()
        
        # Verify error handling
        self.assert_fail_json_called_with_error(mock_module_instance, "Error listing supported operators")
        
        # Verify that the error response was parsed as JSON
        call_args = mock_module_instance.fail_json.call_args[1]
        self.assertEqual(call_args['response'], {"error": "Unauthorized", "code": 401})
        self.assertEqual(call_args['supported_operators'], [])
        self.assertFalse(call_args['changed'])

    @patch('supported_operators.apitoken.GetToken')
    @patch('supported_operators.requests.get')
    @patch('supported_operators.AnsibleModule')
    def test_api_error_handling_with_text_response(self, mock_ansible_module, mock_requests_get, mock_get_token):
        """Test API error handling when response is not JSON"""
        # Setup mocks
        mock_get_token.return_value = self.mock_api_token
        
        mock_response = MagicMock()
        mock_response.ok = False
        mock_response.json.side_effect = ValueError("Not JSON")  # Simulate JSONDecodeError
        mock_response.text = "Internal Server Error"
        mock_requests_get.return_value = mock_response
        
        mock_module_instance = self.create_mock_module(self.get_default_params())
        mock_ansible_module.return_value = mock_module_instance
        
        # Run the module
        supported_operators.run_module()
        
        # Verify error handling
        self.assert_fail_json_called_with_error(mock_module_instance, "Error listing supported operators")
        
        # Verify that the error response fell back to text
        call_args = mock_module_instance.fail_json.call_args[1]
        self.assertEqual(call_args['response'], "Internal Server Error")

    @patch('supported_operators.HAS_REQUESTS', False)
    @patch('supported_operators.AnsibleModule')
    def test_missing_requests_library(self, mock_ansible_module):
        """Test handling of missing requests library"""
        mock_module_instance = self.create_mock_module(self.get_default_params())
        mock_ansible_module.return_value = mock_module_instance
        
        # Run the module
        supported_operators.run_module()
        
        # Verify error handling
        self.assert_fail_json_called_with_error(mock_module_instance, "requests")

    @patch('supported_operators.apitoken.GetToken')
    @patch('supported_operators.requests.get')
    @patch('supported_operators.AnsibleModule')
    def test_empty_response(self, mock_ansible_module, mock_requests_get, mock_get_token):
        """Test handling of empty response"""
        # Setup mocks
        mock_get_token.return_value = self.mock_api_token
        
        mock_response = MagicMock()
        mock_response.ok = True
        mock_response.json.return_value = []
        mock_requests_get.return_value = mock_response
        
        mock_module_instance = self.create_mock_module(self.get_default_params())
        mock_ansible_module.return_value = mock_module_instance
        
        # Run the module
        supported_operators.run_module()
        
        # Verify successful exit with empty list
        self.assert_exit_json_called_with_success(mock_module_instance, 'supported_operators')
        call_args = mock_module_instance.exit_json.call_args[1]
        self.assertEqual(call_args['supported_operators'], [])

    @patch('supported_operators.apitoken.GetToken')
    @patch('supported_operators.requests.get')
    @patch('supported_operators.AnsibleModule')
    def test_no_query_parameters(self, mock_ansible_module, mock_requests_get, mock_get_token):
        """Test that no query parameters are sent (module has no parameters)"""
        # Setup mocks
        mock_get_token.return_value = self.mock_api_token
        
        mock_response = MagicMock()
        mock_response.ok = True
        mock_response.json.return_value = ["lso"]
        mock_requests_get.return_value = mock_response
        
        mock_module_instance = self.create_mock_module(self.get_default_params())
        mock_ansible_module.return_value = mock_module_instance
        
        # Run the module
        supported_operators.run_module()
        
        # Verify no query parameters were sent
        mock_requests_get.assert_called_once()
        call_args = mock_requests_get.call_args
        # Should not have params in kwargs, or params should be empty
        if 'params' in call_args.kwargs:
            self.assertEqual(call_args.kwargs['params'], {})

    @patch('supported_operators.apitoken.GetToken')
    @patch('supported_operators.requests.get')
    @patch('supported_operators.AnsibleModule')
    def test_api_url_construction(self, mock_ansible_module, mock_requests_get, mock_get_token):
        """Test that the API URL is constructed correctly"""
        # Setup mocks
        mock_get_token.return_value = self.mock_api_token
        
        mock_response = MagicMock()
        mock_response.ok = True
        mock_response.json.return_value = []
        mock_requests_get.return_value = mock_response
        
        mock_module_instance = self.create_mock_module(self.get_default_params())
        mock_ansible_module.return_value = mock_module_instance
        
        # Run the module
        supported_operators.run_module()
        
        # Verify URL construction
        mock_requests_get.assert_called_once()
        call_args = mock_requests_get.call_args
        url = call_args[0][0]
        self.assertIn('api.openshift.com/api/assisted-install/v2/supported-operators', url)


if __name__ == '__main__':
    unittest.main()
