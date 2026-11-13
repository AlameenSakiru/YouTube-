"""Find when every word of the voiceover is spoken.

    python3 tools/align-voice.py video-02      -> video-02/voice/word-timings.json

Reads the section texts from VIDEO/voiceover-sections.json and the audio from VIDEO/voice/01.mp3, 02.mp3, ...
Words the recogniser misses get their times filled in between the words it found.
"""
import json, os, re, subprocess, sys, difflib
from concurrent.futures import ProcessPoolExecutor
from pocketsphinx import Decoder

VD = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else 'video-01')
d = json.load(open(os.path.join(VD, 'voiceover-sections.json')))
secs = d['sections'] if isinstance(d, dict) else d
N = len(secs)


def pcm(f):
    return subprocess.run(["ffmpeg", "-v", "error", "-i", f, "-ac", "1", "-ar", "16000", "-f", "s16le", "-"], capture_output=True).stdout


def toks(t):
    return re.sub(r"[^a-z' ]", " ", t.lower().replace("-", " ")).split()


def run(i):
    f = os.path.join(VD, 'voice', '%02d.mp3' % i)
    dec = Decoder(samprate=16000); dec.start_utt(); dec.process_raw(pcm(f), full_utt=True); dec.end_utt()
    return i, [(s.word, s.start_frame / 100.0, (s.end_frame + 1) / 100.0) for s in dec.seg()]


if __name__ == '__main__':
    with ProcessPoolExecutor(4) as ex:
        res = dict(ex.map(run, range(1, N + 1)))
    out = {}
    for i in range(1, N + 1):
        segs = [(re.sub(r"\(\d+\)$", "", w), a, b) for w, a, b in res[i] if not w.startswith("<") and not w.startswith("[")]
        got = [w for w, _, _ in segs]
        exp = toks(' '.join(secs[i - 1]['paras']))
        sm = difflib.SequenceMatcher(None, exp, got, autojunk=False)
        t = [None] * len(exp)
        for a, b, n in sm.get_matching_blocks():
            for k in range(n): t[a + k] = (segs[b + k][1], segs[b + k][2])
        known = [k for k in range(len(exp)) if t[k]]
        st = [None] * len(exp)
        for k in range(len(exp)):
            if t[k]: st[k] = t[k][0]; continue
            prv = max([j for j in known if j < k], default=None); nxt = min([j for j in known if j > k], default=None)
            if prv is None: st[k] = 0.0
            elif nxt is None: st[k] = t[prv][1]
            else: st[k] = t[prv][0] + (t[nxt][0] - t[prv][0]) * (k - prv) / (nxt - prv)
        out[str(i)] = {"words": exp, "start": [round(x, 2) for x in st], "matched": len(known) / len(exp)}
        print("%02d aligned %d/%d words (%.0f%%)" % (i, len(known), len(exp), 100 * len(known) / len(exp)))
    json.dump(out, open(os.path.join(VD, 'voice', 'word-timings.json'), 'w'))
