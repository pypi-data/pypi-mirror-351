import os
import re

from setuptools import find_packages, setup


def get_version():
    version_file = os.path.join("clipkly", "version.py")
    with open(version_file, "r") as f:
        content = f.read()
    return re.search(r'__version__ = "([^"]+)"', content).group(1)


setup(
    name="clipkly",
    version=get_version(),
    packages=find_packages(),
    install_requires=["pandas", "tqdm", "openpyxl"],
    entry_points={
        "console_scripts": [
            "clipkly=clipkly.cli:main"
        ]
    },
    author="Julian Dario Luna Patiño",
    author_email="judlup@trycatch.tv",
    description="Automatiza la creación de clips impactantes desde tus transmisiones. clipkly convierte JSONs con timecodes en cortes precisos listos para redes sociales, exportando también un Excel con metadatos editoriales. Perfecto para devs que crean, editan y publican contenido.",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/judlup/clipkly",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)
