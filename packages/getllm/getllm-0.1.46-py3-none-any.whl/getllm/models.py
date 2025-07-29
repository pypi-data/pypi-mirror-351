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
            return Path(*parts[:i+1]) / "devlama" / ".env"
    
    # If not found, look for the directory structure
    while current_dir != current_dir.parent:  # Stop at the root directory
        # Check if this looks like the py-lama directory
        if (current_dir / "devlama").exists() and (current_dir / "loglama").exists():
            return current_dir / "devlama" / ".env"
        if (current_dir / "devlama").exists() and (current_dir / "getllm").exists():
            return current_dir / "devlama" / ".env"
        
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

def search_huggingface_models(query=None, limit=20):
    """
    Search for models on Hugging Face that match the given query.
    
    Args:
        query: The search query (e.g., "bielik"). If None, returns popular GGUF models.
        limit: Maximum number of results to return.
        
    Returns:
        A list of dictionaries containing model information.
    """
    import requests
    
    try:
        # Base URL for the Hugging Face API
        api_url = "https://huggingface.co/api/models"
        
        # Parameters for the API request
        params = {
            "limit": limit,
            "filter": "gguf",  # Filter for GGUF models compatible with Ollama
            "sort": "downloads",
            "direction": -1  # Sort by most downloads
        }
        
        # Add search query if provided
        if query:
            params["search"] = query
        
        # Make the API request
        response = requests.get(api_url, params=params)
        response.raise_for_status()
        
        # Parse the response
        models_data = response.json()
        
        # Format the results
        results = []
        for model in models_data:
            # Extract model information
            model_id = model.get("id", "")
            model_name = model_id.split("/")[-1] if "/" in model_id else model_id
            
            # Get the model size if available
            size = "Unknown"
            for tag in model.get("tags", []):
                if "q4_k_m" in tag or "q4_0" in tag or "q5_k_m" in tag or "q8_0" in tag:
                    size_match = re.search(r'\b(\d+(\.\d+)?[BM])\b', model.get("description", ""))
                    if size_match:
                        size = size_match.group(1)
                    break
            
            # Add the model to the results
            results.append({
                "name": model_id,  # Full model ID (e.g., "SpeakLeash/bielik-1.5b-v3.0-instruct-gguf")
                "size": size,
                "desc": model.get("description", "")[:100] + ("..." if len(model.get("description", "")) > 100 else ""),
                "downloads": model.get("downloads", 0),
                "likes": model.get("likes", 0),
                "tags": model.get("tags", [])
            })
        
        return results
    except Exception as e:
        print(f"Error searching Hugging Face models: {e}")
        return []

def interactive_model_search(query=None, check_ollama=True):
    """
    Search for models on Hugging Face and allow the user to interactively select one to install.
    
    Args:
        query: The search query (e.g., "bielik"). If None, prompts the user for a query.
        check_ollama: Whether to check if Ollama is installed before proceeding.
        
    Returns:
        The selected model ID or None if cancelled.
    """
    try:
        import questionary
        
        # Check if Ollama is installed if requested
        if check_ollama:
            from getllm.ollama_integration import OllamaIntegration
            ollama = OllamaIntegration()
            
            # Check if we're already in mock mode (set by previous installation choice)
            if os.environ.get('GETLLM_MOCK_MODE') == 'true':
                print("\nRunning in mock mode - Ollama checks bypassed")
                # Continue with model search in mock mode
            elif not ollama.is_ollama_installed:
                print("\nOllama is not installed but required for model installation.")
                
                # Use the enhanced installation options
                if ollama._install_ollama():
                    print("\n✅ Ollama installed successfully! Continuing with model search...")
                elif os.environ.get('GETLLM_MOCK_MODE') == 'true':
                    # User chose mock mode in the installation menu
                    print("\nContinuing with model search in mock mode...")
                else:
                    # User cancelled or installation failed
                    print("\nIf you want to continue without Ollama, use the --mock flag:")
                    print("  getllm --mock --search <query>")
                    return None
        
        # If no query provided, ask the user
        if query is None:
            query = questionary.text("Enter a search term for Hugging Face models:").ask()
            if not query:
                print("Search cancelled.")
                return None
        
        print(f"Searching for models matching '{query}' on Hugging Face...")
        models = search_huggingface_models(query)
        
        if not models:
            print(f"No models found matching '{query}'.")
            return None
        
        # Create choices for the questionary select
        choices = [
            questionary.Choice(
                title=f"{m['name']:<50} {m['size']:<10} Downloads: {m['downloads']:,} | {m['desc']}",
                value=m['name']
            ) for m in models
        ]
        
        # Add a cancel option
        choices.append(questionary.Choice(title="Cancel", value=None))
        
        # Ask the user to select a model
        selected = questionary.select(
            "Select a model to install:",
            choices=choices
        ).ask()
        
        # If user selected Cancel (None), return early
        if selected is None:
            print("Selection cancelled.")
            return None
        
        return selected
    except Exception as e:
        print(f"Error in interactive model search: {e}")
        return None

def update_models_from_huggingface(query=None, interactive=True):
    """
    Search for models on Hugging Face and update the local models.json file.
    
    Args:
        query: The search query (e.g., "bielik"). If None and interactive is True, prompts the user.
        interactive: Whether to allow interactive selection of models.
        
    Returns:
        The updated list of models.
    """
    try:
        # Get existing models
        existing_models = load_models_from_json()
        existing_names = [model["name"] for model in existing_models]
        
        # Search for models
        if interactive:
            selected_model = interactive_model_search(query)
            if selected_model:
                # Check if the model is already in the list
                if selected_model not in existing_names:
                    # Get detailed information about the selected model
                    model_info = search_huggingface_models(selected_model, limit=1)
                    if model_info:
                        # Add the model to the list
                        existing_models.append(model_info[0])
                        # Save the updated list
                        save_models_to_json(existing_models)
                        print(f"Added {selected_model} to the models list.")
                        
                        # Ask if the user wants to install the model now
                        import questionary
                        install_now = questionary.confirm("Do you want to install this model now?", default=True).ask()
                        if install_now:
                            install_model(selected_model)
                    else:
                        print(f"Could not get detailed information about {selected_model}.")
                else:
                    print(f"Model {selected_model} is already in the list.")
                    # Ask if the user wants to install the model now
                    import questionary
                    install_now = questionary.confirm("Do you want to install this model now?", default=True).ask()
                    if install_now:
                        install_model(selected_model)
        else:
            # Non-interactive mode: just search and add models
            if not query:
                print("Error: Query is required in non-interactive mode.")
                return existing_models
                
            new_models = search_huggingface_models(query)
            added = 0
            
            for model in new_models:
                if model["name"] not in existing_names:
                    existing_models.append(model)
                    existing_names.append(model["name"])
                    added += 1
            
            if added > 0:
                save_models_to_json(existing_models)
                print(f"Added {added} new models to the models list.")
            else:
                print("No new models added.")
        
        return existing_models
    except Exception as e:
        print(f"Error updating models from Hugging Face: {e}")
        return load_models_from_json()

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
    
    def update_models_from_remote(self, source="ollama", query=None, interactive=True):
        """
        Update the models list from a remote source.
        
        Args:
            source: The source to update from ("ollama" or "huggingface").
            query: The search query for Hugging Face models.
            interactive: Whether to allow interactive selection for Hugging Face models.
            
        Returns:
            The updated list of models.
        """
        try:
            if source.lower() == "huggingface":
                models = update_models_from_huggingface(query, interactive)
            else:
                models = update_models_from_ollama()
                
            self.models = models
            return models
        except Exception as e:
            print(f"Error updating models from {source}: {e}")
            return self.models
            
    def search_huggingface_models(self, query=None, limit=20):
        """
        Search for models on Hugging Face.
        
        Args:
            query: The search query.
            limit: Maximum number of results to return.
            
        Returns:
            A list of model dictionaries.
        """
        return search_huggingface_models(query, limit)
        
    def interactive_model_search(self, query=None):
        """
        Interactive search for models on Hugging Face.
        
        Args:
            query: The search query.
            
        Returns:
            The selected model ID or None if cancelled.
        """
        return interactive_model_search(query)

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
