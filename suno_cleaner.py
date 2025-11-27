import os
import numpy as np
import noisereduce as nr
from scipy.io import wavfile
from scipy.signal import butter, lfilter
from pydub import AudioSegment
INPUT="Output"; OUTPUT="Cleaned_Master"
def low_pass(data,c,fs): b,a=butter(5,c/(0.5*fs),btype='low',analog=False); return lfilter(b,a,data)
def clean_file(path,out_path,mode):
    audio=AudioSegment.from_file(path).set_frame_rate(44100); samples=np.array(audio.get_array_of_samples())
    if audio.channels==2: samples=samples.reshape((-1,2))
    prop=0.7 if mode=='suno' else 0.15; stat=False if mode=='suno' else True
    try:
        reduced=nr.reduce_noise(y=samples.T if audio.channels==2 else samples,sr=44100,prop_decrease=prop,stationary=stat); data=reduced.T if audio.channels==2 else reduced
    except: data=samples
    if mode=='suno':
        try:
            if audio.channels==2: l=low_pass(data[:,0],17000,44100); r=low_pass(data[:,1],17000,44100); data=np.column_stack((l,r))
            else: data=low_pass(data,17000,44100)
        except: pass
    wavfile.write(out_path,44100,data.astype(np.int16))
def batch_clean(mode='hifi',progress_callback=None):
    if not os.path.exists(OUTPUT): os.makedirs(OUTPUT)
    files=[f for f in os.listdir(INPUT) if f.endswith('.wav')]; total=len(files)
    for i,f in enumerate(files):
        if progress_callback: progress_callback(int((i/total)*100), f"Clean : {f}")
        clean_file(os.path.join(INPUT,f),os.path.join(OUTPUT,f),mode)
