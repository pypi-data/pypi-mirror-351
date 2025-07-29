#!/usr/bin/env python3

import argparse
import sys
import os
import re
import tempfile
import platform
from pathlib import Path

# Import from getllm modules
from getllm import models
from getllm.ollama_integration import OllamaIntegration, get_ollama_integration

# Create .getllm directory if it doesn't exist
PACKAGE_DIR = os.path.join(os.path.expanduser('~'), '.getllm')
os.makedirs(PACKAGE_DIR, exist_ok=True)

# Configure logging
import logging
logger = logging.getLogger('getllm.cli')

# Template functions for code generation
def get_template(prompt, template_type, **kwargs):
    """Get a template for code generation based on the template type."""
    templates = {
        "basic": """Generate Python code for the following task: {prompt}""",
        
        "platform_aware": """Generate Python code for the following task: {prompt}

The code should run on {platform} operating system.
{dependencies}""",
        
        "dependency_aware": """Generate Python code for the following task: {prompt}

Use only the following dependencies: {dependencies}""",
        
        "testable": """Generate Python code for the following task: {prompt}

Include unit tests for the code.
{dependencies}""",
        
        "secure": """Generate secure Python code for the following task: {prompt}

Ensure the code follows security best practices and handles errors properly.
{dependencies}""",
        
        "performance": """Generate high-performance Python code for the following task: {prompt}

Optimize the code for performance.
{dependencies}""",
        
        "pep8": """Generate Python code for the following task: {prompt}

Ensure the code follows PEP 8 style guidelines.
{dependencies}""",
        
        "debug": """Debug the following Python code that has an error:

```python
{code}
```

Error message:
{error_message}

Fix the code to solve the problem and provide the corrected version."""
    }
    
    # Get the template or use basic if not found
    template = templates.get(template_type, templates["basic"])
    
    # Format dependencies if provided
    if "dependencies" in kwargs:
        if kwargs["dependencies"]:
            kwargs["dependencies"] = f"Use the following dependencies: {kwargs['dependencies']}"
        else:
            kwargs["dependencies"] = "Use standard Python libraries."
    else:
        kwargs["dependencies"] = "Use standard Python libraries."
    
    # Format the template with the provided arguments
    return template.format(prompt=prompt, **kwargs)

# Sandbox classes for code execution
class PythonSandbox:
    """Simple implementation of PythonSandbox."""
    def __init__(self):
        pass
    
    def run(self, code):
        """Run Python code in a sandbox."""
        # Create a temporary file to store the code
        with tempfile.NamedTemporaryFile(suffix='.py', delete=False) as f:
            f.write(code.encode('utf-8'))
            temp_file = f.name
        
        try:
            # Run the code in a separate process
            import subprocess
            result = subprocess.run(
                [sys.executable, temp_file],
                capture_output=True,
                text=True,
                timeout=30  # 30 second timeout
            )
            
            # Return the result
            if result.returncode == 0:
                return {
                    "output": result.stdout,
                    "error": None
                }
            else:
                return {
                    "output": result.stdout,
                    "error": result.stderr
                }
        except Exception as e:
            return {
                "output": "",
                "error": str(e)
            }
        finally:
            # Clean up the temporary file
            try:
                os.unlink(temp_file)
            except:
                pass

# Mock implementation for testing without Ollama
class MockOllamaIntegration:
    """Mock implementation of OllamaIntegration for testing."""
    def __init__(self, model=None):
        self.model = model or "mock-model"
    
    def query_ollama(self, prompt, template_type=None, **template_args):
        """Mock implementation of query_ollama."""
        if "hello world" in prompt.lower():
            return "print('Hello, World!')"
        elif "binary search tree" in prompt.lower():
            return """
class Node:
    def __init__(self, value):
        self.value = value
        self.left = None
        self.right = None

class BinarySearchTree:
    def __init__(self):
        self.root = None
    
    def insert(self, value):
        if self.root is None:
            self.root = Node(value)
        else:
            self._insert_recursive(self.root, value)
    
    def _insert_recursive(self, node, value):
        if value < node.value:
            if node.left is None:
                node.left = Node(value)
            else:
                self._insert_recursive(node.left, value)
        else:
            if node.right is None:
                node.right = Node(value)
            else:
                self._insert_recursive(node.right, value)
    
    def search(self, value):
        return self._search_recursive(self.root, value)
    
    def _search_recursive(self, node, value):
        if node is None or node.value == value:
            return node
        if value < node.value:
            return self._search_recursive(node.left, value)
        return self._search_recursive(node.right, value)

# Example usage
bst = BinarySearchTree()
bst.insert(5)
bst.insert(3)
bst.insert(7)
bst.insert(2)
bst.insert(4)

print("Searching for 4:", bst.search(4).value if bst.search(4) else "Not found")
print("Searching for 6:", bst.search(6).value if bst.search(6) else "Not found")
"""
        else:
            return f"# Mock code for: {prompt}\nprint('This is mock code generated for testing')\n"
    
    def extract_python_code(self, text):
        """Mock implementation of extract_python_code."""
        return text

# Helper functions
def save_code_to_file(code, filename=None):
    """Save the generated code to a file."""
    if filename is None:
        import time
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(PACKAGE_DIR, f"generated_script_{timestamp}.py")
    
    # Ensure the target directory exists
    os.makedirs(os.path.dirname(os.path.abspath(filename)), exist_ok=True)
    
    with open(filename, "w", encoding="utf-8") as f:
        f.write(code)
    
    logger.info(f'Saved script to file: {filename}')
    return os.path.abspath(filename)

def execute_code(code, use_docker=False):
    """Execute the generated code and return the result."""
    # Create the sandbox
    sandbox = PythonSandbox()
    
    # Execute the code
    return sandbox.run(code)

def extract_python_code(text):
    """Extract Python code from the response."""
    # If the response already looks like code (no markdown), return it
    if text.strip().startswith("import ") or text.strip().startswith("#") or text.strip().startswith("def ") or text.strip().startswith("class ") or text.strip().startswith("print"):
        return text
        
    # Look for Python code blocks in markdown
    import re
    code_block_pattern = r"```(?:python)?\s*([\s\S]*?)```"
    matches = re.findall(code_block_pattern, text)
    
    if matches:
        # Return the first code block found
        return matches[0].strip()
    
    # If no code blocks found but the text contains "print hello world" or similar
    if "print hello world" in text.lower() or "print(\"hello world\")" in text.lower() or "print('hello world')" in text.lower():
        return "print(\"Hello, World!\")"
    
    # If all else fails, return the original text with a warning
    return """# Could not extract Python code from the model response
# Here's a simple implementation:

print("Hello, World!")

# Original response:
# """ + text

def check_ollama():
    """Check if Ollama is running and return its version."""
    try:
        # Try to connect to the Ollama API
        import requests
        response = requests.get("http://localhost:11434/api/version", timeout=2)
        if response.status_code == 200:
            return response.json().get("version", "unknown")
        return None
    except Exception:
        return None

def interactive_mode(mock_mode=False):
    """Run in interactive mode, allowing the user to input prompts."""
    from getllm.interactive_cli import interactive_shell
    interactive_shell(mock_mode=mock_mode)

def main():
    """Main entry point for the getllm CLI."""
    # First check for direct prompts
    direct_prompt = False
    prompt = None
    args_to_parse = sys.argv[1:]
    
    # Check if the first argument is a command or looks like a prompt
    commands = ["code", "list", "install", "installed", "set-default", "default", "update", "test", "interactive"]
    
    # Special handling for -search command (common user error)
    if len(args_to_parse) >= 2 and args_to_parse[0] == "-search":
        # Convert to proper format
        args_to_parse[0] = "--search"
    
    if len(args_to_parse) > 0 and not args_to_parse[0].startswith('-') and args_to_parse[0] not in commands:
        # This is a direct prompt
        direct_prompt = True
        prompt_parts = []
        options = []
        
        # Separate prompt parts from options
        i = 0
        while i < len(args_to_parse):
            if args_to_parse[i].startswith('-'):
                options.append(args_to_parse[i])
                # If this option takes a value, add it too
                if i + 1 < len(args_to_parse) and not args_to_parse[i+1].startswith('-'):
                    if args_to_parse[i] in ["-m", "--model", "-t", "--template", "-d", "--dependencies"]:
                        options.append(args_to_parse[i+1])
                        i += 1
            else:
                prompt_parts.append(args_to_parse[i])
            i += 1
        
        # Combine prompt parts
        prompt = " ".join(prompt_parts)
        
        # Parse just the options
        args_to_parse = options
    
    # Create the argument parser
    parser = argparse.ArgumentParser(description="getllm CLI - LLM Model Management and Code Generation")
    
    # Global options
    parser.add_argument("-i", "--interactive", action="store_true", help="Run in interactive mode")
    parser.add_argument("--mock", action="store_true", help="Use mock mode (no Ollama required)")
    parser.add_argument("-m", "--model", help="Name of the Ollama model to use")
    parser.add_argument("-t", "--template", 
                        choices=["basic", "platform_aware", "dependency_aware", "testable", "secure", "performance", "pep8"],
                        default="platform_aware",
                        help="Type of template to use")
    parser.add_argument("-d", "--dependencies", help="List of allowed dependencies (only for template=dependency_aware)")
    parser.add_argument("-s", "--save", action="store_true", help="Save the generated code to a file")
    parser.add_argument("-r", "--run", action="store_true", help="Run the generated code after creation")
    parser.add_argument("--search", metavar="QUERY", help="Search for models on Hugging Face matching the query")
    # Add a separate search command for better CLI experience
    parser.add_argument("-S", "--find-model", dest="search", metavar="QUERY", help="Alias for --search")
    parser.add_argument("--update-hf", action="store_true", help="Update models list from Hugging Face")
    
    # Only add subparsers if not using direct prompt
    if not direct_prompt:
        # Subcommands
        subparsers = parser.add_subparsers(dest="command")
        
        # Code generation command
        code_parser = subparsers.add_parser("code", help="Generate Python code using LLM models")
        code_parser.add_argument("prompt", nargs="+", help="Task to be performed by Python code")
        
        # Model management commands
        subparsers.add_parser("list", help="List available models (from models.json)")
        parser_install = subparsers.add_parser("install", help="Install a model using Ollama")
        parser_install.add_argument("model", help="Name of the model to install")
        subparsers.add_parser("installed", help="List installed models (ollama list)")
        parser_setdef = subparsers.add_parser("set-default", help="Set the default model")
        parser_setdef.add_argument("model", help="Name of the model to set as default")
        subparsers.add_parser("default", help="Show the default model")
        subparsers.add_parser("update", help="Update the list of models from ollama.com/library")
        subparsers.add_parser("test", help="Test the default model")
        subparsers.add_parser("interactive", help="Run in interactive mode")
    
    # Parse the arguments
    if direct_prompt:
        # For direct prompt, parse only the options
        args = parser.parse_args(args_to_parse)
        args.command = None  # No command when using direct prompt
    else:
        # Normal parsing for commands
        args = parser.parse_args()
        if args.command == "code":
            prompt = " ".join(args.prompt)
    
    # Handle Hugging Face model search
    if args.search or args.update_hf:
        from getllm.models import update_models_from_huggingface, interactive_model_search
        
        if args.search:
            # Search for models on Hugging Face
            print(f"Searching for models matching '{args.search}' on Hugging Face...")
            
            # If in mock mode, skip Ollama checks entirely
            if args.mock:
                print("\nRunning in mock mode - Ollama checks bypassed")
                selected_model = interactive_model_search(args.search, check_ollama=False)
            else:
                selected_model = interactive_model_search(args.search, check_ollama=True)
            if selected_model:
                # Ask if the user wants to install the model
                import questionary
                install_now = questionary.confirm("Do you want to install this model now?", default=True).ask()
                if install_now:
                    # Check if we're in mock mode
                    if args.mock:
                        print(f"\nUsing mock mode. Model installation is simulated.")
                        print(f"Model '{selected_model}' would be installed in normal mode.")
                    else:
                        from getllm.models import install_model
                        success = install_model(selected_model)
                        
                        if not success:
                            print("\nWould you like to continue in mock mode instead?")
                            continue_mock = questionary.confirm("Continue with mock mode?", default=True).ask()
                            if continue_mock:
                                print(f"\nContinuing in mock mode with model '{selected_model}'")
                                # Set up mock environment
                                os.environ['GETLLM_MOCK_MODEL'] = selected_model
            else:
                print("Search cancelled or no model selected.")
        else:  # args.update_hf
            # Update models from Hugging Face
            print("Updating models from Hugging Face...")
            update_models_from_huggingface()
        
        return 0
        
    # Handle interactive mode
    if args.interactive or args.command == "interactive":
        interactive_mode(mock_mode=args.mock)
        return 0
    
    # Handle model management commands
    if args.command in ["list", "install", "installed", "set-default", "default", "update", "test"]:
        if args.command == "list":
            models_list = models.get_models()
            print("\nAvailable models:")
            for m in models_list:
                print(f"  {m.get('name', '-'):<25} {m.get('size','') or m.get('size_b','')}  {m.get('desc','')}")
        elif args.command == "install":
            models.install_model(args.model)
        elif args.command == "installed":
            models.list_installed_models()
        elif args.command == "set-default":
            models.set_default_model(args.model)
        elif args.command == "default":
            print("Default model:", models.get_default_model())
        elif args.command == "update":
            models.update_models_from_ollama()
        elif args.command == "test":
            default = models.get_default_model()
            print(f"Test default model: {default}")
            if default:
                print("OK: Default model is set.")
            else:
                print("ERROR: Default model is NOT set!")
        return 0
    
    # If we have a prompt, generate code
    if prompt:
        # Get model and template
        model = args.model
        template = args.template or "platform_aware"
        dependencies = args.dependencies
        save = args.save
        run = args.run
        mock_mode = args.mock
        
        # Check if Ollama is running (unless in mock mode)
        if not mock_mode:
            ollama_version = check_ollama()
            if not ollama_version:
                print("Ollama is not running. Please start Ollama with 'ollama serve' and try again.")
                print("Alternatively, use --mock for testing without Ollama.")
                return 1
        
        # Create OllamaIntegration or MockOllamaIntegration
        if mock_mode:
            print("Using mock mode (no Ollama required)")
            runner = MockOllamaIntegration(model=model)
        else:
            runner = get_ollama_integration(model=model)
        
        # Prepare template arguments
        template_args = {}
        if dependencies:
            template_args["dependencies"] = dependencies
        
        # Add platform information for platform_aware template
        if template == "platform_aware":
            template_args["platform"] = platform.system()
        
        # Generate code
        print(f"\nGenerating code with model: {runner.model}")
        print(f"Using template: {template}")
        code = runner.query_ollama(prompt, template_type=template, **template_args)
        
        # Extract Python code if needed
        if hasattr(runner, "extract_python_code") and callable(getattr(runner, "extract_python_code")):
            code = runner.extract_python_code(code)
        else:
            code = extract_python_code(code)
        
        # Display the generated code
        print("\nGenerated Python code:")
        print("-" * 40)
        print(code)
        print("-" * 40)
        
        # Save the code if requested
        if save:
            code_file = save_code_to_file(code)
            print(f"\nCode saved to: {code_file}")
        
        # Run the code if requested
        if run:
            print("\nRunning the generated code...")
            result = execute_code(code)
            if result["error"]:
                print(f"Error running code: {result['error']}")
            else:
                print("Code execution result:")
                print(result["output"])
        
        return 0
    
    # If no command or prompt, show help
    parser.print_help()
    return 1

if __name__ == "__main__":
    main()
