# 🌐 TP CSRF LAN v2 : Multi-Scénarios & Vecteurs d'Exploitation

Ce dossier **`csrf-tp-lan-2`** regroupe trois déclinaisons d'attaques CSRF réalistes en environnement réseau local, illustrant chacune un vecteur technique différent :

---

## 🎯 Vue d'Ensemble des 3 Nouveaux Scénarios

| # | Scénario | Vecteur Technique | Leurre Réaliste (Ingénierie Sociale) | Impact de l'Attaque |
|---|---|---|---|---|
| **1** | **GET Recrutement** | Requête HTTP `GET` | Fausse offre de stage PFE en cybersécurité (1 650 €/mois) | Virement bancaire frauduleux instantané (500 €) |
| **2** | **POST Facture PDF** | Requête HTTP `POST` absorbée par `<iframe style="display:none;">` | Fausse facture télécom PDF avec visionneuse sécurisée | Détournement d'adresse de facturation 100% invisible |
| **3** | **Image Forum** | Balise HTML `<img src="...">` **(Zéro Clic / Zéro JavaScript)** | Mème / Photo amusante sur un forum étudiant | Micro-débit automatique déclenché par le rendu d'image |

---

## 🚀 Guide de Lancement Rapide

Chaque sous-dossier possède son propre lanceur universel Windows (`run_demo.bat`) :

### 1. Tester le Scénario 1 (GET - Offre de stage)
```cmd
cd "1_scenario_get_recrutement"
.\run_demo.bat vulnerable   # Version vulnérable
.\run_demo.bat secure       # Version protégée par rejet du GET & Token CSRF
```
- **Victime** : `http://IP_VICTIME:5000` (Ayoub / password123)
- **Piège** : `http://IP_ATTAQUANT:8081/stage_recrutement.html?target=IP_VICTIME`

### 2. Tester le Scénario 2 (POST - Facture PDF via iFrame)
```cmd
cd "2_scenario_post_facture_pdf"
.\run_demo.bat vulnerable   # Version vulnérable
.\run_demo.bat secure       # Version protégée par Token CSRF
```
- **Victime** : `http://IP_VICTIME:5000` (Ayoub / password123)
- **Piège** : `http://IP_ATTAQUANT:8081/facture_pdf.html?target=IP_VICTIME`

### 3. Tester le Scénario 3 (Balise `<img>` - Forum / Mème)
```cmd
cd "3_scenario_img_forum"
.\run_demo.bat vulnerable   # Version vulnérable
.\run_demo.bat secure       # Version protégée par obligation du POST + Token
```
- **Victime** : `http://IP_VICTIME:5000` (Ayoub / password123)
- **Piège** : `http://IP_ATTAQUANT:8081/forum_photo.html?target=IP_VICTIME`

Consultez le fichier **`PIPELINE_DEMO.txt`** pour le déroulé oral pas à pas à présenter devant le jury.
