# 🚀 La Station Prospection - Version Render

Version cloud de votre application de gestion des contacts, déployée sur **Render** pour permettre la collaboration de votre équipe sans avoir besoin de garder votre PC allumé.

## ✨ **Fonctionnalités**

- ✅ **Gestion des contacts** - Interface complète pour vos leads
- ✅ **Collaboration en temps réel** - Vos collègues peuvent marquer les contacts
- ✅ **Sauvegarde automatique** - Chaque action est immédiatement sauvegardée
- ✅ **Statistiques en direct** - Suivi des performances de contact
- ✅ **Hébergement 24/7** - Disponible sur Render sans interruption

## 🌐 **Déploiement sur Render**

### **Étape 1 : Préparation**
1. Créez un compte sur [Render.com](https://render.com)
2. Connectez votre repository GitHub
3. Assurez-vous que ce dossier est dans votre repo

### **Étape 2 : Création de la base de données**
1. Dans Render, créez une **PostgreSQL Database**
2. Notez l'URL de connexion
3. Le nom sera automatiquement configuré via `render.yaml`

### **Étape 3 : Déploiement de l'application**
1. Créez un **Web Service** dans Render
2. Connectez votre repository GitHub
3. Render détectera automatiquement la configuration
4. L'application se déploiera automatiquement

## 🔧 **Configuration automatique**

Le fichier `render.yaml` configure automatiquement :
- **Base de données PostgreSQL** (1GB gratuit)
- **Service web Python** (750h/mois gratuit)
- **Variables d'environnement** (SECRET_KEY, DATABASE_URL)
- **Déploiement automatique** depuis GitHub

## 📁 **Structure du projet**

```
render_deployment/
├── app/
│   ├── database/
│   │   └── models.py          # Modèle Lead
│   ├── web/
│   │   ├── routes.py          # API REST
│   │   └── templates/         # Interface HTML
│   └── __init__.py            # Configuration Flask
├── run.py                     # Point d'entrée
├── requirements.txt           # Dépendances Python
├── render.yaml               # Configuration Render
└── README.md                 # Ce fichier
```

## 🚀 **Lancement local (test)**

```bash
# Installation des dépendances
pip install -r requirements.txt

# Configuration des variables d'environnement
cp .env.example .env
# Éditez .env avec vos valeurs

# Lancement
python run.py
```

## 🔒 **Sécurité**

- **Lecture seule** sur les données de scraping
- **Modification** uniquement sur les statuts de contact
- **Pas d'accès** aux fonctions de scraping
- **Authentification** possible à ajouter

## 📊 **API Endpoints**

- `GET /` - Dashboard principal
- `GET /contacts` - Gestion des contacts
- `GET /api/leads` - Liste des leads
- `GET /api/leads/contacts-summary` - Résumé des contacts
- `POST /api/lead/{id}/contact` - Marquer comme contacté
- `DELETE /api/lead/{id}/contact/{type}` - Décocher un contact
- `GET /api/status` - Statut de l'application

## 💰 **Coûts Render**

- **Base de données** : Gratuit jusqu'à 1GB
- **Service web** : Gratuit jusqu'à 750h/mois
- **HTTPS** : Inclus
- **Domaine personnalisé** : Possible

## 🎯 **Utilisation par votre équipe**

1. **Vous** : Gardez le contrôle sur le scraping et la mise à jour
2. **Vos collègues** : Accèdent à `/contacts` pour :
   - Voir tous les leads
   - Cocher/décocher les contacts
   - Consulter les statistiques
   - Collaborer en temps réel

## 🚨 **Limitations actuelles**

- Pas de système d'authentification
- Pas de gestion des utilisateurs
- Pas de logs détaillés des actions
- Pas d'export des données

## 🔮 **Améliorations futures possibles**

- Système d'authentification simple
- Gestion des permissions par utilisateur
- Historique des modifications
- Export des données (CSV, PDF)
- Notifications en temps réel
- API pour intégrations externes

## 📞 **Support**

Pour toute question sur le déploiement Render ou l'application, consultez la documentation Render ou contactez votre équipe de développement.

---

**🎉 Votre application sera bientôt disponible 24/7 sur le cloud !**
