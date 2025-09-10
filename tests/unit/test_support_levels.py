#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unit tests for support_levels module

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
    import support_levels
except ImportError:
    support_levels = None


class TestSupportLevelsModule(BaseModuleTest, ModuleTestMixin):
    """Test cases for support_levels module"""

    def setUp(self):
        """Set up test fixtures"""
        super().setUp()
        if support_levels is None:
            self.skipTest("support_levels module not available")
        
        self.module_class = support_levels
        self.default_params = {
            'resource_type': 'architectures',
            'openshift_version': '4.18.1',
            'cpu_architecture': 'x86_64',
            'platform_type': None,
            'external_platform_name': None,
        }

    def get_default_params(self):
        return self.default_params.copy()

    @patch('support_levels.apitoken.GetToken')
    @patch('support_levels.requests.get')
    @patch('support_levels.AnsibleModule')
    def test_query_architectures_success(self, mock_ansible_module, mock_requests_get, mock_get_token):
        """Test successful query of supported architectures"""
        # Setup mocks
        mock_get_token.return_value = self.mock_api_token
        
        mock_response = MagicMock()
        mock_response.ok = True
        mock_response.json.return_value = {
            "ARM64_ARCHITECTURE": "supported",
            "MULTIARCH_RELEASE_IMAGE": "tech-preview",
            "PPC64LE_ARCHITECTURE": "supported",
            "S390X_ARCHITECTURE": "supported",
            "X86_64_ARCHITECTURE": "supported"
        }
        mock_requests_get.return_value = mock_response
        
        mock_module_instance = self.create_mock_module(self.get_default_params())
        mock_ansible_module.return_value = mock_module_instance
        
        # Run the module
        support_levels.run_module()
        
        # Verify API call was made correctly
        mock_requests_get.assert_called_once()
        call_args = mock_requests_get.call_args
        self.assertIn('support-levels/architectures', call_args[0][0])
        self.assertIn('headers', call_args.kwargs)
        self.assertEqual(call_args.kwargs['headers']['Authorization'], f'Bearer {self.mock_api_token}')
        
        # Verify query parameters
        self.assertIn('params', call_args.kwargs)
        self.assertEqual(call_args.kwargs['params']['openshift_version'], '4.18.1')
        
        # Verify successful exit
        mock_module_instance.exit_json.assert_called_once()

    @patch('support_levels.apitoken.GetToken')
    @patch('support_levels.requests.get')
    @patch('support_levels.AnsibleModule')
    def test_query_features_success(self, mock_ansible_module, mock_requests_get, mock_get_token):
        """Test successful query of supported features"""
        # Setup mocks
        mock_get_token.return_value = self.mock_api_token
        
        mock_response = MagicMock()
        mock_response.ok = True
        mock_response.json.return_value = {
            "CLUSTER_MANAGED_NETWORKING": "supported",
            "CNV": "supported",
            "CUSTOM_MANIFEST": "supported",
            "DUAL_STACK": "supported",
            "SNO": "supported"
        }
        mock_requests_get.return_value = mock_response
        
        params = self.get_default_params()
        params.update({
            'resource_type': 'features',
            'openshift_version': '4.18.1',
            'cpu_architecture': 'x86_64',
            'platform_type': 'baremetal'
        })
        mock_module_instance = self.create_mock_module(params)
        mock_ansible_module.return_value = mock_module_instance
        
        # Run the module
        support_levels.run_module()
        
        # Verify API call was made correctly
        mock_requests_get.assert_called_once()
        call_args = mock_requests_get.call_args
        self.assertIn('support-levels/features', call_args[0][0])
        
        # Verify query parameters for features
        self.assertIn('params', call_args.kwargs)
        params_passed = call_args.kwargs['params']
        self.assertEqual(params_passed['openshift_version'], '4.18.1')
        self.assertEqual(params_passed['cpu_architecture'], 'x86_64')
        self.assertEqual(params_passed['platform_type'], 'baremetal')
        
        # Verify successful exit
        mock_module_instance.exit_json.assert_called_once()

    @patch('support_levels.apitoken.GetToken')
    @patch('support_levels.requests.get')
    @patch('support_levels.AnsibleModule')
    def test_query_features_with_external_platform(self, mock_ansible_module, mock_requests_get, mock_get_token):
        """Test query of features with external platform"""
        # Setup mocks
        mock_get_token.return_value = self.mock_api_token
        
        mock_response = MagicMock()
        mock_response.ok = True
        mock_response.json.return_value = {}
        mock_requests_get.return_value = mock_response
        
        params = self.get_default_params()
        params.update({
            'resource_type': 'features',
            'openshift_version': '4.18.1',
            'cpu_architecture': 'x86_64',
            'platform_type': 'external',
            'external_platform_name': 'oci'
        })
        mock_module_instance = self.create_mock_module(params)
        mock_ansible_module.return_value = mock_module_instance
        
        # Run the module
        support_levels.run_module()
        
        # Verify query parameters include external platform name
        mock_requests_get.assert_called_once()
        call_args = mock_requests_get.call_args
        params_passed = call_args.kwargs['params']
        self.assertEqual(params_passed['platform_type'], 'external')
        self.assertEqual(params_passed['external_platform_name'], 'oci')

    @patch('support_levels.apitoken.GetToken')
    @patch('support_levels.requests.get')
    @patch('support_levels.AnsibleModule')
    def test_api_error_handling(self, mock_ansible_module, mock_requests_get, mock_get_token):
        """Test API error handling"""
        # Setup mocks
        mock_get_token.return_value = self.mock_api_token
        
        mock_response = MagicMock()
        mock_response.ok = False
        mock_response.text = "API Error"
        mock_requests_get.return_value = mock_response
        
        mock_module_instance = self.create_mock_module(self.get_default_params())
        mock_ansible_module.return_value = mock_module_instance
        
        # Run the module
        support_levels.run_module()
        
        # Verify error handling
        self.assert_fail_json_called_with_error(mock_module_instance, "Error querying architectures")

    @patch('support_levels.HAS_REQUESTS', False)
    @patch('support_levels.AnsibleModule')
    def test_missing_requests_library(self, mock_ansible_module):
        """Test handling of missing requests library"""
        mock_module_instance = self.create_mock_module(self.get_default_params())
        mock_ansible_module.return_value = mock_module_instance
        
        # Run the module
        support_levels.run_module()
        
        # Verify error handling
        self.assert_fail_json_called_with_error(mock_module_instance, "requests")

    @patch('support_levels.apitoken.GetToken')
    @patch('support_levels.requests.get')
    @patch('support_levels.AnsibleModule')
    def test_query_params_filtering(self, mock_ansible_module, mock_requests_get, mock_get_token):
        """Test that only relevant query parameters are included based on resource type"""
        # Setup mocks
        mock_get_token.return_value = self.mock_api_token
        
        mock_response = MagicMock()
        mock_response.ok = True
        mock_response.json.return_value = {}
        mock_requests_get.return_value = mock_response
        
        # Test architectures - should only include openshift_version
        params = self.get_default_params()
        params.update({
            'resource_type': 'architectures',
            'openshift_version': '4.18.1',
            'cpu_architecture': 'x86_64',  # Should be ignored for architectures
            'platform_type': 'baremetal',  # Should be ignored for architectures
        })
        mock_module_instance = self.create_mock_module(params)
        mock_ansible_module.return_value = mock_module_instance
        
        # Run the module
        support_levels.run_module()
        
        # Verify only openshift_version is in query params for architectures
        mock_requests_get.assert_called_once()
        call_args = mock_requests_get.call_args
        params_passed = call_args.kwargs['params']
        self.assertEqual(len(params_passed), 1)
        self.assertEqual(params_passed['openshift_version'], '4.18.1')

    @patch('support_levels.apitoken.GetToken')
    @patch('support_levels.requests.get')
    @patch('support_levels.AnsibleModule')
    def test_none_values_excluded_from_params(self, mock_ansible_module, mock_requests_get, mock_get_token):
        """Test that None values are excluded from query parameters"""
        # Setup mocks
        mock_get_token.return_value = self.mock_api_token
        
        mock_response = MagicMock()
        mock_response.ok = True
        mock_response.json.return_value = {}
        mock_requests_get.return_value = mock_response
        
        params = self.get_default_params()
        params.update({
            'resource_type': 'features',
            'openshift_version': '4.18.1',
            'cpu_architecture': 'x86_64',
            'platform_type': None,  # Should be excluded
            'external_platform_name': None,  # Should be excluded
        })
        mock_module_instance = self.create_mock_module(params)
        mock_ansible_module.return_value = mock_module_instance
        
        # Run the module
        support_levels.run_module()
        
        # Verify None values are excluded
        mock_requests_get.assert_called_once()
        call_args = mock_requests_get.call_args
        params_passed = call_args.kwargs['params']
        self.assertNotIn('platform_type', params_passed)
        self.assertNotIn('external_platform_name', params_passed)
        self.assertEqual(params_passed['openshift_version'], '4.18.1')
        self.assertEqual(params_passed['cpu_architecture'], 'x86_64')


if __name__ == '__main__':
    unittest.main()
