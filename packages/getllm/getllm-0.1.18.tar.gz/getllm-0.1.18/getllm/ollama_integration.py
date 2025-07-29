#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ollama Integration for PyLLM

This module provides integration with Ollama for high-quality code generation.
It handles model management, automatic installation, and fallback mechanisms.
"""

import os
import json
import time
import subprocess
import sys
import re
import requests
import platform
import threading
import logging
from typing import List, Dict, Any, Tuple, Optional
from pathlib import Path

# Create .getllm directory if it doesn't exist
PACKAGE_DIR = os.path.join(os.path.expanduser('~'), '.getllm')
os.makedirs(PACKAGE_DIR, exist_ok=True)

# Configure logger for OllamaIntegration
logger = logging.getLogger('getllm.ollama')
logger.setLevel(logging.INFO)

# Create file handler for Ollama-specific logs
ollama_log_file = os.path.join(PACKAGE_DIR, 'getllm_ollama.log')
file_handler = logging.FileHandler(ollama_log_file)
file_formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)

logger.debug('OllamaIntegration initialized')


class ProgressSpinner:
    """A simple progress spinner for console output."""
    def __init__(self, message="Processing", delay=0.1):
        self.message = message
        self.delay = delay
        self.running = False
        self.spinner_thread = None
        self.spinner_chars = ['-', '\\', '|', '/']
        self.counter = 0
        self.start_time = 0
        
    def spin(self):
        while self.running:
            elapsed = time.time() - self.start_time
            sys.stderr.write(f"\r{self.message} {self.spinner_chars[self.counter % len(self.spinner_chars)]} ({elapsed:.1f}s) ")
            sys.stderr.flush()
            time.sleep(self.delay)
            self.counter += 1
        # Clear the line when done
        sys.stderr.write("\r" + " " * (len(self.message) + 20) + "\r")
        sys.stderr.flush()
            
    def start(self):
        self.running = True
        self.start_time = time.time()
        self.spinner_thread = threading.Thread(target=self.spin)
        self.spinner_thread.daemon = True
        self.spinner_thread.start()
        
    def stop(self):
        self.running = False
        if self.spinner_thread:
            self.spinner_thread.join(timeout=1.0)


class OllamaIntegration:
    """Class for integrating with Ollama and managing LLM models."""

    def __init__(self, ollama_path: str = None, model: str = None):
        self.ollama_path = ollama_path or os.getenv('OLLAMA_PATH', 'ollama')
        # Set default model with fallbacks to ensure we use an available model
        self.model = model or os.getenv('OLLAMA_MODEL', 'codellama:7b')
        self.fallback_models = os.getenv('OLLAMA_FALLBACK_MODELS', 'codellama:7b,phi3:latest,tinyllama:latest').split(',')
        self.ollama_process = None
        # Ollama API endpoints
        self.base_api_url = "http://localhost:11434/api"
        self.generate_api_url = f"{self.base_api_url}/generate"
        self.chat_api_url = f"{self.base_api_url}/chat"
        self.version_api_url = f"{self.base_api_url}/version"
        self.list_api_url = f"{self.base_api_url}/tags"
        # Track the last error that occurred
        self.last_error = None
        self.original_model_specified = model is not None

    def start_ollama(self) -> None:
        """Start the Ollama server if it's not already running."""
        try:
            # Check if Ollama is already running by querying the version
            response = requests.get(self.version_api_url)
            logger.info(f"Ollama is running (version: {response.json().get('version', 'unknown')})")
            return

        except requests.exceptions.ConnectionError:
            logger.info("Starting Ollama server...")
            # Run Ollama in the background
            self.ollama_process = subprocess.Popen(
                [self.ollama_path, "serve"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            # Wait for the server to start
            time.sleep(5)

            # Check if the server actually started
            try:
                response = requests.get(self.version_api_url)
                logger.info(f"Ollama server started (version: {response.json().get('version', 'unknown')})")
            except requests.exceptions.ConnectionError:
                logger.error("ERROR: Failed to start Ollama server.")
                if self.ollama_process:
                    logger.error("Error details:")
                    out, err = self.ollama_process.communicate(timeout=1)
                    logger.error(f"STDOUT: {out.decode('utf-8', errors='ignore')}")
                    logger.error(f"STDERR: {err.decode('utf-8', errors='ignore')}")
                raise RuntimeError("Failed to start Ollama server")

    def stop_ollama(self) -> None:
        """Stop the Ollama server if it was started by this script."""
        if self.ollama_process:
            logger.info("Stopping Ollama server...")
            self.ollama_process.terminate()
            self.ollama_process.wait()
            logger.info("Ollama server stopped")

    def check_model_availability(self) -> bool:
        """
        Check if the selected model is available in Ollama.
        Returns True if the model is available, False otherwise.
        If the model is not available but auto-install is enabled, attempts to install it.
        """
        try:
            # Get list of available models from Ollama
            response = requests.get(self.list_api_url, timeout=10)
            response.raise_for_status()
            available_models = [tag['name'] for tag in response.json().get('models', [])]
            
            # If the model is available, return True
            if self.model in available_models:
                return True
                
            # Special handling for SpeakLeash/Bielik models - check if already installed with a different name
            if self.model.lower().startswith('speakleash/bielik'):
                for model in available_models:
                    if model.startswith('bielik-custom-'):
                        logger.info(f"Found existing Bielik model installation: {model}")
                        print(f"\nFound existing Bielik model installation: {model}")
                        print(f"Using existing model instead of downloading again.")
                        self.model = model
                        
                        # Increase timeout for Bielik models as they tend to be larger
                        current_timeout = int(os.getenv('OLLAMA_TIMEOUT', '30'))
                        if current_timeout < 120:
                            os.environ['OLLAMA_TIMEOUT'] = '120'
                            print(f"Increased API timeout to 120 seconds for Bielik model.")
                        
                        return True
                
            # Log available models for debugging
            logger.warning(f"Model {self.model} not found in Ollama. Available models: {available_models}")
            
            # If user explicitly specified a model and it's not available, try to install it
            if self.original_model_specified:
                # Check if we should try to automatically install the model
                auto_install = os.getenv('OLLAMA_AUTO_INSTALL_MODEL', 'True').lower() in ('true', '1', 't')
                if auto_install:
                    print(f"\nModel {self.model} not found. Attempting to install it...")
                    if self.install_model(self.model):
                        return True
                
                # Check if we should try to automatically use an available model
                if os.getenv('OLLAMA_AUTO_SELECT_MODEL', 'True').lower() in ('true', '1', 't'):
                    # Try to find a suitable model from the available ones
                    for model in available_models:
                        if 'code' in model.lower() or 'llama' in model.lower() or 'phi' in model.lower():
                            logger.info(f"Automatically selecting available model: {model} instead of {self.model}")
                            self.model = model
                            return True
                    # If no suitable model found, use the first available one
                    if available_models:
                        logger.info(f"Automatically selecting first available model: {available_models[0]} instead of {self.model}")
                        self.model = available_models[0]
                        return True
                else:
                    # Don't use fallbacks if user explicitly specified a model
                    return False
            
            # Try fallback models
            for fallback in self.fallback_models:
                if fallback in available_models:
                    self.model = fallback
                    logger.info(f"Using fallback model: {fallback}")
                    return True
                    
            # If no fallbacks are available, return False
            return False
        except Exception as e:
            logger.warning(f"Could not check model availability: {e}")
            return False  # Assume model is not available if we can't check

    def install_model(self, model_name: str) -> bool:
        """
        Install a model using Ollama's pull command.
        For SpeakLeash models, performs a special installation process.
        
        Args:
            model_name: The name of the model to install
            
        Returns:
            True if installation was successful, False otherwise
        """
        # Check if it's a SpeakLeash model that needs special handling
        if model_name.lower().startswith('speakleash/bielik'):
            print(f"\nDetected SpeakLeash Bielik model: {model_name}")
            print("Starting special installation process...")
            return self._install_speakleash_model(model_name)
        
        # For regular models, use ollama pull
        print(f"\nInstalling model: {model_name}")
        spinner = ProgressSpinner(message=f"Pulling model {model_name}")
        spinner.start()
        
        try:
            # Run ollama pull command
            result = subprocess.run(
                [self.ollama_path, "pull", model_name],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=False
            )
            
            spinner.stop()
            
            if result.returncode == 0:
                print(f"Successfully installed model: {model_name}")
                # Update the current model
                self.model = model_name
                return True
            else:
                print(f"Failed to install model: {model_name}")
                print(f"Error: {result.stderr}")
                return False
                
        except Exception as e:
            spinner.stop()
            print(f"Error installing model: {e}")
            return False
    
    def _install_speakleash_model(self, model_name: str) -> bool:
        """
        Special installation process for SpeakLeash Bielik models.
        
        Args:
            model_name: The name of the SpeakLeash model to install
            
        Returns:
            True if installation was successful, False otherwise
        """
        # Check if a Bielik model is already installed
        try:
            response = requests.get(self.list_api_url, timeout=10)
            response.raise_for_status()
            available_models = [tag['name'] for tag in response.json().get('models', [])]
            
            for model in available_models:
                if model.startswith('bielik-custom-'):
                    logger.info(f"Using existing Bielik model installation: {model}")
                    print(f"\nFound existing Bielik model installation: {model}")
                    print(f"Using existing model instead of downloading again.")
                    
                    # Update the current model
                    self.model = model
                    
                    # Update environment variables for future use
                    os.environ["OLLAMA_MODEL"] = model
                    
                    # Increase timeout for Bielik models as they tend to be larger
                    os.environ["OLLAMA_TIMEOUT"] = "120"
                    print(f"Increased API timeout to 120 seconds for Bielik model.")
                    
                    # Save these settings to .env file if it exists
                    self._update_env_file(model)
                    
                    return True
        except Exception as e:
            logger.warning(f"Could not check for existing Bielik models: {e}")
            # Continue with installation if we can't check for existing models
        
        # Extract the model version from the name
        model_parts = model_name.split('/')
        if len(model_parts) != 2:
            print(f"Invalid model name format: {model_name}")
            return False
        
        model_version = model_parts[1].lower()
        
        # Set up custom model name for Ollama
        custom_model_name = f"bielik-custom-{int(time.time())}"  # Add timestamp to avoid conflicts
        
        # Determine the correct Hugging Face model path and file
        if "1.5b-v3.0" in model_version:
            hf_repo = "speakleash/Bielik-1.5B-v3.0-Instruct-GGUF"
            model_file = "Bielik-1.5B-v3.0-Instruct.Q8_0.gguf"
        elif "4.5b-v3.0" in model_version:
            hf_repo = "speakleash/Bielik-4.5B-v3.0-Instruct-GGUF"
            model_file = "Bielik-4.5B-v3.0-Instruct.Q8_0.gguf"
        elif "11b-v2.3" in model_version:
            hf_repo = "speakleash/Bielik-11B-v2.3-Instruct-GGUF"
            model_file = "Bielik-11B-v2.3-Instruct.Q8_0.gguf"
        else:
            print(f"Unsupported Bielik model version: {model_version}")
            print("Supported versions: 1.5b-v3.0, 4.5b-v3.0, 11b-v2.3")
            return False
        
        # Create a temporary directory for the model
        temp_dir = os.path.join(PACKAGE_DIR, "models", custom_model_name)
        os.makedirs(temp_dir, exist_ok=True)
        
        # Download the model using Hugging Face CLI if available, otherwise use wget
        print(f"\nDownloading {model_name} from Hugging Face...")
        print(f"This may take a while depending on your internet connection.")
        
        model_path = os.path.join(temp_dir, model_file)
        download_url = f"https://huggingface.co/{hf_repo}/resolve/main/{model_file}"
        
        try:
            # First try using huggingface_hub if installed
            try:
                from huggingface_hub import hf_hub_download
                print("Using Hugging Face Hub for download (shows progress)")
                
                hf_hub_download(
                    repo_id=hf_repo,
                    filename=model_file,
                    local_dir=temp_dir,
                    local_dir_use_symlinks=False
                )
                
                if not os.path.exists(model_path):
                    raise FileNotFoundError(f"Downloaded file not found at {model_path}")
                    
            except ImportError:
                # Fall back to wget if huggingface_hub is not installed
                print("Hugging Face Hub not available, using wget for download")
                spinner = ProgressSpinner(message=f"Downloading {model_file}")
                spinner.start()
                
                result = subprocess.run(
                    ["wget", "-O", model_path, download_url],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    check=False
                )
                
                spinner.stop()
                
                if result.returncode != 0 or not os.path.exists(model_path):
                    print(f"Download failed: {result.stderr}")
                    return False
            
            # Create a Modelfile
            modelfile_path = os.path.join(temp_dir, "Modelfile")
            with open(modelfile_path, "w") as f:
                f.write(f"FROM {model_file}\n")
                f.write("PARAMETER num_ctx 4096\n")
                f.write('SYSTEM """\nPoland-optimized NLU model with constitutional AI constraints\n"""\n')
            
            # Create the model in Ollama
            print(f"\nCreating Ollama model: {custom_model_name}")
            spinner = ProgressSpinner(message=f"Creating model in Ollama")
            spinner.start()
            
            result = subprocess.run(
                [self.ollama_path, "create", custom_model_name, "-f", modelfile_path],
                cwd=temp_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=False
            )
            
            spinner.stop()
            
            if result.returncode == 0:
                print(f"\nSuccessfully created model: {custom_model_name}")
                print(f"Original model name: {model_name}")
                print(f"\nYou can now use this model with: --model {custom_model_name}")
                
                # Update environment variables for future use
                os.environ["OLLAMA_MODEL"] = custom_model_name
                
                # Update fallback models to include this model
                fallback_models = os.environ.get("OLLAMA_FALLBACK_MODELS", "")
                if fallback_models:
                    os.environ["OLLAMA_FALLBACK_MODELS"] = f"{custom_model_name},{fallback_models}"
                else:
                    os.environ["OLLAMA_FALLBACK_MODELS"] = custom_model_name
                
                # Enable auto-select model
                os.environ["OLLAMA_AUTO_SELECT_MODEL"] = "true"
                
                # Update the current model
                self.model = custom_model_name
                
                # Save these settings to .env file if it exists
                self._update_env_file(custom_model_name)
                
                return True
            else:
                print(f"Failed to create model: {custom_model_name}")
                print(f"Error: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"Error during model installation: {e}")
            return False
    
    def _update_env_file(self, model_name: str) -> None:
        """
        Update the .env file with the new model settings.
        
        Args:
            model_name: The name of the model to set as default
        """
        from pathlib import Path
        
        # Try to find the central .env file
        current_dir = Path(__file__).parent.absolute()
        env_file = None
        
        # Check if we're in a subdirectory of py-lama
        parts = current_dir.parts
        for i in range(len(parts) - 1, 0, -1):
            if parts[i] == "py-lama":
                env_file = Path(*parts[:i+1]) / ".env"
                break
        
        # If not found, look for the directory structure
        if not env_file or not env_file.exists():
            # Try the local .env file
            env_file = current_dir / ".env"
        
        # Check if .env file exists
        if not env_file.exists():
            try:
                # Create a new .env file
                with open(env_file, "w") as f:
                    f.write(f"OLLAMA_MODEL={model_name}\n")
                    f.write(f"OLLAMA_FALLBACK_MODELS={model_name},codellama:7b,phi:latest\n")
                    f.write("OLLAMA_AUTO_SELECT_MODEL=true\n")
                    # Set higher timeout for Bielik models
                    f.write("OLLAMA_TIMEOUT=120\n")
                print(f"Created .env file with model settings: {env_file}")
            except Exception as e:
                print(f"Error creating .env file: {e}")
            return
        
        try:
            # Read existing .env file
            with open(env_file, "r") as f:
                lines = f.readlines()
            
            # Update or add model settings
            model_line_found = False
            fallback_line_found = False
            auto_select_line_found = False
            timeout_line_found = False
            
            for i, line in enumerate(lines):
                if line.startswith("OLLAMA_MODEL="):
                    lines[i] = f"OLLAMA_MODEL={model_name}\n"
                    model_line_found = True
                elif line.startswith("OLLAMA_FALLBACK_MODELS="):
                    # Add the new model to fallback models if not already there
                    fallback_models = line.split("=")[1].strip()
                    if model_name not in fallback_models:
                        lines[i] = f"OLLAMA_FALLBACK_MODELS={model_name},{fallback_models}\n"
                    fallback_line_found = True
                elif line.startswith("OLLAMA_AUTO_SELECT_MODEL="):
                    lines[i] = "OLLAMA_AUTO_SELECT_MODEL=true\n"
                    auto_select_line_found = True
                elif line.startswith("OLLAMA_TIMEOUT="):
                    # Set higher timeout for Bielik models
                    lines[i] = "OLLAMA_TIMEOUT=120\n"
                    timeout_line_found = True
            
            # Add missing settings
            if not model_line_found:
                lines.append(f"OLLAMA_MODEL={model_name}\n")
            if not fallback_line_found:
                lines.append(f"OLLAMA_FALLBACK_MODELS={model_name},codellama:7b,phi:latest\n")
            if not auto_select_line_found:
                lines.append("OLLAMA_AUTO_SELECT_MODEL=true\n")
            if not timeout_line_found:
                lines.append("OLLAMA_TIMEOUT=120\n")
            
            # Write updated .env file
            with open(env_file, "w") as f:
                f.writelines(lines)
                
            print(f"Updated .env file with model settings: {env_file}")
            
        except Exception as e:
            print(f"Error updating .env file: {e}")

    def list_installed_models(self) -> List[Dict[str, Any]]:
        """
        List models that are currently installed in Ollama.
        
        Returns:
            A list of dictionaries containing model information
        """
        try:
            response = requests.get(self.list_api_url, timeout=10)
            response.raise_for_status()
            return response.json().get('models', [])
        except Exception as e:
            logger.warning(f"Could not list installed models: {e}")
            return []


# Convenience functions for external use
def get_ollama_integration(model: str = None) -> OllamaIntegration:
    """
    Get an OllamaIntegration instance with the specified model.
    
    Args:
        model: Optional model name to use
        
    Returns:
        An OllamaIntegration instance
    """
    return OllamaIntegration(model=model)


def start_ollama_server() -> OllamaIntegration:
    """
    Start the Ollama server and return an OllamaIntegration instance.
    
    Returns:
        An OllamaIntegration instance with the server started
    """
    ollama = OllamaIntegration()
    ollama.start_ollama()
    return ollama


def install_ollama_model(model_name: str) -> bool:
    """
    Install a model using Ollama.
    
    Args:
        model_name: The name of the model to install
        
    Returns:
        True if installation was successful, False otherwise
    """
    ollama = OllamaIntegration()
    ollama.start_ollama()
    return ollama.install_model(model_name)


def list_ollama_models() -> List[Dict[str, Any]]:
    """
    List models that are currently installed in Ollama.
    
    Returns:
        A list of dictionaries containing model information
    """
    ollama = OllamaIntegration()
    try:
        ollama.start_ollama()
        return ollama.list_installed_models()
    except Exception:
        return []
