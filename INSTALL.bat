@echo off
title Installation du Studio Audio
echo ==========================================
echo INSTALLATION DES DEPENDANCES
echo ==========================================
echo Verification de Python...
py -3.10 --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERREUR : Python 3.10 n'est pas detecte !
    echo Veuillez l'installer et cocher "Add to PATH".
    pause
    exit
)
echo Installation des librairies...
py -3.10 -m pip install -r requirements.txt
echo.
echo ==========================================
echo INSTALLATION TERMINEE !
echo ==========================================
pause
