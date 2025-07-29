#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
getLLM: A package for managing LLM models with Ollama and Hugging Face integration.

This package provides functionality for managing, installing, and configuring
LLM models from various sources including Ollama and Hugging Face.
"""

from .models import ModelManager, ModelMetadataManager
from .models.huggingface import HuggingFaceModelManager
from .models.ollama import OllamaModelManager
from .utils import (
    get_models_dir,
    get_default_model,
    set_default_model,
    get_models_metadata_path,
    get_central_env_path
)

# For backward compatibility
from .ollama_integration import (
    OllamaIntegration,
    get_ollama_integration,
    start_ollama_server,
    install_ollama_model,
    list_ollama_models
)

__version__ = '0.2.0'

__all__ = [
    # Main classes
    'ModelManager',
    'HuggingFaceModelManager',
    'OllamaModelManager',
    'ModelMetadataManager',
    
    # Utility functions
    'get_models_dir',
    'get_default_model',
    'set_default_model',
    'get_models_metadata_path',
    'get_central_env_path',
    
    # Ollama integration (legacy)
    'OllamaIntegration',
    'get_ollama_integration',
    'start_ollama_server',
    'install_ollama_model',
    'list_ollama_models'
]
