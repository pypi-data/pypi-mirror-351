import tkinter as tk
from tkintercli import geticon

class Demo(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller # Récuperer les variables et fonctions stockées dans le main.py de votre projet

        self.icon = geticon("accessibility", width=16, height=16)
        
        tk.Label(self, text="Hello world !", compound="left", image=self.icon).pack()
