import os
import numpy as np
import soundfile as sf
import librosa
from scipy.signal import butter, lfilter

INPUT_FOLDER = "Input"
OUTPUT_FOLDER = "Restored_HQ"

def spectral_extension(y, sr):
    b, a = butter(4, 6000/(sr/2), btype='high')
    highs = lfilter(b, a, y)
    harmonics = highs * highs * 0.1
    b2, a2 = butter(4, 14000/(sr/2), btype='high')
    air = lfilter(b2, a2, harmonics)
    return y + (air * 0.05)

def dequantize(y):
    noise = np.random.normal(0, 1e-5, y.shape)
    return y + noise

def process_uncompress(progress_callback=None):
    if not os.path.exists(OUTPUT_FOLDER): os.makedirs(OUTPUT_FOLDER)
    files = [f for f in os.listdir(INPUT_FOLDER) if f.lower().endswith(('.mp3', '.m4a', '.aac', '.wav'))]
    total = len(files)
    target_sr = 48000
    for i, f in enumerate(files):
        if progress_callback: progress_callback(int((i/total)*100), f"Restoring : {f}")
        try:
            path_in = os.path.join(INPUT_FOLDER, f)
            y, sr = librosa.load(path_in, sr=target_sr, mono=False)
            if y.ndim == 1: y = np.vstack((y, y))
            if y.ndim > 1:
                y_L = spectral_extension(y[0], target_sr)
                y_R = spectral_extension(y[1], target_sr)
                y = np.vstack((y_L, y_R))
            else: y = spectral_extension(y, target_sr)
            y = dequantize(y)
            y = y.T
            out_name = f"{os.path.splitext(f)[0]}_HQ_RESTORED.wav"
            sf.write(os.path.join(OUTPUT_FOLDER, out_name), y, target_sr, subtype='PCM_24')
        except Exception as e: print(f"Erreur Restore {f}: {e}")
