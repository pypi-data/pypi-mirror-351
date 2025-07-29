#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test the Ollama integration in the pyllm package.

These tests verify that the Ollama integration functions work correctly.
"""

import os
import sys
import unittest
from unittest.mock import patch, MagicMock

# Add the parent directory to the path so we can import pyllm
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from pyllm import (
    get_ollama_integration,
    start_ollama_server,
    install_ollama_model,
    list_ollama_models,
    OllamaIntegration
)


class TestOllamaIntegration(unittest.TestCase):
    """Test the Ollama integration functionality."""

    @patch('pyllm.ollama_integration.requests.get')
    def test_start_ollama_server_already_running(self, mock_get):
        """Test starting the Ollama server when it's already running."""
        # Mock the response from the Ollama API
        mock_response = MagicMock()
        mock_response.json.return_value = {'version': 'test-version'}
        mock_get.return_value = mock_response

        # Create an OllamaIntegration instance and start the server
        ollama = get_ollama_integration()
        ollama.start_ollama()

        # Verify that the API was called
        mock_get.assert_called_once_with(ollama.version_api_url)

    @patch('pyllm.ollama_integration.requests.get')
    def test_check_model_availability_model_available(self, mock_get):
        """Test checking model availability when the model is available."""
        # Mock the response from the Ollama API
        mock_response = MagicMock()
        mock_response.json.return_value = {'models': [{'name': 'codellama:7b'}]}
        mock_get.return_value = mock_response

        # Create an OllamaIntegration instance with a specific model
        ollama = get_ollama_integration(model='codellama:7b')

        # Check if the model is available
        result = ollama.check_model_availability()

        # Verify that the API was called and the result is True
        mock_get.assert_called_once_with(ollama.list_api_url, timeout=10)
        self.assertTrue(result)

    @patch('pyllm.ollama_integration.requests.get')
    def test_check_model_availability_model_not_available(self, mock_get):
        """Test checking model availability when the model is not available."""
        # Mock the response from the Ollama API
        mock_response = MagicMock()
        mock_response.json.return_value = {'models': [{'name': 'llama:7b'}]}
        mock_get.return_value = mock_response

        # Create an OllamaIntegration instance with a specific model
        ollama = get_ollama_integration(model='codellama:7b')

        # Set auto-install and auto-select to False for this test
        with patch.dict('os.environ', {'OLLAMA_AUTO_INSTALL_MODEL': 'false', 'OLLAMA_AUTO_SELECT_MODEL': 'false'}):
            # Check if the model is available
            result = ollama.check_model_availability()

            # Verify that the API was called and the result is False
            mock_get.assert_called_once_with(ollama.list_api_url, timeout=10)
            self.assertFalse(result)

    @patch('pyllm.ollama_integration.subprocess.run')
    def test_install_model(self, mock_run):
        """Test installing a model."""
        # Mock the subprocess.run function
        mock_run.return_value = MagicMock(returncode=0)

        # Create an OllamaIntegration instance
        ollama = get_ollama_integration()

        # Install a model
        result = ollama.install_model('codellama:7b')

        # Verify that subprocess.run was called with the correct arguments
        mock_run.assert_called_once()
        self.assertEqual(mock_run.call_args[0][0][0], ollama.ollama_path)
        self.assertEqual(mock_run.call_args[0][0][1], 'pull')
        self.assertEqual(mock_run.call_args[0][0][2], 'codellama:7b')
        self.assertTrue(result)

    @patch('pyllm.ollama_integration.requests.get')
    def test_list_installed_models(self, mock_get):
        """Test listing installed models."""
        # Mock the response from the Ollama API
        mock_response = MagicMock()
        mock_response.json.return_value = {'models': [
            {'name': 'codellama:7b'},
            {'name': 'llama:7b'}
        ]}
        mock_get.return_value = mock_response

        # Create an OllamaIntegration instance
        ollama = get_ollama_integration()

        # List installed models
        models = ollama.list_installed_models()

        # Verify that the API was called and the result is correct
        mock_get.assert_called_once_with(ollama.list_api_url, timeout=10)
        self.assertEqual(len(models), 2)
        self.assertEqual(models[0]['name'], 'codellama:7b')
        self.assertEqual(models[1]['name'], 'llama:7b')


if __name__ == '__main__':
    unittest.main()
