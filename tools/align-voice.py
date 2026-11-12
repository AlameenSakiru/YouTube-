import json, subprocess, re, difflib
from concurrent.futures import ProcessPoolExecutor
from pocketsphinx import Decoder
secs=json.load(open('voice/sections.json'))
def pcm(f): return subprocess.run(["ffmpeg","-v","error","-i",f,"-ac","1","-ar","16000","-f","s16le","-"],capture_output=True).stdout
def toks(t): return re.sub(r"[^a-z' ]"," ",t.lower().replace("-"," ")).split()
def run(i):
    f="/home/user/YouTube-/video-01/voice/%02d.mp3"%i
    d=Decoder(samprate=16000); d.start_utt(); d.process_raw(pcm(f),full_utt=True); d.end_utt()
    segs=[(s.word,s.start_frame/100.0,(s.end_frame+1)/100.0) for s in d.seg()]
    return i,segs
with ProcessPoolExecutor(4) as ex: res=dict(ex.map(run,range(1,13)))
out={}
for i in range(1,13):
    segs=[(re.sub(r"\(\d+\)$","",w),a,b) for w,a,b in res[i] if not w.startswith("<") and w not in("[NOISE]","[SPEECH]") and not w.startswith("[")]
    got=[w for w,_,_ in segs]
    exp=toks(' '.join(secs[i-1]['paras']))
    sm=difflib.SequenceMatcher(None,exp,got,autojunk=False)
    t=[None]*len(exp)
    for a,b,n in sm.get_matching_blocks():
        for k in range(n): t[a+k]=(segs[b+k][1],segs[b+k][2])
    # interpolate missing start times
    known=[k for k in range(len(exp)) if t[k]]
    st=[None]*len(exp)
    for k in range(len(exp)):
        if t[k]: st[k]=t[k][0]; continue
        prv=max([j for j in known if j<k],default=None); nxt=min([j for j in known if j>k],default=None)
        if prv is None: st[k]=0.0
        elif nxt is None: st[k]=t[prv][1]
        else: st[k]=t[prv][0]+(t[nxt][0]-t[prv][0])*(k-prv)/(nxt-prv)
    out[i]={"words":exp,"start":[round(x,2) for x in st],"matched":len(known)/len(exp)}
    print("%02d aligned %d/%d words (%.0f%%)"%(i,len(known),len(exp),100*len(known)/len(exp)))
json.dump(out,open('voice/align.json','w'))
