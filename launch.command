#!/bin/bash

# Changer vers le répertoire du script
cd "$(dirname "$0")"

echo "========================================"
echo "  La Station Prospection"
echo "========================================"
echo ""

# Vérifier si l'environnement virtuel existe
if [ ! -d "venv" ]; then
    echo "Environnement virtuel non trouvé. Installation automatique..."
    echo ""
    
    # Vérifier si Python est installé
    if ! command -v python3 &> /dev/null; then
        echo "ERREUR: Python 3 n'est pas installé."
        echo "Veuillez installer Python 3.10+ depuis: https://python.org/"
        echo ""
        echo "Appuyez sur Entrée pour fermer..."
        read
        exit 1
    fi
    
    echo "Création de l'environnement virtuel..."
    python3 -m venv venv
    
    echo "Installation des dépendances..."
    source venv/bin/activate
    pip install -r requirements.txt
    
    echo "Installation de Playwright..."
    playwright install chromium
    
    echo "Création de la base de données..."
    python create_new_db.py
    
    echo "Installation terminée!"
    echo ""
fi

echo "Démarrage de l'application..."
echo ""

# Activer l'environnement virtuel
source venv/bin/activate

# Lancer l'application
python run.py
