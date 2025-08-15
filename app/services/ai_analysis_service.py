"""
Service d'analyse IA pour l'extraction intelligente de données web
"""

import os
import json
import requests
import logging
from typing import Dict, Any, Optional, List
from app.prompts import WEBSITE_ANALYSIS_PROMPT, SCREENSHOT_ANALYSIS_PROMPT, LEAD_SCORING_PROMPT, SYSTEM_PROMPT

logger = logging.getLogger(__name__)

class AIAnalysisService:
    """Service d'analyse IA pour extraire les informations des sites web"""
    
    def __init__(self):
        """Initialise le service d'analyse IA"""
        self.api_key = os.getenv('OPENAI_API_KEY')
        self.api_url = "https://api.openai.com/v1/chat/completions"
        
        if not self.api_key:
            logger.error("❌ [AI] Clé API OpenAI manquante")
            raise ValueError("OPENAI_API_KEY non définie")
        
        logger.info("✅ Service IA initialisé")
    
    def analyze_website(self, html_content: str, url: str = "") -> Dict[str, Any]:
        """
        Analyse un site web avec l'IA
        """
        try:
            logger.info(f"🤖 [AI] Début analyse IA pour {url}")
            
            # Smart truncation pour éviter les limites de tokens
            truncated_html = self._smart_truncate_html(html_content)
            logger.info(f"📏 [AI] HTML original: {len(html_content)} caractères")
            logger.info(f"📏 [AI] HTML smart-truncated: {len(truncated_html)} caractères")
            
            # Créer le prompt avec le template configurable
            prompt = self._create_analysis_prompt(truncated_html, url)
            
            # Appeler l'API OpenAI
            response = self._call_openai_api(prompt)
            
            if response:
                logger.info("✅ [AI] JSON parsé avec succès")
                return response
            else:
                logger.warning("⚠️ [AI] Échec de l'analyse, utilisation du fallback amélioré")
                return self._get_fallback_result_with_html_analysis(html_content, url)
                
        except Exception as e:
            logger.error(f"❌ [AI] Erreur analyse IA: {str(e)}")
            return self._get_fallback_result_with_html_analysis(html_content, url)
    
    def analyze_website_full_html(self, html_content: str, url: str = "") -> Dict[str, Any]:
        """
        Analyse un site web avec le HTML COMPLET (sans troncature)
        Utilise GPT-4 pour gérer de gros contextes
        """
        try:
            logger.info(f"🤖 [AI FULL] Début analyse HTML complet pour {url}")
            logger.info(f"📏 [AI FULL] HTML complet: {len(html_content)} caractères")
            
            # Créer le prompt avec le HTML complet
            prompt = self._create_analysis_prompt(html_content, url)
            
            # Appeler l'API OpenAI avec GPT-4
            response = self._call_openai_api_full(prompt)
            
            if response:
                logger.info("✅ [AI FULL] JSON parsé avec succès")
                return response
            else:
                logger.warning("⚠️ [AI FULL] Échec de l'analyse, utilisation du fallback amélioré")
                return self._get_fallback_result_with_html_analysis(html_content, url)
                
        except Exception as e:
            logger.error(f"❌ [AI FULL] Erreur analyse IA: {str(e)}")
            return self._get_fallback_result_with_html_analysis(html_content, url)
    
    def analyze_website_chunked(self, html_content: str, url: str = "") -> Dict[str, Any]:
        """
        Analyse un site web en divisant le HTML en sections
        """
        try:
            logger.info(f"🤖 [AI CHUNKED] Début analyse par sections pour {url}")
            logger.info(f"📏 [AI CHUNKED] HTML complet: {len(html_content)} caractères")
            
            # Diviser le HTML en sections
            chunks = self._split_html_into_chunks(html_content)
            logger.info(f"📦 [AI CHUNKED] HTML divisé en {len(chunks)} sections")
            
            # Analyser chaque section
            all_results = []
            for i, chunk in enumerate(chunks):
                logger.info(f"🔍 [AI CHUNKED] Analyse section {i+1}/{len(chunks)} ({len(chunk)} caractères)")
                
                # Analyser cette section
                chunk_result = self._analyze_html_chunk(chunk, url, f"Section {i+1}")
                if chunk_result:
                    all_results.append(chunk_result)
            
            # Fusionner tous les résultats
            final_result = self._merge_chunk_results(all_results, url)
            
            logger.info(f"✅ [AI CHUNKED] Analyse par sections terminée")
            return final_result
            
        except Exception as e:
            logger.error(f"❌ [AI CHUNKED] Erreur analyse par sections: {str(e)}")
            return self._get_fallback_result_with_html_analysis(html_content, url)
    
    def _smart_truncate_html(self, html_content: str) -> str:
        """
        Tronque intelligemment le HTML en préservant les sections importantes
        """
        if len(html_content) <= 15000:
            return html_content
        
        logger.info(f"📏 [AI] HTML original: {len(html_content)} caractères")
        
        # Chercher les sections importantes
        important_sections = []
        
        # 1. Header (premiers 5000 caractères)
        header = html_content[:5000]
        important_sections.append(("Header", header))
        
        # 2. Chercher les sections contact/footer
        contact_keywords = ['contact', 'footer', 'adresse', 'téléphone', 'email', 'social']
        for keyword in contact_keywords:
            start = html_content.lower().find(keyword)
            if start != -1:
                end = min(start + 5000, len(html_content))  # Augmenté de 3000 à 5000
                section = html_content[start:end]
                important_sections.append((f"Section {keyword}", section))
        
        # 3. Chercher les réseaux sociaux - AMÉLIORÉ
        social_keywords = ['facebook', 'instagram', 'twitter', 'linkedin', 'youtube', 'tiktok']
        social_patterns = [
            r'https?://[^\s"\'>]*facebook[^\s"\'>]*',
            r'https?://[^\s"\'>]*instagram[^\s"\'>]*',
            r'https?://[^\s"\'>]*twitter[^\s"\'>]*',
            r'https?://[^\s"\'>]*linkedin[^\s"\'>]*',
            r'https?://[^\s"\'>]*youtube[^\s"\'>]*',
            r'https?://[^\s"\'>]*tiktok[^\s"\'>]*',
        ]
        
        # Chercher par mots-clés
        for keyword in social_keywords:
            start = html_content.lower().find(keyword)
            if start != -1:
                end = min(start + 5000, len(html_content))  # Augmenté de 2000 à 5000
                section = html_content[start:end]
                important_sections.append((f"Social {keyword}", section))
        
        # Chercher par patterns regex - NOUVEAU : Plus exhaustif
        import re
        for i, pattern in enumerate(social_patterns):
            matches = re.finditer(pattern, html_content, re.IGNORECASE)
            for match in matches:
                start = max(0, match.start() - 3000)  # Augmenté de 2000 à 3000
                end = min(len(html_content), match.end() + 3000)  # Augmenté de 2000 à 3000
                section = html_content[start:end]
                platform = social_keywords[i] if i < len(social_keywords) else f"social_{i}"
                important_sections.append((f"Social {platform} (regex)", section))
        
        # 4. Chercher les horaires/tarifs
        info_keywords = ['horaires', 'tarifs', 'prix', 'ouverture']
        for keyword in info_keywords:
            start = html_content.lower().find(keyword)
            if start != -1:
                end = min(start + 3000, len(html_content))
                section = html_content[start:end]
                important_sections.append((f"Info {keyword}", section))
        
        # 5. Chercher les icônes réseaux sociaux (classes CSS) - NOUVEAU
        icon_patterns = [
            r'class=["\'][^"\']*facebook[^"\']*["\']',
            r'class=["\'][^"\']*instagram[^"\']*["\']',
            r'class=["\'][^"\']*twitter[^"\']*["\']',
            r'class=["\'][^"\']*linkedin[^"\']*["\']',
            r'class=["\'][^"\']*youtube[^"\']*["\']',
            r'class=["\'][^"\']*social[^"\']*["\']',
            r'class=["\'][^"\']*bi-facebook[^"\']*["\']',  # Bootstrap Icons
            r'class=["\'][^"\']*bi-instagram[^"\']*["\']',
            r'class=["\'][^"\']*bi-twitter[^"\']*["\']',
            r'class=["\'][^"\']*bi-linkedin[^"\']*["\']',
            r'class=["\'][^"\']*bi-youtube[^"\']*["\']',
        ]
        
        for i, pattern in enumerate(icon_patterns):
            matches = re.finditer(pattern, html_content, re.IGNORECASE)
            for match in matches:
                start = max(0, match.start() - 2000)  # Augmenté de 1000 à 2000
                end = min(len(html_content), match.end() + 2000)
                section = html_content[start:end]
                platform = social_keywords[i] if i < len(social_keywords) else f"icon_{i}"
                important_sections.append((f"Icon {platform}", section))
        
        # 6. NOUVEAU : Chercher dans le footer spécifiquement
        footer_patterns = [
            r'<footer[^>]*>.*?</footer>',
            r'<div[^>]*class=["\'][^"\']*footer[^"\']*["\'][^>]*>.*?</div>',
        ]
        
        for pattern in footer_patterns:
            matches = re.finditer(pattern, html_content, re.IGNORECASE | re.DOTALL)
            for match in matches:
                section = match.group(0)
                important_sections.append(("Footer", section))
        
        # 7. NOUVEAU : Chercher les liens externes
        external_link_pattern = r'<a[^>]*href=["\'](https?://[^"\']*facebook[^"\']*|https?://[^"\']*instagram[^"\']*|https?://[^"\']*twitter[^"\']*|https?://[^"\']*linkedin[^"\']*|https?://[^"\']*youtube[^"\']*|https?://[^"\']*tiktok[^"\']*)["\'][^>]*>'
        matches = re.finditer(external_link_pattern, html_content, re.IGNORECASE)
        for match in matches:
            start = max(0, match.start() - 1000)
            end = min(len(html_content), match.end() + 1000)
            section = html_content[start:end]
            important_sections.append(("External Social Link", section))
        
        # Combiner les sections importantes
        combined_html = ""
        for section_name, section_content in important_sections:
            combined_html += f"\n<!-- {section_name} -->\n{section_content}\n"
        
        # Si on a encore de la place, ajouter le début du HTML
        remaining_chars = 15000 - len(combined_html)
        if remaining_chars > 0:
            combined_html = html_content[:remaining_chars] + combined_html
        
        # Tronquer si nécessaire
        if len(combined_html) > 15000:
            combined_html = combined_html[:15000]
        
        logger.info(f"📏 [AI] HTML smart-truncated: {len(combined_html)} caractères")
        logger.info(f"📏 [AI] Sections préservées: {[name for name, _ in important_sections]}")
        
        return combined_html
    
    def _create_analysis_prompt(self, html_content: str, url: str) -> str:
        """Crée le prompt pour l'analyse IA en utilisant le template configurable"""
        return WEBSITE_ANALYSIS_PROMPT.format(url=url, html_content=html_content)
    
    def _call_openai_api(self, prompt: str) -> Optional[Dict[str, Any]]:
        """Appelle l'API OpenAI"""
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "gpt-3.5-turbo",
            "messages": [
                {
                    "role": "system",
                    "content": "Tu es un expert en analyse de sites web. Tu extrais les informations importantes et tu retournes UNIQUEMENT un JSON valide."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.1,
            "max_tokens": 4000
        }
        
        try:
            logger.info(f"📡 [AI] Appel API OpenAI avec {len(prompt)} caractères")
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=data,
                timeout=60
            )
            response.raise_for_status()
            
            result = response.json()
            content = result['choices'][0]['message']['content']
            
            # Essayer de parser le JSON
            try:
                # Chercher le JSON dans la réponse
                json_start = content.find('{')
                json_end = content.rfind('}') + 1
                
                if json_start != -1 and json_end > json_start:
                    json_content = content[json_start:json_end]
                    parsed_result = json.loads(json_content)
                    logger.info("✅ [AI] JSON parsé avec succès")
                    return parsed_result
                else:
                    logger.error(f"❌ [AI] Aucun JSON trouvé dans la réponse")
                    logger.error(f"📄 [AI] Réponse complète: {content}")
                    return None
                    
            except json.JSONDecodeError as e:
                logger.error(f"❌ [AI] Erreur parsing JSON: {str(e)}")
                logger.error(f"📄 [AI] Contenu reçu: {content}")
                return None
                
        except Exception as e:
            logger.error(f"❌ [AI] Erreur API OpenAI: {str(e)}")
            return None
    
    def _call_openai_api_full(self, prompt: str) -> Optional[Dict[str, Any]]:
        """Appelle l'API OpenAI avec GPT-4 pour gérer de gros contextes"""
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "gpt-4",  # Utiliser GPT-4 au lieu de GPT-3.5-turbo
            "messages": [
                {
                    "role": "system",
                    "content": "Tu es un expert en analyse de sites web. Tu extrais les informations importantes et tu retournes UNIQUEMENT un JSON valide. Analyse TOUT le HTML fourni."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.1,
            "max_tokens": 4000
        }
        
        try:
            logger.info(f"📡 [AI FULL] Appel API OpenAI avec {len(prompt)} caractères")
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=data,
                timeout=60
            )
            response.raise_for_status()
            
            result = response.json()
            content = result['choices'][0]['message']['content']
            
            # Essayer de parser le JSON
            try:
                # Chercher le JSON dans la réponse
                json_start = content.find('{')
                json_end = content.rfind('}') + 1
                
                if json_start != -1 and json_end > json_start:
                    json_content = content[json_start:json_end]
                    parsed_result = json.loads(json_content)
                    logger.info("✅ [AI FULL] JSON parsé avec succès")
                    return parsed_result
                else:
                    logger.error(f"❌ [AI FULL] Aucun JSON trouvé dans la réponse")
                    logger.error(f"📄 [AI FULL] Réponse complète: {content}")
                    return None
                    
            except json.JSONDecodeError as e:
                logger.error(f"❌ [AI FULL] Erreur parsing JSON: {str(e)}")
                logger.error(f"📄 [AI FULL] Contenu reçu: {content}")
                return None
                
        except Exception as e:
            logger.error(f"❌ [AI FULL] Erreur API OpenAI: {str(e)}")
            return None
    
    def _call_openai_vision_api(self, prompt: str, encoded_image: str) -> Optional[Dict[str, Any]]:
        """Appelle l'API OpenAI Vision pour analyser une image"""
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "gpt-4o",
            "messages": [
                {
                    "role": "system",
                    "content": "Tu es un expert en analyse d'images de réseaux sociaux. Tu extrais les informations importantes et tu retournes UNIQUEMENT un JSON valide."
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{encoded_image}"
                            }
                        }
                    ]
                }
            ],
            "max_tokens": 2000,
            "temperature": 0.1
        }
        
        try:
            response = requests.post(self.api_url, headers=headers, json=data, timeout=60)
            
            if response.status_code == 200:
                result = response.json()
                content = result['choices'][0]['message']['content']
                
                # Essayer de parser le JSON
                try:
                    # Nettoyer le contenu pour extraire le JSON
                    json_start = content.find('{')
                    json_end = content.rfind('}') + 1
                    
                    if json_start == -1 or json_end == 0:
                        logger.error(f"❌ [AI] Aucun JSON trouvé dans la réponse Vision")
                        logger.error(f"📄 [AI] Contenu reçu: {content[:500]}...")
                        return None
                    
                    json_content = content[json_start:json_end]
                    
                    # Nettoyer le JSON des caractères problématiques
                    json_content = json_content.strip()
                    json_content = json_content.replace('\n', ' ').replace('\r', ' ')
                    json_content = json_content.replace('  ', ' ')
                    
                    parsed_result = json.loads(json_content)
                    logger.info(f"✅ [AI] JSON Vision parsé avec succès")
                    return parsed_result
                    
                except json.JSONDecodeError as e:
                    logger.error(f"❌ [AI] Erreur parsing JSON Vision: {str(e)}")
                    logger.error(f"📄 [AI] Contenu reçu complet: {content}")
                    logger.error(f"📄 [AI] JSON extrait: {json_content}")
                    return None
                    
            else:
                logger.error(f"❌ [AI] Erreur API Vision: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"❌ [AI] Erreur appel API Vision: {str(e)}")
            return None
    
    def _get_fallback_result(self, url: str) -> Dict[str, Any]:
        """Résultat de fallback en cas d'échec - AMÉLIORÉ avec analyse HTML"""
        return {
            "contact": {
                "emails": [],
                "telephones": [],
                "adresse": ""
            },
            "entreprise": {
                "nom": "",
                "type": "",
                "description": "",
                "produits_services": [],
                "public_cible": ""
            },
            "pratique": {
                "horaires": "",
                "tarifs": "",
                "services": []
            },
            "reseaux_sociaux": {},
            "medias": {
                "images": 0,
                "videos": 0,
                "types_images": []
            },
            "error": "Échec de l'analyse IA"
        }
    
    def _get_fallback_result_with_html_analysis(self, html_content: str, url: str) -> Dict[str, Any]:
        """Résultat de fallback avec analyse HTML manuelle"""
        try:
            logger.info(f"🔍 [FALLBACK] Analyse HTML manuelle pour {url}")
            
            # Analyser les médias
            media_info = self._analyze_html_media_manually(html_content)
            
            # Analyser les réseaux sociaux
            social_media = self._analyze_html_social_media(html_content)
            
            # Analyser les contacts
            contact_info = self._analyze_html_contact(html_content)
            
            # Analyser l'entreprise
            entreprise_info = self._analyze_html_entreprise(html_content)
            
            return {
                "contact": contact_info,
                "entreprise": entreprise_info,
                "pratique": {
                    "horaires": "",
                    "tarifs": "",
                    "services": []
                },
                "reseaux_sociaux": social_media,
                "medias": {
                    "images": media_info.get("images", 0),
                    "videos": media_info.get("videos", 0),
                    "types_images": media_info.get("image_types", [])
                },
                "error": "Analyse manuelle (IA indisponible)"
            }
            
        except Exception as e:
            logger.error(f"❌ [FALLBACK] Erreur analyse HTML manuelle: {str(e)}")
            return self._get_fallback_result(url)
    
    def _analyze_html_social_media(self, html_content: str) -> Dict[str, Any]:
        """Analyse manuelle des réseaux sociaux dans le HTML"""
        import re
        
        social_media = {}
        
        # Patterns pour les réseaux sociaux
        social_patterns = {
            'facebook': [
                r'https?://[^\s"\'>]*facebook[^\s"\'>]*',
                r'facebook\.com/[^\s"\'>]*',
                r'fb\.com/[^\s"\'>]*'
            ],
            'instagram': [
                r'https?://[^\s"\'>]*instagram[^\s"\'>]*',
                r'instagram\.com/[^\s"\'>]*'
            ],
            'twitter': [
                r'https?://[^\s"\'>]*twitter[^\s"\'>]*',
                r'x\.com/[^\s"\'>]*',
                r'twitter\.com/[^\s"\'>]*'
            ],
            'linkedin': [
                r'https?://[^\s"\'>]*linkedin[^\s"\'>]*',
                r'linkedin\.com/[^\s"\'>]*'
            ],
            'youtube': [
                r'https?://[^\s"\'>]*youtube[^\s"\'>]*',
                r'youtube\.com/[^\s"\'>]*'
            ],
            'tiktok': [
                r'https?://[^\s"\'>]*tiktok[^\s"\'>]*',
                r'tiktok\.com/[^\s"\'>]*'
            ]
        }
        
        # Chercher dans le HTML
        for platform, patterns in social_patterns.items():
            for pattern in patterns:
                matches = re.findall(pattern, html_content, re.IGNORECASE)
                if matches:
                    # Nettoyer et dédupliquer les URLs
                    clean_urls = []
                    for match in matches:
                        if match.startswith('http'):
                            clean_urls.append(match)
                        else:
                            clean_urls.append(f"https://{match}")
                    
                    if clean_urls:
                        social_media[platform] = list(set(clean_urls))[0]  # Prendre le premier
                        logger.info(f"📱 [FALLBACK] {platform} trouvé: {social_media[platform]}")
                        break  # Passer au réseau suivant
        
        return social_media
    
    def _analyze_html_contact(self, html_content: str) -> Dict[str, Any]:
        """Analyse manuelle des contacts dans le HTML"""
        import re
        
        contact_info = {
            "emails": [],
            "telephones": [],
            "adresse": ""
        }
        
        # Chercher les emails
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, html_content)
        contact_info["emails"] = list(set(emails))  # Dédupliquer
        
        # Chercher les téléphones français
        phone_pattern = r'(?:\+33|0033|33|0)[1-9](?:[ .-]?\d{2}){4}'
        phones = re.findall(phone_pattern, html_content)
        contact_info["telephones"] = list(set(phones))  # Dédupliquer
        
        # Chercher l'adresse (pattern basique)
        address_patterns = [
            r'<address[^>]*>([^<]+)</address>',
            r'class=["\'][^"\']*address[^"\']*["\'][^>]*>([^<]+)</',
        ]
        
        for pattern in address_patterns:
            matches = re.findall(pattern, html_content, re.IGNORECASE)
            if matches:
                contact_info["adresse"] = matches[0].strip()
                break
        
        logger.info(f"📧 [FALLBACK] {len(contact_info['emails'])} emails trouvés")
        logger.info(f"📞 [FALLBACK] {len(contact_info['telephones'])} téléphones trouvés")
        
        return contact_info
    
    def _analyze_html_entreprise(self, html_content: str) -> Dict[str, Any]:
        """Analyse manuelle des informations entreprise dans le HTML"""
        import re
        
        entreprise_info = {
            "nom": "",
            "type": "",
            "description": "",
            "produits_services": [],
            "public_cible": ""
        }
        
        # Chercher le titre
        title_pattern = r'<title[^>]*>([^<]+)</title>'
        title_match = re.search(title_pattern, html_content, re.IGNORECASE)
        if title_match:
            entreprise_info["nom"] = title_match.group(1).strip()
        
        # Chercher la description meta
        desc_pattern = r'<meta[^>]*name=["\']description["\'][^>]*content=["\']([^"\']+)["\']'
        desc_match = re.search(desc_pattern, html_content, re.IGNORECASE)
        if desc_match:
            entreprise_info["description"] = desc_match.group(1).strip()
        
        # Chercher le H1
        h1_pattern = r'<h1[^>]*>([^<]+)</h1>'
        h1_match = re.search(h1_pattern, html_content, re.IGNORECASE)
        if h1_match and not entreprise_info["nom"]:
            entreprise_info["nom"] = h1_match.group(1).strip()
        
        logger.info(f"🏢 [FALLBACK] Nom trouvé: {entreprise_info['nom']}")
        logger.info(f"📄 [FALLBACK] Description trouvée: {entreprise_info['description'][:50]}...")
        
        return entreprise_info

    def _analyze_html_media_manually(self, html_content: str) -> Dict[str, Any]:
        """
        Analyse manuelle du HTML pour détecter les médias
        """
        import re
        
        media_info = {
            "images": 0,
            "videos": 0,
            "image_types": [],
            "video_types": []
        }
        
        # Chercher les balises <img>
        img_pattern = r'<img[^>]*>'
        img_tags = re.findall(img_pattern, html_content, re.IGNORECASE)
        media_info["images"] += len(img_tags)
        
        # Chercher les background-image
        bg_pattern = r'background-image:\s*url\([^)]+\)'
        bg_images = re.findall(bg_pattern, html_content, re.IGNORECASE)
        media_info["images"] += len(bg_images)
        
        # Chercher les data-src (lazy loading)
        data_src_pattern = r'data-src=["\'][^"\']+["\']'
        data_src_images = re.findall(data_src_pattern, html_content, re.IGNORECASE)
        media_info["images"] += len(data_src_images)
        
        # Chercher les iframes vidéo
        iframe_pattern = r'<iframe[^>]*>'
        iframes = re.findall(iframe_pattern, html_content, re.IGNORECASE)
        video_iframes = [iframe for iframe in iframes if any(platform in iframe.lower() for platform in ['youtube', 'vimeo', 'dailymotion'])]
        media_info["videos"] += len(video_iframes)
        
        # Chercher les balises <video>
        video_pattern = r'<video[^>]*>'
        video_tags = re.findall(video_pattern, html_content, re.IGNORECASE)
        media_info["videos"] += len(video_tags)
        
        # Identifier les types d'images
        if img_tags:
            media_info["image_types"].append("Balises img")
        if bg_images:
            media_info["image_types"].append("Background images")
        if data_src_images:
            media_info["image_types"].append("Lazy loading")
        
        # Identifier les types de vidéos
        if video_iframes:
            media_info["video_types"].append("Iframes vidéo")
        if video_tags:
            media_info["video_types"].append("Balises video")
        
        logger.info(f"🔍 [MANUAL] Images trouvées: {media_info['images']}")
        logger.info(f"🔍 [MANUAL] Vidéos trouvées: {media_info['videos']}")
        
        return media_info

    def analyze_social_media_screenshots(self, screenshot_path: str, platform: str) -> Dict[str, Any]:
        """
        Analyse les captures d'écran des réseaux sociaux
        """
        try:
            logger.info(f"🤖 [AI] Analyse capture {platform}: {screenshot_path}")
            
            # Vérifier que le fichier existe
            if not os.path.exists(screenshot_path):
                logger.error(f"❌ [AI] Fichier capture introuvable: {screenshot_path}")
                return self._get_social_media_fallback(platform)
            
            # Lire l'image et la convertir en base64
            import base64
            with open(screenshot_path, "rb") as image_file:
                encoded_image = base64.b64encode(image_file.read()).decode('utf-8')
            
            # Créer le prompt pour l'analyse de capture d'écran
            prompt = SCREENSHOT_ANALYSIS_PROMPT.format(platform=platform)
            
            # Appeler l'API OpenAI Vision pour analyser la capture d'écran
            response = self._call_openai_vision_api(prompt, encoded_image)
            
            if response:
                logger.info(f"✅ [AI] Analyse capture {platform} réussie")
                return {
                    **response,
                    "analysis_success": True
                }
            else:
                logger.warning(f"⚠️ [AI] Échec analyse capture {platform}, utilisation du fallback")
                return self._get_social_media_fallback(platform)
            
        except Exception as e:
            logger.error(f"❌ [AI] Erreur analyse capture {platform}: {str(e)}")
            return {"error": str(e), "analysis_success": False}
    
    def _get_social_media_fallback(self, platform: str) -> Dict[str, Any]:
        """Résultat de fallback pour l'analyse des réseaux sociaux"""
        if platform == 'facebook':
            return {
                "followers": "Non détecté",
                "likes": "Non détecté",
                "description": "Non détecté",
                "contact_info": "Non détecté",
                "services": [],
                "horaires": "Non détecté",
                "public_cible": "Non détecté",
                "analysis_success": False,
                "error": "Échec de l'analyse IA"
            }
        elif platform == 'instagram':
            return {
                "followers": "Non détecté",
                "likes": "Non détecté",
                "description": "Non détecté",
                "contact_info": "Non détecté",
                "services": [],
                "horaires": "Non détecté",
                "public_cible": "Non détecté",
                "analysis_success": False,
                "error": "Échec de l'analyse IA"
            }
        else:
            return {
                "analysis_success": False,
                "error": f"Plateforme {platform} non supportée"
            }
    
    def score_lead_with_rag(self, lead) -> Dict[str, Any]:
        """
        Score un lead avec RAG (Retrieval-Augmented Generation)
        """
        try:
            logger.info(f"🤖 [AI] Scoring lead: {lead.nom}")
            
            # Calculer un score basé sur les données disponibles
            score = 0.0
            argumentaire = []
            
            # Score basé sur les informations de contact
            if lead.email:
                score += 10
                argumentaire.append("Email disponible")
            if lead.telephone:
                score += 10
                argumentaire.append("Téléphone disponible")
            if lead.adresse:
                score += 5
                argumentaire.append("Adresse disponible")
            
            # Score basé sur les réseaux sociaux
            if lead.facebook_url:
                score += 8
                argumentaire.append("Présence Facebook")
            if lead.instagram_url:
                score += 8
                argumentaire.append("Présence Instagram")
            
            # Score basé sur les données Google Maps
            if lead.note_google and lead.note_google >= 4.0:
                score += 15
                argumentaire.append(f"Bonne note Google ({lead.note_google})")
            if lead.nb_avis_google and lead.nb_avis_google >= 10:
                score += 10
                argumentaire.append(f"Nombre d'avis significatif ({lead.nb_avis_google})")
            
            # Score basé sur l'analyse IA du site web
            if lead.ai_analysis:
                ai_data = lead.ai_analysis
                if ai_data.get('contact', {}).get('emails'):
                    score += 5
                    argumentaire.append("Emails extraits du site")
                if ai_data.get('contact', {}).get('telephones'):
                    score += 5
                    argumentaire.append("Téléphones extraits du site")
                if ai_data.get('entreprise', {}).get('description'):
                    score += 3
                    argumentaire.append("Description d'entreprise disponible")
            
            # Score basé sur les données Facebook
            if lead.facebook_stats:
                score += 5
                argumentaire.append("Statistiques Facebook disponibles")
            
            # Score basé sur les données Instagram
            if lead.nb_followers_instagram and lead.nb_followers_instagram > 100:
                score += 8
                argumentaire.append(f"Audience Instagram ({lead.nb_followers_instagram} followers)")
            
            # Limiter le score à 100
            score = min(score, 100.0)
            
            return {
                "score": round(score, 1),
                "argumentaire": " | ".join(argumentaire) if argumentaire else "Données limitées",
                "status": "calculated"
            }
            
        except Exception as e:
            logger.error(f"❌ [AI] Erreur scoring lead: {str(e)}")
            return {"error": str(e), "score": 0.0, "status": "error"}

    def _split_html_into_chunks(self, html_content: str) -> List[str]:
        """
        Divise le HTML en sections intelligentes
        """
        chunks = []
        
        # 1. Header (premiers 10000 caractères)
        header_size = min(10000, len(html_content))
        chunks.append(html_content[:header_size])
        
        # 2. Chercher les sections importantes
        important_sections = []
        
        # Footer (derniers 10000 caractères)
        footer_size = min(10000, len(html_content))
        if len(html_content) > footer_size:
            chunks.append(html_content[-footer_size:])
        
        # Sections avec réseaux sociaux
        social_keywords = ['facebook', 'instagram', 'twitter', 'linkedin', 'youtube', 'tiktok']
        for keyword in social_keywords:
            start = html_content.lower().find(keyword)
            if start != -1:
                chunk_start = max(0, start - 5000)
                chunk_end = min(len(html_content), start + 5000)
                section = html_content[chunk_start:chunk_end]
                chunks.append(section)
        
        # Sections contact
        contact_keywords = ['contact', 'footer', 'adresse', 'téléphone', 'email']
        for keyword in contact_keywords:
            start = html_content.lower().find(keyword)
            if start != -1:
                chunk_start = max(0, start - 5000)
                chunk_end = min(len(html_content), start + 5000)
                section = html_content[chunk_start:chunk_end]
                chunks.append(section)
        
        # 3. Diviser le reste en chunks de 15000 caractères
        remaining_html = html_content
        for chunk in chunks:
            # Retirer les sections déjà traitées du HTML restant
            remaining_html = remaining_html.replace(chunk, "")
        
        # Diviser le HTML restant
        chunk_size = 15000
        for i in range(0, len(remaining_html), chunk_size):
            chunk = remaining_html[i:i + chunk_size]
            if len(chunk) > 1000:  # Ignorer les chunks trop petits
                chunks.append(chunk)
        
        # Dédupliquer et limiter le nombre de chunks
        unique_chunks = []
        seen_chunks = set()
        
        for chunk in chunks:
            chunk_hash = hash(chunk[:1000])  # Hash des 1000 premiers caractères
            if chunk_hash not in seen_chunks and len(chunk) > 1000:
                unique_chunks.append(chunk)
                seen_chunks.add(chunk_hash)
            
            # Limiter à 5 chunks maximum pour éviter trop d'appels API
            if len(unique_chunks) >= 5:
                break
        
        logger.info(f"📦 [CHUNKED] {len(unique_chunks)} sections uniques créées")
        return unique_chunks
    
    def _analyze_html_chunk(self, html_chunk: str, url: str, chunk_name: str) -> Optional[Dict[str, Any]]:
        """
        Analyse une section du HTML
        """
        try:
            # Créer un prompt spécifique pour cette section
            prompt = f"""
Analyse cette section HTML et extrait les informations importantes.

SECTION: {chunk_name}
URL: {url}

INSTRUCTIONS:
- Cherche les réseaux sociaux (Facebook, Instagram, Twitter, LinkedIn, YouTube, TikTok)
- Cherche les emails et téléphones
- Cherche les informations de contact
- Cherche le nom et la description de l'entreprise

RETOURNE UNIQUEMENT UN JSON VALIDE:
{{
  "contact": {{
    "emails": [],
    "telephones": [],
    "adresse": ""
  }},
  "entreprise": {{
    "nom": "",
    "description": ""
  }},
  "reseaux_sociaux": {{
    "facebook": "",
    "instagram": "",
    "twitter": "",
    "linkedin": "",
    "youtube": "",
    "tiktok": ""
  }}
}}

HTML:
{html_chunk}
"""
            
            # Appeler l'API avec cette section
            response = self._call_openai_api(prompt)
            return response
            
        except Exception as e:
            logger.error(f"❌ [CHUNKED] Erreur analyse section {chunk_name}: {str(e)}")
            return None
    
    def _merge_chunk_results(self, chunk_results: List[Dict[str, Any]], url: str) -> Dict[str, Any]:
        """
        Fusionne les résultats de toutes les sections
        """
        merged_result = {
            "contact": {
                "emails": [],
                "telephones": [],
                "adresse": ""
            },
            "entreprise": {
                "nom": "",
                "type": "",
                "description": "",
                "produits_services": [],
                "public_cible": ""
            },
            "pratique": {
                "horaires": "",
                "tarifs": "",
                "services": []
            },
            "reseaux_sociaux": {},
            "medias": {
                "images": 0,
                "videos": 0,
                "types_images": []
            }
        }
        
        # Fusionner les contacts
        all_emails = set()
        all_phones = set()
        
        for result in chunk_results:
            if not result:
                continue
                
            # Fusionner les emails
            emails = result.get('contact', {}).get('emails', [])
            all_emails.update(emails)
            
            # Fusionner les téléphones
            phones = result.get('contact', {}).get('telephones', [])
            all_phones.update(phones)
            
            # Fusionner les réseaux sociaux
            social = result.get('reseaux_sociaux', {})
            for platform, url in social.items():
                if url and url not in merged_result['reseaux_sociaux'].values():
                    merged_result['reseaux_sociaux'][platform] = url
            
            # Prendre la première description/entreprise trouvée
            if not merged_result['entreprise']['nom']:
                merged_result['entreprise']['nom'] = result.get('entreprise', {}).get('nom', '')
            
            if not merged_result['entreprise']['description']:
                merged_result['entreprise']['description'] = result.get('entreprise', {}).get('description', '')
        
        # Mettre à jour les contacts fusionnés
        merged_result['contact']['emails'] = list(all_emails)
        merged_result['contact']['telephones'] = list(all_phones)
        
        logger.info(f"🔗 [CHUNKED] Fusion terminée: {len(merged_result['reseaux_sociaux'])} réseaux sociaux, {len(all_emails)} emails, {len(all_phones)} téléphones")
        
        return merged_result