# 🌐 TP CSRF Multi-Machines (Réseau Local / Wi-Fi)

> **USAGE PÉDAGOGIQUE STRICTEMENT RÉSERVÉ AU RÉSEAU LOCAL PRIVÉ**

Ce projet adapte la démonstration CSRF pour un environnement **réseau réel entre deux machines distinctes** (ex : deux PC portables sur le même Wi-Fi, ou un PC et un smartphone).

---

## 🎯 Architecture Réseau Multi-Machines

```
   ┌───────────────────────────────────┐               ┌───────────────────────────────────┐
   │        MACHINE A (VICTIME)        │               │       MACHINE B (ATTAQUANT)       │
   │      IP Locale : 192.168.1.50     │               │      IP Locale : 192.168.1.80     │
   │                                   │               │                                   │
   │  - Serveur Flask (Port 5000)      │               │  - Serveur Web Malin (Port 8081)  │
   │  - Navigateur Web de la Victime   │               │    hébergeant 'piege.html'        │
   └─────────────────▲─────────────────┘               └─────────────────┬─────────────────┘
                     │                                                   │
                     │       1. La victime visite le piège               │
                     │          http://192.168.1.80:8081/piege.html      │
                     ├───────────────────────────────────────────────────┘
                     │
                     │       2. Le script piège soumet un POST invisible
                     │          vers http://192.168.1.50:5000/update-email
                     ▼
             [ Attaque Réussie ! ]
```

---

## ⚙️ Prérequis Importants pour le Réseau Local

1. **Les deux machines doivent être connectées sur le même réseau Wi-Fi** (ou partage de connexion 4G/5G).
2. **Autoriser Python dans le Pare-feu Windows (Machine A et Machine B)** :
   Lors du premier lancement, Windows affiche une alerte de sécurité. Cochez **"Réseaux privés"** et cliquez sur **Autoriser l'accès**.

---

## 🚀 Déroulement de la Démonstration Pas-à-Pas

### Étape 1 : Obtenir les adresses IP locales
- **Sur la Machine A (Victime)** : Ouvrez un terminal et tapez `ipconfig`. Repérez votre *Adresse IPv4* (ex: `192.168.1.50`).
- **Sur la Machine B (Attaquant)** : De même, repérez son adresse IPv4 (ex: `192.168.1.80`).

---

### Étape 2 : Lancer le Serveur Cible (Sur la Machine A)
Dans le dossier `csrf-tp-lan` :
```cmd
.\run_server_victim.bat vulnerable
```
Le terminal affiche l'IP et le port d'écoute :
```text
[✓] Serveur Cible LAN démarré sur : http://192.168.1.50:5000
```

---

### Étape 3 : Lancer le Serveur Piège (Sur la Machine B)
Dans le dossier `csrf-tp-lan` de la machine attaquante :
```cmd
.\run_attacker.bat
```
Le serveur écoute sur le port 8081 :
```text
Serving HTTP on 0.0.0.0 port 8081 ...
```

---

### Étape 4 : Dérouler l'Attaque en direct

1. **La victime se connecte sur son propre PC (Machine A)** :  
   Ouvrez le navigateur sur `http://192.168.1.50:5000` (ou `http://localhost:5000`).  
   Identifiants : `Ayoub` / `password123`.  
   L'email enregistré est `ayoub.legitime@gmail.com`.

2. **L'attaquant envoie le lien à la victime (par Teams, WhatsApp ou mail)** :  
   Le lien est :  
   `http://192.168.1.80:8081/piege.html?target=192.168.1.50`  
   *(Remplacer `192.168.1.50` par l'IP réelle de la victime)*.

3. **La victime clique sur le lien depuis son navigateur (Machine A)** :  
   - La page piège s'ouvre.
   - En coulisses, elle soumet un formulaire POST vers `http://192.168.1.50:5000/update-email`.
   - Le navigateur de la victime attache automatiquement son cookie de session.

4. **Résultat immédiat** :  
   L'email a été piraté en `hacker.malveillant@evil.com` depuis une machine distante !

---

## 🛡️ Démontrer les Défenses en Réseau Local

### 1. Défense par Token CSRF
Sur la Machine A, relancez avec :
```cmd
.\run_server_victim.bat token
```
- Reconnectez la victime.
- Quand elle recharge le piège depuis la Machine B : **HTTP 403 Forbidden** !

### 2. Défense par `SameSite=Strict`
Sur la Machine A, relancez avec :
```cmd
.\run_server_victim.bat samesite
```
- Reconnectez la victime.
- Quand elle recharge le piège depuis la Machine B : **HTTP 401 Unauthorized** !  
  *Ici, comme les deux machines ont des IP différentes (`192.168.1.80` vs `192.168.1.50`), c'est un véritable contexte Cross-Site universel : le navigateur refuse d'envoyer le cookie sans aucune ambiguïté de port !*

