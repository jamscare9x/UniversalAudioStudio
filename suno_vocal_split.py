import os
from audio_separator.separator import Separator
INPUT="Cleaned_Master"; INPUT_BACKUP="Output"; OUTPUT="Split_Vocals"; MODEL="UVR_MDXNET_KARA_2.onnx"
cached_vocal = None
def get_separator():
    global cached_vocal
    if cached_vocal is None:
        sep = Separator(output_dir=OUTPUT, model_file_dir=os.path.join(OUTPUT, "models"), output_format="wav")
        sep.load_model(MODEL); cached_vocal = sep
    return cached_vocal
def process_vocal_split(progress_callback=None):
    if not os.path.exists(OUTPUT): os.makedirs(OUTPUT)
    source = INPUT; files = [f for f in os.listdir(source) if f.endswith('.wav')]
    if not files: source = INPUT_BACKUP; files = [f for f in os.listdir(source) if f.endswith('.wav')] if os.path.exists(source) else []
    targets = [f for f in files if any(x in f.lower() for x in ['vocal', 'voix', 'lead'])]
    if not targets: return
    sep = get_separator(); total = len(targets)
    for i, f in enumerate(targets):
        if progress_callback: progress_callback(int((i/total)*100), f"Splitting : {f}")
        try:
            outs = sep.separate(os.path.join(source, f))
            for o in outs:
                old = os.path.join(OUTPUT, o)
                if "Instrumental" in o: n=os.path.join(OUTPUT,f"BACKING_{f}"); os.rename(old,n) if not os.path.exists(n) else os.remove(n) or os.rename(old,n)
                elif "Vocals" in o: n=os.path.join(OUTPUT,f"LEAD_{f}"); os.rename(old,n) if not os.path.exists(n) else os.remove(n) or os.rename(old,n)
        except: pass
