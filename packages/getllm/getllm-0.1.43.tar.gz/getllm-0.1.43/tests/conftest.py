"""
Pytest fixtures for getllm tests
"""
import pytest
import os
import sys

# Add the parent directory to the path so we can import getllm
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

@pytest.fixture
def mock_env_vars(monkeypatch):
    """Fixture to set up environment variables for tests"""
    monkeypatch.setenv("OLLAMA_PATH", "/usr/local/bin/ollama")
    monkeypatch.setenv("OLLAMA_MODEL", "llama2")
    monkeypatch.setenv("OLLAMA_FALLBACK_MODELS", "llama2,codellama")
    monkeypatch.setenv("OLLAMA_TIMEOUT", "120")
    
    return {
        "OLLAMA_PATH": "/usr/local/bin/ollama",
        "OLLAMA_MODEL": "llama2",
        "OLLAMA_FALLBACK_MODELS": "llama2,codellama",
        "OLLAMA_TIMEOUT": "120"
    }

@pytest.fixture
def mock_ollama_response():
    """Fixture to provide a mock response from the Ollama API"""
    return {
        "model": "llama2",
        "created_at": "2023-01-01T00:00:00Z",
        "response": "This is a mock response from the Ollama API."
    }
