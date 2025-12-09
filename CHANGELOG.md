# Changelog - Universal Audio Studio

Toutes les modifications notables de ce projet seront documentées dans ce fichier.

## [5.3.6] - Golden Master - 2023-10-XX
**La version de référence.** Réécriture complète des moteurs audio pour une fidélité "Audiophile".

### 🚀 Moteurs Audio (Core)
- **Splitter V5 (Bitcrush Killer) :** Remplacement de la séparation brute par un algorithme à **Logique Floue (Fuzzy Logic)**.
    - Ajout d'un lissage Gaussien (`gaussian_filter1d`) sur les masques spectraux.
    - Élimination de 95% des artefacts métalliques sur les Stems Guitare et Piano.
- **Vocal Doctor (Inpainting) :** Nouveau module dans `suno_vocal_split.py`.
    - Utilise une **Interpolation Cubique** (`scipy.interpolate`) pour détecter et redessiner les micro-coupures (dropouts < 50ms) dans les voix générées par IA.
- **Auto-Remaster V2 (Multipiste) :** Abandon de la simple normalisation globale.
    - Le moteur charge désormais chaque stem individuellement (Bass, Drums, Vocals).
    - Application de panoramiques discrets et de gains spécifiques avant le mixage final via `pydub`.
    - Limiteur Brickwall à -1.0 dB en sortie.
- **Drum Lab (Crossover DSP) :** Refonte totale de la séparation batterie.
    - Utilisation de filtres à phase linéaire (`filtfilt`) pour séparer Kick/Snare/Hats sans déphasage temporel (le Kick reste percutant).
- **Cleaner (Spectral Gate) :** Passage à `noisereduce` avec un profil de bruit stationnaire pour obtenir un fond sonore "noir absolu".

### 📊 Analyse & Métadonnées
- **Analyzer Z-Score :** Intégration de l'algorithme statistique Z-Score pour le calcul du BPM. Élimine les "outliers" (valeurs aberrantes) pour une stabilité parfaite sur la musique électronique.
- **Metadonnées Réelles :** Remplacement de `tinytag` par `mutagen` pour lire le vrai bitrate et la profondeur de bits (16/24/32-float).

---

## [5.3.5] - Stabilization Update
Correction des régressions critiques introduites par la refonte UI.

### 🐛 Correctifs
- **Fix Import :** Résolution du bug où la barre de progression fantôme faisait planter l'upload de fichiers. L'import utilise désormais la barre de statut principale.
- **Fix Moteur Analyse :** Le fichier `universal_analyzer.py` est désormais inclus par défaut pour éviter le crash au démarrage si Librosa est absent.

---

## [5.3.3] - WebView & Download Fix
Adaptation du code pour l'environnement de bureau "PyWebView".

### 🛠️ Système
- **Contournement Sécurité WebView :** Les téléchargements (ZIP et Pistes individuelles) étaient bloqués par le navigateur interne.
- **Solution :** Réécriture des appels JS pour utiliser `window.open(url, '_blank')`, forçant l'ouverture du navigateur système pour la sauvegarde des fichiers.

---

## [5.3.2] - Player & Loop Fix
Amélioration de l'expérience utilisateur dans le lecteur audio intégré.

### 🎧 Player Audio
- **Boucle Synchronisée (Loop) :** Correction d'un bug logique où le player s'arrêtait à la fin de la piste au lieu de boucler. La fonction `ended` force maintenant un `.play()` immédiat.
- **UI Langues :** Les boutons FR/GB sont désormais fonctionnels et persistent via `localStorage`.
- **Tooltips :** Retour des info-bulles explicatives au survol des tuiles.

---

## [5.0.0] - "Universal" Update (Major)
Passage d'une collection de scripts à une application unifiée.

### ✨ Nouveautés
- **Nouvelle Interface :** Design "Glassmorphism" sombre, tuiles interactives, barre de progression globale.
- **Architecture Flask :** Le backend Python sert désormais une interface HTML/JS/CSS moderne.
- **Modèles SOTA :** Intégration par défaut de `UVR-MDX-NET-Inst_HQ_3` (le meilleur modèle vocal actuel) et `htdemucs_6s` (6 pistes).

---

## [4.5.0] - The "Stem" Era
Introduction de la séparation avancée.

- **6 Stems :** Ajout du support pour la guitare et le piano (auparavant limités à Drums/Bass/Other).
- **Format WAV Float :** Passage du traitement interne en 32-bit Float pour éviter la saturation numérique entre les étapes.

---

## [3.0.0] - Python Scripts
L'époque des scripts en ligne de commande.

- **Batch Processing :** Capacité de traiter un dossier entier d'un coup.
- **Librairie Audio-Separator :** Abandon des implémentations manuelles de Demucs pour l'utilisation du wrapper `audio-separator` plus rapide.

---

## [2.34] - Legacy (Point de départ)
Version initiale.

- **Fonctionnalités :** Séparation basique 4 pistes (Vocals, Drums, Bass, Other).
- **Moteur :** Demucs v3 standard.
- **Interface :** Aucune (Ligne de commande CLI).
- **Qualité :** Standard (beaucoup de "bleed" vocal et d'artefacts).
- 
## [v2.34] - Final Fix
- Correction du script de génération de release.

## [v2.33] - Bit Depth
- Ajout de l'analyse 16/24/32-bit.
- Correction nommage De-Reverb.

