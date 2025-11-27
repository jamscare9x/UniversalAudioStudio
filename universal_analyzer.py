import os
import librosa
import numpy as np
import warnings
warnings.filterwarnings('ignore')
def analyze_folder_and_return_data(input_folder_path, progress_callback=None):
    if not os.path.exists(input_folder_path): return [{"name": "Erreur", "bpm": "Dossier", "key": "Introuvable"}]
    files = [f for f in os.listdir(input_folder_path) if f.lower().endswith(('.mp3', '.wav', '.flac', '.ogg', '.m4a'))]
    results = []
    total = len(files)
    if total == 0: return [{"name": "Aucun fichier", "bpm": "-", "key": "-"}]
    for i, f in enumerate(files):
        if progress_callback: progress_callback(int((i / total) * 100), f"Analyse : {f}")
        data = {"name": f, "bpm": "?", "key": "?"}; path = os.path.join(input_folder_path, f)
        try:
            y, sr = librosa.load(path, duration=30)
            if len(y) > 0:
                onset_env = librosa.onset.onset_strength(y=y, sr=sr); tempo = librosa.beat.tempo(onset_envelope=onset_env, sr=sr)
                bpm_val = tempo[0] if isinstance(tempo, np.ndarray) else tempo
                data["bpm"] = str(int(round(float(bpm_val))))
                chroma = np.sum(librosa.feature.chroma_cqt(y=y, sr=sr), axis=1)
                notes = ['C','C#','D','D#','E','F','F#','G','G#','A','A#','B']; data["key"] = notes[np.argmax(chroma)]
            else: data["bpm"] = "Err"; data["key"] = "Vide"
        except Exception as e: print(f"Erreur {f}: {e}"); data["bpm"] = "Err"; data["key"] = "Err"
        results.append(data)
    if progress_callback: progress_callback(100, "Terminé.")
    return results
