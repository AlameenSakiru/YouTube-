"""Every graphic in video 5 (We Drained the Edmund Fitzgerald's Graveyard), keyed by its G number in
video-05/edit-plan.json. Selected by render.py when GFX_SET=video5.

Built from the same case-file blocks as videos 3 and 4, with its own look: slate-blue storm colours, signal orange
for the ships and the killers, ice blue for the cold. Maps of Whitefish Point use the full-resolution coastline, and
the preserve map uses the real positions of its wrecks. The bottom of the frame stays clear for the captions and
the right edge for the depth meter.
"""
import math, os, json, re
import numpy as np
import cairo
from PIL import Image, ImageFilter, ImageEnhance
from style import *
import maps
from maps import View, LAKES, ISLANDS, UPPER, COUNTRIES, basemap, _poly, _load
import video3 as v3

G = {}
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
V5 = os.path.join(ROOT, 'video-05')

OR = (1.0, 0.45, 0.26)          # signal orange: ships, the storm, the killers
CY = (0.62, 0.86, 1.0)          # ice blue: the cold, labels
WH = (0.95, 0.97, 0.98)
GR = (0.70, 0.78, 0.84)
RD = (1.0, 0.33, 0.30)
GD = (1.0, 0.80, 0.30)          # gold: the silver, the bell
DK = (0.55, 0.58, 0.75)         # dusk violet: the dark
SAND = (0.52, 0.45, 0.36)
SAND_D = (0.26, 0.22, 0.18)

_OLD = {'OR': v3.OR, 'CY': v3.CY}
_swap = {_OLD['OR']: OR, _OLD['CY']: CY}
v3.OR, v3.CY, v3.WH, v3.GR = OR, CY, WH, GR
for _f in list(vars(v3).values()):
    if callable(_f) and getattr(_f, '__module__', '') == 'video3' and getattr(_f, '__defaults__', None):
        _f.__defaults__ = tuple(_swap.get(x, x) if isinstance(x, tuple) else x for x in _f.__defaults__)
v3.hud.__defaults__ = ('FILE 05 · WHITEFISH POINT', None, 1.0)

HEAD, MONO, BODY = v3.HEAD, v3.MONO, v3.BODY


# ---------------------------------------------------------------- the picture behind each graphic
def _prev_images():
    """gid -> (folder, image number) of the picture just before it (reused pictures come from their own video)."""
    try:
        plan = json.load(open(os.path.join(V5, 'edit-plan.json')))
    except Exception:
        return {}
    shots = json.load(open(os.path.join(V5, 'shots-untimed.json'))) if os.path.exists(os.path.join(V5, 'shots-untimed.json')) else plan
    out, prev = {}, ('video-05', 1)
    for s in plan:
        if s['kind'] == 'G': out[s['gid']] = prev
        elif re.match(r'V\d$', s['kind']): prev = ('video-%02d' % int(s['kind'][1]), s['img'])
        elif s.get('img'): prev = ('video-05', s['img'])
    return out


BACK = _prev_images()
BACK.update({'G54': ('video-05', 77)})
_SURF5 = {}


def _bg(folder, n, blur, dark):
    d = os.path.join(V5, 'build', 'bg'); os.makedirs(d, exist_ok=True)
    out = os.path.join(d, 'v5-%s-%03d-%d-%d.png' % (folder[-2:], n, blur, int(dark * 100)))
    if not os.path.exists(out):
        src = os.path.join(ROOT, folder)
        cf = os.path.join(src, 'images', 'crops.json')
        crops = json.load(open(cf)) if os.path.exists(cf) else {}
        im = Image.open(os.path.join(src, 'images', '%03d.jpg' % n)).convert('RGB')
        if '%03d' % n in crops: im = im.crop(tuple(crops['%03d' % n]))
        w, h = im.size
        if w / h > 16 / 9: nw = int(h * 16 / 9); im = im.crop(((w - nw) // 2, 0, (w - nw) // 2 + nw, h))
        else: nh = int(w * 9 / 16); im = im.crop((0, (h - nh) // 2, w, (h - nh) // 2 + nh))
        im = im.resize((2112, 1188), Image.LANCZOS)
        if blur: im = im.filter(ImageFilter.GaussianBlur(blur))
        im = ImageEnhance.Brightness(im).enhance(dark)
        a = np.asarray(im, np.float32) * np.array([0.93, 0.97, 1.05])
        tmp = out + '.%d.tmp.png' % os.getpid()          # write then rename: parallel workers never read half a file
        Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).save(tmp)
        os.replace(tmp, out)
    return out


def backdrop(cr, gid, t, d, blur=14, dark=0.58, n=None):
    folder, img = ('video-05', n) if n else BACK.get(gid, ('video-05', 1))
    key = (folder, img, blur, dark)
    if key not in _SURF5: _SURF5[key] = cairo.ImageSurface.create_from_png(_bg(folder, img, blur, dark))
    s = _SURF5[key]
    z = 1.0 + 0.05 * (t / max(d, 0.1))
    cr.save(); cr.translate(W / 2, H / 2); cr.scale(z * W / 2112, z * H / 1188)
    cr.translate(-2112 / 2, -1188 / 2); cr.set_source_surface(s, 0, 0); cr.paint(); cr.restore()
    g = cairo.RadialGradient(W / 2, H / 2, 100, W / 2, H / 2, W * 0.7)
    g.add_color_stop_rgba(0, 0.01, 0.02, 0.05, 0.34); g.add_color_stop_rgba(0.6, 0.01, 0.02, 0.05, 0.22)
    g.add_color_stop_rgba(1, 0.01, 0.02, 0.05, 0.55)
    cr.set_source(g); cr.paint()


v3.backdrop = backdrop
from video3 import (hud, head, mono, body, bar, box, stamp, count, sonar, cursor, bell, thumb, sub_button,
                    like_anim, comment_box, dim_v, miles_line)


def reg(gid):
    def deco(fn):
        G[gid] = fn; return fn
    return deco


def tag(cr, s, x, y, col, a, size=22):
    if a <= 0: return
    font(cr, MONO, size, bold=True); w = text_width(cr, s, 2)
    box(cr, x - 12, y - size - 6, w + 24, size + 20, 6, fill=(0.02, 0.04, 0.07), fa=0.85 * a)
    text(cr, s, x, y, col, a, tracking=2)


# ---------------------------------------------------------------- Whitefish Point, full-resolution coastline
def _near(a, la0=46.25, la1=47.45, lo0=-86.4, lo1=-83.8):
    return ((a[:, 1] > la0) & (a[:, 1] < la1) & (a[:, 0] > lo0) & (a[:, 0] < lo1)).any()


_FULL = _load('gshhs', 'f')
W_LAKES = [a for lvl, a in _FULL if lvl == 2 and len(a) > 40 and _near(a)]
W_ISL = [a for lvl, a in _FULL if lvl == 3 and _near(a)]
del _FULL

PT = {
    'point': (46.765, -84.964), 'wreck': (46.9985, -85.11), 'soo': (46.50, -84.35), 'myron': (46.8077, -85.0274),
}
# Whitefish Point Underwater Preserve wrecks with known coordinates (Wikipedia, "Whitefish Point Underwater Preserve")
WRECKS = {
    'Allegheny': (46.7669, -85.1767), 'Comet': (46.7170, -84.8667), 'John B. Cowle': (46.7406, -84.9646),
    'Drake': (46.7765, -85.0989), 'Eureka': (46.8358, -85.1793), 'Indiana': (46.8110, -85.2860),
    'Samuel Mather': (46.5718, -84.7054), 'John Mitchell': (46.8342, -85.0802), 'Miztec': (46.8012, -85.0750),
    'Myron': (46.8077, -85.0274), 'Niagara': (46.8196, -85.1248), 'Alexander Nimick': (46.7624, -85.2164),
    'John M. Osborn': (46.8662, -85.0868), 'Panther': (46.6384, -84.8062), 'Sadie Thompson': (46.7085, -84.9976),
    'Sagamore': (46.5181, -84.6323), 'Saturn': (46.7659, -85.0258), 'Superior City': (46.7252, -84.8728),
    'Vienna': (46.7410, -84.9652), 'Zillah': (46.7292, -84.9162),
}
REGION = View(46.80, -84.98, 1500)
PRESERVE = View(46.74, -84.98, 3000)
CLOSE = View(46.785, -84.995, 9000)


def grid_w(cr, v, a=0.15):
    cr.set_line_width(1); cr.set_source_rgba(*CY, a)
    for lat in np.arange(46.0, 47.6, 0.1):
        _, y = v.xy(lat, -85); cr.move_to(0, y); cr.line_to(W, y); cr.stroke()
    for lon in np.arange(-86.5, -83.5, 0.2):
        x, _ = v.xy(46.8, lon); cr.move_to(x, 0); cr.line_to(x, H); cr.stroke()


def region_map(cr, v, t, label='FILE 05 · WHITEFISH POINT', border=False, names=True):
    cr.set_source_rgb(*LAND); cr.paint()
    for a in W_LAKES:
        _poly(cr, v.pts(a)); cr.set_source_rgb(*WATER); cr.fill()
    for a in W_ISL:
        _poly(cr, v.pts(a)); cr.set_source_rgb(*LAND); cr.fill()
    cr.set_line_width(1.8); cr.set_source_rgba(*COAST, 0.85)
    for a in W_LAKES + W_ISL:
        _poly(cr, v.pts(a)); cr.stroke()
    if border:
        cr.save()
        for a in W_LAKES: _poly(cr, v.pts(a))
        cr.clip()
        cr.set_dash([12, 9]); cr.set_line_width(2.5); cr.set_source_rgba(*WH, 0.55)
        for a in COUNTRIES:
            p = v.pts(a)
            if ((p[:, 0] > -200) & (p[:, 0] < W + 200) & (p[:, 1] > -200) & (p[:, 1] < H + 200)).any():
                cr.move_to(*p[0])
                for q in p[1:]: cr.line_to(*q)
                cr.stroke()
        cr.set_dash([]); cr.restore()
    g = cairo.RadialGradient(W / 2, H / 2, 300, W / 2, H / 2, W * 0.75)
    g.add_color_stop_rgba(0, 0, 0, 0, 0); g.add_color_stop_rgba(1, 0, 0.01, 0.04, 0.55)
    cr.set_source(g); cr.paint()
    grid_w(cr, v)
    if names:
        font(cr, MONO, 22)
        for s, ll in (('LAKE SUPERIOR', (47.05, -85.55)), ('WHITEFISH BAY', (46.62, -84.83)), ('MICHIGAN', (46.55, -85.40)),
                      ('ONTARIO', (47.05, -84.55))):
            x, y = v.xy(*ll)
            if 100 < x < W - 260 and 120 < y < H - 220:
                text(cr, s, x, y, CY if 'LAKE' in s or 'BAY' in s else WH, 0.65, 'center', tracking=5)
    hud(cr, t, label, None)


def point_mark(cr, v, t, start=0.0, label='WHITEFISH POINT', dx=26, dy=-18, align='left'):
    a = ramp(t, start, 0.4)
    if a <= 0: return
    x, y = v.xy(*PT['point'])
    circle(cr, x, y, 9, WH, a); circle(cr, x, y, 16, WH, 0.5 * a, fill=False, width=2)
    font(cr, HEAD, 30)
    if align == 'left': text(cr, label, x + dx, y + dy, WH, a)
    else: text(cr, label, x - dx, y + dy, WH, a, 'right')


def wreck_mark(cr, v, t, start, lab, sub=None, color=OR, dx=28, dy=-16):
    a = ramp(t, start, 0.4)
    if a <= 0: return
    x, y = v.xy(*PT['wreck'])
    sonar(cr, x, y, t - start, color, a=a, rmax=110)
    font(cr, HEAD, 36); text(cr, lab, x + dx, y + dy, color, a)
    if sub: tag(cr, sub, x + dx + 2, y + dy + 46, WH, a)


# ---------------------------------------------------------------- the shelf off Whitefish Point, in cross-section
SURF = 300
X0, X1 = 110, 1690


def shelf_depth(u):
    """Depth in feet along a line from the point (u=0) out into the open lake (u=1). Not to scale."""
    if u < 0.04: return -min(45.0, (0.04 - u) * 900)
    k = [(0.04, 0), (0.16, 30), (0.28, 55), (0.40, 110), (0.52, 160), (0.62, 230), (0.70, 270), (0.80, 330), (0.92, 500), (1.0, 530)]
    for (u0, d0), (u1, d1) in zip(k, k[1:]):
        if u <= u1:
            f = (u - u0) / (u1 - u0); f = f * f * (3 - 2 * f)
            return d0 + (d1 - d0) * f + 4 * math.sin(u * 61)
    return 530


PPF = 0.92


def shelf(cr, t, level=0.0, label='FILE 05 · OFF WHITEFISH POINT · NOT TO SCALE', glow=None):
    background(cr)
    g = cairo.LinearGradient(0, 0, 0, SURF); g.add_color_stop_rgb(0, 0.04, 0.07, 0.12); g.add_color_stop_rgb(1, 0.11, 0.17, 0.24)
    cr.set_source(g); cr.rectangle(0, 0, W, SURF); cr.fill()
    yw = SURF + level * PPF
    g = cairo.LinearGradient(0, yw, 0, SURF + 530 * PPF)
    g.add_color_stop_rgb(0, 0.12, 0.36, 0.52); g.add_color_stop_rgb(1, 0.02, 0.08, 0.15)
    cr.set_source(g); cr.move_to(0, yw)
    for x in range(0, W + 41, 40): cr.line_to(x, yw + 4 * math.sin(x / 70 + t * 2.0))
    cr.line_to(W, H); cr.line_to(0, H); cr.close_path(); cr.fill()
    xs = list(range(0, W + 9, 8))
    yb = lambda x: SURF + shelf_depth((x - X0) / (X1 - X0)) * PPF
    cr.move_to(0, H)
    for x in xs: cr.line_to(x, yb(x))
    cr.line_to(W, H); cr.close_path()
    g = cairo.LinearGradient(0, SURF, 0, H); g.add_color_stop_rgb(0, *SAND); g.add_color_stop_rgb(1, *SAND_D)
    cr.set_source(g); cr.fill()
    cr.set_source_rgba(*CY, 0.5); cr.set_line_width(2); cr.move_to(0, yb(0))
    for x in xs: cr.line_to(x, yb(x))
    cr.stroke()
    if glow:
        a, d0, d1 = glow
        cr.set_source_rgba(*OR, a); cr.set_line_width(6)
        pts = [(x, yb(x)) for x in xs if d0 <= shelf_depth((x - X0) / (X1 - X0)) <= d1 and x > X0]
        if pts:
            cr.move_to(*pts[0])
            for p in pts[1:]: cr.line_to(*p)
            cr.stroke()
    if level > 0:
        cr.set_dash([14, 10]); cr.set_source_rgba(*CY, 0.75); cr.set_line_width(2.5)
        cr.move_to(0, SURF); cr.line_to(X1 + 40, SURF); cr.stroke(); cr.set_dash([])
        font(cr, MONO, 20); text(cr, 'NORMAL WATER LEVEL', 260, SURF - 14, CY, 0.8, tracking=3)
    # the lighthouse on the point
    lx, ly = 60, SURF - 40
    cr.set_source_rgba(0.9, 0.92, 0.92, 1); cr.set_line_width(3)
    for dx in (-14, 14): cr.move_to(lx + dx, ly); cr.line_to(lx + dx * 0.4, ly - 120); cr.stroke()
    for k in range(4):
        yy = ly - 20 - k * 28; cr.move_to(lx - 14 + k * 2.4, yy); cr.line_to(lx + 14 - k * 2.4, yy - 14); cr.stroke()
    cr.rectangle(lx - 3, ly - 120, 6, 120); cr.fill()
    cr.set_source_rgba(0.1, 0.1, 0.1, 1); cr.rectangle(lx - 9, ly - 138, 18, 18); cr.fill()
    cr.set_source_rgba(*GD, 0.9); cr.arc(lx, ly - 129, 5, 0, 2 * math.pi); cr.fill()
    font(cr, MONO, 20); text(cr, 'WHITEFISH POINT', 110, SURF - 70, WH, 0.75, tracking=3)
    text(cr, 'OPEN LAKE SUPERIOR', X1 + 30, SURF - 70, WH, 0.75, 'right', tracking=3)
    hud(cr, t, label, None)


# ---------------------------------------------------------------- card layouts
def big_number(cr, gid, t, d, num, label, sub=None, kicker=None, color=OR, suffix=''):
    backdrop(cr, gid, t, d); hud(cr, t)
    if kicker: mono(cr, kicker, W / 2, 330, 32, CY, align='center', t=t, start=0.0, bold=True)
    v = count(t, 0.05, min(1.0, d * 0.4), num)
    font(cr, HEAD, 280); text(cr, '{:,}'.format(v) + suffix, W / 2, 590, color, ramp(t, 0, 0.25), 'center', tracking=-3)
    mono(cr, label, W / 2, 685, 40, WH, align='center', t=t, start=0.35, bold=True, cps=60)
    if sub: body(cr, sub, W / 2, 752, 34, GR, align='center', t=t, start=0.7)


def title_card(cr, gid, t, d, kicker, title, line=None, size=150, dark=0.42, color=WH):
    backdrop(cr, gid, t, d, dark=dark); hud(cr, t)
    mono(cr, kicker, W / 2, 400, 32, CY, align='center', t=t, start=0.0, bold=True, cps=60)
    head(cr, title, W / 2, 560, size, color, align='center', t=t, start=0.1)
    bar(cr, W / 2 - 260, 605, 520, t, 0.35, color=OR)
    if line: mono(cr, line, W / 2, 680, 32, OR, align='center', t=t, start=0.5, bold=True, cps=60)


KILL = {'THE STORM': OR, 'THE DARK': DK, 'THE COLD': CY}


def killer_cards(cr, t, items, starts, lit=None, y=430, w=440, h=250):
    n = len(items); gap = 50
    x0 = W / 2 - (n * w + (n - 1) * gap) / 2 - 40
    for i, (word, st) in enumerate(zip(items, starts)):
        k = ramp(t, st, 0.35)
        if k <= 0: continue
        col = KILL.get(word, WH)
        on = 1.0 if lit is None else lit[i]
        x = x0 + i * (w + gap); yy = y + 40 * (1 - ease_out(k))
        box(cr, x, yy, w, h, 22, fill=(0.03, 0.05, 0.09), fa=0.9 * k, stroke=col, sa=(0.35 + 0.6 * on) * k, lw=4)
        if on > 0:
            g = cairo.RadialGradient(x + w / 2, yy + h / 2, 10, x + w / 2, yy + h / 2, w * 0.7)
            g.add_color_stop_rgba(0, *col, 0.25 * on * k); g.add_color_stop_rgba(1, *col, 0)
            cr.set_source(g); cr.rectangle(x, yy, w, h); cr.fill()
        font(cr, MONO, 26, bold=True); text(cr, '%d' % (i + 1), x + 30, yy + 52, col, k)
        font(cr, HEAD, 54 if len(word) < 11 else 44); text(cr, word, x + w / 2, yy + 160, WH if on else GR, k, 'center')


def choice_cards(cr, t, items, starts, y=470, w=360, h=220):
    n = len(items); gap = 36
    x0 = W / 2 - (n * w + (n - 1) * gap) / 2 - 40
    for i, (word, st) in enumerate(zip(items, starts)):
        k = ramp(t, st, 0.35)
        if k <= 0: continue
        x = x0 + i * (w + gap); yy = y + 40 * (1 - ease_out(k))
        box(cr, x, yy, w, h, 22, fill=(0.03, 0.05, 0.09), fa=0.9 * k, stroke=CY, sa=0.75 * k, lw=3)
        font(cr, HEAD, 56); text(cr, 'ABCD'[i], x + 32, yy + 76, OR, k)
        font(cr, HEAD, 42 if len(word) < 12 else 36); text(cr, word, x + w / 2, yy + 166, WH, k, 'center')


def comment_cta(cr, t, d, y=820):
    k = ramp(t, d * 0.55, 0.4)
    if k <= 0: return
    p = 1 + 0.05 * math.sin(t * 6)
    cr.save(); cr.translate(W / 2 - 40, y); cr.scale(p, p)
    box(cr, -330, -50, 660, 92, 46, fill=(0.86, 0.13, 0.13), fa=k)
    font(cr, BODY, 40, bold=True); text(cr, 'COMMENT YOUR GUESS  ↓', 0, 14, WH, k, 'center')
    cr.restore()


def sub_anim(cr, gid, t, d, click, line, y=520, kicker=None):
    backdrop(cr, gid, t, d, dark=0.42); hud(cr, t)
    k = ramp(t, 0, 0.4)
    if kicker: mono(cr, kicker, W / 2, y - 170, 32, OR, align='center', t=t, start=0.1, bold=True, cps=50)
    sub_button(cr, W / 2 - 80, y, t, click, k)
    bell(cr, W / 2 + 260, y, 1.3, k, ring=max(0, t - click - 0.5), filled=t > click + 0.5)
    if t > click + 0.5: sonar(cr, W / 2 + 260, y, t - click - 0.5, OR, r0=0.1, rings=2, a=0.9, rmax=90)
    f_in = ramp(t, 0.3, max(0.4, click - 0.3))
    if t <= click: cx, cy = W / 2 - 60 + 300 * (1 - f_in), y + 10 + 220 * (1 - f_in)
    else: f2 = ramp(t, click + 0.15, 0.3); cx, cy = W / 2 - 60 + 320 * f2, y + 10
    cursor(cr, cx, cy, k, press=max(0.0, 1 - min(abs(t - click), abs(t - click - 0.5)) / 0.15))
    mono(cr, line, W / 2, y + 165, 30, WH, align='center', t=t, start=0.6, bold=True, cps=50)


def hull(cr, x0, x1, deck, keel, wl, a=1.0, pellets=False):
    """A long laker in side view: hull from deck to keel, pilothouse forward (right), engine house aft (left)."""
    cr.set_source_rgba(0.16, 0.16, 0.18, a)
    cr.move_to(x0, deck); cr.line_to(x1 - 30, deck); cr.line_to(x1, deck + 30); cr.line_to(x1 - 18, keel); cr.line_to(x0 + 14, keel)
    cr.line_to(x0, keel - 30); cr.close_path(); cr.fill()
    cr.set_source_rgba(0.55, 0.17, 0.13, a); cr.rectangle(x0 + 8, wl, x1 - x0 - 30, keel - wl - 2); cr.fill()
    cr.set_source_rgba(0.9, 0.92, 0.92, a)
    cr.rectangle(x1 - 150, deck - 70, 110, 70); cr.fill(); cr.rectangle(x1 - 130, deck - 100, 70, 30); cr.fill()
    cr.rectangle(x0 + 20, deck - 80, 170, 80); cr.fill()
    cr.set_source_rgba(0.12, 0.12, 0.13, a); cr.rectangle(x0 + 70, deck - 140, 40, 60); cr.fill()
    cr.set_source_rgba(0.35, 0.36, 0.38, a)
    for k in range(10):
        hx = x0 + 230 + k * (x1 - x0 - 420) / 10; cr.rectangle(hx, deck - 8, (x1 - x0 - 420) / 10 - 12, 8); cr.fill()


def waterline(cr, y, a=1.0, wave=0.0, t=0.0):
    g = cairo.LinearGradient(0, y, 0, H); g.add_color_stop_rgba(0, 0.14, 0.40, 0.58, 0.85 * a); g.add_color_stop_rgba(1, 0.03, 0.10, 0.18, 0.95 * a)
    cr.set_source(g); cr.move_to(0, y)
    for x in range(0, W + 41, 40): cr.line_to(x, y + 5 * math.sin(x / 60 + t * 2))
    cr.line_to(W, H); cr.line_to(0, H); cr.close_path(); cr.fill()


# ================================================================ the graphics, in order
@reg('G01')
def g01(cr, t, d):
    v = REGION
    region_map(cr, v, t, 'FILE 05 · 10 NOVEMBER 1975 · 7:10 P.M.')
    point_mark(cr, v, t, 0.1, dy=40)
    wreck_mark(cr, v, t, 0.5, 'EDMUND FITZGERALD')
    a = ramp(t, 1.2, 1.2)
    p0 = v.xy(*PT['point']); p1 = v.xy(*PT['wreck'])
    if a > 0:
        q = (p0[0] + (p1[0] - p0[0]) * a, p0[1] + (p1[1] - p0[1]) * a)
        miles_line(cr, p0, q, '17 MILES' if a > 0.9 else '', 1.0, OR)
    tag(cr, 'SHELTER: WHITEFISH BAY', v.xy(46.62, -84.80)[0] - 60, v.xy(46.62, -84.80)[1] + 40, CY, ramp(t, 2.6, 0.4))
    k = ramp(t, d * 0.6, 0.4)
    if k > 0:
        box(cr, 110, 140, 560, 130, 14, fill=(0.02, 0.04, 0.07), fa=0.88 * k, stroke=OR, sa=0.7 * k)
        font(cr, HEAD, 54); text(cr, 'JUST OVER', 140, 200, WH, k)
        font(cr, HEAD, 54); text(cr, 'AN HOUR AWAY', 140, 254, OR, k)


@reg('G02')
def g02(cr, t, d):
    v3.card_quote(cr, 'G02', t, d, ['"We are holding', 'our own."'], 'CAPT. ERNEST McSORLEY · 7:10 P.M. · 10 NOVEMBER 1975', size=96)


@reg('G03')
def g03(cr, t, d):
    big_number(cr, 'G03', t, d, 29, 'MEN')


@reg('G04')
def g04(cr, t, d):
    big_number(cr, 'G04', t, d, 240, 'SHIPS LOST AROUND WHITEFISH POINT', 'At least, from 1816 to 1975', suffix='+')


@reg('G05')
def g05(cr, t, d):
    v = PRESERVE
    region_map(cr, v, t, 'FILE 05 · DIVERS · SONAR · SHIPWRECK RECORDS')
    sx = -100 + (W + 200) * ease_in_out(ramp(t, 0.2, max(1.5, d - 1.2)))
    cr.save()
    for a in W_LAKES: _poly(cr, v.pts(a))
    cr.clip(); cr.rectangle(0, 0, max(0, sx), H); cr.clip()
    for y in range(0, H, 6):
        cr.set_source_rgba(*CY, 0.08 + 0.08 * math.sin(y * 0.37) ** 2); cr.rectangle(0, y, W, 2); cr.fill()
    for name, ll in WRECKS.items():
        x, y = v.xy(*ll); circle(cr, x, y, 6, OR, 0.9)
    cr.restore()
    g = cairo.LinearGradient(sx - 160, 0, sx, 0); g.add_color_stop_rgba(0, *CY, 0); g.add_color_stop_rgba(1, *CY, 0.35)
    cr.set_source(g); cr.rectangle(sx - 160, 0, 160, H); cr.fill()
    cr.set_source_rgba(*CY, 0.9); cr.rectangle(sx - 2, 0, 3, H); cr.fill()
    for i, s in enumerate(('DIVERS', 'SONAR', '200 YEARS OF RECORDS')):
        k = ramp(t, 0.5 + i * 0.8, 0.3)
        if k <= 0: continue
        box(cr, 120, 170 + i * 84, 470, 62, 10, fill=(0.02, 0.05, 0.09), fa=0.85 * k, stroke=CY, sa=0.6 * k)
        circle(cr, 150, 201 + i * 84, 8, OR, k)
        font(cr, MONO, 28, bold=True); text(cr, s, 176, 211 + i * 84, WH, k, tracking=3)


@reg('G06')
def g06(cr, t, d):
    big_number(cr, 'G06', t, d, 530, 'THE BOTTOM OF THE GRAVEYARD', kicker='WE WILL GO ALL THE WAY DOWN TO', suffix=' FT')


@reg('G07')
def g07(cr, t, d):
    backdrop(cr, 'G07', t, d, dark=0.36); hud(cr, t)
    mono(cr, 'YOU ARE WATCHING', W / 2, 430, 30, CY, align='center', t=t, start=0.0, bold=True, cps=60)
    head(cr, 'GREAT LAKES FILES', W / 2, 580, 140, WH, align='center', t=t, start=0.05)
    bar(cr, W / 2 - 300, 620, 600, t, 0.25)
    mono(cr, 'THE PLACES HIDDEN IN AND UNDER THESE LAKES', W / 2, 690, 28, OR, align='center', t=t, start=0.4, cps=70, bold=True)


@reg('G08')
def g08(cr, t, d):
    sub_anim(cr, 'G08', t, d, 1.2, "IT'S FREE. IT TAKES ONE SECOND.", kicker='FOUND US THROUGH THE FITZGERALD? WELCOME')


@reg('G09')
def g09(cr, t, d):
    v = View(47.35, -86.6, 230)
    basemap(cr, v, labels=False)
    hud(cr, t, 'FILE 05 · LAKE SUPERIOR', None)
    xp, yp = v.xy(*PT['point'])
    routes = [[(46.80, -92.0), (47.30, -89.5), (47.30, -87.0), (46.95, -85.4), PT['point'], PT['soo']],
              [(48.30, -89.1), (47.90, -87.5), (47.35, -86.0), (46.90, -85.2), PT['point'], PT['soo']],
              [(46.90, -88.2), (46.95, -86.8), (46.85, -85.6), PT['point'], PT['soo']]]
    for i, r in enumerate(routes):
        v3.path(cr, v, r, t, 0.6 + i * 0.5, 2.6, OR, 4, a=0.85)
    a = ramp(t, 0.2, 0.4)
    sonar(cr, xp, yp, t - 0.2, WH, a=a, rmax=80)
    tag(cr, 'WHITEFISH POINT', xp - 320, yp - 50, WH, a, size=24)
    x, y = v.xy(47.6, -87.6); font(cr, MONO, 26); text(cr, 'LAKE SUPERIOR', x, y, CY, 0.6, 'center', tracking=8)
    k = ramp(t, d * 0.45, 0.4)
    if k > 0:
        box(cr, W - 1000, 140, 880, 150, 14, fill=(0.02, 0.04, 0.07), fa=0.88 * k, stroke=OR, sa=0.7 * k)
        font(cr, HEAD, 46); text(cr, 'EVERY SHIP IN OR OUT', W - 970, 205, WH, k)
        font(cr, MONO, 24, bold=True); text(cr, 'MORE WRECKS HERE THAN ANYWHERE ON THE LAKE', W - 968, 255, OR, ramp(t, d * 0.65, 0.4), tracking=1)


@reg('G10')
def g10(cr, t, d):
    title_card(cr, 'G10', t, d, 'OFF WHITEFISH POINT', 'THREE KILLERS', size=150)


@reg('G11')
def g11(cr, t, d):
    v = View(47.35, -86.6, 230)
    basemap(cr, v, labels=False)
    hud(cr, t, 'FILE 05 · THE STORM', None)
    xp, yp = v.xy(*PT['point'])
    x0, y0 = v.xy(47.93, -87.94)          # 160 miles northwest of the point
    k = ease_in_out(ramp(t, 0.3, 1.6))
    miles_line(cr, (x0, y0), (x0 + (xp - x0) * k, y0 + (yp - y0) * k), '160 MILES OF OPEN WATER' if k > 0.9 else '', 1.0, CY)
    for j in range(7):
        ph = (t * 0.45 + j / 7) % 1
        sx, sy = x0 + (xp - x0) * ph, y0 + (yp - y0) * ph
        a = math.sin(ph * math.pi) * ramp(t, 1.0, 0.5)
        cr.set_source_rgba(*OR, 0.9 * a); cr.set_line_width(6); cr.set_line_cap(cairo.LINE_CAP_ROUND)
        ang = math.atan2(yp - y0, xp - x0)
        cr.move_to(sx - 60 * math.cos(ang), sy - 60 * math.sin(ang)); cr.line_to(sx, sy); cr.stroke()
    cr.set_line_cap(cairo.LINE_CAP_BUTT)
    tag(cr, 'NORTHWEST GALE', x0 - 40, y0 - 40, OR, ramp(t, 0.8, 0.4), size=26)
    a = ramp(t, d * 0.5, 0.4)
    if a > 0:
        box(cr, 110, 720, 600, 130, 14, fill=(0.02, 0.04, 0.07), fa=0.88 * a, stroke=OR, sa=0.7 * a)
        font(cr, HEAD, 64); text(cr, 'WAVES 30 FT+', 140, 808, OR, a)


@reg('G12')
def g12(cr, t, d):
    backdrop(cr, 'G12', t, d, dark=0.36); hud(cr, t)
    mono(cr, 'REMEMBER THESE THREE', W / 2 - 40, 330, 32, CY, align='center', t=t, start=0.0, bold=True)
    killer_cards(cr, t, ['THE STORM', 'THE DARK', 'THE COLD'], [0.2, 0.9, 1.6])


@reg('G13')
def g13(cr, t, d):
    shelf(cr, t, level=6 * ease_in_out(ramp(t, 0.3, d)))
    head(cr, 'START THE DRAIN', 120, 800, 84, WH, t=t, start=0.05)
    for i in range(3):
        x = 520 + i * 360; ph = (t * 1.6 + i * 0.3) % 1
        cr.set_source_rgba(*OR, 0.9 * (1 - ph)); cr.set_line_width(6)
        y = SURF + 30 + ph * 40
        cr.move_to(x - 18, y - 14); cr.line_to(x, y + 4); cr.line_to(x + 18, y - 14); cr.stroke()


def killer_stamp_card(cr, gid, t, d, killer, name, line, sub=None):
    backdrop(cr, gid, t, d, dark=0.4); hud(cr, t)
    head(cr, name, W / 2, 470, 130, WH, align='center', t=t, start=0.05)
    mono(cr, line, W / 2, 545, 34, GR, align='center', t=t, start=0.25, bold=True, cps=60)
    if sub: body(cr, sub, W / 2, 600, 32, GR, align='center', t=t, start=0.5)
    stamp(cr, killer, W / 2, 720, t, min(0.9, d * 0.35), size=80, color=KILL.get(killer, OR))


@reg('G14')
def g14(cr, t, d):
    killer_stamp_card(cr, 'G14', t, d, 'THE STORM', 'SATURN', 'NOVEMBER 1872 · 7 MEN')


@reg('G15')
def g15(cr, t, d):
    title_card(cr, 'G15', t, d, 'THE WRECK AT 50 FEET', 'MYRON', '186 FT · 23 NOVEMBER 1919', size=170)


@reg('G16')
def g16(cr, t, d):
    v = CLOSE
    region_map(cr, v, t, 'FILE 05 · 23 NOVEMBER 1919', names=False)
    point_mark(cr, v, t, 0.0, dx=30, dy=60)
    xm, ym = v.xy(*PT['myron']); xp, yp = v.xy(*PT['point'])
    a = ramp(t, 0.2, 0.3)
    sonar(cr, xm, ym, t - 0.2, RD, a=a, rmax=90)
    font(cr, HEAD, 36); text(cr, 'MYRON', xm - 26, ym - 26, RD, a, 'right')
    miles_line(cr, (xm, ym + 40), (xp, yp + 40), '1.5 MILES', ramp(t, 0.5, 0.4), WH)


@reg('G17')
def g17(cr, t, d):
    big_number(cr, 'G17', t, d, 1, 'SURVIVOR', '17 men were lost', color=GD)


@reg('G18')
def g18(cr, t, d):
    backdrop(cr, 'G18', t, d, dark=0.4); hud(cr, t)
    head(cr, 'ALL 17 FOUND', W / 2, 480, 140, WH, align='center', t=t, start=0.1)
    mono(cr, 'STILL IN THEIR LIFE JACKETS, COVERED IN ICE', W / 2, 560, 32, CY, align='center', t=t, start=0.5, bold=True)
    stamp(cr, 'THE COLD', W / 2, 700, t, d * 0.35, size=80, color=CY)


@reg('G19')
def g19(cr, t, d):
    backdrop(cr, 'G19', t, d, dark=0.4); hud(cr, t)
    mono(cr, 'THE BARGE THAT SURVIVED THE STORM', W / 2, 360, 30, CY, align='center', t=t, start=0.0, bold=True)
    head(cr, 'MIZTEC', W / 2, 520, 170, WH, align='center', t=t, start=0.15)
    bar(cr, W / 2 - 240, 565, 480, t, 0.4)
    k = ramp(t, d * 0.4, 0.3)
    if k > 0:
        font(cr, HEAD, 72); text(cr, '1921 · ALL 7 LOST', W / 2, 670, RD, k, 'center')


@reg('G20')
def g20(cr, t, d):
    v = PRESERVE
    region_map(cr, v, t, 'FILE 05 · WHITEFISH POINT UNDERWATER PRESERVE')
    point_mark(cr, v, t, 0.0, dx=24, dy=-20, align='right')
    names = list(WRECKS)
    n = int(min(len(names), max(0, (t - 0.4) / max(0.1, d * 0.6) * len(names))))
    for i, nm in enumerate(names[:n]):
        x, y = v.xy(*WRECKS[nm]); a = ramp(t, 0.4 + i * d * 0.6 / len(names), 0.25)
        circle(cr, x, y, 7, OR, a); circle(cr, x, y, 13, OR, 0.35 * a, fill=False, width=2)
    k = ramp(t, 0.3, 0.5)
    box(cr, 110, 150, 540, 170, 14, fill=(0.02, 0.04, 0.07), fa=0.88 * k, stroke=OR, sa=0.6 * k)
    font(cr, HEAD, 60); text(cr, '376 SQ MI', 140, 222, WH, k)
    font(cr, MONO, 22, bold=True); text(cr, 'PROTECTED SINCE 1987', 142, 262, OR, k, tracking=2)
    font(cr, MONO, 18); text(cr, 'DOTS: KNOWN WRECK POSITIONS', 142, 298, GR, k, tracking=2)


@reg('G21')
def g21(cr, t, d):
    backdrop(cr, 'G21', t, d, dark=0.34); hud(cr, t)
    head(cr, 'TAKE A GUESS', W / 2 - 40, 270, 96, WH, align='center', t=t, start=0.0)
    mono(cr, 'WHAT REALLY SANK THE EDMUND FITZGERALD?', W / 2 - 40, 340, 32, OR, align='center', t=t, start=0.3, bold=True)
    choice_cards(cr, t, ['THE STORM', 'THE HATCHES', 'A SHOAL', 'THE SHIP'], [d * 0.18, d * 0.24, d * 0.30, d * 0.36])
    comment_cta(cr, t, d)


@reg('G22')
def g22(cr, t, d):
    backdrop(cr, 'G22', t, d, dark=0.34); hud(cr, t)
    head(cr, 'ONE WORD IS ENOUGH', W / 2 - 40, 330, 90, WH, align='center', t=t, start=0.0)
    comment_box(cr, W / 2 - 600, 450, 1120, 'My guess: ', t, 0.6, cps=9)
    mono(cr, 'AT THE END, SEE IF YOU CHANGED YOUR MIND', W / 2 - 40, 680, 30, OR, align='center', t=t, start=d * 0.45, bold=True)


@reg('G23')
def g23(cr, t, d):
    big_number(cr, 'G23', t, d, 14, 'OF HER 24 CREW DIED', 'John B. Cowle · July 1909', color=RD)


@reg('G24')
def g24(cr, t, d):
    title_card(cr, 'G24', t, d, 'AT 200 FEET · 1875', 'THE COMET', 'THE TREASURE SHIP OF LAKE SUPERIOR', size=170, color=GD)


@reg('G25')
def g25(cr, t, d):
    big_number(cr, 'G25', t, d, 10, 'MEN DIED', color=RD)


@reg('G26')
def g26(cr, t, d):
    big_number(cr, 'G26', t, d, 70, 'TONS OF SILVER ORE', 'From Montana, with 500 tons of pig iron and some copper', color=GD)


@reg('G27')
def g27(cr, t, d):
    backdrop(cr, 'G27', t, d, dark=0.4); hud(cr, t)
    mono(cr, 'SALVAGE ATTEMPTS', W / 2, 360, 30, CY, align='center', t=t, start=0.0, bold=True)
    for i, (yr, st) in enumerate(((1876, 0.15), (1938, 0.7))):
        k = ramp(t, st, 0.3)
        if k <= 0: continue
        x = W / 2 - 230 + i * 460
        font(cr, HEAD, 130); text(cr, str(yr), x, 540, WH, k, 'center')
        font(cr, MONO, 28, bold=True); text(cr, 'WRECK NOT FOUND', x, 600, RD, ramp(t, st + 0.3, 0.3), 'center', tracking=2)


@reg('G28')
def g28(cr, t, d):
    backdrop(cr, 'G28', t, d, dark=0.4); hud(cr, t)
    mono(cr, 'DIVERS FOUND HER IN THE 1970s', W / 2, 380, 30, CY, align='center', t=t, start=0.0, bold=True)
    head(cr, 'THE SILVER ORE', W / 2, 520, 120, GD, align='center', t=t, start=0.15)
    stamp(cr, 'UNKNOWN', W / 2, 690, t, d * 0.35, size=100, color=RD)


@reg('G29')
def g29(cr, t, d):
    lv = 200 + 30 * ease_in_out(ramp(t, 0.2, d))
    shelf(cr, t, level=lv, glow=(ramp(t, 0.5, 0.5), 200, 275))
    head(cr, 'THE BAY FALLS AWAY', 120, 800, 76, WH, t=t, start=0.1)
    tag(cr, 'DEEPEST POINT OF THE PRESERVE: ABOUT 270 FT', 560, SURF + 300 * PPF + 70, OR, ramp(t, 0.8, 0.4))


@reg('G30')
def g30(cr, t, d):
    backdrop(cr, 'G30', t, d, dark=0.4); hud(cr, t)
    mono(cr, 'SUPERIOR CITY · LAUNCHED 1898', W / 2, 380, 30, CY, align='center', t=t, start=0.0, bold=True)
    head(cr, 'THE LARGEST SHIP', W / 2, 520, 120, WH, align='center', t=t, start=0.15)
    head(cr, 'EVER BUILT ON FRESH WATER', W / 2, 630, 80, OR, align='center', t=t, start=0.5)


@reg('G31')
def g31(cr, t, d):
    backdrop(cr, 'G31', t, d); hud(cr, t)
    mono(cr, 'WHITEFISH BAY', 220, 400, 28, CY, t=t, start=0.0, bold=True)
    head(cr, '9:10 P.M.', 214, 560, 170, WH, t=t, start=0.1)
    bar(cr, 220, 605, 560, t, 0.4)
    mono(cr, '20 AUGUST 1920 · 7,600 TONS OF IRON ORE', 222, 680, 34, OR, t=t, start=0.6, bold=True)


@reg('G32')
def g32(cr, t, d):
    big_number(cr, 'G32', t, d, 29, 'PEOPLE DIED', '28 men and one woman · only 4 survived', color=RD)


@reg('G33')
def g33(cr, t, d):
    backdrop(cr, 'G33', t, d, dark=0.38); hud(cr, t)
    head(cr, 'THE WORST COLLISION', W / 2, 400, 110, WH, align='center', t=t, start=0.05)
    mono(cr, "IN LAKE SUPERIOR'S HISTORY", W / 2, 470, 34, GR, align='center', t=t, start=0.4, bold=True)
    stamp(cr, 'THE DARK', W / 2 - 250, 640, t, d * 0.35, size=70, color=DK, angle=-0.06)
    stamp(cr, 'THE COLD', W / 2 + 250, 640, t, d * 0.55, size=70, color=CY, angle=0.05)


@reg('G34')
def g34(cr, t, d):
    background(cr); hud(cr, t)
    k = ramp(t, 0.1, 0.6)
    g = cairo.RadialGradient(W / 2, 520, 10, W / 2, 520, 420)
    g.add_color_stop_rgba(0, *OR, 0.35 * k); g.add_color_stop_rgba(1, *OR, 0)
    cr.set_source(g); cr.paint()
    font(cr, HEAD, 360); text(cr, '29', W / 2, 650, WH, k, 'center', tracking=-4)


@reg('G35')
def g35(cr, t, d):
    v = REGION
    region_map(cr, v, t, 'FILE 05 · 10 NOVEMBER 1975', border=True)
    point_mark(cr, v, t, 0.0, dy=40)
    a = ramp(t, 0.3, 1.0)
    p0 = v.xy(*PT['point']); p1 = v.xy(*PT['wreck'])
    if a > 0:
        q = (p0[0] + (p1[0] - p0[0]) * a, p0[1] + (p1[1] - p0[1]) * a)
        miles_line(cr, p0, q, '17 MILES' if a > 0.9 else '', 1.0, OR)
    wreck_mark(cr, v, t, 1.2, 'EDMUND FITZGERALD', '530 FT DOWN')
    k = ramp(t, 2.0, 0.4)
    xb, yb = v.xy(47.10, -84.75)
    tag(cr, 'CANADIAN WATERS', xb, yb, WH, k)
    tag(cr, 'US WATERS', v.xy(46.70, -85.55)[0], v.xy(46.70, -85.55)[1], WH, k)


@reg('G36')
def g36(cr, t, d):
    title_card(cr, 'G36', t, d, '530 FEET DOWN', 'EDMUND FITZGERALD', '729 FT · 10 NOVEMBER 1975', size=130)


@reg('G37')
def g37(cr, t, d):
    backdrop(cr, 'G37', t, d, dark=0.36); hud(cr, t)
    mono(cr, 'ON HER LAST NIGHT', W / 2 - 40, 330, 32, CY, align='center', t=t, start=0.0, bold=True)
    killer_cards(cr, t, ['THE STORM', 'THE DARK', 'THE COLD'], [0.1, 0.2, 0.3],
                 lit=[ramp(t, d * 0.35, 0.3), ramp(t, d * 0.55, 0.3), ramp(t, d * 0.75, 0.3)])


@reg('G38')
def g38(cr, t, d):
    backdrop(cr, 'G38', t, d, dark=0.38); hud(cr, t)
    mono(cr, '4:39 P.M. · HER CAPTAIN ASKS', W / 2, 380, 30, CY, align='center', t=t, start=0.0, bold=True, cps=60)
    head(cr, 'WHITEFISH POINT', W / 2, 500, 110, WH, align='center', t=t, start=0.05)
    head(cr, 'RADIO BEACON', W / 2, 600, 80, GR, align='center', t=t, start=0.2)
    stamp(cr, 'OFF', W / 2, 740, t, min(0.8, d * 0.35), size=100, color=RD)


@reg('G39')
def g39(cr, t, d):
    backdrop(cr, 'G39', t, d, dark=0.36); hud(cr, t)
    for i, (name, yr, st) in enumerate((('SUPERIOR CITY', '1920', 0.1), ('EDMUND FITZGERALD', '1975', d * 0.35))):
        k = ramp(t, st, 0.4)
        if k <= 0: continue
        x = W / 2 - 400 + i * 800
        font(cr, HEAD, 220); text(cr, '29', x, 560, OR, k, 'center')
        font(cr, MONO, 30, bold=True); text(cr, name, x, 640, WH, k, 'center', tracking=2)
        font(cr, MONO, 26); text(cr, yr, x, 690, GR, k, 'center', tracking=2)
    k = ramp(t, d * 0.6, 0.3)
    font(cr, HEAD, 140); text(cr, '=', W / 2, 545, WH, k, 'center')


@reg('G40')
def g40(cr, t, d):
    like_anim(cr, 'G40', t, d)


@reg('G41')
def g41(cr, t, d):
    backdrop(cr, 'G41', t, d, dark=0.36); hud(cr, t)
    killer_cards(cr, t, ['THE STORM', 'THE DARK', 'THE COLD', '?'], [0.0, 0.0, 0.0, 0.5], lit=[0.3, 0.3, 0.3, 1.0], w=340, h=220)
    head(cr, 'A FOURTH KILLER?', W / 2 - 40, 330, 90, WH, align='center', t=t, start=0.6)


@reg('G42')
def g42(cr, t, d):
    title_card(cr, 'G42', t, d, 'THE FOURTH SUSPECT', 'THE SHIP HERSELF', size=130)


def hull_scene(cr, t, label, wl, freeboard_label=None, marks=None, extra=None):
    background(cr); hud(cr, t, label, None)
    deck = 400; keel = 640
    x0, x1 = 170, 1640
    hull(cr, x0, x1, deck, keel, wl)
    waterline(cr, wl, t=t)
    if marks:
        for (y, yr, a) in marks:
            if a <= 0: continue
            cr.set_source_rgba(*OR, a); cr.set_line_width(3); cr.move_to(x0 - 10, y); cr.line_to(x0 + 60, y); cr.stroke()
            pass
    if freeboard_label:
        s, a = freeboard_label
        dim_v(cr, x0 + 330, deck, wl, s, a, CY)
    if extra: extra()


@reg('G43')
def g43(cr, t, d):
    hull_scene(cr, t, 'FILE 05 · HOW SHE WAS DESIGNED', 520, ('FREEBOARD', ramp(t, 1.0, 0.5)))
    head(cr, 'FREEBOARD', 120, 220, 84, WH, t=t, start=0.3)
    mono(cr, 'HOW MUCH HULL STAYS ABOVE THE WATER', 124, 270, 26, CY, t=t, start=0.7, bold=True)


@reg('G44')
def g44(cr, t, d):
    steps = [(0.0, 520), (d * 0.25, 520 + 14), (d * 0.42, 520 + 28), (d * 0.58, 520 + 42)]
    wl = 520
    for st, y in steps:
        if t > st: wl = wl + (y - wl) * ease_out(ramp(t, st, 0.6))
    marks = [(520 + 14, '1969', ramp(t, d * 0.25, 0.3)), (520 + 28, '1971', ramp(t, d * 0.42, 0.3)), (520 + 42, '1973', ramp(t, d * 0.58, 0.3))]
    hull_scene(cr, t, 'FILE 05 · HER LOAD LINE RAISED', wl, ('FREEBOARD', 1.0), marks)
    head(cr, 'RIDING DEEPER', 120, 220, 84, WH, t=t, start=0.1)
    yrs = ' · '.join(y for st, y in ((d * 0.25, '1969'), (d * 0.42, '1971'), (d * 0.58, '1973')) if t > st)
    if yrs:
        font(cr, MONO, 28, bold=True); text(cr, 'LOAD LINE RAISED: ' + yrs, 124, 275, OR, 1.0, tracking=2)
    k = ramp(t, d * 0.72, 0.4)
    if k > 0:
        box(cr, 110, 720, 760, 130, 14, fill=(0.02, 0.04, 0.07), fa=0.88 * k, stroke=OR, sa=0.7 * k)
        font(cr, HEAD, 52); text(cr, '3 FT 3 IN LESS', 140, 790, OR, k)
        font(cr, MONO, 22, bold=True); text(cr, 'FREEBOARD THAN SHE WAS DESIGNED FOR', 142, 828, WH, k, tracking=1)


@reg('G45')
def g45(cr, t, d):
    def wave():
        k = ease_out(ramp(t, 0.6, 1.2))
        if k <= 0: return
        x = 1500 - 260 * k; top = 562 - 35 * 9.5
        cr.set_source_rgba(0.75, 0.88, 0.95, 0.8)
        cr.move_to(x - 260, 562); cr.curve_to(x - 120, 560, x - 60, top + 60, x, top)
        cr.curve_to(x + 60, top + 40, x + 120, 520, x + 300, 562); cr.close_path(); cr.fill()
        dim_v(cr, x + 200, top, 562, '35 FT', ramp(t, 1.6, 0.4), RD)
    hull_scene(cr, t, 'FILE 05 · 10 NOVEMBER 1975', 562, ('11.5 FT', ramp(t, 0.3, 0.4)), extra=wave)
    head(cr, 'HER LAST NIGHT', 120, 220, 84, WH, t=t, start=0.1)


@reg('G46')
def g46(cr, t, d):
    backdrop(cr, 'G46', t, d, dark=0.38); hud(cr, t)
    mono(cr, 'HER STEWARD: "A LOOSE KEEL", WELDS BROKEN', W / 2, 380, 30, CY, align='center', t=t, start=0.0, bold=True, cps=60)
    stamp(cr, 'NEVER CALLED', W / 2, 560, t, 0.5, size=96, color=RD)
    mono(cr, 'TO THE OFFICIAL INQUIRY', W / 2, 700, 34, WH, align='center', t=t, start=1.0, bold=True)


@reg('G47')
def g47(cr, t, d):
    v3.card_quote(cr, 'G47', t, d, ['"Not seaworthy."'], 'ONE OF THE ENGINEERS WHO HELPED DESIGN HER HULL · ON 10 NOVEMBER 1975', size=110)


@reg('G48')
def g48(cr, t, d):
    backdrop(cr, 'G48', t, d, dark=0.36); hud(cr, t)
    k = ramp(t, 0.1, 0.4)
    box(cr, 160, 300, 760, 360, 20, fill=(0.03, 0.05, 0.09), fa=0.88 * k, stroke=CY, sa=0.8 * k, lw=3)
    font(cr, MONO, 28, bold=True); text(cr, 'THE OFFICIAL ANSWER', 200, 370, CY, k, tracking=3)
    font(cr, HEAD, 64); text(cr, 'WATER THROUGH', 200, 480, WH, k)
    font(cr, HEAD, 64); text(cr, 'THE HATCH COVERS', 200, 560, WH, k)
    k2 = ramp(t, d * 0.25, 0.4)
    box(cr, 980, 300, 680, 360, 20, fill=(0.03, 0.05, 0.09), fa=0.88 * k2, stroke=OR, sa=0.8 * k2, lw=3)
    font(cr, MONO, 28, bold=True); text(cr, 'OTHERS BLAME', 1020, 370, OR, k2, tracking=3)
    for i, s in enumerate(('THE WAVES', 'A SHOAL', 'HER OWN HULL')):
        ki = ramp(t, d * 0.3 + i * 0.4, 0.3)
        font(cr, HEAD, 52); text(cr, s, 1020, 460 + i * 74, WH, ki)
    k3 = ramp(t, d * 0.55, 0.4)
    if k3 > 0:
        tag(cr, 'THE WRECK CANNOT SETTLE IT', W / 2 - 270, 760, GR, k3, size=28)


@reg('G49')
def g49(cr, t, d):
    backdrop(cr, 'G49', t, d, dark=0.4); hud(cr, t)
    bell(cr, W / 2, 400, 2.2, ramp(t, 0.0, 0.4), filled=True)
    head(cr, 'A REPLICA', W / 2, 600, 110, GD, align='center', t=t, start=0.2)
    mono(cr, 'ENGRAVED WITH THE NAMES OF ALL 29 MEN', W / 2, 680, 32, WH, align='center', t=t, start=0.6, bold=True)


@reg('G50')
def g50(cr, t, d):
    backdrop(cr, 'G50', t, d, dark=0.36); hud(cr, t)
    head(cr, 'YOUR STORIES', W / 2 - 40, 320, 96, WH, align='center', t=t, start=0.0)
    mono(cr, 'SAILED PAST WHITEFISH POINT? DIVED THESE WRECKS?', W / 2 - 40, 390, 30, OR, align='center', t=t, start=0.3, bold=True)
    comment_box(cr, W / 2 - 600, 470, 1120, 'Tell me yours in the comments', t, 0.9, cps=14)


@reg('G51')
def g51(cr, t, d):
    backdrop(cr, 'G51', t, d, dark=0.34); hud(cr, t)
    head(cr, 'YOUR VERDICT', W / 2 - 40, 270, 96, WH, align='center', t=t, start=0.0)
    mono(cr, 'WHAT SANK THE EDMUND FITZGERALD?', W / 2 - 40, 340, 32, OR, align='center', t=t, start=0.3, bold=True)
    choice_cards(cr, t, ['THE WAVES', 'THE HATCHES', 'A SHOAL', 'THE SHIP'], [0.6, 1.2, 1.8, 2.4])


@reg('G52')
def g52(cr, t, d):
    backdrop(cr, 'G52', t, d, dark=0.34); hud(cr, t)
    head(cr, 'CHANGED YOUR MIND?', W / 2 - 40, 330, 90, WH, align='center', t=t, start=0.0)
    comment_box(cr, W / 2 - 600, 450, 1120, 'My verdict: ', t, 0.6, cps=10)
    mono(cr, 'I READ EVERY ONE', W / 2 - 40, 680, 32, OR, align='center', t=t, start=d * 0.4, bold=True)


@reg('G53')
def g53(cr, t, d):
    sub_anim(cr, 'G53', t, d, d * 0.5, 'MORE GRAVEYARDS ARE HIDDEN IN THESE LAKES', kicker='YOU WATCHED ALL THE WAY HERE')


@reg('G54')
def g54(cr, t, d):
    backdrop(cr, 'G54', t, d, blur=4, dark=0.62)
    g = cairo.LinearGradient(0, 0, W * 0.6, 0); g.add_color_stop_rgba(0, 0.01, 0.02, 0.05, 0.85); g.add_color_stop_rgba(1, 0.01, 0.02, 0.05, 0)
    cr.set_source(g); cr.paint()
    hud(cr, t, 'GREAT LAKES FILES', None)
    mono(cr, 'END OF FILE 05', 140, 360, 30, OR, t=t, start=0.2, bold=True)
    head(cr, 'THANKS FOR', 134, 500, 110, WH, t=t, start=0.4)
    head(cr, 'WATCHING', 134, 620, 110, WH, t=t, start=0.6)
    mono(cr, 'WATCH THE NEXT FILE  →', 140, 740, 32, CY, t=t, start=1.4, bold=True)
    mono(cr, 'SUBSCRIBE SO YOU DON\'T MISS IT', 140, 800, 28, WH, t=t, start=2.0, bold=True)
