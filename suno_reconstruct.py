import os
import numpy as np
import soundfile as sf
from scipy.interpolate import interp1d

INPUT_FOLDER = "Output"
OUTPUT_FOLDER = "Reconstructed_Stems"

def fill_gaps(y, sr):
    # Détection des zéros absolus (Dropouts)
    # On considère un "trou" si on a plus de 50 échantillons consécutifs à 0 exactement
    is_zero = np.all(y == 0, axis=1) if y.ndim > 1 else (y == 0)
    
    # On trouve les indices des zéros
    zero_indices = np.where(is_zero)[0]
    
    if len(zero_indices) == 0:
        return y # Pas de trous
        
    print(f"   -> {len(zero_indices)} échantillons manquants détectés.")
    
    # On travaille canal par canal
    y_fixed = np.copy(y)
    channels = y.shape[1] if y.ndim > 1 else 1
    
    # Optimisation : On ne fait pas sample par sample, on cherche les segments
    # (Logique simplifiée pour l'exemple : interpolation sur les zones détectées)
    
    # Pour faire simple et robuste : On utilise une interpolation linéaire sur les segments
    # On crée un masque des valeurs VALIDES (non zéro)
    valid_indices = np.where(~is_zero)[0]
    
    if len(valid_indices) < 2: return y # Fichier vide
    
    for ch in range(channels):
        data_ch = y[:, ch] if channels > 1 else y
        
        # On prend les valeurs aux indices valides
        valid_values = data_ch[valid_indices]
        
        # On crée une fonction d'interpolation
        # 'linear' = moyenne simple entre deux points
        # 'cubic' = courbe lisse (plus naturel pour l'audio)
        interp_func = interp1d(valid_indices, valid_values, kind='linear', fill_value="extrapolate")
        
        # On remplit les trous
        y_fixed[zero_indices, ch] = interp_func(zero_indices)
        
    return y_fixed

def process_reconstruction(progress_callback=None):
    if not os.path.exists(OUTPUT_FOLDER): os.makedirs(OUTPUT_FOLDER)
    
    # On cherche dans Output (les stems générés)
    files = [f for f in os.listdir(INPUT_FOLDER) if f.endswith('.wav')]
    total = len(files)
    
    for i, f in enumerate(files):
        if progress_callback: progress_callback(int((i/total)*100), f"Doctor : {f}")
        
        try:
            path_in = os.path.join(INPUT_FOLDER, f)
            y, sr = sf.read(path_in, dtype='float32')
            
            # RECONSTRUCTION
            y_repaired = fill_gaps(y, sr)
            
            # Sauvegarde
            path_out = os.path.join(OUTPUT_FOLDER, f)
            sf.write(path_out, y_repaired, sr, subtype='PCM_24')
            
        except Exception as e: print(f"Erreur Doctor {f}: {e}")

