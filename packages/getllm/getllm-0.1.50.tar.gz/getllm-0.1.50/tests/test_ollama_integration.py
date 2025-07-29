"""
Tests for the getllm.ollama_integration module
"""
import unittest
import os
import sys
from unittest.mock import patch, MagicMock

# Add the parent directory to the path so we can import getllm
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

class TestOllamaIntegration(unittest.TestCase):
    """Tests for the getllm.ollama_integration module"""
    
    @patch('getllm.ollama_integration.requests.get')
    def test_check_server_running(self, mock_get):
        """Test that the check_server_running method works"""
        # Mock the requests.get method to return a response with status_code 200
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        # Import the ollama_integration module
        from getllm.ollama_integration import OllamaIntegration
        
        # Create an instance of OllamaIntegration
        ollama = OllamaIntegration()
        
        # Call the check_server_running method
        result = ollama.check_server_running()
        
        # Verify that the method returns True
        self.assertTrue(result)
        
        # Verify that requests.get was called with the correct URL
        mock_get.assert_called_once()

if __name__ == "__main__":
    unittest.main()
