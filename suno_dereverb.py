import os
from audio_separator.separator import Separator
INPUT_CLEAN="Split_Vocals"; OUTPUT="Dry_Vocals"; MODEL="Reverb_HQ_By_FoxJoy.onnx"
cached_dereverb = None
def get_separator():
    global cached_dereverb
    if cached_dereverb is None:
        sep = Separator(output_dir=OUTPUT, model_file_dir=os.path.join(OUTPUT, "models"), output_format="wav")
        sep.load_model(MODEL); cached_dereverb = sep
    return cached_dereverb
def process_dereverb(progress_callback=None):
    if not os.path.exists(OUTPUT): os.makedirs(OUTPUT)
    files = [f for f in os.listdir(INPUT_CLEAN) if f.endswith('.wav')]
    targets = [f for f in files if any(x in f.lower() for x in ['vocal', 'voix', 'lead', 'backing'])]
    if not targets: return
    sep = get_separator(); total = len(targets)
    for i, f in enumerate(targets):
        if progress_callback: progress_callback(int((i/total)*100), f"De-Reverb : {f}")
        try:
            out = sep.separate(os.path.join(INPUT_CLEAN, f))
            for o in out:
                p = os.path.join(OUTPUT, o)
                if "Reverb" in o and "Other" not in o:
                    n = f.replace(".wav", "_WET.wav"); 
                    if os.path.exists(os.path.join(OUTPUT, n)): os.remove(os.path.join(OUTPUT, n)); os.rename(p, os.path.join(OUTPUT, n))
                else:
                    n = f.replace(".wav", "_DRY.wav"); 
                    if os.path.exists(os.path.join(OUTPUT, n)): os.remove(os.path.join(OUTPUT, n)); os.rename(p, os.path.join(OUTPUT, n))
        except: pass
