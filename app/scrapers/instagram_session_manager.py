"""
Gestionnaire de sessions Instagram pour sauvegarder et charger les cookies
"""

import os
import pickle
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from app.utils.logger import SystemLogger

class InstagramSessionManager:
    """Gestionnaire de sessions Instagram"""
    
    def __init__(self):
        self.cookies_path = 'instagram_cookies.pkl'
    
    def save_cookies(self, driver, path):
        """Sauvegarder les cookies du navigateur"""
        try:
            with open(path, 'wb') as file:
                pickle.dump(driver.get_cookies(), file)
            SystemLogger.info(f"Cookies Instagram sauvegardés dans {path}")
        except Exception as e:
            SystemLogger.error(f"Erreur sauvegarde cookies Instagram: {str(e)}")
    
    def load_cookies(self, driver, path):
        """Charger les cookies dans le navigateur"""
        try:
            if os.path.exists(path):
                with open(path, 'rb') as file:
                    cookies = pickle.load(file)
                    for cookie in cookies:
                        try:
                            driver.add_cookie(cookie)
                        except Exception as e:
                            SystemLogger.warning(f"Cookie ignoré: {str(e)}")
                SystemLogger.info(f"Cookies Instagram chargés depuis {path}")
                return True
            else:
                SystemLogger.warning(f"Fichier de cookies Instagram non trouvé: {path}")
                return False
        except Exception as e:
            SystemLogger.error(f"Erreur chargement cookies Instagram: {str(e)}")
            return False
    
    def login_instagram(self, cookies_path='instagram_cookies.pkl'):
        """
        Ouvre un navigateur pour login manuel Instagram. 
        Quand tu es connectée, appuie sur Entrée dans le terminal pour sauvegarder la session.
        """
        try:
            chrome_options = Options()
            # Mode non-headless pour login manuel
            driver = webdriver.Chrome(options=chrome_options)
            driver.get('https://www.instagram.com/accounts/login/')
            
            print('🔐 Connexion Instagram manuelle')
            print('1. Connectez-vous à Instagram dans le navigateur qui s\'ouvre')
            print('2. Une fois connecté, revenez ici et appuyez sur Entrée')
            input('Appuyez sur Entrée pour sauvegarder les cookies Instagram...')
            
            # Vérifier que l'utilisateur est bien connecté
            if 'login' in driver.current_url:
                print('❌ Vous n\'êtes pas encore connecté à Instagram')
                driver.quit()
                return False
            
            self.save_cookies(driver, cookies_path)
            driver.quit()
            print('✅ Cookies Instagram sauvegardés avec succès!')
            return True
            
        except Exception as e:
            SystemLogger.error(f"Erreur lors de la connexion Instagram: {str(e)}")
            print(f'❌ Erreur: {str(e)}')
            return False
    
    def check_session_valid(self, cookies_path='instagram_cookies.pkl'):
        """Vérifier si la session Instagram est encore valide"""
        try:
            if not os.path.exists(cookies_path):
                return False
            
            chrome_options = Options()
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            
            driver = webdriver.Chrome(options=chrome_options)
            driver.get('https://www.instagram.com/')
            
            if self.load_cookies(driver, cookies_path):
                driver.refresh()
                time.sleep(3)
                
                # Vérifier si on est connecté
                if 'login' not in driver.current_url and 'accounts/login' not in driver.current_url:
                    driver.quit()
                    return True
                else:
                    driver.quit()
                    return False
            else:
                driver.quit()
                return False
                
        except Exception as e:
            SystemLogger.error(f"Erreur vérification session Instagram: {str(e)}")
            return False
    
    def get_session_info(self, cookies_path='instagram_cookies.pkl'):
        """Obtenir des informations sur la session"""
        try:
            if not os.path.exists(cookies_path):
                return {
                    'exists': False,
                    'valid': False,
                    'message': 'Aucun fichier de cookies trouvé'
                }
            
            with open(cookies_path, 'rb') as file:
                cookies = pickle.load(file)
            
            session_cookie = next((c for c in cookies if c['name'] == 'sessionid'), None)
            
            return {
                'exists': True,
                'valid': self.check_session_valid(cookies_path),
                'cookies_count': len(cookies),
                'has_sessionid': session_cookie is not None,
                'message': f"Session avec {len(cookies)} cookies"
            }
            
        except Exception as e:
            return {
                'exists': False,
                'valid': False,
                'message': f'Erreur: {str(e)}'
            } 