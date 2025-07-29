import os, importlib

def snake_to_pascal(s):
    return ''.join(part.capitalize() for part in s.split('_'))

def chargerPages(dossier="pages"):
    classes = []
    chemin_absolu = os.path.join(os.path.dirname(__file__), "..", dossier)
    for fichier in os.listdir(chemin_absolu):
        if fichier.endswith(".py") and not fichier.startswith("_"):
            nom_module = fichier[:-3]
            nom_classe = snake_to_pascal(nom_module)
            module = importlib.import_module(f"{dossier}.{nom_module}")
            classe = getattr(module, nom_classe)
            classes.append(classe)
    return classes