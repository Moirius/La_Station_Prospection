"""
Module de scraping de sites web utilisant Scrapy - Version améliorée
Alternative moderne et performante au scraper requests/BeautifulSoup
"""

import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from scrapy.http import Request
from typing import Dict, Any, Optional, List
import json
import re
from urllib.parse import urljoin, urlparse
from app.utils.logger import get_logger
from app.config import Config
import subprocess
import sys
import os
import tempfile
import logging
import requests
import time

logger = get_logger('scrapy_spider_improved')

# Force le logger à écrire dans le fichier de logs principal
file_handler = logging.FileHandler('logs/prospection.log', encoding='utf-8')
formatter = logging.Formatter('%(asctime)s - prospection - %(levelname)s - [scrapy] %(message)s')
file_handler.setFormatter(formatter)
logger.handlers = []  # Supprime les handlers existants pour éviter les doublons
logger.addHandler(file_handler)
logger.setLevel(logging.INFO)

class WebsiteSpider(scrapy.Spider):
    """Spider Scrapy pour extraire les données des sites web"""
    
    name = 'website_spider'
    
    def __init__(self, url=None, result_path=None, *args, **kwargs):
        super(WebsiteSpider, self).__init__(*args, **kwargs)
        self.start_urls = [url] if url else []
        self.extracted_data = {}
        self.result_path = result_path
        
    def start_requests(self):
        """Démarre les requêtes de scraping"""
        for url in self.start_urls:
            logger.info(f"🔍 Démarrage du scraping Scrapy pour: {url}")
            yield Request(
                url=url,
                callback=self.parse,
                meta={'url': url},
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                    'Accept-Language': 'fr-FR,fr;q=0.9,en;q=0.8',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1',
                    'Sec-Fetch-Dest': 'document',
                    'Sec-Fetch-Mode': 'navigate',
                    'Sec-Fetch-Site': 'none',
                    'Cache-Control': 'max-age=0',
                }
            )
    
    def parse(self, response):
        """Parse la page web et extrait les données"""
        url = response.meta.get('url', response.url)
        logger.info(f"📄 Parsing de la page: {url}")
        
        try:
            # Vérifier si le contenu est du texte
            if not hasattr(response, 'text') or not response.text:
                logger.warning(f"⚠️ [PARSE] Contenu non-textuel détecté pour {url}")
                # Essayer d'extraire le contenu brut
                try:
                    raw_content = response.body.decode('utf-8', errors='ignore')
                    logger.info(f"📄 [PARSE] Contenu brut extrait: {len(raw_content)} caractères")
                    
                    # Créer un faux résultat avec les données extraites manuellement
                    website_data = self._extract_from_raw_content(raw_content, url)
                    return website_data
                    
                except Exception as e:
                    logger.error(f"❌ [PARSE] Erreur extraction contenu brut: {str(e)}")
                    return {
                        'url': url,
                        'scraping_success': False,
                        'error': f"Contenu non-textuel: {str(e)}"
                    }
            
            # Extraction normale si le contenu est du texte
            # Extraction exhaustive des réseaux sociaux
            social_media = self._extract_social_media_all(response)
            # Extraction exhaustive des emails/téléphones
            emails = self._extract_emails_all(response)
            phones = self._extract_phones_all(response)
            # Extraction des liens importants
            links = self._extract_important_links(response)
            # Extraction de l'adresse et horaires
            address, opening_hours = self._extract_address_hours(response)
            # Extraction des microdonnées/JSON-LD
            structured_data = self._extract_structured_data(response)

            website_data = {
                'url': url,
                'title': self._extract_title(response),
                'description': self._extract_description(response),
                'emails': emails,
                'phones': phones,
                'social_media': social_media,
                'links': links,
                'address': address,
                'opening_hours': opening_hours,
                'structured_data': structured_data,
                'has_video': self._has_video(response),
                'has_images': self._has_images(response),
                'images_count': self._count_images(response),
                'videos_count': self._count_videos(response),
                'text_summary': self._extract_text_summary(response),
                'products_services': self._has_products_services(response),
                'contact_form': self._has_contact_form(response),
                'scraping_success': True
            }
            
            # Logs des résultats
            logger.info(f"📊 Résultats scraping Scrapy {url}:")
            logger.info(f"   📧 Emails trouvés: {len(website_data.get('emails', []))}")
            logger.info(f"   📞 Téléphones trouvés: {len(website_data.get('phones', []))}")
            logger.info(f"   🖼️ Images: {website_data.get('images_count', 0)}")
            logger.info(f"   🎥 Vidéos: {website_data.get('videos_count', 0)}")
            logger.info(f"   📱 Réseaux sociaux: {len(website_data.get('social_media', {}))}")
            # Log détaillé des réseaux sociaux
            for platform, links in website_data.get('social_media', {}).items():
                logger.info(f"      - {platform}: {len(links)} liens")
                for link in links:
                    logger.info(f"         {link}")
            # Log détaillé des liens importants
            if website_data.get('links'):
                logger.info(f"   🔗 Liens importants extraits ({len(website_data['links'])}):")
                for l in website_data['links']:
                    logger.info(f"      {l}")
            
            self.extracted_data = website_data
            # Si un chemin de résultat est fourni, écrire le résultat dans ce fichier
            if self.result_path:
                try:
                    with open(self.result_path, 'w', encoding='utf-8') as f:
                        json.dump(self.extracted_data, f, ensure_ascii=False, indent=2)
                    logger.info(f"💾 Résultat écrit dans {self.result_path}")
                except Exception as e:
                    logger.error(f"Erreur lors de l'écriture du résultat: {str(e)}")
            return website_data
            
        except Exception as e:
            logger.error(f"❌ [PARSE] Erreur lors du parsing de {url}: {str(e)}")
            return {
                'url': url,
                'scraping_success': False,
                'error': str(e)
            }
    
    def _extract_title(self, response) -> str:
        """Extraire le titre de la page"""
        # Meta title
        title = response.css('title::text').get()
        if title:
            title = title.strip()
            logger.info(f"📝 Titre trouvé: {title[:50]}...")
            return title
        
        # Fallback: H1
        h1 = response.css('h1::text').get()
        if h1:
            h1 = h1.strip()
            logger.info(f"📝 Titre H1 trouvé: {h1[:50]}...")
            return h1
        
        logger.warning("⚠️ Aucun titre trouvé")
        return ""
    
    def _extract_description(self, response) -> str:
        """Extraire la description de la page"""
        # Meta description
        desc = response.css('meta[name="description"]::attr(content)').get()
        if desc:
            desc = desc.strip()
            logger.info(f"📄 Description meta trouvée: {desc[:50]}...")
            return desc
        
        # Open Graph description
        og_desc = response.css('meta[property="og:description"]::attr(content)').get()
        if og_desc:
            og_desc = og_desc.strip()
            logger.info(f"📄 Description OG trouvée: {og_desc[:50]}...")
            return og_desc
        
        logger.warning("⚠️ Aucune description trouvée")
        return ""
    
    def _extract_social_media_all(self, response) -> dict:
        """Extraction exhaustive des liens réseaux sociaux (a, meta, scripts, JSON-LD)"""
        social_media = {}
        
        logger.info(f"🔍 [SOCIAL] Début extraction réseaux sociaux pour {response.url}")
        
        # 1. Liens <a> - AMÉLIORÉ
        for a in response.css('a[href]'):
            href = a.attrib.get('href', '')
            text = a.css('::text').get() or ''
            title = a.attrib.get('title', '')
            classes = ' '.join(a.attrib.get('class', []))
            
            # Chercher dans href, texte, title et classes
            search_text = f"{href} {text} {title} {classes}".lower()
            
            for platform in ['facebook', 'instagram', 'twitter', 'linkedin', 'youtube', 'tiktok']:
                if platform in search_text:
                    full_url = response.urljoin(href)
                    social_media.setdefault(platform, []).append(full_url)
                    logger.info(f"📱 [SOCIAL] {platform} trouvé dans lien: {full_url}")
        
        # 2. Meta tags - AMÉLIORÉ
        for meta in response.css('meta'):
            content = meta.attrib.get('content', '')
            property_attr = meta.attrib.get('property', '')
            name_attr = meta.attrib.get('name', '')
            
            # Chercher dans content, property et name
            search_text = f"{content} {property_attr} {name_attr}".lower()
            
            for platform in ['facebook', 'instagram', 'twitter', 'linkedin', 'youtube', 'tiktok']:
                if platform in search_text:
                    social_media.setdefault(platform, []).append(content)
                    logger.info(f"📱 [SOCIAL] {platform} trouvé dans meta: {content}")
        
        # 3. Scripts - AMÉLIORÉ
        for script in response.css('script'):
            script_text = script.get()
            if script_text:
                # Chercher les URLs complètes
                for platform in ['facebook', 'instagram', 'twitter', 'linkedin', 'youtube', 'tiktok']:
                    # Pattern pour URLs complètes
                    urls = re.findall(rf'https?://[^\s"\'>]*{platform}[^\s"\'>]*', script_text, re.IGNORECASE)
                    for url in urls:
                        social_media.setdefault(platform, []).append(url)
                        logger.info(f"📱 [SOCIAL] {platform} trouvé dans script: {url}")
                    
                    # Pattern pour chemins relatifs
                    paths = re.findall(rf'/{platform}[^\s"\'>]*', script_text, re.IGNORECASE)
                    for path in paths:
                        full_url = response.urljoin(path)
                        social_media.setdefault(platform, []).append(full_url)
                        logger.info(f"📱 [SOCIAL] {platform} trouvé dans script (path): {full_url}")
        
        # 4. JSON-LD - AMÉLIORÉ
        for script in response.css('script[type="application/ld+json"]::text').getall():
            try:
                data = json.loads(script)
                self._extract_social_from_json(data, social_media, response)
            except Exception as e:
                logger.debug(f"⚠️ [SOCIAL] Erreur parsing JSON-LD: {str(e)}")
                continue
        
        # 5. Chercher dans les icônes et classes CSS
        for element in response.css('*[class*="facebook"], *[class*="instagram"], *[class*="twitter"], *[class*="linkedin"], *[class*="youtube"], *[class*="social"]'):
            classes = ' '.join(element.attrib.get('class', []))
            parent = element.xpath('..')
            
            # Chercher le lien parent
            if parent and parent.css('a[href]'):
                href = parent.css('a::attr(href)').get()
                if href:
                    for platform in ['facebook', 'instagram', 'twitter', 'linkedin', 'youtube', 'tiktok']:
                        if platform in classes.lower():
                            full_url = response.urljoin(href)
                            social_media.setdefault(platform, []).append(full_url)
                            logger.info(f"📱 [SOCIAL] {platform} trouvé via icône: {full_url}")
        
        # 6. Chercher dans le texte brut
        text_content = response.text
        for platform in ['facebook', 'instagram', 'twitter', 'linkedin', 'youtube', 'tiktok']:
            # URLs complètes
            urls = re.findall(rf'https?://[^\s"\'>]*{platform}[^\s"\'>]*', text_content, re.IGNORECASE)
            for url in urls:
                social_media.setdefault(platform, []).append(url)
                logger.info(f"📱 [SOCIAL] {platform} trouvé dans texte: {url}")
        
        # Dédupliquer les URLs
        for platform in social_media:
            social_media[platform] = list(set(social_media[platform]))
        
        logger.info(f"✅ [SOCIAL] Extraction terminée: {len(social_media)} plateformes trouvées")
        for platform, urls in social_media.items():
            logger.info(f"   📱 {platform}: {len(urls)} URLs")
            for url in urls:
                logger.info(f"      - {url}")
        
        return social_media
    
    def _extract_social_from_json(self, data, social_media, response):
        """Extrait les réseaux sociaux depuis les données JSON"""
        if isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, str):
                    for platform in ['facebook', 'instagram', 'twitter', 'linkedin', 'youtube', 'tiktok']:
                        if platform in value.lower():
                            social_media.setdefault(platform, []).append(value)
                            logger.info(f"📱 [SOCIAL] {platform} trouvé dans JSON: {value}")
                elif isinstance(value, list):
                    for item in value:
                        if isinstance(item, str):
                            for platform in ['facebook', 'instagram', 'twitter', 'linkedin', 'youtube', 'tiktok']:
                                if platform in item.lower():
                                    social_media.setdefault(platform, []).append(item)
                                    logger.info(f"📱 [SOCIAL] {platform} trouvé dans JSON array: {item}")
                elif isinstance(value, dict):
                    self._extract_social_from_json(value, social_media, response)
        elif isinstance(data, list):
            for item in data:
                self._extract_social_from_json(item, social_media, response)

    def _extract_emails_all(self, response) -> list:
        """Extraction exhaustive des emails (texte, href, meta, scripts, JSON-LD)"""
        emails = set()
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        
        logger.info(f"🔍 [EMAIL] Début extraction emails pour {response.url}")
        
        # Texte brut
        text_emails = re.findall(email_pattern, response.text)
        emails.update(text_emails)
        logger.info(f"📧 [EMAIL] {len(text_emails)} emails trouvés dans le texte")
        
        # Href mailto
        mailto_emails = []
        for mailto in response.css('a[href^="mailto:"]::attr(href)').getall():
            email = mailto.replace('mailto:', '').split('?')[0]
            if re.match(email_pattern, email):
                emails.add(email)
                mailto_emails.append(email)
        logger.info(f"📧 [EMAIL] {len(mailto_emails)} emails trouvés dans les liens mailto")
        
        # Meta
        meta_emails = []
        for meta in response.css('meta'):
            content = meta.attrib.get('content', '')
            found_emails = re.findall(email_pattern, content)
            emails.update(found_emails)
            meta_emails.extend(found_emails)
        logger.info(f"📧 [EMAIL] {len(meta_emails)} emails trouvés dans les meta tags")
        
        # Scripts
        script_emails = []
        for script in response.css('script'):
            script_text = script.get()
            if script_text:
                found_emails = re.findall(email_pattern, script_text)
                emails.update(found_emails)
                script_emails.extend(found_emails)
        logger.info(f"📧 [EMAIL] {len(script_emails)} emails trouvés dans les scripts")
        
        # JSON-LD
        jsonld_emails = []
        for script in response.css('script[type="application/ld+json"]::text').getall():
            try:
                data = json.loads(script)
                if isinstance(data, dict):
                    for v in data.values():
                        if isinstance(v, str):
                            found_emails = re.findall(email_pattern, v)
                            emails.update(found_emails)
                            jsonld_emails.extend(found_emails)
                        elif isinstance(v, list):
                            for item in v:
                                if isinstance(item, str):
                                    found_emails = re.findall(email_pattern, item)
                                    emails.update(found_emails)
                                    jsonld_emails.extend(found_emails)
            except Exception:
                continue
        logger.info(f"📧 [EMAIL] {len(jsonld_emails)} emails trouvés dans JSON-LD")
        
        final_emails = list(emails)
        logger.info(f"✅ [EMAIL] Total emails uniques extraits: {len(final_emails)}")
        for email in final_emails:
            logger.debug(f"📧 [EMAIL] Email trouvé: {email}")
        
        return final_emails

    def _extract_phones_all(self, response) -> list:
        """Extraction exhaustive des téléphones (texte, href, meta, scripts, JSON-LD)"""
        phones = set()
        phone_pattern = r'(?:\+33|0033|33|0)[1-9](?:[ .-]?\d{2}){4}'
        # Texte brut
        phones.update(re.findall(phone_pattern, response.text))
        # Href tel
        for tel in response.css('a[href^="tel:"]::attr(href)').getall():
            phone = tel.replace('tel:', '').strip()
            if re.match(phone_pattern, phone):
                phones.add(phone)
        # Meta
        for meta in response.css('meta'):
            content = meta.attrib.get('content', '')
            phones.update(re.findall(phone_pattern, content))
        # Scripts
        for script in response.css('script'):
            script_text = script.get()
            if script_text:
                phones.update(re.findall(phone_pattern, script_text))
        # JSON-LD
        for script in response.css('script[type="application/ld+json"]::text').getall():
            try:
                data = json.loads(script)
                if isinstance(data, dict):
                    for v in data.values():
                        if isinstance(v, str):
                            phones.update(re.findall(phone_pattern, v))
                        elif isinstance(v, list):
                            for item in v:
                                if isinstance(item, str):
                                    phones.update(re.findall(phone_pattern, item))
            except Exception:
                continue
        return list(phones)

    def _extract_important_links(self, response) -> list:
        """Extraction des liens de contact, réservation, menu, etc."""
        keywords = ['contact', 'reservation', 'menu', 'carte', 'book', 'reserver', 'access', 'localisation', 'find-us']
        links = set()
        for a in response.css('a[href]'):
            href = a.attrib.get('href', '')
            text = a.css('::text').get() or ''
            if any(kw in href.lower() or kw in text.lower() for kw in keywords):
                links.add(response.urljoin(href))
        return list(links)

    def _extract_address_hours(self, response):
        """Extraction de l'adresse et des horaires (balises, microdonnées, JSON-LD)"""
        address = ''
        opening_hours = ''
        # Balises address
        addr = response.css('address::text').get()
        if addr:
            address = addr.strip()
        # Microdonnées/JSON-LD
        for script in response.css('script[type="application/ld+json"]::text').getall():
            try:
                data = json.loads(script)
                if isinstance(data, dict):
                    if 'address' in data:
                        if isinstance(data['address'], dict):
                            address = ', '.join([str(v) for v in data['address'].values() if v])
                        elif isinstance(data['address'], str):
                            address = data['address']
                    if 'openingHours' in data:
                        opening_hours = data['openingHours']
            except Exception:
                continue
        # Recherche dans le texte pour les horaires
        if not opening_hours:
            for kw in ['horaires', 'ouverture', 'opening']:
                found = re.findall(rf'{kw}[^\n\r:]*[:\-]([^\n\r<]+)', response.text, re.IGNORECASE)
                if found:
                    opening_hours = found[0].strip()
                    break
        return address, opening_hours

    def _extract_structured_data(self, response):
        """Extraction brute des scripts JSON-LD"""
        data = []
        for script in response.css('script[type="application/ld+json"]::text').getall():
            try:
                json_data = json.loads(script)
                data.append(json_data)
            except Exception:
                continue
        return data
    
    def _has_video(self, response) -> bool:
        """Détecter la présence de vidéos"""
        # Chercher les balises video
        video_tags = response.css('video').getall()
        if video_tags:
            logger.info(f"🎥 Vidéos trouvées: {len(video_tags)} balises video")
            return True
        
        # Chercher les iframes YouTube/Vimeo
        iframe_srcs = response.css('iframe::attr(src)').getall()
        video_platforms = ['youtube', 'vimeo', 'dailymotion', 'vimeo']
        
        for src in iframe_srcs:
            if any(platform in src.lower() for platform in video_platforms):
                logger.info(f"🎥 Vidéo iframe trouvée: {src}")
                return True
        
        # Chercher les liens vers des vidéos
        video_links = response.css('a[href*="youtube"], a[href*="vimeo"], a[href*="dailymotion"]').getall()
        if video_links:
            logger.info(f"🎥 Liens vidéo trouvés: {len(video_links)}")
            return True
        
        return False
    
    def _count_videos(self, response) -> int:
        """Compter le nombre de vidéos"""
        count = 0
        
        # Balises video
        count += len(response.css('video').getall())
        
        # Iframes vidéo
        iframe_srcs = response.css('iframe::attr(src)').getall()
        video_platforms = ['youtube', 'vimeo', 'dailymotion']
        for src in iframe_srcs:
            if any(platform in src.lower() for platform in video_platforms):
                count += 1
        
        # Liens vidéo
        video_links = response.css('a[href*="youtube"], a[href*="vimeo"], a[href*="dailymotion"]').getall()
        count += len(video_links)
        
        return count
    
    def _has_images(self, response) -> bool:
        """Détecter la présence d'images"""
        images = response.css('img').getall()
        if images:
            logger.info(f"🖼️ Images trouvées: {len(images)}")
            return True
        return False
    
    def _count_images(self, response) -> int:
        """Compter le nombre d'images"""
        return len(response.css('img').getall())
    
    def _extract_text_summary(self, response) -> str:
        """Extraire un résumé du texte de la page"""
        # Extraire le texte des paragraphes
        paragraphs = response.css('p::text').getall()
        text = ' '.join([p.strip() for p in paragraphs if p.strip()])
        
        # Limiter à 500 caractères
        if len(text) > 500:
            text = text[:500] + "..."
        
        return text
    
    def _has_products_services(self, response) -> bool:
        """Détecter la présence de produits/services"""
        # Mots-clés liés aux produits/services
        keywords = ['produit', 'service', 'tarif', 'prix', 'commander', 'acheter', 'réservation', 'booking']
        page_text = response.text.lower()
        
        for keyword in keywords:
            if keyword in page_text:
                logger.info(f"🛍️ Produits/services détectés (mot-clé: {keyword})")
                return True
        
        return False
    
    def _has_contact_form(self, response) -> bool:
        """Détecter la présence d'un formulaire de contact"""
        # Chercher les formulaires
        forms = response.css('form').getall()
        if forms:
            logger.info(f"📝 Formulaires trouvés: {len(forms)}")
            return True
        
        # Chercher les liens de contact
        contact_links = response.css('a[href*="contact"], a[href*="nous-contacter"]').getall()
        if contact_links:
            logger.info(f"📝 Liens de contact trouvés: {len(contact_links)}")
            return True
        
        return False

    def _extract_from_raw_content(self, raw_content: str, url: str) -> dict:
        """Extraire les données depuis le contenu brut"""
        logger.info(f"🔍 [RAW] Extraction depuis le contenu brut de {url}")
        logger.info(f"📏 [RAW] Taille du contenu brut: {len(raw_content)} caractères")
        
        # Essayer différents encodages si le contenu semble tronqué
        if len(raw_content) < 1000:
            logger.warning(f"⚠️ [RAW] Contenu brut trop court, tentative de décodage alternatif")
            try:
                # Essayer de récupérer le contenu depuis la réponse
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                    'Accept-Language': 'fr-FR,fr;q=0.9,en;q=0.8',
                }
                response = requests.get(url, headers=headers, timeout=10)
                if response.status_code == 200:
                    raw_content = response.text
                    logger.info(f"📄 [RAW] Contenu récupéré via requests: {len(raw_content)} caractères")
            except Exception as e:
                logger.warning(f"⚠️ [RAW] Échec récupération via requests: {str(e)}")
        
        # Extraction des emails
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, raw_content)
        logger.info(f"📧 [RAW] {len(emails)} emails trouvés dans le contenu brut")
        for email in emails:
            logger.info(f"   📧 [RAW] Email trouvé: {email}")
        
        # Extraction des téléphones
        phone_pattern = r'(?:\+33|0033|33|0)[1-9](?:[ .-]?\d{2}){4}'
        phones = re.findall(phone_pattern, raw_content)
        logger.info(f"📞 [RAW] {len(phones)} téléphones trouvés dans le contenu brut")
        for phone in phones:
            logger.info(f"   📞 [RAW] Téléphone trouvé: {phone}")
        
        # Extraction du titre
        title_match = re.search(r'<title[^>]*>([^<]+)</title>', raw_content, re.IGNORECASE)
        title = title_match.group(1) if title_match else ""
        logger.info(f"📝 [RAW] Titre extrait: {title}")
        
        # Extraction de la description
        desc_match = re.search(r'<meta[^>]*name=["\']description["\'][^>]*content=["\']([^"\']+)["\']', raw_content, re.IGNORECASE)
        description = desc_match.group(1) if desc_match else ""
        logger.info(f"📄 [RAW] Description extraite: {description[:100]}...")
        
        # Extraction des réseaux sociaux
        social_media = {}
        social_patterns = {
            'instagram': r'https?://[^\s"\'>]*instagram[^\s"\'>]*',
            'facebook': r'https?://[^\s"\'>]*facebook[^\s"\'>]*',
            'twitter': r'https?://[^\s"\'>]*twitter[^\s"\'>]*',
            'linkedin': r'https?://[^\s"\'>]*linkedin[^\s"\'>]*',
            'youtube': r'https?://[^\s"\'>]*youtube[^\s"\'>]*',
        }
        
        for platform, pattern in social_patterns.items():
            matches = re.findall(pattern, raw_content, re.IGNORECASE)
            if matches:
                social_media[platform] = list(set(matches))
                logger.info(f"📱 [RAW] {platform}: {len(matches)} liens trouvés")
        
        logger.info(f"📱 [RAW] {len(social_media)} réseaux sociaux trouvés")
        
        return {
            'url': url,
            'title': title,
            'description': description,
            'emails': emails,
            'phones': phones,
            'social_media': social_media,
            'links': [],
            'address': '',
            'opening_hours': '',
            'structured_data': [],
            'has_video': False,
            'has_images': False,
            'images_count': 0,
            'videos_count': 0,
            'text_summary': raw_content[:500] + "..." if len(raw_content) > 500 else raw_content,
            'products_services': False,
            'contact_form': False,
            'scraping_success': True
        }


class ScrapyWebsiteScraperImproved:
    """Scraper de sites web amélioré avec analyse IA"""
    
    def __init__(self):
        self.ai_service = None
        try:
            from app.services.ai_analysis_service import AIAnalysisService
            self.ai_service = AIAnalysisService()
            logger.info("✅ Service IA initialisé")
        except Exception as e:
            logger.warning(f"⚠️ Service IA non disponible: {str(e)}")
    
    def get_raw_html(self, url: str) -> Optional[str]:
        """
        Récupère le HTML brut d'un site web
        
        Args:
            url: L'URL du site à scraper
            
        Returns:
            Le code HTML brut ou None si erreur
        """
        try:
            logger.info(f"🔍 [SCRAPER] Récupération HTML brut pour {url}")
            
            # Utiliser requests directement pour plus de contrôle
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                'Accept-Language': 'fr-FR,fr;q=0.9,en;q=0.8',
                'Accept-Encoding': 'gzip, deflate',  # Pas de br pour éviter les problèmes
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            }
            
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            
            # Décoder le contenu
            html_content = response.text
            
            logger.info(f"✅ [SCRAPER] HTML récupéré: {len(html_content)} caractères")
            return html_content
                
        except Exception as e:
            logger.error(f"❌ [SCRAPER] Erreur récupération HTML: {str(e)}")
            return None
    
    def analyze_with_ai(self, html_content: str, url: str = "") -> Dict[str, Any]:
        """
        Analyse le HTML avec l'IA
        
        Args:
            html_content: Le code HTML brut
            url: L'URL du site
            
        Returns:
            Résultat de l'analyse IA
        """
        if not self.ai_service:
            logger.error("❌ [SCRAPER] Service IA non disponible")
            return {"error": "Service IA non disponible"}
        
        try:
            logger.info(f"🤖 [SCRAPER] Début analyse IA pour {url}")
            result = self.ai_service.analyze_website(html_content, url)
            logger.info(f"✅ [SCRAPER] Analyse IA terminée")
            return result
            
        except Exception as e:
            logger.error(f"❌ [SCRAPER] Erreur analyse IA: {str(e)}")
            return {"error": f"Erreur analyse IA: {str(e)}"}
    
    def analyze_with_ai_full_html(self, html_content: str, url: str = "") -> Dict[str, Any]:
        """
        Analyse le HTML COMPLET avec l'IA (sans troncature)
        
        Args:
            html_content: Le code HTML brut complet
            url: L'URL du site
            
        Returns:
            Résultat de l'analyse IA
        """
        if not self.ai_service:
            logger.error("❌ [SCRAPER FULL] Service IA non disponible")
            return {"error": "Service IA non disponible"}
        
        try:
            logger.info(f"🤖 [SCRAPER FULL] Début analyse IA HTML complet pour {url}")
            logger.info(f"📏 [SCRAPER FULL] HTML complet: {len(html_content)} caractères")
            
            # Utiliser la nouvelle méthode d'analyse HTML complet
            result = self.ai_service.analyze_website_full_html(html_content, url)
            logger.info(f"✅ [SCRAPER FULL] Analyse IA HTML complet terminée")
            return result
            
        except Exception as e:
            logger.error(f"❌ [SCRAPER FULL] Erreur analyse IA HTML complet: {str(e)}")
            return {"error": f"Erreur analyse IA HTML complet: {str(e)}"}
    
    def analyze_with_ai_chunked(self, html_content: str, url: str = "") -> Dict[str, Any]:
        """
        Analyse le HTML en sections avec l'IA
        
        Args:
            html_content: Le code HTML brut complet
            url: L'URL du site
            
        Returns:
            Résultat de l'analyse IA par sections
        """
        if not self.ai_service:
            logger.error("❌ [SCRAPER CHUNKED] Service IA non disponible")
            return {"error": "Service IA non disponible"}
        
        try:
            logger.info(f"🤖 [SCRAPER CHUNKED] Début analyse IA par sections pour {url}")
            logger.info(f"📏 [SCRAPER CHUNKED] HTML complet: {len(html_content)} caractères")
            
            # Utiliser la nouvelle méthode d'analyse par sections
            result = self.ai_service.analyze_website_chunked(html_content, url)
            logger.info(f"✅ [SCRAPER CHUNKED] Analyse IA par sections terminée")
            return result
            
        except Exception as e:
            logger.error(f"❌ [SCRAPER CHUNKED] Erreur analyse IA par sections: {str(e)}")
            return {"error": f"Erreur analyse IA par sections: {str(e)}"}
    
    def scrape_website_with_ai(self, url: str) -> Optional[Dict[str, Any]]:
        """
        Scrape un site web avec analyse IA
        
        Args:
            url: L'URL du site à scraper
            
        Returns:
            Résultat complet avec analyse IA
        """
        try:
            logger.info(f"🚀 [SCRAPER] Début scraping IA pour {url}")
            
            # 1. Récupérer le HTML brut
            html_content = self.get_raw_html(url)
            if not html_content:
                logger.error(f"❌ [SCRAPER] Impossible de récupérer le HTML pour {url}")
                return None
            
            # 2. Choisir la méthode d'analyse selon la taille du HTML
            if len(html_content) > 200000:  # Très gros HTML
                logger.info(f"📏 [SCRAPER] HTML très volumineux ({len(html_content)} caractères), utilisation de l'analyse par sections")
                ai_result = self.analyze_with_ai_chunked(html_content, url)
            elif len(html_content) > 100000:  # Gros HTML
                logger.info(f"📏 [SCRAPER] HTML volumineux ({len(html_content)} caractères), utilisation de l'analyse complète")
                ai_result = self.analyze_with_ai_full_html(html_content, url)
            else:  # HTML normal
                logger.info(f"📏 [SCRAPER] HTML normal ({len(html_content)} caractères), utilisation de l'analyse standard")
                ai_result = self.analyze_with_ai(html_content, url)
            
            # 3. Combiner les résultats
            final_result = {
                "url": url,
                "scraping_success": True,
                "html_size": len(html_content),
                "ai_analysis": ai_result,
                "timestamp": time.time()
            }
            
            logger.info(f"✅ [SCRAPER] Scraping IA terminé pour {url}")
            return final_result
            
        except Exception as e:
            logger.error(f"❌ [SCRAPER] Erreur scraping IA: {str(e)}")
            return {
                "url": url,
                "scraping_success": False,
                "error": str(e)
            }
    
    def scrape_website(self, url: str) -> Optional[Dict[str, Any]]:
        """
        Scraper un site web avec Scrapy en utilisant un processus séparé
        
        Args:
            url: URL du site web à scraper
            
        Returns:
            Données extraites du site ou None
        """
        try:
            logger.info(f"🚀 Démarrage du scraping Scrapy pour: {url}")
            
            # Créer un fichier temporaire pour les résultats
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp_file:
                temp_filename = temp_file.name
            
            # Correction : ajouter le chemin racine du projet dans sys.path du script généré
            project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
            project_root_escaped = json.dumps(project_root)
            temp_filename_escaped = json.dumps(temp_filename)
            script_content = f'''
import sys
import os
import json
import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

# Ajouter le chemin racine du projet dans sys.path
sys.path.insert(0, {project_root_escaped})

from app.scrapers.scrapy_spider_improved import WebsiteSpider

def run_spider():
    try:
        # Configuration Scrapy
        settings = get_project_settings()
        settings.update({{
            'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'ROBOTSTXT_OBEY': False,
            'DOWNLOAD_DELAY': 1,
            'CONCURRENT_REQUESTS': 1,
            'CONCURRENT_REQUESTS_PER_DOMAIN': 1,
            'AUTOTHROTTLE_ENABLED': True,
            'AUTOTHROTTLE_START_DELAY': 1,
            'AUTOTHROTTLE_MAX_DELAY': 3,
            'AUTOTHROTTLE_TARGET_CONCURRENCY': 1.0,
            'COOKIES_ENABLED': False,
            'TELNETCONSOLE_ENABLED': False,
            'LOG_LEVEL': 'ERROR',  # Réduire les logs
        }})
        
        # Créer le processus de crawling
        process = CrawlerProcess(settings)
        process.crawl(WebsiteSpider, url="{url}", result_path={temp_filename_escaped})
        process.start()
        
    except Exception as e:
        print(f"Erreur: {{str(e)}}", file=sys.stderr)

if __name__ == "__main__":
    run_spider()
'''
            
            # Créer le script temporaire
            script_filename = temp_filename.replace('.json', '_script.py')
            with open(script_filename, 'w', encoding='utf-8') as f:
                f.write(script_content)
            
            # Exécuter le script dans un processus séparé
            try:
                result = subprocess.run(
                    [sys.executable, script_filename],
                    capture_output=True,
                    text=True,
                    timeout=60,
                    cwd=os.getcwd()
                )
                
                # Log du stdout et stderr du sous-processus
                if result.stdout:
                    logger.info(f"[SCRAPY STDOUT] {result.stdout}")
                if result.stderr:
                    logger.error(f"[SCRAPY STDERR] {result.stderr}")
                
                # Vérifier si le fichier de résultats existe
                if os.path.exists(temp_filename):
                    with open(temp_filename, 'r', encoding='utf-8') as f:
                        result_data = json.load(f)
                    
                    if result_data and result_data.get('scraping_success'):
                        logger.info(f"✅ Scraping Scrapy réussi pour {url}")
                        return result_data
                    else:
                        logger.error(f"❌ Échec du scraping Scrapy pour {url}")
                        return None
                else:
                    logger.error(f"❌ Aucun fichier de résultats généré pour {url}")
                    if result.stderr:
                        logger.error(f"Erreur: {result.stderr}")
                    return None
                    
            except subprocess.TimeoutExpired:
                logger.error(f"❌ Timeout du scraping Scrapy pour {url}")
                return None
            except Exception as e:
                logger.error(f"❌ Erreur lors de l'exécution du processus: {str(e)}")
                return None
            finally:
                # Nettoyer les fichiers temporaires
                try:
                    os.unlink(temp_filename)
                    if os.path.exists(temp_filename.replace('_script.py', '.json')):
                        os.unlink(temp_filename.replace('_script.py', '.json'))
                except:
                    pass
                
        except Exception as e:
            logger.error(f"❌ Erreur lors du scraping Scrapy {url}: {str(e)}")
            return None
    
    def scrape_multiple_websites(self, urls: List[str]) -> List[Dict[str, Any]]:
        """
        Scraper plusieurs sites web
        
        Args:
            urls: Liste des URLs à scraper
            
        Returns:
            Liste des données extraites
        """
        results = []
        
        for url in urls:
            logger.info(f"🔄 Scraping de {url}")
            result = self.scrape_website(url)
            if result:
                results.append(result)
            else:
                logger.warning(f"⚠️ Échec du scraping pour {url}")
        
        logger.info(f"📊 Scraping terminé: {len(results)}/{len(urls)} sites traités avec succès")
        return results 