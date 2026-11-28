"""Every graphic in video 6 (the Henry B. Smith), keyed by its G number in video-06/edit-plan.json.
Selected by render.py when GFX_SET=video6.

Built from the case-file blocks of videos 3 to 5 with its own look: storm navy, frost blue for the lake and the
coasts, lamplight amber for the ship and her clues, a cold green tick for what the wreck proved. Maps around
Marquette use the full-resolution coastline. The bottom of the frame stays clear for the captions.
Places marked "approximate" on screen are approximate: nobody knows exactly where she was last seen.
"""
import math, os, json, re
import numpy as np
import cairo
from PIL import Image, ImageFilter, ImageEnhance
from style import *
import maps
from maps import View, LAKES, ISLANDS, UPPER, COUNTRIES, STATES, basemap, _poly, _load, GREAT_LAKES
import video3 as v3

G = {}
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
V6 = os.path.join(ROOT, 'video-06')

OR = (1.0, 0.66, 0.23)          # lamplight amber: the ship, her clues
CY = (0.70, 0.86, 0.97)         # frost blue: the lake, labels
WH = (0.96, 0.95, 0.92)
GR = (0.72, 0.76, 0.80)
RD = (1.0, 0.36, 0.30)          # a clue that was wrong
GN = (0.48, 0.88, 0.62)         # what the wreck proved
NV = (0.03, 0.05, 0.09)
ORE = (0.62, 0.20, 0.13)

_swap = {v3.OR: OR, v3.CY: CY}
v3.OR, v3.CY, v3.WH, v3.GR = OR, CY, WH, GR
for _f in list(vars(v3).values()):
    if callable(_f) and getattr(_f, '__module__', '') == 'video3' and getattr(_f, '__defaults__', None):
        _f.__defaults__ = tuple(_swap.get(x, x) if isinstance(x, tuple) else x for x in _f.__defaults__)
v3.hud.__defaults__ = ('FILE 06 · HENRY B. SMITH', None, 1.0)
HEAD, MONO, BODY = v3.HEAD, v3.MONO, v3.BODY


# ---------------------------------------------------------------- the picture behind each graphic
def _prev_images():
    """gid -> (folder, image number) of the picture just before it (reused pictures come from their own video)."""
    p = os.path.join(V6, 'edit-plan.json')
    if not os.path.exists(p): p = os.path.join(V6, 'shots-untimed.json')
    try:
        plan = json.load(open(p))
    except Exception:
        return {}
    out, prev = {}, ('video-06', 1)
    for s in plan:
        if s['kind'] == 'G': out[s['gid']] = prev
        elif re.match(r'V\d$', s['kind']): prev = ('video-%02d' % int(s['kind'][1]), s['img'])
        elif s.get('img'): prev = ('video-06', s['img'])
    return out


BACK = _prev_images()
BACK.update({'G52': ('video-06', 60), 'G50': ('video-06', 58)})
_SURF = {}


def _src(folder, n):
    return os.path.join(ROOT, folder, 'images', '%03d.jpg' % n)


def _bg(folder, n, blur, dark):
    d = os.path.join(V6, 'build', 'bg'); os.makedirs(d, exist_ok=True)
    out = os.path.join(d, 'v6-%s-%03d-%d-%d.png' % (folder[-2:], n, blur, int(dark * 100)))
    if not os.path.exists(out):
        src = os.path.join(ROOT, folder)
        cf = os.path.join(src, 'images', 'crops.json')
        crops = json.load(open(cf)) if os.path.exists(cf) else {}
        im = Image.open(_src(folder, n)).convert('RGB')
        if '%03d' % n in crops: im = im.crop(tuple(crops['%03d' % n]))
        w, h = im.size
        if w / h > 16 / 9: nw = int(h * 16 / 9); im = im.crop(((w - nw) // 2, 0, (w - nw) // 2 + nw, h))
        else: nh = int(w * 9 / 16); im = im.crop((0, (h - nh) // 2, w, (h - nh) // 2 + nh))
        im = im.resize((2112, 1188), Image.LANCZOS)
        if blur: im = im.filter(ImageFilter.GaussianBlur(blur))
        im = ImageEnhance.Brightness(im).enhance(dark)
        a = np.asarray(im, np.float32) * np.array([0.94, 0.98, 1.06])
        tmp = out + '.%d.tmp.png' % os.getpid()
        Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).save(tmp)
        os.replace(tmp, out)
    return out


def backdrop(cr, gid, t, d, blur=14, dark=0.56, n=None):
    folder, img = ('video-06', n) if n else BACK.get(gid, ('video-06', 3))
    if not os.path.exists(_src(folder, img)):         # pictures not made yet: a plain storm-navy ground
        g = cairo.LinearGradient(0, 0, 0, H); g.add_color_stop_rgb(0, 0.07, 0.10, 0.16); g.add_color_stop_rgb(1, 0.02, 0.03, 0.06)
        cr.set_source(g); cr.paint()
    else:
        key = (folder, img, blur, dark)
        if key not in _SURF: _SURF[key] = cairo.ImageSurface.create_from_png(_bg(folder, img, blur, dark))
        s = _SURF[key]
        z = 1.0 + 0.05 * (t / max(d, 0.1))
        cr.save(); cr.translate(W / 2, H / 2); cr.scale(z * W / 2112, z * H / 1188)
        cr.translate(-2112 / 2, -1188 / 2); cr.set_source_surface(s, 0, 0); cr.paint(); cr.restore()
    g = cairo.RadialGradient(W / 2, H / 2, 100, W / 2, H / 2, W * 0.7)
    g.add_color_stop_rgba(0, 0.01, 0.02, 0.05, 0.34); g.add_color_stop_rgba(0.6, 0.01, 0.02, 0.05, 0.22)
    g.add_color_stop_rgba(1, 0.01, 0.02, 0.05, 0.58)
    cr.set_source(g); cr.paint()


v3.backdrop = backdrop
from video3 import (hud, head, mono, body, bar, box, stamp, count, sonar, cursor, bell, thumb, sub_button,
                    comment_box, dim_v, miles_line, card_quote, card_lines)


def reg(gid):
    def deco(fn):
        G[gid] = fn; return fn
    return deco


def tag(cr, s, x, y, col, a, size=22, align='left'):
    if a <= 0: return
    font(cr, MONO, size, bold=True); w = text_width(cr, s, 2)
    if align == 'right': x -= w
    elif align == 'center': x -= w / 2
    box(cr, x - 12, y - size - 6, w + 24, size + 20, 6, fill=(0.02, 0.04, 0.07), fa=0.85 * a)
    text(cr, s, x, y, col, a, tracking=2)


def tick(cr, x, y, s, col, a, ok=True):
    """A drawn tick or cross (the fonts have no reliable glyphs for them)."""
    if a <= 0: return
    cr.save(); cr.translate(x, y); cr.scale(s, s)
    cr.set_source_rgba(*col, a); cr.set_line_width(9); cr.set_line_cap(cairo.LINE_CAP_ROUND); cr.set_line_join(cairo.LINE_JOIN_ROUND)
    if ok: cr.move_to(-22, 2); cr.line_to(-6, 18); cr.line_to(24, -20)
    else: cr.move_to(-18, -18); cr.line_to(18, 18); cr.move_to(18, -18); cr.line_to(-18, 18)
    cr.stroke(); cr.restore()


# ---------------------------------------------------------------- the coast around Marquette, full resolution
def _near(a, la0=46.3, la1=47.75, lo0=-88.6, lo1=-86.3):
    return ((a[:, 1] > la0) & (a[:, 1] < la1) & (a[:, 0] > lo0) & (a[:, 0] < lo1)).any()


_FULL = _load('gshhs', 'f')
M_LAKES = [a for lvl, a in _FULL if lvl == 2 and len(a) > 40 and _near(a)]
M_ISL = [a for lvl, a in _FULL if lvl == 3 and _near(a)]
del _FULL

PT = {
    'marquette': (46.5436, -87.3954), 'wreck': (46.914, -87.333), 'keweenaw': (47.42, -87.70),
    'chocolay': (46.505, -87.345), 'shot': (46.497, -87.165), 'laughing': (46.512, -87.015),
    'note': (46.545, -87.140), 'seen': (46.62, -87.30), 'fitz': (46.9985, -85.11),
}
NEAR = View(46.70, -87.30, 1450)        # Marquette and the water north of it
WIDE = View(46.95, -87.45, 760)         # Marquette to the Keweenaw
SUP = View(47.55, -87.9, 205)           # the whole lake


def grid_m(cr, v, a=0.14):
    cr.set_line_width(1); cr.set_source_rgba(*CY, a)
    for lat in np.arange(45.0, 49.5, 0.1 if v.scale > 1000 else 0.25):
        _, y = v.xy(lat, -87); cr.move_to(0, y); cr.line_to(W, y); cr.stroke()
    for lon in np.arange(-92.0, -84.0, 0.2 if v.scale > 1000 else 0.5):
        x, _ = v.xy(47, lon); cr.move_to(x, 0); cr.line_to(x, H); cr.stroke()


def coast_map(cr, v, t, label='FILE 06 · MARQUETTE, MICHIGAN', names=True):
    cr.set_source_rgb(*LAND); cr.paint()
    for a in M_LAKES:
        _poly(cr, v.pts(a)); cr.set_source_rgb(*WATER); cr.fill()
    for a in M_ISL:
        _poly(cr, v.pts(a)); cr.set_source_rgb(*LAND); cr.fill()
    cr.set_line_width(1.8); cr.set_source_rgba(*COAST, 0.85)
    for a in M_LAKES + M_ISL:
        _poly(cr, v.pts(a)); cr.stroke()
    g = cairo.RadialGradient(W / 2, H / 2, 300, W / 2, H / 2, W * 0.75)
    g.add_color_stop_rgba(0, 0, 0, 0, 0); g.add_color_stop_rgba(1, 0, 0.01, 0.04, 0.55)
    cr.set_source(g); cr.paint()
    grid_m(cr, v)
    if names:
        font(cr, MONO, 22)
        for s, ll in (('LAKE SUPERIOR', (46.98, -86.95)), ('MICHIGAN', (46.40, -87.55)), ('KEWEENAW PENINSULA', (47.20, -88.25))):
            x, y = v.xy(*ll)
            if 120 < x < W - 300 and 140 < y < H - 220:
                text(cr, s, x, y, CY if 'LAKE' in s else WH, 0.6, 'center', tracking=5)
    hud(cr, t, label, None)


def lake_map(cr, v, t, label):
    basemap(cr, v, labels=False)
    g = cairo.RadialGradient(W / 2, H / 2, 300, W / 2, H / 2, W * 0.75)
    g.add_color_stop_rgba(0, 0, 0, 0, 0); g.add_color_stop_rgba(1, 0, 0.01, 0.04, 0.5)
    cr.set_source(g); cr.paint()
    hud(cr, t, label, None)


def mark(cr, v, key, t, start, lab, col=WH, dx=22, dy=-14, size=32, align='left', ring=False, sub=None):
    a = ramp(t, start, 0.4)
    if a <= 0: return
    x, y = v.xy(*PT[key])
    if ring: sonar(cr, x, y, t - start, col, a=a, rmax=100)
    else: circle(cr, x, y, 9, col, a); circle(cr, x, y, 17, col, 0.45 * a, fill=False, width=2)
    font(cr, HEAD, size)
    if align == 'left': text(cr, lab, x + dx, y + dy, col, a)
    else: text(cr, lab, x - dx, y + dy, col, a, 'right')
    if sub: tag(cr, sub, x + dx + 2 if align == 'left' else x - dx - 2, y + dy + 44, WH, a, 20, align)


def marquette(cr, v, t, start=0.0, align='right'):
    mark(cr, v, 'marquette', t, start, 'MARQUETTE', WH, dx=24, dy=40, align=align)


def ll_path(v, pts):
    return [v.xy(*p) for p in pts]


# ---------------------------------------------------------------- the ship
def smith_side(cr, x0, x1, deck, keel, a=1.0, hatches=True, color=(0.10, 0.10, 0.12)):
    """The Henry B. Smith in side view: bow on the right, pilothouse and mast forward, funnel aft."""
    L = x1 - x0
    cr.set_source_rgba(*color, a)
    cr.move_to(x0 + 18, deck); cr.line_to(x1 - 24, deck - 6); cr.line_to(x1 + 6, deck - 14); cr.line_to(x1 - 22, keel)
    cr.line_to(x0 + 24, keel); cr.curve_to(x0 + 4, keel - 6, x0, deck + 20, x0 + 18, deck); cr.close_path(); cr.fill_preserve()
    cr.set_source_rgba(*CY, 0.45 * a); cr.set_line_width(2); cr.stroke()
    cr.set_source_rgba(0.42, 0.13, 0.10, a); cr.rectangle(x0 + 16, keel - (keel - deck) * 0.28, L - 44, (keel - deck) * 0.26); cr.fill()
    cr.set_source_rgba(0.92, 0.91, 0.86, a)
    ph = (keel - deck)
    cr.rectangle(x1 - L * 0.09, deck - ph * 0.55, L * 0.06, ph * 0.55); cr.fill()            # forward cabins
    cr.rectangle(x1 - L * 0.085, deck - ph * 0.95, L * 0.05, ph * 0.4); cr.fill()            # pilothouse
    cr.set_source_rgba(0.75, 0.75, 0.72, a); cr.set_line_width(2)
    cr.move_to(x1 - L * 0.09, deck - ph * 0.95); cr.line_to(x1 - L * 0.03, deck - ph * 0.95); cr.stroke()   # open bridge rail
    cr.set_source_rgba(0.85, 0.84, 0.80, a); cr.set_line_width(4)
    mx = x1 - L * 0.13; cr.move_to(mx, deck); cr.line_to(mx, deck - ph * 2.1); cr.stroke()        # forward mast
    cr.set_source_rgba(0.92, 0.91, 0.86, a)
    cr.rectangle(x0 + L * 0.03, deck - ph * 0.6, L * 0.13, ph * 0.6); cr.fill()               # aft deckhouse
    cr.set_source_rgba(0.08, 0.08, 0.09, a); cr.rectangle(x0 + L * 0.07, deck - ph * 1.45, L * 0.03, ph * 0.85); cr.fill_preserve()  # funnel
    cr.set_source_rgba(*CY, 0.45 * a); cr.set_line_width(2); cr.stroke()
    cr.set_source_rgba(0.85, 0.84, 0.80, a); cr.set_line_width(3)
    ax = x0 + L * 0.15; cr.move_to(ax, deck - ph * 0.6); cr.line_to(ax, deck - ph * 1.7); cr.stroke()
    if hatches:
        cr.set_source_rgba(0.40, 0.42, 0.44, a)
        n = 16; hx0, hx1 = x0 + L * 0.19, x1 - L * 0.16
        for k in range(n):
            hx = hx0 + k * (hx1 - hx0) / n; cr.rectangle(hx, deck - 5, (hx1 - hx0) / n - 8, 5); cr.fill()


def smith_top(cr, cx, cy, L, Wd, t, closed_until=None, a=1.0):
    """The Smith seen from above with her 32 hatches. closed_until: how many hatches (from the bow) are covered."""
    x0, x1 = cx - L / 2, cx + L / 2
    cr.set_source_rgba(0.12, 0.12, 0.14, a)
    cr.move_to(x0 + 30, cy - Wd / 2); cr.line_to(x1 - 70, cy - Wd / 2); cr.curve_to(x1 - 10, cy - Wd / 2, x1, cy - 10, x1, cy)
    cr.curve_to(x1, cy + 10, x1 - 10, cy + Wd / 2, x1 - 70, cy + Wd / 2); cr.line_to(x0 + 30, cy + Wd / 2)
    cr.curve_to(x0, cy + Wd / 2, x0, cy - Wd / 2, x0 + 30, cy - Wd / 2); cr.close_path(); cr.fill_preserve()
    cr.set_source_rgba(*CY, 0.5 * a); cr.set_line_width(2); cr.stroke()
    cr.set_source_rgba(0.9, 0.9, 0.86, a)
    cr.rectangle(x1 - 120, cy - Wd * 0.32, 70, Wd * 0.64); cr.fill()           # pilothouse and cabins
    cr.rectangle(x0 + 28, cy - Wd * 0.38, 120, Wd * 0.76); cr.fill()            # aft deckhouse
    cr.set_source_rgba(0.07, 0.07, 0.08, a); circle(cr, x0 + 90, cy, 13, (0.07, 0.07, 0.08), a)
    hx0, hx1 = x0 + 175, x1 - 140
    n = 32; step = (hx1 - hx0) / n; hw = step * 0.62
    for k in range(n):
        hx = hx1 - (k + 1) * step + (step - hw) / 2                                  # counted from the bow
        covered = closed_until is not None and k < closed_until
        if covered:
            cr.set_source_rgba(0.55, 0.57, 0.58, a); cr.rectangle(hx, cy - Wd * 0.3, hw, Wd * 0.6); cr.fill()
        else:
            cr.set_source_rgba(0.0, 0.0, 0.0, a); cr.rectangle(hx, cy - Wd * 0.3, hw, Wd * 0.6); cr.fill()
            cr.set_source_rgba(*OR, 0.55 * a); cr.set_line_width(1.5); cr.rectangle(hx, cy - Wd * 0.3, hw, Wd * 0.6); cr.stroke()
    return hx0, hx1


# ---------------------------------------------------------------- side-scan sonar
_SON = {}


def _sonar_tex(h=2200, w=1400, seed=6):
    """A side-scan sonar strip: amber speckle on black, a dark water column down the middle, the wreck in two
    pieces with their acoustic shadows. Not real data: an illustration of what the searchers' screen shows."""
    if 'tex' in _SON: return _SON['tex']
    rng = np.random.default_rng(seed)
    y = np.arange(h)[:, None]; x = np.arange(w)[None, :]
    dist = np.abs(x - w / 2) / (w / 2)
    base = 0.35 + 0.45 * dist + 0.12 * np.sin(y / 37.0) * np.sin(x / 53.0)
    noise = rng.random((h, w)) ** 2
    img = base * (0.45 + 0.75 * noise)
    img[:, int(w * 0.47):int(w * 0.53)] *= 0.05                                      # the water column under the boat
    # the wreck: two long bright shapes on the right-hand channel, with shadows beyond them
    def piece(yc, x0, x1, th, bow):
        """One section of hull lying across the track: a bright return, tapered at the bow, with its shadow."""
        for yy in range(int(yc - th), int(yc + th)):
            f = 1 - abs(yy - yc) / th
            xe = x1 - (int((1 - f) * 70) if bow else 0)
            xs = x0 + int((yy - yc) * 0.35)
            img[yy, xs:xe] = np.maximum(img[yy, xs:xe], 0.85 + 0.35 * f * (0.7 + 0.3 * rng.random(xe - xs)))
            img[yy, xe:xe + 190] *= np.linspace(0.05, 0.6, 190)                     # acoustic shadow
    piece(990, 840, 1030, 48, True)
    piece(1190, 850, 1020, 44, False)
    for k in range(180):                                                             # spilled ore: bright speckle
        yy = int(rng.normal(1090, 70)); xx = int(rng.normal(930, 50))
        if 0 < yy < h - 4 and 0 < xx < w - 4: img[yy:yy + 3, xx:xx + 3] = 1.2
    img = np.clip(img, 0, 1.3) / 1.3
    rgb = np.stack([img * 255, img * 165, img * 60], -1).astype(np.uint8)
    a = np.full((h, w, 1), 255, np.uint8)
    bgra = np.concatenate([rgb[:, :, 2:3], rgb[:, :, 1:2], rgb[:, :, 0:1], a], -1).copy()
    s = cairo.ImageSurface.create_for_data(memoryview(bgra), cairo.FORMAT_ARGB32, w, h, w * 4)
    _SON['tex'] = (s, bgra, h, w)
    return _SON['tex']


def sonar_screen(cr, t, d, full=False, label='SIDE-SCAN SONAR · 24 MAY 2013'):
    cr.set_source_rgb(0.01, 0.01, 0.01); cr.paint()
    s, _, th, tw = _sonar_tex()
    sx, sy, sw, sh = (160, 140, 1600, 800) if full else (300, 150, 1320, 760)
    cr.save(); cr.rectangle(sx, sy, sw, sh); cr.clip()
    k = sw / tw
    prog = ease_in_out(ramp(t, 0.2, max(1.0, d * 0.62)))
    off = -th + sh / k + prog * (th - sh / k - 760)                                  # the strip scrolls down
    cr.translate(sx, sy); cr.scale(k, k); cr.set_source_surface(s, 0, off); cr.paint()
    cr.restore()
    box(cr, sx, sy, sw, sh, 6, stroke=OR, sa=0.6, lw=2)
    font(cr, MONO, 22); text(cr, 'PORT', sx + 20, sy + sh + 40, OR, 0.7, tracking=3); text(cr, 'STARBOARD', sx + sw - 20, sy + sh + 40, OR, 0.7, 'right', tracking=3)
    text(cr, label, sx, sy - 22, OR, 0.85, tracking=3)
    rng_y = sy + sh * 0.5
    if prog > 0.82:
        a = ramp(prog, 0.82, 0.12)
        x = sx + sw * 0.66; y = rng_y
        cr.set_source_rgba(*CY, a); cr.set_line_width(3); cr.rectangle(x - 130, y - 150, 300, 300); cr.stroke()
        tag(cr, '535 FT DOWN', x - 130, y - 172, CY, a, 24)
    hud(cr, t, 'FILE 06 · LAKE SUPERIOR · ILLUSTRATION', None)


# ---------------------------------------------------------------- card layouts
def big_number(cr, gid, t, d, num, label, sub=None, kicker=None, color=OR, suffix='', prefix=''):
    backdrop(cr, gid, t, d); hud(cr, t)
    if kicker: mono(cr, kicker, W / 2, 330, 32, CY, align='center', t=t, start=0.0, bold=True)
    v = count(t, 0.05, min(1.0, d * 0.4), num)
    font(cr, HEAD, 280); text(cr, prefix + '{:,}'.format(v) + suffix, W / 2, 590, color, ramp(t, 0, 0.25), 'center', tracking=-3)
    mono(cr, label, W / 2, 685, 40, WH, align='center', t=t, start=0.35, bold=True, cps=60)
    if sub: body(cr, sub, W / 2, 752, 34, GR, align='center', t=t, start=0.7)


def title_card(cr, gid, t, d, kicker, title, line=None, size=150, dark=0.42, color=WH, y=560):
    backdrop(cr, gid, t, d, dark=dark); hud(cr, t)
    mono(cr, kicker, W / 2, y - 160, 32, CY, align='center', t=t, start=0.0, bold=True, cps=60)
    head(cr, title, W / 2, y, size, color, align='center', t=t, start=0.1)
    bar(cr, W / 2 - 260, y + 45, 520, t, 0.35, color=OR)
    if line: mono(cr, line, W / 2, y + 120, 32, OR, align='center', t=t, start=0.5, bold=True, cps=60)


def cards(cr, t, items, starts, cols=None, y=430, w=440, h=250, letters=False, face_down=None, size=None):
    n = len(items); gap = 44
    x0 = W / 2 - (n * w + (n - 1) * gap) / 2
    for i, (word, st) in enumerate(zip(items, starts)):
        k = ramp(t, st, 0.35)
        if k <= 0: continue
        col = (cols[i] if cols else CY)
        x = x0 + i * (w + gap); yy = y + 40 * (1 - ease_out(k))
        flip = 1.0 if face_down is None else ramp(t, face_down[i], 0.35)
        sx = abs(math.cos(math.pi * (1 - flip))) if face_down is not None else 1.0
        cr.save(); cr.translate(x + w / 2, yy + h / 2); cr.scale(max(0.02, sx), 1); cr.translate(-(x + w / 2), -(yy + h / 2))
        box(cr, x, yy, w, h, 22, fill=(0.03, 0.05, 0.09), fa=0.9 * k, stroke=col, sa=0.8 * k, lw=3)
        shown = face_down is None or flip > 0.5
        if letters: font(cr, HEAD, 52); text(cr, 'ABCD'[i], x + 30, yy + 70, OR, k)
        else: font(cr, MONO, 26, bold=True); text(cr, '%d' % (i + 1), x + 30, yy + 52, col, k)
        if shown:
            lines = word.split('\n')
            sz = size or (50 if max(len(l) for l in lines) < 12 else 40)
            font(cr, HEAD, sz)
            for j, l in enumerate(lines):
                text(cr, l, x + w / 2, yy + h * 0.66 + (j - (len(lines) - 1) / 2) * sz * 1.1, WH, k, 'center')
        else:
            font(cr, HEAD, 110); text(cr, '?', x + w / 2, yy + h * 0.68, col, 0.8 * k, 'center')
        cr.restore()


def comment_cta(cr, t, d, s='COMMENT YOUR GUESS  ↓', y=790):
    k = ramp(t, d * 0.55, 0.4)
    if k <= 0: return
    p = 1 + 0.05 * math.sin(t * 6)
    cr.save(); cr.translate(W / 2, y); cr.scale(p, p)
    font(cr, BODY, 40, bold=True); w = text_width(cr, s)
    box(cr, -w / 2 - 50, -50, w + 100, 92, 46, fill=(0.86, 0.13, 0.13), fa=k)
    text(cr, s, 0, 14, WH, k, 'center')
    cr.restore()


def sub_anim(cr, gid, t, d, line, kicker=None, y=520):
    backdrop(cr, gid, t, d, dark=0.42); hud(cr, t)
    k = ramp(t, 0, 0.4); click = min(2.0, d * 0.42)
    if kicker: mono(cr, kicker, W / 2, y - 170, 32, OR, align='center', t=t, start=0.1, bold=True, cps=50)
    sub_button(cr, W / 2 - 80, y, t, click, k)
    bell(cr, W / 2 + 260, y, 1.3, k, ring=max(0, t - click - 0.5), filled=t > click + 0.5)
    if t > click + 0.5: sonar(cr, W / 2 + 260, y, t - click - 0.5, OR, r0=0.1, rings=2, a=0.9, rmax=90)
    f_in = ramp(t, 0.3, max(0.4, click - 0.3))
    if t <= click: cx, cy = W / 2 - 60 + 300 * (1 - f_in), y + 10 + 220 * (1 - f_in)
    else: f2 = ramp(t, click + 0.15, 0.3); cx, cy = W / 2 - 60 + 320 * f2, y + 10
    cursor(cr, cx, cy, k, press=max(0.0, 1 - min(abs(t - click), abs(t - click - 0.5)) / 0.15))
    mono(cr, line, W / 2, y + 165, 30, WH, align='center', t=t, start=0.6, bold=True, cps=50)


def like_card(cr, gid, t, d, line):
    backdrop(cr, gid, t, d, dark=0.40); hud(cr, t)
    k = ramp(t, 0, 0.4); y = 520; c1 = min(1.4, d * 0.35)
    liked = t > c1
    pop = 1 + 0.25 * max(0.0, 1 - abs(t - c1) / 0.25)
    box(cr, W / 2 - 150, y - 90, 300, 180, 90, fill=(0.2, 0.24, 0.27), fa=0.85 * k)
    thumb(cr, W / 2, y + 4, 1.45 * pop, k, liked)
    if liked: sonar(cr, W / 2, y, t - c1, OR, r0=0.1, rings=2, a=0.8, rmax=130)
    f = ramp(t, 0.2, max(0.3, c1 - 0.2))
    cursor(cr, W / 2 - 10 + 280 * (1 - f), y + 20 + 220 * (1 - f), k, press=max(0.0, 1 - abs(t - c1) / 0.15))
    mono(cr, 'WAITED A HUNDRED YEARS FOR THIS?', W / 2, 330, 34, OR, align='center', t=t, start=0.2, bold=True, cps=50)
    mono(cr, line, W / 2, y + 200, 28, WH, align='center', t=t, start=0.8, bold=True, cps=50)


def stat_pair(cr, gid, t, d, a, b, kicker=None, sub=None):
    """Two big numbers side by side: a and b are (number, prefix, suffix, label, colour)."""
    backdrop(cr, gid, t, d); hud(cr, t)
    if kicker: mono(cr, kicker, W / 2, 300, 30, CY, align='center', t=t, start=0.0, bold=True)
    for i, (num, pre, suf, lab, col) in enumerate((a, b)):
        cx = W / 2 + (-380 if i == 0 else 380); st = 0.1 + i * 0.5
        v = count(t, st, min(1.0, d * 0.35), num)
        font(cr, HEAD, 210); text(cr, pre + '{:,}'.format(v) + suf, cx, 580, col, ramp(t, st, 0.25), 'center', tracking=-3)
        mono(cr, lab, cx, 670, 36, WH, align='center', t=t, start=st + 0.3, bold=True, cps=60)
    cr.set_source_rgba(*CY, 0.35 * ramp(t, 0.3, 0.4)); cr.rectangle(W / 2 - 1, 400, 2, 300); cr.fill()
    if sub: body(cr, sub, W / 2, 780, 34, GR, align='center', t=t, start=1.2)


# ================================================================ the graphics, in order
@reg('G01')
def g01(cr, t, d):
    sonar_screen(cr, t, d)


@reg('G02')
def g02(cr, t, d):
    big_number(cr, 'G02', t, d, 535, 'BELOW THE SURFACE', 'Lake Superior, about 30 miles north of Marquette', suffix=' FT', color=CY)


@reg('G03')
def g03(cr, t, d):
    backdrop(cr, 'G03', t, d); hud(cr, t)
    for i, (yr, lab, col) in enumerate((('1913', 'LOST', RD), ('2013', 'FOUND', GN))):
        cx = W / 2 + (-420 if i == 0 else 420); st = 0.1 + i * 0.9
        mono(cr, lab, cx, 380, 40, col, align='center', t=t, start=st, bold=True, cps=40)
        head(cr, yr, cx, 560, 220, WH, align='center', t=t, start=st + 0.1)
    k = ramp(t, 0.6, 1.0)
    if k > 0:
        x0, x1, y = W / 2 - 160, W / 2 + 160, 480
        arrow(cr, [(x0, y), (x0 + (x1 - x0) * k, y)], OR, 0.9, 6, 22, 1.0)
    mono(cr, 'ALMOST EXACTLY 100 YEARS', W / 2, 720, 40, OR, align='center', t=t, start=1.6, bold=True, cps=50)


@reg('G04')
def g04(cr, t, d):
    big_number(cr, 'G04', t, d, 25, 'MEN ON BOARD', kicker='SUNDAY · 9 NOVEMBER 1913', color=WH)


@reg('G05')
def g05(cr, t, d):
    v = WIDE
    coast_map(cr, v, t, 'FILE 06 · THE CLUES, 1913–1914')
    marquette(cr, v, t, 0.1)
    mx, my = v.xy(*PT['marquette'])
    for i, key in enumerate(('chocolay', 'note')):
        k = ramp(t, 0.6 + i * 0.8, 0.8)
        if k <= 0: continue
        x1, y1 = v.xy(*PT[key])
        arrow(cr, [(mx + 40, my - 40 - i * 40), (mx + 340, my - 40 - i * 40)], OR, 0.9, 6, 22, k)
        tag(cr, ('THE WRECKAGE' if i == 0 else 'THE NOTE') + ' → EAST', mx + 360, my - 32 - i * 40, OR, k, 22)
    a = ramp(t, 2.4, 0.5)
    if a > 0:
        x, y = v.xy(47.05, -87.40)
        font(cr, HEAD, 200); text(cr, '?', x, y + 70, CY, 0.85 * a, 'center')
        tag(cr, 'SHE WAS SOMEWHERE ELSE', x - 140, y + 130, CY, a, 24)


@reg('G06')
def g06(cr, t, d):
    backdrop(cr, 'G06', t, d, dark=0.40); hud(cr, t)
    mono(cr, 'CASE FILE 06 · FOUR QUESTIONS', 240, 270, 30, OR, t=t, start=0.0, bold=True)
    qs = ['WHY DID SHE SAIL?', 'WHAT WAS HER CREW DOING ON DECK?', 'WHY DID EVERY CLUE POINT EAST?', 'WHAT DOES THE WRECK SAY?']
    for i, q in enumerate(qs):
        k = ramp(t, 0.4 + i * d * 0.17, 0.4)
        if k <= 0: continue
        y = 380 + i * 110
        font(cr, HEAD, 38); text(cr, '%02d' % (i + 1), 240, y, OR, k)
        head(cr, q, 330, y, 58, WH, a=k)


@reg('G07')
def g07(cr, t, d):
    backdrop(cr, 'G07', t, d, dark=0.40); hud(cr, t)
    mono(cr, 'FROM THE EDMUND FITZGERALD VIDEO? WELCOME', W / 2, 330, 32, CY, align='center', t=t, start=0.0, bold=True, cps=60)
    for i, s in enumerate(('SAME LAKE', 'SAME MONTH', '62 YEARS EARLIER')):
        head(cr, s, W / 2, 480 + i * 110, 96, OR if i == 2 else WH, align='center', t=t, start=0.4 + i * 0.5)


@reg('G08')
def g08(cr, t, d):
    sub_anim(cr, 'G08', t, d, 'THAT\'S HOW WE FIND PEOPLE WHO LOVE THESE LAKES', kicker='WANT THE NEXT STORY?')


@reg('G09')
def g09(cr, t, d):
    v = GREAT_LAKES
    lake_map(cr, v, t, 'FILE 06 · 7 TO 10 NOVEMBER 1913 · SIMPLIFIED')
    lows = [((48.6, -91.5), (46.8, -84.5), 'STORM 1', 'FROM THE NORTHWEST'), ((37.0, -79.5), (42.3, -80.5), 'STORM 2', 'FROM THE SOUTH')]
    for i, (p0, p1, lab, sub) in enumerate(lows):
        k = ease_in_out(ramp(t, 0.3 + i * 0.6, max(1.0, d * 0.55)))
        la = p0[0] + (p1[0] - p0[0]) * k; lo = p0[1] + (p1[1] - p0[1]) * k
        x, y = v.xy(la, lo)
        a = ramp(t, 0.2 + i * 0.6, 0.4)
        for r in (44, 74, 104):
            cr.set_source_rgba(*(RD if i else OR), 0.55 * a); cr.set_line_width(4)
            ang = t * 1.8 + r
            cr.new_sub_path(); cr.arc_negative(x, y, r, ang, ang - 4.5); cr.stroke()
        font(cr, HEAD, 64); text(cr, 'L', x, y + 22, RD if i else OR, a, 'center')
        tag(cr, lab + ' · ' + sub, x + (130 if i == 0 else 120), y + (-90 if i == 0 else 20), RD if i else OR, a, 22)
    a = ramp(t, d * 0.7, 0.5)
    if a > 0:
        x, y = v.xy(45.3, -83.6)
        sonar(cr, x, y, t - d * 0.7, WH, a=a, rmax=200)
        tag(cr, 'THEY MEET OVER THE LAKES', x - 180, y + 160, WH, a, 26)


@reg('G10')
def g10(cr, t, d):
    backdrop(cr, 'G10', t, d, dark=0.40); hud(cr, t)
    mono(cr, 'ONE STORM, THREE NAMES', W / 2, 330, 32, CY, align='center', t=t, start=0.0, bold=True)
    cards(cr, t, ['THE BIG\nBLOW', 'THE FRESHWATER\nFURY', 'THE WHITE\nHURRICANE'], [0.3, d * 0.33, d * 0.58],
          cols=[OR, CY, WH], y=420, w=500, h=270, size=48)


@reg('G11')
def g11(cr, t, d):
    stat_pair(cr, 'G11', t, d, (90, '', '', 'MPH GUSTS', OR), (35, '', '+', 'FOOT WAVES', CY), kicker='THE GREAT LAKES STORM OF 1913')


@reg('G12')
def g12(cr, t, d):
    card_lines(cr, 'G12', t, d, 'WEATHER FORECASTING IN 1913', ['REPORTS COLLECTED TWICE A DAY', 'MAPS DRAWN BY HAND',
               'NO WAY TO SEE IT COMING'], step=d * 0.25, start=0.4, size=60, y0=470)


@reg('G13')
def g13(cr, t, d):
    stat_pair(cr, 'G13', t, d, (250, '', '+', 'PEOPLE KILLED', RD), (19, '', '', 'SHIPS DESTROYED', OR),
              kicker='7 TO 10 NOVEMBER 1913', sub='The deadliest natural disaster in Great Lakes history')


@reg('G14')
def g14(cr, t, d):
    backdrop(cr, 'G14', t, d, dark=0.38); hud(cr, t)
    head(cr, 'HENRY B. SMITH', W / 2, 230, 96, WH, align='center', t=t, start=0.0)
    mono(cr, 'STEEL ORE FREIGHTER · ACME TRANSIT COMPANY', W / 2, 290, 28, CY, align='center', t=t, start=0.3, bold=True, cps=60)
    k = ramp(t, 0.4, 0.6)
    x0, x1, deck, keel = 260, 1660, 540, 650
    cr.save(); cr.translate(-1600 * (1 - ease_out(k)), 0)
    smith_side(cr, x0, x1, deck, keel, a=1.0, color=(0.06, 0.06, 0.07))
    cr.restore()
    a = ramp(t, 1.1, 0.5)
    if a > 0:
        cr.set_source_rgba(*OR, a); cr.set_line_width(3)
        cr.move_to(x0, 705); cr.line_to(x1, 705); cr.stroke()
        for x in (x0, x1): cr.move_to(x, 689); cr.line_to(x, 721); cr.stroke()
        font(cr, HEAD, 60); w = text_width(cr, '545 FT')
        box(cr, W / 2 - w / 2 - 24, 673, w + 48, 70, 8, fill=(0.03, 0.05, 0.09), fa=0.95 * a)
        text(cr, '545 FT', W / 2, 730, OR, a, 'center')
    mono(cr, 'BUILT 1906 · LORAIN, OHIO', W / 2, 800, 32, WH, align='center', t=t, start=1.6, bold=True, cps=60)


@reg('G15')
def g15(cr, t, d):
    backdrop(cr, 'G15', t, d, dark=0.40); hud(cr, t)
    mono(cr, 'MARQUETTE · NOVEMBER 1913', W / 2, 300, 30, CY, align='center', t=t, start=0.0, bold=True)
    days = [('THU', '6', 'ARRIVES'), ('FRI', '7', 'ORE FREEZES'), ('SAT', '8', 'STILL LOADING'), ('SUN', '9', 'SAILS')]
    w, h, gap = 330, 330, 40; x0 = W / 2 - (4 * w + 3 * gap) / 2
    for i, (dw, dn, lab) in enumerate(days):
        st = 0.3 + i * d * 0.18; k = ramp(t, st, 0.35)
        if k <= 0: continue
        x = x0 + i * (w + gap); y = 380
        col = OR if i == 3 else CY
        box(cr, x, y, w, h, 18, fill=(0.03, 0.05, 0.09), fa=0.9 * k, stroke=col, sa=0.8 * k, lw=3)
        cr.set_source_rgba(*col, 0.85 * k); cr.rectangle(x, y, w, 60); cr.fill()
        font(cr, MONO, 28, bold=True); text(cr, 'NOV · ' + dw, x + w / 2, y + 42, NV, k, 'center', tracking=3)
        font(cr, HEAD, 150); text(cr, dn, x + w / 2, y + 230, WH, k, 'center')
        font(cr, MONO, 24, bold=True); text(cr, lab, x + w / 2, y + 300, col, k, 'center', tracking=2)


@reg('G16')
def g16(cr, t, d):
    card_quote(cr, 'G16', t, d, ['"This last trip had better', 'be on time."'], 'THE STORY TOLD IN MARQUETTE · NEVER PROVEN', size=88)


@reg('G17')
def g17(cr, t, d):
    backdrop(cr, 'G17', t, d, dark=0.40); hud(cr, t)
    cx, cy, r = W / 2, 700, 250
    a = ramp(t, 0, 0.4)
    cr.set_line_width(26); cr.set_line_cap(cairo.LINE_CAP_BUTT)
    for lo, hi, col in ((0, 39, CY), (39, 73, OR), (73, 100, RD)):
        a0 = math.pi + math.pi * lo / 100; a1 = math.pi + math.pi * hi / 100
        cr.set_source_rgba(*col, 0.75 * a); cr.arc(cx, cy, r, a0, a1); cr.stroke()
    font(cr, MONO, 24, bold=True)
    for v_, lab in ((0, '0'), (32, '32'), (55, 'GALE'), (74, 'HURRICANE')):
        ang = math.pi + math.pi * v_ / 100
        text(cr, lab, cx + (r + 60) * math.cos(ang), cy + (r + 60) * math.sin(ang) + 8, WH, 0.8 * a, 'center', tracking=2)
    val = 66 - (66 - 32) * ease_in_out(ramp(t, 0.6, max(1.0, d * 0.45)))
    ang = math.pi + math.pi * val / 100
    cr.set_source_rgba(*WH, a); cr.set_line_width(8); cr.set_line_cap(cairo.LINE_CAP_ROUND)
    cr.move_to(cx, cy); cr.line_to(cx + (r - 40) * math.cos(ang), cy + (r - 40) * math.sin(ang)); cr.stroke()
    circle(cr, cx, cy, 18, WH, a)
    font(cr, HEAD, 110); text(cr, '%d MPH' % round(val), cx, cy + 130, OR if val < 40 else WH, a, 'center')
    mono(cr, 'THE WIND DROPS · SUNDAY AFTERNOON', cx, 230, 32, CY, align='center', t=t, start=0.2, bold=True)
    mono(cr, 'BY ONE ACCOUNT', cx, 280, 24, GR, align='center', t=t, start=0.6, bold=True)


@reg('G18')
def g18(cr, t, d):
    backdrop(cr, 'G18', t, d, dark=0.40); hud(cr, t)
    cx, cy, r = 620, 560, 210
    a = ramp(t, 0, 0.4)
    circle(cr, cx, cy, r, (0.03, 0.05, 0.09), 0.85 * a); circle(cr, cx, cy, r, OR, 0.9 * a, fill=False, width=5)
    for k in range(12):
        an = k * math.pi / 6
        cr.set_source_rgba(*WH, 0.8 * a); cr.set_line_width(5 if k % 3 == 0 else 2)
        cr.move_to(cx + (r - 30) * math.sin(an), cy - (r - 30) * math.cos(an)); cr.line_to(cx + (r - 10) * math.sin(an), cy - (r - 10) * math.cos(an)); cr.stroke()
    m = 60 * (1 - ease_out(ramp(t, 0.1, 1.2)))           # the minute hand sweeps up to twelve, the hour hand to five
    for ang, L, wd in ((math.radians(150 - m * 0.5), 120, 10), (math.radians(-m * 6), 170, 6)):
        cr.set_source_rgba(*WH, a); cr.set_line_width(wd); cr.set_line_cap(cairo.LINE_CAP_ROUND)
        cr.move_to(cx, cy); cr.line_to(cx + L * math.sin(ang), cy - L * math.cos(ang)); cr.stroke()
    circle(cr, cx, cy, 12, OR, a)
    head(cr, '5:00 P.M.', 920, 540, 150, WH, t=t, start=0.4)
    mono(cr, 'SUNDAY · 9 NOVEMBER 1913', 926, 620, 36, OR, t=t, start=0.8, bold=True, cps=50)
    mono(cr, 'THE LAST CAR OF ORE IS LOADED', 926, 690, 30, CY, t=t, start=1.4, bold=True, cps=50)


@reg('G19')
def g19(cr, t, d):
    backdrop(cr, 'G19', t, d, dark=0.36); hud(cr, t)
    mono(cr, 'THE SMITH FROM ABOVE · 32 HATCHES', W / 2, 270, 32, CY, align='center', t=t, start=0.0, bold=True)
    closed = int(round(9 * ease_out(ramp(t, d * 0.45, d * 0.4))))
    a = ramp(t, 0.2, 0.5)
    smith_top(cr, W / 2, 520, 1600, 170, t, closed_until=closed, a=a)
    k = ramp(t, 1.0, 0.5)
    if k > 0:
        for i, (lab, col) in enumerate((('COVERED', (0.55, 0.57, 0.58)), ('STILL OPEN', OR))):
            x = W / 2 - 330 + i * 380
            box(cr, x, 690, 34, 34, 4, fill=col if i == 0 else (0, 0, 0), fa=k, stroke=OR if i else None, sa=k)
            font(cr, MONO, 28, bold=True); text(cr, lab, x + 50, 718, WH, k, tracking=2)
    mono(cr, 'NORMALLY HOURS OF WORK BEFORE OPEN WATER', W / 2, 790, 30, OR, align='center', t=t, start=d * 0.35, bold=True, cps=50)
    font(cr, MONO, 22); text(cr, 'BOW →', W / 2 + 720, 450, GR, a, 'right', tracking=3)


@reg('G20')
def g20(cr, t, d):
    backdrop(cr, 'G20', t, d, dark=0.38); hud(cr, t)
    cx, cy, r = W / 2, 520, 200
    k = ease_in_out(ramp(t, 0.2, max(0.8, d * 0.6)))
    circle(cr, cx, cy, r, CY, 0.25, fill=False, width=14)
    cr.set_source_rgba(*OR, 0.95); cr.set_line_width(14); cr.arc(cx, cy, r, -math.pi / 2, -math.pi / 2 + 2 * math.pi * k); cr.stroke()
    font(cr, HEAD, 130); text(cr, '+%d' % round(20 * k), cx, cy + 30, WH, ramp(t, 0, 0.3), 'center')
    mono(cr, 'MINUTES', cx, cy + 100, 34, CY, align='center', t=t, start=0.2, bold=True)
    mono(cr, 'THE STORM RETURNS WITH ITS FULL FORCE', cx, 790, 32, OR, align='center', t=t, start=d * 0.6, bold=True, cps=60)


@reg('G21')
def g21(cr, t, d):
    v = GREAT_LAKES
    lake_map(cr, v, t, 'FILE 06 · NIGHT OF 9 NOVEMBER 1913 · 8 P.M. TO MIDNIGHT')
    k = ramp(t, 0.3, 0.6)
    lakes = [(47.6, -87.6), (44.0, -87.0), (44.8, -82.4), (42.2, -81.2)]
    for i, (la, lo) in enumerate(lakes):
        a = ramp(t, 0.3 + i * 0.35, 0.4)
        if a <= 0: continue
        x, y = v.xy(la, lo)
        for j in range(4):
            ph = ((t * 0.9 + j * 0.25 + i * 0.13) % 1.0)
            xx = x - 140 + 280 * ph; yy = y - 60 + 40 * j - 50 * ph
            arrow(cr, [(xx - 50, yy - 40), (xx + 20, yy + 20)], WH, 0.7 * a * (1 - abs(ph - 0.5) * 1.6), 4, 14, 1.0)
        tag(cr, '70+ MPH', x - 60, y + (70 if la > 43 else -60), OR, a, 24)
    k2 = ramp(t, d * 0.5, 0.4)
    if k2 > 0: box(cr, W / 2 - 520, 120, 1040, 170, 16, fill=(0.02, 0.04, 0.07), fa=0.85 * k2)
    head(cr, 'HURRICANE FORCE', W / 2, 210, 84, WH, align='center', t=t, start=d * 0.5)
    mono(cr, 'FOR HOURS, ON FOUR OF THE FIVE LAKES', W / 2, 262, 30, OR, align='center', t=t, start=d * 0.6, bold=True, cps=60)


@reg('G22')
def g22(cr, t, d):
    v = View.lerp(NEAR, WIDE, ramp(t, d * 0.55, d * 0.35))
    coast_map(cr, v, t, 'FILE 06 · THE LAST SIGHTING · APPROXIMATE')
    marquette(cr, v, t, 0.1)
    pts = [PT['marquette'], (46.56, -87.36), (46.585, -87.30), PT['seen']]
    v3.path(cr, v, [(la + 0.004, lo + 0.012) for la, lo in pts[:3]] + [pts[3]], t, 0.5, 1.4, OR, 6, None, 1.0, False)
    a = ramp(t, 1.8, 0.4)
    if a > 0:
        x, y = v.xy(*PT['seen'])
        sonar(cr, x, y, t - 1.8, OR, a=a, rmax=80)
        tag(cr, 'LAST SEEN · TURNING TO PORT', x + 30, y - 30, OR, a, 24)
    k = ramp(t, 2.4, 1.2)
    if k > 0:
        cr.set_dash([12, 10])
        v3.path(cr, v, [PT['seen'], (46.80, -87.36), (47.05, -87.55), (47.30, -87.70)], t, 2.4, 1.6, CY, 4, [12, 10], 0.8, True)
        cr.set_dash([])
        x, y = v.xy(47.30, -87.70)
        tag(cr, 'TOWARD THE KEWEENAW?', x + 24, y + 10, CY, ramp(t, 3.6, 0.4), 22)


@reg('G23')
def g23(cr, t, d):
    backdrop(cr, 'G23', t, d, dark=0.36); hud(cr, t)
    a = ramp(t, 0.2, 0.6)
    k = ease_in_out(ramp(t, 0.2, 1.0))
    arrow(cr, [(W / 2 - 300, 640), (W / 2 - 60, 640), (W / 2 + 40, 600), (W / 2 + 90, 480)], OR, a, 10, 34, k)
    head(cr, 'REMEMBER THE TURN', W / 2, 360, 110, WH, align='center', t=t, start=0.4)


@reg('G24')
def g24(cr, t, d):
    v = View(46.55, -87.20, 2600)
    coast_map(cr, v, t, 'FILE 06 · 11 NOVEMBER 1913 · WRECKAGE ON THE BEACHES')
    marquette(cr, v, t, 0.1, align='left')
    for i, (key, lab) in enumerate((('chocolay', 'CHOCOLAY BAY'), ('shot', 'SHOT POINT'), ('laughing', 'LAUGHING FISH POINT'))):
        st = 0.5 + i * d * 0.16
        a = ramp(t, st, 0.4)
        if a <= 0: continue
        x, y = v.xy(*PT[key])
        rng = np.random.default_rng(i + 3)
        for j in range(10):
            dx, dy = rng.normal(0, 18), rng.normal(0, 6)
            cr.save(); cr.translate(x + dx, y - 14 + dy); cr.rotate(rng.uniform(0, 3))
            cr.set_source_rgba(*OR, 0.85 * a); cr.rectangle(-9, -2.5, 18, 5); cr.fill(); cr.restore()
        font(cr, HEAD, 34); text(cr, lab, x + (60 if i == 0 else 0), y + (95 if i == 0 else 60 if i == 2 else -40), WH, a, 'center')
    tag(cr, 'ALL EAST OF MARQUETTE', W / 2 - 200, 260, OR, ramp(t, d * 0.7, 0.4), 28)


@reg('G25')
def g25(cr, t, d):
    big_number(cr, 'G25', t, d, 25, 'MEN ON BOARD', 'Only two were ever found', color=WH)


@reg('G26')
def g26(cr, t, d):
    backdrop(cr, 'G26', t, d, dark=0.38); hud(cr, t)
    a = ramp(t, 0, 0.5)
    mono(cr, 'IN OUR WORDS: NOT A COPY OF THE NOTE', W / 2, 250, 24, GR, align='center', t=t, start=1.8, bold=True, cps=60)
    cr.save(); cr.translate(W / 2, 540); cr.rotate(-0.03)
    box(cr, -520, -240, 1040, 480, 10, fill=(0.90, 0.86, 0.76), fa=0.96 * a)
    cr.set_source_rgba(0.55, 0.50, 0.42, 0.35 * a); cr.set_line_width(1.5)
    for k in range(8): cr.move_to(-470, -150 + k * 50); cr.line_to(470, -150 + k * 50); cr.stroke()
    font(cr, MONO, 26, bold=True); text(cr, 'FOUND JUNE 1914 · WHAT THE NOTE CLAIMED', -470, -180, (0.35, 0.28, 0.22), a, tracking=2)
    head(cr, 'SHE BROKE IN TWO', 0, -40, 92, (0.12, 0.10, 0.09), align='center', t=t, start=0.5)
    head(cr, '12 MILES EAST', 0, 80, 92, (0.62, 0.16, 0.10), align='center', t=t, start=1.0)
    head(cr, 'OF MARQUETTE', 0, 180, 70, (0.12, 0.10, 0.09), align='center', t=t, start=1.3)
    cr.restore()


@reg('G27')
def g27(cr, t, d):
    v = View(46.56, -87.22, 3300)
    coast_map(cr, v, t, 'FILE 06 · TWO CLUES')
    marquette(cr, v, t, 0.1, align='right')
    a = ramp(t, 0.4, 0.4)
    for key in ('chocolay', 'shot', 'laughing'):
        x, y = v.xy(*PT[key]); circle(cr, x, y, 9, OR, a)
    if a > 0:
        x, y = v.xy(*PT['shot']); tag(cr, 'THE WRECKAGE', x - 80, y + 60, OR, a, 24)
    a2 = ramp(t, 1.0, 0.4)
    if a2 > 0:
        mx, my = v.xy(*PT['marquette']); nx, ny = v.xy(*PT['note'])
        miles_line(cr, (mx + 10, my), (nx, ny), '12 MILES EAST', a2, OR)
        sonar(cr, nx, ny, t - 1.0, OR, a=a2, rmax=90)
        tag(cr, 'THE NOTE SAID HERE', nx - 120, ny - 70, OR, a2, 24)
    k = ramp(t, d * 0.55, 0.8)
    if k > 0:
        arrow(cr, [(W / 2 - 300, 230), (W / 2 - 300 + 600 * k, 230)], OR, 0.9, 8, 26, 1.0)
        head(cr, 'EAST', W / 2 + 360, 250, 70, OR, a=k)


@reg('G28')
def g28(cr, t, d):
    backdrop(cr, 'G28', t, d, dark=0.38); hud(cr, t)
    for i, (lab, big, col) in enumerate((('THE NOTE WAS DATED', '12 NOV', OR), ('SHE WAS LOST ON', '9–10 NOV', CY))):
        cx = W / 2 + (-420 if i == 0 else 420); st = 0.2 + i * 0.8
        mono(cr, lab, cx, 380, 32, col, align='center', t=t, start=st, bold=True, cps=50)
        head(cr, big, cx, 540, 150, WH, align='center', t=t, start=st + 0.1)
    stamp(cr, 'JUDGED A FAKE', W / 2, 760, t, d * 0.55, 80, RD)


@reg('G29')
def g29(cr, t, d):
    backdrop(cr, 'G29', t, d, dark=0.34); hud(cr, t)
    head(cr, 'WHERE WAS SHE?', W / 2, 270, 96, WH, align='center', t=t, start=0.0)
    mono(cr, 'YOUR GUESS, BEFORE THE ANSWER', W / 2, 340, 32, OR, align='center', t=t, start=0.3, bold=True)
    cards(cr, t, ['EAST', 'SOMEWHERE\nELSE'], [d * 0.2, d * 0.32], cols=[OR, CY], y=420, w=560, h=270, letters=True, size=60)
    comment_cta(cr, t, d)


@reg('G30')
def g30(cr, t, d):
    backdrop(cr, 'G30', t, d, dark=0.34); hud(cr, t)
    head(cr, 'ONE WORD IS ENOUGH', W / 2, 330, 90, WH, align='center', t=t, start=0.0)
    comment_box(cr, W / 2 - 560, 450, 1120, 'My guess: ', t, 0.6, cps=9)
    mono(cr, 'THE ANSWER IS A FEW MINUTES AWAY', W / 2, 680, 30, OR, align='center', t=t, start=d * 0.45, bold=True)


@reg('G31')
def g31(cr, t, d):
    backdrop(cr, 'G31', t, d, dark=0.36); hud(cr, t)
    y = 560; x0, x1 = 260, 1660
    k = ramp(t, 0.2, max(1.0, d * 0.6))
    cr.set_source_rgba(*CY, 0.6); cr.set_line_width(4); cr.move_to(x0, y); cr.line_to(x0 + (x1 - x0) * k, y); cr.stroke()
    ev = [(1913, 'HENRY B. SMITH', 'LOST · 25 MEN', OR), (1975, 'EDMUND FITZGERALD', 'LOST · 29 MEN', RD), (2013, 'THE SMITH', 'FOUND', GN)]
    for i, (yr, lab, sub, col) in enumerate(ev):
        fx = (yr - 1905) / (2020 - 1905); x = x0 + (x1 - x0) * fx
        a = ramp(t, 0.2 + fx * max(1.0, d * 0.6), 0.4)
        if a <= 0: continue
        circle(cr, x, y, 16, col, a)
        font(cr, HEAD, 80); text(cr, str(yr), x, y - 50, WH, a, 'center')
        font(cr, MONO, 26, bold=True); text(cr, lab, x, y + 70, col, a, 'center', tracking=2)
        font(cr, MONO, 22); text(cr, sub, x, y + 108, GR, a, 'center', tracking=2)


@reg('G32')
def g32(cr, t, d):
    v = SUP
    lake_map(cr, v, t, 'FILE 06 · LAKE SUPERIOR')
    a = ramp(t, 0.3, 0.5)
    font(cr, MONO, 30, bold=True); x, y = v.xy(47.6, -88.2); text(cr, 'LAKE SUPERIOR', x, y, CY, 0.8 * a, 'center', tracking=8)
    k2 = ramp(t, 0.6, 0.4)
    if k2 > 0: box(cr, W / 2 - 560, 110, 1120, 170, 16, fill=(0.02, 0.04, 0.07), fa=0.85 * k2)
    head(cr, 'THE LARGEST FRESHWATER LAKE', W / 2, 200, 64, WH, align='center', t=t, start=0.6)
    mono(cr, 'IN THE WORLD, BY AREA · ABOUT 31,700 SQUARE MILES', W / 2, 255, 28, OR, align='center', t=t, start=1.0, bold=True, cps=60)
    mx, my = v.xy(*PT['marquette']); circle(cr, mx, my, 7, WH, a)
    font(cr, BODY, 26, bold=True); text(cr, 'Marquette', mx + 14, my + 30, WH, a)


@reg('G33')
def g33(cr, t, d):
    backdrop(cr, 'G33', t, d, dark=0.38); hud(cr, t)
    mono(cr, 'THE SEARCHERS', W / 2, 300, 32, CY, align='center', t=t, start=0.0, bold=True)
    for i, n in enumerate(('JERRY ELIASON', 'KEN MERRYMAN', 'KRAIG SMITH')):
        head(cr, n, W / 2, 430 + i * 105, 84, WH, align='center', t=t, start=0.3 + i * 0.45)
    mono(cr, 'ABOUT 20 YEARS OF SEARCHING · SEVERAL TIMES A YEAR', W / 2, 800, 30, OR, align='center', t=t, start=1.8, bold=True, cps=60)


@reg('G34')
def g34(cr, t, d):
    sonar_screen(cr, t, d, full=True, label='SIDE-SCAN SONAR · 24 MAY 2013 · +20 MINUTES')


@reg('G35')
def g35(cr, t, d):
    v = View.lerp(View(46.62, -87.37, 2200), View(46.74, -87.36, 1300), ramp(t, 0.2, d * 0.5))
    coast_map(cr, v, t, 'FILE 06 · 24 MAY 2013 · POSITION APPROXIMATE')
    marquette(cr, v, t, 0.1)
    a = ramp(t, 0.9, 0.4)
    if a > 0:
        mx, my = v.xy(*PT['marquette']); wx, wy = v.xy(*PT['wreck'])
        miles_line(cr, (mx, my - 20), (wx, wy + 20), 'ABOUT 30 MILES NORTH', a, CY)
        sonar(cr, wx, wy, t - 0.9, GN, a=a, rmax=120)
        font(cr, HEAD, 44); text(cr, 'HENRY B. SMITH', wx + 40, wy - 10, GN, a)
        tag(cr, '535 FT DOWN', wx + 42, wy + 44, WH, a, 24)


@reg('G36')
def g36(cr, t, d):
    v = View(46.72, -87.25, 1250)
    coast_map(cr, v, t, 'FILE 06 · WHERE THE CLUES POINTED · WHERE SHE WAS')
    marquette(cr, v, t, 0.0)
    a = ramp(t, 0.2, 0.4)
    for key in ('chocolay', 'shot', 'laughing', 'note'):
        x, y = v.xy(*PT[key]); circle(cr, x, y, 8, RD, a)
    if a > 0:
        x, y = v.xy(*PT['shot']); tag(cr, 'THE WRECKAGE · THE NOTE', x - 60, y + 54, RD, a, 22)
    wx, wy = v.xy(*PT['wreck'])
    sonar(cr, wx, wy, t, GN, a=ramp(t, 0.5, 0.4), rmax=110)
    font(cr, HEAD, 40); text(cr, 'THE WRECK', wx + 36, wy - 8, GN, ramp(t, 0.5, 0.4))
    stamp(cr, 'NORTH. NOT EAST.', W / 2 + 420, 470, t, d * 0.45, 72, GN, 0.0)


@reg('G37')
def g37(cr, t, d):
    like_card(cr, 'G37', t, d, 'A LIKE HELPS YOUTUBE SHOW THIS STORY TO MORE PEOPLE')


@reg('G38')
def g38(cr, t, d):
    backdrop(cr, 'G38', t, d, dark=0.34); hud(cr, t)
    mono(cr, 'STILL READABLE ON HER STERN', W / 2, 390, 32, CY, align='center', t=t, start=0.0, bold=True)
    k = ramp(t, 0.3, 1.2)
    s = 'HENRY B. SMITH'; n = int(len(s) * k + 0.999)
    font(cr, HEAD, 150); text(cr, s[:n], W / 2 - text_width(cr, s) / 2, 590, WH, ramp(t, 0.3, 0.3))
    bar(cr, W / 2 - 300, 640, 600, t, 1.3, color=OR)


@reg('G39')
def g39(cr, t, d):
    background(cr)
    g = cairo.LinearGradient(0, 0, 0, H); g.add_color_stop_rgb(0, 0.02, 0.06, 0.09); g.add_color_stop_rgb(1, 0.01, 0.02, 0.03)
    cr.set_source(g); cr.paint()
    floor = 780
    cr.set_source_rgb(0.16, 0.15, 0.14); cr.move_to(0, floor)
    for x in range(0, W + 41, 40): cr.line_to(x, floor + 6 * math.sin(x / 90))
    cr.line_to(W, H); cr.line_to(0, H); cr.close_path(); cr.fill()
    a = ramp(t, 0.2, 0.6)
    # the bow (right) upright with pilothouse and mast; the stern (left) with its cabins collapsed; a gap between
    cr.save(); cr.rectangle(980, 0, W, H); cr.clip()
    smith_side(cr, 260, 1700, 690, 790, a=a, hatches=True, color=(0.20, 0.15, 0.12)); cr.restore()
    cr.save(); cr.rectangle(0, 0, 900, H); cr.clip()
    cr.translate(0, 8); smith_side(cr, 260, 1700, 690, 790, a=a, hatches=True, color=(0.20, 0.15, 0.12)); cr.restore()
    cr.set_source_rgb(0.02, 0.06, 0.09); cr.rectangle(300, 560, 230, 140); cr.fill()                 # crush the stern cabins
    cr.set_source_rgba(0.78, 0.76, 0.70, a); cr.set_line_width(3)
    for k in range(7):
        cr.move_to(305 + k * 30, 700); cr.line_to(330 + k * 28, 664 + 10 * math.sin(k * 2.3)); cr.line_to(352 + k * 27, 700); cr.stroke()
    cr.set_source_rgb(0.02, 0.06, 0.09)
    cr.move_to(900, 680); cr.line_to(930, 720); cr.line_to(910, 760); cr.line_to(940, 800); cr.line_to(960, 690); cr.line_to(980, 750)
    cr.line_to(985, 680); cr.close_path(); cr.fill()
    rng = np.random.default_rng(2)
    oa = ramp(t, 1.0, 0.6)
    for k in range(260):
        x = rng.normal(940, 160); y = floor - 4 + abs(rng.normal(0, 10))
        circle(cr, x, y, rng.uniform(2, 5), ORE, 0.9 * oa)
    lab = [(1560, 470, 'PILOTHOUSE AND MAST STILL IN PLACE', 1.4, 'right'), (940, 420, 'BROKEN IN TWO NEAR THE MIDDLE', 2.0, 'center'),
           (420, 500, 'STERN CABINS COLLAPSED', 2.6, 'center'), (940, 500, 'HER IRON ORE, SPILLED ON THE BOTTOM', 3.2, 'center')]
    for x, y, s, st, al in lab:
        tag(cr, s, x, y, OR if 'BROKEN' in s else WH, ramp(t, st, 0.4), 24, al)
    dim_v(cr, 1820, 140, floor, '535 FT', ramp(t, 0.6, 0.4), CY, 'left')
    hud(cr, t, 'FILE 06 · THE WRECK · ILLUSTRATION, NOT TO SCALE', None)


@reg('G40')
def g40(cr, t, d):
    backdrop(cr, 'G40', t, d, dark=0.36); hud(cr, t)
    mono(cr, 'THE NOTE AGAINST THE WRECK', 300, 330, 32, CY, t=t, start=0.0, bold=True)
    rows = [('SHE BROKE IN TWO', True), ('12 MILES EAST OF MARQUETTE', False)]
    for i, (s, ok) in enumerate(rows):
        st = 0.4 + i * d * 0.3; k = ramp(t, st, 0.4)
        y = 470 + i * 160
        head(cr, s, 400, y, 70, WH, a=k)
        tick(cr, 330, y - 24, 1.4, GN if ok else RD, ramp(t, st + 0.4, 0.3), ok)
    mono(cr, 'RIGHT ABOUT ONE THING · WRONG ABOUT THE OTHER', 300, 820, 30, OR, t=t, start=d * 0.7, bold=True, cps=60)


@reg('G41')
def g41(cr, t, d):
    v = View(46.73, -87.33, 1350)
    coast_map(cr, v, t, 'FILE 06 · THE TURN · POSITIONS APPROXIMATE')
    marquette(cr, v, t, 0.0)
    a = ramp(t, 0.2, 0.4)
    x, y = v.xy(*PT['seen'])
    if a > 0:
        circle(cr, x, y, 10, OR, a); tag(cr, 'LAST SEEN · TURNING TO PORT', x + 30, y + 40, OR, a, 22)
    v3.path(cr, v, [PT['seen'], (46.72, -87.31), (46.83, -87.33), PT['wreck']], t, 0.6, 1.6, GN, 5, None, 1.0, True)
    wx, wy = v.xy(*PT['wreck']); sonar(cr, wx, wy, t - 2.0, GN, a=ramp(t, 2.0, 0.4), rmax=100)
    font(cr, HEAD, 40); text(cr, 'THE WRECK', wx + 36, wy - 8, GN, ramp(t, 2.0, 0.4))
    stamp(cr, 'THEY WERE RIGHT', W / 2 + 430, 560, t, d * 0.55, 70, GN, -0.05)


@reg('G42')
def g42(cr, t, d):
    v = View(46.70, -87.22, 1250)
    coast_map(cr, v, t, 'FILE 06 · WIND FROM THE NORTH AND NORTHWEST · ILLUSTRATION')
    a = ramp(t, 0.2, 0.5)
    for j in range(14):                                     # wind streaks blowing from the north-west
        ph = (t * 0.35 + j * 0.073) % 1.0
        x = 200 + (j * 137) % 1500 + 420 * ph; y = 150 + (j * 89) % 500 + 300 * ph
        arrow(cr, [(x - 60, y - 45), (x, y)], WH, 0.5 * a * (1 - abs(ph - 0.5) * 1.8), 3, 12, 1.0)
    wx, wy = v.xy(*PT['wreck'])
    circle(cr, wx, wy, 9, GN, a); font(cr, HEAD, 34); text(cr, 'THE WRECK', wx + 26, wy - 10, GN, a)
    rng = np.random.default_rng(9)
    for k in range(26):                                     # floating wreckage drifting to the beaches
        tgt = v.xy(*PT[('chocolay', 'shot', 'laughing')[k % 3]])
        f = ease_in_out(ramp(t, 0.6 + (k % 7) * 0.12, max(1.5, d * 0.6)))
        x = wx + (tgt[0] - wx) * f + rng.normal(0, 14); y = wy + (tgt[1] - wy) * f + rng.normal(0, 14)
        cr.save(); cr.translate(x, y); cr.rotate(k); cr.set_source_rgba(*OR, 0.9 * a); cr.rectangle(-8, -2.5, 16, 5); cr.fill(); cr.restore()
    for key in ('chocolay', 'shot', 'laughing'):
        x, y = v.xy(*PT[key]); circle(cr, x, y, 7, OR, ramp(t, d * 0.7, 0.4))
    x, y = v.xy(*PT['shot']); tag(cr, 'THE THREE BEACHES', x - 120, y - 60, OR, ramp(t, d * 0.7, 0.4), 24)
    tag(cr, 'THE WIND', 230, 210, WH, a, 24)


@reg('G43')
def g43(cr, t, d):
    backdrop(cr, 'G43', t, d, dark=0.36); hud(cr, t)
    head(cr, 'THREE SUSPECTS', W / 2, 290, 100, WH, align='center', t=t, start=0.0)
    cards(cr, t, ['THE HATCHES', 'THE STORM', 'THE DECISION'], [0.4, 0.6, 0.8], cols=[OR, CY, WH], y=430,
          face_down=[1e9, 1e9, 1e9])


@reg('G44')
def g44(cr, t, d):
    background(cr)
    g = cairo.LinearGradient(0, 0, 0, H); g.add_color_stop_rgb(0, 0.05, 0.07, 0.11); g.add_color_stop_rgb(1, 0.02, 0.03, 0.05)
    cr.set_source(g); cr.paint()
    x0, x1, deck, keel = 180, 1740, 430, 700
    cr.set_source_rgb(0.12, 0.12, 0.14); cr.rectangle(x0, deck, x1 - x0, keel - deck); cr.fill()
    cr.set_source_rgba(*CY, 0.6); cr.set_line_width(3); cr.rectangle(x0, deck, x1 - x0, keel - deck); cr.stroke()
    holds = 6; hw = (x1 - x0 - 400) / holds
    lvl = ease_in_out(ramp(t, 0.8, max(1.5, d * 0.7)))
    for i in range(holds):
        hx = x0 + 250 + i * hw
        cr.set_source_rgb(0.03, 0.04, 0.06); cr.rectangle(hx + 6, deck + 20, hw - 12, keel - deck - 30); cr.fill()
        cr.set_source_rgb(*ORE); cr.rectangle(hx + 6, keel - 90, hw - 12, 80); cr.fill()                  # the ore
        wl = (keel - deck - 120) * lvl * (0.7 + 0.3 * ((i * 37) % 5) / 4)
        cr.set_source_rgba(0.25, 0.55, 0.75, 0.75); cr.rectangle(hx + 6, keel - 90 - wl, hw - 12, wl); cr.fill()
        cr.set_source_rgb(0.0, 0.0, 0.0); cr.rectangle(hx + hw * 0.3, deck - 4, hw * 0.4, 10); cr.fill()      # open hatch
        ph = (t * 1.3 + i * 0.4) % 1.0
        cr.set_source_rgba(0.55, 0.80, 0.95, 0.8 * ramp(t, 0.5, 0.4)); cr.set_line_width(6)
        for k in range(3):
            xx = hx + hw * 0.35 + k * hw * 0.1
            cr.move_to(xx, deck - 40 + 40 * ph); cr.line_to(xx, deck + 30 + 60 * ph); cr.stroke()
    head(cr, 'EVERY WAVE, INTO THE HOLDS', W / 2, 250, 76, WH, align='center', t=t, start=0.2)
    mono(cr, 'IF THE HATCHES WEREN\'T FASTENED DOWN', W / 2, 310, 30, OR, align='center', t=t, start=0.5, bold=True, cps=60)
    hud(cr, t, 'FILE 06 · A THEORY · ILLUSTRATION', None)


@reg('G45')
def g45(cr, t, d):
    background(cr)
    g = cairo.LinearGradient(0, 0, 0, H); g.add_color_stop_rgb(0, 0.05, 0.07, 0.11); g.add_color_stop_rgb(1, 0.02, 0.03, 0.05)
    cr.set_source(g); cr.paint()
    k = ease_in_out(ramp(t, 0.6, max(1.2, d * 0.5)))
    wl = lambda x: 640 + 110 * k * math.cos((x - 960) / 760 * math.pi)                 # crests under bow and stern
    cr.set_source_rgba(0.16, 0.38, 0.55, 0.9); cr.move_to(0, wl(0))
    for x in range(0, W + 21, 20): cr.line_to(x, wl(x))
    cr.line_to(W, H); cr.line_to(0, H); cr.close_path(); cr.fill()
    bend = 26 * k
    hull = lambda x: (wl(200) - 38) + (0 if x < 200 or x > 1720 else bend * math.sin((x - 200) / 1520 * math.pi))
    cr.set_source_rgb(0.08, 0.08, 0.10); cr.move_to(200, hull(200) - 40)
    for x in range(200, 1721, 20): cr.line_to(x, hull(x) - 40)
    for x in range(1720, 199, -20): cr.line_to(x, hull(x) + 40)
    cr.close_path(); cr.fill()
    cr.set_source_rgba(0.92, 0.91, 0.86, 1); cr.rectangle(1560, hull(1600) - 90, 90, 50); cr.fill(); cr.rectangle(240, hull(280) - 92, 150, 52); cr.fill()
    a = ramp(t, 1.4, 0.4)
    for x, s in ((300, 'LIFTED'), (1620, 'LIFTED')):
        arrow(cr, [(x, 790), (x, hull(x) + 60)], GN, a, 6, 20, 1.0); tag(cr, s, x - 50, hull(x) - 120, GN, a, 24)
    tag(cr, 'NOTHING HOLDING UP HER MIDDLE', 960 - 230, hull(960) + 150, OR, ramp(t, 2.0, 0.4), 26)
    head(cr, 'A WAVE UNDER EACH END', W / 2, 230, 76, WH, align='center', t=t, start=0.2)
    mono(cr, '545 FEET OF SHIP, LOADED WITH IRON ORE', W / 2, 290, 30, OR, align='center', t=t, start=0.5, bold=True, cps=60)
    hud(cr, t, 'FILE 06 · A THEORY · ILLUSTRATION, NOT TO SCALE', None)


@reg('G46')
def g46(cr, t, d):
    backdrop(cr, 'G46', t, d, dark=0.36); hud(cr, t)
    head(cr, 'THREE SUSPECTS', W / 2, 290, 100, WH, align='center', t=t, start=0.0)
    cards(cr, t, ['THE HATCHES', 'THE STORM', 'THE DECISION'], [0.0, 0.0, 0.0], cols=[OR, CY, WH], y=430,
          face_down=[0.3, 0.3 + d * 0.15, 0.3 + d * 0.3])


@reg('G47')
def g47(cr, t, d):
    backdrop(cr, 'G47', t, d, dark=0.36); hud(cr, t)
    mono(cr, 'THE HARDEST QUESTION', W / 2, 300, 32, CY, align='center', t=t, start=0.0, bold=True)
    head(cr, 'BROKE ON THE SURFACE?', W / 2, 460, 96, WH, align='center', t=t, start=0.3)
    mono(cr, 'OR', W / 2, 545, 36, OR, align='center', t=t, start=0.9, bold=True)
    head(cr, 'BROKE AT THE BOTTOM?', W / 2, 660, 96, WH, align='center', t=t, start=1.1)
    mono(cr, 'THE SAME QUESTION AS THE EDMUND FITZGERALD', W / 2, 790, 30, OR, align='center', t=t, start=d * 0.55, bold=True, cps=60)


@reg('G48')
def g48(cr, t, d):
    backdrop(cr, 'G48', t, d, dark=0.34); hud(cr, t)
    head(cr, 'YOUR VERDICT', W / 2, 270, 96, WH, align='center', t=t, start=0.0)
    mono(cr, 'WHAT SANK THE HENRY B. SMITH?', W / 2, 340, 32, OR, align='center', t=t, start=0.3, bold=True)
    cards(cr, t, ['THE HATCHES', 'THE STORM', 'THE DECISION', 'ALL THREE'], [d * 0.12, d * 0.2, d * 0.28, d * 0.4],
          cols=[OR, CY, WH, GN], y=430, w=370, h=220, letters=True, size=40)
    comment_cta(cr, t, d, 'COMMENT YOUR VERDICT  ↓')


@reg('G49')
def g49(cr, t, d):
    backdrop(cr, 'G49', t, d, dark=0.34); hud(cr, t)
    head(cr, 'I READ EVERY ONE', W / 2, 330, 90, WH, align='center', t=t, start=0.0)
    comment_box(cr, W / 2 - 560, 450, 1120, 'My verdict: ', t, 0.6, cps=9)


@reg('G50')
def g50(cr, t, d):
    backdrop(cr, 'G50', t, d, blur=18, dark=0.40); hud(cr, t, 'GREAT LAKES FILES', None)
    mono(cr, 'IN MEMORY', W / 2, 400, 32, CY, align='center', t=t, start=0.2, bold=True, cps=30)
    head(cr, 'THE 25 MEN OF THE', W / 2, 530, 84, WH, align='center', t=t, start=0.6, dur=1.0)
    head(cr, 'HENRY B. SMITH', W / 2, 640, 110, WH, align='center', t=t, start=1.0, dur=1.0)
    mono(cr, 'LOST IN LAKE SUPERIOR · 9–10 NOVEMBER 1913', W / 2, 740, 30, GR, align='center', t=t, start=1.8, bold=True, cps=40)


@reg('G51')
def g51(cr, t, d):
    sub_anim(cr, 'G51', t, d, 'LAKE SUPERIOR STILL HAS SHIPS NOBODY HAS FOUND', kicker='FOR THE NEXT ONE')


@reg('G52')
def g52(cr, t, d):
    backdrop(cr, 'G52', t, d, blur=4, dark=0.62)
    g = cairo.LinearGradient(0, 0, W * 0.6, 0); g.add_color_stop_rgba(0, 0.01, 0.02, 0.05, 0.85); g.add_color_stop_rgba(1, 0.01, 0.02, 0.05, 0)
    cr.set_source(g); cr.paint()
    hud(cr, t, 'GREAT LAKES FILES', None)
    mono(cr, 'END OF FILE 06', 140, 360, 30, OR, t=t, start=0.2, bold=True)
    head(cr, 'THANKS FOR', 134, 500, 110, WH, t=t, start=0.4)
    head(cr, 'WATCHING', 134, 620, 110, WH, t=t, start=0.6)
    mono(cr, 'THE FITZGERALD FILE  →', 140, 740, 32, CY, t=t, start=1.4, bold=True)
    mono(cr, 'SUBSCRIBE FOR THE NEXT ONE', 140, 800, 28, WH, t=t, start=2.0, bold=True)
