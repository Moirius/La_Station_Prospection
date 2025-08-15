from setuptools import setup, find_packages
import os

# Lire le contenu du README
def read_readme():
    if os.path.exists("README.md"):
        with open("README.md", "r", encoding="utf-8") as fh:
            return fh.read()
    return "La Station Prospection - Application de prospection commerciale"

# Lire les dépendances
def read_requirements():
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        return [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="la-station-prospection",
    version="1.0.0",
    author="La Station",
    author_email="contact@lastation.com",
    description="Application de prospection commerciale avec scraping et analyse IA",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/lastation/prospection",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
    ],
    python_requires=">=3.10",
    install_requires=read_requirements(),
    entry_points={
        "console_scripts": [
            "la-station-prospection=run:main",
        ],
    },
    include_package_data=True,
    package_data={
        "app": ["web/templates/*", "web/static/*"],
    },
) 