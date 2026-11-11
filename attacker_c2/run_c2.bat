@echo off
chcp 65001 > nul
title Console C2 Attaquant - Port 8082
cls

echo ===============================================================================
echo            CONSOLE C2 COMMAND ^& CONTROL (ATTAQUANT) - PORT 8082
echo ===============================================================================
echo.
echo Démarrage du serveur de surveillance des butins...
echo URL du Dashboard Attaquant : http://127.0.0.1:8082
echo.
python c2_server.py
pause
