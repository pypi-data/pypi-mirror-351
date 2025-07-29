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

def update_models_metadata():
    """
    Create and update a combined models metadata file that contains information
    about both Hugging Face and Ollama models.
    
    This function loads models from both Hugging Face and Ollama caches and
    combines them into a single metadata file for easier access.
    
    Returns:
        True if successful, False otherwise.
    """
    try:
        # Get models from both sources
        hf_models = load_huggingface_models_from_cache()
        ollama_models = load_ollama_models_from_cache()
        
        # If no cached models, try to fetch them
        if not hf_models:
            print("No Hugging Face models in cache, using default models...")
            hf_models = DEFAULT_HF_MODELS
        
        if not ollama_models:
            print("No Ollama models in cache, using default models...")
            ollama_models = DEFAULT_MODELS
            
        # Create a combined metadata dictionary
        metadata = {}
        
        # Add Hugging Face models
        for model in hf_models:
            model_id = model.get('id') or model.get('name')
            if not model_id:
                continue
                
            metadata[model_id] = {
                'name': model.get('name', model_id),
                'source': 'huggingface',
                'description': model.get('description', ''),
                'size': model.get('size', 'Unknown'),
                'downloads': model.get('downloads', ''),
                'url': model.get('url', f"https://huggingface.co/{model_id}"),
                'metadata': model.get('metadata', {})
            }
        
        # Add Ollama models
        for model in ollama_models:
            model_name = model.get('name')
            if not model_name:
                continue
                
            metadata[model_name] = {
                'name': model_name,
                'source': 'ollama',
                'description': model.get('desc', ''),
                'size': model.get('size', 'Unknown'),
                'url': model.get('url', ''),
                'metadata': model.get('metadata', {})
            }
        
        # Save the combined metadata to a file
        metadata_path = get_models_metadata_path()
        os.makedirs(os.path.dirname(metadata_path), exist_ok=True)
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
            
        print(f"Successfully updated models metadata with {len(metadata)} models.")
        return True
    
    except Exception as e:
        print(f"Error updating models metadata: {e}")
        return False

def get_model_metadata(model_name):
    """
    Get metadata for a specific model.
    
    Args:
        model_name: The name of the model to get metadata for.
        
    Returns:
        A dictionary containing model metadata, or None if not found.
    """
    try:
        # Try to load from metadata file first
        metadata_path = get_models_metadata_path()
        if os.path.exists(metadata_path):
            with open(metadata_path, 'r') as f:
                metadata = json.load(f)
                if model_name in metadata:
                    return metadata[model_name]
        
        # If not found, check Hugging Face models
        hf_models = load_huggingface_models_from_cache()
        for model in hf_models:
            if model.get('id') == model_name or model.get('name') == model_name:
                return {
                    'name': model.get('name', model_name),
                    'source': 'huggingface',
                    'description': model.get('description', ''),
                    'size': model.get('size', 'Unknown'),
                    'downloads': model.get('downloads', ''),
                    'url': model.get('url', f"https://huggingface.co/{model_name}"),
                    'metadata': model.get('metadata', {})
                }
        
        # If not found, check Ollama models
        ollama_models = load_ollama_models_from_cache()
        for model in ollama_models:
            if model.get('name') == model_name:
                return {
                    'name': model_name,
                    'source': 'ollama',
                    'description': model.get('desc', ''),
                    'size': model.get('size', 'Unknown'),
                    'url': model.get('url', ''),
                    'metadata': model.get('metadata', {})
                }
        
        return None
    
    except Exception as e:
        print(f"Error getting model metadata: {e}")
        return None

def get_models():
    """
    Get a list of available models from the models.json file or default list.
    Also updates the models metadata file if needed.
    
    Returns:
        A list of dictionaries containing model information.
    """
    # Update models metadata in the background (don't wait for it)
    try:
        update_models_metadata()
    except Exception as e:
        print(f"Warning: Could not update models metadata: {e}")
    
    return load_models_from_json()

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

# Hardcoded list of popular Hugging Face GGUF models
DEFAULT_HF_MODELS = [
    {
        'id': 'TheBloke/Llama-2-7B-Chat-GGUF',
        'description': 'Llama 2 7B Chat GGUF',
        'downloads': '100K+',
        'source': 'huggingface'
    },
    {
        'id': 'TheBloke/Mistral-7B-Instruct-v0.2-GGUF',
        'description': 'Mistral 7B Instruct v0.2 GGUF',
        'downloads': '50K+',
        'source': 'huggingface'
    },
    {
        'id': 'TheBloke/Llama-3-8B-Instruct-GGUF',
        'description': 'Llama 3 8B Instruct GGUF',
        'downloads': '100K+',
        'source': 'huggingface'
    },
    {
        'id': 'TheBloke/phi-2-GGUF',
        'description': 'Phi-2 GGUF',
        'downloads': '50K+',
        'source': 'huggingface'
    },
    {
        'id': 'TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF',
        'description': 'TinyLlama 1.1B Chat GGUF',
        'downloads': '10K+',
        'source': 'huggingface'
    },
    {
        'id': 'TheBloke/Gemma-7B-it-GGUF',
        'description': 'Gemma 7B Instruct GGUF',
        'downloads': '20K+',
        'source': 'huggingface'
    },
    {
        'id': 'TheBloke/Gemma-2B-it-GGUF',
        'description': 'Gemma 2B Instruct GGUF',
        'downloads': '10K+',
        'source': 'huggingface'
    },
    {
        'id': 'TheBloke/CodeLlama-7B-Instruct-GGUF',
        'description': 'CodeLlama 7B Instruct GGUF',
        'downloads': '50K+',
        'source': 'huggingface'
    },
    {
        'id': 'TheBloke/WizardCoder-Python-7B-V1.0-GGUF',
        'description': 'WizardCoder Python 7B GGUF',
        'downloads': '20K+',
        'source': 'huggingface'
    },
    {
        'id': 'speakleash/Bielik-1.5B-v3.0-Instruct-GGUF',
        'description': 'Bielik 1.5B v3.0 Instruct GGUF',
        'downloads': '1K+',
        'source': 'huggingface'
    },
    {
        'id': 'speakleash/Bielik-4.5B-v3.0-Instruct-GGUF',
        'description': 'Bielik 4.5B v3.0 Instruct GGUF',
        'downloads': '1K+',
        'source': 'huggingface'
    },
    {
        'id': 'speakleash/Bielik-11B-v2.3-Instruct-GGUF',
        'description': 'Bielik 11B v2.3 Instruct GGUF',
        'downloads': '500+',
        'source': 'huggingface'
    }
]

# Paths to the models cache files
def get_hf_models_cache_path():
    return os.path.join(os.path.dirname(__file__), 'hf_models.json')

def get_ollama_models_cache_path():
    return os.path.join(os.path.dirname(__file__), 'ollama_models.json')

def get_models_metadata_path():
    return os.path.join(os.path.dirname(__file__), 'models_metadata.json')

def load_huggingface_models_from_cache():
    """
    Load Hugging Face models from the cache file.
    
    Returns:
        A list of Hugging Face models, or an empty list if the cache file doesn't exist or is invalid.
    """
    try:
        cache_path = get_hf_models_cache_path()
        if os.path.exists(cache_path):
            with open(cache_path, 'r') as f:
                return json.load(f)
        return []
    except Exception as e:
        print(f"Error loading Hugging Face models from cache: {e}")
        return []

def get_huggingface_models():
    """
    Get a list of popular models from Hugging Face.
    First tries to load from the cache file, then falls back to the hardcoded list.
    
    Returns:
        A list of dictionaries containing model information.
    """
    # Try to load from cache file first
    cached_models = load_huggingface_models_from_cache()
    if cached_models and len(cached_models) > 0:
        return cached_models
    
    # Fall back to hardcoded list
    # Ensure all DEFAULT_HF_MODELS have metadata and name fields
    for model in DEFAULT_HF_MODELS:
        if 'metadata' not in model:
            model['metadata'] = {
                'description': model.get('description', ''),
                'downloads': model.get('downloads', ''),
                'updated': model.get('updated', ''),
                'url': f"https://huggingface.co/{model['id']}",
                'size': model.get('size', 'Unknown'),
                'source': 'huggingface'
            }
        if 'name' not in model:
            model['name'] = model['id']
    
    return DEFAULT_HF_MODELS

def search_huggingface_models(query=None, limit=20):
    """
    Search for models on Hugging Face that match the given query.
    Uses the cached or hardcoded list and filters by the query.
    
    Args:
        query: The search query (e.g., "bielik"). If None, returns all models.
        limit: Maximum number of results to return.
        
    Returns:
        A list of dictionaries containing model information.
    """
    try:
        # First try to use the local cache or hardcoded models
        all_models = get_huggingface_models()
        
        # If no query, return all models up to the limit
        if not query:
            return all_models[:limit]
        
        # Filter models by query
        query = query.lower()
        filtered_models = []
        
        # Search in multiple fields
        for model in all_models:
            # Check in id/name
            if query in model.get('id', '').lower() or query in model.get('name', '').lower():
                filtered_models.append(model)
                continue
                
            # Check in description
            if query in model.get('description', '').lower():
                filtered_models.append(model)
                continue
                
            # Check in metadata
            metadata = model.get('metadata', {})
            if metadata and any(query in str(v).lower() for v in metadata.values() if v):
                filtered_models.append(model)
                continue
        
        # If we found models in the cache/hardcoded list, return them
        if filtered_models:
            return filtered_models[:limit]
        
        # Special handling for 'meta' query - look for Meta AI models
        if query == 'meta':
            meta_models = []
            for model in all_models:
                desc = model.get('description', '').lower()
                if 'meta' in desc and ('ai' in desc or 'llama' in desc):
                    meta_models.append(model)
            if meta_models:
                return meta_models[:limit]
        
        # Special handling for 'biel' query - look for Bielik models
        if 'biel' in query:
            bielik_models = []
            for model in all_models:
                if 'bielik' in model.get('id', '').lower() or 'bielik' in model.get('name', '').lower():
                    bielik_models.append(model)
            if bielik_models:
                return bielik_models[:limit]
        
        # If still no models found, try a direct search with error handling
        try:
            # Use a custom User-Agent to avoid 401 errors
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            # Fetch models matching the query
            url = f"https://huggingface.co/search/models?search={query}&sort=downloads&filter=gguf"
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            # Parse the HTML content
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find all model cards
            model_cards = soup.select('article.overview-card')
            
            results = []
            for card in model_cards[:limit]:
                # Extract model ID (username/model_name)
                model_id_elem = card.select_one('a.header-link')
                if not model_id_elem:
                    continue
                
                model_id = model_id_elem.text.strip()
                
                # Extract description
                desc_elem = card.select_one('p.description')
                description = desc_elem.text.strip() if desc_elem else ""
                
                # Extract downloads count
                downloads_elem = card.select_one('div.flex.flex-col span.whitespace-nowrap')
                downloads = downloads_elem.text.strip() if downloads_elem else ""
                
                # Extract model URL
                model_url = None
                if model_id_elem and 'href' in model_id_elem.attrs:
                    href = model_id_elem['href']
                    if href.startswith('/'):
                        model_url = f"https://huggingface.co{href}"
                    elif href.startswith('http'):
                        model_url = href
                
                # Extract size from description if available
                size = "Unknown"
                size_match = re.search(r'\b(\d+(\.\d+)?[BM])\b', description)
                if size_match:
                    size = size_match.group(1)
                
                # Create metadata
                metadata = {
                    'description': description,
                    'downloads': downloads,
                    'url': model_url,
                    'size': size,
                    'source': 'huggingface'
                }
                
                results.append({
                    'id': model_id,
                    'name': model_id,
                    'description': description,
                    'downloads': downloads,
                    'url': model_url,
                    'size': size,
                    'source': 'huggingface',
                    'metadata': metadata
                })
            
            # If we found models from the direct search, save them to the cache
            if results:
                try:
                    # Get existing cache
                    cached_models = load_huggingface_models_from_cache()
                    
                    # Add new models if they don't exist in cache
                    existing_ids = {m.get('id') for m in cached_models}
                    for model in results:
                        if model.get('id') not in existing_ids:
                            cached_models.append(model)
                    
                    # Save updated cache
                    cache_path = get_hf_models_cache_path()
                    os.makedirs(os.path.dirname(cache_path), exist_ok=True)
                    with open(cache_path, 'w') as f:
                        json.dump(cached_models, f, indent=2)
                    
                    print(f"Added {len(results)} new models to HF cache.")
                except Exception as cache_e:
                    print(f"Error updating HF cache with search results: {cache_e}")
            
            return results
        except Exception as e:
            # If direct search fails, return the filtered models from cache/hardcoded list
            print(f"Error searching Hugging Face models: {e}")
            return filtered_models[:limit]
    except Exception as e:
        # If anything fails, return an empty list
        print(f"Error searching Hugging Face models: {e}")
        return []

def update_huggingface_models_cache(limit=50):
    """
    Update the Hugging Face models cache by fetching from the HF website.
    This is a separate function that can be called to refresh the cache.
    
    Args:
        limit: Maximum number of models to fetch
        
    Returns:
        True if successful, False otherwise.
    """
    # Try to use the model_scrapers module first
    try:
        from .model_scrapers import scrape_huggingface_models, are_scrapers_available
        if are_scrapers_available():
            models = scrape_huggingface_models(limit=limit)
            return len(models) > 0
    except ImportError:
        print("Model scrapers not available, using fallback method")
        # Continue with the fallback method below
    try:
        print("Fetching models from Hugging Face...")
        # Use multiple User-Agent options to avoid 401 errors
        headers_options = [
            {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            },
            {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Safari/605.1.15'
            },
            {
                'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36'
            }
        ]
        
        # Try different URLs and User-Agents
        urls = [
            "https://huggingface.co/models?sort=downloads&filter=gguf",
            "https://huggingface.co/models?filter=gguf&sort=downloads",
            "https://huggingface.co/models?filter=gguf"
        ]
        
        response = None
        success = False
        
        # Try each combination of URL and header until one works
        for url in urls:
            for headers in headers_options:
                try:
                    response = requests.get(url, headers=headers, timeout=10)
                    response.raise_for_status()
                    success = True
                    break
                except Exception as e:
                    print(f"Attempt failed with {url}: {e}")
                    continue
            if success:
                break
        
        # If all attempts failed, raise an exception
        if not success or not response:
            raise Exception("All attempts to fetch models from Hugging Face failed")
        
        # Parse the HTML content
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find all model cards
        model_cards = soup.select('article.overview-card')
        
        results = []
        for card in model_cards[:50]:  # Get top 50 models
            # Extract model ID (username/model_name)
            model_id_elem = card.select_one('a.header-link')
            if not model_id_elem:
                continue
            
            model_id = model_id_elem.text.strip()
            
            # Extract description
            desc_elem = card.select_one('p.description')
            description = desc_elem.text.strip() if desc_elem else ""
            
            # Extract downloads count
            downloads_elem = card.select_one('div.flex.flex-col span.whitespace-nowrap')
            downloads = downloads_elem.text.strip() if downloads_elem else ""
            
            # Extract last updated time
            updated_elem = card.select_one('div.metadata time')
            updated = updated_elem.text.strip() if updated_elem else ""
            
            # Extract model URL
            model_url = None
            if model_id_elem and 'href' in model_id_elem.attrs:
                href = model_id_elem['href']
                if href.startswith('/'):
                    model_url = f"https://huggingface.co{href}"
                elif href.startswith('http'):
                    model_url = href
            
            # Extract size from description if available
            size = "Unknown"
            size_match = re.search(r'\b(\d+(\.\d+)?[BM])\b', description)
            if size_match:
                size = size_match.group(1)
            
            # Create metadata dictionary
            metadata = {
                'description': description,
                'downloads': downloads,
                'updated': updated,
                'url': model_url,
                'size': size,
                'source': 'huggingface'
            }
            
            # Create the model entry
            model_entry = {
                'id': model_id,
                'name': model_id,  # Use id as name for consistency
                'description': description,
                'downloads': downloads,
                'updated': updated,
                'url': model_url,
                'size': size,
                'source': 'huggingface',
                'metadata': metadata
            }
            
            results.append(model_entry)
        
        # Always ensure Bielik models are included
        # First, get all Bielik models from DEFAULT_HF_MODELS
        bielik_models = [m for m in DEFAULT_HF_MODELS if 'bielik' in m['id'].lower()]
        
        # Then check if they're already in the results
        existing_ids = [m['id'] for m in results]
        for bielik_model in bielik_models:
            if bielik_model['id'] not in existing_ids:
                # Add metadata if not present
                if 'metadata' not in bielik_model:
                    bielik_model['metadata'] = {
                        'description': bielik_model.get('description', ''),
                        'downloads': bielik_model.get('downloads', ''),
                        'updated': bielik_model.get('updated', ''),
                        'url': f"https://huggingface.co/{bielik_model['id']}",
                        'size': bielik_model.get('size', 'Unknown'),
                        'source': 'huggingface'
                    }
                # Add name if not present
                if 'name' not in bielik_model:
                    bielik_model['name'] = bielik_model['id']
                
                results.append(bielik_model)
                existing_ids.append(bielik_model['id'])
        
        # If we didn't find any models, use the default list
        if not results:
            # Ensure all DEFAULT_HF_MODELS have metadata
            for model in DEFAULT_HF_MODELS:
                if 'metadata' not in model:
                    model['metadata'] = {
                        'description': model.get('description', ''),
                        'downloads': model.get('downloads', ''),
                        'updated': model.get('updated', ''),
                        'url': f"https://huggingface.co/{model['id']}",
                        'size': model.get('size', 'Unknown'),
                        'source': 'huggingface'
                    }
                if 'name' not in model:
                    model['name'] = model['id']
            
            results = DEFAULT_HF_MODELS
        
        # Save to cache file
        cache_path = get_hf_models_cache_path()
        try:
            # Ensure the directory exists
            os.makedirs(os.path.dirname(cache_path), exist_ok=True)
            with open(cache_path, 'w') as f:
                json.dump(results, f, indent=2)
            
            print(f"Successfully updated HF models cache with {len(results)} models.")
            return True
        except Exception as e:
            print(f"Error saving HF models cache: {e}")
            return False
    
    except Exception as e:
        print(f"Error updating HF models cache: {e}")
        # If there was an error, ensure we at least have the default models in the cache
        try:
            cache_path = get_hf_models_cache_path()
            os.makedirs(os.path.dirname(cache_path), exist_ok=True)
            
            # Ensure all DEFAULT_HF_MODELS have metadata
            for model in DEFAULT_HF_MODELS:
                if 'metadata' not in model:
                    model['metadata'] = {
                        'description': model.get('description', ''),
                        'downloads': model.get('downloads', ''),
                        'updated': model.get('updated', ''),
                        'url': f"https://huggingface.co/{model['id']}",
                        'size': model.get('size', 'Unknown'),
                        'source': 'huggingface'
                    }
                if 'name' not in model:
                    model['name'] = model['id']
            
            with open(cache_path, 'w') as f:
                json.dump(DEFAULT_HF_MODELS, f, indent=2)
            print("Created default HF models cache.")
            return False
        except Exception as inner_e:
            print(f"Error creating default HF models cache: {inner_e}")
            return False

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
        
        # First try to update the cache, but don't fail if it doesn't work
        try:
            update_huggingface_models_cache()
        except Exception as e:
            print(f"Warning: Could not update Hugging Face models cache: {e}")
            print("Using cached or default models instead.")
        
        # Search for models with our enhanced search function
        models_list = search_huggingface_models(query)
        
        if not models_list:
            print(f"No models found matching '{query}'.")
            return None
        
        # Create choices for the questionary select
        choices = []
        for m in models_list:
            # Handle different model formats (from cache vs. direct search)
            model_id = m.get('id', m.get('name', ''))
            model_size = m.get('size', 'Unknown')
            model_desc = m.get('description', m.get('desc', ''))
            model_downloads = m.get('downloads', 'N/A')
            
            # Format the display title
            if isinstance(model_downloads, (int, float)):
                title = f"{model_id:<50} {model_size:<10} Downloads: {model_downloads:,} | {model_desc}"
            else:
                title = f"{model_id:<50} {model_size:<10} {model_desc}"
            
            choices.append(questionary.Choice(title=title, value=model_id))
        
        if not choices:
            print(f"No models found matching '{query}'.")
            return None
        
        # Add a cancel option
        choices.append(questionary.Choice(title="Cancel", value="__CANCEL__"))
        
        # Ask the user to select a model
        selected = questionary.select(
            "Select a model to install:",
            choices=choices
        ).ask()
        
        # If user selected Cancel, return early
        if selected == "__CANCEL__":
            print("Selection cancelled.")
            return None
        
        return selected
    except Exception as e:
        print(f"Error in interactive model search: {e}")
        return None

def update_models_from_huggingface(query=None, interactive=True):
    """
    Update the local models.json file with models from Hugging Face.
    First updates the HF models cache, then allows selection of models to add to the local models list.
    
    Args:
        query: The search query (e.g., "bielik"). If None and interactive is True, prompts the user.
        interactive: Whether to allow interactive selection of models.
        
    Returns:
        The updated list of models.
    """
    # First update the HF models cache
    print("Updating Hugging Face models cache...")
    success = update_huggingface_models_cache()
    if not success:
        print("Warning: Using fallback models list due to update failure.")
    
    # Check if questionary is available for interactive mode
    if interactive:
        try:
            import questionary
        except ImportError:
            print("questionary package is required for interactive mode.")
            print("Install it with: pip install questionary")
            interactive = False
    
    # Get all HF models from cache or default list
    all_hf_models = get_huggingface_models()
    
    # If query is provided, filter models
    if query:
        print(f"Filtering models matching '{query}'...")
        query = query.lower()
        filtered_models = [
            model for model in all_hf_models 
            if query in model['id'].lower() or 
               query in model.get('description', '').lower()
        ]
        models_data = filtered_models
    else:
        models_data = all_hf_models
    
    if not models_data:
        print(f"No models found matching '{query if query else 'criteria'}'.")
        return get_models()
    
    # If interactive mode, allow selection of models to add
    if interactive:
        # If no query and interactive mode, prompt for filtering
        if query is None:
            filter_query = questionary.text("Enter filter term for Hugging Face models (or leave empty for all):").ask()
            if filter_query:
                filter_query = filter_query.lower()
                models_data = [
                    model for model in models_data 
                    if filter_query in model['id'].lower() or 
                       filter_query in model.get('description', '').lower()
                ]
                if not models_data:
                    print(f"No models found matching '{filter_query}'.")
                    return get_models()
        
        choices = []
        for model in models_data:
            model_id = model.get('id', '')
            desc = model.get('description', '')[:50] + ('...' if len(model.get('description', '')) > 50 else '')
            downloads = model.get('downloads', '')
            
            choices.append(
                questionary.Choice(
                    title=f"{model_id} - {desc} ({downloads})",
                    value=model
                )
            )
        
        if not choices:
            print("No models found to add.")
            return get_models()
        
        print("\nSelect models to add to your local models list:")
        selected_models = questionary.checkbox(
            "Select models:",
            choices=choices
        ).ask()
        
        if not selected_models:
            print("No models selected.")
            return get_models()
        
        models_data = selected_models
    
    # Load existing models
    existing_models = load_models_from_json()
    existing_model_names = {m['name'] for m in existing_models}
    
    # Add new models
    new_models = []
    for model in models_data:
        model_id = model.get('id', '')
        if model_id and model_id not in existing_model_names:
            # Extract size from description if available
            size = "Unknown"
            desc = model.get('description', '')
            size_match = re.search(r'\b(\d+(\.\d+)?[BM])\b', desc)
            if size_match:
                size = size_match.group(1)
            
            new_model = {
                'name': model_id,
                'size': size,
                'desc': desc[:100] + ('...' if len(desc) > 100 else ''),
                'source': 'huggingface'
            }
            
            new_models.append(new_model)
            existing_model_names.add(model_id)  # Add to set to avoid duplicates
    
    if new_models:
        # Add new models to existing models
        existing_models.extend(new_models)
        
        # Save updated models list
        save_models_to_json(existing_models)
        
        print(f"Added {len(new_models)} new models to the local models list.")
        
        # Print the new models
        print("\nNew models added:")
        for model in new_models:
            print(f"  {model['name']:<40} {model['size']:<6} {model['desc']}")
    else:
        print("No new models added. All selected models already exist in the local list.")

    return existing_models

def update_models_from_ollama(save_to_cache=True, limit=50):
    """
    Fetch the latest coding-related models up to 7B from the Ollama library web page
    and update the local models.json file.

    Args:
        save_to_cache: Whether to save the models to the ollama_models.json cache file.
        limit: Maximum number of models to fetch

    Returns:
        The list of models from Ollama.
    """
    # Try to use the model_scrapers module first
    try:
        from .model_scrapers import scrape_ollama_models, are_scrapers_available
        if are_scrapers_available():
            print("Using model scrapers to fetch Ollama models")
            models = scrape_ollama_models(limit=limit)
            if models:
                return models
    except ImportError:
        print("Model scrapers not available, using fallback method")
        # Continue with the fallback method below
    import requests
    import re
    from bs4 import BeautifulSoup
    import json

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

                # Try to extract the model URL
                model_url = None
                link_elem = card.find('a')
                if link_elem and 'href' in link_elem.attrs:
                    href = link_elem['href']
                    if href.startswith('/'):
                        model_url = f"https://ollama.com{href}"
                    elif href.startswith('http'):
                        model_url = href

                # Extract metadata
                metadata = {
                    'size_b': size,
                    'description': description,
                    'url': model_url,
                    'source': 'ollama'
                }

                # Check if this is a coding-related model
                is_coding = any(keyword in description.lower() for keyword in ['code', 'program', 'develop', 'python', 'javascript', 'java', 'c++', 'typescript'])

                # Check if this is a small enough model (up to 7B)
                is_small = True  # Default to True
                if size.endswith('B'):
                    try:
                        size_value = float(size[:-1])
                        is_small = size_value <= 7.0
                    except ValueError:
                        pass  # If we can't parse the size, assume it's small enough

                # Only add coding-related models up to 7B
                if is_small and (is_coding or 'code' in model_name.lower()):
                    models.append({
                        'name': model_name,
                        'size': size,
                        'desc': description,
                        'url': model_url,
                        'source': 'ollama',
                        'metadata': metadata
                    })
            except Exception as e:
                print(f"Error processing model card: {e}")
                continue

        # Save to ollama_models.json cache file if requested
        if save_to_cache and models:
            try:
                cache_path = get_ollama_models_cache_path()
                os.makedirs(os.path.dirname(cache_path), exist_ok=True)
                with open(cache_path, 'w') as f:
                    json.dump(models, f, indent=2)
                print(f"Saved {len(models)} Ollama models to cache file.")
            except Exception as e:
                print(f"Error saving Ollama models to cache: {e}")

        # If we found models, also update the models.json file
        if models:
            # Load existing models
            existing_models = load_models_from_json()

            # Create a set of existing model names for quick lookup
            existing_model_names = {m['name'] for m in existing_models}

            # Add new models that don't already exist
            for model in models:
                if model['name'] not in existing_model_names:
                    # Create a simplified version for models.json
                    simple_model = {
                        'name': model['name'],
                        'size': model['size'],
                        'desc': model['desc'],
                        'source': 'ollama'
                    }
                    existing_models.append(simple_model)
                    existing_model_names.add(model['name'])

            # Save the updated models list
            save_models_to_json(existing_models)

            print(f"Updated models list with {len(models)} models from Ollama library.")
            return models
        else:
            print("No models found on Ollama library page.")
            return load_ollama_models_from_cache() or []

        # Save the updated models to the JSON file
        save_models_to_json(models)
        
        print(f"Updated models.json with {len(models)} models from Ollama library")
        return models
    except Exception as e:
        print(f"Error updating models from Ollama: {e}")
        return load_ollama_models_from_cache() or DEFAULT_MODELS


def load_ollama_models_from_cache():
    """
    Load Ollama models from the cache file.
    
    Returns:
        A list of Ollama models, or an empty list if the cache file doesn't exist or is invalid.
    """
    try:
        cache_path = get_ollama_models_cache_path()
        if os.path.exists(cache_path):
            with open(cache_path, 'r') as f:
                return json.load(f)
        return []
    except Exception as e:
        print(f"Error loading Ollama models from cache: {e}")
        return []


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
