import os
from setuptools import setup, find_packages

def parse_requirements(filename):
    here = os.path.abspath(os.path.dirname(__file__))  # directory of setup.py
    with open(os.path.join(here, filename), 'r') as f:
        return [line.strip() for line in f if line.strip() and not line.startswith('#')]

setup(
    name="tini-editor",
    version="0.1.3",
    packages=find_packages(),
    install_requires=parse_requirements('requirements.txt'),
    entry_points={
        "console_scripts": [
            "tini=tini.app:main",
        ],
    },
    author="WolfQuery",
    description="A tiny terminal text editor built with Textual",
    readme="README.md",
    keywords=["textual", "terminal", "text editor", "nano", "tini"],
    url="https://codeberg.org/WolfQuery/tini-editor",
    license= "CC-BY-NC-SA-4.0",
    classifiers=[
        "Programming Language :: Python :: 3"
    ],
)
