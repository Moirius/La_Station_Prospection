"""
Modèles de données pour les leads/prospects - Version Render
"""

from datetime import datetime
from app import db

class Lead(db.Model):
    """Modèle pour les leads/prospects"""
    
    __tablename__ = 'leads'
    
    # Champs principaux
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(255), nullable=False, index=True)
    adresse = db.Column(db.Text, nullable=True)
    telephone = db.Column(db.String(50), nullable=True)
    email = db.Column(db.String(255), nullable=True)
    
    # Coordonnées GPS des établissements
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)
    
    # URLs et réseaux sociaux
    site_web = db.Column(db.String(500), nullable=True)
    facebook_url = db.Column(db.String(500), nullable=True)
    instagram_handle = db.Column(db.String(100), nullable=True)
    instagram_url = db.Column(db.String(500), nullable=True)
    
    # Données Google Maps
    note_google = db.Column(db.Float, nullable=True)
    nb_avis_google = db.Column(db.Integer, nullable=True)
    business_type = db.Column(db.String(100), nullable=True)
    
    # Données de scraping site web
    has_video_on_site = db.Column(db.Boolean, default=False)
    has_images_on_site = db.Column(db.Boolean, default=False)
    videos_count = db.Column(db.Integer, default=0)
    images_count = db.Column(db.Integer, default=0)
    texte_site_resume = db.Column(db.Text, nullable=True)
    produits_services_detectes = db.Column(db.Boolean, default=False)
    contact_form_detecte = db.Column(db.Boolean, default=False)
    social_media_detectes = db.Column(db.Boolean, default=False)
    
    # Données Instagram
    nb_posts_instagram = db.Column(db.Integer, nullable=True)
    nb_followers_instagram = db.Column(db.Integer, nullable=True)
    nb_following_instagram = db.Column(db.Integer, nullable=True)
    bio_instagram = db.Column(db.Text, nullable=True)
    
    # Données Facebook
    nb_likes_facebook = db.Column(db.Integer, nullable=True)
    nb_followers_facebook = db.Column(db.Integer, nullable=True)
    description_facebook = db.Column(db.Text, nullable=True)
    intro_facebook = db.Column(db.Text, nullable=True)
    facebook_stats = db.Column(db.Text, nullable=True)
    
    # Informations de contact Facebook
    facebook_telephone = db.Column(db.String(50), nullable=True)
    facebook_email = db.Column(db.String(255), nullable=True)
    facebook_adresse = db.Column(db.Text, nullable=True)
    facebook_site_web = db.Column(db.String(500), nullable=True)
    
    # Informations de contact Instagram
    instagram_telephone = db.Column(db.String(50), nullable=True)
    instagram_email = db.Column(db.String(255), nullable=True)
    instagram_adresse = db.Column(db.Text, nullable=True)
    instagram_site_web = db.Column(db.String(500), nullable=True)
    
    # Nouvelles données pour captures d'écran et IA
    instagram_screenshot_path = db.Column(db.String(500), nullable=True)
    facebook_screenshot_path = db.Column(db.String(500), nullable=True)
    ai_extraction_status = db.Column(db.String(50), default='en_attente')
    ai_extraction_log = db.Column(db.Text, nullable=True)
    
    # Analyse IA du site web
    ai_analysis = db.Column(db.JSON, nullable=True)
    
    # Statut et logs
    statut_scraping = db.Column(db.String(50), default='en_attente')
    log = db.Column(db.Text, nullable=True)
    
    # Champ de score d'opportunité IA
    score_opportunite = db.Column(db.Float, nullable=True, default=None)
    argumentaire = db.Column(db.Text, nullable=True)
    
    # Nouvelles colonnes pour suivi des informations récupérées
    has_email = db.Column(db.Boolean, default=False)
    has_phone = db.Column(db.Boolean, default=False)
    has_address = db.Column(db.Boolean, default=False)
    has_instagram = db.Column(db.Boolean, default=False)
    has_facebook = db.Column(db.Boolean, default=False)
    has_contact_form = db.Column(db.Boolean, default=False)
    
    # Nouvelles colonnes pour suivi des contacts effectués
    contacted_by_email = db.Column(db.Boolean, default=False)
    contacted_by_phone = db.Column(db.Boolean, default=False)
    contacted_by_address = db.Column(db.Boolean, default=False)
    contacted_by_instagram = db.Column(db.Boolean, default=False)
    contacted_by_facebook = db.Column(db.Boolean, default=False)
    contacted_by_contact_form = db.Column(db.Boolean, default=False)
    
    # Dates de contact
    date_contacted_by_email = db.Column(db.DateTime, nullable=True)
    date_contacted_by_phone = db.Column(db.DateTime, nullable=True)
    date_contacted_by_address = db.Column(db.DateTime, nullable=True)
    date_contacted_by_instagram = db.Column(db.DateTime, nullable=True)
    date_contacted_by_facebook = db.Column(db.DateTime, nullable=True)
    date_contacted_by_contact_form = db.Column(db.DateTime, nullable=True)
    
    # Données supplémentaires Google Maps
    google_maps_email = db.Column(db.String(255), nullable=True)
    google_maps_telephone = db.Column(db.String(50), nullable=True)
    google_maps_adresse = db.Column(db.Text, nullable=True)
    
    # Données supplémentaires site web
    site_web_email = db.Column(db.String(255), nullable=True)
    site_web_telephone = db.Column(db.String(50), nullable=True)
    site_web_adresse = db.Column(db.Text, nullable=True)
    site_web_description = db.Column(db.Text, nullable=True)
    site_web_horaires = db.Column(db.Text, nullable=True)
    site_web_services = db.Column(db.Text, nullable=True)
    
    # Scoring IA
    score_ia = db.Column(db.Float, nullable=True)
    argumentaire_ia = db.Column(db.Text, nullable=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        """Convertir le lead en dictionnaire"""
        return {
            'id': self.id,
            'nom': self.nom,
            'adresse': self.adresse,
            'telephone': self.telephone,
            'email': self.email,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'site_web': self.site_web,
            'facebook_url': self.facebook_url,
            'instagram_handle': self.instagram_handle,
            'instagram_url': self.instagram_url,
            'note_google': self.note_google,
            'nb_avis_google': self.nb_avis_google,
            'business_type': self.business_type,
            'has_email': self.has_email,
            'has_phone': self.has_phone,
            'has_address': self.has_address,
            'has_instagram': self.has_instagram,
            'has_facebook': self.has_facebook,
            'has_contact_form': self.has_contact_form,
            'contacted_by_email': self.contacted_by_email,
            'contacted_by_phone': self.contacted_by_phone,
            'contacted_by_address': self.contacted_by_address,
            'contacted_by_instagram': self.contacted_by_instagram,
            'contacted_by_facebook': self.contacted_by_facebook,
            'contacted_by_contact_form': self.contacted_by_contact_form,
            'date_contacted_by_email': self.date_contacted_by_email.isoformat() if self.date_contacted_by_email else None,
            'date_contacted_by_phone': self.date_contacted_by_phone.isoformat() if self.date_contacted_by_phone else None,
            'date_contacted_by_address': self.date_contacted_by_address.isoformat() if self.date_contacted_by_address else None,
            'date_contacted_by_instagram': self.date_contacted_by_instagram.isoformat() if self.date_contacted_by_instagram else None,
            'date_contacted_by_facebook': self.date_contacted_by_facebook.isoformat() if self.date_contacted_by_facebook else None,
            'date_contacted_by_contact_form': self.date_contacted_by_contact_form.isoformat() if self.date_contacted_by_contact_form else None,
            'score_opportunite': self.score_opportunite,
            'score_ia': self.score_ia,
            'argumentaire_ia': self.argumentaire_ia,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def mark_contacted(self, contact_type):
        """Marquer un lead comme contacté par un moyen spécifique"""
        contact_fields = {
            'email': 'contacted_by_email',
            'phone': 'contacted_by_phone', 
            'address': 'contacted_by_address',
            'instagram': 'contacted_by_instagram',
            'facebook': 'contacted_by_facebook',
            'contact_form': 'contacted_by_contact_form'
        }
        
        date_fields = {
            'email': 'date_contacted_by_email',
            'phone': 'date_contacted_by_phone',
            'address': 'date_contacted_by_address', 
            'instagram': 'date_contacted_by_instagram',
            'facebook': 'date_contacted_by_facebook',
            'contact_form': 'date_contacted_by_contact_form'
        }
        
        if contact_type in contact_fields:
            setattr(self, contact_fields[contact_type], True)
            setattr(self, date_fields[contact_type], datetime.utcnow())
            self.updated_at = datetime.utcnow()
            return True
        return False
    
    def unmark_contacted(self, contact_type):
        """Décocher un contact (marquer comme non contacté)"""
        contact_fields = {
            'email': 'contacted_by_email',
            'phone': 'contacted_by_phone',
            'address': 'contacted_by_address',
            'instagram': 'contacted_by_instagram', 
            'facebook': 'contacted_by_facebook',
            'contact_form': 'contacted_by_contact_form'
        }
        
        date_fields = {
            'email': 'date_contacted_by_email',
            'phone': 'date_contacted_by_phone',
            'address': 'date_contacted_by_address',
            'instagram': 'date_contacted_by_instagram',
            'facebook': 'date_contacted_by_facebook',
            'contact_form': 'date_contacted_by_contact_form'
        }
        
        if contact_type in contact_fields:
            setattr(self, contact_fields[contact_type], False)
            setattr(self, date_fields[contact_type], None)
            self.updated_at = datetime.utcnow()
            return True
        return False
