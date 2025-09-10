#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unit tests for clusters module

assisted-by: Claude 3.5 Sonnet (Cursor)
"""

import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Add the plugins directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'plugins', 'modules'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'plugins', 'module_utils'))

from .base_test import BaseModuleTest, ModuleTestMixin

try:
    import clusters
except ImportError:
    clusters = None


class TestClustersModule(BaseModuleTest, ModuleTestMixin):
    """Test cases for clusters module"""

    def setUp(self):
        """Set up test fixtures"""
        super().setUp()
        if clusters is None:
            self.skipTest("clusters module not available")
        
        self.module_class = clusters
        self.default_params = {
            'state': None,
            'cluster_id': None,
            'with_hosts': False,
            'name': None,
            'openshift_version': None,
        }

    def get_default_params(self):
        return self.default_params.copy()

    @patch.dict(os.environ, {'AI_PULL_SECRET': 'test-pull-secret'})
    @patch('clusters.apitoken.GetToken')
    @patch('clusters.requests.get')
    @patch('clusters.AnsibleModule')
    def test_list_clusters_success(self, mock_ansible_module, mock_requests_get, mock_get_token):
        """Test successful cluster listing"""
        # Setup mocks
        mock_get_token.return_value = self.mock_api_token
        mock_response = MagicMock()
        mock_response.ok = True
        mock_response.json.return_value = [{"id": "cluster1", "name": "test-cluster"}]
        mock_requests_get.return_value = mock_response
        
        mock_module_instance = self.create_mock_module(self.get_default_params())
        mock_ansible_module.return_value = mock_module_instance
        
        # Run the module
        clusters.run_module()
        
        # Verify API call was made correctly
        mock_requests_get.assert_called_once()
        call_args = mock_requests_get.call_args
        self.assertIn('headers', call_args.kwargs)
        self.assertEqual(call_args.kwargs['headers']['Authorization'], f'Bearer {self.mock_api_token}')
        
        # Verify successful exit
        self.assert_exit_json_called_with_success(mock_module_instance, 'clusters')

    @patch('clusters.apitoken.GetToken')
    @patch('clusters.requests.get')
    @patch('clusters.AnsibleModule')
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
        clusters.run_module()
        
        # Verify error handling
        self.assert_fail_json_called_with_error(mock_module_instance, "Error listing clusters")

    @patch('clusters.HAS_REQUESTS', False)
    @patch('clusters.AnsibleModule')
    def test_missing_requests_library(self, mock_ansible_module):
        """Test handling of missing requests library"""
        mock_module_instance = self.create_mock_module(self.get_default_params())
        mock_ansible_module.return_value = mock_module_instance
        
        # Run the module
        clusters.run_module()
        
        # Verify error handling
        self.assert_fail_json_called_with_error(mock_module_instance, "requests")


if __name__ == '__main__':
    unittest.main()
