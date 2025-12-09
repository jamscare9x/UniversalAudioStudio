import os
import numpy as np
import soundfile as sf
import librosa
from audio_separator.separator import Separator
from pydub import AudioSegment
from scipy.interpolate import interp1d

# Chemins intelligents (V5.4)
DIR_CLEAN = "Cleaned_Master"
DIR_RAW = "Output"
OUTPUT = "Split_Vocals"

MODEL = "UVR_MDXNET_KARA_2.onnx"
cached_vocal = None

def get_separator():
    global cached_vocal
    if cached_vocal is None:
        sep = Separator(output_dir=OUTPUT, model_file_dir=os.path.join(OUTPUT, "models"), output_format="wav")
        sep.load_model(MODEL)
        cached_vocal = sep
    return cached_vocal

# --- MOTEUR INPAINTING (VOCAL DOCTOR) ---
def apply_vocal_inpainting(y, sr):
    """
    Répare les micro-coupures dans la voix par interpolation cubique.
    Rend la voix plus "liquide" et naturelle.
    """
    if y is None: return None
    
    # Détection des trous (0 absolu)
    is_zero = np.all(y == 0, axis=1) if y.ndim > 1 else (y == 0)
    zero_indices = np.where(is_zero)[0]
    
    # S'il n'y a pas de trous, on renvoie l'audio tel quel
    if len(zero_indices) == 0: return y
    
    # On ne répare que les "petits" trous (< 50ms) pour ne pas inventer des paroles
    # Mais sur une voix processée, tous les zéros sont suspects.
    
    y_fixed = np.copy(y)
    channels = y.shape[1] if y.ndim > 1 else 1
    valid_indices = np.where(~is_zero)[0]
    
    if len(valid_indices) < 10: return y # Fichier vide
    
    for ch in range(channels):
        data_ch = y[:, ch] if channels > 1 else y
        valid_values = data_ch[valid_indices]
        
        # Interpolation 'cubic' pour la voix (plus naturel que linear)
        try:
            interp_func = interp1d(valid_indices, valid_values, kind='cubic', fill_value="extrapolate")
            y_fixed[zero_indices, ch] = interp_func(zero_indices)
        except:
            # Fallback linear si cubic échoue
            interp_func = interp1d(valid_indices, valid_values, kind='linear', fill_value="extrapolate")
            y_fixed[zero_indices, ch] = interp_func(zero_indices)
            
    return y_fixed

def manual_tta_process(sep, input_path):
    filename = os.path.basename(input_path)
    print(f"   -> Vocal Split V5.5 (TTA + Inpainting) : {filename}")
    
    # Passe 1
    out_1 = sep.separate(input_path)
    p_lead_1 = next((os.path.join(OUTPUT, f) for f in out_1 if "Vocals" in f), None)
    p_back_1 = next((os.path.join(OUTPUT, f) for f in out_1 if "Instrumental" in f), None)
    
    if not p_lead_1: return
    
    # Passe 2 (Shift)
    audio = AudioSegment.from_file(input_path); silence = AudioSegment.silent(duration=250)
    shifted = silence + audio; shift_path = input_path.replace(".wav", "_shift.wav")
    shifted.export(shift_path, format="wav")
    
    out_2 = sep.separate(shift_path)
    p_lead_2 = next((os.path.join(OUTPUT, f) for f in out_2 if "Vocals" in f), None)
    p_back_2 = next((os.path.join(OUTPUT, f) for f in out_2 if "Instrumental" in f), None)

    def process_and_save(p1, p2, out_name):
        try:
            a1, sr = sf.read(p1, dtype='float32'); a2, _ = sf.read(p2, dtype='float32')
            offset = int(sr * 0.250)
            if a2.ndim > 1: a2 = a2[offset:, :]
            else: a2 = a2[offset:]
            
            min_len = min(len(a1), len(a2))
            
            # 1. Moyenne TTA
            res = (a1[:min_len] + a2[:min_len]) / 2
            
            # 2. INPAINTING (Le Doctor passe ici)
            res = apply_vocal_inpainting(res, sr)
            
            # 3. Safe Save
            mx = np.max(np.abs(res))
            if mx > 0.98: res = res * (0.98 / mx)
            
            sf.write(out_name, res, sr, subtype='PCM_24')
        except Exception as e: print(f"Err Fusion: {e}")
    
    base = filename.replace(".wav", "")
    process_and_save(p_lead_1, p_lead_2, os.path.join(OUTPUT, f"LEAD_{base}.wav"))
    process_and_save(p_back_1, p_back_2, os.path.join(OUTPUT, f"BACKING_{base}.wav"))
    
    # Cleanup
    temp_files = [p_lead_1, p_back_1, p_lead_2, p_back_2, shift_path]
    for p in temp_files:
        if p and os.path.exists(p): 
            try: os.remove(p)
            except: pass

def process_vocal_split(progress_callback=None):
    if not os.path.exists(OUTPUT): os.makedirs(OUTPUT)
    
    targets = []
    source_folder = ""
    
    # 1. Priorité Cleaned_Master
    if os.path.exists(DIR_CLEAN):
        candidates = [f for f in os.listdir(DIR_CLEAN) if f.endswith('.wav')]
        valid = [f for f in candidates if any(x in f.lower() for x in ['voc', 'voix', 'lead'])]
        if valid: targets = valid; source_folder = DIR_CLEAN

    # 2. Fallback Output
    if not targets and os.path.exists(DIR_RAW):
        candidates = [f for f in os.listdir(DIR_RAW) if f.endswith('.wav')]
        valid = [f for f in candidates if any(x in f.lower() for x in ['voc', 'voix', 'lead'])]
        if valid: targets = valid; source_folder = DIR_RAW
            
    if not targets:
        print("ERREUR : Aucun fichier vocal trouvé.")
        return

    sep = get_separator()
    total = len(targets)
    for i, f in enumerate(targets):
        if progress_callback: progress_callback(int((i/total)*100), f"Doctor Vocal Split : {f}")
        manual_tta_process(sep, os.path.join(source_folder, f))
