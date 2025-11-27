#!/bin/bash
echo "Installation des dépendances..."
if command -v python3.10 &> /dev/null; then PY="python3.10"; else PY="python3"; fi
$PY -m pip install --upgrade pip
$PY -m pip install -r requirements.txt
read -p "Terminé. Appuyez sur Entrée..."
