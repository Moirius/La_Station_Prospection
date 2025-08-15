"""
Configuration des prompts pour l'IA
"""

# Prompt pour l'analyse des sites web
WEBSITE_ANALYSIS_PROMPT = """
Analyse ce code HTML et extrait TOUTES les informations importantes de l'entreprise.

INSTRUCTIONS DÉTAILLÉES :

1. CONTACT - Cherche dans TOUT le HTML :
   - Emails 
   - Téléphones 
   - Adresse 

2. ENTREPRISE - Analyse complète :
   - Nom : titre, h1, h2, meta title, logo alt
   - Type : description, mots-clés, contexte
   - Description : meta description, textes, about
   - Services : liste, menu, sections

3. RÉSEAUX SOCIAUX - Cherche PARTOUT MAIS VALIDE :
   IMPORTANT : Ne retourner QUE les URLs des vraies pages de réseaux sociaux
   - Facebook : facebook.com, fb.com (IGNORER les fichiers .css, .js, .png, etc.)
   - Instagram : instagram.com (IGNORER les fichiers .css, .js, .png, etc.)
   - Twitter : twitter.com, x.com (IGNORER les fichiers .css, .js, .png, etc.)
   - LinkedIn : linkedin.com (IGNORER les fichiers .css, .js, .png, etc.)
   - YouTube : youtube.com (IGNORER les fichiers .css, .js, .png, etc.)
   - TikTok : tiktok.com (IGNORER les fichiers .css, .js, .png, etc.)
   
   RÈGLES STRICTES :
   - URL doit contenir le nom du réseau social
   - IGNORER les URLs de fichiers (.css, .js, .png, .jpg, .gif, .ico, .svg, .woff, .ttf)
   - IGNORER les URLs de plugins ou widgets
   - IGNORER les URLs de tracking ou analytics
   - Seulement les URLs de pages de profils ou d'entreprises

4. PRATIQUE - Informations utiles :
   - Horaires : textes, sections horaires
   - Tarifs : prix, coûts, tarifs
   - Services : liste détaillée

MÉTHODE :
- Parcours TOUT le HTML ligne par ligne
- Cherche dans les attributs href, src, alt, title
- Cherche dans les textes visibles et cachés
- Vérifie les liens externes
- Analyse les métadonnées

IMPORTANT :
- Sois exhaustif, ne rate rien
- Si une information n'est pas trouvée, utiliser ""
- Retourner UNIQUEMENT un JSON valide

JSON REQUIS :
{{
  "contact": {{
    "emails": [],
    "telephones": [],
    "adresse": ""
  }},
  "entreprise": {{
    "nom": "",
    "type": "",
    "description": "",
    "produits_services": [],
    "public_cible": ""
  }},
  "pratique": {{
    "horaires": "",
    "tarifs": "",
    "services": []
  }},
  "reseaux_sociaux": {{
    "facebook": "",
    "instagram": "",
    "twitter": "",
    "linkedin": "",
    "youtube": "",
    "tiktok": "",
    "autres": []
  }}
}}

URL : {url}
HTML : {html_content}
"""

# Prompt pour l'analyse des captures d'écran
SCREENSHOT_ANALYSIS_PROMPT = """
Analyse cette capture d'écran de {platform} et extrait TOUTES les informations visibles.

INSTRUCTIONS DÉTAILLÉES :

1. STATISTIQUES - Compte EXACTEMENT :
   - Nombre de followers/abonnés
   - Nombre de likes/j'aime
   - Nombre de posts/publications
   - Nombre de commentaires si visible

2. INFORMATIONS ENTREPRISE :
   - Nom de la page/entreprise
   - Description complète
   - Type d'activité
   - Localisation/ville

3. CONTACT - Cherche PARTOUT :
   - Téléphone (numéros visibles)
   - Email (adresses visibles)
   - Adresse physique
   - Site web

4. CONTENU :
   - Services/produits mentionnés
   - Horaires d'ouverture
   - Prix/tarifs
   - Événements/actualités

5. PUBLIC CIBLE :
   - Description du public
   - Âge, style de vie
   - Intérêts mentionnés

MÉTHODE :
- Analyse TOUT le texte visible
- Compte les chiffres exacts
- Extrais les informations de contact
- Identifie les liens et URLs
- Note les détails importants

IMPORTANT :
- Sois exhaustif, ne rate rien
- Si une information n'est pas visible, mettre "Non visible"
- Pour les nombres, utiliser le format exact (ex: "1,234" ou "1.2K")
- Être précis et objectif

RETOURNE UNIQUEMENT UN JSON VALIDE :

POUR INSTAGRAM :
{{
  "followers": "nombre exact de followers",
  "following": "nombre exact de following/abonnements",
  "posts": "nombre exact de posts/publications",
  "bio": "bio complète de l'entreprise",
  "description": "description complète de l'entreprise",
  "contact_info": {{
    "phone": "téléphone si visible",
    "email": "email si visible",
    "address": "adresse si visible",
    "website": "site web si visible"
  }},
  "services": ["service1", "service2"],
  "horaires": "horaires d'ouverture si visibles",
  "public_cible": "public cible mentionné",
  "localisation": "ville/région mentionnée"
}}

POUR FACEBOOK :
{{
  "followers": "nombre exact de followers/abonnés",
  "likes": "nombre exact de likes/j'aime",
  "posts": "nombre de posts si visible",
  "intro": "intro complète de la page (toutes les informations visibles)",
  "description": "description complète de l'entreprise",
  "contact_info": {{
    "phone": "téléphone si visible",
    "email": "email si visible",
    "address": "adresse si visible",
    "website": "site web si visible"
  }},
  "services": ["service1", "service2"],
  "horaires": "horaires d'ouverture si visibles",
  "public_cible": "public cible mentionné",
  "localisation": "ville/région mentionnée"
}}
"""

# Prompt pour le scoring des leads
LEAD_SCORING_PROMPT = """
Évalue ce lead en fonction des informations disponibles et génère un score d'opportunité.

CRITÈRES D'ÉVALUATION :
1. Qualité des informations de contact (email, téléphone, adresse)
2. Présence et qualité du site web
3. Engagement sur les réseaux sociaux
4. Type d'entreprise et secteur d'activité
5. Note Google et nombre d'avis
6. Présence de médias (vidéos, images)

SCORE SUR 100 :
- 80-100 : Prospect excellent
- 60-79 : Bon prospect
- 40-59 : Prospect intéressant
- 20-39 : Prospect faible
- 0-19 : Prospect à éviter

RETOURNE UN JSON VALIDE :
{
  "score": 75,
  "argumentaire": "Explication détaillée du score",
  "points_forts": ["point1", "point2"],
  "points_faibles": ["point1", "point2"],
  "recommandations": ["recommandation1", "recommandation2"]
}
"""

# Prompt système pour l'API OpenAI
SYSTEM_PROMPT = """
Tu es un expert en analyse de sites web et de données d'entreprise. 
Tu extrais les informations importantes et tu retournes UNIQUEMENT un JSON valide.
Sois précis, objectif et structuré dans tes réponses.
""" 