# 🎵 Universal Audio Studio (v5.3.6 - Golden Master)

> **The Audiophile's Offline Swiss Army Knife.** > *Qualité Studio. Traitement Local. Zéro Compression.*

![Version](https://img.shields.io/badge/version-5.3.6_Golden_Master-blue) ![Python](https://img.shields.io/badge/python-3.10%2B-yellow) ![License](https://img.shields.io/badge/license-MIT-green)

**Universal Audio Studio** est une suite de post-production audio alimentée par l'IA, conçue pour fonctionner **localement** (sans cloud). Contrairement aux outils en ligne qui compressent l'audio pour la vitesse, ou aux logiciels DJ qui sacrifient la qualité pour la latence, ce projet vise la **fidélité audio absolue** (WAV 24-bit/float).

---

## 🌟 Nouveautés de la v5.3.6 (Golden Master)

Cette version intègre des moteurs audio entièrement réécrits pour corriger les défauts historiques de la séparation par IA (artefacts métalliques, trous dans le spectre).

### 🛠️ Moteurs Exclusifs
| Module | Technologie / Algorithme | Fonction |
| :--- | :--- | :--- |
| **Splitter V5** | **"Bitcrush Killer"** | Utilise un *lissage gaussien* sur les masques de séparation flous (Fuzzy Logic) pour éliminer le son métallique sur les guitares et pianos. |
| **Vocal Doctor** | **Inpainting Cubique** | Répare les micro-coupures (<50ms) et les zéros numériques dans les voix par interpolation mathématique (`scipy`). |
| **Auto-Remaster** | **AutoMixer Multipiste** | Mixage dynamique des stems (Pan/Vol) via `pydub` suivi d'une normalisation LUFS et d'un Limiteur Brickwall. |
| **Drum Lab** | **Crossover DSP** | Sépare Kick/Snare/Hats en utilisant des filtres à phase linéaire (`filtfilt`) pour préserver le "punch" des transitoires. |
| **Analyzer** | **Z-Score Fuzzy Logic** | Détection de BPM statistique qui élimine les faux positifs (doubles/moitiés) via calcul d'écart-type. |
| **Cleaner** | **Spectral Gating** | Débruitage stationnaire avancé basé sur `noisereduce` pour un fond sonore "noir absolu". |

---

## 🚀 Performances & Comparatif

| Critère | Universal Audio Studio | LALAL.ai / Moises | Serato / VirtualDJ |
| :--- | :--- | :--- | :--- |
| **Modèle Voix** | **MDX-Net HQ_3 (SOTA)** | Propriétaire (Optimisé Cloud) | Low-Latency (Allégé) |
| **Qualité Audio** | **Lossless (WAV 24-bit)** | Souvent compressé | Artefacts de phase |
| **Confidentialité**| **100% Local (Offline)** | Upload Cloud requis | Local |
| **Vitesse** | Lente (Focus Qualité) | Très Rapide | Temps Réel (10ms) |
| **Coût** | **Gratuit** | Abonnement | Licence Logiciel |

---

## 📦 Installation

### Pré-requis
1.  **Python 3.10+** installé.
2.  **FFmpeg** installé et ajouté au PATH système (Requis par `pydub`).

### Dépendances
Installez les bibliothèques nécessaires via pip :

```bash
pip install flask pywebview psutil numpy scipy librosa soundfile audio-separator pydub noisereduce mutagen openai-whisper torch onnxruntime
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
* **Option "NUCLEAR WIPE" :** Cochez pour réparer les "trous" de fréquences (son plus riche, mais traitement plus long).

### 2b. Drumlab (Séparation des drums)
Kick, Snare, Hi-hat

### 3. Cleaner (Nettoyage)
Supprime le souffle.
* **Mode Hi-Fi (Recommandé) :** Nettoyage doux.
* **Mode Suno :** Nettoyage agressif (coupe > 16kHz) pour les sons générés par IA.

### 3b. Stem doctor
Répare les dropouts des stem après séparation

### 3c. MP3 restore
Répare les dégats causés par le compression MP3,MP4, ou autre

### 4. Vocal Split
Divise la piste voix en deux : **Lead** (Chanteur principal) et **Backing** (Chœurs).

### 5. De-Reverb
Supprime l'écho de la pièce sur les voix pour un son "studio sec" (Dry).

### 6. Mastering
Remixe automatiquement les pistes, applique un panoramique (stéréo) et normalise le volume.

### 7. Lyrics
Essaie de determiner les lyrics d'un morceau


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




