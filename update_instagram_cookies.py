import pickle
import time
from playwright.sync_api import sync_playwright

COOKIES_PATH = 'instagram_cookies.pkl'
INSTAGRAM_URL = 'https://www.instagram.com/'

print("[INFO] Lancement du navigateur... (Playwright)")
with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()
    page.goto(INSTAGRAM_URL)
    print("[ACTION] Connecte-toi à Instagram dans la fenêtre ouverte.")
    input("[ACTION] Appuie sur Entrée ici quand tu as fini de te connecter et que la page d'accueil Instagram est bien chargée...")
    cookies = page.context.cookies()
    with open(COOKIES_PATH, 'wb') as f:
        pickle.dump(cookies, f)
    print(f"[OK] Cookies Instagram sauvegardés dans {COOKIES_PATH}")
    browser.close() 