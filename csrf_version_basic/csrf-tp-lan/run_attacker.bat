@echo off
REM ==============================================================================
# SCRIPT POUR LA MACHINE ATTAQUANTE (SERVEUR WEB HEBERGEANT PIEGE.HTML)
REM ==============================================================================
echo ==============================================================================
echo       SERVEUR ATTAQUANT (LAN) - HEBERGEMENT DE PIEGE.HTML
echo ==============================================================================
echo.
echo Demarrage du serveur HTTP sur le port 8081...
echo Les victimes pourront charger http://VOTRE_IP:8081/piege.html
echo.
python -m http.server 8081 --bind 0.0.0.0 --directory attacker

