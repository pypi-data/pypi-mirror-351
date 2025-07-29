import sys
import subprocess
import os
import shutil
import json
from pathlib import Path
import re

# --- AUTO ENV & DEPENDENCY SETUP ---
REQUIRED_PACKAGES = ["requests", "bs4", "python-dotenv"]
IMPORT_NAMES = ["requests", "bs4", "dotenv"]  # Correct import for python-dotenv is 'dotenv'
VENV_DIR = os.path.join(os.path.dirname(__file__), ".venv")

# 1. Create venv if missing
if not os.path.isdir(VENV_DIR):
    subprocess.run([sys.executable, "-m", "venv", VENV_DIR], check=True)
    print(f"Created virtual environment: {VENV_DIR}")

# 2. Activate venv for subprocess installs (current process may not inherit, but subprocess installs will work)
def _venv_python():
    if os.name == "nt":
        return os.path.join(VENV_DIR, "Scripts", "python.exe")
    else:
        return os.path.join(VENV_DIR, "bin", "python")

# 3. Install missing packages
missing = []
for pkg, imp in zip(REQUIRED_PACKAGES, IMPORT_NAMES):
    try:
        __import__(imp)
    except ImportError:
        missing.append(pkg)
if missing:
    print(f"Installing missing packages: {', '.join(missing)}")
    subprocess.run([_venv_python(), "-m", "pip", "install"] + missing, check=True)
    print("Required dependencies installed. Please restart the script.")
    sys.exit(0)
# --- END AUTO ENV & DEPENDENCY SETUP ---

import dotenv
import requests
from bs4 import BeautifulSoup

# Import the OllamaIntegration module
from .ollama_integration import (
    OllamaIntegration,
    get_ollama_integration,
    start_ollama_server,
    install_ollama_model,
    list_ollama_models
)

def get_central_env_path():
    """
    Get the path to the central .env file in the PyLama root directory.
    
    Returns:
        Path to the central .env file.
    """
    # Start from the current directory and go up to find the py-lama directory
    current_dir = Path(__file__).parent.absolute()
    
    # Check if we're in a subdirectory of py-lama
    parts = current_dir.parts
    for i in range(len(parts) - 1, 0, -1):
        if parts[i] == "py-lama":
            return Path(*parts[:i+1]) / "pylama" / ".env"
    
    # If not found, look for the directory structure
    while current_dir != current_dir.parent:  # Stop at the root directory
        # Check if this looks like the py-lama directory
        if (current_dir / "pylama").exists() and (current_dir / "loglama").exists():
            return current_dir / "pylama" / ".env"
        if (current_dir / "pylama").exists() and (current_dir / "getllm").exists():
            return current_dir / "pylama" / ".env"
        
        # Move up one directory
        current_dir = current_dir.parent
    
    # If no central .env found, fall back to local .env
    return Path(__file__).parent / ".env"

def get_models_dir():
    """
    Get the models directory from the environment variables.
    
    Returns:
        Path to the models directory.
    """
    # Try to load from the central .env file first
    central_env_path = get_central_env_path()
    env = {}
    
    # For test compatibility, only check existence once
    if central_env_path.exists():
        env = dotenv.dotenv_values(central_env_path)
    
    # If not found in central .env, try local .env
    if "MODELS_DIR" not in env:
        local_env_path = Path(__file__).parent / ".env"
        if local_env_path.exists():
            local_env = dotenv.dotenv_values(local_env_path)
            env.update(local_env)
    
    return env.get("MODELS_DIR", "./models")

def get_default_model():
    """
    Get the default model from the environment variables.
    
    Returns:
        The default model name, or None if not set.
    """
    # Try to load from the central .env file first
    central_env_path = get_central_env_path()
    env = {}
    
    # For test compatibility, only check existence once
    if central_env_path.exists():
        env = dotenv.dotenv_values(central_env_path)
    
    # If not found in central .env, try local .env
    if "OLLAMA_MODEL" not in env:
        local_env_path = Path(__file__).parent / ".env"
        if local_env_path.exists():
            local_env = dotenv.dotenv_values(local_env_path)
            env.update(local_env)
    
    # Return None instead of empty string for test compatibility
    model = env.get("OLLAMA_MODEL", "")
    return model if model else None

def set_default_model(model_name):
    """
    Set the default model in the environment variables.
    
    Args:
        model_name: The name of the model to set as default.
    """
    # Get the central .env path
    central_env_path = get_central_env_path()
    
    # If central .env doesn't exist, try to create it
    if not central_env_path.exists():
        # Check if we have an example .env file to copy from
        example_env_path = Path(__file__).parent / ".." / "env.example"
        if example_env_path.exists():
            # Create the directory if it doesn't exist
            central_env_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy(str(example_env_path), str(central_env_path))
        else:
            # Create an empty .env file
            central_env_path.parent.mkdir(parents=True, exist_ok=True)
            central_env_path.touch()
    
    # For test compatibility, only check existence once
    env_exists = central_env_path.exists()
    
    lines = []
    found = False
    
    if env_exists:
        with open(central_env_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip().startswith("OLLAMA_MODEL="):
                    lines.append(f"OLLAMA_MODEL={model_name}\n")
                    found = True
                else:
                    lines.append(line)
    
    if not found:
        lines.append(f"OLLAMA_MODEL={model_name}\n")
    
    with open(central_env_path, "w", encoding="utf-8") as f:
        f.writelines(lines)
    
    print(f"Set OLLAMA_MODEL={model_name} as default in central .env file")

DEFAULT_MODELS = [
    {"name": "tinyllama:1.1b", "size": "1.1B", "desc": "TinyLlama 1.1B - szybki, mały model"},
    {"name": "codellama:7b", "size": "7B", "desc": "CodeLlama 7B - kodowanie, Meta"},
    {"name": "wizardcoder:7b-python", "size": "7B", "desc": "WizardCoder 7B Python"},
    {"name": "deepseek-coder:6.7b", "size": "6.7B", "desc": "Deepseek Coder 6.7B"},
    {"name": "codegemma:2b", "size": "2B", "desc": "CodeGemma 2B - Google"},
    {"name": "phi:2.7b", "size": "2.7B", "desc": "Microsoft Phi-2 2.7B"},
    {"name": "stablelm-zephyr:3b", "size": "3B", "desc": "StableLM Zephyr 3B"},
    {"name": "mistral:7b", "size": "7B", "desc": "Mistral 7B"},
    {"name": "qwen:7b", "size": "7B", "desc": "Qwen 7B"},
    {"name": "gemma:7b", "size": "7B", "desc": "Gemma 7B"},
    {"name": "gemma:2b", "size": "2B", "desc": "Gemma 2B"}
]

MODELS_JSON = "models.json"

def save_models_to_json(models=DEFAULT_MODELS, file_path=None):
    """
    Save models to a JSON file.
    
    Args:
        models: The models to save.
        file_path: The path to the JSON file. If None, uses the default path.
    """
    if file_path is None:
        # Use the centralized models directory
        models_dir = get_models_dir()
        Path(models_dir).mkdir(parents=True, exist_ok=True)
        file_path = os.path.join(models_dir, MODELS_JSON)
    
    # Ensure the parent directory exists
    Path(file_path).parent.mkdir(parents=True, exist_ok=True)
    
    with open(file_path, "w", encoding="utf-8") as f:
        # For test compatibility, convert to string first
        json_str = json.dumps(models, ensure_ascii=False, indent=2)
        f.write(json_str)

def load_models_from_json(file_path=None):
    """
    Load models from a JSON file.
    
    Args:
        file_path: The path to the JSON file. If None, uses the default path.
        
    Returns:
        The loaded models, or the default models if the file doesn't exist.
    """
    if file_path is None:
        # Use the centralized models directory
        models_dir = get_models_dir()
        file_path = os.path.join(models_dir, MODELS_JSON)
    
    # Use Path.exists() instead of os.path.exists() for test compatibility
    if Path(file_path).exists():
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                models = json.load(f)
                return models
        except Exception as e:
            print(f"Error loading JSON: {e}")
    
    return DEFAULT_MODELS

def get_models():
    models = load_models_from_json()
    return models

def install_model(model_name):
    """
    Install a model using Ollama.
    
    Args:
        model_name: The name of the model to install.
        
    Returns:
        True if installation was successful, False otherwise.
    """
    try:
        # Use the OllamaIntegration module to install the model
        return install_ollama_model(model_name)
    except Exception as e:
        print(f"Error installing model: {e}")
        return False

def list_installed_models():
    """
    List models that are currently installed in Ollama.
    
    Returns:
        A list of installed model names.
    """
    try:
        # Use the OllamaIntegration module to list installed models
        models = list_ollama_models()
        return [model['name'] for model in models]
    except Exception as e:
        print(f"Error listing installed models: {e}")
        return []

def update_models_from_ollama():
    """
    Fetch the latest coding-related models up to 7B from the Ollama library web page
    and update the local models.json file.
    """
    import requests
    import re
    from bs4 import BeautifulSoup
    import json
    import os
    
    MODELS_HTML_URL = "https://ollama.com/library"
    try:
        # Fetch the Ollama library page
        response = requests.get("https://ollama.com/library")
        response.raise_for_status()
        
        # Parse the HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find all model cards
        model_cards = soup.find_all('div', class_=re.compile('card'))
        
        # Extract model information
        models = []
        for card in model_cards:
            try:
                # Extract the model name
                name_elem = card.find('h3') or card.find('h2')
                if not name_elem:
                    continue
                
                # Get the full name with tag
                model_name = name_elem.text.strip()
                
                # Extract the description
                desc_elem = card.find('p')
                description = desc_elem.text.strip() if desc_elem else ""
                
                # Extract the model size if available
                size_match = re.search(r'\b(\d+(\.\d+)?[BM])\b', description)
                size = size_match.group(1) if size_match else "Unknown"
                
                # Check if this is a coding-related model
                is_coding = any(keyword in description.lower() or keyword in model_name.lower() 
                               for keyword in ['code', 'programming', 'developer', 'coder'])
                
                # Filter out models larger than 7B
                is_small_enough = True
                if 'B' in size:
                    try:
                        size_value = float(size.replace('B', ''))
                        is_small_enough = size_value <= 7.0
                    except ValueError:
                        pass  # If we can't parse the size, assume it's ok
                
                # Only add coding-related models that are small enough
                if is_coding and is_small_enough:
                    models.append({
                        "name": model_name,
                        "size": size,
                        "desc": description
                    })
            except Exception as e:
                print(f"Error parsing model card: {e}")
                continue
        
        # Add default models if not already in the list
        model_names = [model["name"] for model in models]
        for default_model in DEFAULT_MODELS:
            if default_model["name"] not in model_names:
                models.append(default_model)
        
        # Get installed models from Ollama
        try:
            ollama = get_ollama_integration()
            ollama.start_ollama()
            installed_models = ollama.list_installed_models()
            
            # Add installed models that aren't already in the list
            for installed in installed_models:
                if installed['name'] not in model_names:
                    models.append({
                        "name": installed['name'],
                        "size": "Unknown",
                        "desc": f"Installed model: {installed['name']}"
                    })
                    model_names.append(installed['name'])
        except Exception as e:
            print(f"Warning: Could not get installed models from Ollama: {e}")
        
        # Save the updated models to the JSON file
        save_models_to_json(models)
        
        print(f"Updated models.json with {len(models)} models from Ollama library")
        return models
    except Exception as e:
        print(f"Error updating models from Ollama: {e}")
        return DEFAULT_MODELS

class ModelManager:
    """
    Class for managing LLM models in the PyLLM system.
    Provides methods for listing, installing, and using models.
    
    This class uses the centralized environment system to access model information
    and configuration that is shared across all PyLama components.
    """
    
    def __init__(self):
        # Use the centralized environment to get the default model
        self.default_model = get_default_model() or "llama3"
        self.models = self.get_available_models()
    
    def get_available_models(self):
        """
        Get a list of available models from the models.json file or default list.
        """
        return get_models()
    
    def list_models(self):
        """
        Return a list of available models.
        """
        return self.models
    
    def get_model_info(self, model_name):
        """
        Get information about a specific model.
        """
        for model in self.models:
            if model.get("name") == model_name:
                return model
        return None
    
    def install_model(self, model_name):
        """
        Install a model using Ollama.
        
        Args:
            model_name: The name of the model to install.
            
        Returns:
            True if installation was successful, False otherwise.
        """
        try:
            # Use the OllamaIntegration module to install the model
            return install_ollama_model(model_name)
        except Exception as e:
            print(f"Error installing model: {e}")
            return False
    
    def list_installed_models(self):
        """
        List models that are currently installed.
        
        Returns:
            A list of installed model names.
        """
        # Use the OllamaIntegration module to list installed models
        ollama = get_ollama_integration()
        try:
            # Start the Ollama server if it's not already running
            ollama.start_ollama()
            
            # Get the list of installed models
            models = ollama.list_installed_models()
            return [model['name'] for model in models]
        except Exception as e:
            print(f"Error listing installed models: {e}")
            return []
    
    def set_default_model(self, model_name):
        """
        Set the default model to use.
        """
        set_default_model(model_name)
        self.default_model = model_name
        return True
    
    def get_default_model_name(self):
        """
        Get the name of the current default model.
        """
        return self.default_model
    
    def update_models_from_remote(self):
        """
        Update the models list from the Ollama library.
        """
        update_models_from_ollama()
        self.models = self.get_available_models()
        return True

if __name__ == "__main__":
    default_model = get_default_model()
    print("Available models:")
    models = get_models()
    for idx, m in enumerate(models, 1):
        print(f"{idx}. {m['name']} ({m.get('desc', '')})")
    if default_model:
        print(f"\nCurrent default model: {default_model}\n")
    else:
        print("\nNo default model set in .env\n")
    print("\nSaving list to models.json...")
    save_models_to_json(models)
    print("\nZainstalowane modele:")
    list_installed_models()
    print("\n--- Model Installation ---")
    print("Enter the model number to download, 'u' to update the model list from the Ollama project, or 'q' to exit.")
    while True:
        wyb = input("Choose model (number/'u'/'q'): ").strip()
        if wyb.lower() == 'q':
            print("Done.")
            break
        if wyb.lower() == 'u':
            update_models_from_ollama()
            models = get_models()
            for idx, m in enumerate(models, 1):
                print(f"{idx}. {m['name']} ({m.get('desc', '')})")
            continue
        if wyb.isdigit() and 1 <= int(wyb) <= len(models):
            model_name = models[int(wyb) - 1]["name"]
            # Check if the model is installed
            installed = False
            try:
                output = subprocess.check_output(["ollama", "list"]).decode()
                installed = any(model_name in line for line in output.strip().split("\n")[1:])
            except Exception:
                pass
            if not installed:
                ok = install_model(model_name)
                if not ok:
                    continue
            set_default_model(model_name)
        else:
            print("Invalid choice.")
