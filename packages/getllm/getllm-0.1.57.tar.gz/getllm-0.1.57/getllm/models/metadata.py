"""
Model metadata manager for handling model metadata operations.
"""
import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Any

from ..utils.config import get_models_metadata_path, get_models_dir


class ModelMetadataManager:
    """Manages model metadata operations."""
    
    def __init__(self):
        self.metadata_file = get_models_metadata_path()
        self.models_dir = get_models_dir()
        
        # Ensure the models directory exists
        self.models_dir.mkdir(parents=True, exist_ok=True)
    
    def get_metadata(self, model_name: str) -> Optional[Dict[str, Any]]:
        """Get metadata for a specific model.
        
        Args:
            model_name: Name of the model to get metadata for.
            
        Returns:
            Dictionary containing model metadata, or None if not found.
        """
        metadata = self._load_metadata()
        return metadata.get(model_name)
    
    def update_metadata(self, model_name: str, data: Dict[str, Any]) -> bool:
        """Update metadata for a model.
        
        Args:
            model_name: Name of the model to update.
            data: Dictionary containing metadata to update.
            
        Returns:
            True if successful, False otherwise.
        """
        metadata = self._load_metadata()
        
        if model_name not in metadata:
            metadata[model_name] = {}
            
        metadata[model_name].update(data)
        
        return self._save_metadata(metadata)
    
    def remove_metadata(self, model_name: str) -> bool:
        """Remove metadata for a model.
        
        Args:
            model_name: Name of the model to remove.
            
        Returns:
            True if successful, False otherwise.
        """
        metadata = self._load_metadata()
        
        if model_name in metadata:
            del metadata[model_name]
            return self._save_metadata(metadata)
            
        return True
    
    def list_models(self) -> List[str]:
        """List all models with metadata.
        
        Returns:
            List of model names that have metadata.
        """
        metadata = self._load_metadata()
        return list(metadata.keys())
    
    def _load_metadata(self) -> Dict[str, Dict[str, Any]]:
        """Load metadata from the metadata file.
        
        Returns:
            Dictionary containing all metadata.
        """
        if not self.metadata_file.exists():
            return {}
            
        try:
            with open(self.metadata_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {}
    
    def _save_metadata(self, metadata: Dict[str, Any]) -> bool:
        """Save metadata to the metadata file.
        
        Args:
            metadata: Dictionary containing all metadata to save.
            
        Returns:
            True if successful, False otherwise.
        """
        try:
            # Ensure the directory exists
            self.metadata_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Save with pretty-printing
            with open(self.metadata_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
            return True
        except IOError:
            return False
