"""
Utilitaires de validation des données
"""

import re
from urllib.parse import urlparse

def is_valid_email(email):
    """Valider un email"""
    if not email:
        return False
    
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def is_valid_phone(phone):
    """Valider un numéro de téléphone"""
    if not phone:
        return False
    
    # Nettoyer le numéro
    clean_phone = re.sub(r'[^\d+]', '', phone)
    
    # Vérifier la longueur (au moins 10 chiffres)
    digits_only = re.sub(r'[^\d]', '', clean_phone)
    return len(digits_only) >= 10

def is_valid_url(url):
    """Valider une URL"""
    if not url:
        return False
    
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False

def extract_emails_from_text(text):
    """Extraire les emails d'un texte"""
    if not text:
        return []
    
    pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    emails = re.findall(pattern, text)
    
    # Filtrer les emails valides
    return [email for email in emails if is_valid_email(email)]

def extract_phones_from_text(text):
    """Extraire les numéros de téléphone d'un texte"""
    if not text:
        return []
    
    # Patterns pour différents formats de téléphone
    patterns = [
        r'(\+33|0)[1-9](\d{8})',  # Format français
        r'(\+1)?\s?\(?[0-9]{3}\)?[\s.-]?[0-9]{3}[\s.-]?[0-9]{4}',  # Format US
        r'(\+[0-9]{1,3})?[\s.-]?[0-9]{6,14}'  # Format international
    ]
    
    phones = []
    for pattern in patterns:
        matches = re.findall(pattern, text)
        phones.extend(matches)
    
    # Nettoyer et valider
    clean_phones = []
    for phone in phones:
        if isinstance(phone, tuple):
            phone = ''.join(phone)
        if is_valid_phone(phone):
            clean_phones.append(phone)
    
    return list(set(clean_phones))  # Supprimer les doublons

def is_social_media_url(url):
    """Détecter si une URL est un réseau social"""
    if not url:
        return False, None
    
    social_patterns = {
        'facebook': r'facebook\.com|fb\.com',
        'instagram': r'instagram\.com|instagr\.am',
        'twitter': r'twitter\.com|x\.com',
        'linkedin': r'linkedin\.com',
        'youtube': r'youtube\.com|youtu\.be',
        'tiktok': r'tiktok\.com'
    }
    
    url_lower = url.lower()
    for platform, pattern in social_patterns.items():
        if re.search(pattern, url_lower):
            return True, platform
    
    return False, None

def clean_text(text, max_length=None):
    """Nettoyer un texte"""
    if not text:
        return ""
    
    # Supprimer les espaces multiples
    text = re.sub(r'\s+', ' ', text.strip())
    
    # Tronquer si nécessaire
    if max_length and len(text) > max_length:
        text = text[:max_length-3] + "..."
    
    return text

def extract_domain_from_url(url):
    """Extraire le domaine d'une URL"""
    if not url:
        return None
    
    try:
        parsed = urlparse(url)
        return parsed.netloc.lower()
    except:
        return None 