import os
import logging
os.environ["ORT_STRATEGY"] = "system"
import numpy as np
from audio_separator.separator import Separator
from pydub import AudioSegment
import scipy.io.wavfile as wavfile
from scipy.signal import butter, lfilter

INPUT_FOLDER="Input"; OUTPUT_FOLDER="Output"; MODEL_NAME="htdemucs_6s.yaml" 
FORMATS=('.mp3','.wav','.flac','.ogg','.m4a','.mp4','.wma')
cached_separators = {}

def get_separator(model_code):
    model_name = "htdemucs_6s.yaml" if model_code == '6s' else "htdemucs.yaml"
    global cached_separators
    if model_name not in cached_separators:
        print(f"Chargement {model_name}...")
        sep = Separator(output_dir=OUTPUT_FOLDER, model_file_dir=os.path.join(OUTPUT_FOLDER, "models"), output_format="wav")
        sep.load_model(model_name)
        cached_separators[model_name] = sep
    return cached_separators[model_name]

def apply_gate(path, thresh):
    try:
        audio=AudioSegment.from_file(path); chunks=[audio[i:i+50] for i in range(0,len(audio),50)]; processed=[c-30 if c.dBFS<thresh else c for c in chunks]; sum(processed).export(path,format="wav",parameters=["-acodec","pcm_s16le"])
    except: pass
def butter_filter(data, cutoff, fs, btype, order=5):
    nyq = 0.5 * fs; normal_cutoff = cutoff / nyq; b, a = butter(order, normal_cutoff, btype=btype, analog=False); return lfilter(b, a, data)
def safe_normalize_and_save(data, rate, path):
    rms = np.sqrt(np.mean(data**2))
    if rms < 10.0: silence = np.zeros_like(data).astype(np.int16); wavfile.write(path, rate, silence); return
    max_val = np.max(np.abs(data)); target_ceiling = 32000.0
    if max_val > target_ceiling: data = data * (target_ceiling / max_val)
    data = np.clip(data, -32768, 32767)
    wavfile.write(path, rate, data.astype(np.int16))
def apply_studio_eq(file_path, instrument_name):
    try:
        rate, data = wavfile.read(file_path); data = data.astype(np.float32)
        if len(data.shape) > 1: channels = [data[:, i] for i in range(data.shape[1])]
        else: channels = [data]
        filtered_channels = []
        lp_freq = None; hp_freq = None; n = instrument_name.lower()
        if 'bass' in n: hp_freq = 30; lp_freq = 8000
        elif 'drum' in n: hp_freq = 20
        elif 'vocal' in n or 'lead' in n: hp_freq = 100; lp_freq = 17000
        elif 'guitar' in n: hp_freq = 80; lp_freq = 16000
        elif 'piano' in n: hp_freq = 60; lp_freq = 16000
        elif 'other' in n: hp_freq = 40
        for chan in channels:
            if hp_freq: chan = butter_filter(chan, hp_freq, rate, 'high')
            if lp_freq: chan = butter_filter(chan, lp_freq, rate, 'low')
            filtered_channels.append(chan)
        if len(filtered_channels) > 1: final_data = np.column_stack(filtered_channels)
        else: final_data = filtered_channels[0]
        safe_normalize_and_save(final_data, rate, file_path)
    except Exception as e: print(f"Erreur EQ {instrument_name}: {e}")
def recover_lost_frequencies_safe(original_path, stem_path, other_stems_paths, output_path):
    try:
        sound_og = AudioSegment.from_file(original_path); sound_others = None
        for p in other_stems_paths:
            if os.path.exists(p):
                s = AudioSegment.from_file(p); sound_others = s if sound_others is None else sound_others.overlay(s)
        if sound_others is None: return
        residual = sound_og.overlay(sound_others.invert_phase())
        target_stem = AudioSegment.from_file(stem_path)
        final_mix = target_stem.overlay(residual - 4)
        final_mix.export(output_path, format="wav")
    except Exception as e: print(f"Erreur Recovery Safe: {e}")
def process_audio(progress_callback=None, smart_recovery=False, stem_mode='6s'):
    if not os.path.exists(INPUT_FOLDER): os.makedirs(INPUT_FOLDER)
    if not os.path.exists(OUTPUT_FOLDER): os.makedirs(OUTPUT_FOLDER)
    files=[f for f in os.listdir(INPUT_FOLDER) if f.lower().endswith(FORMATS)]
    if not files: return
    sep = get_separator('6s' if stem_mode=='6s' else '4s'); total = len(files)
    for i, f in enumerate(files):
        base = int((i/total)*100)
        if progress_callback: progress_callback(base, f"Séparation : {f}")
        original_file_path = os.path.join(INPUT_FOLDER, f); out_files = sep.separate(original_file_path)
        stems_map = {}
        for stem in out_files:
            path = os.path.join(OUTPUT_FOLDER, stem); stems_map[stem] = path
            if "drums" in stem: apply_gate(path, -25)
            elif "guitar" in stem: apply_gate(path, -32)
        if smart_recovery and stem_mode == '6s':
            def get_others(exclude_stem): return [os.path.join(OUTPUT_FOLDER, s) for s in out_files if s != exclude_stem]
            for stem in out_files:
                if "guitar" in stem.lower() or "piano" in stem.lower():
                    if progress_callback: progress_callback(base, f"Densification : {stem}")
                    path = os.path.join(OUTPUT_FOLDER, stem)
                    recover_lost_frequencies_safe(original_file_path, path, get_others(stem), path)
        for stem in out_files:
            path = os.path.join(OUTPUT_FOLDER, stem); apply_studio_eq(path, stem)
        if stem_mode == '2s':
            instru_mix = None
            for stem in out_files:
                stem_path = os.path.join(OUTPUT_FOLDER, stem)
                if "vocal" in stem.lower():
                    new_vox = os.path.join(OUTPUT_FOLDER, f"{f}_Vocals.wav")
                    if os.path.exists(new_vox): os.remove(new_vox); os.rename(stem_path, new_vox)
                else:
                    seg = AudioSegment.from_file(stem_path)
                    if instru_mix is None: instru_mix = seg
                    else: instru_mix = instru_mix.overlay(seg)
                    os.remove(stem_path)
            if instru_mix:
                inst_path = os.path.join(OUTPUT_FOLDER, f"{f}_Instrumental.wav"); instru_mix.export(inst_path, format="wav")
