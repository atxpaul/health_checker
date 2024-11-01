import os
import requests
import json
import questionary
from rich import print
from rich.console import Console
from rich.markup import escape

SERVERS_FILE = 'servers.json'

console = Console()

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def load_servers():
    try:
        with open(SERVERS_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}
    
def save_servers(servers):
    with open(SERVERS_FILE,'w') as f:
        json.dump(servers, f, indent=4)

def check_status(url):
    try:
        response = requests.get(url, timeout=5)
        return response.status_code == 200
    except requests.RequestException:
        return False

def main():
    servers = load_servers()

    if not servers:
        print("[yellow]No se encontraron servidores guardados. Añade uno nuevo para comenzar[/yellow]")
        add_new_server(servers)
    else:
        action = questionary.select(
            "Qué te gustaría hacer",
            choices=[
                "Comprobar todos los servidores",
                "Comprobar servidores específicos",
                "Añadir un nuevo servidor"
            ]
        ).ask()

        if action == "Comprobar todos los servidores":
            clear_screen()
            check_all_servers(servers)
        elif action == "Comprobar servidores específicos":
            clear_screen()
            check_selected_servers(servers)
        elif action == "Añadir un nuevo servidor":
            clear_screen()
            add_new_server(servers)

def add_new_server(servers):
    url = questionary.text("Introduce la URL del nuevo servidor").ask()
    alias = questionary.text("Introduce un alias para el servidor (opcional)").ask() or url

    print(f"Realizando comprobación del servidor {alias}...")
    with console.status(f"[bold green]Comprobando {alias}...", spinner="dots"):
        status = check_status(url)
        show_status(alias, url, status)

    if status:
        servers[alias] = url
        save_servers(servers)
        print("[green]Servidor añadido existosamente[/green]")
    else:
        save_anyway = questionary.confirm(
            f"El servidor {alias} no está respondiendo, ¿quieres guardarlo de todas formas?"
        ).ask()
        if save_anyway:
            servers[alias]=url
            save_servers(servers)
            print("[yellow]Servidor guardado, aunque no responde actualmente[/yellow]")

def show_status(alias, url, status):
    if status:
        console.print(f"{alias} ({escape(url)}) [green]✓[/green]")
    else:
        console.print(f"{alias} ({escape(url)}) [red]✗[/red]")


def check_all_servers(servers):
    for alias, url, in servers.items():
        with console.status(f"[bold green]Comprobando {alias}...", spinner="dots"):
            status = check_status(url)
            show_status(alias, url, status)
        
def check_selected_servers(servers):
    choices = [f"{alias} ({url})" for alias, url, in servers.items()]
    selected = questionary.checkbox("Selecciona los servidores a comprobar",
                                    choices=choices).ask()
    selected_urls = [servers[alias.split()[0]] for alias in selected]

    for alias, url in servers.items():
        if url in selected_urls:
            with console.status(f"[bold green]Comprobando {alias}...", spinner="dots"):
                status = check_status(url)
                show_status(alias, url, status)

if __name__ == "__main__":
    main()