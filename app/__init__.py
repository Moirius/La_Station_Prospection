# Package principal de l'application La Station Prospection 

from flask import Flask
from app.config import config
from app.database.database import init_database
from app.utils.logger import setup_logger
from app.web.routes import register_routes
import os
from dotenv import load_dotenv

def create_app(config_name='development'):
    """Factory pour créer l'application Flask"""
    
    # Charger le .env
    load_dotenv()
    
    # Créer l'application avec le bon dossier de templates
    app = Flask(__name__, 
                template_folder=os.path.join(os.path.dirname(__file__), 'web', 'templates'))
    
    # Configuration
    app.config.from_object(config[config_name])
    
    # Initialiser la base de données
    init_database(app)
    
    # Configurer le logging
    setup_logger()
    
    # Enregistrer les routes
    register_routes(app)
    
    return app 