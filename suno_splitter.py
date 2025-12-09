import os
import logging
import gc
import shutil
# Force ONNX strategy
os.environ["ORT_STRATEGY"] = "system"

import numpy as np
import soundfile as sf
import librosa
from audio_separator.separator import Separator
from scipy.signal import butter, lfilter, savgol_filter
from scipy.special import expit
from scipy.ndimage import gaussian_filter1d

INPUT_FOLDER = "Input"
OUTPUT_FOLDER = "Output"
TEMP_FOLDER = "Temp_Smooth"

# --- CONFIGURATION V4.5 ---
MODEL_MDX = "UVR-MDX-NET-Inst_HQ_3.onnx"
MODEL_DEMUCS = "htdemucs_6s.yaml" 
FORMATS = ('.mp3','.wav','.flac','.ogg','.m4a','.mp4','.wma')

separator_mdx = None
separator_demucs = None

def get_mdx_engine():
    global separator_mdx
    if separator_mdx is None:
        print(f"Chargement Moteur Vocal (MDX)...")
        sep = Separator(output_dir=TEMP_FOLDER, model_file_dir=os.path.join(OUTPUT_FOLDER, "models"), output_format="wav")
        sep.load_model(MODEL_MDX)
        separator_mdx = sep
    return separator_mdx

def get_demucs_engine():
    global separator_demucs
    if separator_demucs is None:
        print(f"Chargement Moteur Instrumental (Demucs)...")
        sep = Separator(output_dir=TEMP_FOLDER, model_file_dir=os.path.join(OUTPUT_FOLDER, "models"), output_format="wav")
        sep.load_model(MODEL_DEMUCS)
        separator_demucs = sep
    return separator_demucs

def safe_load(path, target_sr=44100):
    try:
        if not os.path.exists(path): return None, target_sr
        data, sr = sf.read(path, dtype='float32')
        if sr != target_sr:
            if data.ndim > 1: data = librosa.resample(data.T, orig_sr=sr, target_sr=target_sr).T
            else: data = librosa.resample(data, orig_sr=sr, target_sr=target_sr)
            sr = target_sr
        if data.ndim == 1: data = np.column_stack((data, data))
        return data, sr
    except: return None, target_sr

def safe_save(path, data, sr):
    if data is None: return
    if np.isnan(data).any(): data = np.nan_to_num(data)
    
    # Clamp Anti-Clip
    max_peak = np.max(np.abs(data))
    if max_peak > 0.98:
        scaler = 0.98 / max_peak
        data = data * scaler
        
    sf.write(path, data, sr, subtype='PCM_24')

# --- LE CORRECTIF ANTI-BITCRUSH (Lissage du Masque) ---
def apply_smooth_fuzzy_correction(audio, stem_name, sr):
    """
    Applique la logique floue MAIS avec un lissage agressif sur le masque
    pour empêcher le masque de "vibrer" (ce qui crée le son bitcrush/métallique).
    """
    if audio is None: return None
    
    # 1. Analyse Mono
    mono = np.mean(audio, axis=1) if audio.ndim > 1 else audio
    
    # 2. Calcul d'enveloppe haute résolution
    # On réduit le hop_length pour plus de précision temporelle
    hop_len = 256 
    frame_len = 1024
    
    rms = librosa.feature.rms(y=mono, frame_length=frame_len, hop_length=hop_len)[0]
    # Interpolation linéaire pour revenir à la taille échantillon
    rms_full = np.interp(np.arange(len(mono)), np.arange(len(rms)) * hop_len, rms)
    
    noise_floor = np.mean(rms_full)
    std_dev = np.std(rms_full)
    if std_dev == 0: return audio
    
    # 3. Logique Floue (Sigmoïde) - Le Cerveau
    # Détermine ce qui est signal et ce qui est bruit
    z_score = (rms_full - noise_floor) / std_dev
    
    # Agressivité adaptée : Moins forte sur la guitare pour garder le corps
    sigmoid_slope = 1.0
    if "guitar" in stem_name.lower(): sigmoid_slope = 0.8
    if "piano" in stem_name.lower(): sigmoid_slope = 0.7
    
    raw_mask = expit(z_score * sigmoid_slope)
    
    # 4. Protection des Transitoires (Dérivée)
    derivative = np.abs(np.gradient(mono))
    derivative = np.convolve(derivative, np.ones(100)/100, mode='same') # Lissage dérivée
    transient_thresh = np.mean(derivative) * 2.0
    protection = np.where(derivative > transient_thresh, 1.0, 0.0)
    
    # Masque combiné brut (C'est lui qui causait le bitcrush car il tremble trop vite)
    combined_mask = np.maximum(raw_mask, protection)
    
    # 5. LE LISSAGE MAGIQUE (The Bitcrush Killer)
    # On applique un filtre Gaussien sur le masque lui-même.
    # Cela empêche le volume de changer plus vite que 20ms.
    # Sigma = sr * 0.01 (10ms de lissage)
    sigma = sr * 0.015 
    smooth_mask = gaussian_filter1d(combined_mask, sigma)
    
    # On ne laisse jamais le masque tomber à 0 (Silence absolu = son artificiel)
    # On garde un "Noise Floor" de 10% (-20dB)
    smooth_mask = np.clip(smooth_mask, 0.1, 1.0)
    
    # Application
    if audio.ndim > 1:
        return audio * smooth_mask[:, np.newaxis]
    else:
        return audio * smooth_mask

def invert_audio(original, subtraction):
    min_len = min(len(original), len(subtraction))
    return original[:min_len] - subtraction[:min_len]

def process_audio(progress_callback=None, smart_recovery=True, stem_mode='6s'):
    if not os.path.exists(INPUT_FOLDER): os.makedirs(INPUT_FOLDER)
    if not os.path.exists(OUTPUT_FOLDER): os.makedirs(OUTPUT_FOLDER)
    if not os.path.exists(TEMP_FOLDER): os.makedirs(TEMP_FOLDER)
    
    files = [f for f in os.listdir(INPUT_FOLDER) if f.lower().endswith(FORMATS)]
    
    for i, f in enumerate(files):
        f_path = os.path.join(INPUT_FOLDER, f)
        base = int((i/len(files))*100)
        
        # --- PHASE 1 : VOIX ---
        if progress_callback: progress_callback(base, f"Isolation Voix (MDX)...")
        sep_mdx = get_mdx_engine()
        outs_mdx = sep_mdx.separate(f_path)
        
        p_inst_mdx = ""
        p_vox_mdx = ""
        for out in outs_mdx:
            if "Instrumental" in out: p_inst_mdx = os.path.join(TEMP_FOLDER, out)
            elif "Vocals" in out: p_vox_mdx = os.path.join(TEMP_FOLDER, out)
            
        vox_data, sr = safe_load(p_vox_mdx)
        if vox_data is None:
            og, _ = safe_load(f_path)
            ins, _ = safe_load(p_inst_mdx)
            vox_data = invert_audio(og, ins)
            
        # Nettoyage Voix
        #vox_data = apply_smooth_fuzzy_correction(vox_data, "Vocals", sr)
        safe_save(os.path.join(OUTPUT_FOLDER, f"{os.path.splitext(f)[0]}_Vocals.wav"), vox_data, sr)
        
        # --- PHASE 2 : INSTRUMENTS ---
        if progress_callback: progress_callback(base+30, f"Séparation Stems (Demucs)...")
        sep_dem = get_demucs_engine()
        outs_dem = sep_dem.separate(p_inst_mdx)
        
        detected_stems = {}
        for out in outs_dem:
            low = out.lower()
            s_type = "Unknown"
            if "drum" in low: s_type = "Drums"
            elif "bass" in low: s_type = "Bass"
            elif "guitar" in low: s_type = "Guitar"
            elif "piano" in low: s_type = "Piano"
            elif "other" in low: s_type = "Other"
            
            if s_type != "Unknown":
                detected_stems[s_type] = os.path.join(TEMP_FOLDER, out)
        
        # --- PHASE 3 : LISSAGE MATHÉMATIQUE ---
        if progress_callback: progress_callback(base+70, f"Smooth Math Processing...")
        
        for s_type, s_path in detected_stems.items():
            data, s_rate = safe_load(s_path)
            
            # Application sur Guitar/Piano/Other (là où le bitcrush était)
            if s_type in ["Guitar", "Piano", "Other"]:
                print(f"   -> Cleaning {s_type} (Smooth Mode)...")
                data = apply_smooth_fuzzy_correction(data, s_type, s_rate)
            
            final_name = f"{os.path.splitext(f)[0]}_{s_type}.wav"
            safe_save(os.path.join(OUTPUT_FOLDER, final_name), data, s_rate)

        try:
            shutil.rmtree(TEMP_FOLDER)
            os.makedirs(TEMP_FOLDER)
        except: pass
