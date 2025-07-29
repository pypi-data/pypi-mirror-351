"""
Ollama model manager for handling Ollama models.
"""
import json
import os
from pathlib import Path
from typing import List, Dict, Optional, Any
import subprocess

from .base import BaseModelManager
from ..utils.config import get_models_dir, get_models_metadata_path


class OllamaModelManager(BaseModelManager):
    """Manages Ollama models."""
    
    DEFAULT_MODELS = [
        {
            'name': 'llama3',
            'size': '8B',
            'description': 'Meta\'s Llama 3 8B model',
            'source': 'ollama',
            'format': 'gguf'
        },
        # Add more default models as needed
    ]
    
    def __init__(self):
        self.models_dir = get_models_dir()
        self.cache_file = self.models_dir / "ollama_models.json"
        self.models_metadata_file = get_models_metadata_path()
    
    def get_available_models(self) -> List[Dict]:
        """Get available Ollama models."""
        # First try to load from cache
        cached_models = self._load_cached_models()
        if cached_models:
            return cached_models
        
        # Fall back to default models if cache is empty
        return self.DEFAULT_MODELS
    
    def install_model(self, model_name: str) -> bool:
        """Install an Ollama model."""
        try:
            result = subprocess.run(
                ["ollama", "pull", model_name],
                capture_output=True,
                text=True
            )
            return result.returncode == 0
        except (subprocess.SubprocessError, FileNotFoundError):
            return False
    
    def list_installed_models(self) -> List[str]:
        """List installed Ollama models."""
        try:
            result = subprocess.run(
                ["ollama", "list"],
                capture_output=True,
                text=True
            )
            if result.returncode != 0:
                return []
                
            # Parse the output to get model names
            lines = result.stdout.strip().split('\n')[1:]  # Skip header
            return [line.split()[0] for line in lines if line.strip()]
            
        except (subprocess.SubprocessError, FileNotFoundError):
            return []
    
    def update_models_cache(self) -> bool:
        """Update the local cache of Ollama models."""
        try:
            result = subprocess.run(
                ["ollama", "list", "--json"],
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                return False
                
            models = json.loads(result.stdout)
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(models, f, indent=2)
                
            return True
            
        except (subprocess.SubprocessError, json.JSONDecodeError, IOError):
            return False
    
    def _load_cached_models(self) -> List[Dict]:
        """Load models from the cache file."""
        if not self.cache_file.exists():
            return []
        
        try:
            with open(self.cache_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return []
    
    def get_model_info(self, model_name: str) -> Optional[Dict]:
        """Get information about a specific model."""
        models = self.get_available_models()
        for model in models:
            if model.get('name') == model_name:
                return model
        return None
