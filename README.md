# 🛡️ Projet Académique : Sécurité Web Applicative (OWASP)
## Démonstrations Pratiques & Contre-Mesures : CSRF & XSS

**Auteur :** Ayoub  
**Formation :** Master 2 Ingénierie Informatique (M2I) - Semestre 3  
**Module :** Cybersécurité Applicative & Certification CEH (*Certified Ethical Hacker*)  
**Environnement :** Python 3.10+, Flask, Vanilla JavaScript, Pytest/Unittest  

---

> [!IMPORTANT]
> **Avertissement Éthique & Légal**  
> L'ensemble du code source, des scripts d'exploitation et des démonstrations contenus dans cet espace de travail a été conçu à des **fins strictement pédagogiques et éducatives**. Les tests s'effectuent exclusivement en local (`127.0.0.1` / `localhost`) ou sur un réseau local privé autorisé (`LAN`). Tout usage malveillant sur des systèmes tiers sans consentement écrit est formellement illégal (Articles 323-1 et suivants du Code Pénal).

---

## 1. Vue d'Ensemble du Projet

Ce projet constitue une plateforme complète d'apprentissage et de démonstration technique sur les vulnérabilités majeures du **Top 10 OWASP**, en se concentrant sur :
1. **La falsification de requête intersites (CSRF - *Cross-Site Request Forgery*)** : étude en environnement mono-machine et en environnement distribué multi-machines (LAN).
2. **L'injection de code indirecte (XSS - *Cross-Site Scripting*)** : étude des variantes réfléchie et stockée avec exfiltration de session en temps réel.
3. **L'interaction critique CSRF ↔ XSS** : démonstration de la destruction des jetons anti-CSRF par le XSS et application du principe de **Défense en Profondeur**.

Tous les modules ont été développés selon des standards industriels : **zéro dépendance lourde** (stockage mémoire transparent), **reproductibilité garantie**, **scripts d'automatisation Windows / Linux**, et **suites de tests unitaires automatisées validées**.

---

## 2. Cartographie de l'Espace de Travail

Le répertoire racine regroupe trois sous-projets indépendants et complémentaires :

```text
Exposé - CSRF Attack/
│
├── 📁 csrf-tp/              # TP 1 : CSRF en environnement local (Mono-machine)
│   ├── vulnerable/          # Application cible sans protection (Port 5000)
│   ├── secure_token/        # Défense par Synchronizer Token Pattern (Port 5000)
│   ├── secure_samesite/     # Défense par cookie SameSite=Strict & HttpOnly (Port 5000)
│   ├── attacker/            # Page piège auto-soumise piege.html (Port 8081)
│   ├── tests/               # Validation automatisée (unittest + requests)
│   ├── run_demo.bat         # Lanceur rapide Windows (vulnerable | token | samesite)
│   ├── PIPELINE_DEMO.txt    # Déroulé pas à pas pour l'exposé oral
│   └── README.md            # Guide théorique et technique complet
│
├── 📁 csrf-tp-lan/          # TP 2 : CSRF distribué en Réseau Local (Multi-machines)
│   ├── vulnerable/          # Serveur Flask écoutant sur 0.0.0.0 (Port 5000)
│   ├── secure_token/        # Défense par Token sur IP LAN
│   ├── secure_samesite/     # Défense SameSite sur IP LAN (contexte Cross-Site natif)
│   ├── attacker/            # Piège avec configuration dynamique de l'IP cible
│   ├── tests/               # Tests automatisés sur l'interface réseau locale
│   ├── run_server_victim.bat# Lanceur pour la Machine Victime
│   ├── run_attacker.bat     # Lanceur pour la Machine Attaquante
│   └── README.md            # Guide d'interconnexion réseau Wi-Fi / LAN
│
└── 📁 xss-tp/               # TP 3 : Failles XSS & Exfiltration de Session C2
    ├── vulnerable/          # Vulnérabilités Reflected (/search) & Stored (/guestbook)
    ├── secure/              # Défenses : Échappement HTML + HttpOnly + Header CSP
    ├── attacker/            # Serveur C2 d'écoute d'exfiltration de cookies (Port 8888)
    ├── tests/               # Tests automatisés de non-régression XSS
    ├── run_demo.bat         # Lanceur universel (vulnerable | secure)
    ├── PIPELINE_DEMO.txt    # Fiche mémo des payloads à injecter
    └── README.md            # Guide complet sur les mécanismes XSS & CSP
```

---

## 3. Synthèse des Modules et Notions Clés

### Module 1 : `csrf-tp` (Attaque CSRF Locale)
- **Le problème historique** : Le navigateur attache aveuglément les cookies de session à toute requête sortante vers un domaine donné, même initiée depuis un site tiers malveillant.
- **La SOP (Same-Origin Policy)** : Elle interdit la lecture de la réponse HTTP par le script tiers, mais **n'interdit pas l'écriture** (envoi du formulaire POST).
- **Les deux contre-mesures implémentées** :
  1. **Synchronizer Token Pattern** : Jeton cryptographique imprévisible (`secrets.token_hex(32)`) associé à la session et vérifié en temps constant (`secrets.compare_digest`).
  2. **Cookie `SameSite=Strict`** : Le navigateur refuse de transmettre le cookie lors d'une navigation intersites. *(Démonstration de la nuance technique entre `127.0.0.1` et `localhost`)*.

### Module 2 : `csrf-tp-lan` (Attaque CSRF Multi-Machines)
- **Objectif** : Valider l'attaque sur un réseau physique réel entre deux équipements distincts (PC Victime `10.5.100.x` et PC Attaquant).
- **Apport pédagogique** : Suppression de l'ambiguïté des ports locaux sur une même adresse IP. La séparation des adresses IP offre une démonstration grandeur nature de la frontière *Cross-Site*.

### Module 3 : `xss-tp` (Cross-Site Scripting & Vol de Session)
- **XSS Réfléchi (Reflected)** : Injection dans un paramètre d'URL non assaini, exécutée immédiatement chez la victime via un lien piégé.
- **XSS Stocké (Stored)** : Injection persistante dans le livre d'or, infectant tout utilisateur consultant la page.
- **Serveur C2 Pirate (Port 8888)** : Démonstration concrète du vol de `document.cookie` via `fetch()`.
- **Défenses appliquées** : Échappement automatique (Contextual HTML Encoding), drapeau de sécurité **`HttpOnly`** (masquage de `document.cookie`), et en-tête **`Content-Security-Policy: default-src 'self'`**.

---

## 4. Matrice Comparative des Vulnérabilités & Défenses

| Critère | CSRF (Cross-Site Request Forgery) | XSS (Cross-Site Scripting) |
| :--- | :--- | :--- |
| **Origine de la faille** | Confiance aveugle du serveur dans le navigateur de l'utilisateur. | Confiance aveugle du navigateur dans le code renvoyé par le serveur. |
| **Lieu d'exécution** | Serveur cible (qui traite une requête légitime en apparence). | Navigateur client (qui exécute du JavaScript injecté). |
| **Capacité de lecture** | **Nulle** (La SOP bloque la lecture de la réponse par le pirate). | **Totale** (Le script tourne dans l'origine du site cible). |
| **Impact principal** | Action non consentie (virement, changement d'email/mot de passe). | Vol de session, défiguration, keylogging, bypass de CSRF. |
| **Défense de référence** | **Token anti-CSRF** + Cookie `SameSite=Strict/Lax`. | **Échappement contextuel** + Cookie `HttpOnly` + **CSP**. |

> [!TIP]
> **Le lien fatal entre XSS et CSRF :**  
> Une protection anti-CSRF (même par token) devient **caduque** si le site présente une vulnérabilité XSS. Le script malveillant injecté sur le domaine légitime a le droit de lire le DOM, de subtiliser le jeton CSRF et de forger la requête en contournant la défense. D'où la nécessité absolue de la **défense en profondeur**.

---

## 5. Guide d'Exécution Rapide (Cheat Sheet)

### A. Exécuter le TP CSRF (Mono-machine)
```powershell
cd "csrf-tp"
# Lancer la version vulnérable :
.\run_demo.bat vulnerable
# Lancer la version sécurisée par Token :
.\run_demo.bat token
# Lancer la version sécurisée par SameSite :
.\run_demo.bat samesite
# Exécuter la suite de tests :
python tests/test_csrf.py
```

### B. Exécuter le TP CSRF (Multi-machines / LAN)
```powershell
cd "csrf-tp-lan"
# Sur la machine victime :
.\run_server_victim.bat vulnerable
# Sur la machine attaquante :
.\run_attacker.bat
# Exécuter la suite de tests LAN :
python tests/test_lan_csrf.py
```

### C. Exécuter le TP XSS & Vol de Session
```powershell
cd "xss-tp"
# Lancer la version vulnérable (Serveur Web 5000 + C2 Pirate 8888) :
.\run_demo.bat vulnerable
# Lancer la version sécurisée (Échappement + HttpOnly + CSP) :
.\run_demo.bat secure
# Exécuter la suite de tests XSS :
python tests/test_xss.py
```

---

## 6. Validation Industrielle et Qualité Logicielle

Chaque module intègre sa propre suite de tests automatisés validant les scénarios d'attaque et de remédiation :

```text
[SUITE DE TESTS 1 : csrf-tp/tests/test_csrf.py]
  - test_01_vulnerable_app_csrf_succeeds          -> [OK] (Email altéré)
  - test_02_secure_token_blocks_forged_request    -> [OK] (Rejet 403 Forbidden)
  - test_03_secure_token_legitimate_succeeds      -> [OK] (Validation 200 OK)
  - test_04_secure_samesite_attribute_configured  -> [OK] (En-têtes & Rejet 401)
  Résultat : 4/4 PASSÉ (100%)

[SUITE DE TESTS 2 : csrf-tp-lan/tests/test_lan_csrf.py]
  - test_01_lan_vulnerable_app_receptive         -> [OK] (Validation sur IP 10.5.100.x)
  - test_02_lan_secure_token_blocks              -> [OK] (Rejet 403)
  - test_03_lan_secure_token_legit_works         -> [OK] (Validation 200)
  - test_04_lan_samesite_configured             -> [OK] (Rejet 401)
  Résultat : 4/4 PASSÉ (100%)

[SUITE DE TESTS 3 : xss-tp/tests/test_xss.py]
  - test_01_reflected_xss_is_injected_raw         -> [OK] (Balise <script> non échappée)
  - test_02_stored_xss_persists_in_guestbook     -> [OK] (Persistance du payload)
  - test_03_vulnerable_cookie_missing_httponly   -> [OK] (Flag HttpOnly absent)
  - test_04_secure_app_escapes_xss_payloads      -> [OK] (Encodage entités HTML)
  - test_05_secure_app_enforces_httponly_and_csp -> [OK] (HttpOnly + CSP actifs)
  Résultat : 5/5 PASSÉ (100%)
```

---

## 7. Références & Normes de Cybersécurité

- **OWASP Top 10** : A01:2021-Broken Access Control & A03:2021-Injection
- **RFC 6265bis** : Cookies: HTTP State Management Mechanism (SameSite Attribute)
- **RFC 7231** : Hypertext Transfer Protocol (HTTP/1.1): Semantics and Content (Idempotence des requêtes GET)
- **W3C Content Security Policy Level 3** : Recommandations officielles pour la restriction des contextes d'exécution de scripts.

