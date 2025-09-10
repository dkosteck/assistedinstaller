#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unit tests for openshift_versions module

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
    import openshift_versions
except ImportError:
    openshift_versions = None


class TestOpenshiftVersionsModule(BaseModuleTest, ModuleTestMixin):
    """Test cases for openshift_versions module"""

    def setUp(self):
        """Set up test fixtures"""
        super().setUp()
        if openshift_versions is None:
            self.skipTest("openshift_versions module not available")
        
        self.module_class = openshift_versions
        self.default_params = {
            'version': None,
            'only_latest': False,
        }

    def get_default_params(self):
        return self.default_params.copy()

    @patch('openshift_versions.apitoken.GetToken')
    @patch('openshift_versions.apiurl.GetURL')
    @patch('openshift_versions.requests.get')
    @patch('openshift_versions.AnsibleModule')
    def test_list_all_versions_success(self, mock_ansible_module, mock_requests_get, mock_get_url, mock_get_token):
        """Test successful listing of all OpenShift versions"""
        # Setup mocks
        mock_get_token.return_value = self.mock_api_token
        mock_get_url.return_value = f"{self.mock_api_url}/openshift-versions"
        
        mock_response = MagicMock()
        mock_response.ok = True
        mock_response.json.return_value = {
            "4.18.1": {
                "cpu_architectures": ["x86_64", "arm64"],
                "default": True,
                "display_name": "4.18.1",
                "support_level": "production"
            },
            "4.17.5": {
                "cpu_architectures": ["x86_64"],
                "default": False,
                "display_name": "4.17.5",
                "support_level": "production"
            }
        }
        mock_requests_get.return_value = mock_response
        
        mock_module_instance = self.create_mock_module(self.get_default_params())
        mock_ansible_module.return_value = mock_module_instance
        
        # Run the module
        openshift_versions.run_module()
        
        # Verify API call was made correctly
        mock_requests_get.assert_called_once()
        call_args = mock_requests_get.call_args
        self.assertIn('headers', call_args.kwargs)
        self.assertEqual(call_args.kwargs['headers']['Authorization'], f'Bearer {self.mock_api_token}')
        
        # Verify successful exit
        self.assert_exit_json_called_with_success(mock_module_instance, 'versions')

    @patch('openshift_versions.apitoken.GetToken')
    @patch('openshift_versions.apiurl.GetURL')
    @patch('openshift_versions.requests.get')
    @patch('openshift_versions.AnsibleModule')
    def test_list_versions_with_filter(self, mock_ansible_module, mock_requests_get, mock_get_url, mock_get_token):
        """Test listing OpenShift versions with version filter"""
        # Setup mocks
        mock_get_token.return_value = self.mock_api_token
        mock_get_url.return_value = f"{self.mock_api_url}/openshift-versions"
        
        mock_response = MagicMock()
        mock_response.ok = True
        mock_response.json.return_value = {
            "4.18.1": {
                "cpu_architectures": ["x86_64", "arm64"],
                "default": True,
                "display_name": "4.18.1",
                "support_level": "production"
            }
        }
        mock_requests_get.return_value = mock_response
        
        params = self.get_default_params()
        params.update({
            'version': '4.18',
            'only_latest': True
        })
        mock_module_instance = self.create_mock_module(params)
        mock_ansible_module.return_value = mock_module_instance
        
        # Run the module
        openshift_versions.run_module()
        
        # Verify query parameters were included
        mock_requests_get.assert_called_once()
        call_args = mock_requests_get.call_args
        self.assertIn('params', call_args.kwargs)
        self.assertEqual(call_args.kwargs['params']['version'], '4.18')
        self.assertEqual(call_args.kwargs['params']['only_latest'], True)

    @patch('openshift_versions.apitoken.GetToken')
    @patch('openshift_versions.apiurl.GetURL')
    @patch('openshift_versions.requests.get')
    @patch('openshift_versions.AnsibleModule')
    def test_list_versions_only_latest(self, mock_ansible_module, mock_requests_get, mock_get_url, mock_get_token):
        """Test listing only latest versions"""
        # Setup mocks
        mock_get_token.return_value = self.mock_api_token
        mock_get_url.return_value = f"{self.mock_api_url}/openshift-versions"
        
        mock_response = MagicMock()
        mock_response.ok = True
        mock_response.json.return_value = {
            "4.18.1": {
                "cpu_architectures": ["x86_64", "arm64"],
                "default": True,
                "display_name": "4.18.1",
                "support_level": "production"
            }
        }
        mock_requests_get.return_value = mock_response
        
        params = self.get_default_params()
        params['only_latest'] = True
        mock_module_instance = self.create_mock_module(params)
        mock_ansible_module.return_value = mock_module_instance
        
        # Run the module
        openshift_versions.run_module()
        
        # Verify query parameter was included
        mock_requests_get.assert_called_once()
        call_args = mock_requests_get.call_args
        self.assertIn('params', call_args.kwargs)
        self.assertEqual(call_args.kwargs['params']['only_latest'], True)

    @patch('openshift_versions.apitoken.GetToken')
    @patch('openshift_versions.apiurl.GetURL')
    @patch('openshift_versions.requests.get')
    @patch('openshift_versions.AnsibleModule')
    def test_api_error_handling(self, mock_ansible_module, mock_requests_get, mock_get_url, mock_get_token):
        """Test API error handling"""
        # Setup mocks
        mock_get_token.return_value = self.mock_api_token
        mock_get_url.return_value = f"{self.mock_api_url}/openshift-versions"
        
        mock_response = MagicMock()
        mock_response.ok = False
        mock_response.text = "API Error"
        mock_requests_get.return_value = mock_response
        
        mock_module_instance = self.create_mock_module(self.get_default_params())
        mock_ansible_module.return_value = mock_module_instance
        
        # Run the module
        openshift_versions.run_module()
        
        # Verify error handling
        self.assert_fail_json_called_with_error(mock_module_instance, "Error querying openshift versions")

    @patch('openshift_versions.HAS_REQUESTS', False)
    @patch('openshift_versions.AnsibleModule')
    def test_missing_requests_library(self, mock_ansible_module):
        """Test handling of missing requests library"""
        mock_module_instance = self.create_mock_module(self.get_default_params())
        mock_ansible_module.return_value = mock_module_instance
        
        # Run the module
        openshift_versions.run_module()
        
        # Verify error handling
        self.assert_fail_json_called_with_error(mock_module_instance, "requests")

    @patch('openshift_versions.apitoken.GetToken')
    @patch('openshift_versions.apiurl.GetURL')
    @patch('openshift_versions.requests.get')
    @patch('openshift_versions.AnsibleModule')
    def test_empty_query_params(self, mock_ansible_module, mock_requests_get, mock_get_url, mock_get_token):
        """Test that empty query parameters are not included"""
        # Setup mocks
        mock_get_token.return_value = self.mock_api_token
        mock_get_url.return_value = f"{self.mock_api_url}/openshift-versions"
        
        mock_response = MagicMock()
        mock_response.ok = True
        mock_response.json.return_value = {}
        mock_requests_get.return_value = mock_response
        
        params = self.get_default_params()
        params.update({
            'version': None,  # Should not be included
            'only_latest': False  # Should not be included (falsy)
        })
        mock_module_instance = self.create_mock_module(params)
        mock_ansible_module.return_value = mock_module_instance
        
        # Run the module
        openshift_versions.run_module()
        
        # Verify empty parameters were not included
        mock_requests_get.assert_called_once()
        call_args = mock_requests_get.call_args
        params_passed = call_args.kwargs.get('params', {})
        self.assertEqual(len(params_passed), 0)


if __name__ == '__main__':
    unittest.main()
