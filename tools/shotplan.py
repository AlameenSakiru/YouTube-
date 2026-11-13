"""Read a video's shot plan and check it against the voiceover text.

    python3 tools/shotplan.py video-02            # parse, number the images, check every cue
    python3 tools/shotplan.py video-02 --json     # also write video-02/shots-untimed.json

Plan lines: kind|style|cue|description, sections start with "== N".
kind: F (Flow image), F? (optional Flow image), F- (Flow image not used), G (graphic), R:<cue> (reuse the Flow image
that starts at <cue>), V1:<n> (reuse image n from video 1).
"""
import json, os, re, sys


def toks(t):
    return re.sub(r"[^a-z' ]", " ", t.lower().replace("-", " ")).split()


def sections_of(video_dir):
    d = json.load(open(os.path.join(video_dir, 'voiceover-sections.json')))
    return d['sections'] if isinstance(d, dict) else d


def parse(video_dir):
    shots, sec = [], None
    for line in open(os.path.join(video_dir, 'shot-plan.txt')):
        line = line.rstrip('\n')
        if not line or line.startswith('#'):
            continue
        if line.startswith('=='):
            sec = int(line[2:]); continue
        kind, style, cue, desc = line.split('|', 3)
        if kind == 'F-':   # Flow image made but not used: keeps the numbers of the images after it
            shots.append(dict(sec=sec, kind='X', style=style, cue=cue, desc=desc, optional=False)); continue
        opt = kind == 'F?'
        shots.append(dict(sec=sec, kind='F' if opt else kind, style=style, cue=cue, desc=desc, optional=opt))
    flow, fcue, g = 0, {}, 0
    for s in shots:
        if s['kind'] in ('F', 'X'):
            flow += 1; s['img'] = flow; fcue[s['cue']] = flow
    shots = [s for s in shots if s['kind'] != 'X']
    for s in shots:
        if s['kind'].startswith('R:'):
            s['img'] = fcue[s['kind'][2:]]; s['kind'] = 'R'
        elif s['kind'].startswith('V1:'):
            s['img'] = int(s['kind'][3:]); s['kind'] = 'V1'
        elif s['kind'] == 'G':
            g += 1; s['gid'] = 'G%02d' % g
    return shots


def check_cues(shots, sections):
    """Each cue must appear in its section's text, in plan order. Returns word index per shot."""
    problems = []
    for i, sec in enumerate(sections, 1):
        words = toks(' '.join(sec['paras']))
        k0 = 0
        for s in [s for s in shots if s['sec'] == i]:
            c = toks(s['cue'])
            found = next((k for k in range(k0, len(words) - len(c) + 1) if words[k:k + len(c)] == c), None)
            if found is None:
                problems.append('section %d: cue not found after word %d: "%s"' % (i, k0, s['cue']))
            else:
                s['word'] = found; k0 = found + 1
    return problems


if __name__ == '__main__':
    vd = sys.argv[1]
    shots = parse(vd)
    secs = sections_of(vd)
    probs = check_cues(shots, secs)
    words = sum(len(toks(' '.join(s['paras']))) for s in secs)
    n = lambda k: sum(1 for s in shots if s['kind'] == k)
    print('shots %d: Flow images %d, graphics %d, reuses %d, video 1 reuses %d' % (len(shots), n('F'), n('G'), n('R'), n('V1')))
    print('about %.1f s per shot at 150 words a minute' % (words / 150 * 60 / len(shots)))
    for i in range(1, len(secs) + 1):
        ws = len(toks(' '.join(secs[i - 1]['paras'])))
        k = sum(1 for s in shots if s['sec'] == i)
        print('  section %2d: %2d shots, %3d words, about %.1f s each' % (i, k, ws, ws / 150 * 60 / k))
    print('\n'.join(probs) or 'all cues found in order')
    if '--json' in sys.argv:
        json.dump(shots, open(os.path.join(vd, 'shots-untimed.json'), 'w'), indent=1)
