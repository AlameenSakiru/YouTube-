"""Time every shot of a video to its voiceover.

    python3 tools/time-shots.py video-02      -> video-02/edit-plan.json

Needs VIDEO/shot-plan.txt, VIDEO/voice/word-timings.json (from align-voice.py) and the voice files.
Prompts are copied in from VIDEO/shots-untimed.json if write-flow-prompts.py has been run.
"""
import json, os, subprocess, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import shotplan

VD = os.path.abspath(sys.argv[1])
al = json.load(open(os.path.join(VD, 'voice', 'word-timings.json')))
shots = shotplan.parse(VD)
secs = shotplan.sections_of(VD)
probs = shotplan.check_cues(shots, secs)
assert not probs, probs
untimed = os.path.join(VD, 'shots-untimed.json')
if os.path.exists(untimed):
    prompts = {s['img']: s.get('prompt') for s in json.load(open(untimed)) if s['kind'] == 'F'}
    for s in shots:
        if s['kind'] == 'F' and prompts.get(s['img']): s['prompt'] = prompts[s['img']]


def dur(i):
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=nw=1:nk=1",
                                 os.path.join(VD, 'voice', '%02d.mp3' % i)], capture_output=True, text=True).stdout)


for i in range(1, len(secs) + 1):
    words, st, D = al[str(i)]['words'], al[str(i)]['start'], dur(i)
    ss = [s for s in shots if s['sec'] == i]
    for s in ss:
        s['t'] = max(0.0, st[s['word']] - 0.15)
    ss[0]['t'] = 0.0
    for a, b in zip(ss, ss[1:]): a['d'] = round(b['t'] - a['t'], 1)
    ss[-1]['d'] = round(D - ss[-1]['t'], 1)
    for s in ss: s['line'] = ' '.join(words[s['word']:s['word'] + 12])

json.dump(shots, open(os.path.join(VD, 'edit-plan.json'), 'w'), indent=1)
n = lambda k: sum(1 for s in shots if s['kind'] == k)
print("shots", len(shots), "flow images", n('F'), "graphics", n('G'), "reuses", n('R') + n('V1'))
print("average %.1f s per shot" % (sum(s['d'] for s in shots) / len(shots)))
for s in shots:
    if s['d'] > 9 or s['d'] < 2.5:
        print("  %s s%02d %-2s %4.1fs  %s" % ('LONG ' if s['d'] > 9 else 'SHORT', s['sec'], s['kind'], s['d'], s['cue']))
