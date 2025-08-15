#!/usr/bin/env python3
"""
Point d'entrée pour lancer l'application La Station Prospection
"""

from app import create_app

def main():
    """Fonction principale pour lancer l'application"""
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)

if __name__ == '__main__':
    main() 