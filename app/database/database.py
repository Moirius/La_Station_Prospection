"""
Configuration de la base de données SQLAlchemy
"""

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# Instance SQLAlchemy
db = SQLAlchemy()

# Instance Migrate pour les migrations
migrate = Migrate()

def init_database(app):
    """Initialiser la base de données avec l'application Flask"""
    db.init_app(app)
    migrate.init_app(app, db)
    
    # Créer les tables si elles n'existent pas
    with app.app_context():
        db.create_all()
    
    return db 