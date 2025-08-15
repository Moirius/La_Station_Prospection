"""
Scraper Google Maps V2 avec recherche continue jusqu'à obtenir le nombre de bars uniques souhaité
Évite les doublons et continue à chercher intelligemment
"""

import time
import os
from typing import List, Dict, Any, Optional

import googlemaps
from googlemaps import exceptions
from googlemaps.places import places_nearby, place
from googlemaps.geocoding import geocode

from app.config import Config
from app.utils.logger import get_logger

logger = get_logger('google_maps_scraper_v2_continuous')

class GoogleMapsScraperV2Continuous:
    """Scraper avec recherche continue jusqu'à obtenir le nombre de bars uniques souhaité"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or Config.GOOGLE_PLACES_API_KEY
        if not self.api_key:
            logger.error("Clé API Google Places manquante")
            raise ValueError("Clé API Google Places requise")
        
        logger.info(f"Initialisation du scraper Google Maps V2 Continuous avec clé API: {self.api_key[:10]}...")
        
        # Initialiser le client officiel Google
        try:
            self.client = googlemaps.Client(
                key=self.api_key,
                timeout=Config.REQUEST_TIMEOUT,
                retry_timeout=60,
                queries_per_second=10,
                queries_per_minute=600,
                retry_over_query_limit=True
            )
            logger.info("✅ Client Google Maps officiel initialisé avec succès")
        except Exception as e:
            logger.error(f"❌ Erreur lors de l'initialisation du client Google: {str(e)}")
            raise
    
    def _check_database_duplicates(self, bars: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Vérifier les doublons en base de données et retourner seulement les bars uniques"""
        try:
            from app.database.models import Lead
            from app.database.database import db
            
            # Récupérer tous les noms de leads existants en base
            existing_leads = Lead.query.with_entities(Lead.nom).all()
            existing_names = {lead.nom.lower() for lead in existing_leads if lead.nom}
            
            unique_bars = []
            doublons_db = 0
            
            for bar in bars:
                bar_name = bar.get('name', '').lower()
                if bar_name and bar_name not in existing_names:
                    unique_bars.append(bar)
                else:
                    doublons_db += 1
            
            logger.info(f"🛡️ [CONTINUOUS] Doublons en base évités: {doublons_db}")
            logger.info(f"✅ [CONTINUOUS] Bars uniques (pas en base): {len(unique_bars)}")
            
            return unique_bars
            
        except Exception as e:
            logger.error(f"❌ [CONTINUOUS] Erreur lors de la vérification des doublons en base: {str(e)}")
            return bars  # Retourner tous les bars en cas d'erreur

    def search_continuous_until_target(self, location: str, target_count: int = 250, 
                                     business_type: str = "bar", radius: int = 5000,
                                     min_rating: float = 4.0, min_reviews: int = 10,
                                     max_pages_per_search: int = 5, 
                                     max_searches: int = 10, wide_search: bool = False) -> List[Dict[str, Any]]:
        """
        Recherche continue jusqu'à obtenir le nombre d'entreprises souhaité
        """
        logger.info(f"🚀 [CONTINUOUS] Début de la recherche continue")
        logger.info(f"📍 [CONTINUOUS] Localisation: {location}")
        logger.info(f"🏢 [CONTINUOUS] Type d'entreprise: {business_type}")
        logger.info(f"🎯 [CONTINUOUS] Objectif: {target_count} entreprises")
        logger.info(f"📏 [CONTINUOUS] Rayon: {radius}m")
        logger.info(f"⭐ [CONTINUOUS] Note minimum: {min_rating}")
        logger.info(f"📝 [CONTINUOUS] Avis minimum: {min_reviews}")
        
        try:
            # Étape 1: Géocodage
            coordinates = self._geocode_location(location)
            if not coordinates:
                logger.error(f"❌ [CONTINUOUS] Impossible de géocoder: {location}")
                return []
            
            lat, lng = coordinates
            logger.info(f"✅ [CONTINUOUS] Géocodage réussi: {lat:.6f}, {lng:.6f}")
            
            # Étape 2: Recherche continue
            all_unique_bars = []
            search_count = 0
            total_api_cost = 0.005  # Coût du géocodage
            doublons_evites = 0
            
            # Stratégies de recherche adaptatives selon le type d'entreprise
            if wide_search:
                # Mode recherche large : utiliser uniquement le mot-clé de l'utilisateur
                logger.info(f"🔍 [CONTINUOUS] Mode RECHERCHE LARGE activé - utilisation du mot-clé uniquement")
                search_strategies = [
                    {"type": None, "keyword": business_type, "radius": radius},
                    {"type": None, "keyword": business_type, "radius": radius * 2},  # Rayon doublé pour plus de résultats
                ]
            else:
                # Mode recherche précise : utiliser les stratégies optimisées
                logger.info(f"🔍 [CONTINUOUS] Mode RECHERCHE PRÉCISE activé - utilisation des stratégies optimisées")
                search_strategies = self._get_search_strategies(business_type, radius)
            
            while len(all_unique_bars) < target_count and search_count < max_searches:
                search_count += 1
                strategy = search_strategies[search_count - 1] if search_count <= len(search_strategies) else search_strategies[0]
                
                logger.info(f"🔍 [CONTINUOUS] Recherche {search_count}/{max_searches}")
                logger.info(f"📊 [CONTINUOUS] Entreprises uniques actuelles: {len(all_unique_bars)}/{target_count}")
                logger.info(f"🎯 [CONTINUOUS] Stratégie: {strategy}")
                
                # Recherche avec cette stratégie
                new_bars = self._search_with_strategy(
                    lat, lng, strategy, min_rating, min_reviews, max_pages_per_search
                )
                
                # Filtrer les doublons entre nouveaux résultats
                unique_new_bars = self._filter_duplicates(new_bars, all_unique_bars)
                doublons_evites += len(new_bars) - len(unique_new_bars)
                
                # Filtrer les doublons en base de données
                unique_new_bars = self._check_database_duplicates(unique_new_bars)
                
                logger.info(f"📈 [CONTINUOUS] Nouvelles entreprises trouvées: {len(new_bars)}")
                logger.info(f"✅ [CONTINUOUS] Entreprises uniques ajoutées: {len(unique_new_bars)}")
                logger.info(f"🛡️ [CONTINUOUS] Doublons évités: {len(new_bars) - len(unique_new_bars)}")
                
                # Ajouter les nouvelles entreprises uniques
                all_unique_bars.extend(unique_new_bars)
                
                # Calculer le coût
                total_api_cost += (len(unique_new_bars) * 0.017)  # Place Details
                
                logger.info(f"💰 [CONTINUOUS] Coût total actuel: ~${total_api_cost:.3f}")
                
                # Si on a assez d'entreprises, arrêter
                if len(all_unique_bars) >= target_count:
                    logger.info(f"🎉 [CONTINUOUS] Objectif atteint: {len(all_unique_bars)} entreprises uniques")
                    break
                
                # Délai entre les recherches pour éviter les quotas
                if search_count < max_searches:
                    logger.info(f"⏳ [CONTINUOUS] Attente de 3 secondes avant la prochaine recherche...")
                    time.sleep(3)
            
            # Tronquer à l'objectif exact
            final_bars = all_unique_bars[:target_count]
            
            logger.info(f"🎉 [CONTINUOUS] Recherche terminée!")
            logger.info(f"📊 [CONTINUOUS] Entreprises uniques trouvées: {len(final_bars)}/{target_count}")
            logger.info(f"🛡️ [CONTINUOUS] Doublons évités au total: {doublons_evites}")
            logger.info(f"💰 [CONTINUOUS] Coût total final: ~${total_api_cost:.3f}")
            logger.info(f"🔍 [CONTINUOUS] Recherches effectuées: {search_count}")
            
            return final_bars
            
        except Exception as e:
            logger.error(f"❌ [CONTINUOUS] Erreur lors de la recherche continue: {str(e)}")
            return []

    def _get_search_strategies(self, business_type: str, radius: int) -> List[Dict[str, Any]]:
        """
        Générer des stratégies de recherche adaptées au type d'entreprise
        """
        # Stratégies de base communes
        base_strategies = [
            {"type": business_type, "keyword": None, "radius": radius},
            {"type": business_type, "keyword": None, "radius": radius * 2},  # Zone élargie
        ]
        
        # Stratégies spécifiques selon le type d'entreprise
        specific_strategies = []
        
        if business_type in ['bar', 'restaurant', 'cafe']:
            # Stratégies pour les établissements de restauration
            specific_strategies = [
                {"type": business_type, "keyword": "cocktail", "radius": radius},
                {"type": business_type, "keyword": "pub", "radius": radius},
                {"type": business_type, "keyword": "brasserie", "radius": radius},
                {"type": business_type, "keyword": "terrasse", "radius": radius},
                {"type": business_type, "keyword": "happy hour", "radius": radius},
                {"type": business_type, "keyword": "live music", "radius": radius},
            ]
        elif business_type == 'florist':
            # Stratégies pour les fleuristes
            specific_strategies = [
                {"type": business_type, "keyword": "fleurs", "radius": radius},
                {"type": business_type, "keyword": "bouquet", "radius": radius},
                {"type": business_type, "keyword": "plantes", "radius": radius},
                {"type": business_type, "keyword": "livraison fleurs", "radius": radius},
                {"type": business_type, "keyword": "composition florale", "radius": radius},
            ]
        elif business_type == 'beauty_salon':
            # Stratégies pour les salons de beauté
            specific_strategies = [
                {"type": business_type, "keyword": "coiffure", "radius": radius},
                {"type": business_type, "keyword": "manucure", "radius": radius},
                {"type": business_type, "keyword": "esthétique", "radius": radius},
                {"type": business_type, "keyword": "soin visage", "radius": radius},
            ]
        elif business_type == 'spa':
            # Stratégies pour les spas
            specific_strategies = [
                {"type": business_type, "keyword": "massage", "radius": radius},
                {"type": business_type, "keyword": "bien-être", "radius": radius},
                {"type": business_type, "keyword": "relaxation", "radius": radius},
                {"type": business_type, "keyword": "thérapie", "radius": radius},
            ]
        elif business_type == 'hotel' or business_type == 'lodging':
            # Stratégies pour les hôtels
            specific_strategies = [
                {"type": business_type, "keyword": "chambre", "radius": radius},
                {"type": business_type, "keyword": "hébergement", "radius": radius},
                {"type": business_type, "keyword": "réservation", "radius": radius},
                {"type": business_type, "keyword": "confort", "radius": radius},
            ]
        elif business_type == 'gym' or business_type == 'fitness_center':
            # Stratégies pour les salles de sport
            specific_strategies = [
                {"type": business_type, "keyword": "musculation", "radius": radius},
                {"type": business_type, "keyword": "cardio", "radius": radius},
                {"type": business_type, "keyword": "cours collectifs", "radius": radius},
                {"type": business_type, "keyword": "entraînement", "radius": radius},
            ]
        elif business_type == 'pharmacy':
            # Stratégies pour les pharmacies
            specific_strategies = [
                {"type": business_type, "keyword": "médicament", "radius": radius},
                {"type": business_type, "keyword": "parapharmacie", "radius": radius},
                {"type": business_type, "keyword": "conseil santé", "radius": radius},
            ]
        elif business_type == 'bakery':
            # Stratégies pour les boulangeries
            specific_strategies = [
                {"type": business_type, "keyword": "pain", "radius": radius},
                {"type": business_type, "keyword": "viennoiserie", "radius": radius},
                {"type": business_type, "keyword": "pâtisserie", "radius": radius},
            ]
        else:
            # Stratégies génériques pour les autres types
            specific_strategies = [
                {"type": business_type, "keyword": business_type, "radius": radius},
                {"type": business_type, "keyword": "service", "radius": radius},
                {"type": business_type, "keyword": "professionnel", "radius": radius},
            ]
        
        # Combiner les stratégies de base avec les stratégies spécifiques
        all_strategies = base_strategies + specific_strategies
        
        logger.info(f"🎯 [CONTINUOUS] Stratégies générées pour {business_type}: {len(all_strategies)} stratégies")
        
        return all_strategies
    
    def _search_with_strategy(self, lat: float, lng: float, strategy: Dict[str, Any], 
                            min_rating: float, min_reviews: int, max_pages: int) -> List[Dict[str, Any]]:
        """Recherche avec une stratégie spécifique"""
        bars_found = []
        next_page_token = None
        page_count = 0
        
        while page_count < max_pages:
            page_count += 1
            
            try:
                # Construire les paramètres de recherche
                params = {
                    'location': (lat, lng),
                    'radius': strategy['radius'],
                    'type': strategy['type'],
                    'language': 'fr',
                    'rank_by': 'prominence'
                }
                
                if strategy['keyword']:
                    params['keyword'] = strategy['keyword']
                
                if next_page_token:
                    params['page_token'] = next_page_token
                
                # Effectuer la recherche
                response = places_nearby(self.client, **params)
                
                # Filtrer par qualité
                for result in response.get('results', []):
                    rating = result.get('rating', 0)
                    user_ratings_total = result.get('user_ratings_total', 0)
                    
                    if rating >= min_rating and user_ratings_total >= min_reviews:
                        # Enrichir avec les détails
                        enriched_bar = self._enrich_business_data(result)
                        if enriched_bar:
                            bars_found.append(enriched_bar)
                
                # Vérifier s'il y a une page suivante
                next_page_token = response.get('next_page_token')
                if not next_page_token:
                    break
                
                # Délai pour le token de page suivante
                if next_page_token:
                    time.sleep(2)
            
            except Exception as e:
                logger.error(f"❌ [CONTINUOUS] Erreur lors de la recherche: {str(e)}")
                break
        
        return bars_found
    
    def _filter_duplicates(self, new_bars: List[Dict[str, Any]], existing_bars: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filtrer les doublons entre nouveaux bars et bars existants"""
        existing_names = {bar['name'].lower() for bar in existing_bars if bar.get('name')}
        unique_new_bars = []
        
        for bar in new_bars:
            bar_name = bar.get('name', '').lower()
            if bar_name and bar_name not in existing_names:
                unique_new_bars.append(bar)
                existing_names.add(bar_name)
        
        return unique_new_bars
    
    def _enrich_business_data(self, place_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Enrichir les données d'une entreprise"""
        try:
            place_id = place_data.get('place_id')
            if not place_id:
                return None
            
            # Récupérer les détails complets
            details = self._get_place_details(place_id)
            if not details:
                return self._format_basic_data(place_data)
            
            # Extraire les coordonnées GPS
            geometry = place_data.get('geometry', {})
            location = geometry.get('location', {})
            latitude = location.get('lat')
            longitude = location.get('lng')
            
            # Fusionner les données
            enriched_data = {
                'name': place_data.get('name'),
                'address': self._extract_address(place_data),
                'phone': details.get('formatted_phone_number'),
                'website': details.get('website'),
                'rating': place_data.get('rating'),
                'user_ratings_total': place_data.get('user_ratings_total'),
                'types': place_data.get('types', []),
                'business_type': self._extract_primary_type(place_data.get('types', [])),
                'place_id': place_id,
                'geometry': place_data.get('geometry', {}),
                'latitude': latitude,
                'longitude': longitude,
                'opening_hours': details.get('opening_hours'),
                'price_level': details.get('price_level'),
                'reviews': details.get('reviews', [])[:3],
                'photos': details.get('photos', [])[:3],
                'formatted_address': details.get('formatted_address'),
                'international_phone_number': details.get('international_phone_number'),
                'url': details.get('url'),
                'website_verified': details.get('website') is not None
            }
            
            return enriched_data
            
        except Exception as e:
            logger.error(f"❌ [CONTINUOUS] Erreur lors de l'enrichissement: {str(e)}")
            return self._format_basic_data(place_data)
    
    def _get_place_details(self, place_id: str) -> Optional[Dict[str, Any]]:
        """Récupérer les détails complets d'un lieu"""
        try:
            details = place(self.client,
                place_id,
                fields=[
                    'formatted_phone_number',
                    'website',
                    'opening_hours',
                    'price_level',
                    'reviews',
                    'photo',
                    'formatted_address',
                    'international_phone_number',
                    'url'
                ],
                language='fr'
            )
            
            if details and 'result' in details:
                return details['result']
            else:
                return None
            
        except Exception as e:
            logger.error(f"❌ [CONTINUOUS] Erreur lors de la récupération des détails: {str(e)}")
            return None
    
    def _format_basic_data(self, place_data: Dict[str, Any]) -> Dict[str, Any]:
        """Formater les données de base d'une entreprise"""
        try:
            geometry = place_data.get('geometry', {})
            location = geometry.get('location', {})
            
            return {
                'name': place_data.get('name'),
                'address': self._extract_address(place_data),
                'phone': None,
                'website': None,
                'rating': place_data.get('rating'),
                'user_ratings_total': place_data.get('user_ratings_total'),
                'types': place_data.get('types', []),
                'business_type': self._extract_primary_type(place_data.get('types', [])),
                'place_id': place_data.get('place_id'),
                'geometry': geometry,
                'latitude': location.get('lat'),
                'longitude': location.get('lng'),
                'opening_hours': None,
                'price_level': None,
                'reviews': [],
                'photos': [],
                'formatted_address': place_data.get('vicinity'),
                'international_phone_number': None,
                'url': None,
                'website_verified': False
            }
        except Exception as e:
            logger.error(f"❌ [CONTINUOUS] Erreur lors du formatage: {str(e)}")
            return {}
    
    def _geocode_location(self, location: str) -> Optional[tuple]:
        """Géocoder une localisation pour obtenir les coordonnées"""
        try:
            geocode_result = geocode(self.client, location, language='fr')
            
            if not geocode_result:
                return None
            
            location_data = geocode_result[0]['geometry']['location']
            lat, lng = location_data['lat'], location_data['lng']
            return (lat, lng)
            
        except Exception as e:
            logger.error(f"❌ [CONTINUOUS] Erreur lors du géocodage: {str(e)}")
            return None
    
    def _extract_primary_type(self, types: List[str], search_type: Optional[str] = None) -> str:
        """Extraire le type principal d'une liste de types"""
        if not types:
            return 'unknown'
        
        if search_type and search_type in types:
            return search_type
        
        priority_types = [
            'restaurant', 'cafe', 'bar', 'store', 'shopping_mall', 'supermarket',
            'beauty_salon', 'hair_care', 'spa', 'gym', 'fitness_center',
            'dentist', 'doctor', 'hospital', 'pharmacy', 'veterinary_care',
            'lawyer', 'accounting', 'real_estate_agency', 'insurance_agency',
            'bank', 'car_dealer', 'car_repair', 'gas_station', 'hotel', 'lodging'
        ]
        
        for priority_type in priority_types:
            if priority_type in types:
                return priority_type
        
        return types[0]
    
    def _extract_address(self, place_data: Dict[str, Any]) -> str:
        """Extraire l'adresse complète d'un lieu"""
        try:
            if 'formatted_address' in place_data:
                return place_data['formatted_address']
            
            components = place_data.get('vicinity', '')
            if components:
                return components
            
            return place_data.get('name', 'Adresse non disponible')
            
        except Exception as e:
            logger.error(f"❌ [CONTINUOUS] Erreur lors de l'extraction de l'adresse: {str(e)}")
            return 'Adresse non disponible'
    
    def search_nearby_smart(self, location, radius=5000, business_type=None, max_results=20, min_rating=4.0, min_reviews=10, check_duplicates=True):
        """
        Méthode de compatibilité : même signature que l'ancien scraper.
        Redirige vers la recherche continue optimisée.
        """
        return self.search_continuous_until_target(
            location=location,
            target_count=max_results,
            business_type=business_type or "bar",
            radius=radius,
            min_rating=min_rating,
            min_reviews=min_reviews
        )

    def get_business_types(self) -> List[str]:
        """
        Obtenir la liste des types d'entreprises supportés par Google Places
        Méthode de compatibilité pour l'interface web
        """
        return [
            'accounting', 'airport', 'amusement_park', 'aquarium', 'art_gallery',
            'atm', 'bakery', 'bank', 'bar', 'beauty_salon', 'bicycle_store',
            'book_store', 'bowling_alley', 'bus_station', 'cafe', 'car_dealer',
            'car_rental', 'car_repair', 'car_wash', 'casino', 'cemetery',
            'church', 'city_hall', 'clothing_store', 'convenience_store',
            'courthouse', 'dentist', 'department_store', 'doctor', 'drugstore',
            'electrician', 'electronics_store', 'embassy', 'fire_station',
            'florist', 'funeral_home', 'furniture_store', 'gas_station',
            'gym', 'hair_care', 'hardware_store', 'hindu_temple', 'home_goods_store',
            'hospital', 'insurance_agency', 'jewelry_store', 'laundry',
            'lawyer', 'library', 'light_rail_station', 'liquor_store',
            'local_government_office', 'locksmith', 'lodging', 'meal_delivery',
            'meal_takeaway', 'mosque', 'movie_rental', 'movie_theater',
            'moving_company', 'museum', 'night_club', 'painter', 'park',
            'parking', 'pet_store', 'pharmacy', 'physiotherapist', 'plumber',
            'police', 'post_office', 'primary_school', 'real_estate_agency',
            'restaurant', 'roofing_contractor', 'rv_park', 'school',
            'secondary_school', 'shoe_store', 'shopping_mall', 'spa',
            'stadium', 'storage', 'store', 'subway_station', 'supermarket',
            'synagogue', 'taxi_stand', 'tourist_attraction', 'train_station',
            'transit_station', 'travel_agency', 'university', 'veterinary_care',
            'zoo'
        ]

    def search_nearby(self, location: str, radius: int = 5000, business_type: Optional[str] = None, max_results: int = 20) -> List[Dict[str, Any]]:
        """
        Méthode de compatibilité : même signature que l'ancien scraper.
        Redirige vers la recherche continue optimisée.
        """
        return self.search_continuous_until_target(
            location=location,
            target_count=max_results,
            business_type=business_type or "bar",
            radius=radius,
            min_rating=4.0,
            min_reviews=10
        ) 