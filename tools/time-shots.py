import json, re, subprocess
al=json.load(open('align.json')); secs=json.load(open('sections.json'))
def toks(t): return re.sub(r"[^a-z' ]"," ",t.lower().replace("-"," ")).split()
def dur(i): return float(subprocess.run(["ffprobe","-v","error","-show_entries","format=duration","-of","default=nw=1:nk=1","/home/user/YouTube-/video-01/voice/%02d.mp3"%i],capture_output=True,text=True).stdout)
shots=[]; sec=None
for line in open('plan.txt'):
    line=line.rstrip('\n')
    if not line or line.startswith('#'): continue
    if line.startswith('=='): sec=int(line[2:]); continue
    kind,style,cue,desc=line.split('|',3)
    opt=kind=='F?'; kind='F' if opt else kind
    shots.append(dict(sec=sec,kind=kind,style=style,cue=cue,desc=desc,optional=opt))
flow=0; fcue={}
for s in shots:
    if s['kind']=='F': flow+=1; s['img']=flow; fcue[s['cue']]=flow
for s in shots:
    if s['kind'].startswith('R:'):
        s['img']=fcue[s['kind'][2:]]; s['kind']='R'
g=0
for s in shots:
    if s['kind']=='G': g+=1; s['gid']='G%02d'%g
# timing
pos={}
for i in range(1,13):
    words=al[str(i)]['words']; st=al[str(i)]['start']; D=dur(i)
    ss=[s for s in shots if s['sec']==i]; k0=0
    for s in ss:
        c=toks(s['cue']); found=None
        for k in range(k0,len(words)-len(c)+1):
            if words[k:k+len(c)]==c: found=k; break
        assert found is not None, (i,s['cue'])
        s['word']=found; s['t']=max(0.0,st[found]-0.15); k0=found+1
    ss[0]['t']=0.0
    for a,b in zip(ss,ss[1:]): a['d']=round(b['t']-a['t'],1)
    ss[-1]['d']=round(D-ss[-1]['t'],1)
    for s in ss:
        s['line']=' '.join(words[s['word']:s['word']+12])
json.dump(shots,open('shots.json','w'),indent=1)
import collections
print("shots",len(shots),"flow images",flow,"optional",sum(1 for s in shots if s.get("optional")),"reuses",sum(1 for s in shots if s['kind']=='R'),"graphics",g)
long=[s for s in shots if s['d']>9]; short=[s for s in shots if s['d']<2.5]
print("avg seconds per shot %.1f"%(sum(s['d'] for s in shots)/len(shots)))
print("LONG (>9s):"); [print("  s%02d %-2s %4.1fs  %s"%(s['sec'],s['kind'],s['d'],s['cue'])) for s in long]
print("SHORT (<2.5s):"); [print("  s%02d %-2s %4.1fs  %s"%(s['sec'],s['kind'],s['d'],s['cue'])) for s in short]
