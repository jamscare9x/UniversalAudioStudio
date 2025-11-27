import os
import mutagen
from mutagen.mp3 import MP3; from mutagen.wave import WAVE; from mutagen.flac import FLAC; from mutagen.oggvorbis import OggVorbis
def get_audio_metadata(folder_path):
    if not os.path.exists(folder_path): return []
    files=[f for f in os.listdir(folder_path) if f.lower().endswith(('.mp3','.wav','.flac','.ogg','.m4a'))]; report=[]
    for f in files:
        path=os.path.join(folder_path,f); meta={"filename":f,"format":f.split('.')[-1].upper(),"duration":"0:00","sample_rate":"? Hz","bitrate":"? kbps","bit_depth":"-","channels":"Mono","tags":{"title":"-","artist":"-"}}
        try:
            audio=mutagen.File(path)
            if audio is not None:
                if hasattr(audio,'info'):
                    info=audio.info
                    if hasattr(info,'length') and info.length>0: m,s=divmod(int(info.length),60); meta['duration']=f"{m}:{s:02d}"
                    if hasattr(info,'sample_rate'): meta['sample_rate']=f"{info.sample_rate} Hz"
                    if hasattr(info,'channels'): meta['channels']="Stereo" if info.channels==2 else f"{info.channels} Ch"
                    if hasattr(info,'bitrate') and info.bitrate>0: meta['bitrate']=f"{int(info.bitrate/1000)} kbps"
                    else:
                        try:
                            size=os.path.getsize(path); dur=info.length
                            if dur>0: calc=int((size*8)/dur/1000); meta['bitrate']=f"{calc} kbps"
                        except: pass
                    if hasattr(info,'bits_per_sample'): meta['bit_depth']=f"{info.bits_per_sample} bit"
                    elif meta['format']=="MP3" or meta['format']=="OGG": meta['bit_depth']="Lossy"
                tags=audio.tags
                if tags:
                    if 'TIT2' in tags: meta['tags']['title']=str(tags['TIT2'])
                    if 'TPE1' in tags: meta['tags']['artist']=str(tags['TPE1'])
                    if 'INAM' in tags: meta['tags']['title']=str(tags['INAM'])
                    if 'IART' in tags: meta['tags']['artist']=str(tags['IART'])
                    if 'title' in tags: meta['tags']['title']=str(tags['title'][0])
                    if 'artist' in tags: meta['tags']['artist']=str(tags['artist'][0])
        except Exception as e: print(f"Err meta {f}: {e}")
        report.append(meta)
    return report
