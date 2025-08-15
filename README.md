# 🚀 La Station Prospection

**Système de prospection automatisé avec analyse IA des réseaux sociaux**

## 📋 Description

La Station Prospection est une application web Flask qui automatise la recherche d'entreprises et l'analyse de leur présence sur les réseaux sociaux. Le système utilise une approche moderne basée sur des captures d'écran analysées par l'IA pour extraire des données précises et fiables.

## ✨ Fonctionnalités Principales

### 🔍 Scraping Intelligent

- **Google Maps V2 Continuous** : Recherche continue jusqu'à obtenir le nombre d'entreprises souhaité
- **Filtrage intelligent** : Évite les doublons, filtre par note et nombre d'avis
- **Géocodage automatique** : Extraction des coordonnées GPS précises
- **Recherche adaptative** : Stratégies de recherche selon le type d'entreprise

### 📱 Analyse des Réseaux Sociaux

- **Instagram** : Followers, posts, bio, taux d'engagement
- **Facebook** : Likes, followers, description, informations de contact
- **Captures d'écran intelligentes** : Playwright avec optimisation automatique
- **Analyse IA avancée** : OpenAI GPT-4o pour extraction structurée

### 🗄️ Base de Données Structurée

- **Modèle Lead complet** : Toutes les informations extraites
- **Coordonnées GPS** : Latitude/longitude pour cartographie
- **Statuts de traitement** : Suivi des étapes de scraping et d'analyse
- **Logs détaillés** : Historique complet des opérations

### 🎯 Interface Web Moderne

- **Dashboard interactif** : Visualisation des statistiques
- **Carte géographique** : Affichage des leads avec coordonnées GPS
- **API REST complète** : Endpoints pour intégration externe
- **Gestion des leads** : Interface de gestion des prospects

## 🏗️ Architecture

```
la_station_prospection/
├── app/
│   ├── __init__.py                 # Factory Flask
│   ├── config.py                   # Configuration de l'application
│   ├── database/
│   │   ├── __init__.py
│   │   ├── database.py             # Configuration SQLAlchemy
│   │   └── models.py               # Modèle Lead
│   ├── scrapers/
│   │   ├── __init__.py
│   │   ├── google_maps_v2_continuous.py    # Scraper Google Maps principal
│   │   ├── scrapy_spider_improved.py       # Scraper sites web avec IA
│   │   └── instagram_session_manager.py    # Gestionnaire sessions Instagram
│   ├── services/
│   │   ├── __init__.py
│   │   ├── scraping_service.py     # Service principal d'orchestration
│   │   ├── screenshot_service.py   # Service de captures d'écran
│   │   └── ai_analysis_service.py  # Service d'analyse IA
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── logger.py               # Système de logging centralisé
│   │   ├── validators.py           # Validation des données
│   │   └── gcp_billing.py          # Intégration facturation GCP
│   └── web/
│       ├── __init__.py
│       ├── routes.py               # Routes Flask et API REST
│       └── templates/
│           ├── base.html           # Template de base
│           ├── dashboard.html      # Dashboard principal
│           ├── dashboard_simple.html # Dashboard simplifié
│           ├── scraping_map.html   # Interface cartographique
│           └── logs.html           # Page des logs
├── migrations/                     # Migrations de base de données
├── logs/                          # Fichiers de logs
├── screenshots/                   # Captures d'écran
├── instance/                      # Base de données SQLite
├── .env                           # Variables d'environnement
├── requirements.txt               # Dépendances Python
└── run.py                        # Point d'entrée de l'application
```

## 🚀 Installation

### Méthodes d'Installation

#### 🎯 **Méthode Simple (Recommandée)**

**Windows :**

1. Double-cliquez sur `install.bat` pour l'installation automatique
2. Double-cliquez sur `launch.bat` pour lancer l'application

**Linux/Mac :**

```bash
chmod +x install.sh
./install.sh
```

#### 🔧 **Installation Manuelle**

### Prérequis

- **Python** : 3.10 ou supérieur
- **Node.js** : Pour Playwright
- **Comptes API** : OpenAI, Google Places

### 1. Cloner le projet

```bash
git clone <repository-url>
cd la_station_prospection
```

### 2. Créer l'environnement virtuel

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 3. Installer les dépendances

```bash
pip install -r requirements.txt
```

### 4. Installer Playwright

```bash
playwright install chromium
```

### 5. Configuration

Créer un fichier `.env` à la racine du projet :

```env
# API Keys (requises)
OPENAI_API_KEY=votre_clé_openai
GOOGLE_PLACES_API_KEY=votre_clé_google_places

# Configuration Flask
FLASK_ENV=development
SECRET_KEY=votre_clé_secrète_flask

# Base de données
DATABASE_URL=sqlite:///instance/prospection.db

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/prospection.log

# Captures d'écran
SCREENSHOTS_DIR=screenshots
```

### 6. Initialiser la base de données

```bash
# Créer les tables
python create_new_db.py

# Ou utiliser les migrations Alembic
flask db upgrade
```

#### 🐳 **Installation avec Docker**

```bash
# Construire et lancer avec Docker Compose
docker-compose up -d

# Ou construire manuellement
docker build -t la-station-prospection .
docker run -p 5000:5000 la-station-prospection
```

#### 📦 **Installation via pip (Développement)**

```bash
# Installer en mode développement
pip install -e .

# Lancer avec la commande
la-station-prospection
```

## 🎯 Utilisation

### Démarrer l'application

```bash
python run.py
```

L'application sera accessible sur `http://localhost:5000`

### Interface Web

#### Dashboard Principal (`/`)

- Vue d'ensemble des leads et statistiques
- Graphiques de performance
- Statuts des derniers scrapings

#### Interface Cartographique (`/scraping-map`)

- Visualisation géographique des leads
- Carte interactive Google Maps
- Filtres et contrôles avancés

#### Gestion des Leads

- Liste complète des prospects
- Détails de chaque lead
- Actions de scraping et d'analyse

#### Logs Centralisés (`/logs`)

- Logs système en temps réel
- Historique des opérations
- Filtres par niveau et source

### API REST

#### Scraping

```bash
# Démarrer un scraping optimisé
POST /api/start-scraping-smart
{
  "location": "Rennes, France",
  "business_type": "restaurant",
  "max_results": 20,
  "min_rating": 4.0,
  "min_reviews": 10,
  "radius": 5000,
  "anti_hotels": true,
  "wide_search": false
}
```

#### Gestion des Leads

```bash
# Récupérer tous les leads
GET /api/leads

# Récupérer un lead spécifique
GET /api/lead/{id}

# Capturer un profil social
POST /api/lead/{id}/screenshot

# Analyser avec l'IA
POST /api/lead/{id}/analyze

# Recalculer les scores d'opportunité
POST /api/leads/recalculate-scores
```

#### Logs et Monitoring

```bash
# Récupérer les logs
GET /api/logs

# Résumé des logs
GET /api/logs/summary

# Vider les logs
POST /api/logs/clear

# Statut de l'application
GET /api/status
```

#### Sessions Sociales

```bash
# Gérer les sessions Facebook
POST /api/sessions/facebook

# Gérer les sessions Instagram
POST /api/sessions/instagram

# Statut des sessions
GET /api/sessions/status
```

## 📊 Données Extraites

### Google Maps

- **Informations de base** : Nom, adresse, téléphone, site web
- **Coordonnées GPS** : Latitude et longitude précises
- **Évaluations** : Note moyenne, nombre d'avis
- **Type d'entreprise** : Classification Google Places

### Instagram

- **Statistiques** : Followers, posts, comptes suivis
- **Profil** : Bio, nom d'utilisateur, statut vérifié
- **Engagement** : Taux calculé automatiquement
- **Dernière activité** : Date du dernier post

### Facebook

- **Statistiques** : Likes, followers
- **Informations** : Description, texte d'introduction
- **Contact** : Adresse, téléphone, horaires
- **Localisation** : Coordonnées et adresse

### Site Web

- **Contenu** : Résumé du texte, détection de produits/services
- **Médias** : Nombre d'images et vidéos
- **Fonctionnalités** : Formulaire de contact, réseaux sociaux
- **Analyse** : Score d'opportunité calculé par IA

## 🔧 Configuration Avancée

### Variables d'Environnement

| Variable                | Description               | Défaut                     | Requis |
| ----------------------- | ------------------------- | -------------------------- | ------ |
| `OPENAI_API_KEY`        | Clé API OpenAI            | -                          | ✅     |
| `GOOGLE_PLACES_API_KEY` | Clé API Google Places     | -                          | ✅     |
| `FLASK_ENV`             | Environnement Flask       | `development`              | ❌     |
| `SECRET_KEY`            | Clé secrète Flask         | `dev-secret-key`           | ❌     |
| `DATABASE_URL`          | URL de la base de données | `sqlite:///prospection.db` | ❌     |
| `SCREENSHOTS_DIR`       | Dossier des captures      | `screenshots`              | ❌     |
| `LOG_LEVEL`             | Niveau de log             | `INFO`                     | ❌     |
| `LOG_FILE`              | Fichier de log            | `logs/prospection.log`     | ❌     |

### Configuration du Scraping

```python
# Dans app/config.py
class Config:
    # Timeouts et retry
    REQUEST_TIMEOUT = 30
    MAX_RETRIES = 3
    DELAY_BETWEEN_REQUESTS = 1

    # Limites
    MAX_LEADS_PER_REQUEST = 50
    MAX_SCRAPING_TIME = 300
```

### Personnalisation des Prompts IA

Éditer `app/services/ai_analysis_service.py` pour adapter l'analyse à vos besoins spécifiques.

## 🧪 Tests et Validation

### Tests Automatisés

```bash
# Lancer tous les tests
pytest

# Tests spécifiques
pytest tests/test_scraping.py
pytest tests/test_ai_analysis.py
```

### Tests Manuels

```bash
# Test de la pipeline complète
python -c "
from app import create_app
from app.services.scraping_service import ScrapingService

app = create_app()
with app.app_context():
    service = ScrapingService()
    result = service.start_scraping_smart('Paris, France', 'restaurant', 5)
    print(f'Résultat: {result}')
"
```

### Validation des Données

- Vérification de l'intégrité des coordonnées GPS
- Contrôle des doublons en base de données
- Validation des données extraites par l'IA

## 📈 Performance et Monitoring

### Métriques Actuelles

- **Temps de scraping** : 2-5 secondes par entreprise
- **Taille des captures** : 0.3-0.7 MB (optimisées)
- **Précision IA** : >95% sur les données extraites
- **Temps d'analyse** : 5-10 secondes par plateforme

### Optimisations Implémentées

- **Recherche continue** : Évite les doublons et optimise les coûts API
- **Captures compressées** : Réduction de 70% de la taille des fichiers
- **Cache des sessions** : Réutilisation des sessions sociales
- **Analyse asynchrone** : Traitement parallèle des analyses IA

### Monitoring

- **Logs centralisés** : Suivi détaillé de toutes les opérations
- **Statistiques de performance** : Temps, coûts, taux de conversion
- **Alertes automatiques** : Notifications en cas d'erreur

## 🛡️ Sécurité

### Bonnes Pratiques

- **API Keys** : Stockées dans des variables d'environnement
- **Sessions** : Gestion sécurisée des cookies sociaux
- **Logs** : Pas d'informations sensibles dans les logs
- **Rate Limiting** : Protection contre les abus d'API

### Configuration de Production

```python
# Dans app/config.py
class ProductionConfig(Config):
    DEBUG = False
    TESTING = False
    LOG_LEVEL = 'WARNING'
    SECRET_KEY = os.environ.get('SECRET_KEY')  # Toujours définir en prod
```

## 🔍 Dépannage

### Erreurs Courantes

#### 1. "Client OpenAI non initialisé"

```bash
# Vérifier la clé API
echo $OPENAI_API_KEY

# Ou dans le fichier .env
OPENAI_API_KEY=votre_clé_ici
```

#### 2. "Erreur capture d'écran"

```bash
# Installer Playwright
playwright install chromium

# Vérifier les permissions
chmod 755 screenshots/
```

#### 3. "Erreur base de données"

```bash
# Créer la base
python create_new_db.py

# Ou appliquer les migrations
flask db upgrade
```

#### 4. "API Google Places non fonctionnelle"

```bash
# Vérifier la clé API
echo $GOOGLE_PLACES_API_KEY

# Tester l'API
curl "https://maps.googleapis.com/maps/api/geocode/json?address=Paris&key=VOTRE_CLE"
```

### Logs et Debug

- **Logs système** : `logs/prospection.log`
- **Logs Flask** : Console en mode debug
- **Logs IA** : Stockés dans la base de données
- **Logs web** : Interface `/logs`

## 🧹 Maintenance et Nettoyage

### Fichiers de Configuration

- **Cookies sociaux** : `fb_cookies.pkl` et `instagram_cookies.pkl`
- **Credentials GCP** : `lastationprospection-64ca8df5cdaf.json`
- **Variables d'environnement** : `.env`

### Nettoyage Automatique

Le système inclut des mécanismes de nettoyage automatique :

- Suppression des captures d'écran obsolètes
- Rotation des logs
- Gestion des sessions expirées

## 🤝 Contribution

### Processus de Contribution

1. **Fork** le projet
2. **Créer** une branche feature (`git checkout -b feature/NouvelleFonctionnalite`)
3. **Commit** les changements (`git commit -m 'Ajouter nouvelle fonctionnalité'`)
4. **Push** vers la branche (`git push origin feature/NouvelleFonctionnalite`)
5. **Ouvrir** une Pull Request

### Standards de Code

- **PEP 8** : Style de code Python
- **Docstrings** : Documentation des fonctions
- **Type hints** : Annotations de types
- **Tests** : Couverture de tests pour les nouvelles fonctionnalités

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

## 📞 Support

### Ressources

- **Documentation technique** : Ce README
- **Issues GitHub** : Pour signaler des bugs
- **Logs d'erreur** : `logs/prospection.log`

### Contact

Pour toute question ou problème :

- Ouvrir une issue sur GitHub
- Consulter la documentation technique
- Vérifier les logs d'erreur

---

**La Station Prospection** - Propulsez votre prospection avec l'IA ! 🚀

_Dernière mise à jour : Janvier 2025_
