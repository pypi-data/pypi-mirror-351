from getllm import models
import questionary

MENU_OPTIONS = [
    ("Wyświetl dostępne modele", "list"),
    ("Wyświetl domyślny model", "default"),
    ("Wyświetl zainstalowane modele", "installed"),
    ("Zainstaluj model (wybierz z listy)", "wybierz-model"),
    ("Ustaw domyślny model (wybierz z listy)", "wybierz-default"),
    ("Aktualizuj listę modeli z ollama.com", "update"),
    ("Test domyślnego modelu", "test"),
    ("Wyjdź", "exit")
]

INTRO = """
Tryb interaktywny getllm
Poruszaj się po menu strzałkami, zatwierdzaj Enterem lub wpisz komendę (np. install <model>)
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
        f"Wybierz model do {action_desc}:", choices=choices
    ).ask()
    if answer:
        callback(answer)
    else:
        print("Przerwano wybór.")

def interactive_shell():
    print(INTRO)
    while True:
        answer = questionary.select(
            "Wybierz akcję z menu:",
            choices=[questionary.Choice(title=desc, value=cmd) for desc, cmd in MENU_OPTIONS]
        ).ask()
        if not answer:
            print("Przerwano lub wyjście z menu.")
            break
        cmd = answer
        args = cmd.split()
        if args[0] == "exit" or args[0] == "quit": 
            print("Wyjście z trybu interaktywnego.")
            break
        elif args[0] == "list":
            models_list = models.get_models()
            print("\nDostępne modele:")
            for m in models_list:
                print(f"  {m.get('name', '-'):<25} {m.get('size','') or m.get('size_b','')}  {m.get('desc','')}")
        elif args[0] == "install" and len(args) > 1:
            models.install_model(args[1])
        elif args[0] == "installed":
            models.list_installed_models()
        elif args[0] == "set-default" and len(args) > 1:
            models.set_default_model(args[1])
        elif args[0] == "default":
            print("Domyślny model:", models.get_default_model())
        elif args[0] == "update":
            models.update_models_from_ollama()
        elif args[0] == "test":
            default = models.get_default_model()
            print(f"Test domyślnego modelu: {default}")
            if default:
                print("OK: Domyślny model jest ustawiony.")
            else:
                print("BŁĄD: Domyślny model NIE jest ustawiony!")
        elif args[0] == "wybierz-model":
            choose_model("pobrania", models.install_model)
        elif args[0] == "wybierz-default":
            choose_model("ustawienia jako domyślny", models.set_default_model)
        else:
            print("Nieznana komenda. Dostępne: list, install <model>, installed, set-default <model>, default, update, test, wybierz-model, wybierz-default, exit")

if __name__ == "__main__":
    interactive_shell()
