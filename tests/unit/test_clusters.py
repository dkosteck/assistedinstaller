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

from base_test import BaseModuleTest, ModuleTestMixin

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

    @patch.dict(os.environ, {'AI_PULL_SECRET': 'test-pull-secret'})
    @patch('clusters.apitoken.GetToken')
    @patch('clusters.requests.post')
    @patch('clusters.AnsibleModule')
    def test_create_cluster_success(self, mock_ansible_module, mock_requests_post, mock_get_token):
        """Test successful cluster creation"""
        # Setup mocks
        mock_get_token.return_value = self.mock_api_token
        mock_response = MagicMock()
        mock_response.ok = True
        mock_response.json.return_value = {"id": "new-cluster", "name": "test-cluster"}
        mock_requests_post.return_value = mock_response
        
        params = self.get_default_params()
        params.update({
            'state': 'present',
            'name': 'test-cluster',
            'openshift_version': '4.18.1'
        })
        mock_module_instance = self.create_mock_module(params)
        mock_ansible_module.return_value = mock_module_instance
        
        # Run the module
        clusters.run_module()
        
        # Verify API call was made correctly
        mock_requests_post.assert_called_once()
        call_args = mock_requests_post.call_args
        self.assertIn('json', call_args.kwargs)
        self.assertEqual(call_args.kwargs['json']['name'], 'test-cluster')
        self.assertEqual(call_args.kwargs['json']['openshift_version'], '4.18.1')
        self.assertEqual(call_args.kwargs['json']['pull_secret'], 'test-pull-secret')
        
        # Verify successful exit
        self.assert_exit_json_called_with_success(mock_module_instance, 'clusters')

    @patch('clusters.apitoken.GetToken')
    @patch('clusters.requests.delete')
    @patch('clusters.AnsibleModule')
    def test_delete_cluster_success(self, mock_ansible_module, mock_requests_delete, mock_get_token):
        """Test successful cluster deletion"""
        # Setup mocks
        mock_get_token.return_value = self.mock_api_token
        mock_response = MagicMock()
        mock_response.status_code = 204
        mock_requests_delete.return_value = mock_response
        
        params = self.get_default_params()
        params.update({
            'state': 'absent',
            'cluster_id': 'test-cluster-id'
        })
        mock_module_instance = self.create_mock_module(params)
        mock_ansible_module.return_value = mock_module_instance
        
        # Run the module
        clusters.run_module()
        
        # Verify API call was made correctly
        mock_requests_delete.assert_called_once()
        call_args = mock_requests_delete.call_args
        self.assertIn('test-cluster-id', call_args[0][0])
        
        # Verify successful exit
        self.assert_exit_json_called_with_success(mock_module_instance, 'clusters', expected_changed=True)

    @patch('clusters.apitoken.GetToken')
    @patch('clusters.requests.get')
    @patch('clusters.AnsibleModule')
    def test_list_clusters_with_hosts(self, mock_ansible_module, mock_requests_get, mock_get_token):
        """Test cluster listing with hosts parameter"""
        # Setup mocks
        mock_get_token.return_value = self.mock_api_token
        mock_response = MagicMock()
        mock_response.ok = True
        mock_response.json.return_value = []
        mock_requests_get.return_value = mock_response
        
        params = self.get_default_params()
        params['with_hosts'] = True
        mock_module_instance = self.create_mock_module(params)
        mock_ansible_module.return_value = mock_module_instance
        
        # Run the module
        clusters.run_module()
        
        # Verify query parameter was included
        mock_requests_get.assert_called_once()
        call_args = mock_requests_get.call_args
        self.assertIn('params', call_args.kwargs)
        self.assertEqual(call_args.kwargs['params']['with_hosts'], True)

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

    def test_remove_module_fields(self):
        """Test the remove_module_fields utility function"""
        mock_module = MagicMock()
        mock_module.params = {
            'state': 'present',
            'with_hosts': True,
            'cluster_id': 'test-id',
            'name': 'test-cluster',
            'openshift_version': '4.18.1'
        }
        
        result = clusters.remove_module_fields(mock_module)
        
        # Verify removed fields
        self.assertNotIn('state', result)
        self.assertNotIn('with_hosts', result)
        self.assertNotIn('cluster_id', result)
        
        # Verify kept fields
        self.assertIn('name', result)
        self.assertIn('openshift_version', result)
        self.assertEqual(result['name'], 'test-cluster')
        self.assertEqual(result['openshift_version'], '4.18.1')


if __name__ == '__main__':
    unittest.main()
