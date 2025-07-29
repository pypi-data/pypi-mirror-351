import argparse
from pyllm import models

def main():
    parser = argparse.ArgumentParser(description="pyllm CLI - zarządzanie modelami LLM (Ollama)")
    parser.add_argument("-i", "--interactive", action="store_true", help="Uruchom w trybie interaktywnym (shell)")
    subparsers = parser.add_subparsers(dest="command")

    # List available models
    subparsers.add_parser("list", help="Wyświetl dostępne modele (z models.json)")
    # Install model
    parser_install = subparsers.add_parser("install", help="Pobierz model przez ollama")
    parser_install.add_argument("model", help="Nazwa modelu do pobrania")
    # List installed models
    subparsers.add_parser("installed", help="Wyświetl zainstalowane modele (ollama list)")
    # Set default model
    parser_setdef = subparsers.add_parser("set-default", help="Ustaw domyślny model")
    parser_setdef.add_argument("model", help="Nazwa modelu do ustawienia jako domyślny")
    # Show default model
    subparsers.add_parser("default", help="Pokaż domyślny model")
    # Update models from Ollama
    subparsers.add_parser("update", help="Aktualizuj listę modeli z ollama.com/library")
    # Test default model
    subparsers.add_parser("test", help="Przetestuj domyślny model (wypisz jego nazwę i sprawdź czy nie jest pusty)")
    # Interactive mode as subcommand
    subparsers.add_parser("interactive", help="Uruchom tryb interaktywny (shell)")

    args = parser.parse_args()

    # Tryb interaktywny przez -i lub komendę 'interactive'
    if getattr(args, "interactive", False) or args.command == "interactive":
        from pyllm.interactive_cli import interactive_shell
        interactive_shell()
        return

    if args.command == "list":
        models_list = models.get_models()
        print("\nDostępne modele:")
        for m in models_list:
            print(f"  {m.get('name', '-'):<25} {m.get('size','') or m.get('size_b','')}  {m.get('desc','')}")
    elif args.command == "install":
        models.install_model(args.model)
    elif args.command == "installed":
        models.list_installed_models()
    elif args.command == "set-default":
        models.set_default_model(args.model)
    elif args.command == "default":
        print("Domyślny model:", models.get_default_model())
    elif args.command == "update":
        models.update_models_from_ollama()
    elif args.command == "test":
        default = models.get_default_model()
        print(f"Test domyślnego modelu: {default}")
        if default:
            print("OK: Domyślny model jest ustawiony.")
        else:
            print("BŁĄD: Domyślny model NIE jest ustawiony!")
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
