#!/bin/bash

echo "========================================"
echo "  Installation La Station Prospection"
echo "========================================"
echo ""

# Vérifier si Python est installé
if ! command -v python3 &> /dev/null; then
    echo "ERREUR: Python 3 n'est pas installé."
    echo "Veuillez installer Python 3.10+ depuis: https://python.org/"
    exit 1
fi

echo "Python détecté:"
python3 --version

echo ""
echo "Création de l'environnement virtuel..."
python3 -m venv venv

echo ""
echo "Activation de l'environnement virtuel..."
source venv/bin/activate

echo ""
echo "Installation des dépendances..."
pip install -r requirements.txt

echo ""
echo "Installation de Playwright..."
playwright install chromium

echo ""
echo "Installation terminée!"
echo ""
echo "Pour lancer l'application:"
echo "  - Exécutez: ./launch.sh"
echo "  - Ou ouvrez un terminal et tapez: python run.py"
echo ""
echo "L'application sera accessible sur: http://localhost:5000"
echo ""

# Rendre les scripts exécutables
chmod +x launch.sh 