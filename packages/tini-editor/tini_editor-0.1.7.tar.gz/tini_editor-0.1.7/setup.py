import os
from setuptools import setup, find_packages

def parse_requirements(filename):
    here = os.path.abspath(os.path.dirname(__file__))
    with open(os.path.join(here, filename), 'r') as f:
        return [line.strip() for line in f if line.strip() and not line.startswith('#')]

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="tini-editor",
    version="0.1.7",
    packages=find_packages(),
    install_requires=parse_requirements('requirements.txt'),
    entry_points={
        "console_scripts": [
            "tini=tini.app:main",
        ],
    },
    author="WolfQuery",
    description="A tiny terminal text editor built with Textual",
    long_description=long_description,
    long_description_content_type="text/markdown",
    keywords=["textual", "terminal", "text editor", "nano", "tini"],
    url="https://codeberg.org/WolfQuery/tini-editor",
    license="CC-BY-NC-SA-4.0",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: Other/Proprietary License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.12",
    license_files = ("LICENSE",),
)
