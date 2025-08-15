"""
Service principal d'orchestration du scraping
"""

import time
import os
from typing import List, Dict, Any, Optional
from app.database.models import Lead
from app.database.database import db
from app.utils.logger import LeadLogger, SystemLogger
from app.utils.validators import is_valid_url, is_social_media_url
from app.scrapers.google_maps_v2_continuous import GoogleMapsScraperV2Continuous
from app.scrapers.scrapy_spider_improved import ScrapyWebsiteScraperImproved
from app.services.screenshot_service import ScreenshotService
from app.services.ai_analysis_service import AIAnalysisService
from app.config import Config
from dotenv import load_dotenv

class ScrapingService:
    """Service principal de scraping"""
    
    def __init__(self):
        # Charger le .env pour garantir la présence des variables d'environnement
        load_dotenv()
        SystemLogger.info("Initialisation du ScrapingService")
        
        # Initialiser les services de production
        try:
            SystemLogger.info("Tentative d'utilisation des services de production")
            
            # Initialisation des services avec gestion d'erreurs spécifiques
            try:
                self.google_maps_service = GoogleMapsScraperV2Continuous()
                SystemLogger.info("✅ Service Google Maps initialisé")
            except Exception as e:
                SystemLogger.error(f"❌ Erreur initialisation Google Maps: {str(e)}")
                raise ValueError(f"Impossible d'initialiser le service Google Maps: {str(e)}")
            
            try:
                self.website_scraper = ScrapyWebsiteScraperImproved()
                SystemLogger.info("✅ Service de scraping web initialisé")
            except Exception as e:
                SystemLogger.error(f"❌ Erreur initialisation scraper web: {str(e)}")
                raise ValueError(f"Impossible d'initialiser le scraper web: {str(e)}")
            
            try:
                self.screenshot_service = ScreenshotService()
                SystemLogger.info("✅ Service de captures d'écran initialisé")
            except Exception as e:
                SystemLogger.error(f"❌ Erreur initialisation service screenshots: {str(e)}")
                raise ValueError(f"Impossible d'initialiser le service de captures d'écran: {str(e)}")
            
            try:
                self.ai_analysis_service = AIAnalysisService()
                SystemLogger.info("✅ Service d'analyse IA initialisé")
            except Exception as e:
                SystemLogger.error(f"❌ Erreur initialisation service IA: {str(e)}")
                raise ValueError(f"Impossible d'initialiser le service d'analyse IA: {str(e)}")
            
            # Test rapide de l'API Google Places seulement si une clé est configurée
            if Config.GOOGLE_PLACES_API_KEY:
                SystemLogger.info("Test de l'API Google Places...")
                try:
                    test_result = self.google_maps_service._geocode_location("Paris, France")
                    if test_result:
                        SystemLogger.info("✅ API Google Places fonctionnelle")
                    else:
                        raise ValueError("API Google Places non fonctionnelle")
                except Exception as e:
                    SystemLogger.error(f"❌ Test API Google Places échoué: {str(e)}")
                    raise ValueError(f"Test de l'API Google Places échoué: {str(e)}")
            else:
                SystemLogger.warning("Aucune clé API Google Places configurée")
                raise ValueError("Pas de clé API Google Places")
            
        except ValueError as e:
            SystemLogger.error(f"Erreur de configuration: {str(e)}")
            raise e
        except Exception as e:
            SystemLogger.error(f"Erreur inattendue lors de l'initialisation des services: {str(e)}")
            raise e
    
    def start_scraping_smart(self, location: str, business_type: Optional[str] = "", 
                           max_results: int = 20, min_rating: float = 4.0, 
                           min_reviews: int = 10, radius: int = 5000, anti_hotels: bool = False,
                           wide_search: bool = False) -> Dict[str, Any]:
        """
        Démarrer le processus de scraping optimisé avec gestion des zones
        
        Args:
            location: Localisation à scraper
            business_type: Type d'entreprise
            max_results: Nombre maximum de résultats
            min_rating: Note minimum pour inclure l'entreprise
            min_reviews: Nombre minimum d'avis
            radius: Rayon de recherche en mètres
            anti_hotels: Booléen pour filtrer les hôtels
            
        Returns:
            Résultat du scraping avec statistiques
        """
        SystemLogger.info(f"🚀 [PIPELINE SMART] --- DÉBUT SCRAPING OPTIMISÉ ---")
        SystemLogger.info(f"📍 [PIPELINE SMART] Localisation: {location}")
        SystemLogger.info(f"🏢 [PIPELINE SMART] Type d'entreprise: {business_type or 'Tous'}")
        SystemLogger.info(f"📊 [PIPELINE SMART] Filtres: note >= {min_rating}, avis >= {min_reviews}")
        SystemLogger.info(f"📏 [PIPELINE SMART] Rayon: {radius}m")
        SystemLogger.info(f"🎯 [PIPELINE SMART] Max résultats: {max_results}")
        
        try:
            # Étape 1: Créer ou récupérer la zone
            SystemLogger.info(f"🗺️ [PIPELINE SMART] Étape 1: Création/récupération de la zone...")
            coordinates = self.google_maps_service._geocode_location(location)
            if not coordinates:
                SystemLogger.error(f"❌ [PIPELINE SMART] Impossible de géocoder la localisation: {location}")
                return {'success': False, 'message': 'Impossible de géocoder la localisation', 'leads_processed': 0}
            
            lat, lng = coordinates
            SystemLogger.info(f"✅ [PIPELINE SMART] Géocodage réussi: {lat:.6f}, {lng:.6f}")
            
            zone_nom = f"{location} - {business_type or 'Général'}"
            
            # Créer la zone si elle n'existe pas
            
            # Étape 2: Recherche continue jusqu'à obtenir le nombre de bars uniques souhaité
            SystemLogger.info(f"🔍 [PIPELINE SMART] Étape 2: Recherche continue Google Maps...")
            SystemLogger.info(f"🔍 [PIPELINE SMART] Mode recherche: {'LARGE' if wide_search else 'PRÉCIS'}")
            businesses = self.google_maps_service.search_continuous_until_target(
                location=location,
                target_count=max_results,
                business_type=business_type or "bar",
                radius=radius,
                min_rating=min_rating,
                min_reviews=min_reviews,
                max_pages_per_search=5,
                max_searches=10,
                wide_search=wide_search
            )
            
            # Filtre anti-hôtels si demandé
            if anti_hotels:
                businesses = [b for b in businesses if 'lodging' not in (b.get('types') or [])]
            SystemLogger.info(f"✅ [PIPELINE SMART] Recherche terminée: {len(businesses)} entreprises trouvées (anti_hotels={anti_hotels})")
            
            if not businesses:
                SystemLogger.warning(f"⚠️ [PIPELINE SMART] Aucune entreprise trouvée")
                return {'success': False, 'message': 'Aucune entreprise trouvée', 'leads_processed': 0}
            
            # Étape 3: Traitement de chaque entreprise
            SystemLogger.info(f"🔧 [PIPELINE SMART] Étape 3: Traitement des entreprises...")
            leads_created = 0
            leads_updated = 0
            total_api_cost = 0.005  # Coût du géocodage
            
            for i, business in enumerate(businesses):
                try:
                    name = business.get('name', 'N/A')
                    SystemLogger.info(f"🔧 [PIPELINE SMART] --- TRAITEMENT ENTREPRISE {i+1}/{len(businesses)} : {name} ---")
                    
                    # Validation des données de l'entreprise
                    if not business.get('place_id'):
                        SystemLogger.warning(f"⚠️ [PIPELINE SMART] Entreprise sans place_id: {name}")
                        continue
                    
                    lead = self._process_business_smart(business, None) # Pas de zone_id pour le scraping classique
                    if lead:
                        SystemLogger.info(f"✅ [PIPELINE SMART] Lead traité: {lead.nom} (ID: {lead.id})")
                        if lead.id:  # Lead existant mis à jour
                            leads_updated += 1
                            SystemLogger.info(f"🔄 [PIPELINE SMART] Lead mis à jour: {lead.nom}")
                        else:  # Nouveau lead
                            leads_created += 1
                            SystemLogger.info(f"🆕 [PIPELINE SMART] Nouveau lead créé: {lead.nom}")
                    else:
                        SystemLogger.warning(f"⚠️ [PIPELINE SMART] Échec du traitement: {name}")
                    
                    # Délai entre les requêtes
                    if i < len(businesses) - 1:
                        time.sleep(Config.DELAY_BETWEEN_REQUESTS)
                        
                except ValueError as e:
                    SystemLogger.error(f"❌ [PIPELINE SMART] Erreur de validation pour {business.get('name', 'N/A')}: {str(e)}")
                    continue
                except ConnectionError as e:
                    SystemLogger.error(f"❌ [PIPELINE SMART] Erreur de connexion pour {business.get('name', 'N/A')}: {str(e)}")
                    continue
                except Exception as e:
                    SystemLogger.error(f"❌ [PIPELINE SMART] Erreur inattendue pour {business.get('name', 'N/A')}: {str(e)}")
                    continue
            
            # Calculer le coût total (géocodage + Place Details)
            total_api_cost += len(businesses) * 0.0179
            
            SystemLogger.info(f"✅ [PIPELINE SMART] --- FIN TRAITEMENT ENTREPRISES ---")
            SystemLogger.info(f"📊 [PIPELINE SMART] Résultats finaux:")
            SystemLogger.info(f"   - Leads traités: {len(businesses)}")
            SystemLogger.info(f"   - Leads créés: {leads_created}")
            SystemLogger.info(f"   - Leads mis à jour: {leads_updated}")
            SystemLogger.info(f"💰 [PIPELINE SMART] Coût API total: ${total_api_cost:.4f}")
            
            # Sauvegarder les changements
            db.session.commit()
            SystemLogger.info(f"💾 [PIPELINE SMART] Commit DB effectué")
            result = {
                'success': True,
                'message': f'Scraping optimisé terminé avec succès',
                'leads_processed': len(businesses),
                'leads_created': leads_created,
                'leads_updated': leads_updated,
                'api_cost': total_api_cost,
                'optimization_savings': f"{(len(businesses) * 0.0179) - total_api_cost:.4f}"
            }
            
            SystemLogger.info(f"🎉 [PIPELINE SMART] --- FIN SCRAPING OPTIMISÉ ---")
            return result
            
        except Exception as e:
            SystemLogger.error(f"❌ [PIPELINE SMART] Erreur globale scraping: {str(e)}")
            db.session.rollback()
            return {'success': False, 'message': f'Erreur: {str(e)}', 'leads_processed': 0}
    
    def start_scraping(self, location: str, business_type: Optional[str] = "", max_results: int = 20) -> Dict[str, Any]:
        """
        Démarrer le processus de scraping classique
        
        Args:
            location: Localisation à scraper
            business_type: Type d'entreprise
            max_results: Nombre maximum de résultats
            
        Returns:
            Résultat du scraping
        """
        SystemLogger.info(f"🚀 [PIPELINE CLASSIC] --- DÉBUT SCRAPING CLASSIQUE ---")
        SystemLogger.info(f"📍 [PIPELINE CLASSIC] Localisation: {location}")
        SystemLogger.info(f"🏢 [PIPELINE CLASSIC] Type d'entreprise: {business_type or 'Tous'}")
        SystemLogger.info(f"🎯 [PIPELINE CLASSIC] Max résultats: {max_results}")
        
        try:
            # Recherche Google Maps
            SystemLogger.info(f"🔍 [PIPELINE CLASSIC] Recherche Google Maps...")
            businesses = self.google_maps_service.search_nearby(
                location=location,
                radius=5000,
                business_type=business_type,
                max_results=max_results
            )
            
            SystemLogger.info(f"✅ [PIPELINE CLASSIC] Recherche terminée: {len(businesses)} entreprises trouvées")
            
            if not businesses:
                SystemLogger.warning(f"⚠️ [PIPELINE CLASSIC] Aucune entreprise trouvée")
                return {'success': False, 'message': 'Aucune entreprise trouvée', 'leads_processed': 0}
            
            # Traitement de chaque entreprise
            SystemLogger.info(f"🔧 [PIPELINE CLASSIC] Traitement des entreprises...")
            leads_created = 0
            leads_updated = 0
            
            for i, business in enumerate(businesses):
                try:
                    name = business.get('name', 'N/A')
                    SystemLogger.info(f"🔧 [PIPELINE CLASSIC] --- TRAITEMENT ENTREPRISE {i+1}/{len(businesses)} : {name} ---")
                    
                    # Utiliser la méthode smart pour le traitement
                    lead = self._process_business_smart(business, None)  # Pas de zone_id pour le scraping classique
                    if lead:
                        SystemLogger.info(f"✅ [PIPELINE CLASSIC] Lead traité: {lead.nom} (ID: {lead.id})")
                        if lead.id:  # Lead existant mis à jour
                            leads_updated += 1
                            SystemLogger.info(f"🔄 [PIPELINE CLASSIC] Lead mis à jour: {lead.nom}")
                        else:  # Nouveau lead
                            leads_created += 1
                            SystemLogger.info(f"🆕 [PIPELINE CLASSIC] Nouveau lead créé: {lead.nom}")
                    else:
                        SystemLogger.warning(f"⚠️ [PIPELINE CLASSIC] Échec du traitement: {name}")
                    
                    # Délai entre les requêtes
                    if i < len(businesses) - 1:
                        time.sleep(Config.DELAY_BETWEEN_REQUESTS)
                        
                except Exception as e:
                    SystemLogger.error(f"❌ [PIPELINE CLASSIC] Erreur lors du traitement de l'entreprise {business.get('name', 'N/A')}: {str(e)}")
                    continue
            
            # Sauvegarder les changements
            db.session.commit()
            SystemLogger.info(f"💾 [PIPELINE CLASSIC] Commit DB effectué")
            
            result = {
                'success': True,
                'message': f'Scraping classique terminé avec succès',
                'leads_processed': len(businesses),
                'leads_created': leads_created,
                'leads_updated': leads_updated
            }
            
            SystemLogger.info(f"🎉 [PIPELINE CLASSIC] --- FIN SCRAPING CLASSIQUE ---")
            return result
            
        except Exception as e:
            SystemLogger.error(f"❌ [PIPELINE CLASSIC] Erreur globale scraping: {str(e)}")
            db.session.rollback()
            return {'success': False, 'message': f'Erreur: {str(e)}', 'leads_processed': 0}
    
    def _process_business_smart(self, business_data: Dict[str, Any], zone_id: Optional[int] = None) -> Optional[Lead]:
        """Traiter une entreprise avec les nouvelles fonctionnalités optimisées"""
        SystemLogger.info(f"🔧 [PROCESS SMART] Début du traitement: {business_data.get('name')}")
        
        # Vérifier si le lead existe déjà
        lead = Lead.query.filter_by(nom=business_data.get('name')).first()
        
        if not lead:
            # Créer un nouveau lead
            SystemLogger.info(f"🆕 [PROCESS SMART] Création d'un nouveau lead")
            lead = Lead()
            lead.nom = business_data.get('name')
            
            # Stocker les données Google Maps dans les champs dédiés
            lead.google_maps_adresse = business_data.get('address') or business_data.get('formatted_address')
            lead.google_maps_telephone = business_data.get('phone') or business_data.get('formatted_phone_number')
            
            # Garder les champs existants pour compatibilité
            lead.adresse = business_data.get('address') or business_data.get('formatted_address')
            lead.telephone = business_data.get('phone') or business_data.get('formatted_phone_number')
            
            lead.note_google = business_data.get('rating')
            lead.nb_avis_google = business_data.get('user_ratings_total')
            lead.business_type = business_data.get('business_type')  # Type réel de Google Places
            
            # Stocker les coordonnées GPS
            latitude = business_data.get('latitude')
            longitude = business_data.get('longitude')
            if latitude and longitude:
                lead.latitude = latitude
                lead.longitude = longitude
                SystemLogger.info(f"📍 [PROCESS SMART] Coordonnées GPS stockées: {latitude:.6f}, {longitude:.6f}")
            else:
                SystemLogger.warning(f"⚠️ [PROCESS SMART] Coordonnées GPS manquantes")
            
            lead.statut_scraping = 'en_cours'
            
            db.session.add(lead)
            db.session.flush()  # Pour obtenir l'ID
            SystemLogger.info(f"✅ [PROCESS SMART] Nouveau lead créé avec ID: {lead.id}")
        else:
            SystemLogger.info(f"🔄 [PROCESS SMART] Lead existant trouvé: {lead.nom} (ID: {lead.id})")
            # Mettre à jour le business_type si pas encore défini
            if not lead.business_type and business_data.get('business_type'):
                lead.business_type = business_data.get('business_type')
                SystemLogger.info(f"🔄 [PROCESS SMART] Business type mis à jour: {lead.business_type}")
        
        # Logger pour ce lead
        lead_logger = LeadLogger(lead.id, lead.nom)
        lead_logger.info("🚀 [PROCESS SMART] Début du traitement optimisé")
        
        try:
            # Étape 1: Validation des données Google Maps
            if not business_data.get('name'):
                raise ValueError("Nom de l'entreprise manquant")
            
            lead_logger.info("✅ [PROCESS SMART] Étape 1: Données Google Maps OK")
            # Étape 1: Données Google Maps
            lead.update_log("google_maps_scraped: OK")
            
            # Étape 2: Site web
            website_url = business_data.get('website')
            if website_url and is_valid_url(website_url):
                lead_logger.info(f"🌐 [PROCESS SMART] Étape 2: Site web trouvé: {website_url}")
                lead.site_web = website_url
                lead_logger.info(f"✅ [PROCESS SMART] Site web enregistré: {website_url}")
                
                # Vérifier si c'est un réseau social
                is_social, platform = is_social_media_url(website_url)
                if is_social:
                    lead_logger.info(f"📱 [PROCESS SMART] URL détectée comme réseau social: {platform}")
                    if platform == 'facebook':
                        lead_logger.info(f"📘 [PROCESS SMART] Facebook détecté: {website_url}")
                        lead.facebook_url = website_url
                    elif platform == 'instagram':
                        lead_logger.info(f"📷 [PROCESS SMART] Instagram détecté: {website_url}")
                        lead.instagram_url = website_url
                    
                    # Scraper le réseau social
                    self._scrape_social_media(lead, lead_logger)
                else:
                    lead_logger.info(f"🌐 [PROCESS SMART] Scraping du site web classique...")
                    # Scraper le site web
                    self._scrape_website(lead, lead_logger)
                    
                    # APRÈS l'analyse IA du site web, vérifier si des réseaux sociaux ont été trouvés
                    if lead.ai_analysis:
                        reseaux_sociaux = lead.ai_analysis.get('reseaux_sociaux', {})
                        facebook_found = False
                        instagram_found = False
                        
                        if reseaux_sociaux.get('facebook'):
                            lead_logger.info(f"📘 [PROCESS SMART] Facebook trouvé via IA: {reseaux_sociaux['facebook']}")
                            lead.facebook_url = reseaux_sociaux['facebook']
                            facebook_found = True
                        
                        if reseaux_sociaux.get('instagram'):
                            lead_logger.info(f"📷 [PROCESS SMART] Instagram trouvé via IA: {reseaux_sociaux['instagram']}")
                            lead.instagram_url = reseaux_sociaux['instagram']
                            instagram_found = True
                        
                        # Lancer l'analyse IA des réseaux sociaux si au moins un a été trouvé
                        if facebook_found or instagram_found:
                            lead_logger.info("[PROCESS SMART] Lancement de l'analyse IA des réseaux sociaux...")
                            self._scrape_social_media(lead, lead_logger)
            else:
                lead_logger.info("⚠️ [PROCESS SMART] Aucun site web valide trouvé")
                lead.update_log("site_web: NOK (pas d'URL)")
            
            # Étape 3: Réseaux sociaux (si pas déjà fait)
            if not lead.facebook_url and business_data.get('facebook_url'):
                lead_logger.info(f"📘 [PROCESS SMART] Facebook additionnel détecté: {business_data.get('facebook_url')}")
                lead.facebook_url = business_data.get('facebook_url')
                self._scrape_social_media(lead, lead_logger)
            
            if not lead.instagram_url and business_data.get('instagram_url'):
                lead_logger.info(f"📷 [PROCESS SMART] Instagram additionnel détecté: {business_data.get('instagram_url')}")
                lead.instagram_url = business_data.get('instagram_url')
                self._scrape_social_media(lead, lead_logger)
            
            # Finaliser le statut
            lead.set_statut('succès')
            lead.update_log("status: succès")
            lead_logger.info("✅ [PROCESS SMART] Statut scraping finalisé à 'succès'")

            # Appel du scoring IA (RAG) pour générer l'argumentaire
            try:
                from app.services.ai_analysis_service import AIAnalysisService
                ai_service = AIAnalysisService()
                ai_result = ai_service.score_lead_with_rag(lead)
                
                # Stocker les résultats du scoring IA
                if ai_result.get('score'):
                    lead.score_ia = ai_result['score']
                if ai_result.get('argumentaire'):
                    lead.argumentaire_ia = ai_result['argumentaire']
                
                lead_logger.info(f"✅ [PROCESS SMART] Scoring IA effectué: {ai_result}")
            except Exception as e:
                lead_logger.error(f"❌ [PROCESS SMART] Erreur scoring IA: {str(e)}")

            SystemLogger.info(f"✅ [PROCESS SMART] Traitement terminé avec succès: {lead.nom}")
            return lead
            
        except Exception as e:
            lead_logger.error(f"❌ [PROCESS SMART] Erreur lors du traitement: {str(e)}")
            lead.set_statut('erreur')
            lead.update_log(f"error: {str(e)}")
            SystemLogger.error(f"❌ [PROCESS SMART] Erreur lors du traitement de {lead.nom}: {str(e)}")
            return None
    
    def _scrape_website(self, lead: Lead, logger: LeadLogger):
        """
        Scrape le site web avec le nouveau système IA
        """
        if not lead.site_web:
            logger.info("❌ Pas d'URL de site web à scraper")
            return
        
        try:
            logger.info(f"🌐 [WEBSITE] Début scraping IA pour {lead.site_web}")
            
            # Validation de l'URL
            if not is_valid_url(lead.site_web):
                logger.error(f"❌ [WEBSITE] URL invalide: {lead.site_web}")
                return
            
            # Utiliser le nouveau scraper IA
            scraper = ScrapyWebsiteScraperImproved()
            result = scraper.scrape_website_with_ai(lead.site_web)
            
            if result and result.get('scraping_success'):
                ai_analysis = result.get('ai_analysis', {})
                
                # Mettre à jour le lead avec les données IA
                self._update_lead_with_ai_analysis(lead, ai_analysis, logger)
                
                logger.info(f"✅ [WEBSITE] Scraping IA terminé pour {lead.site_web}")
            else:
                error_msg = result.get('error', 'Erreur inconnue') if result else 'Pas de résultat'
                logger.error(f"❌ [WEBSITE] Échec du scraping IA pour {lead.site_web}: {error_msg}")
                
        except ConnectionError as e:
            logger.error(f"❌ [WEBSITE] Erreur de connexion pour {lead.site_web}: {str(e)}")
        except TimeoutError as e:
            logger.error(f"❌ [WEBSITE] Timeout pour {lead.site_web}: {str(e)}")
        except ValueError as e:
            logger.error(f"❌ [WEBSITE] Erreur de validation pour {lead.site_web}: {str(e)}")
        except Exception as e:
            logger.error(f"❌ [WEBSITE] Erreur inattendue pour {lead.site_web}: {str(e)}")
    
    def _update_lead_with_ai_analysis(self, lead: Lead, ai_analysis: Dict[str, Any], logger: LeadLogger):
        """
        Met à jour le lead avec les données de l'analyse IA (site web)
        """
        try:
            # Contact (Site Web)
            contact = ai_analysis.get('contact', {})
            if contact.get('emails'):
                lead.site_web_email = contact['emails'][0]
            if contact.get('telephones'):
                lead.site_web_telephone = contact['telephones'][0]
            if contact.get('adresse'):
                lead.site_web_adresse = contact['adresse']
            
            # Entreprise (Site Web)
            entreprise = ai_analysis.get('entreprise', {})
            if entreprise.get('description'):
                lead.site_web_description = entreprise['description']
            
            # Informations pratiques (Site Web)
            pratique = ai_analysis.get('pratique', {})
            if pratique.get('horaires'):
                lead.site_web_horaires = pratique['horaires']
            if pratique.get('services'):
                lead.site_web_services = ', '.join(pratique['services']) if isinstance(pratique['services'], list) else pratique['services']
            
            # Réseaux sociaux (Site Web) - avec validation des URLs
            reseaux = ai_analysis.get('reseaux_sociaux', {})
            if reseaux.get('facebook'):
                facebook_url = reseaux['facebook']
                # Validation de l'URL Facebook
                if is_valid_url(facebook_url) and 'facebook.com' in facebook_url and not any(ext in facebook_url.lower() for ext in ['.css', '.js', '.png', '.jpg', '.gif', '.ico', '.svg', '.woff', '.ttf']):
                    lead.facebook_url = facebook_url
                    logger.info(f"📘 [LEAD] Facebook trouvé via IA: {facebook_url}")
                else:
                    logger.warning(f"⚠️ [LEAD] URL Facebook invalide ignorée: {facebook_url}")
            
            if reseaux.get('instagram'):
                instagram_url = reseaux['instagram']
                # Validation de l'URL Instagram
                if is_valid_url(instagram_url) and 'instagram.com' in instagram_url and not any(ext in instagram_url.lower() for ext in ['.css', '.js', '.png', '.jpg', '.gif', '.ico', '.svg', '.woff', '.ttf']):
                    lead.instagram_url = instagram_url
                    logger.info(f"📷 [LEAD] Instagram trouvé via IA: {instagram_url}")
                else:
                    logger.warning(f"⚠️ [LEAD] URL Instagram invalide ignorée: {instagram_url}")
            
            # Sauvegarder l'analyse IA complète
            lead.ai_analysis = ai_analysis
            
            # Sauvegarder en base
            db.session.commit()
            
            logger.info(f"✅ [LEAD] Données site web mises à jour")
            
        except Exception as e:
            logger.error(f"❌ [LEAD] Erreur mise à jour lead: {str(e)}")
    
    def _scrape_social_media(self, lead: Lead, logger: LeadLogger):
        """Nouvelle méthode : Capture d'écran + analyse IA des réseaux sociaux"""
        logger.info("[PIPELINE] --- DÉBUT SCRAPING SOCIAL MEDIA ---")
        try:
            logger.info("[PIPELINE] Capture d'écran des réseaux sociaux...")
            # Préparer les données du lead pour la capture
            lead_data = {
                'id': lead.id,
                'facebook_url': lead.facebook_url,
                'instagram_url': lead.instagram_url
            }
            
            # Étape 1: Capture d'écran
            screenshots = self.screenshot_service.capture_social_media(lead_data)
            
            # Sauvegarder les chemins des captures d'écran
            if screenshots.get('facebook_screenshot'):
                lead.facebook_screenshot_path = screenshots['facebook_screenshot']
                logger.info(f"Capture Facebook sauvegardée: {lead.facebook_screenshot_path}")
            
            if screenshots.get('instagram_screenshot'):
                lead.instagram_screenshot_path = screenshots['instagram_screenshot']
                logger.info(f"Capture Instagram sauvegardée: {lead.instagram_screenshot_path}")
            
            # Étape 2: Analyse IA des captures d'écran
            logger.info("[PIPELINE] Analyse IA des captures d'écran...")
            ai_service = AIAnalysisService()
            
            # Analyser chaque screenshot séparément
            ai_results = {}
            if screenshots.get('facebook_screenshot'):
                fb_result = ai_service.analyze_social_media_screenshots(screenshots['facebook_screenshot'], 'facebook')
                ai_results['facebook_data'] = fb_result
                
                # Stocker les données Facebook dans les champs appropriés
                if fb_result.get('followers'):
                    followers_str = fb_result['followers']
                    try:
                        # Nettoyer la chaîne et gérer les minuscules
                        followers_clean = followers_str.strip().upper()
                        if 'K' in followers_clean:
                            followers_num = float(followers_clean.replace('K', '').replace(',', '.').replace(' ', '')) * 1000
                            lead.nb_followers_facebook = int(followers_num)
                        elif 'M' in followers_clean:
                            followers_num = float(followers_clean.replace('M', '').replace(',', '.').replace(' ', '')) * 1000000
                            lead.nb_followers_facebook = int(followers_num)
                        else:
                            # Essayer de convertir directement
                            followers_clean = followers_str.replace(',', '').replace(' ', '')
                            lead.nb_followers_facebook = int(followers_clean)
                    except Exception as e:
                        logger.warning(f"Erreur conversion followers Facebook: {str(e)}")
                        # Essayer une conversion plus robuste
                        try:
                            import re
                            # Extraire les chiffres avec regex
                            numbers = re.findall(r'\d+(?:\.\d+)?', followers_str)
                            if numbers:
                                if 'k' in followers_str.lower():
                                    lead.nb_followers_facebook = int(float(numbers[0]) * 1000)
                                elif 'm' in followers_str.lower():
                                    lead.nb_followers_facebook = int(float(numbers[0]) * 1000000)
                                else:
                                    lead.nb_followers_facebook = int(float(numbers[0]))
                                logger.info(f"✅ Conversion followers Facebook réussie avec regex: {lead.nb_followers_facebook}")
                        except Exception as e2:
                            logger.warning(f"Échec conversion followers Facebook avec regex: {str(e2)}")
                
                if fb_result.get('likes') and fb_result['likes'] != 'Non visible':
                    likes_str = fb_result['likes']
                    try:
                        # Nettoyer la chaîne et gérer les minuscules
                        likes_clean = likes_str.strip().upper()
                        if 'K' in likes_clean:
                            likes_num = float(likes_clean.replace('K', '').replace(',', '.').replace(' ', '')) * 1000
                            lead.nb_likes_facebook = int(likes_num)
                        elif 'M' in likes_clean:
                            likes_num = float(likes_clean.replace('M', '').replace(',', '.').replace(' ', '')) * 1000000
                            lead.nb_likes_facebook = int(likes_num)
                        else:
                            # Essayer de convertir directement
                            likes_clean = likes_str.replace(',', '').replace(' ', '')
                            lead.nb_likes_facebook = int(likes_clean)
                    except Exception as e:
                        logger.warning(f"Erreur conversion likes Facebook: {str(e)}")
                        # Essayer une conversion plus robuste
                        try:
                            import re
                            # Extraire les chiffres avec regex
                            numbers = re.findall(r'\d+(?:\.\d+)?', likes_str)
                            if numbers:
                                if 'k' in likes_str.lower():
                                    lead.nb_likes_facebook = int(float(numbers[0]) * 1000)
                                elif 'm' in likes_str.lower():
                                    lead.nb_likes_facebook = int(float(numbers[0]) * 1000000)
                                else:
                                    lead.nb_likes_facebook = int(float(numbers[0]))
                                logger.info(f"✅ Conversion likes Facebook réussie avec regex: {lead.nb_likes_facebook}")
                        except Exception as e2:
                            logger.warning(f"Échec conversion likes Facebook avec regex: {str(e2)}")
                
                # Stocker l'intro Facebook (informations complètes)
                if fb_result.get('intro'):
                    lead.intro_facebook = fb_result['intro']
                elif fb_result.get('description'):
                    lead.description_facebook = fb_result['description']
                
                # Stocker les informations de contact Facebook
                if fb_result.get('contact_info') and isinstance(fb_result['contact_info'], dict):
                    contact = fb_result['contact_info']
                    if contact.get('phone') and contact['phone'] != 'Non visible':
                        lead.facebook_telephone = contact['phone']
                    if contact.get('email') and contact['email'] != 'Non visible':
                        lead.facebook_email = contact['email']
                    if contact.get('address') and contact['address'] != 'Non visible':
                        lead.facebook_adresse = contact['address']
                    if contact.get('website') and contact['website'] != 'Non visible':
                        lead.facebook_site_web = contact['website']
                
                # Créer une chaîne de statistiques pour l'affichage
                stats_parts = []
                if fb_result.get('followers'):
                    stats_parts.append(f"{fb_result['followers']} followers")
                if fb_result.get('likes') and fb_result['likes'] != 'Non visible':
                    stats_parts.append(f"{fb_result['likes']} likes")
                if stats_parts:
                    lead.facebook_stats = " • ".join(stats_parts)
            
            if screenshots.get('instagram_screenshot'):
                insta_result = ai_service.analyze_social_media_screenshots(screenshots['instagram_screenshot'], 'instagram')
                ai_results['instagram_data'] = insta_result
                
                # Stocker les données Instagram dans les champs appropriés
                if insta_result.get('followers'):
                    followers_str = insta_result['followers']
                    try:
                        # Nettoyer la chaîne et gérer les minuscules
                        followers_clean = followers_str.strip().upper()
                        if 'K' in followers_clean:
                            followers_num = float(followers_clean.replace('K', '').replace(',', '.').replace(' ', '')) * 1000
                            lead.nb_followers_instagram = int(followers_num)
                        elif 'M' in followers_clean:
                            followers_num = float(followers_clean.replace('M', '').replace(',', '.').replace(' ', '')) * 1000000
                            lead.nb_followers_instagram = int(followers_num)
                        else:
                            # Essayer de convertir directement
                            followers_clean = followers_str.replace(',', '').replace(' ', '')
                            lead.nb_followers_instagram = int(followers_clean)
                    except Exception as e:
                        logger.warning(f"Erreur conversion followers Instagram: {str(e)}")
                        # Essayer une conversion plus robuste
                        try:
                            import re
                            # Extraire les chiffres avec regex
                            numbers = re.findall(r'\d+(?:\.\d+)?', followers_str)
                            if numbers:
                                if 'k' in followers_str.lower():
                                    lead.nb_followers_instagram = int(float(numbers[0]) * 1000)
                                elif 'm' in followers_str.lower():
                                    lead.nb_followers_instagram = int(float(numbers[0]) * 1000000)
                                else:
                                    lead.nb_followers_instagram = int(float(numbers[0]))
                                logger.info(f"✅ Conversion followers Instagram réussie avec regex: {lead.nb_followers_instagram}")
                        except Exception as e2:
                            logger.warning(f"Échec conversion followers Instagram avec regex: {str(e2)}")
                
                # Traiter le following Instagram
                if insta_result.get('following'):
                    following_str = insta_result['following']
                    try:
                        # Nettoyer la chaîne et gérer les minuscules
                        following_clean = following_str.strip().upper()
                        if 'K' in following_clean:
                            following_num = float(following_clean.replace('K', '').replace(',', '.').replace(' ', '')) * 1000
                            lead.nb_following_instagram = int(following_num)
                        elif 'M' in following_clean:
                            following_num = float(following_clean.replace('M', '').replace(',', '.').replace(' ', '')) * 1000000
                            lead.nb_following_instagram = int(following_num)
                        else:
                            # Essayer de convertir directement
                            following_clean = following_str.replace(',', '').replace(' ', '')
                            lead.nb_following_instagram = int(following_clean)
                    except Exception as e:
                        logger.warning(f"Erreur conversion following Instagram: {str(e)}")
                        # Essayer une conversion plus robuste
                        try:
                            import re
                            # Extraire les chiffres avec regex
                            numbers = re.findall(r'\d+(?:\.\d+)?', following_str)
                            if numbers:
                                if 'k' in following_str.lower():
                                    lead.nb_following_instagram = int(float(numbers[0]) * 1000)
                                elif 'm' in following_str.lower():
                                    lead.nb_following_instagram = int(float(numbers[0]) * 1000000)
                                else:
                                    lead.nb_following_instagram = int(float(numbers[0]))
                                logger.info(f"✅ Conversion following Instagram réussie avec regex: {lead.nb_following_instagram}")
                        except Exception as e2:
                            logger.warning(f"Échec conversion following Instagram avec regex: {str(e2)}")
                
                if insta_result.get('posts'):
                    posts_str = insta_result['posts']
                    try:
                        # Nettoyer la chaîne et gérer les minuscules
                        posts_clean = posts_str.strip().upper()
                        if 'K' in posts_clean:
                            posts_num = float(posts_clean.replace('K', '').replace(',', '.').replace(' ', '')) * 1000
                            lead.nb_posts_instagram = int(posts_num)
                        elif 'M' in posts_clean:
                            posts_num = float(posts_clean.replace('M', '').replace(',', '.').replace(' ', '')) * 1000000
                            lead.nb_posts_instagram = int(posts_num)
                        else:
                            # Essayer de convertir directement
                            posts_clean = posts_str.replace(',', '').replace(' ', '')
                            lead.nb_posts_instagram = int(posts_clean)
                    except Exception as e:
                        logger.warning(f"Erreur conversion posts Instagram: {str(e)}")
                        # Essayer une conversion plus robuste
                        try:
                            import re
                            # Extraire les chiffres avec regex
                            numbers = re.findall(r'\d+(?:\.\d+)?', posts_str)
                            if numbers:
                                if 'k' in posts_str.lower():
                                    lead.nb_posts_instagram = int(float(numbers[0]) * 1000)
                                elif 'm' in posts_str.lower():
                                    lead.nb_posts_instagram = int(float(numbers[0]) * 1000000)
                                else:
                                    lead.nb_posts_instagram = int(float(numbers[0]))
                                logger.info(f"✅ Conversion posts Instagram réussie avec regex: {lead.nb_posts_instagram}")
                        except Exception as e2:
                            logger.warning(f"Échec conversion posts Instagram avec regex: {str(e2)}")
                
                # Stocker la bio Instagram
                if insta_result.get('bio'):
                    lead.bio_instagram = insta_result['bio']
                elif insta_result.get('description'):
                    lead.bio_instagram = insta_result['description']
                
                # Stocker les informations de contact Instagram
                if insta_result.get('contact_info') and isinstance(insta_result['contact_info'], dict):
                    contact = insta_result['contact_info']
                    if contact.get('phone') and contact['phone'] != 'Non visible':
                        lead.instagram_telephone = contact['phone']
                    if contact.get('email') and contact['email'] != 'Non visible':
                        lead.instagram_email = contact['email']
                    if contact.get('address') and contact['address'] != 'Non visible':
                        lead.instagram_adresse = contact['address']
                    if contact.get('website') and contact['website'] != 'Non visible':
                        lead.instagram_site_web = contact['website']
                
                # Créer une chaîne de statistiques pour l'affichage
                stats_parts = []
                if insta_result.get('followers'):
                    stats_parts.append(f"{insta_result['followers']} followers")
                if insta_result.get('posts'):
                    stats_parts.append(f"{insta_result['posts']} posts")
                if stats_parts:
                    lead.instagram_stats = " • ".join(stats_parts)
            
            # Traiter les résultats Facebook et Instagram (données déjà traitées dans les sections précédentes)
            if ai_results.get('facebook_data'):
                fb_data = ai_results['facebook_data']
                logger.info(f"📊 [FACEBOOK] Données extraites: {fb_data}")
                lead.update_ai_log(f"Analyse Facebook IA réussie: {lead.nb_followers_facebook} followers")
            
            if ai_results.get('instagram_data'):
                insta_data = ai_results['instagram_data']
                logger.info(f"📊 [INSTAGRAM] Données extraites: {insta_data}")
                lead.update_ai_log(f"Analyse Instagram IA réussie: {lead.nb_followers_instagram} followers")
            
            # Étape 3: SCORING D'OPPORTUNITÉ (NOUVELLE ÉTAPE)
            logger.info("[PIPELINE] Calcul du score d'opportunité...")
            try:
                # Calculer le score d'opportunité basé sur les données collectées
                score = self._calculate_opportunity_score(lead)
                lead.score_opportunite = score
                lead.update_ai_log(f"Score d'opportunité calculé: {score}/100")
                logger.info(f"Score d'opportunité: {score}/100")
            except Exception as e:
                logger.error(f"Erreur calcul score d'opportunité: {str(e)}")
                lead.update_ai_log(f"Erreur calcul score: {str(e)}")
            
            # Finaliser le statut
            if ai_results.get('analysis_success'):
                lead.set_ai_status('succès')
                lead.update_ai_log("Analyse IA terminée avec succès")
            else:
                lead.set_ai_status('erreur')
                lead.update_ai_log("Erreur lors de l'analyse IA")
            
            logger.info("[PIPELINE] Commit DB après social media.")
            db.session.commit()
            logger.info("Analyse IA des réseaux sociaux terminée avec succès")
            
        except Exception as e:
            logger.error(f"Erreur lors de l'analyse IA des réseaux sociaux: {str(e)}")
            lead.set_ai_status('erreur')
            lead.update_ai_log(f"Erreur: {str(e)}")
            db.session.commit()
    
    def _calculate_opportunity_score(self, lead: Lead) -> float:
        """
        Calculer un score d'opportunité (0-100) basé sur les données du lead
        
        Args:
            lead: Le lead à analyser
            
        Returns:
            Score d'opportunité entre 0 et 100
        """
        score = 0.0
        
        # 1. Score Google Maps (25 points max)
        if lead.note_google:
            # Note Google (0-5) → 0-15 points
            score += (lead.note_google / 5.0) * 15
        if lead.nb_avis_google:
            # Nombre d'avis → 0-10 points (plus d'avis = plus d'engagement)
            if lead.nb_avis_google >= 100:
                score += 10
            elif lead.nb_avis_google >= 50:
                score += 7
            elif lead.nb_avis_google >= 20:
                score += 5
            elif lead.nb_avis_google >= 10:
                score += 3
            else:
                score += 1
        
        # 2. Score Site Web (20 points max)
        if lead.site_web:
            score += 5  # Présence d'un site web
            if lead.has_video_on_site:
                score += 5  # Présence de vidéos
            if lead.has_images_on_site:
                score += 3  # Présence d'images
            if lead.contact_form_detecte:
                score += 3  # Formulaire de contact
            if lead.produits_services_detectes:
                score += 2  # Produits/services détectés
            if lead.email:
                score += 2  # Email de contact
        
        # 3. Score Facebook (25 points max)
        if lead.facebook_url:
            score += 5  # Présence Facebook
            if lead.nb_followers_facebook:
                # Followers Facebook → 0-15 points
                if lead.nb_followers_facebook >= 10000:
                    score += 15
                elif lead.nb_followers_facebook >= 5000:
                    score += 12
                elif lead.nb_followers_facebook >= 1000:
                    score += 10
                elif lead.nb_followers_facebook >= 500:
                    score += 7
                elif lead.nb_followers_facebook >= 100:
                    score += 5
                else:
                    score += 2
            if lead.description_facebook:
                score += 3  # Description présente
            if lead.intro_facebook:
                score += 2  # Intro complète
        
        # 4. Score Instagram (20 points max)
        if lead.instagram_url or lead.instagram_handle:
            score += 5  # Présence Instagram
            if lead.nb_followers_instagram:
                # Followers Instagram → 0-10 points
                if lead.nb_followers_instagram >= 10000:
                    score += 10
                elif lead.nb_followers_instagram >= 5000:
                    score += 8
                elif lead.nb_followers_instagram >= 1000:
                    score += 6
                elif lead.nb_followers_instagram >= 500:
                    score += 4
                elif lead.nb_followers_instagram >= 100:
                    score += 2
                else:
                    score += 1
            if lead.nb_posts_instagram and lead.nb_posts_instagram > 10:
                score += 3  # Activité régulière
            if lead.bio_instagram:
                score += 2  # Bio présente
        
        # 5. Score Type d'Entreprise (10 points max)
        # Prioriser certains types d'entreprises pour la vidéo
        if lead.business_type:
            high_value_types = [
                'restaurant', 'bar', 'cafe', 'hotel', 'spa', 'salon', 
                'gym', 'fitness', 'art_gallery', 'museum', 'theater',
                'event_venue', 'wedding_venue', 'tourist_attraction'
            ]
            if any(high_type in lead.business_type.lower() for high_type in high_value_types):
                score += 10
            elif 'retail' in lead.business_type.lower() or 'store' in lead.business_type.lower():
                score += 7
            else:
                score += 3
        
        # Limiter le score à 100
        return min(score, 100.0)
    
    def get_leads(self, limit: int = 50) -> List[Lead]:
        """Récupérer les leads"""
        return Lead.query.order_by(Lead.created_at.desc()).limit(limit).all()
    
    def get_lead_by_id(self, lead_id: int) -> Optional[Lead]:
        """Récupérer un lead par ID"""
        return Lead.query.get(lead_id)
    
    def get_business_types(self) -> List[str]:
        """Récupérer les types d'entreprises disponibles"""
        return self.google_maps_service.get_business_types()
    
    def _is_valid_facebook_page(self, url: str) -> bool:
        """Vérifie si l'URL Facebook est une page publique (pas un partage, post, event, etc.)"""
        if not url or 'facebook.com/' not in url:
            return False
        # Exclure les liens de partage, posts, events, groups, etc.
        exclure = ['/sharer', '/share', '/post', '/posts', '/events', '/groups', '/watch', '/permalink', '/media', '/photos', '/login', '/pages', '/search', '/reel', '/reels', '/story', '/stories']
        for exclu in exclure:
            if exclu in url:
                return False
        # Doit ressembler à https://www.facebook.com/nomdelapage
        path = url.split('facebook.com/')[-1].split('?')[0].split('/')[0]
        return bool(path) and len(path) > 2
    
    def recalculate_all_opportunity_scores(self) -> Dict[str, Any]:
        """
        Recalculer les scores d'opportunité pour tous les leads existants
        
        Returns:
            Résultat du recalcul avec statistiques
        """
        SystemLogger.info("🔄 [SCORING] Début du recalcul des scores d'opportunité...")
        
        try:
            # Récupérer tous les leads
            leads = Lead.query.all()
            SystemLogger.info(f"📊 [SCORING] {len(leads)} leads à traiter")
            
            scores_updated = 0
            scores_unchanged = 0
            errors = 0
            
            for i, lead in enumerate(leads):
                try:
                    SystemLogger.info(f"🔧 [SCORING] Traitement lead {i+1}/{len(leads)}: {lead.nom}")
                    
                    # Calculer le nouveau score
                    new_score = self._calculate_opportunity_score(lead)
                    old_score = lead.score_opportunite
                    
                    # Mettre à jour le score
                    lead.score_opportunite = new_score
                    
                    if old_score != new_score:
                        scores_updated += 1
                        SystemLogger.info(f"🔄 [SCORING] Score mis à jour: {old_score} → {new_score}")
                    else:
                        scores_unchanged += 1
                        SystemLogger.info(f"✅ [SCORING] Score inchangé: {new_score}")
                    
                    # Commit tous les 10 leads pour éviter les timeouts
                    if (i + 1) % 10 == 0:
                        db.session.commit()
                        SystemLogger.info(f"💾 [SCORING] Commit intermédiaire ({i+1}/{len(leads)})")
                        
                except Exception as e:
                    errors += 1
                    SystemLogger.error(f"❌ [SCORING] Erreur pour {lead.nom}: {str(e)}")
                    continue
            
            # Commit final
            db.session.commit()
            
            result = {
                'success': True,
                'message': 'Recalcul des scores terminé',
                'total_leads': len(leads),
                'scores_updated': scores_updated,
                'scores_unchanged': scores_unchanged,
                'errors': errors
            }
            
            SystemLogger.info(f"🎉 [SCORING] Recalcul terminé:")
            SystemLogger.info(f"   - Total leads: {len(leads)}")
            SystemLogger.info(f"   - Scores mis à jour: {scores_updated}")
            SystemLogger.info(f"   - Scores inchangés: {scores_unchanged}")
            SystemLogger.info(f"   - Erreurs: {errors}")
            
            return result
            
        except Exception as e:
            SystemLogger.error(f"❌ [SCORING] Erreur globale recalcul: {str(e)}")
            db.session.rollback()
            return {
                'success': False,
                'message': f'Erreur: {str(e)}',
                'total_leads': 0,
                'scores_updated': 0,
                'scores_unchanged': 0,
                'errors': 1
            } 