# 🛡️ Projet Pédagogique : Sécurité Web Applicative (OWASP)
## Démonstrations Pratiques & Contre-Mesures : CSRF & XSS

**Projet :** Laboratoire Pratique de Cybersécurité Web  
**Environnement :** Python 3.10+, Flask, Vanilla JavaScript, Unittest  

---

> [!IMPORTANT]
> **Avertissement Éthique & Légal**  
> L'ensemble du code source, des scripts d'exploitation et des démonstrations contenus dans cet espace de travail a été conçu à des **fins strictement pédagogiques et éducatives**. Les tests s'effectuent exclusivement en local (`127.0.0.1` / `localhost`) ou sur un réseau local privé autorisé (`LAN`). Tout usage malveillant sur des systèmes tiers sans consentement écrit préalable est formellement illégal (Articles 323-1 et suivants du Code Pénal).

---

## 1. Vue d'Ensemble du Projet

Ce projet constitue une plateforme complète d'apprentissage et de démonstration technique sur les vulnérabilités majeures du **Top 10 OWASP** :
1. **La falsification de requête intersites (CSRF - *Cross-Site Request Forgery*)** :
   - Démonstration de scénarios métiers réalistes : méthode `GET` (fausse offre de recrutement) et balises médias `<img>` (catalogue photos interactif).
   - Archives des versions fondamentales mono-machine et réseau local multi-machines.
2. **L'injection de code indirecte (XSS - *Cross-Site Scripting*)** :
   - XSS Réfléchi (*Reflected XSS*) via des paramètres de recherche HTTP `GET`.
   - XSS Stocké (*Stored XSS*) persistant en base/mémoire via un livre d'or.
   - Exfiltration en direct de cookies de session vers un serveur pirate d'écoute C2 (*Command & Control* sur le port `8888`).
3. **L'interaction critique CSRF ↔ XSS** :
   - Démonstration de la rupture du jeton anti-CSRF en présence d'une faille XSS.
   - Application concrète du principe de **Défense en Profondeur**.

Tous les modules respectent des standards professionnels : **zéro dépendance externe lourde** (stockage transparent en mémoire vive), **reproductibilité garantie**, **scripts universels Windows (`run_demo.bat`)**, et **suites de tests unitaires automatisées (100% de réussite)**.

---

## 2. Cartographie Réelle de l'Espace de Travail

Le projet est organisé de manière claire et modulaire selon l'arborescence suivante :

```text
Exposé - CSRF & XSS/
│
├── 📁 csrf_version_basic/          # ARCHIVES DES VERSIONS FONDAMENTALES CSRF
│   ├── 📁 csrf-tp/                 # Version de base mono-machine (Changement d'email)
│   └── 📁 csrf-tp-lan/             # Version de base distribuée réseau local (LAN)
│
├── 📁 csrf-tp/                     # PROJET CSRF PRINCIPAL (SCÉNARIOS MÉTIERS POUR LE COURS)
│   ├── 📁 1_scenario_get_recrutement/
│   │   ├── app.py                  # Banque vulnérable avec virement en GET (Port 5000)
│   │   ├── app_secure.py           # Version sécurisée (Interdiction du GET + Token CSRF)
│   │   ├── attacker/stage_recrutement.html # Fausse offre de stage PFE NexaSec (1 650 €/mois)
│   │   └── run_demo.bat            # Lanceur rapide du Scénario 1
│   │
│   ├── 📁 2_scenario_img_forum/
│   │   ├── app.py                  # Portefeuille solidaire vulnérable aux débits (Port 5000)
│   │   ├── app_secure.py           # Version sécurisée (POST obligatoire + Jeton CSRF)
│   │   ├── attacker/forum_photo.html # Galerie PhotoSphere (Clic sur n'importe quelle photo ou recherche)
│   │   └── run_demo.bat            # Lanceur rapide du Scénario 2
│   │
│   ├── PIPELINE_DEMO.txt           # Guide pas à pas pour la démonstration orale
│   ├── README.md                   # Documentation technique des scénarios CSRF
│   └── requirements.txt            # Dépendances (Flask, requests)
│
├── 📁 xss-tp/                      # PROJET XSS COMPLET & VOL DE SESSION C2
│   ├── 📁 attacker/
│   │   └── logger_server.py        # Serveur d'écoute C2 d'exfiltration de cookies (Port 8888)
│   ├── 📁 vulnerable/
│   │   └── app.py                  # Application vulnérable (Recherche Réfléchie + Livre d'or Stocké)
│   ├── 📁 secure/
│   │   └── app_secure.py           # Version protégée (Échappement HTML + Cookie HttpOnly + CSP)
│   ├── 📁 tests/
│   │   └── test_xss.py             # Suite de tests d'injection XSS (5/5 tests validés)
│   ├── PIPELINE_DEMO.txt           # Payloads et déroulé pas à pas pour l'exposé
│   ├── README.md                   # Guide complet sur les failles XSS et la CSP
│   ├── requirements.txt            # Dépendances (Flask, requests)
│   └── run_demo.bat                # Lanceur universel Windows (vulnerable | secure)
│
├── 📁 combo-csrf-xss/              # DÉMONSTRATION AVANCÉE : BYPASS DE CSRF TOKEN VIA XSS
│   ├── app.py                      # Banque protégée par CSRF Token + Forum avec XSS Stocké
│   ├── run_demo.bat                # Lanceur unifié (App port 5000 + Attaquant port 8081)
│   ├── PIPELINE_DEMO.txt           # Scénario détaillé pour réussir la démo combinée
│   ├── README.md                   # Explications de la chaîne d'exploitation et SOP
│   └── 📁 attacker/
│       ├── 1_csrf_fail.html        # Tentative CSRF directe (bloquée par le jeton CSRF, HTTP 403)
│       └── 2_xss_payload.txt       # Payload XSS : vole le jeton dans le DOM et exécute le virement
│
├── 📁 attacker_c2/                 # CONSOLE C2 DE L'ATTAQUANT (SURVEILLANCE DES BUTINS)
│   ├── c2_server.py                # Serveur C2 écoutant sur le port 8082
│   └── run_c2.bat                  # Lanceur de la console C2
│
├── lancer_demo_complete.bat        # LANCEUR GLOBAL EN 1 CLIC (C2 + HTTP + Choix de Scénario)
└── README.md                       # Synthèse globale et guide d'orientation de l'exposé
```

---

## 3. Synthèse Technique Approfondie des Vulnérabilités

### A. L'Attaque CSRF (Cross-Site Request Forgery)
* **Mécanisme fondamental** : Le navigateur attache **automatiquement** les cookies de session enregistrés à toute requête HTTP sortante dirigée vers le domaine cible, peu importe l'origine à l'initiative de la requête.
* **Le rôle de la SOP (Same-Origin Policy)** : La SOP est une politique de **lecture** et non d'écriture. Un script tiers ne peut pas lire la réponse bancaire, mais le navigateur l'autorise à envoyer un formulaire ou une requête `GET` modifiant les données côté serveur.
* **Les Scénarios Métiers du TP CSRF (`csrf-tp`)** :
  1. **Scénario 1 (`1_scenario_get_recrutement`)** : Virement bancaire frauduleux immédiat de 500 € déclenché via la méthode `GET` au clic sur une offre de stage attractive ou automatiquement.
  2. **Scénario 2 (`2_scenario_img_forum`)** : Débit automatique de 200 € déclenché au clic sur n'importe quelle photo d'une galerie de catalogue (PhotoSphere) ou via des balises `<img src="...">` **sans aucun JavaScript requis**.
* **Contre-mesures** : Interdiction formelle des mutations en `GET`, implémentation du **Synchronizer Token Pattern** et cookies **`SameSite=Strict`**.

### B. L'Attaque XSS (Cross-Site Scripting)
* **Mécanisme fondamental** : L'attaquant injecte du code JavaScript malveillant dans l'application cible. Ce code est interprété par le navigateur de la victime au sein du **contexte d'origine légitime** du site.
* **Variantes démontrées (`xss-tp`)** :
  - **XSS Réfléchi (*Reflected*)** : Injection dans la barre de recherche (`/search?q=<script>...`) exécutée immédiatement chez la victime.
  - **XSS Stocké (*Stored / Persistant*)** : Injection persistante dans le livre d'or (`/guestbook`), infectant tout utilisateur consultant la page.
* **Vol de session en temps réel** : Exfiltration de `document.cookie` vers le serveur pirate C2 (`http://127.0.0.1:8888`) capturant le secret de session en direct.
* **Contre-mesures** : Échappement HTML contextuel (Jinja2), drapeau **`HttpOnly=True`** (qui rend le cookie invisible en JS), et en-tête **`Content-Security-Policy: default-src 'self'`**.

---

## 4. Matrice Comparative : CSRF vs XSS

| Critère d'Analyse | CSRF (*Cross-Site Request Forgery*) | XSS (*Cross-Site Scripting*) |
| :--- | :--- | :--- |
| **Origine de la vulnérabilité** | Confiance aveugle du serveur dans le navigateur de la victime. | Confiance aveugle du navigateur dans les données renvoyées par le serveur. |
| **Lieu d'exécution** | **Sur le serveur cible** (qui traite l'ordre transmis par le navigateur). | **Dans le navigateur client** (qui interprète le JavaScript injecté). |
| **Capacité de lecture des données** | **Aucune** (La SOP bloque la lecture de la réponse par le site attaquant). | **Totale** (Le script tourne dans l'origine et le DOM de la cible). |
| **Besoins de l'attaquant** | Une victime connectée + un prétexte de clic / visite (Phishing). | Un champ de saisie non assaini ou une URL réfléchie non échappée. |
| **Conséquences types** | Virement bancaire, changement d'email, modification d'adresse. | Vol de session, défiguration de site, keylogger, bypass de token CSRF. |
| **Contre-mesures de référence** | **Jeton anti-CSRF** + Cookie `SameSite=Strict/Lax`. | **Échappement HTML** + Cookie `HttpOnly` + En-tête **CSP**. |

> [!CAUTION]
> **Le Lien Fatal entre XSS et CSRF (Défense en Profondeur) :**  
> Une protection anti-CSRF par jeton devient **totalement inefficace** si le site présente une vulnérabilité XSS. Le script malveillant injecté sur le domaine légitime a le droit de lire le DOM, de subtiliser le jeton CSRF et de soumettre la requête en toute légitimité. Sécuriser contre le CSRF impose donc d'éradiquer au préalable tout risque XSS.

---

## 5. Guide d'Exécution Rapide (Pour la Soutenance en Cours)

### A. Démonstration CSRF Métier (`csrf-tp`)

#### 1. Scénario 1 : Méthode GET (Offre de stage PFE NexaSec)
```cmd
cd "csrf-tp\1_scenario_get_recrutement"
.\run_demo.bat vulnerable   # Version vulnérable
# Victime : http://localhost:5000 (identifiants : user / password123)
# Piège   : http://localhost:8081/stage_recrutement.html
.\run_demo.bat secure       # Défense : Interdiction du GET + Token CSRF
```

#### 2. Scénario 2 : Images & Médias (Galerie Pinterest PhotoSphere)
```cmd
cd "..\2_scenario_img_forum"
.\run_demo.bat vulnerable   # Version vulnérable (Débit au clic sur n'importe quelle photo)
# Victime : http://localhost:5000 (identifiants : user / password123)
# Piège   : http://localhost:8081/forum_photo.html
.\run_demo.bat secure       # Défense : POST obligatoire + Jeton CSRF
```

---

### B. Démonstration XSS & Vol de Session C2 (`xss-tp`)
```cmd
cd "..\xss-tp"

# Lancer la version vulnérable (Serveur Cible 5000 + Serveur C2 Pirate 8888) :
.\run_demo.bat vulnerable
# 1. Tester le XSS Réfléchi sur http://127.0.0.1:5000/search
# 2. Tester le XSS Stocké et le vol de session sur http://127.0.0.1:5000/guestbook

# Démontrer les défenses (Échappement, HttpOnly, Content-Security-Policy) :
.\run_demo.bat secure

# Valider la suite de tests automatisés (5/5 tests validés) :
python tests/test_xss.py
```

---

### C. Démonstration Avancée : Chaîne d'Exploitation Combo CSRF + XSS (`combo-csrf-xss`)
```cmd
cd "..\combo-csrf-xss"

# Démarrer le lab combiné (Serveur bancaire 5000 + Serveur pirate 8081) :
.\run_demo.bat

# Étape 1 : Connexion sur http://127.0.0.1:5000 (user / password123)
# Étape 2 : Test de l'échec CSRF pur sur http://127.0.0.1:8081/1_csrf_fail.html -> 403 Forbidden
# Étape 3 : Injection du script XSS dans le forum depuis attacker/2_xss_payload.txt
# Résultat : Le script vole le jeton anti-CSRF dans le DOM et exécute le virement de 850 € avec succès !
```

---

## 6. Références Officielles & Bibliographie

* **OWASP Top 10:2021** :
  - *A01:2021 – Broken Access Control* (Catégorie couvrant le CSRF).
  - *A03:2021 – Injection* (Catégorie couvrant le XSS).
* **RFC 6265bis** : *Cookies: HTTP State Management Mechanism* (Spécification officielle des attributs `SameSite=Strict/Lax/None` et `HttpOnly`).
* **RFC 7231** : *Hypertext Transfer Protocol (HTTP/1.1): Semantics and Content* (Principe d'idempotence et d'innocuité des méthodes HTTP `GET`).
* **W3C Content Security Policy Level 3** : Recommandations pour la restriction des contextes d'exécution de scripts côté client.
