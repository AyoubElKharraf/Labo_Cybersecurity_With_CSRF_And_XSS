#!/usr/bin/env python3
# ==============================================================================
# TESTS AUTOMATISES POUR LE TP CSRF MULTI-MACHINES (LAN)
# ==============================================================================

import time
import subprocess
import sys
import os
import re
import socket
import unittest
import requests

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

TARGET_HOST = get_local_ip()
TARGET_PORT = 5000
BASE_URL = f"http://{TARGET_HOST}:{TARGET_PORT}"

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

class TestCSRFLanScenarios(unittest.TestCase):

    def start_server(self, script_path):
        proc = subprocess.Popen(
            [sys.executable, script_path],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            cwd=PROJECT_ROOT
        )
        for _ in range(30):
            try:
                r = requests.get(f"{BASE_URL}/login", timeout=0.5)
                if r.status_code == 200:
                    return proc
            except Exception:
                time.sleep(0.1)
        proc.kill()
        raise RuntimeError(f"Le serveur {script_path} n'a pas pu démarrer sur {BASE_URL}")

    def stop_server(self, proc):
        if proc:
            proc.terminate()
            try:
                proc.wait(timeout=2)
            except subprocess.TimeoutExpired:
                proc.kill()

    def test_01_lan_vulnerable_app_receptive(self):
        """Vérifie que la version vulnérable écoute bien sur l'IP LAN et accepte le POST forgé."""
        app_path = os.path.join(PROJECT_ROOT, "vulnerable", "app.py")
        proc = self.start_server(app_path)
        try:
            session = requests.Session()
            login_res = session.post(f"{BASE_URL}/login", data={"username": "Ayoub", "password": "password123"})
            self.assertEqual(login_res.status_code, 200)

            # POST malveillant simulant la requête émise par une autre machine
            csrf_post = session.post(f"{BASE_URL}/update-email", data={"email": "hacker.malveillant@evil.com"})
            self.assertEqual(csrf_post.status_code, 200)

            profil = session.get(f"{BASE_URL}/profil").text
            self.assertIn("hacker.malveillant@evil.com", profil)
            print(f"\n[OK] LAN Vulnérable validé sur {BASE_URL} : L'attaque a réussi !")
        finally:
            self.stop_server(proc)

    def test_02_lan_secure_token_blocks(self):
        """Vérifie que la version Token bloque toute requête forgée (403)."""
        app_path = os.path.join(PROJECT_ROOT, "secure_token", "app_secure.py")
        proc = self.start_server(app_path)
        try:
            session = requests.Session()
            session.post(f"{BASE_URL}/login", data={"username": "Ayoub", "password": "password123"})

            # Sans token
            forged = session.post(f"{BASE_URL}/update-email", data={"email": "hacker.malveillant@evil.com"})
            self.assertEqual(forged.status_code, 403)

            # Avec faux token
            fake = session.post(f"{BASE_URL}/update-email", data={"email": "hacker@evil.com", "csrf_token": "faux_token_123"})
            self.assertEqual(fake.status_code, 403)
            print(f"[OK] LAN Token validé sur {BASE_URL} : Requêtes sans jeton rejetées (403 Forbidden) !")
        finally:
            self.stop_server(proc)

    def test_03_lan_secure_token_legit_works(self):
        """Vérifie que le formulaire avec jeton valide fonctionne normalement (200)."""
        app_path = os.path.join(PROJECT_ROOT, "secure_token", "app_secure.py")
        proc = self.start_server(app_path)
        try:
            session = requests.Session()
            session.post(f"{BASE_URL}/login", data={"username": "Ayoub", "password": "password123"})

            profil = session.get(f"{BASE_URL}/profil").text
            match = re.search(r'name="csrf_token" value="([a-f0-9]+)"', profil)
            self.assertIsNotNone(match)
            token = match.group(1)

            res = session.post(f"{BASE_URL}/update-email", data={"email": "ayoub.nouveau@gmail.com", "csrf_token": token})
            self.assertEqual(res.status_code, 200)
            self.assertIn("ayoub.nouveau@gmail.com", session.get(f"{BASE_URL}/profil").text)
            print(f"[OK] LAN Token Légitime validé : Modification d'email réussie avec token !")
        finally:
            self.stop_server(proc)

    def test_04_lan_samesite_configured(self):
        """Vérifie que SameSite=Strict est configuré et rejette les requêtes non authentifiées (401)."""
        app_path = os.path.join(PROJECT_ROOT, "secure_samesite", "app_samesite.py")
        proc = self.start_server(app_path)
        try:
            res = requests.post(f"{BASE_URL}/login", data={"username": "Ayoub", "password": "password123"}, allow_redirects=False)
            set_cookie = res.headers.get("Set-Cookie", "")
            self.assertIn("SameSite=Strict", set_cookie)
            self.assertIn("HttpOnly", set_cookie)

            # Une requête provenant d'une autre machine sans cookie est bloquée
            unauth = requests.post(f"{BASE_URL}/update-email", data={"email": "hacker@evil.com"})
            self.assertEqual(unauth.status_code, 401)
            print(f"[OK] LAN SameSite validé : En-têtes conformes et requête non authentifiée bloquée (401) !")
        finally:
            self.stop_server(proc)

if __name__ == '__main__':
    unittest.main()

