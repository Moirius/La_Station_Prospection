"""
Service de capture d'écran des réseaux sociaux avec Playwright
"""

import os
import time
from pathlib import Path
from typing import Optional, Dict, Any
from playwright.sync_api import sync_playwright, Browser, Page
from app.utils.logger import SystemLogger
from app.config import Config

class ScreenshotService:
    """Service de capture d'écran des réseaux sociaux"""
    
    def __init__(self):
        self.screenshots_dir = Path("screenshots")
        self.screenshots_dir.mkdir(exist_ok=True)
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
        
        # Chemins des cookies
        self.facebook_cookies_path = 'fb_cookies.pkl'
        self.instagram_cookies_path = 'instagram_cookies.pkl'
        
    def __enter__(self):
        """Context manager entry"""
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(
            headless=True,
            args=[
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
                '--disable-accelerated-2d-canvas',
                '--no-first-run',
                '--no-zygote',
                '--disable-gpu'
            ]
        )
        if self.browser:
            self.page = self.browser.new_page()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        if self.page:
            self.page.close()
        if self.browser:
            self.browser.close()
        if hasattr(self, 'playwright'):
            self.playwright.stop()
    
    def load_selenium_cookies_to_playwright(self, cookies_path: str) -> bool:
        """Charger les cookies Selenium dans Playwright"""
        try:
            if not os.path.exists(cookies_path):
                SystemLogger.warning(f"Fichier de cookies non trouvé: {cookies_path}")
                return False
            
            if not self.page:
                SystemLogger.error("Page non initialisée")
                return False
            
            import pickle
            with open(cookies_path, 'rb') as file:
                selenium_cookies = pickle.load(file)
            
            # Convertir les cookies Selenium en format Playwright
            for cookie in selenium_cookies:
                try:
                    self.page.context.add_cookies([{
                        'name': cookie['name'],
                        'value': cookie['value'],
                        'domain': cookie.get('domain', ''),
                        'path': cookie.get('path', '/'),
                        'secure': cookie.get('secure', False),
                        'httpOnly': cookie.get('httpOnly', False)
                    }])
                except Exception as e:
                    SystemLogger.warning(f"Cookie ignoré: {str(e)}")
            
            SystemLogger.info(f"Cookies chargés depuis {cookies_path}")
            return True
            
        except Exception as e:
            SystemLogger.error(f"Erreur chargement cookies: {str(e)}")
            return False
    
    def capture_instagram_profile(self, instagram_url: str, lead_id: int) -> Optional[str]:
        """
        Capture d'écran d'un profil Instagram avec session - format horizontal standard 1920x1080, pas de scroll
        """
        try:
            if not self.page:
                SystemLogger.error("Page non initialisée")
                return None
            SystemLogger.info(f"Capture d'écran Instagram: {instagram_url}")
            # Aller d'abord sur Instagram pour charger les cookies
            self.page.goto('https://www.instagram.com/', wait_until='networkidle', timeout=30000)
            # Charger les cookies Instagram si disponibles
            if self.load_selenium_cookies_to_playwright(self.instagram_cookies_path):
                self.page.reload()
                time.sleep(3)
            # Naviguer vers le profil
            self.page.goto(instagram_url, wait_until='networkidle', timeout=40000)
            time.sleep(5)
            # Attendre la présence de la bio ou du nombre de followers
            try:
                self.page.wait_for_selector('header', timeout=15000)
                self.page.wait_for_selector('img[alt*="photo de profil"], img[alt*="profile photo"], img[alt*="Photo de profil"]', timeout=10000)
            except Exception:
                SystemLogger.warning("Header ou photo de profil Instagram non trouvé, continuation...")
            # Attendre que le contenu soit chargé
            time.sleep(3)
            # Viewport standard horizontal 1920x1080
            self.page.set_viewport_size({'width': 1920, 'height': 1080})
            # Forcer le zoom à 100% (1.0)
            self.page.evaluate("document.body.style.zoom = '1'")
            self.page.evaluate("document.body.style.transform = 'scale(1)'")
            time.sleep(1)
            # Pas de scroll, viewport standard
            filename = f"instagram_lead_{lead_id}_{int(time.time())}.png"
            filepath = self.screenshots_dir / filename
            self.page.screenshot(
                path=str(filepath),
                full_page=False  # Seulement la partie visible
            )
            SystemLogger.info(f"Capture Instagram 1920x1080 zoom 100% réussie: {filepath}")
            return str(filepath)
        except Exception as e:
            SystemLogger.error(f"Erreur capture Instagram {instagram_url}: {str(e)}")
            return None
    
    def capture_instagram_profile_zoom(self, instagram_url: str, lead_id: int) -> Optional[str]:
        """
        Capture d'écran d'un profil Instagram avec session - format optimisé pour centrer le contenu
        """
        try:
            if not self.page:
                SystemLogger.error("Page non initialisée")
                return None
            SystemLogger.info(f"Capture d'écran Instagram optimisée: {instagram_url}")
            # Aller d'abord sur Instagram pour charger les cookies
            self.page.goto('https://www.instagram.com/', wait_until='networkidle', timeout=30000)
            # Charger les cookies Instagram si disponibles
            if self.load_selenium_cookies_to_playwright(self.instagram_cookies_path):
                self.page.reload()
                time.sleep(3)
            # Naviguer vers le profil
            self.page.goto(instagram_url, wait_until='networkidle', timeout=40000)
            time.sleep(5)
            # Attendre la présence de la bio ou du nombre de followers
            try:
                self.page.wait_for_selector('header', timeout=15000)
                self.page.wait_for_selector('img[alt*="photo de profil"], img[alt*="profile photo"], img[alt*="Photo de profil"]', timeout=10000)
            except Exception:
                SystemLogger.warning("Header ou photo de profil Instagram non trouvé, continuation...")
            # Attendre que le contenu soit chargé
            time.sleep(3)
            
            # Viewport optimisé pour Instagram (plus étroit pour centrer le contenu)
            self.page.set_viewport_size({'width': 1200, 'height': 800})
            
            # Forcer le zoom à 100% pour éviter les décalages
            self.page.evaluate("document.body.style.zoom = '1'")
            self.page.evaluate("document.body.style.transform = 'scale(1)'")
            self.page.evaluate("document.body.style.transformOrigin = 'top left'")
            
            # Centrer le contenu en scrollant légèrement si nécessaire
            self.page.evaluate("window.scrollTo(0, 0)")
            time.sleep(1)
            
            # Capturer l'écran
            filename = f"instagram_lead_{lead_id}_{int(time.time())}.png"
            filepath = self.screenshots_dir / filename
            self.page.screenshot(
                path=str(filepath),
                full_page=False  # Seulement la partie visible
            )
            SystemLogger.info(f"Capture Instagram optimisée 1200x800 réussie: {filepath}")
            return str(filepath)
        except Exception as e:
            SystemLogger.error(f"Erreur capture Instagram optimisée {instagram_url}: {str(e)}")
            return None
    
    def capture_facebook_profile(self, facebook_url: str, lead_id: int) -> Optional[str]:
        """
        Capture d'écran d'une page Facebook avec session - format horizontal standard 1920x1080, scroll 400px
        """
        try:
            if not self.page:
                SystemLogger.error("Page non initialisée")
                return None
            SystemLogger.info(f"Capture d'écran Facebook: {facebook_url}")
            # Aller d'abord sur Facebook pour charger les cookies
            self.page.goto('https://www.facebook.com/', wait_until='networkidle', timeout=30000)
            # Charger les cookies Facebook si disponibles
            if self.load_selenium_cookies_to_playwright(self.facebook_cookies_path):
                self.page.reload()
                time.sleep(3)
            # Naviguer vers la page
            self.page.goto(facebook_url, wait_until='networkidle', timeout=40000)
            time.sleep(5)
            # Attendre la présence du nom de la page ou du nombre de likes
            try:
                self.page.wait_for_selector('h1', timeout=15000)
            except Exception:
                SystemLogger.warning("Nom de la page Facebook non trouvé, continuation...")
            # Attendre que le contenu soit chargé
            time.sleep(3)
            # Viewport standard horizontal 1920x1080
            self.page.set_viewport_size({'width': 1920, 'height': 1080})
            # Forcer le zoom à 100% (1.0)
            self.page.evaluate("document.body.style.zoom = '1'")
            self.page.evaluate("document.body.style.transform = 'scale(1)'")
            time.sleep(1)
            # Scroll de 400px vers le bas
            self.page.evaluate("window.scrollTo(0, 400)")
            time.sleep(1)
            # Capturer uniquement le viewport visible
            filename = f"facebook_lead_{lead_id}_{int(time.time())}.png"
            filepath = self.screenshots_dir / filename
            self.page.screenshot(
                path=str(filepath),
                full_page=False
            )
            SystemLogger.info(f"Capture Facebook 1920x1080 scroll 400px zoom 100% réussie: {filepath}")
            return str(filepath)
        except Exception as e:
            SystemLogger.error(f"Erreur capture Facebook {facebook_url}: {str(e)}")
            return None
    
    def capture_facebook_profile_zoom(self, facebook_url: str, lead_id: int) -> Optional[str]:
        """
        Capture d'écran d'une page Facebook avec session - format horizontal zoom +25% (2400x1350), scroll 400px
        """
        try:
            if not self.page:
                SystemLogger.error("Page non initialisée")
                return None
            SystemLogger.info(f"Capture d'écran Facebook zoom +25%: {facebook_url}")
            # Aller d'abord sur Facebook pour charger les cookies
            self.page.goto('https://www.facebook.com/', wait_until='networkidle', timeout=30000)
            # Charger les cookies Facebook si disponibles
            if self.load_selenium_cookies_to_playwright(self.facebook_cookies_path):
                self.page.reload()
                time.sleep(3)
            # Naviguer vers la page
            self.page.goto(facebook_url, wait_until='networkidle', timeout=40000)
            time.sleep(5)
            # Attendre la présence du nom de la page ou du nombre de likes
            try:
                self.page.wait_for_selector('h1', timeout=15000)
            except Exception:
                SystemLogger.warning("Nom de la page Facebook non trouvé, continuation...")
            # Attendre que le contenu soit chargé
            time.sleep(3)
            # Viewport horizontal zoom +25% (2400x1350)
            self.page.set_viewport_size({'width': 2400, 'height': 1350})
            # Appliquer un zoom de 125% via le navigateur
            self.page.evaluate("document.body.style.zoom = '125%'")
            # Alternative avec transform scale
            self.page.evaluate("document.body.style.transform = 'scale(1.25)'")
            self.page.evaluate("document.body.style.transformOrigin = 'top left'")
            time.sleep(2)
            # Scroll de 700px vers le bas
            self.page.evaluate("window.scrollTo(0, 700)")
            time.sleep(1)
            # Capturer uniquement le viewport visible
            filename = f"facebook_lead_{lead_id}_{int(time.time())}.png"
            filepath = self.screenshots_dir / filename
            self.page.screenshot(
                path=str(filepath),
                full_page=False
            )
            SystemLogger.info(f"Capture Facebook 2400x1350 scroll 700px zoom +25% réussie: {filepath}")
            return str(filepath)
        except Exception as e:
            SystemLogger.error(f"Erreur capture Facebook zoom {facebook_url}: {str(e)}")
            return None
    
    def capture_social_media(self, lead_data: Dict[str, Any]) -> Dict[str, Optional[str]]:
        """
        Capture d'écran des réseaux sociaux d'un lead avec zoom +25% et scroll optimisé
        
        Args:
            lead_data: Données du lead avec facebook_url et instagram_url
            
        Returns:
            Dictionnaire avec les chemins des captures d'écran
        """
        result: Dict[str, Optional[str]] = {
            'facebook_screenshot': None,
            'instagram_screenshot': None
        }
        
        try:
            with self as screenshot_service:
                # Capture Facebook avec zoom +25% et scroll 700px
                if lead_data.get('facebook_url'):
                    facebook_url = lead_data['facebook_url']
                    # Validation de l'URL Facebook
                    if self._is_valid_social_media_url(facebook_url, 'facebook'):
                        result['facebook_screenshot'] = screenshot_service.capture_facebook_profile_zoom(
                            facebook_url, 
                            lead_data['id']
                        )
                    else:
                        SystemLogger.warning(f"⚠️ URL Facebook invalide ignorée: {facebook_url}")
                
                # Capture Instagram avec zoom +25%
                if lead_data.get('instagram_url'):
                    instagram_url = lead_data['instagram_url']
                    # Validation de l'URL Instagram
                    if self._is_valid_social_media_url(instagram_url, 'instagram'):
                        result['instagram_screenshot'] = screenshot_service.capture_instagram_profile_zoom(
                            instagram_url, 
                            lead_data['id']
                        )
                    else:
                        SystemLogger.warning(f"⚠️ URL Instagram invalide ignorée: {instagram_url}")
                    
        except Exception as e:
            SystemLogger.error(f"Erreur lors de la capture des réseaux sociaux: {str(e)}")
        
        return result
    
    def _is_valid_social_media_url(self, url: str, platform: str) -> bool:
        """
        Valider une URL de réseau social
        
        Args:
            url: URL à valider
            platform: 'facebook' ou 'instagram'
            
        Returns:
            True si l'URL est valide
        """
        if not url:
            return False
        
        # Vérifier que c'est une URL valide
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            if not parsed.scheme or not parsed.netloc:
                return False
        except:
            return False
        
        # Vérifier que c'est le bon réseau social
        if platform == 'facebook':
            if 'facebook.com' not in url and 'fb.com' not in url:
                return False
        elif platform == 'instagram':
            if 'instagram.com' not in url:
                return False
        
        # Ignorer les fichiers (CSS, JS, images, etc.)
        file_extensions = ['.css', '.js', '.png', '.jpg', '.jpeg', '.gif', '.ico', '.svg', '.woff', '.ttf', '.woff2']
        if any(ext in url.lower() for ext in file_extensions):
            return False
        
        # Ignorer les URLs de plugins ou widgets
        plugin_keywords = ['/wp-content/', '/plugins/', '/widgets/', '/assets/', '/static/']
        if any(keyword in url.lower() for keyword in plugin_keywords):
            return False
        
        return True
    
    def get_screenshot_path(self, lead_id: int, platform: str) -> Optional[str]:
        """
        Récupérer le chemin d'une capture d'écran existante
        
        Args:
            lead_id: ID du lead
            platform: 'facebook' ou 'instagram'
            
        Returns:
            Chemin vers le fichier ou None si non trouvé
        """
        pattern = f"{platform}_lead_{lead_id}_*.png"
        files = list(self.screenshots_dir.glob(pattern))
        
        if files:
            # Retourner le plus récent
            latest_file = max(files, key=lambda f: f.stat().st_mtime)
            return str(latest_file)
        
        return None 