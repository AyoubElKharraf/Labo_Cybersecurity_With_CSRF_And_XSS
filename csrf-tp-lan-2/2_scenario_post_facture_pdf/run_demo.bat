@echo off
REM Lanceur universel pour le Scénario 2 (POST - Facture PDF via iFrame)
set MODE=%1
if "%MODE%"=="" set MODE=vulnerable

if "%MODE%"=="vulnerable" (
    set SCRIPT=app.py
    set TITLE=Portail Client Vulnerable POST
)
if "%MODE%"=="secure" (
    set SCRIPT=app_secure.py
    set TITLE=Portail Client Securise
)

echo ==========================================================
echo   SCENARIO 2 : METHODE POST IFRAME - LANCEMENT : %MODE%
echo ==========================================================

echo [+] Demarrage du Serveur Attaquant (Port 8081)...
start "Attaquant Facture (Port 8081)" python -m http.server 8081 --bind 0.0.0.0 --directory attacker

echo [+] Demarrage du %TITLE% (Port 5000)...
start "Serveur Cible (Port 5000)" python %SCRIPT%

echo.
echo Serveurs actifs ! Fermez les fenetres ouvertes pour arreter.
