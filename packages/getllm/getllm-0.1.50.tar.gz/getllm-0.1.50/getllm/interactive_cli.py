from getllm import models
import questionary
import sys

MENU_OPTIONS = [
    ("List available models", "list"),
    ("Show default model", "default"),
    ("List installed models", "installed"),
    ("Install model (select from list)", "wybierz-model"),
    ("Search Hugging Face models", "search-hf"),
    ("Set default model (select from list)", "wybierz-default"),
    ("Generate code (interactive)", "generate"),
    ("Update models list from ollama.com", "update"),
    ("Update models list from Hugging Face", "update-hf"),
    ("Test default model", "test"),
    ("Exit", "exit")
]

INTRO = """
GetLLM Interactive Mode
Use arrow keys to navigate, Enter to select, or type a command (e.g., install <model>)
"""

def choose_model(action_desc, callback):
    models_list = models.get_models()
    choices = [
        questionary.Choice(
            title=f"{m.get('name','-'):<25} {m.get('size','') or m.get('size_b','')}  {m.get('desc','')}",
            value=m['name']
        ) for m in models_list
    ]
    answer = questionary.select(
        f"Select model to {action_desc}:", choices=choices
    ).ask()
    if answer:
        callback(answer)
    else:
        print("Selection cancelled.")

def generate_code_interactive(mock_mode=False):
    """Interactive code generation function"""
    from getllm.cli import get_template, extract_python_code, execute_code, save_code_to_file
    from getllm.ollama_integration import get_ollama_integration
    import platform
    
    # Mock implementation for testing without Ollama
    if mock_mode:
        from getllm.cli import MockOllamaIntegration
        runner = MockOllamaIntegration()
        print("Using mock mode (no Ollama required)")
    else:
        # Get the default model
        model = models.get_default_model()
        if not model:
            print("No default model set. Please set a default model first.")
            return
        runner = get_ollama_integration(model=model)
    
    # Get the prompt from the user
    prompt = questionary.text("Enter your code generation prompt:").ask()
    if not prompt:
        print("Cancelled.")
        return
    
    # Choose template
    template_choices = [
        "basic", "platform_aware", "dependency_aware", 
        "testable", "secure", "performance", "pep8"
    ]
    template = questionary.select(
        "Select template:",
        choices=template_choices,
        default="platform_aware"
    ).ask()
    if not template:
        print("Cancelled.")
        return
    
    # Get dependencies if using dependency_aware template
    dependencies = None
    if template == "dependency_aware":
        dependencies = questionary.text(
            "Enter dependencies (comma-separated):"
        ).ask()
    
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
    
    # Ask if the user wants to save the code
    save = questionary.confirm("Save the code to a file?", default=False).ask()
    if save:
        code_file = save_code_to_file(code)
        print(f"\nCode saved to: {code_file}")
    
    # Ask if the user wants to run the code
    run = questionary.confirm("Run the generated code?", default=False).ask()
    if run:
        print("\nRunning the generated code...")
        result = execute_code(code)
        if result["error"]:
            print(f"Error running code: {result['error']}")
        else:
            print("Code execution result:")
            print(result["output"])

def interactive_shell(mock_mode=False):
    print(INTRO)
    if mock_mode:
        print("Running in mock mode (no Ollama required)")
    
    while True:
        answer = questionary.select(
            "Select an action from the menu:",
            choices=[questionary.Choice(title=desc, value=cmd) for desc, cmd in MENU_OPTIONS]
        ).ask()
        if not answer:
            print("Cancelled or exiting menu.")
            break
        cmd = answer
        args = cmd.split()
        if args[0] == "exit" or args[0] == "quit": 
            print("Exiting interactive mode.")
            break
        elif args[0] == "list":
            models_list = models.get_models()
            print("\nAvailable models:")
            for m in models_list:
                print(f"  {m.get('name', '-'):<25} {m.get('size','') or m.get('size_b','')}  {m.get('desc','')}")
        elif args[0] == "install" and len(args) > 1:
            models.install_model(args[1])
        elif args[0] == "installed":
            models.list_installed_models()
        elif args[0] == "set-default" and len(args) > 1:
            models.set_default_model(args[1])
        elif args[0] == "default":
            print("Default model:", models.get_default_model())
        elif args[0] == "update":
            models.update_models_from_ollama()
        elif args[0] == "test":
            default = models.get_default_model()
            print(f"Test default model: {default}")
            if default:
                print("OK: Default model is set.")
            else:
                print("ERROR: Default model is NOT set!")
        elif args[0] == "wybierz-model":
            choose_model("install", models.install_model)
        elif args[0] == "wybierz-default":
            choose_model("set as default", models.set_default_model)
        elif args[0] == "search-hf":
            # Search for models on Hugging Face
            from getllm.models import interactive_model_search
            query = questionary.text("Enter search term for Hugging Face models:").ask()
            if query:
                selected_model = interactive_model_search(query)
                if selected_model:
                    # Ask if the user wants to install the model
                    install_now = questionary.confirm("Do you want to install this model now?", default=True).ask()
                    if install_now:
                        models.install_model(selected_model)
        elif args[0] == "update-hf":
            # Update models from Hugging Face
            from getllm.models import update_models_from_huggingface
            print("Updating models from Hugging Face...")
            update_models_from_huggingface()
        elif args[0] == "generate":
            generate_code_interactive(mock_mode=mock_mode)
        else:
            print("Unknown command. Available: list, install <model>, installed, set-default <model>, default, update, update-hf, test, wybierz-model, search-hf, wybierz-default, generate, exit")

if __name__ == "__main__":
    # Check if mock mode is requested
    mock_mode = "--mock" in sys.argv
    interactive_shell(mock_mode=mock_mode)
