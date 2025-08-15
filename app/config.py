"""
Configuration de l'application La Station Prospection
"""

import os
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv(override=True)

class Config:
    """Configuration de base"""
    
    # Flask
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    FLASK_ENV = os.environ.get('FLASK_ENV', 'development')
    
    # Base de données
    DATABASE_URL = os.environ.get('DATABASE_URL') or 'sqlite:///prospection.db'
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Google Places API
    GOOGLE_PLACES_API_KEY = os.environ.get('GOOGLE_PLACES_API_KEY')
    
    # OpenAI API
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
    
    # Logging
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'DEBUG')
    LOG_FILE = os.environ.get('LOG_FILE', 'logs/prospection.log')
    
    # Scraping
    REQUEST_TIMEOUT = 30
    MAX_RETRIES = 3
    DELAY_BETWEEN_REQUESTS = 1  # secondes
    
    # Limites
    MAX_LEADS_PER_REQUEST = 50
    MAX_SCRAPING_TIME = 300  # secondes
    
    # Captures d'écran
    SCREENSHOTS_DIR = os.environ.get('SCREENSHOTS_DIR', 'screenshots')

class DevelopmentConfig(Config):
    """Configuration pour le développement"""
    DEBUG = True
    TESTING = False

class ProductionConfig(Config):
    """Configuration pour la production"""
    DEBUG = False
    TESTING = False

class TestingConfig(Config):
    """Configuration pour les tests"""
    TESTING = True
    DATABASE_URL = 'sqlite:///:memory:'

# Configuration par défaut
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
} 