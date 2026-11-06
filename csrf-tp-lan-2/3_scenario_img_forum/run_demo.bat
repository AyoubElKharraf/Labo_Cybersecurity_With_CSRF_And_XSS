@echo off
REM Lanceur universel pour le Scénario 3 (Balise <img> / Forum)
set MODE=%1
if "%MODE%"=="" set MODE=vulnerable

if "%MODE%"=="vulnerable" (
    set SCRIPT=app.py
    set TITLE=Portefeuille Solidaire Vulnerable IMG
)
if "%MODE%"=="secure" (
    set SCRIPT=app_secure.py
    set TITLE=Portefeuille Securise
)

echo ==========================================================
echo   SCENARIO 3 : BALISE IMAGE - LANCEMENT : %MODE%
echo ==========================================================

echo [+] Demarrage du Serveur Attaquant Forum (Port 8081)...
start "Attaquant Forum (Port 8081)" python -m http.server 8081 --bind 0.0.0.0 --directory attacker

echo [+] Demarrage du %TITLE% (Port 5000)...
start "Serveur Cible (Port 5000)" python %SCRIPT%

echo.
echo Serveurs actifs ! Fermez les fenetres ouvertes pour arreter.
