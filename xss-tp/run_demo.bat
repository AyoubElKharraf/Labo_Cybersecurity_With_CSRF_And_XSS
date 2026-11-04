@echo off
REM ==============================================================================
REM LANCEUR UNIVERSEL WINDOWS POUR LE TP XSS
REM Usage : .\run_demo.bat [vulnerable | secure]
REM ==============================================================================
setlocal enabledelayedexpansion

set MODE=%1
if "%MODE%"=="" set MODE=vulnerable

if "%MODE%"=="vulnerable" (
    set SCRIPT=vulnerable\app.py
    set TITLE=Application Vulnerable XSS
)
if "%MODE%"=="secure" (
    set SCRIPT=secure\app_secure.py
    set TITLE=Application Securisee XSS
)

echo ==========================================================
echo        TP XSS - LANCEMENT DU SCENARIO : %MODE%
echo ==========================================================

echo [+] Demarrage du Serveur d'Ecoute Attaquant sur http://127.0.0.1:8888...
start "Attaquant C2 (Port 8888)" python attacker\logger_server.py

echo [+] Demarrage de l'%TITLE% sur http://127.0.0.1:5000...
start "Application Cible (Port 5000)" python %SCRIPT%

echo.
echo ----------------------------------------------------------
echo Serveurs actifs :
echo  - Application Web Cible : http://127.0.0.1:5000
echo  - Serveur C2 Attaquant   : http://127.0.0.1:8888
echo ----------------------------------------------------------
echo Fermez simplement les fenetres ouvertes pour arreter les serveurs.

