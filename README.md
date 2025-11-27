# 🎛️ Universal Audio Studio

![Version](https://img.shields.io/badge/version-1.0.49-blue) ![Python](https://img.shields.io/badge/Python-3.10-yellow) ![Status](https://img.shields.io/badge/Status-Stable-green)

**Universal Audio Studio** est une station de travail audio (DAW) autonome alimentée par l'IA. Elle permet de déconstruire, nettoyer, remixer et masteriser n'importe quel fichier audio via une interface moderne.

---

## ⚠️ PRÉ-REQUIS (À LIRE AVANT D'INSTALLER)

Pour que le traitement audio fonctionne, votre ordinateur doit disposer de deux outils système essentiels.

### 1. Python 3.10 (Le Moteur)
Cet outil a été conçu spécifiquement pour **Python 3.10**. Les versions plus récentes (3.11, 3.12) peuvent poser problème avec certaines bibliothèques audio.
* 📥 [Télécharger Python 3.10.11](https://www.python.org/ftp/python/3.10.11/python-3.10.11-amd64.exe)
* 🛑 **IMPORTANT :** Lors de l'installation, cochez impérativement la case **"Add Python 3.10 to PATH"** en bas de la fenêtre.

### 2. FFmpeg (Le Convertisseur)
C'est le "couteau suisse" qui permet de lire et écrire les fichiers MP3/WAV. Sans lui, l'application ne pourra pas ouvrir vos fichiers.

* **Sur Windows :**
    1.  Téléchargez la version "Essentials" sur [gyan.dev](https://www.gyan.dev/ffmpeg/builds/ffmpeg-git-essentials.7z).
    2.  Dézippez le dossier (ex: à la racine `C:fmpeg`).
    3.  Ajoutez le dossier `bin` (ex: `C:fmpegin`) à vos **Variables d'environnement (PATH)** Windows.
    4.  *Vérification :* Ouvrez une console (cmd) et tapez `ffmpeg -version`. Si du texte s'affiche, c'est bon.

* **Sur macOS :** `brew install ffmpeg`
* **Sur Linux :** `sudo apt install ffmpeg`

---

## 🚀 Installation & Lancement

Une fois les pré-requis installés :

### 🪟 Sur Windows
1.  Double-cliquez sur `SETUP.bat`.
2.  Choisissez le HArdware GPU compatible
3.  *(Cela va télécharger les cerveaux de l'IA, environ 2 Go. Patientez).*
4.  Une fois fini, double-cliquez sur `LANCER_STUDIO.bat` pour ouvrir le studio.

### 🐧 Sur Linux / macOS
1.  Ouvrez un terminal dans le dossier.
2.  Rendez les scripts exécutables : `chmod +x *.sh`
3.  Installez : `./INSTALL.sh`
4.  Lancez : `./LANCER_STUDIO.sh`

---

## 📖 Guide d'Utilisation

L'application est divisée en 6 étapes logiques :

### 1. Import & Analyse
* **Action :** Glissez vos fichiers audio.
* **Analyse BPM :** Cliquez sur la loupe pour détecter le Tempo et la Tonalité (Key).

### 2. Splitter (Séparation des sources)
Découpe votre musique en pistes individuelles (Stems).
* **Mode 6 Pistes :** Drums, Bass, Guitar, Piano, Vocals, Other.
* **Mode 4 Pistes :** Drums, Bass, Vocals, Other.
* **Mode Karaoké :** Sépare juste l'Instrumental et la Voix.
* **Option "Densité" :** Cochez pour réparer les "trous" de fréquences (son plus riche, mais traitement plus long).

### 3. Cleaner (Nettoyage)
Supprime le souffle.
* **Mode Hi-Fi (Recommandé) :** Nettoyage doux.
* **Mode Suno :** Nettoyage agressif (coupe > 16kHz) pour les sons générés par IA.

### 4. Vocal Split
Divise la piste voix en deux : **Lead** (Chanteur principal) et **Backing** (Chœurs).

### 5. De-Reverb
Supprime l'écho de la pièce sur les voix pour un son "studio sec" (Dry).

### 6. Mastering
Remixe automatiquement les pistes, applique un panoramique (stéréo) et normalise le volume.

---

## ⌨️ Raccourcis Clavier (Player)
Lorsque la fenêtre de lecture (visualiseur d'onde) est ouverte :
* **Espace :** Lecture / Pause.
* **Flèches Gauche/Droite :** Reculer / Avancer de 5 secondes.

---

## 🛠️ Stack Technique
* **Backend :** Python 3.10, Flask
* **Frontend :** HTML5, Glassmorphism CSS, WaveSurfer.js
* **Audio AI :** Torch, Demucs v4 (Hybrid Transformer), MDX-Net (UVR)
* **Wrapper :** PyWebview (Standalone Window)



