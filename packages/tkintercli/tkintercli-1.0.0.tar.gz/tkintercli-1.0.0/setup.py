from setuptools import setup, find_packages
from pathlib import Path
import os

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

version_file = Path(__file__).parent / "tkintercli" / "__version__.py"
version_globals = {}
with open(version_file) as f:
    exec(f.read(), version_globals)
VERSION = version_globals['__version__']


setup(
    name='tkintercli',
    version=VERSION,
    description='TkinterCLI est un outil en ligne de commande permettant de simplfier la création de projet avec Tkinter.',
    author='Albatros329',
    packages=find_packages(),
    long_description=long_description,
    long_description_content_type="text/markdown",
    package_data={
        'tkintercli': ['model/**/*', 'model/**/.*', 'icons/**/*', 'icons/**/.*'],
    },
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'tkintercli=tkintercli.main:main',
        ],
    },
    install_requires=[
        "click",
        "colorama",
        "PyYAML",
        "setuptools",
        "Pillow",
    ],
    python_requires='>=3.10',
    url="https://github.com/Albatros329/atc_tracker/"
)
