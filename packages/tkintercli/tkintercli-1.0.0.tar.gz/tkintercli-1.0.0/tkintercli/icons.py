import os
import re
from PIL import Image, ImageTk
import io
import subprocess
import tempfile

def geticon(name, color="black", width=16, height=16):
    """
    Récupère une icône SVG du package et la colorise
    
    Args:
        name (str): Nom du fichier SVG sans extension
        color (str, optional): Couleur de l'icône (white, black, red, blue, green). Par défaut "black".
        width (int, optional): Largeur souhaitée. Par défaut 16.
        height (int, optional): Hauteur souhaitée. Par défaut 16.
    
    Returns:
        ImageTk.PhotoImage: L'image prête à être utilisée dans Tkinter
    """
    valid_colors = ["white", "black", "red", "blue", "green", "purple", "yellow"]

    if not color in valid_colors:
        raise ValueError("Couleur invalide.")
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    icons_dir = os.path.join(current_dir, "icons")
    
    if not os.path.exists(icons_dir):
        try:
            import pkg_resources
            icons_dir = pkg_resources.resource_filename('tkintercli', 'icons')
        except Exception as e:
            raise FileNotFoundError(f"Impossible de trouver le dossier d'icônes: {str(e)}")
    
    icon_path = os.path.join(icons_dir, f"{name}.svg")
    
    if not os.path.exists(icon_path):
        raise FileNotFoundError(f"L'icône {name}.svg n'existe pas dans {icons_dir}")
    
    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_png:
        tmp_png_path = tmp_png.name
    
    try:
        magick_cmd = [
            "magick",
            "-background", "none",   
            "-density", "300",        
            icon_path,        
            "-resize", f"{width}x{height}",
            "-fill", color.replace("black", "#020302"),    
            "-colorize", "100%",    
            tmp_png_path         
        ]
        
        
        process = subprocess.run(magick_cmd, check=False, capture_output=True)
        
        if process.returncode != 0:
            print(f"Erreur (code {process.returncode}):")
            print(process.stderr.decode('utf-8'))
            raise RuntimeError(f"Erreur lors de la conversion SVG avec ImageMagick")
        
        img = Image.open(tmp_png_path)
        
        return ImageTk.PhotoImage(img)
    
    except subprocess.CalledProcessError as e:
        print(f"Exception CalledProcessError: {e}")
        raise RuntimeError(f"Erreur lors de la conversion SVG avec ImageMagick: {e}")
    
    except Exception as e:
        print(f"Exception générale: {e}")
        raise Exception(f"Erreur lors du traitement de l'icône: {e}")
    
    finally:
        if os.path.exists(tmp_png_path):
            os.remove(tmp_png_path)