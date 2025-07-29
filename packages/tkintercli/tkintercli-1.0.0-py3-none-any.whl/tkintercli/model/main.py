"""
##############################################################################
#                                                                            #
#                  Projet généré avec TkinterCLI                             #
#                                                                            #
#  TkinterCLI est un outil en ligne de commande permettant de simplifier     #
#  la création de projets Tkinter avec une architecture organisée.           #
#                                                                            #
#                                                                            #
#  GitHub: https://github.com/Albatros329/tkintercli                         #
#                                                                            #
##############################################################################
"""

import tkinter as tk
from tkinter import ttk
from tkinter.messagebox import showerror
import yaml
import os
import sys
from utils.pagesLoader import chargerPages

class Application:
    def __init__(self, root):
        self.root = root


        # Chemin & config
        if getattr(sys, 'frozen', False):
            self.PATH = os.path.join(sys._MEIPASS + "\\\\")  # type: ignore
        else:
            self.PATH = os.getcwd()

        self.CONFIG = yaml.safe_load(open(f"{self.PATH}/conf/app.conf"))


        # Propriétés de la fenêtre
        self.root.title(self.CONFIG['DEFAULT']['app_name'])
        self.root.iconbitmap(f"{self.PATH}/ressources/images/logo.ico")
        self.root.geometry("800x600")

        # Conteneur principal
        container = tk.Frame(self.root)
        container.pack(fill="both", expand=True)

        self.pages = {}

        for PageClasse in chargerPages():
            nom = PageClasse.__name__
            page = PageClasse(container, self)
            self.pages[nom] = page
            page.grid(row=0, column=0, sticky="nsew")


        self.show_page("Demo")  # Display the first page



    def show_page(self, nom_page):
        """
        Changer la page actuellement affichée.
        """
        if nom_page in self.pages:
            self.pages[nom_page].tkraise()
        else:
            showerror("Erreur", f"Page non trouvée: {nom_page}")



if __name__ == "__main__":
    root = tk.Tk()
    app = Application(root)
    root.mainloop()
