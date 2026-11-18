"""Sound bed for the 'casefile' format (video 3): ambience that follows the pictures, a low drone, and effects
on the graphics, ducked under the voice. Writes BUILD/bed.wav and BUILD/mix.wav (voice + bed at -14 LUFS).

Everything is synthesised here (ffmpeg noise generators and numpy), so there are no outside sound files to license.
"""
import os, json, subprocess, math
import numpy as np

SR = 24000      # the bed has no high detail; the mix is upsampled to 48 kHz
CR = 100        # control rate for envelopes


def noise(kind, dur, filt, seed):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-f', 'lavfi', '-i', f'anoisesrc=color={kind}:sample_rate={SR}:seed={seed}:duration={dur}',
                          '-af', filt, '-ac', '1', '-f', 'f32le', '-'], capture_output=True, check=True).stdout
    a = np.frombuffer(raw, np.float32).copy()
    return a / (np.sqrt(np.mean(a ** 2)) + 1e-9)


def smooth_steps(times, values, n, tau=1.2):
    """Piecewise-constant targets at `times` (s) -> smoothed control curve of length n (at CR)."""
    tgt = np.zeros(n, np.float32)
    for k, (t0, v) in enumerate(zip(times, values)):
        t1 = times[k + 1] if k + 1 < len(times) else n / CR
        tgt[int(t0 * CR):int(t1 * CR)] = v
    out = np.empty_like(tgt); a = 1 / (tau * CR); y = tgt[0]
    for i in range(n):
        y += (tgt[i] - y) * a; out[i] = y
    return out


def up(ctrl, n):
    return np.interp(np.arange(n) / SR * CR, np.arange(len(ctrl)), ctrl).astype(np.float32)


def env_exp(n, tau):
    return np.exp(-np.arange(n) / (tau * SR)).astype(np.float32)


def ping(f=1150, dur=2.6):
    n = int(dur * SR); t = np.arange(n) / SR
    s = np.sin(2 * np.pi * f * t) * env_exp(n, 0.35) + 0.5 * np.sin(2 * np.pi * f * 1.5 * t) * env_exp(n, 0.12)
    d = int(0.42 * SR); s[d:] += 0.35 * s[:-d]                      # one echo off the bottom
    return (s * np.minimum(1, t / 0.004)).astype(np.float32)


def boom(dur=2.2):
    n = int(dur * SR); t = np.arange(n) / SR
    f = 55 * np.exp(-t * 1.4) + 30
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * env_exp(n, 0.55)
    s += np.random.default_rng(5).normal(0, 1, n) * env_exp(n, 0.05) * 0.25
    return (s * np.minimum(1, t / 0.006)).astype(np.float32)


def bell_tone(f=196, dur=6.0):
    n = int(dur * SR); t = np.arange(n) / SR; s = np.zeros(n, np.float32)
    for ratio, amp, tau in ((0.5, 0.6, 3.5), (1.0, 1.0, 2.6), (1.19, 0.5, 1.8), (1.5, 0.45, 1.6), (2.0, 0.35, 1.2), (2.74, 0.2, 0.7)):
        s += amp * np.sin(2 * np.pi * f * ratio * t) * env_exp(n, tau)
    return (s * np.minimum(1, t / 0.003)).astype(np.float32)


def click(dur=0.06):
    n = int(dur * SR); t = np.arange(n) / SR
    return (np.random.default_rng(9).normal(0, 1, n) * env_exp(n, 0.006) + np.sin(2 * np.pi * 2400 * t) * env_exp(n, 0.01)).astype(np.float32)


def tick(dur=0.05):
    n = int(dur * SR); t = np.arange(n) / SR
    return (np.sin(2 * np.pi * 1800 * t) * env_exp(n, 0.008)).astype(np.float32)


def place(buf, s, t0, gain):
    i = int(t0 * SR)
    if i >= len(buf): return
    j = min(len(buf), i + len(s)); buf[i:j] += s[:j - i] * gain


def drone(n):
    t = np.arange(n, dtype=np.float64) / SR
    s = np.zeros(n, np.float64)
    for f, amp, lfo in ((73.42, 0.55, 0.031), (110.0, 0.35, 0.023), (146.83, 0.22, 0.017), (174.61, 0.12, 0.041)):
        s += amp * np.sin(2 * np.pi * f * t + 0.3 * np.sin(2 * np.pi * 0.05 * t)) * (0.65 + 0.35 * np.sin(2 * np.pi * lfo * t))
    return (s / 1.2).astype(np.float32)


# ------------------------------------------------------------------ which ambience goes with each shot
STORM = ('night', 'storm', 'waves', 'wave', 'snow', 'sea')
INSIDE = ('pilothouse', 'engine room', 'mess', 'hold', 'desk', 'classroom', 'church', 'museum', 'students')


def amb(style, desc):
    d = desc.lower()
    if style == 'U': return (0.0, 0.05, 1.0)
    if any(w in d for w in INSIDE): return (0.25, 0.1, 0.12)
    if style in ('S', 'F') and any(w in d for w in STORM): return (1.0, 0.9, 0.0)
    if style in ('S', 'F'): return (0.4, 0.5, 0.0)
    if style == 'D': return (0.3, 0.45, 0.0)
    return (0.18, 0.5, 0.0)


def events(g):
    """Effects for a graphic: list of (seconds after its start, kind)."""
    gid, d, desc = g['gid'], g['dur_final'], g['desc'].lower()
    ev = []
    if any(w in desc for w in ('map', 'chart', 'cutaway', 'relief')): ev.append((0.25, 'ping'))
    hits = {'G02': [0.1], 'G20': [0.0, 0.6], 'G26': [0.1, 2.4], 'G46': [0.2], 'G59': [0.8], 'G42': [3.2], 'G55': [3.4],
            'G18': [2.4], 'G19': [3.0], 'G56': [4.0], 'G61': [1.2, 5.4], 'G32': [2.2], 'G50': [5.6], 'G60': [3.6],
            'G44': [2.8], 'G09': [2.2], 'G04': [2.0], 'G22': [2.0], 'G34': [6.0], 'G29': [1.2]}
    for x in hits.get(gid, []):
        ev.append((x, 'ping' if gid in ('G09', 'G04', 'G22', 'G34', 'G29') else 'boom'))
    if gid in ('G08', 'G71'): ev.append((min(2.2, d * 0.45), 'click'))
    if gid == 'G47': ev += [(1.3, 'click'), (3.2, 'click')]
    if gid == 'G63':
        ev.append((0.0, 'bell'))
        for k in range(29): ev.append((0.2 + k * max(0.06, (d - 0.9) / 29), 'tick'))
    return ev


def make(tl, V, BUILD):
    T = tl['end']; n = int(T * SR) + SR; nc = int(T * CR) + CR
    shots = tl['shots']
    styles = {s['img']: s['style'] for s in shots if s['kind'] == 'F'}
    times, wv, wa, ru = [], [], [], []
    last = (0.2, 0.4, 0.0)
    for g in shots:
        if g['kind'] in ('F', 'R', 'V1'):
            st = g['style'] if g['kind'] == 'F' else styles.get(g.get('img'), 'B')
            desc = g['desc'] if g['kind'] == 'F' else next((s['desc'] for s in shots if s['kind'] == 'F' and s.get('img') == g.get('img')), '')
            a = amb(st, desc); last = a
        else:
            a = (last[0] * 0.45, last[1] * 0.45, max(last[2] * 0.6, 0.25))
        if g['kind'] == 'R' and 'single light fading' in g['desc'].lower():
            a = (0.0, 0.0, 0.15)          # "Then nothing": the storm drops out
        times.append(g['T']); wv.append(a[0]); wa.append(a[1]); ru.append(a[2])
    c_w = smooth_steps(times, wv, nc, 1.0); c_a = smooth_steps(times, wa, nc, 1.2); c_r = smooth_steps(times, ru, nc, 0.8)

    print('sound: noise beds', flush=True)
    dur = '%.2f' % (n / SR)
    wind = noise('pink', dur, 'highpass=f=250,lowpass=f=1800,bandpass=f=700:width_type=o:w=2', 3)
    gust = up(np.clip(0.55 + 0.45 * np.sin(np.arange(nc) / CR * 2 * np.pi * 0.07) * np.sin(np.arange(nc) / CR * 2 * np.pi * 0.023 + 1), 0.1, 1), n)
    waves = noise('brown', dur, 'lowpass=f=520,highpass=f=40', 4)
    tt = np.arange(nc) / CR
    swell = up((0.5 + 0.5 * np.sin(2 * np.pi * tt / 6.3)) ** 2 * 0.8 + 0.2, n)
    rumble = noise('brown', dur, 'lowpass=f=140,highpass=f=25', 5)

    bed = (wind[:n] * up(c_w, n) * gust * 0.05 + waves[:n] * up(c_a, n) * swell * 0.07 + rumble[:n] * up(c_r, n) * 0.08)
    bed += drone(n) * 0.022

    fx = np.zeros(n, np.float32)
    P, B, BL, C, TK = ping(), boom(), bell_tone(), click(), tick()
    for g in shots:
        if g['kind'] == 'G':
            for dt, kind in events(g):
                place(fx, {'ping': P, 'boom': B, 'bell': BL, 'click': C, 'tick': TK}[kind], g['T'] + dt,
                      {'ping': 0.05, 'boom': 0.16, 'bell': 0.08, 'click': 0.12, 'tick': 0.03}[kind])
        elif g['kind'] == 'F' and 'church' in g['desc'].lower():
            place(fx, BL, g['T'] + 0.2, 0.07)

    # duck the ambience (not the effects) under the voice
    vraw = subprocess.run(['ffmpeg', '-v', 'error', '-i', os.path.join(BUILD, 'voice.wav'), '-ac', '1', '-ar', str(SR), '-f', 'f32le', '-'],
                          capture_output=True, check=True).stdout
    v = np.frombuffer(vraw, np.float32)
    hop = SR // CR; m = min(len(v) // hop, nc)
    rms = np.sqrt(np.mean(v[:m * hop].reshape(m, hop) ** 2, 1))
    on = np.clip((20 * np.log10(rms + 1e-6) + 45) / 15, 0, 1)
    duck = np.ones(nc, np.float32); y = 0.0
    for i in range(m):
        k = 0.25 if on[i] > y else 0.03            # fast attack, slow release
        y += (on[i] - y) * k; duck[i] = 1 - 0.62 * y
    bed = bed * up(duck, n) + fx
    fade = int(2.0 * SR); bed[:fade] *= np.linspace(0, 1, fade); bed[-fade:] *= np.linspace(1, 0, fade)
    bed = bed[:int(T * SR)]
    out = os.path.join(BUILD, 'bed.wav')
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'f32le', '-ar', str(SR), '-ac', '1', '-i', '-', '-ar', '48000', '-ac', '2', out],
                   input=bed.astype(np.float32).tobytes(), check=True)
    print('sound: mixing', flush=True)
    raw = os.path.join(BUILD, 'mix-raw.wav'); mix = os.path.join(BUILD, 'mix.wav')
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', os.path.join(BUILD, 'voice.wav'), '-i', out, '-filter_complex',
                    '[0:a][1:a]amix=inputs=2:normalize=0:duration=first[a]', '-map', '[a]', raw], check=True)
    meas = subprocess.run(['ffmpeg', '-hide_banner', '-i', raw, '-af', 'loudnorm=I=-14:TP=-1.0:LRA=11:print_format=json', '-f', 'null', '-'],
                          capture_output=True, text=True).stderr
    js = json.loads(meas[meas.rindex('{'):meas.rindex('}') + 1])
    af = ('loudnorm=I=-14:TP=-1.0:LRA=11:measured_I={input_i}:measured_TP={input_tp}:measured_LRA={input_lra}:'
          'measured_thresh={input_thresh}:offset={target_offset}:linear=true').format(**js)
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', raw, '-af', af + ',aresample=48000', '-ac', '2', mix], check=True)
    print('sound: wrote', mix)
