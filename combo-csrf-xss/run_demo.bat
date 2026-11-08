@echo off
chcp 65001 > nul
title Lab Combo CSRF + XSS : Chaîne d'Exploitation
cls

echo ===============================================================================
echo         LAB TP : CHAÎNE D'ATTAQUE COMBINÉE (CSRF TOKEN BYPASS VIA XSS)
echo ===============================================================================
echo.
echo [1/2] Lancement du serveur Web bancaire sécurisé par CSRF Token (Port 5000)...
start "Application Bancaire (Port 5000)" cmd /k "python app.py"

echo [2/2] Lancement du serveur attaquant HTTP (Port 8081)...
start "Serveur Attaquant (Port 8081)" cmd /k "python -m http.server 8081 --directory attacker"

echo.
echo ===============================================================================
echo Les deux serveurs sont démarrés !
echo.
echo 1. Connectez-vous sur l'application : http://127.0.0.1:5000
echo    Identifiants : user / password123
echo.
echo 2. Testez l'échec de l'attaque CSRF classique (Port 8081) :
echo    Ouvrez : http://127.0.0.1:8081/1_csrf_fail.html
echo    -> Vous verrez une erreur 403 Forbidden (le token anti-CSRF bloque l'attaque).
echo.
echo 3. Contournez la protection avec le XSS Stocké :
echo    Copiez le payload dans 'attacker/2_xss_payload.txt'
echo    et postez-le sur le forum de l'application !
echo.
echo Pour le guide complet, consultez PIPELINE_DEMO.txt ou README.md.
echo ===============================================================================
pause
