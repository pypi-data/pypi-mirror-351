import shutil
import os
import sys
import click
from colorama import init, Fore
import yaml
import getpass

def snake_to_pascal(s):
    return ''.join(part.capitalize() for part in s.split('_'))

@click.group()
def cli():
    """
    TkinterCLI est un outil en ligne de commande permettant de simplfier la création de projet avec Tkinter.

    -> https://github.com/Albatros329/tkintercli
    """
    pass

@cli.group()
def add():
    """Groupe de commandes pour ajouter des éléments dans un projet TkinterCLI."""
    pass


@cli.command()
@click.argument("name")
@click.option("--venv", is_flag=True, help="Créer un environnement virtuel dans le projet.")
def new(name, venv):
    """Créer un projet"""

    if not os.path.exists(f"{PATH}\\{name}"):
        shutil.copytree(f"{PATH_TKINTERCLI}\\model", f"{PATH}\\{name}")

        with open(f"{PATH}\\{name}\\conf\\app.conf", "r+", encoding="utf-8") as f:
            data = yaml.safe_load(f)
            data["DEFAULT"]["app_name"] = name
            data["DEFAULT"]["author"] = getpass.getuser()
            f.seek(0)
            yaml.dump(data, f)
            f.close()

        with open(f"{PATH}\\{name}\\build.bat", "r+", encoding="utf-8") as f:
            data = f.read()
            f.seek(0)
            f.write(data.replace("MyApp", name))
            f.close()

        if venv:
            print(Fore.BLUE + "Création de l'environnement virtuel...")
            os.system(f'python -m venv "{PATH}\\{name}\\venv"')


        print(Fore.GREEN + f"Succès: Le projet {name} a été créé.")
    else:
        print(Fore.RED + "Erreur: dossier déjà existant.")


@add.command()
@click.argument("name")
def page(name):
    """Créer une nouvelle page"""
    if os.path.exists(f"{PATH}\\pages"):
        if not os.path.exists(f"{PATH}\\pages\\{name}.py"):
            name = name.lower()
            shutil.copy(f"{PATH_TKINTERCLI}\\model\\pages\\demo.py", f"{PATH}\\pages\\{name}.py")

            with open(f"{PATH}\\pages\\{name}.py", "r+", encoding="utf-8") as f:
                data = f.read()
                f.seek(0)
                f.write(data.replace("Demo", snake_to_pascal(name)))
                f.close()

            print(Fore.GREEN + f"Succès: La page {name} a été créée.")
        else:
            print(Fore.YELLOW + "Erreur: cette page existe déjà.")
    else:
        print(Fore.RED + "Erreur: cette commande est uniquement disponible dans les projets tkintercli")



def main():
    """Fonction principale appelée lors de l'exécution de la commande tkintercli"""
    init(autoreset=True)

    global PATH, PATH_TKINTERCLI
    PATH = os.getcwd()
    PATH_TKINTERCLI = os.path.dirname(os.path.abspath(__file__))


    cli()


if __name__ == '__main__':
    main()
