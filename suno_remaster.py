import os
from pydub import AudioSegment
from pydub.effects import normalize
DIR_INST="Cleaned_Master"; DIR_VOX="Dry_Vocals"; OUTPUT="FINAL_MASTER"
class AutoMixer:
    def __init__(self):
        if not os.path.exists(OUTPUT): os.makedirs(OUTPUT)
    def load(self,f,n,v,p):
        path=os.path.join(f,n)
        if not os.path.exists(path): return None
        return normalize(AudioSegment.from_file(path)).pan(p)+v
    def find(self,f,k):
        if not os.path.exists(f): return None
        for i in os.listdir(f):
            if k in i.lower() and "dry" in i.lower() and i.endswith('.wav'): return i
        for i in os.listdir(f):
            if k in i.lower() and i.endswith('.wav'): return i
        return None
    def run_mastering(self,progress_callback=None):
        drums=[f for f in os.listdir(DIR_INST) if "drums" in f.lower()]; total=len(drums)
        for i,d in enumerate(drums):
            if progress_callback: progress_callback(int((i/total)*100), "Mixage & Mastering...")
            pid=d.lower().replace("drums","").replace(".wav","").replace("clean_","")
            mix=self.load(DIR_INST,d,-1.5,0.0)
            b=self.load(DIR_INST,self.find(DIR_INST,"bass")or"",-3.0,0.0); mix=mix.overlay(b) if b else mix
            g=self.load(DIR_INST,self.find(DIR_INST,"guitar")or"",-4.0,-0.3); mix=mix.overlay(g) if g else mix
            p=self.load(DIR_INST,self.find(DIR_INST,"piano")or"",-4.0,0.3); mix=mix.overlay(p) if p else mix
            o=self.load(DIR_INST,self.find(DIR_INST,"other")or"",-6.0,0.0); mix=mix.overlay(o) if o else mix
            bk=self.load(DIR_VOX,self.find(DIR_VOX,"backing")or"",-5.0,0.6); mix=mix.overlay(bk).overlay(bk.pan(-0.6)) if bk else mix
            ld=self.load(DIR_VOX,self.find(DIR_VOX,"lead")or"",-0.5,0.0); mix=mix.overlay(ld) if ld else mix
            normalize(mix,headroom=1.0).export(os.path.join(OUTPUT,f"MASTER_{pid}.wav"),format="wav")
