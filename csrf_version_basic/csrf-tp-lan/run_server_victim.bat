@echo off
REM ==============================================================================
# SCRIPT POUR LA MACHINE VICTIME (SERVEUR DU SITE BANCAIRE / CLIENT)
REM ==============================================================================
setlocal enabledelayedexpansion

set MODE=%1
if "%MODE%"=="" set MODE=vulnerable

if "%MODE%"=="vulnerable" (
    set SCRIPT=vulnerable\app.py
    set TITLE=Site Vulnerable (LAN)
)
if "%MODE%"=="token" (
    set SCRIPT=secure_token\app_secure.py
    set TITLE=Site Protege par Token (LAN)
)
if "%MODE%"=="samesite" (
    set SCRIPT=secure_samesite\app_samesite.py
    set TITLE=Site Protege par SameSite (LAN)
)

echo ==============================================================================
echo       SERVEUR VICTIME (LAN) - SCENARIO : %MODE%
echo ==============================================================================
echo.
echo Demarrage du serveur %TITLE% sur le port 5000...
echo Les autres machines du reseau pourront s'y connecter avec votre IP locale.
echo.
python %SCRIPT%

