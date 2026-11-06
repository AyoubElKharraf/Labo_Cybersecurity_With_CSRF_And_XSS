@echo off
REM Lanceur universel pour le Scénario 1 (GET - Offre de stage)
set MODE=%1
if "%MODE%"=="" set MODE=vulnerable

if "%MODE%"=="vulnerable" (
    set SCRIPT=app.py
    set TITLE=Banque Vulnerable GET
)
if "%MODE%"=="secure" (
    set SCRIPT=app_secure.py
    set TITLE=Banque Securisee
)

echo ==========================================================
echo   SCENARIO 1 : METHODE GET - LANCEMENT : %MODE%
echo ==========================================================

echo [+] Demarrage du Serveur Attaquant (Port 8081)...
start "Attaquant Recrutement (Port 8081)" python -m http.server 8081 --bind 0.0.0.0 --directory attacker

echo [+] Demarrage de la %TITLE% (Port 5000)...
start "Serveur Cible (Port 5000)" python %SCRIPT%

echo.
echo Serveurs actifs ! Fermez les fenetres ouvertes pour arreter.
