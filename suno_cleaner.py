import os
import numpy as np
import noisereduce as nr
import soundfile as sf
from scipy.signal import butter, lfilter
INPUT="Output"; OUTPUT="Cleaned_Master"
def clean_file(path,out_path,mode):
    try:
        data, sr = sf.read(path)
        prop=0.7 if mode=='suno' else 0.15
        stat=False if mode=='suno' else True
        if data.ndim > 1: data = data.T
        reduced = nr.reduce_noise(y=data, sr=sr, prop_decrease=prop, stationary=stat)
        if data.ndim > 1: reduced = reduced.T
        if mode=='suno':
            b, a = butter(5, 17000/(0.5*sr), btype='low')
            if reduced.ndim > 1:
                l = lfilter(b, a, reduced[:,0]); r = lfilter(b, a, reduced[:,1]); reduced = np.column_stack((l,r))
            else: reduced = lfilter(b, a, reduced)
        mx = np.max(np.abs(reduced))
        if mx > 1.0: reduced = reduced * (0.98 / mx)
        sf.write(out_path, reduced, sr, subtype='PCM_24')
    except Exception as e: print(e)
def batch_clean(mode='hifi',progress_callback=None):
    if not os.path.exists(OUTPUT): os.makedirs(OUTPUT)
    files=[f for f in os.listdir(INPUT) if f.endswith('.wav')]; total=len(files)
    for i,f in enumerate(files):
        if progress_callback: progress_callback(int((i/total)*100), f"Clean : {f}")
        clean_file(os.path.join(INPUT,f),os.path.join(OUTPUT,f),mode)
