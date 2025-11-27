# 📖 Guide d'Utilisation - Universal Audio Studio

## 🎛️ L'Interface
L'application est divisée en 6 cartes représentant le flux de travail (Workflow) idéal. Il est conseillé de suivre les étapes de 1 à 6, mais chaque module est indépendant.

---

## 1. Import & Analyse
* **Action :** Glissez vos fichiers ou cliquez sur le bouton pour charger des MP3/WAV/FLAC.
* **Analyse BPM :** Cliquez sur la loupe pour détecter le Tempo et la Tonalité (Key).
* **Astuce :** Vous pouvez écouter le fichier original avant traitement.

## 2. Splitter (La Séparation)
C'est le cœur du réacteur. Il découpe votre musique en pistes.

* **Sélecteur de Mode :**
    * **6 Pistes (Complet) :** Idéal pour le remixage pro. Sépare Guitare et Piano.
    * **4 Pistes (Standard) :** Plus robuste. Guitare et Piano sont mélangés dans "Other".
    * **2 Pistes (Karaoké) :** Sépare juste la Voix et l'Instru.
* **Option "Densité (Smart Recovery)" :** * *Activé :* Utilise une technique de soustraction pour remplir les "trous" fréquentiels laissés par l'IA. Le son est plus riche mais peut contenir des résidus.
    * *Désactivé :* Son plus chirurgical, idéal pour le sampling pur.

## 3. Cleaner (Nettoyage)
Supprime le souffle et les artefacts numériques.
* **Option "Mode Hi-Fi" :** * *Activé (Recommandé) :* Nettoyage doux, garde les aigus brillants.
    * *Désactivé :* Nettoyage agressif (coupe au-dessus de 17kHz), utile pour les sources de mauvaise qualité (Suno V2, vieux MP3).

## 4. Vocal Split
Prend les pistes vocales générées et sépare le **Chanteur Principal (Lead)** des **Chœurs (Backing)**.
* *Note :* Indispensable pour pouvoir mixer les chœurs en retrait sur les côtés.

## 5. De-Reverb
Supprime l'écho de la pièce (Room) sur les voix.
* Rend les voix "sèches" (Dry), comme enregistrées en studio cabine, ce qui permet de remettre votre propre réverbération au mixage.

## 6. Mastering
Assemble toutes les pistes générées.
* Applique un panoramique automatique (Basse au centre, Chœurs sur les côtés).
* Normalise le volume final à -1dB.

---

## ⌨️ Raccourcis Clavier (Player)
Lorsque la fenêtre de lecture est ouverte :
* **Espace :** Lecture / Pause.
* **Flèche Gauche :** Reculer de 5 secondes.
* **Flèche Droite :** Avancer de 5 secondes.
