#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unit tests for events module

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
    import events
except ImportError:
    events = None


class TestEventsModule(BaseModuleTest, ModuleTestMixin):
    """Test cases for events module"""

    def setUp(self):
        """Set up test fixtures"""
        super().setUp()
        if events is None:
            self.skipTest("events module not available")
        
        self.module_class = events
        self.default_params = {
            'cluster_id': None,
            'limit': None,
            'order': 'ascending',
            'offset': 0,
            'severities': None,
        }

    def get_default_params(self):
        return self.default_params.copy()

    @patch('events.apitoken.GetToken')
    @patch('events.requests.get')
    @patch('events.AnsibleModule')
    def test_list_events_success(self, mock_ansible_module, mock_requests_get, mock_get_token):
        """Test successful listing of events"""
        # Setup mocks
        mock_get_token.return_value = self.mock_api_token
        
        mock_response = MagicMock()
        mock_response.ok = True
        mock_response.json.return_value = [
            {
                "cluster_id": "46f3094d-8967-4f1d-ad09-d5fdfda3830a",
                "event_time": "2024-11-08T20:15:44.447Z",
                "message": "Successfully registered cluster",
                "name": "cluster_registration_succeeded",
                "severity": "info"
            },
            {
                "cluster_id": "46f3094d-8967-4f1d-ad09-d5fdfda3830a",
                "event_time": "2024-11-08T20:15:52.436Z",
                "message": "Updated status of the cluster to pending-for-input",
                "name": "cluster_status_updated",
                "severity": "info"
            }
        ]
        mock_requests_get.return_value = mock_response
        
        mock_module_instance = self.create_mock_module(self.get_default_params())
        mock_ansible_module.return_value = mock_module_instance
        
        # Run the module
        events.run_module()
        
        # Verify API call was made correctly
        mock_requests_get.assert_called_once()
        call_args = mock_requests_get.call_args
        self.assertIn('events', call_args[0][0])
        self.assertIn('headers', call_args.kwargs)
        self.assertEqual(call_args.kwargs['headers']['Authorization'], f'Bearer {self.mock_api_token}')
        
        # Verify successful exit
        self.assert_exit_json_called_with_success(mock_module_instance, 'cluster_events', expected_changed=False)

    @patch('events.apitoken.GetToken')
    @patch('events.requests.get')
    @patch('events.AnsibleModule')
    def test_list_events_with_cluster_id(self, mock_ansible_module, mock_requests_get, mock_get_token):
        """Test listing events with cluster ID filter"""
        # Setup mocks
        mock_get_token.return_value = self.mock_api_token
        
        mock_response = MagicMock()
        mock_response.ok = True
        mock_response.json.return_value = []
        mock_requests_get.return_value = mock_response
        
        params = self.get_default_params()
        params['cluster_id'] = 'test-cluster-id'
        mock_module_instance = self.create_mock_module(params)
        mock_ansible_module.return_value = mock_module_instance
        
        # Run the module
        events.run_module()
        
        # Verify query parameters
        mock_requests_get.assert_called_once()
        call_args = mock_requests_get.call_args
        self.assertIn('params', call_args.kwargs)
        self.assertEqual(call_args.kwargs['params']['cluster_id'], 'test-cluster-id')

    @patch('events.apitoken.GetToken')
    @patch('events.requests.get')
    @patch('events.AnsibleModule')
    def test_list_events_with_pagination(self, mock_ansible_module, mock_requests_get, mock_get_token):
        """Test listing events with pagination parameters"""
        # Setup mocks
        mock_get_token.return_value = self.mock_api_token
        
        mock_response = MagicMock()
        mock_response.ok = True
        mock_response.json.return_value = []
        mock_requests_get.return_value = mock_response
        
        params = self.get_default_params()
        params.update({
            'limit': 50,
            'offset': 10,
            'order': 'descending'
        })
        mock_module_instance = self.create_mock_module(params)
        mock_ansible_module.return_value = mock_module_instance
        
        # Run the module
        events.run_module()
        
        # Verify query parameters
        mock_requests_get.assert_called_once()
        call_args = mock_requests_get.call_args
        self.assertIn('params', call_args.kwargs)
        params_passed = call_args.kwargs['params']
        self.assertEqual(params_passed['limit'], 50)
        self.assertEqual(params_passed['offset'], 10)
        self.assertEqual(params_passed['order'], 'descending')

    @patch('events.apitoken.GetToken')
    @patch('events.requests.get')
    @patch('events.AnsibleModule')
    def test_list_events_with_severities(self, mock_ansible_module, mock_requests_get, mock_get_token):
        """Test listing events with severity filters"""
        # Setup mocks
        mock_get_token.return_value = self.mock_api_token
        
        mock_response = MagicMock()
        mock_response.ok = True
        mock_response.json.return_value = []
        mock_requests_get.return_value = mock_response
        
        params = self.get_default_params()
        params['severities'] = ['critical', 'error', 'warning']
        mock_module_instance = self.create_mock_module(params)
        mock_ansible_module.return_value = mock_module_instance
        
        # Run the module
        events.run_module()
        
        # Verify query parameters (list should be joined with commas)
        mock_requests_get.assert_called_once()
        call_args = mock_requests_get.call_args
        self.assertIn('params', call_args.kwargs)
        self.assertEqual(call_args.kwargs['params']['severities'], 'critical,error,warning')

    @patch('events.apitoken.GetToken')
    @patch('events.requests.get')
    @patch('events.AnsibleModule')
    def test_list_events_with_single_severity(self, mock_ansible_module, mock_requests_get, mock_get_token):
        """Test listing events with single severity filter"""
        # Setup mocks
        mock_get_token.return_value = self.mock_api_token
        
        mock_response = MagicMock()
        mock_response.ok = True
        mock_response.json.return_value = []
        mock_requests_get.return_value = mock_response
        
        params = self.get_default_params()
        params['severities'] = ['info']
        mock_module_instance = self.create_mock_module(params)
        mock_ansible_module.return_value = mock_module_instance
        
        # Run the module
        events.run_module()
        
        # Verify query parameters
        mock_requests_get.assert_called_once()
        call_args = mock_requests_get.call_args
        self.assertIn('params', call_args.kwargs)
        self.assertEqual(call_args.kwargs['params']['severities'], 'info')

    @patch('events.apitoken.GetToken')
    @patch('events.requests.get')
    @patch('events.AnsibleModule')
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
        events.run_module()
        
        # Verify error handling
        self.assert_fail_json_called_with_error(mock_module_instance, "Error listing cluster events")

    @patch('events.HAS_REQUESTS', False)
    @patch('events.AnsibleModule')
    def test_missing_requests_library(self, mock_ansible_module):
        """Test handling of missing requests library"""
        mock_module_instance = self.create_mock_module(self.get_default_params())
        mock_ansible_module.return_value = mock_module_instance
        
        # Run the module
        events.run_module()
        
        # Verify error handling
        self.assert_fail_json_called_with_error(mock_module_instance, "requests")

    @patch('events.apitoken.GetToken')
    @patch('events.requests.get')
    @patch('events.AnsibleModule')
    def test_default_offset_parameter(self, mock_ansible_module, mock_requests_get, mock_get_token):
        """Test that default offset parameter is included"""
        # Setup mocks
        mock_get_token.return_value = self.mock_api_token
        
        mock_response = MagicMock()
        mock_response.ok = True
        mock_response.json.return_value = []
        mock_requests_get.return_value = mock_response
        
        mock_module_instance = self.create_mock_module(self.get_default_params())
        mock_ansible_module.return_value = mock_module_instance
        
        # Run the module
        events.run_module()
        
        # Verify default offset is included
        mock_requests_get.assert_called_once()
        call_args = mock_requests_get.call_args
        self.assertIn('params', call_args.kwargs)
        self.assertEqual(call_args.kwargs['params']['offset'], 0)

    @patch('events.apitoken.GetToken')
    @patch('events.requests.get')
    @patch('events.AnsibleModule')
    def test_default_order_parameter(self, mock_ansible_module, mock_requests_get, mock_get_token):
        """Test that default order parameter is included"""
        # Setup mocks
        mock_get_token.return_value = self.mock_api_token
        
        mock_response = MagicMock()
        mock_response.ok = True
        mock_response.json.return_value = []
        mock_requests_get.return_value = mock_response
        
        mock_module_instance = self.create_mock_module(self.get_default_params())
        mock_ansible_module.return_value = mock_module_instance
        
        # Run the module
        events.run_module()
        
        # Verify default order is included
        mock_requests_get.assert_called_once()
        call_args = mock_requests_get.call_args
        self.assertIn('params', call_args.kwargs)
        self.assertEqual(call_args.kwargs['params']['order'], 'ascending')

    @patch('events.apitoken.GetToken')
    @patch('events.requests.get')
    @patch('events.AnsibleModule')
    def test_none_values_excluded_from_params(self, mock_ansible_module, mock_requests_get, mock_get_token):
        """Test that None values are excluded from query parameters"""
        # Setup mocks
        mock_get_token.return_value = self.mock_api_token
        
        mock_response = MagicMock()
        mock_response.ok = True
        mock_response.json.return_value = []
        mock_requests_get.return_value = mock_response
        
        params = self.get_default_params()
        params.update({
            'cluster_id': None,  # Should be excluded
            'limit': None,  # Should be excluded
            'severities': None,  # Should be excluded
        })
        mock_module_instance = self.create_mock_module(params)
        mock_ansible_module.return_value = mock_module_instance
        
        # Run the module
        events.run_module()
        
        # Verify None values are excluded, but defaults are included
        mock_requests_get.assert_called_once()
        call_args = mock_requests_get.call_args
        params_passed = call_args.kwargs['params']
        self.assertNotIn('cluster_id', params_passed)
        self.assertNotIn('limit', params_passed)
        self.assertNotIn('severities', params_passed)
        # But defaults should be present
        self.assertEqual(params_passed['offset'], 0)
        self.assertEqual(params_passed['order'], 'ascending')


if __name__ == '__main__':
    unittest.main()
