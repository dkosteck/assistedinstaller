#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unit tests for infra_envs module

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
    import infra_envs
except ImportError:
    infra_envs = None


class TestInfraEnvsModule(BaseModuleTest, ModuleTestMixin):
    """Test cases for infra_envs module"""

    def setUp(self):
        """Set up test fixtures"""
        super().setUp()
        if infra_envs is None:
            self.skipTest("infra_envs module not available")
        
        self.module_class = infra_envs
        self.default_params = {
            'state': None,
            'name': None,
            'pull_secret': None,
        }

    def get_default_params(self):
        return self.default_params.copy()

    @patch('infra_envs.apitoken.GetToken')
    @patch('infra_envs.requests.post')
    @patch('infra_envs.AnsibleModule')
    def test_create_infra_env_success(self, mock_ansible_module, mock_requests_post, mock_get_token):
        """Test successful infra-env creation"""
        # Setup mocks
        mock_get_token.return_value = self.mock_api_token
        
        mock_response = MagicMock()
        mock_response.ok = True
        mock_response.json.return_value = {
            "cpu_architecture": "x86_64",
            "created_at": "2025-02-28T15:39:40.008442Z",
            "download_url": "https://api.openshift.com/api/assisted-images/bytoken/tokenval/4.19/x86_64/minimal.iso",
            "id": "7d4618af-d367-4c47-ab3f-49e0822a4cf7",
            "name": "testinfra",
            "openshift_version": "4.19",
            "pull_secret_set": True,
            "type": "minimal-iso"
        }
        mock_requests_post.return_value = mock_response
        
        params = self.get_default_params()
        params.update({
            'state': 'present',
            'name': 'testinfra',
            'pull_secret': 'test-pull-secret'
        })
        mock_module_instance = self.create_mock_module(params)
        mock_ansible_module.return_value = mock_module_instance
        
        # Run the module
        infra_envs.run_module()
        
        # Verify API call was made correctly
        mock_requests_post.assert_called_once()
        call_args = mock_requests_post.call_args
        self.assertIn('infra-envs', call_args[0][0])
        self.assertIn('headers', call_args.kwargs)
        self.assertEqual(call_args.kwargs['headers']['Authorization'], f'Bearer {self.mock_api_token}')
        
        # Verify request body
        self.assertIn('json', call_args.kwargs)
        request_data = call_args.kwargs['json']
        self.assertEqual(request_data['name'], 'testinfra')
        self.assertEqual(request_data['pull_secret'], 'test-pull-secret')
        self.assertNotIn('state', request_data)  # Should be removed
        
        # Verify successful exit
        self.assert_exit_json_called_with_success(mock_module_instance, 'infra_envs')

    @patch('infra_envs.apitoken.GetToken')
    @patch('infra_envs.requests.post')
    @patch('infra_envs.AnsibleModule')
    def test_create_infra_env_api_error(self, mock_ansible_module, mock_requests_post, mock_get_token):
        """Test infra-env creation API error handling"""
        # Setup mocks
        mock_get_token.return_value = self.mock_api_token
        
        mock_response = MagicMock()
        mock_response.ok = False
        mock_response.text = "Bad Request: Invalid pull secret"
        mock_requests_post.return_value = mock_response
        
        params = self.get_default_params()
        params.update({
            'state': 'present',
            'name': 'testinfra',
            'pull_secret': 'invalid-secret'
        })
        mock_module_instance = self.create_mock_module(params)
        mock_ansible_module.return_value = mock_module_instance
        
        # Run the module
        infra_envs.run_module()
        
        # Verify error handling
        self.assert_fail_json_called_with_error(mock_module_instance, "Error creating infra-envs")

    @patch('infra_envs.HAS_REQUESTS', False)
    @patch('infra_envs.AnsibleModule')
    def test_missing_requests_library(self, mock_ansible_module):
        """Test handling of missing requests library"""
        mock_module_instance = self.create_mock_module(self.get_default_params())
        mock_ansible_module.return_value = mock_module_instance
        
        # Run the module
        infra_envs.run_module()
        
        # Verify error handling
        self.assert_fail_json_called_with_error(mock_module_instance, "requests")

    def test_remove_module_fields(self):
        """Test the remove_module_fields utility function"""
        mock_module = MagicMock()
        mock_module.params = {
            'state': 'present',
            'name': 'test-infra',
            'pull_secret': 'test-secret'
        }
        
        result = infra_envs.remove_module_fields(mock_module)
        
        # Verify state field is removed
        self.assertNotIn('state', result)
        
        # Verify other fields are kept
        self.assertIn('name', result)
        self.assertIn('pull_secret', result)
        self.assertEqual(result['name'], 'test-infra')
        self.assertEqual(result['pull_secret'], 'test-secret')

    @patch('infra_envs.AnsibleModule')
    def test_required_if_validation(self, mock_ansible_module):
        """Test that AnsibleModule is configured with correct required_if rules"""
        # Setup mock
        mock_module_instance = self.create_mock_module(self.get_default_params())
        mock_ansible_module.return_value = mock_module_instance
        
        # Import and inspect the module args
        from infra_envs import run_module
        
        # This will call AnsibleModule constructor
        try:
            run_module()
        except:
            pass  # We expect this to fail due to missing dependencies
        
        # Verify AnsibleModule was called with required_if
        mock_ansible_module.assert_called_once()
        call_args = mock_ansible_module.call_args
        self.assertIn('required_if', call_args.kwargs)
        
        # Verify the required_if rules
        required_if = call_args.kwargs['required_if']
        self.assertIn(("state", "present", ["name", "pull_secret"]), required_if)

    @patch('infra_envs.apitoken.GetToken')
    @patch('infra_envs.AnsibleModule')
    def test_no_state_parameter_handling(self, mock_ansible_module, mock_get_token):
        """Test handling when state parameter is None (should not perform any action)"""
        # Setup mocks
        mock_get_token.return_value = self.mock_api_token
        
        # Note: The current implementation has a bug - it only handles 'present' state
        # but doesn't handle the case where state is None properly.
        # This test documents the current behavior.
        
        mock_module_instance = self.create_mock_module(self.get_default_params())
        mock_ansible_module.return_value = mock_module_instance
        
        # This should raise an exception because result is not defined
        # when state is not 'present'
        with self.assertRaises(UnboundLocalError):
            infra_envs.run_module()

    @patch('infra_envs.apitoken.GetToken')
    @patch('infra_envs.requests.post')
    @patch('infra_envs.AnsibleModule')
    def test_pull_secret_marked_no_log(self, mock_ansible_module, mock_requests_post, mock_get_token):
        """Test that pull_secret parameter is marked as no_log"""
        # Setup mocks
        mock_get_token.return_value = self.mock_api_token
        mock_response = MagicMock()
        mock_response.ok = True
        mock_response.json.return_value = {"id": "test"}
        mock_requests_post.return_value = mock_response
        
        mock_module_instance = self.create_mock_module(self.get_default_params())
        mock_ansible_module.return_value = mock_module_instance
        
        # Import and inspect the module args
        from infra_envs import run_module
        
        try:
            run_module()
        except:
            pass
        
        # Verify AnsibleModule was called with no_log for pull_secret
        mock_ansible_module.assert_called_once()
        call_args = mock_ansible_module.call_args
        argument_spec = call_args.kwargs['argument_spec']
        
        # Check that pull_secret has no_log=True
        self.assertIn('pull_secret', argument_spec)
        pull_secret_spec = argument_spec['pull_secret']
        self.assertTrue(pull_secret_spec.get('no_log', False))

    @patch('infra_envs.apitoken.GetToken')
    @patch('infra_envs.requests.post')
    @patch('infra_envs.AnsibleModule')
    def test_api_headers_content_type(self, mock_ansible_module, mock_requests_post, mock_get_token):
        """Test that API requests include correct Content-Type header"""
        # Setup mocks
        mock_get_token.return_value = self.mock_api_token
        mock_response = MagicMock()
        mock_response.ok = True
        mock_response.json.return_value = {"id": "test"}
        mock_requests_post.return_value = mock_response
        
        params = self.get_default_params()
        params.update({
            'state': 'present',
            'name': 'testinfra',
            'pull_secret': 'test-secret'
        })
        mock_module_instance = self.create_mock_module(params)
        mock_ansible_module.return_value = mock_module_instance
        
        # Run the module
        infra_envs.run_module()
        
        # Verify headers
        mock_requests_post.assert_called_once()
        call_args = mock_requests_post.call_args
        headers = call_args.kwargs['headers']
        self.assertEqual(headers['Content-Type'], 'application/json')


if __name__ == '__main__':
    unittest.main()
