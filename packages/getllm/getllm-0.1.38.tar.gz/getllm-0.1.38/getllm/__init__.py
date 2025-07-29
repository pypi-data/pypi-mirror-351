#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
getLLM: A package for managing LLM models with Ollama integration.

This package provides functionality for managing, installing, and configuring
LLM models for use with the Ollama API.
"""

from .models import (
    get_models, 
    get_default_model, 
    set_default_model, 
    install_model,
    list_installed_models,
    update_models_from_ollama,
    ModelManager
)

from .ollama_integration import (
    OllamaIntegration,
    get_ollama_integration,
    start_ollama_server,
    install_ollama_model,
    list_ollama_models
)

__all__ = [
    # Model management
    'get_models',
    'get_default_model',
    'set_default_model',
    'install_model',
    'list_installed_models',
    'update_models_from_ollama',
    'ModelManager',
    
    # Ollama integration
    'OllamaIntegration',
    'get_ollama_integration',
    'start_ollama_server',
    'install_ollama_model',
    'list_ollama_models'
]

__version__ = '0.1.33'
