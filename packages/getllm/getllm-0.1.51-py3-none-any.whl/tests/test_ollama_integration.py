"""
Tests for the getllm.ollama_integration module
"""
import unittest
import os
import sys
import tempfile
import platform
from unittest.mock import patch, MagicMock, mock_open, call

# Add the parent directory to the path so we can import getllm
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

class TestOllamaIntegration(unittest.TestCase):
    """Tests for the getllm.ollama_integration module"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Import the ollama_integration module
        from getllm.ollama_integration import OllamaIntegration
        self.OllamaIntegration = OllamaIntegration
    
    @patch('getllm.ollama_integration.requests.get')
    def test_check_server_running(self, mock_get):
        """Test that the check_server_running method works"""
        # Mock the requests.get method to return a response with status_code 200
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"version": "0.1.0"}
        mock_get.return_value = mock_response
        
        # Create an instance of OllamaIntegration
        ollama = self.OllamaIntegration()
        
        # Call the check_server_running method
        result = ollama.check_server_running()
        
        # Verify that the method returns True
        self.assertTrue(result)
        
        # Verify that requests.get was called with the correct URL
        mock_get.assert_called_once()
    
    @patch('getllm.ollama_integration.requests.get')
    def test_check_server_not_running(self, mock_get):
        """Test that the check_server_running method returns False when server is not running"""
        # Mock the requests.get method to raise an exception
        mock_get.side_effect = Exception("Connection refused")
        
        # Create an instance of OllamaIntegration
        ollama = self.OllamaIntegration()
        
        # Call the check_server_running method
        result = ollama.check_server_running()
        
        # Verify that the method returns False
        self.assertFalse(result)
    
    @patch('getllm.ollama_integration.os.path.isfile')
    @patch('getllm.ollama_integration.os.access')
    def test_check_ollama_installed(self, mock_access, mock_isfile):
        """Test that the _check_ollama_installed method works when Ollama is installed"""
        # Mock the os.path.isfile and os.access methods to return True
        mock_isfile.return_value = True
        mock_access.return_value = True
        
        # Create an instance of OllamaIntegration
        ollama = self.OllamaIntegration()
        
        # Verify that is_ollama_installed is True
        self.assertTrue(ollama.is_ollama_installed)
    
    @patch('getllm.ollama_integration.os.path.isfile')
    @patch('getllm.ollama_integration.subprocess.run')
    def test_check_ollama_not_installed(self, mock_run, mock_isfile):
        """Test that the _check_ollama_installed method works when Ollama is not installed"""
        # Mock the os.path.isfile method to return False
        mock_isfile.return_value = False
        
        # Mock the subprocess.run method to return a failed result
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_run.return_value = mock_result
        
        # Create a new instance of OllamaIntegration to force _check_ollama_installed to run
        from getllm.ollama_integration import OllamaIntegration
        ollama = OllamaIntegration()
        
        # Verify that is_ollama_installed is False
        self.assertFalse(ollama.is_ollama_installed)
    
    @patch('getllm.ollama_integration.subprocess.run')
    @patch('getllm.ollama_integration.platform.system')
    @patch('builtins.print')
    def test_install_ollama_direct_success(self, mock_print, mock_platform, mock_run):
        """Test that the _install_ollama_direct method works when installation succeeds"""
        # Mock the platform.system method to return "Linux"
        mock_platform.return_value = "Linux"
        
        # Mock the subprocess.run method to return a successful result
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_run.return_value = mock_result
        
        # Create an instance of OllamaIntegration and patch the _check_ollama_installed method
        ollama = self.OllamaIntegration()
        ollama._check_ollama_installed = MagicMock(return_value=True)
        
        # Call the _install_ollama_direct method
        result = ollama._install_ollama_direct()
        
        # Verify that the method returns True
        self.assertTrue(result)
        
        # Verify that subprocess.run was called with the correct command
        mock_run.assert_called_once()
        self.assertIn("curl -fsSL https://ollama.com/install.sh | sh", mock_run.call_args[0][0])
    
    @patch('getllm.ollama_integration.subprocess.run')
    @patch('getllm.ollama_integration.platform.system')
    @patch('builtins.print')
    def test_install_ollama_direct_failure(self, mock_print, mock_platform, mock_run):
        """Test that the _install_ollama_direct method works when installation fails"""
        # Mock the platform.system method to return "Linux"
        mock_platform.return_value = "Linux"
        
        # Mock the subprocess.run method to return a failed result
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stderr = "Installation failed"
        mock_run.return_value = mock_result
        
        # Create an instance of OllamaIntegration
        ollama = self.OllamaIntegration()
        
        # Call the _install_ollama_direct method
        result = ollama._install_ollama_direct()
        
        # Verify that the method returns False
        self.assertFalse(result)
    
    @patch('getllm.ollama_integration.subprocess.run')
    @patch('getllm.ollama_integration.time.sleep')
    @patch('builtins.print')
    def test_install_ollama_docker_success(self, mock_print, mock_sleep, mock_run):
        """Test that the _install_ollama_docker method works when installation succeeds"""
        # Mock the subprocess.run method to return successful results for all calls
        mock_results = [
            MagicMock(returncode=0, stdout="Docker version 20.10.12"),  # docker --version
            MagicMock(returncode=0),  # docker pull
            MagicMock(returncode=0, stdout=""),  # docker ps -q -f name=ollama
            MagicMock(returncode=0, stdout=""),  # docker ps -a -q -f name=ollama
            MagicMock(returncode=0)  # docker run
        ]
        mock_run.side_effect = mock_results
        
        # Create an instance of OllamaIntegration and patch the check_server_running method
        ollama = self.OllamaIntegration()
        ollama.check_server_running = MagicMock(return_value=True)
        
        # Call the _install_ollama_docker method
        result = ollama._install_ollama_docker()
        
        # Verify that the method returns True
        self.assertTrue(result)
        
        # Verify that subprocess.run was called with the correct commands
        self.assertEqual(mock_run.call_count, 5)
        self.assertIn("docker", mock_run.call_args_list[0][0][0][0])
        self.assertIn("pull", mock_run.call_args_list[1][0][0][1])
    
    @patch('getllm.ollama_integration.os.path.isdir')
    @patch('getllm.ollama_integration.os.path.join')
    @patch('getllm.ollama_integration.subprocess.run')
    @patch('builtins.open', new_callable=mock_open)
    @patch('builtins.print')
    def test_install_ollama_bexy_success(self, mock_print, mock_file, mock_run, mock_join, mock_isdir):
        """Test that the _install_ollama_bexy method works when installation succeeds"""
        # Mock the os.path.isdir method to return True
        mock_isdir.return_value = True
        
        # Mock the os.path.join method to return a valid path
        mock_join.return_value = "/path/to/bexy"
        
        # Mock the subprocess.run method to return successful results for all calls
        mock_results = [
            MagicMock(returncode=0),  # venv creation
            MagicMock(returncode=0),  # pip install
            MagicMock(returncode=0)   # run sandbox script
        ]
        mock_run.side_effect = mock_results
        
        # Create an instance of OllamaIntegration and patch the check_server_running method
        from getllm.ollama_integration import OllamaIntegration
        ollama = OllamaIntegration()
        ollama.check_server_running = MagicMock(return_value=True)
        
        # Call the _install_ollama_bexy method
        result = ollama._install_ollama_bexy()
        
        # Verify that the method returns True
        self.assertTrue(result)
        
        # Verify that the file was opened for writing the sandbox script
        mock_file.assert_called_once()
        
        # Verify that subprocess.run was called
        self.assertTrue(mock_run.called)
    
    @patch('builtins.print')
    def test_install_ollama_with_bexy(self, mock_print):
        """Test that the _install_ollama method works when user selects bexy sandbox"""
        # Import the necessary modules
        from getllm.ollama_integration import OllamaIntegration
        
        # Create an instance of OllamaIntegration and patch the necessary methods
        ollama = OllamaIntegration()
        
        # Mock the input function to return 'bexy'
        with patch('builtins.input', return_value='3'):
            # Mock the _install_ollama_bexy method
            with patch.object(ollama, '_install_ollama_bexy', return_value=True):
                # Call the _install_ollama method
                result = ollama._install_ollama()
                
                # Verify that the method returns True
                self.assertTrue(result)

if __name__ == "__main__":
    unittest.main()
