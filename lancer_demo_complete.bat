@echo off
chcp 65001 > nul
title Lanceur Global de la Démonstration Cybersécurité
cls

echo ===============================================================================
echo        DEMO CYBERSÉCURITÉ APPLICATIVE : CSRF, XSS ^& CHAÎNE COMBINÉE
echo ===============================================================================
echo.
echo [1/3] Démarrage de la Console C2 Attaquant (Port 8082)...
start "Console C2 Attaquant (Port 8082)" cmd /k "cd attacker_c2 && python c2_server.py"

echo [2/3] Démarrage du Serveur Web Attaquant HTTP (Port 8081)...
start "Serveur Attaquant Web (Port 8081)" cmd /k "python -m http.server 8081 --directory csrf-tp\1_scenario_get_recrutement\attacker"

echo.
echo ===============================================================================
echo   CONSOLE C2 ATTAQUANT PRÊTE : http://127.0.0.1:8082
echo ===============================================================================
echo.
echo Choisissez l'application cible à lancer :
echo.
echo [1] Scénario 1 CSRF (Offre de stage en GET - Port 5000)
echo [2] Scénario 2 CSRF (Catalogue photos et images - Port 5000)
echo [3] Scénario 3 COMBO (Contournement de Token CSRF via XSS - Port 5000)
echo [4] Quitter
echo.
set /p choix="Entrez votre choix (1, 2 ou 3) : "

if "%choix%"=="1" (
    echo Lancement du Scénario 1...
    cd "csrf-tp\1_scenario_get_recrutement"
    python app.py
)

if "%choix%"=="2" (
    echo Lancement du Scénario 2...
    cd "csrf-tp\2_scenario_img_forum"
    python app.py
)

if "%choix%"=="3" (
    echo Lancement du Scénario 3 (Combo CSRF + XSS)...
    cd "combo-csrf-xss"
    python app.py
)

pause
