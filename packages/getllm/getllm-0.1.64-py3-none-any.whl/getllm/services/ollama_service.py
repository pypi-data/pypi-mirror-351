"""
Service for interacting with Ollama models.
"""
import json
import subprocess
from pathlib import Path
from typing import List, Dict, Optional, Any

from ..utils.config import get_models_dir


class OllamaService:
    """Service for interacting with Ollama models."""
    
    def __init__(self):
        self.models_dir = get_models_dir()
        self.cache_file = self.models_dir / "ollama_models.json"
        
        # Ensure the models directory exists
        self.models_dir.mkdir(parents=True, exist_ok=True)
    
    def list_models(self) -> List[Dict]:
        """List all available Ollama models.
        
        Returns:
            List of dictionaries containing model information.
        """
        # First try to load from cache
        cached_models = self._load_cached_models()
        if cached_models:
            return cached_models
            
        # If no cache, try to fetch from Ollama
        models = self._fetch_models_from_ollama()
        if models:
            self._save_models_to_cache(models)
            return models
            
        return []
    
    def get_model_info(self, model_name: str) -> Optional[Dict]:
        """Get information about a specific Ollama model.
        
        Args:
            model_name: The name of the model to get information about.
            
        Returns:
            Dictionary containing model information, or None if not found.
        """
        try:
            result = subprocess.run(
                ["ollama", "show", "--json", model_name],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                return json.loads(result.stdout)
                
            # If the model is not found locally, try to find it in the cache
            models = self._load_cached_models()
            for model in models:
                if model.get('name') == model_name:
                    return model
                    
            return None
            
        except (subprocess.SubprocessError, json.JSONDecodeError):
            return None
    
    def pull_model(self, model_name: str) -> bool:
        """Pull a model from the Ollama library.
        
        Args:
            model_name: The name of the model to pull.
            
        Returns:
            True if the pull was successful, False otherwise.
        """
        try:
            result = subprocess.run(
                ["ollama", "pull", model_name],
                capture_output=True,
                text=True
            )
            return result.returncode == 0
            
        except subprocess.SubprocessError:
            return False
    
    def list_installed_models(self) -> List[str]:
        """List all installed Ollama models.
        
        Returns:
            List of installed model names.
        """
        try:
            result = subprocess.run(
                ["ollama", "list", "--json"],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                models = json.loads(result.stdout)
                return [model.get('name') for model in models if 'name' in model]
                
            return []
            
        except (subprocess.SubprocessError, json.JSONDecodeError):
            return []
    
    def update_models_cache(self) -> bool:
        """Update the local cache of Ollama models.
        
        Returns:
            True if successful, False otherwise.
        """
        models = self._fetch_models_from_ollama()
        if models:
            return self._save_models_to_cache(models)
        return False
    
    def _fetch_models_from_ollama(self) -> List[Dict]:
        """Fetch models from the Ollama library.
        
        Returns:
            List of model dictionaries.
        """
        try:
            # First, get the list of installed models
            installed_models = {}
            result = subprocess.run(
                ["ollama", "list", "--json"],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                installed = json.loads(result.stdout)
                for model in installed:
                    if 'name' in model:
                        installed_models[model['name']] = model
            
            # Get all available models from the library
            result = subprocess.run(
                ["ollama", "list", "--all", "--json"],
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                return []
                
            models = json.loads(result.stdout)
            
            # Mark which models are installed
            for model in models:
                if 'name' in model and model['name'] in installed_models:
                    model['installed'] = True
                    # Merge with installed model data
                    model.update(installed_models[model['name']])
                else:
                    model['installed'] = False
            
            return models
            
        except (subprocess.SubprocessError, json.JSONDecodeError):
            return []
    
    def _load_cached_models(self) -> List[Dict]:
        """Load models from the cache file.
        
        Returns:
            List of model dictionaries, or empty list if cache doesn't exist or is invalid.
        """
        if not self.cache_file.exists():
            return []
            
        try:
            with open(self.cache_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return []
    
    def _save_models_to_cache(self, models: List[Dict]) -> bool:
        """Save models to the cache file.
        
        Args:
            models: List of model dictionaries to save.
            
        Returns:
            True if successful, False otherwise.
        """
        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(models, f, indent=2, ensure_ascii=False)
            return True
        except IOError:
            return False
