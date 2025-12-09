import os
import numpy as np
import soundfile as sf
import librosa
from scipy.signal import butter, filtfilt

INPUT_FOLDER = "Output"; OUTPUT_FOLDER = "Drum_Kit"

def linear_phase_filter(data, cutoff, fs, btype, order=6):
    # Utilisation de filtfilt (Forward-Backward) pour annuler le déphasage
    # Indispensable pour que le Kick ne devienne pas "mou"
    nyq = 0.5 * fs
    if isinstance(cutoff, list): normal_cutoff = [x / nyq for x in cutoff]
    else: normal_cutoff = cutoff / nyq
    b, a = butter(order, normal_cutoff, btype=btype, analog=False)
    
    if data.ndim > 1:
        # Traitement par canal
        channels = []
        for i in range(data.shape[1]):
            channels.append(filtfilt(b, a, data[:, i]))
        return np.column_stack(channels)
    else:
        return filtfilt(b, a, data)

def normalize_stem(audio, target_db=-1.0):
    # Normalisation Peak propre
    mx = np.max(np.abs(audio))
    if mx > 0.001: # Seuil minimum de bruit
        target = 10 ** (target_db / 20)
        return audio * (target / mx)
    return audio

def process_drum_split(progress_callback=None):
    if not os.path.exists(OUTPUT_FOLDER): os.makedirs(OUTPUT_FOLDER)
    files = [f for f in os.listdir(INPUT_FOLDER) if "drums" in f.lower() and f.endswith('.wav')]
    total = len(files)
    
    for i, f in enumerate(files):
        if progress_callback: progress_callback(int((i/total)*100), f"Drum Reboot : {f}")
        file_path = os.path.join(INPUT_FOLDER, f); base_name = f.replace(".wav", "")
        
        try:
            # 1. Chargement Haute Qualité
            y, sr = sf.read(file_path, dtype='float32')
            if y.ndim == 1: y = np.vstack((y, y)).T
            
            # --- STRATEGIE CROSSOVER V2.0 ---
            
            # KICK : Tout ce qui est sous 150Hz (Sub) + 
            # On ne filtre pas les aigus brutalement, sinon on perd le "click" du pied
            # On fait un LowPass doux à 200Hz pour le corps, et on mixe un peu du signal complet traité
            
            # A. KICK (BASSE FREQUENCE PURE)
            kick_low = linear_phase_filter(np.copy(y), 160, sr, 'low', order=6)
            # B. KICK (ATTACK - TRANSIENT)
            # On garde une petite partie des médiums pour l'attaque, mais gâté
            kick_click = linear_phase_filter(np.copy(y), [160, 4000], sr, 'band', order=4)
            # Gate rudimentaire sur le click : on ne garde que les pics forts (coïncidant avec le kick)
            # (Simplification pour éviter les algos complexes : on garde juste le Low solide)
            final_kick = kick_low 
            
            # SNARE : Bande Médium
            # De 160Hz (Corps) à 6000Hz (Timbre)
            final_snare = linear_phase_filter(np.copy(y), [160, 6000], sr, 'band', order=6)
            
            # HATS : Tout ce qui brille
            # Au dessus de 6000Hz
            final_hats = linear_phase_filter(np.copy(y), 6000, sr, 'high', order=6)
            
            # --- NORMALISATION ---
            # Indispensable car le filtrage réduit l'énergie perçue
            final_kick = normalize_stem(final_kick, -1.0)
            final_snare = normalize_stem(final_snare, -2.0)
            final_hats = normalize_stem(final_hats, -3.0)
            
            # --- EXPORT ---
            sf.write(os.path.join(OUTPUT_FOLDER, f"{base_name}_KICK.wav"), final_kick, sr, subtype='PCM_24')
            sf.write(os.path.join(OUTPUT_FOLDER, f"{base_name}_SNARE.wav"), final_snare, sr, subtype='PCM_24')
            sf.write(os.path.join(OUTPUT_FOLDER, f"{base_name}_HATS.wav"), final_hats, sr, subtype='PCM_24')
            
        except Exception as e: print(f"Erreur Drum Reboot: {e}")
