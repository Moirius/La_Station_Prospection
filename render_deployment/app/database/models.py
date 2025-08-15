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
    facebook_description = db.Column(db.Text, nullable=True)
    
    # Données Instagram supplémentaires
    instagram_stats = db.Column(db.Text, nullable=True)
    instagram_description = db.Column(db.Text, nullable=True)
    
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
            'has_video_on_site': self.has_video_on_site,
            'has_images_on_site': self.has_images_on_site,
            'videos_count': self.videos_count,
            'images_count': self.images_count,
            'texte_site_resume': self.texte_site_resume,
            'produits_services_detectes': self.produits_services_detectes,
            'contact_form_detecte': self.contact_form_detecte,
            'social_media_detectes': self.social_media_detectes,
            'nb_posts_instagram': self.nb_posts_instagram,
            'nb_followers_instagram': self.nb_followers_instagram,
            'nb_following_instagram': self.nb_following_instagram,
            'bio_instagram': self.bio_instagram,
            'nb_likes_facebook': self.nb_likes_facebook,
            'nb_followers_facebook': self.nb_followers_facebook,
            'description_facebook': self.description_facebook,
            'intro_facebook': self.intro_facebook,
            'facebook_stats': self.facebook_stats,
            
            # Informations de contact Facebook
            'facebook_telephone': self.facebook_telephone,
            'facebook_email': self.facebook_email,
            'facebook_adresse': self.facebook_adresse,
            'facebook_site_web': self.facebook_site_web,
            
            # Informations de contact Instagram
            'instagram_telephone': self.instagram_telephone,
            'instagram_email': self.instagram_email,
            'instagram_adresse': self.instagram_adresse,
            'instagram_site_web': self.instagram_site_web,
            'instagram_screenshot_path': self.instagram_screenshot_path,
            'facebook_screenshot_path': self.facebook_screenshot_path,
            'ai_extraction_status': self.ai_extraction_status,
            'ai_extraction_log': self.ai_extraction_log,
            'ai_analysis': self.ai_analysis,
            
            # Données Google Maps
            'google_maps_email': self.google_maps_email,
            'google_maps_telephone': self.google_maps_telephone,
            'google_maps_adresse': self.google_maps_adresse,
            
            # Données Site Web (IA)
            'site_web_email': self.site_web_email,
            'site_web_telephone': self.site_web_telephone,
            'site_web_adresse': self.site_web_adresse,
            'site_web_description': self.site_web_description,
            'site_web_horaires': self.site_web_horaires,
            'site_web_services': self.site_web_services,
            
            # Données Réseaux Sociaux (IA)
            'facebook_stats': self.facebook_stats,
            'facebook_description': self.facebook_description,
            'instagram_stats': self.instagram_stats,
            'instagram_description': self.instagram_description,
            
            # Scoring IA
            'score_ia': self.score_ia,
            'argumentaire_ia': self.argumentaire_ia,
            
            'statut_scraping': self.statut_scraping,
            'log': self.log,
            'score_opportunite': self.score_opportunite,
            'argumentaire': self.argumentaire,
            # Nouvelles colonnes pour suivi des informations récupérées
            'has_email': self.has_email,
            'has_phone': self.has_phone,
            'has_address': self.has_address,
            'has_instagram': self.has_instagram,
            'has_facebook': self.has_facebook,
            'has_contact_form': self.has_contact_form,
            # Nouvelles colonnes pour suivi des contacts effectués
            'contacted_by_email': self.contacted_by_email,
            'contacted_by_phone': self.contacted_by_phone,
            'contacted_by_address': self.contacted_by_address,
            'contacted_by_instagram': self.contacted_by_instagram,
            'contacted_by_facebook': self.contacted_by_facebook,
            'contacted_by_contact_form': self.contacted_by_contact_form,
            # Dates de contact
            'date_contacted_by_email': self.date_contacted_by_email.isoformat() if self.date_contacted_by_email else None,
            'date_contacted_by_phone': self.date_contacted_by_phone.isoformat() if self.date_contacted_by_phone else None,
            'date_contacted_by_address': self.date_contacted_by_address.isoformat() if self.date_contacted_by_address else None,
            'date_contacted_by_instagram': self.date_contacted_by_instagram.isoformat() if self.date_contacted_by_instagram else None,
            'date_contacted_by_facebook': self.date_contacted_by_facebook.isoformat() if self.date_contacted_by_facebook else None,
            'date_contacted_by_contact_form': self.date_contacted_by_contact_form.isoformat() if self.date_contacted_by_contact_form else None,
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
