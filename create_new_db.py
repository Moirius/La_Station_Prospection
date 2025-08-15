#!/usr/bin/env python3
"""
Script pour créer une nouvelle base de données vierge
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.database.database import db
from app.utils.logger import SystemLogger

def create_new_database():
    """Créer une nouvelle base de données vierge"""
    
    print("=== CRÉATION D'UNE NOUVELLE BASE DE DONNÉES ===")
    print()
    
    try:
        # Créer l'application Flask
        app = create_app()
        
        with app.app_context():
            # Créer toutes les tables
            db.create_all()
            
            print("✅ Base de données créée avec succès !")
            print(f"📁 Fichier: {app.config['SQLALCHEMY_DATABASE_URI']}")
            
            # Vérifier que le fichier existe
            db_path = app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
            if os.path.exists(db_path):
                file_size = os.path.getsize(db_path)
                print(f"📏 Taille: {file_size} bytes")
            else:
                print("⚠️ Le fichier de base de données n'a pas été créé")
            
            print("\n🎉 Nouvelle base de données vierge prête à l'emploi !")
            
    except Exception as e:
        print(f"❌ Erreur lors de la création de la base: {str(e)}")
        SystemLogger.error(f"Erreur création base de données: {str(e)}")

if __name__ == "__main__":
    create_new_database() 