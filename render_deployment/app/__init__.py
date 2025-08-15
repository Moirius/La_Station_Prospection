"""
Application Flask pour La Station Prospection - Version Render
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os

# Initialisation des extensions
db = SQLAlchemy()
migrate = Migrate()

def create_app():
    """Factory pour créer l'application Flask"""
    app = Flask(__name__)
    
    # Configuration pour Render
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # Configuration de la base de données PostgreSQL pour Render
    database_url = os.environ.get('DATABASE_URL')
    if database_url and database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url or 'sqlite:///app.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialisation des extensions
    db.init_app(app)
    migrate.init_app(app, db)
    
    # Enregistrement des routes
    from app.web.routes import register_routes
    register_routes(app)
    
    # Création des tables si elles n'existent pas
    with app.app_context():
        db.create_all()
    
    return app
