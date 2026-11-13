"""Assemble a video from the voiceover, the Flow images and the graphics.

VIDEO=video-02 python3 build.py ...   (default video-01). Per-video settings (pauses, name captions,
reuse crops, subtitle spellings, graphics set) live in VIDEO/edit_config.py.

python3 build.py plan              work out final timings (pauses, gaps, end card) -> build/timeline.json
python3 build.py images [N..]      render image shots (motion, name and place captions)
python3 build.py graphics          render graphics clips at their final lengths
python3 build.py audio             voice track with pauses, levelled to -14 LUFS
python3 build.py subs              subtitles (.srt) with correct spellings
python3 build.py video [OUT] [--to SECONDS]   join everything into the final file
"""
import sys, os, json, re, subprocess, hashlib, math
from multiprocessing import Pool
import numpy as np
from PIL import Image, ImageFilter

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
VIDEO = os.environ.get('VIDEO', 'video-01')
V = os.path.join(ROOT, VIDEO)
V1 = os.path.join(ROOT, 'video-01')
BUILD = os.environ.get('BUILD_DIR', os.path.join(V, 'build'))
GFX = os.path.join(ROOT, 'tools', 'gfx')
sys.path.insert(0, GFX)
W, H, FPS, SR = 1920, 1080, 30, 48000
GAP = 0.6          # silence between sections
END_CARD = 16.0    # seconds the end card stays up (YouTube end screens need 5 to 20)
CHANNEL = os.environ.get('CHANNEL_NAME', 'Great Lakes Files')  # shown in the corner of the whole video

# dramatic pauses: (section, words that end the line, extra seconds)
PAUSES = [
    (1, 'was a wet shoe', 0.6), (1, 'coming over his foot', 0.8), (1, 'on a lake', 0.6),
    (3, 'they went back', 0.5),
    (4, 'with four words', 0.6), (4, 'dozens down at montrose', 1.0),
    (5, 'then she disappeared', 0.8), (5, 'he was forty nine', 1.0),
    (6, 'never heard of', 0.5), (6, 'meteo tsunami', 0.8),
    (8, 'and it bounced', 0.6),
    (9, 'nobody was hurt', 1.2),
    (10, 'then the water', 1.0),
    (11, 'go up', 0.8),
    (12, 'didn\'t even get that', 0.8),
]

LOWER_THIRDS = {  # image number -> (title, subtitle)
    2: ('Herbert Riederer', 'State conservation officer, 24'),
    17: ('Joseph Pecararo', 'Lifeguard captain, 24'),
    18: ('North Avenue Beach', 'Chicago'),
    28: ('Montrose Harbor', 'Chicago'),
    41: ('Michigan City, Indiana', '8:10 a.m.'),
}

# reuse shots: description keyword -> (focus x, focus y, zoom start, zoom end)
REUSE_FOCUS = [
    ('fisherman being given', (0.66, 0.50, 1.45, 1.55)), ('closer crop of the wet shoe', (0.40, 0.55, 1.40, 1.55)),
    ('wide crop of the calm lake', (0.50, 0.55, 1.12, 1.04)), ('push-in on the calm', (0.56, 0.78, 1.20, 1.40)),
    ('officer with his ticket', (0.32, 0.45, 1.55, 1.65)), ('push-in on the swell', (0.48, 0.55, 1.10, 1.35)),
    ('the calm lake again', (0.40, 0.60, 1.25, 1.15)), ('dark storm line', (0.50, 0.35, 1.35, 1.45)),
    ('officers clearing', (0.30, 0.42, 1.45, 1.55)), ('surge over the breakwater', (0.70, 0.55, 1.35, 1.45)),
    ('calm lake under a bright', (0.50, 0.50, 1.25, 1.35)), ('beach with dunes', (0.30, 0.55, 1.35, 1.25)),
    ('storm moving away', (0.55, 0.40, 1.30, 1.40)), ('hurrying off the pier', (0.45, 0.50, 1.30, 1.40)),
    ('walking back out', (0.50, 0.50, 1.30, 1.40)), ('wet shoe again', (0.40, 0.55, 1.20, 1.35)),
]


def toks(s):
    return re.sub(r"[^a-z' ]", ' ', s.lower().replace('-', ' ')).split()


def load_audio(path):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', path, '-ac', '1', '-ar', str(SR), '-f', 'f32le', '-'],
                         capture_output=True).stdout
    return np.frombuffer(raw, np.float32).copy()


def silences(a, thresh_db=-38, min_len=0.08):
    hop = int(SR * 0.01); n = len(a) // hop
    rms = np.sqrt(np.mean(a[:n * hop].reshape(n, hop) ** 2, axis=1) + 1e-12)
    quiet = 20 * np.log10(rms) < thresh_db
    out = []; s = None
    for i, q in enumerate(list(quiet) + [False]):
        if q and s is None: s = i
        if not q and s is not None:
            if (i - s) * 0.01 >= min_len: out.append((s * 0.01, i * 0.01))
            s = None
    return out


# ---------------------------------------------------------------------------- plan
def n_sections():
    d = json.load(open(os.path.join(V, 'voiceover-sections.json')))
    return len(d['sections'] if isinstance(d, dict) else d)


def plan():
    shots = json.load(open(os.path.join(V, 'edit-plan.json')))
    al = json.load(open(os.path.join(V, 'voice', 'word-timings.json')))
    os.makedirs(BUILD, exist_ok=True)
    sections = []
    T = 0.35  # voice starts just after the first picture
    for sec in range(1, n_sections() + 1):
        a = load_audio(os.path.join(V, 'voice', '%02d.mp3' % sec))
        words, starts = al[str(sec)]['words'], al[str(sec)]['start']
        sil = silences(a)
        inserts = []
        for s_, phrase, extra in PAUSES:
            if s_ != sec: continue
            p = toks(phrase); k = None
            for i in range(len(words) - len(p) + 1):
                if words[i:i + len(p)] == p: k = i + len(p); break
            assert k is not None, (sec, phrase)
            target = starts[k] if k < len(starts) else len(a) / SR
            cands = [((s0 + s1) / 2, s0, s1) for s0, s1 in sil if s1 > target - 0.9 and s0 < target + 0.3]
            if not cands:
                at = len(a) / SR if k >= len(starts) else target - 0.1
            else:
                at = min(cands, key=lambda c: abs(c[0] - (target - 0.12)))[0]
            inserts.append((at, extra, k))
        inserts.sort()
        dur = len(a) / SR + sum(e for _, e, _ in inserts)
        sections.append(dict(sec=sec, start=T, raw=len(a) / SR, dur=dur, inserts=inserts))
        T += dur + GAP
    total_voice_end = sections[-1]['start'] + sections[-1]['dur']

    seq = []
    for s in shots:
        g = dict(s)
        g['T'] = 0.0 if (s['sec'] == 1 and s['t'] == 0) else shift(sections, s['sec'], s['t'], s['word'])
        seq.append(g)
    seq.sort(key=lambda g: g['T'])
    end_T = max(total_voice_end + 1.0, seq[-1]['T'] + END_CARD)
    for a_, b_ in zip(seq, seq[1:]):
        a_['F0'] = round(a_['T'] * FPS); a_['F1'] = round(b_['T'] * FPS)
    seq[-1]['F0'] = round(seq[-1]['T'] * FPS); seq[-1]['F1'] = round(end_T * FPS)
    for g in seq:
        g['n'] = g['F1'] - g['F0']; g['dur_final'] = g['n'] / FPS
    json.dump(dict(sections=sections, shots=seq, end=end_T), open(os.path.join(BUILD, 'timeline.json'), 'w'), indent=1)
    print('length %d:%02d, %d shots, shortest %.1fs, longest %.1fs' % (end_T // 60, end_T % 60, len(seq),
          min(g['dur_final'] for g in seq), max(g['dur_final'] for g in seq)))


def shift(sections, sec, t, word):
    """Where a moment in a section lands once the pauses are added. Pauses before this word push it later."""
    s = sections[sec - 1]
    before = [(at, e) for at, e, k in s['inserts'] if k <= word]
    if before: t = max(t, max(at for at, _ in before))
    return s['start'] + t + sum(e for _, e in before)


def timeline():
    return json.load(open(os.path.join(BUILD, 'timeline.json')))


# ---------------------------------------------------------------------------- image shots
_VIG = None


def vignette():
    global _VIG
    if _VIG is None:
        y, x = np.mgrid[0:H, 0:W]
        r = np.sqrt(((x - W / 2) / (W / 2)) ** 2 + ((y - H / 2) / (H / 2)) ** 2)
        _VIG = (1 - 0.28 * np.clip(r - 0.55, 0, 1) ** 1.5)[..., None].astype(np.float32)
    return _VIG


def overlay(lines_fn):
    """Render a transparent cairo overlay to an RGBA float array."""
    import cairo
    s = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H); cr = cairo.Context(s)
    lines_fn(cr)
    s.flush()
    buf = np.ndarray((H, W, 4), np.uint8, s.get_data()).astype(np.float32) / 255
    rgb = buf[:, :, 2::-1]; alpha = buf[:, :, 3:4]
    return rgb, alpha  # premultiplied


def watermark_png(path):
    """The channel name, small, in the bottom-right corner, readable on bright skies too."""
    import cairo
    from style import font, text, text_width, AMBER
    s = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H); cr = cairo.Context(s)
    font(cr, 'Inter', 24, bold=True)
    label = CHANNEL.upper(); tr = 4
    w = text_width(cr, label, tr); x = W - 48 - w; y = H - 40
    for dx, dy, al in ((2, 2, 0.45), (1, 1, 0.45)):
        text(cr, label, x + dx, y + dy, (0, 0, 0), al, tracking=tr)
    cr.set_source_rgba(*AMBER, 0.85); cr.rectangle(x - 18, y - 19, 5, 22); cr.fill()
    text(cr, label, x, y, (1, 1, 1), 0.72, tracking=tr)
    s.write_to_png(path)


def lower_third(title, sub):
    from style import font, text, INK, MUTED, AMBER, BG
    def draw(cr):
        cr.set_source_rgba(*BG, 0.72); cr.rectangle(0, H - 250, 900, 150); cr.fill()
        cr.set_source_rgba(*AMBER, 1); cr.rectangle(0, H - 250, 10, 150); cr.fill()
        font(cr, 'Inter Display', 56, bold=True); text(cr, title, 70, H - 172, INK, 1)
        font(cr, 'Inter', 34); text(cr, sub, 72, H - 124, MUTED, 1)
    return overlay(draw)


def motion(g):
    """(focus x, focus y, zoom0, zoom1) for a shot."""
    if g['kind'] in ('R', 'V1'):
        for key, m in REUSE_FOCUS:
            if key in g['desc'].lower(): return m
        return (0.5, 0.5, 1.30, 1.40)
    h = int(hashlib.md5(str(g['img']).encode()).hexdigest(), 16)
    zin = h % 2 == 0
    z = 0.06 + min(g['dur_final'], 12) * 0.006
    fx = 0.5 + ((h >> 3) % 7 - 3) * 0.015; fy = 0.5 + ((h >> 6) % 5 - 2) * 0.012
    return (fx, fy, 1.0 if zin else 1.0 + z, 1.0 + z if zin else 1.0)


def load_image(n, src=None):
    src = src or V
    cf = os.path.join(src, 'images', 'crops.json')
    crops = json.load(open(cf)) if os.path.exists(cf) else {}
    im = Image.open(os.path.join(src, 'images', '%03d.jpg' % n)).convert('RGB')
    if '%03d' % n in crops: im = im.crop(tuple(crops['%03d' % n]))
    w, h = im.size
    if w / h > 16 / 9: nw = int(h * 16 / 9); im = im.crop(((w - nw) // 2, 0, (w - nw) // 2 + nw, h))
    else: nh = int(w * 9 / 16); im = im.crop((0, (h - nh) // 2, w, (h - nh) // 2 + nh))
    im = im.resize((2560, 1440), Image.LANCZOS).filter(ImageFilter.UnsharpMask(2, 55, 2))
    return im


def render_image_shot(g):
    out = os.path.join(BUILD, 'clips', 'S%04d.mp4' % g['F0'])
    if os.path.exists(out) and os.path.getsize(out) > 1000: return out
    im = load_image(g['img'], V1 if g['kind'] == 'V1' else None); sw, sh = im.size
    fx, fy, z0, z1 = motion(g)
    lt = None
    if g['kind'] == 'F' and g['img'] in LOWER_THIRDS: lt = lower_third(*LOWER_THIRDS[g['img']])
    vig = vignette(); n = g['n']
    if lt is not None: lt = (lt[0][H - 260:H - 90, :920], lt[1][H - 260:H - 90, :920])
    p = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS),
                          '-i', '-', '-c:v', 'libx264', '-preset', 'medium', '-crf', '18', '-pix_fmt', 'yuv420p', out],
                         stdin=subprocess.PIPE)
    for i in range(n):
        f = i / max(n - 1, 1); f = f * f * (3 - 2 * f) * 0.5 + f * 0.5
        z = z0 + (z1 - z0) * f
        cw, ch = sw / z, sh / z
        cx = min(max(fx * sw, cw / 2), sw - cw / 2); cy = min(max(fy * sh, ch / 2), sh - ch / 2)
        fr = im.transform((W, H), Image.EXTENT, (cx - cw / 2, cy - ch / 2, cx + cw / 2, cy + ch / 2), Image.BILINEAR)
        a = np.asarray(fr, np.float32) * vig
        if lt is not None:
            t = i / FPS; al = min(1, max(0, (t - 0.6) / 0.4)) * min(1, max(0, (min(g['dur_final'], 5.5) - t) / 0.4))
            if al > 0:
                r = a[H - 260:H - 90, :920] / 255
                a[H - 260:H - 90, :920] = (r * (1 - lt[1] * al) + lt[0] * al) * 255
        if g['F0'] == 0: a *= min(1, i / (0.5 * FPS))
        p.stdin.write(np.clip(a, 0, 255).astype(np.uint8).tobytes())
    p.stdin.close(); p.wait()
    return out


def images(only=None):
    tl = timeline(); os.makedirs(os.path.join(BUILD, 'clips'), exist_ok=True)
    jobs = [g for g in tl['shots'] if g['kind'] in ('F', 'R', 'V1') and (not only or g.get('img') in only)]
    if only:
        for g in jobs:
            out = os.path.join(BUILD, 'clips', 'S%04d.mp4' % g['F0'])
            if os.path.exists(out): os.remove(out)
    with Pool(4) as pool:
        for k, out in enumerate(pool.imap_unordered(render_image_shot, jobs)):
            if k % 10 == 0: print('image clips', k + 1, '/', len(jobs), flush=True)


# ---------------------------------------------------------------------------- graphics
def render_graphic(g):
    out = os.path.join(BUILD, 'clips', 'S%04d.mp4' % g['F0'])
    if os.path.exists(out) and os.path.getsize(out) > 1000: return out
    import render as R
    d = g['dur_final']; last = g is None
    p = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS),
                          '-i', '-', '-c:v', 'libx264', '-preset', 'medium', '-crf', '18', '-pix_fmt', 'yuv420p', out],
                         stdin=subprocess.PIPE)
    for i in range(g['n']):
        fr = R.frame(g['gid'], i / FPS, d, i)
        if g.get('last'):
            fade = min(1, (g['n'] - 1 - i) / (1.2 * FPS)); fr = (fr * fade).astype(np.uint8)
        p.stdin.write(fr.tobytes())
    p.stdin.close(); p.wait()
    return out


def graphics():
    tl = timeline(); os.makedirs(os.path.join(BUILD, 'clips'), exist_ok=True)
    jobs = [g for g in tl['shots'] if g['kind'] == 'G']
    jobs[-1]['last'] = tl['shots'][-1]['F0'] == jobs[-1]['F0']
    with Pool(4) as pool:
        for k, out in enumerate(pool.imap_unordered(render_graphic, jobs)):
            if k % 10 == 0: print('graphic clips', k + 1, '/', len(jobs), flush=True)


# ---------------------------------------------------------------------------- audio
def audio():
    tl = timeline()
    total = np.zeros(int(tl['end'] * SR) + SR, np.float32)
    for s in tl['sections']:
        a = load_audio(os.path.join(V, 'voice', '%02d.mp3' % s['sec']))
        pieces, last = [], 0
        for at, extra, _ in s['inserts']:
            k = int(at * SR); pieces += [a[last:k], np.zeros(int(extra * SR), np.float32)]; last = k
        pieces.append(a[last:])
        b = np.concatenate(pieces)
        o = int(s['start'] * SR); total[o:o + len(b)] += b
    total = total[:int(tl['end'] * SR)]
    fade = int(1.2 * SR); total[-fade:] *= np.linspace(1, 0, fade)
    raw = os.path.join(BUILD, 'voice-raw.wav'); out = os.path.join(BUILD, 'voice.wav')
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'f32le', '-ar', str(SR), '-ac', '1', '-i', '-', raw], input=total.tobytes())
    m = subprocess.run(['ffmpeg', '-hide_banner', '-i', raw, '-af', 'loudnorm=I=-14:TP=-1.0:LRA=11:print_format=json', '-f', 'null', '-'],
                       capture_output=True, text=True).stderr
    js = json.loads(m[m.rindex('{'):m.rindex('}') + 1])
    af = ('loudnorm=I=-14:TP=-1.0:LRA=11:measured_I={input_i}:measured_TP={input_tp}:measured_LRA={input_lra}:'
          'measured_thresh={input_thresh}:offset={target_offset}:linear=true').format(**js)
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', raw, '-af', af + ',aresample=48000', '-ac', '2', out])
    print('audio', out)


# ---------------------------------------------------------------------------- subtitles
DISPLAY = [
    ('saysh', 'seiche'), ('Saysh', 'Seiche'), ('meteo-tsunamis', 'meteotsunamis'), ('meteo-tsunami', 'meteotsunami'),
    ('Meteo-tsunami', 'Meteotsunami'), ('Noah', 'NOAA'),
    ('June twenty-sixth, nineteen fifty-four', 'June 26, 1954'), ('July sixth, nineteen fifty-four', 'July 6, 1954'),
    ('July fourth, nineteen twenty-nine', 'July 4, 1929'), ('July fourth, two thousand three', 'July 4, 2003'),
    ('April, twenty eighteen', 'April 2018'), ('June, twenty twenty-five', 'June 2025'),
    ('Nineteen twenty-nine. Nineteen fifty-four. Two thousand three.', '1929. 1954. 2003.'),
    ('nineteen fifty-four', '1954'), ('Nineteen fifty-four', '1954'), ('twenty sixteen', '2016'),
    ('three hundred and seven miles', '307 miles'), ('one hundred and six', '106'), ('twelve hundred feet', '1,200 feet'),
    ('forty-five inch', '45-inch'), ('Twelve million', '12 million'), ('Seven thirty.', '7:30.'), ('Ten past eight.', '8:10.'),
    ('Nine thirty.', '9:30.'), ('sixty miles an hour', '60 miles an hour'),
]


# per-video settings override the video 1 defaults above
GFX_SET = 'video1'
_cfg = os.path.join(V, 'edit_config.py')
if os.path.exists(_cfg):
    exec(open(_cfg).read())
os.environ['GFX_SET'] = GFX_SET


def subs():
    tl = timeline(); al = json.load(open(os.path.join(V, 'voice', 'word-timings.json')))
    secs = json.load(open(os.path.join(V, 'voiceover-sections.json')))
    secs = secs['sections'] if isinstance(secs, dict) else secs
    cues = []
    for s in tl['sections']:
        sec = s['sec']; starts = al[str(sec)]['start']
        text_ = ' '.join(secs[sec - 1]['paras'])
        sents = re.findall(r'[^.?!]+(?:\.\.\.|[.?!]+)["”]?\s*', text_ + ' ')
        k = 0
        for se in sents:
            n = len(toks(se))
            t0 = starts[min(k, len(starts) - 1)]
            T0 = shift(tl['sections'], sec, t0, k)
            cues.append([T0, se.strip(), sec]); k += n
    for i, c in enumerate(cues):
        nxt = cues[i + 1][0] if i + 1 < len(cues) else tl['end'] - END_CARD + 4
        c.append(min(nxt - 0.05, c[0] + 7.0))
    def fmt(x):
        ms = int(round(x * 1000)); return '%02d:%02d:%02d,%03d' % (ms // 3600000, ms // 60000 % 60, ms // 1000 % 60, ms % 1000)
    lines = []; idx = 1
    for T0, s, sec, T1 in cues:
        for a, b in DISPLAY: s = s.replace(a, b)
        s = s.replace('...', '…')
        chunks = [s]
        if len(s) > 84:
            parts = re.split(r'(?<=,) ', s); chunks = []; cur = ''
            for p_ in parts:
                if len(cur) + len(p_) > 84 and cur: chunks.append(cur); cur = p_
                else: cur = (cur + ' ' + p_).strip()
            chunks.append(cur)
        span = (T1 - T0) / sum(len(c) for c in chunks); t = T0
        for c in chunks:
            d = span * len(c); lines.append('%d\n%s --> %s\n%s\n' % (idx, fmt(t), fmt(t + d - 0.02), c)); idx += 1; t += d
    out = os.path.join(V, 'subtitles-en.srt'); open(out, 'w').write('\n'.join(lines))
    print('subtitles', idx - 1, 'cues ->', out)


# ---------------------------------------------------------------------------- final
def video(out, to=None):
    tl = timeline()
    lst = os.path.join(BUILD, 'concat.txt')
    with open(lst, 'w') as f:
        for g in tl['shots']:
            if to and g['T'] >= to: break
            f.write("file '%s'\n" % os.path.join(BUILD, 'clips', 'S%04d.mp4' % g['F0']))
    vid = os.path.join(BUILD, 'video-only.mp4')
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', lst, '-c', 'copy', vid], check=True)
    wm = os.path.join(BUILD, 'watermark.png'); watermark_png(wm)
    end_card_start = tl['shots'][-1]['T']
    cmd = ['ffmpeg', '-v', 'error', '-y', '-i', vid, '-i', wm, '-i', os.path.join(BUILD, 'voice.wav'),
           '-filter_complex', "[0:v][1:v]overlay=0:0:enable='lt(t,%.2f)'[v]" % end_card_start,
           '-map', '[v]', '-map', '2:a', '-c:v', 'libx264', '-preset', 'medium', '-crf', '18', '-pix_fmt', 'yuv420p',
           '-c:a', 'aac', '-b:a', '192k', '-shortest', '-movflags', '+faststart']
    if to: cmd += ['-t', str(to)]
    subprocess.run(cmd + [out], check=True)
    print('wrote', out)


if __name__ == '__main__':
    m = sys.argv[1]
    if m == 'plan': plan()
    elif m == 'images': images([int(x) for x in sys.argv[2:]] or None)
    elif m == 'graphics': graphics()
    elif m == 'audio': audio()
    elif m == 'subs': subs()
    elif m == 'video':
        to = None; args = sys.argv[2:]
        if '--to' in args: i = args.index('--to'); to = float(args[i + 1]); args = args[:i] + args[i + 2:]
        video(args[0] if args else os.path.join(V, VIDEO + '.mp4'), to)
