import os
from audio_separator.separator import Separator
INPUT_CLEAN = "Split_Vocals"; OUTPUT = "Dry_Vocals"; MODEL = "Reverb_HQ_By_FoxJoy.onnx"
cached_dereverb = None
def get_separator():
    global cached_dereverb
    if cached_dereverb is None:
        print("Chargement De-Reverb...")
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
            out = sep.separate(os.path.join(INPUT_CLEAN, f)); base_name = os.path.splitext(f)[0]
            for o in out:
                p = os.path.join(OUTPUT, o)
                if "(Reverb)" in o:
                    n = f"{base_name}_WET_ECHO.wav"; final=os.path.join(OUTPUT, n)
                    if os.path.exists(final): os.remove(final)
                    os.rename(p, final)
                else:
                    n = f"{base_name}_DRY_STUDIO.wav"; final=os.path.join(OUTPUT, n)
                    if os.path.exists(final): os.remove(final)
                    os.rename(p, final)
        except Exception as e: print(f"Erreur: {e}")
