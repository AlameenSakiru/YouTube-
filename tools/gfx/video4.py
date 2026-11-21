"""Every graphic in video 4 (We Drained the Water Under the Mackinac Bridge), keyed by its G number in
video-04/edit-plan.json. Selected by render.py when GFX_SET=video4.

Same "case file" building blocks as video 3 (blurred backdrop, sonar frame, heavy type), in a brighter look:
sky blue and gold instead of cyan and orange, lighter backdrops, and the drained lake bed in warm sand.
Graphics keep the bottom of the frame clear for the burned-in captions, and the right edge clear for the depth meter.
Maps of the Straits use the full-resolution GSHHS coastline (basemap-data-hires).
"""
import math, os, json
import numpy as np
import cairo
from style import *
import maps
from maps import View, PLACES, LAKES, ISLANDS, UPPER, basemap, _poly, _load
import video3 as v3

G = {}
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
V4 = os.path.join(ROOT, 'video-04')

# ---------------------------------------------------------------- re-point the video 3 helpers at video 4
_OLD = {'OR': v3.OR, 'CY': v3.CY}
OR = (1.0, 0.79, 0.24)          # gold
CY = (0.31, 0.76, 0.97)         # sky blue
WH = (0.95, 0.97, 0.97)
GR = (0.70, 0.79, 0.82)
RD = (1.0, 0.36, 0.26)
GN = (0.36, 0.86, 0.55)
SAND = (0.55, 0.44, 0.30)
SAND_D = (0.30, 0.23, 0.16)
HEAD, MONO, BODY = v3.HEAD, v3.MONO, v3.BODY
_swap = {_OLD['OR']: OR, _OLD['CY']: CY}
v3.OR, v3.CY, v3.WH, v3.GR = OR, CY, WH, GR
v3.V3 = V4
for _f in list(vars(v3).values()):
    if callable(_f) and getattr(_f, '__module__', '') == 'video3' and getattr(_f, '__defaults__', None):
        _f.__defaults__ = tuple(_swap.get(x, x) if isinstance(x, tuple) else x for x in _f.__defaults__)
v3.hud.__defaults__ = ('FILE 04 · MACKINAC BRIDGE', None, 1.0)
v3.backdrop.__defaults__ = (14, 0.5, None)
v3.BACK = v3._prev_images()
BACK = v3.BACK

from PIL import Image, ImageFilter, ImageEnhance
_SURF4 = {}


def _bg4(n, blur, dark):
    d = os.path.join(V4, 'build', 'bg'); os.makedirs(d, exist_ok=True)
    out = os.path.join(d, 'v4-%03d-%d-%d.png' % (n, blur, int(dark * 100)))
    if not os.path.exists(out):
        cf = os.path.join(V4, 'images', 'crops.json')
        crops = json.load(open(cf)) if os.path.exists(cf) else {}
        im = Image.open(os.path.join(V4, 'images', '%03d.jpg' % n)).convert('RGB')
        if '%03d' % n in crops: im = im.crop(tuple(crops['%03d' % n]))
        w, h = im.size
        if w / h > 16 / 9: nw = int(h * 16 / 9); im = im.crop(((w - nw) // 2, 0, (w - nw) // 2 + nw, h))
        im = im.resize((2112, 1188), Image.LANCZOS)
        if blur: im = im.filter(ImageFilter.GaussianBlur(blur))
        im = ImageEnhance.Brightness(im).enhance(dark)
        im = ImageEnhance.Color(im).enhance(1.15)
        a = np.asarray(im, np.float32) * np.array([0.95, 0.99, 1.03])
        Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).save(out)
    return out


def backdrop(cr, gid, t, d, blur=14, dark=0.62, n=None):
    """Video 4: the scene the graphic follows, blurred, lighter than video 3, with a soft centre shade for the type."""
    n = n or BACK.get(gid, 1)
    key = (n, blur, dark)
    if key not in _SURF4: _SURF4[key] = cairo.ImageSurface.create_from_png(_bg4(n, blur, dark))
    s = _SURF4[key]
    z = 1.0 + 0.05 * (t / max(d, 0.1))
    cr.save(); cr.translate(W / 2, H / 2); cr.scale(z * W / 2112, z * H / 1188)
    cr.translate(-2112 / 2, -1188 / 2); cr.set_source_surface(s, 0, 0); cr.paint(); cr.restore()
    g = cairo.RadialGradient(W / 2, H / 2, 100, W / 2, H / 2, W * 0.7)
    g.add_color_stop_rgba(0, 0.0, 0.03, 0.05, 0.30); g.add_color_stop_rgba(0.6, 0.0, 0.03, 0.05, 0.18)
    g.add_color_stop_rgba(1, 0.0, 0.03, 0.05, 0.5)
    cr.set_source(g); cr.paint()


v3.backdrop = backdrop
from video3 import (hud, head, mono, body, bar, box, stamp, count, sonar, cursor, bell, thumb, sub_button,
                    like_anim, comment_box, dim_v, miles_line)


def reg(gid):
    def deco(fn):
        G[gid] = fn; return fn
    return deco


# ---------------------------------------------------------------- Straits of Mackinac, full-resolution coastline
def _near(a, la0=45.35, la1=46.25, lo0=-85.6, lo1=-83.8):
    return ((a[:, 1] > la0) & (a[:, 1] < la1) & (a[:, 0] > lo0) & (a[:, 0] < lo1)).any()


_FULL = _load('gshhs', 'f')
S_LAKES = [a for lvl, a in _FULL if lvl == 2 and len(a) > 40 and _near(a)]
S_ISL = [a for lvl, a in _FULL if lvl == 3 and _near(a)]
del _FULL

CED_TRACK = [(45.845, -84.52), (45.830, -84.565), (45.812, -84.600), (45.800, -84.618)]
P = {
    'bridge_s': (45.788, -84.7275), 'bridge_n': (45.8535, -84.7255),
    'cedarville': (45.787, -84.671), 'collision': (45.800, -84.618),
    'rockmaze': (45.861, -84.597), 'line5_s': (45.799, -84.766), 'line5_n': (45.861, -84.768),
}
STRAITS = View(45.817, -84.70, 5200)
EASTV = View(45.806, -84.655, 7400)
WESTV = View(45.826, -84.742, 7200)
WIDEV = View(45.815, -84.68, 3300)
BED = (0.52, 0.42, 0.29)


def grid_s(cr, v, a=0.16):
    cr.set_line_width(1); cr.set_source_rgba(*CY, a)
    for lat in np.arange(45.60, 46.05, 0.05):
        _, y = v.xy(lat, -84.7); cr.move_to(0, y); cr.line_to(W, y); cr.stroke()
    for lon in np.arange(-85.2, -84.2, 0.1):
        x, _ = v.xy(45.8, lon); cr.move_to(x, 0); cr.line_to(x, H); cr.stroke()


def straits(cr, v, t, band=0.0, label='FILE 04 · STRAITS OF MACKINAC', names=True, name_a=1.0, water=WATER):
    """The Straits map. band > 0 draws the lake bed exposed by the drain as a sand band inside the old shoreline."""
    cr.set_source_rgb(*LAND); cr.paint()
    for a in S_LAKES:
        _poly(cr, v.pts(a)); cr.set_source_rgb(*water); cr.fill()
    if band > 0:
        cr.save()
        for a in S_LAKES: _poly(cr, v.pts(a))
        cr.clip()
        cr.set_line_join(cairo.LINE_JOIN_ROUND)
        for lw, col, al in ((2 * band + 4, CY, 0.8), (2 * band, BED, 1.0)):
            cr.set_line_width(lw); cr.set_source_rgba(*col, al)
            for a in S_LAKES + S_ISL:
                _poly(cr, v.pts(a)); cr.stroke()
        cr.restore()
    for a in S_ISL:
        _poly(cr, v.pts(a)); cr.set_source_rgb(*LAND); cr.fill()
    cr.set_line_width(1.8); cr.set_source_rgba(*COAST, 0.85 if band <= 0 else 0.35)
    for a in S_LAKES + S_ISL:
        _poly(cr, v.pts(a)); cr.stroke()
    g = cairo.RadialGradient(W / 2, H / 2, 300, W / 2, H / 2, W * 0.75)
    g.add_color_stop_rgba(0, 0, 0, 0, 0); g.add_color_stop_rgba(1, 0, 0.02, 0.04, 0.55)
    cr.set_source(g); cr.paint()
    grid_s(cr, v)
    if names:
        font(cr, MONO, 22)
        for s, (la, lo), al in (('ST. IGNACE', (45.872, -84.735), 'center'), ('MACKINAW CITY', (45.772, -84.735), 'center'),
                                ('MACKINAC ISLAND', (45.885, -84.625), 'center'), ('LAKE MICHIGAN', (45.815, -84.90), 'center'),
                                ('LAKE HURON', (45.835, -84.48), 'center'), ('BOIS BLANC ISLAND', (45.775, -84.50), 'center')):
            x, y = v.xy(la, lo)
            if 80 < x < W - 80 and 80 < y < H - 200:
                text(cr, s, x, y, WH if 'LAKE' not in s else CY, 0.7 * name_a, al, tracking=4)
    hud(cr, t, label, None)


def bridge(cr, v, t, start=0.0, label=True, a=1.0):
    k = ramp(t, start, 0.6) * a
    if k <= 0: return
    x0, y0 = v.xy(*P['bridge_s']); x1, y1 = v.xy(*P['bridge_n'])
    cr.set_line_cap(cairo.LINE_CAP_ROUND)
    cr.set_source_rgba(0, 0, 0, 0.5 * k); cr.set_line_width(11); cr.move_to(x0, y0); cr.line_to(x1, y1); cr.stroke()
    cr.set_source_rgba(*WH, k); cr.set_line_width(6)
    cr.move_to(x0, y0); cr.line_to(x0 + (x1 - x0) * ease_out(ramp(t, start, 0.8)), y0 + (y1 - y0) * ease_out(ramp(t, start, 0.8))); cr.stroke()
    for f in (0.40, 0.60):
        circle(cr, x0 + (x1 - x0) * f, y0 + (y1 - y0) * f, 9, OR, k)
    cr.set_line_cap(cairo.LINE_CAP_BUTT)
    if label:
        font(cr, MONO, 22, bold=True)
        text(cr, 'MACKINAC BRIDGE', (x0 + x1) / 2 + 26, (y0 + y1) / 2 + 8, WH, 0.9 * k, tracking=3)


def line5(cr, v, t, start=0.0, dur=1.6, a=1.0, label=True):
    for off in (-5, 5):
        p0 = v.xy(*P['line5_s']); p1 = v.xy(*P['line5_n'])
        p0 = (p0[0] + off, p0[1]); p1 = (p1[0] + off, p1[1])
        k = ease_in_out(ramp(t, start, dur))
        if k <= 0: return
        cr.set_source_rgba(0, 0, 0, 0.5 * a); cr.set_line_width(7)
        cr.move_to(*p0); cr.line_to(p0[0] + (p1[0] - p0[0]) * k, p0[1] + (p1[1] - p0[1]) * k); cr.stroke()
        cr.set_source_rgba(*OR, a); cr.set_line_width(4)
        cr.move_to(*p0); cr.line_to(p0[0] + (p1[0] - p0[0]) * k, p0[1] + (p1[1] - p0[1]) * k); cr.stroke()
    if label:
        x, y = v.xy(45.838, -84.767)
        font(cr, HEAD, 44); text(cr, 'LINE 5', x + 24, y, OR, a * ramp(t, start + dur * 0.6, 0.4))


def mark(cr, v, latlon, t, start, lab, sub=None, color=OR, dx=24, dy=-14, align='left', ring=True):
    a = ramp(t, start, 0.4)
    if a <= 0: return
    x, y = v.xy(*latlon)
    if ring: sonar(cr, x, y, t - start, color, a=a, rmax=90)
    else: circle(cr, x, y, 8, color, a)
    font(cr, HEAD, 34)
    xx = x + dx if align == 'left' else x - dx
    text(cr, lab, xx, y + dy, color, a, align)
    if sub:
        font(cr, MONO, 22); text(cr, sub, xx, y + dy + 32, WH, 0.85 * a, align, tracking=2)


# ---------------------------------------------------------------- cross-section under the bridge (not to scale)
SURF = 300
PPF = 1.55
X0, X1 = 110, 1690          # keep clear of the depth meter on the right


def depth_at(u, maxd=250):
    if u <= 0.03 or u >= 0.97:
        e = min(abs(u - 0.03), abs(u - 0.97)) if (u <= 0.03 or u >= 0.97) else 0
        return -min(40, 900 * e)
    s = ss(0.03, 0.2, u) * ss(0.97, 0.8, u)
    c = math.exp(-((u - 0.5) / 0.13) ** 2)
    shelf = 75
    return shelf * s + (maxd - shelf) * c + 5 * math.sin(u * 47) * s


def ss(a, b, x):
    f = min(1, max(0, (x - a) / (b - a))); return f * f * (3 - 2 * f)


def bed_y(x, maxd=250):
    u = (x - X0) / (X1 - X0)
    return SURF + depth_at(u, maxd) * PPF


def section(cr, t, level=0.0, maxd=250, bridge_on=True, label='FILE 04 · UNDER THE BRIDGE · NOT TO SCALE', canyon=0.0,
            pipes=0.0, towers_down=0.0):
    background(cr)
    g = cairo.LinearGradient(0, 0, 0, SURF)
    g.add_color_stop_rgb(0, 0.04, 0.09, 0.14); g.add_color_stop_rgb(1, 0.10, 0.20, 0.27)
    cr.set_source(g); cr.rectangle(0, 0, W, SURF); cr.fill()
    yw = SURF + level * PPF
    # water
    g = cairo.LinearGradient(0, yw, 0, SURF + maxd * PPF)
    g.add_color_stop_rgb(0, 0.10, 0.45, 0.62); g.add_color_stop_rgb(1, 0.03, 0.16, 0.26)
    cr.set_source(g)
    cr.move_to(0, yw)
    for x in range(0, W + 41, 40): cr.line_to(x, yw + 4 * math.sin(x / 70 + t * 2.0))
    cr.line_to(W, H); cr.line_to(0, H); cr.close_path(); cr.fill()
    # ground
    cr.move_to(0, H)
    xs = list(range(0, W + 9, 8))
    for x in xs: cr.line_to(x, bed_y(x, maxd))
    cr.line_to(W, H); cr.close_path()
    g = cairo.LinearGradient(0, SURF, 0, H)
    g.add_color_stop_rgb(0, *BED); g.add_color_stop_rgb(1, *SAND_D)
    cr.set_source(g); cr.fill()
    # wet, exposed lake bed above the new waterline
    if level > 0:
        cr.set_line_width(6); cr.set_source_rgba(0.80, 0.68, 0.50, 0.9)
        started = False
        for x in xs:
            y = bed_y(x, maxd)
            if SURF - 2 < y < yw:
                if not started: cr.move_to(x, y); started = True
                else: cr.line_to(x, y)
            elif started:
                cr.stroke(); started = False
        if started: cr.stroke()
    cr.set_source_rgba(*CY, 0.5); cr.set_line_width(2)
    cr.move_to(0, bed_y(0, maxd))
    for x in xs: cr.line_to(x, bed_y(x, maxd))
    cr.stroke()
    if canyon > 0:
        cr.save(); cr.set_source_rgba(*OR, canyon); cr.set_line_width(6)
        pts = [(x, bed_y(x, maxd)) for x in xs if 0.25 < (x - X0) / (X1 - X0) < 0.75]
        cr.move_to(*pts[0])
        for p in pts[1:]: cr.line_to(*p)
        cr.stroke(); cr.restore()
    # the old waterline
    cr.set_dash([14, 10]); cr.set_source_rgba(*CY, 0.75 if level > 0 else 0.0); cr.set_line_width(2.5)
    cr.move_to(0, SURF); cr.line_to(X1 + 40, SURF); cr.stroke(); cr.set_dash([])
    if level > 0:
        font(cr, MONO, 20); text(cr, 'NORMAL WATER LEVEL', 120, SURF - 14, CY, 0.8, tracking=3)
    if pipes > 0: pipe_line(cr, maxd, pipes)
    if bridge_on: span(cr, towers_down)
    font(cr, MONO, 20)
    text(cr, 'SOUTH · MACKINAW CITY', 90, SURF - 104, WH, 0.75, tracking=3)
    text(cr, 'NORTH · ST. IGNACE', X1 + 30, SURF - 104, WH, 0.75, 'right', tracking=3)
    hud(cr, t, label, None)


def tag(cr, s, x, y, col, a, size=22):
    if a <= 0: return
    font(cr, MONO, size, bold=True); w = text_width(cr, s, 2)
    box(cr, x - 12, y - size - 6, w + 24, size + 20, 6, fill=(0.02, 0.06, 0.08), fa=0.85 * a)
    text(cr, s, x, y, col, a, tracking=2)


def span(cr, down=0.0):
    """The bridge in side view: deck, two towers and their foundations, main cables."""
    deck = SURF - 78
    tx = [X0 + (X1 - X0) * f for f in (0.40, 0.60)]
    top = SURF - 200
    cr.set_source_rgba(0.85, 0.88, 0.88, 1)
    cr.rectangle(X0 - 20, deck, X1 - X0 + 40, 9); cr.fill()
    for x in tx:
        cr.set_source_rgba(0.86, 0.89, 0.88, 1)
        cr.rectangle(x - 12, top, 9, deck - top + 10); cr.fill(); cr.rectangle(x + 3, top, 9, deck - top + 10); cr.fill()
        for yy in (top + 10, top + 70, top + 130): cr.rectangle(x - 12, yy, 24, 7); cr.fill()
        cr.rectangle(x - 10, deck, 20, SURF - deck); cr.fill()
        fy = SURF + 210 * PPF
        cr.set_source_rgba(0.62, 0.64, 0.63, 1); cr.rectangle(x - 34, SURF, 68, fy - SURF); cr.fill()
        cr.set_source_rgba(*OR, 0.9 * down); cr.set_line_width(4); cr.rectangle(x - 34, SURF, 68, fy - SURF); cr.stroke()
    cr.set_source_rgba(0.85, 0.88, 0.88, 0.95); cr.set_line_width(3)
    a0, a1 = X0 + 30, X1 - 30
    cr.move_to(a0, deck - 4); cr.curve_to(a0 + 200, deck - 40, tx[0] - 80, top + 60, tx[0], top + 4)
    cr.curve_to(tx[0] + 120, deck - 10, tx[1] - 120, deck - 10, tx[1], top + 4)
    cr.curve_to(tx[1] + 80, top + 60, a1 - 200, deck - 40, a1, deck - 4); cr.stroke()


def pipe_line(cr, maxd, a):
    """Line 5 lying on the bed; buried (dashed) where the water is shallower than 65 ft."""
    xs = list(range(X0 + 20, X1 - 19, 6))
    seg_b, seg_o = [], []
    for x in xs:
        u = (x - X0) / (X1 - X0)
        d = depth_at(u, maxd)
        y = SURF + d * PPF
        (seg_b if d < 65 else seg_o).append((x, y + (14 if d < 65 else -6)))
    cr.set_line_width(7); cr.set_source_rgba(*OR, a)
    run = None
    for x in xs:
        u = (x - X0) / (X1 - X0); d = depth_at(u, maxd)
        if d >= 65:
            y = SURF + d * PPF - 6
            if run is None: cr.move_to(x, y); run = 1
            else: cr.line_to(x, y)
    cr.stroke()
    cr.set_dash([10, 8]); cr.set_line_width(5); cr.set_source_rgba(*OR, 0.75 * a)
    for side in (0, 1):
        pts = [(x, SURF + depth_at((x - X0) / (X1 - X0), maxd) * PPF + 16) for x in xs
               if depth_at((x - X0) / (X1 - X0), maxd) < 65 and ((x < (X0 + X1) / 2) == (side == 0))]
        if pts:
            cr.move_to(*pts[0])
            for p in pts[1:]: cr.line_to(*p)
            cr.stroke()
    cr.set_dash([])


# ---------------------------------------------------------------- small layouts
def big_number(cr, gid, t, d, s_final, num, label, sub=None, kicker=None, color=OR, prefix='', suffix=''):
    backdrop(cr, gid, t, d); hud(cr, t)
    if kicker: mono(cr, kicker, W / 2, 320, 32, CY, align='center', t=t, start=0.0, bold=True)
    v = count(t, 0.1, min(1.1, d * 0.4), num)
    s = prefix + '{:,}'.format(v) + suffix if num else s_final
    font(cr, HEAD, 280); text(cr, s, W / 2, 590, color, ramp(t, 0, 0.3), 'center', tracking=-3)
    mono(cr, label, W / 2, 685, 40, WH, align='center', t=t, start=0.45, bold=True)
    if sub: body(cr, sub, W / 2, 752, 34, GR, align='center', t=t, start=0.85)


def title_card(cr, gid, t, d, kicker, title, line=None, size=150, dark=0.36):
    backdrop(cr, gid, t, d, dark=dark); hud(cr, t)
    mono(cr, kicker, W / 2, 400, 32, CY, align='center', t=t, start=0.0, bold=True)
    head(cr, title, W / 2, 560, size, WH, align='center', t=t, start=0.15)
    bar(cr, W / 2 - 260, 605, 520, t, 0.45)
    if line: mono(cr, line, W / 2, 680, 32, OR, align='center', t=t, start=0.65, bold=True)


def choice_cards(cr, t, items, starts, y=470, w=440, h=230, sel=None):
    n = len(items); gap = 50
    x0 = W / 2 - (n * w + (n - 1) * gap) / 2 - 40
    for i, ((letter, word), st) in enumerate(zip(items, starts)):
        k = ramp(t, st, 0.35)
        if k <= 0: continue
        x = x0 + i * (w + gap); yy = y + 40 * (1 - ease_out(k))
        box(cr, x, yy, w, h, 22, fill=(0.04, 0.10, 0.14), fa=0.9 * k, stroke=OR if sel == i else CY, sa=0.8 * k, lw=3)
        font(cr, HEAD, 64); text(cr, letter, x + 36, yy + 82, OR, k)
        font(cr, HEAD, 46 if len(word) < 12 else 40); text(cr, word, x + w / 2, yy + 170, WH, k, 'center')


# ================================================================ the graphics, in order
@reg('G01')
def g01(cr, t, d):
    big_number(cr, 'G01', t, d, '', 295, 'FEET AT THE DEEPEST POINT', 'The Straits of Mackinac', kicker='HIDDEN IN WATER UP TO')


@reg('G02')
def g02(cr, t, d):
    v = STRAITS
    straits(cr, v, t, label='FILE 04 · LAKE-BED MAPS · SONAR · DIVERS')
    bridge(cr, v, t, 0.0, label=False)
    sx = -100 + (W + 200) * ease_in_out(ramp(t, 0.2, max(1.5, d - 1.2)))
    cr.save()
    for a in S_LAKES: _poly(cr, v.pts(a))
    cr.clip(); cr.rectangle(0, 0, max(0, sx), H); cr.clip()
    for y in range(0, H, 6):
        cr.set_source_rgba(*CY, 0.10 + 0.08 * math.sin(y * 0.37) ** 2); cr.rectangle(0, y, W, 2); cr.fill()
    cr.restore()
    g = cairo.LinearGradient(sx - 160, 0, sx, 0); g.add_color_stop_rgba(0, *CY, 0); g.add_color_stop_rgba(1, *CY, 0.35)
    cr.set_source(g); cr.rectangle(sx - 160, 0, 160, H); cr.fill()
    cr.set_source_rgba(*CY, 0.9); cr.rectangle(sx - 2, 0, 3, H); cr.fill()
    for i, s in enumerate(('LAKE-BED MAPS', 'SONAR', 'DIVERS')):
        k = ramp(t, 0.5 + i * 0.9, 0.3)
        if k <= 0: continue
        box(cr, 120, 170 + i * 84, 380, 62, 10, fill=(0.02, 0.07, 0.10), fa=0.85 * k, stroke=CY, sa=0.6 * k)
        circle(cr, 150, 201 + i * 84, 8, GN, k)
        font(cr, MONO, 28, bold=True); text(cr, s, 176, 211 + i * 84, WH, k, tracking=3)


@reg('G03')
def g03(cr, t, d):
    backdrop(cr, 'G03', t, d, dark=0.34); hud(cr, t)
    mono(cr, 'YOU ARE WATCHING', W / 2, 430, 30, CY, align='center', t=t, start=0.0, bold=True)
    head(cr, 'GREAT LAKES FILES', W / 2, 580, 140, WH, align='center', t=t, start=0.1)
    bar(cr, W / 2 - 300, 620, 600, t, 0.3)
    mono(cr, 'THE PLACES HIDDEN IN AND UNDER THESE LAKES', W / 2, 690, 28, OR, align='center', t=t, start=0.45, cps=60, bold=True)


def sub_anim(cr, gid, t, d, click, line, y=520, kicker=None):
    backdrop(cr, gid, t, d, dark=0.4); hud(cr, t)
    k = ramp(t, 0, 0.4)
    if kicker: mono(cr, kicker, W / 2, y - 170, 32, OR, align='center', t=t, start=0.1, bold=True)
    sub_button(cr, W / 2 - 80, y, t, click, k)
    bell(cr, W / 2 + 260, y, 1.3, k, ring=max(0, t - click - 0.5), filled=t > click + 0.5)
    if t > click + 0.5:
        sonar(cr, W / 2 + 260, y, t - click - 0.5, OR, r0=0.1, rings=2, a=0.9, rmax=90)
    f_in = ramp(t, 0.3, max(0.4, click - 0.3))
    if t <= click: cx, cy = W / 2 - 60 + 300 * (1 - f_in), y + 10 + 220 * (1 - f_in)
    else: f2 = ramp(t, click + 0.15, 0.3); cx, cy = W / 2 - 60 + 320 * f2, y + 10
    cursor(cr, cx, cy, k, press=max(0.0, 1 - min(abs(t - click), abs(t - click - 0.5)) / 0.15))
    mono(cr, line, W / 2, y + 165, 30, WH, align='center', t=t, start=0.6, bold=True)


@reg('G04')
def g04(cr, t, d):
    sub_anim(cr, 'G04', t, d, 1.3, "IT'S FREE. IT TAKES ONE SECOND.", kicker='MOST VIEWERS HAVEN\'T SUBSCRIBED YET')


@reg('G05')
def g05(cr, t, d):
    lv = 4 * ease_in_out(ramp(t, 0.3, d))
    section(cr, t, level=lv)
    head(cr, 'START THE DRAIN', 120, 800, 84, WH, t=t, start=0.05)
    for i in range(3):
        x = 520 + i * 360; ph = (t * 1.6 + i * 0.3) % 1
        a = 0.9 * (1 - ph)
        cr.set_source_rgba(*OR, a); cr.set_line_width(6)
        y = SURF + 30 + ph * 40
        cr.move_to(x - 18, y - 14); cr.line_to(x, y + 4); cr.line_to(x + 18, y - 14); cr.stroke()


@reg('G06')
def g06(cr, t, d):
    v = STRAITS
    b = 13 * ease_in_out(ramp(t, 0.4, d - 0.8))
    straits(cr, v, t, band=b)
    bridge(cr, v, t, 0.0)
    x0, y0 = v.xy(*P['bridge_s']); x1, y1 = v.xy(*P['bridge_n'])
    miles_line(cr, (x0 - 140, y0), (x1 - 140, y1), '5 MILES', ramp(t, 0.2, 0.5) * (1 - ramp(t, d - 1.6, 0.5)))
    head(cr, 'THE GAP NARROWS', 110, 380, 72, WH, t=t, start=0.3)
    mono(cr, "BETWEEN MICHIGAN'S TWO PENINSULAS", 114, 428, 24, CY, t=t, start=0.7, bold=True)
    a = ramp(t, d - 1.6, 0.5)
    if a > 0:
        cr.set_source_rgba(*BED, a); cr.rectangle(114, 466, 26, 22); cr.fill()
        font(cr, MONO, 22, bold=True); text(cr, 'EXPOSED LAKE BED', 152, 485, BED, a, tracking=3)


@reg('G07')
def g07(cr, t, d):
    backdrop(cr, 'G07', t, d, dark=0.38); hud(cr, t)
    mono(cr, 'THE SHIP UNDER 35 FT OF WATER', W / 2, 380, 30, CY, align='center', t=t, start=0.0, bold=True)
    head(cr, 'CEDARVILLE', W / 2, 545, 170, WH, align='center', t=t, start=0.1)
    bar(cr, W / 2 - 300, 590, 600, t, 0.4)
    mono(cr, '588 FT LONG', W / 2 - 230, 665, 34, OR, align='center', t=t, start=0.7, bold=True)
    mono(cr, 'SANK 7 MAY 1965', W / 2 + 200, 665, 34, OR, align='center', t=t, start=1.1, bold=True)


@reg('G08')
def g08(cr, t, d):
    big_number(cr, 'G08', t, d, '', 35, 'MEN ON BOARD')


def ships_map(cr, t, d, stage):
    v = EASTV
    straits(cr, v, t, label='FILE 04 · 7 MAY 1965 · DENSE FOG', names=stage == 1)
    bridge(cr, v, t, 0.0)
    ced = CED_TRACK
    top = [(45.818, -84.735), (45.812, -84.69), (45.805, -84.65), P['collision']]
    if stage == 1:
        v3.path(cr, v, ced, t, 0.2, 2.4, OR, 6)
        v3.path(cr, v, top, t, 0.6, 2.2, CY, 6)
        a = ramp(t, 0.5, 0.4)
        x, y = v.xy(*ced[0]); font(cr, HEAD, 34); text(cr, 'CEDARVILLE', x - 10, y - 30, OR, a, 'right')
        x, y = v.xy(*top[0]); text(cr, 'TOPDALSFJORD', x + 30, y + 62, CY, ramp(t, 0.9, 0.4))
        if t > 2.9:
            x, y = v.xy(*P['collision']); sonar(cr, x, y, t - 2.9, RD, a=1, rmax=130)
            font(cr, HEAD, 40); text(cr, 'COLLISION', x + 30, y + 60, RD, ramp(t, 2.9, 0.3))
        # fog
        for k in range(5):
            xx = (k * 520 + t * 30) % (W + 600) - 300
            g = cairo.RadialGradient(xx, 380 + 90 * math.sin(k), 10, xx, 380 + 90 * math.sin(k), 420)
            g.add_color_stop_rgba(0, 0.8, 0.85, 0.88, 0.16); g.add_color_stop_rgba(1, 0.8, 0.85, 0.88, 0)
            cr.set_source(g); cr.paint()
    else:
        for pts, col in ((ced, OR), (top, CY)):
            v3.path(cr, v, pts, 99, 0, 1, col, 4, a=0.35)
        x, y = v.xy(*P['collision']); circle(cr, x, y, 10, RD)
        wr = P['cedarville']
        dla, dlo = wr[0] - P['collision'][0], wr[1] - P['collision'][1]
        beach = (wr[0] + dla * 0.73, wr[1] + dlo * 0.73)
        v3.path(cr, v, [P['collision'], beach], t, 0.3, 1.4, WH, 4, dash=[14, 10], a=0.8, arrow_head=True)
        v3.path(cr, v, [P['collision'], wr], t, 0.3, 1.4 * 0.56, OR, 7, arrow_head=False)
        xb, yb = v.xy(*beach)
        a = ramp(t, 1.6, 0.4)
        font(cr, HEAD, 34); text(cr, 'BEACH', xb - 26, yb + 50, WH, a, 'right')
        tag(cr, 'ABOUT 4 MILES AWAY', xb - 260, yb + 92, WH, a)
        if t > 2.4:
            xw, yw = v.xy(*wr); sonar(cr, xw, yw, t - 2.4, RD, a=1, rmax=110)
            font(cr, HEAD, 40); text(cr, 'SANK HERE', xw + 40, yw + 70, RD, ramp(t, 2.4, 0.3))
            tag(cr, '10:25 A.M. · 2 MILES SHORT', xw + 42, yw + 112, WH, ramp(t, 2.8, 0.3), size=24)


@reg('G09')
def g09(cr, t, d):
    ships_map(cr, t, d, 1)


@reg('G10')
def g10(cr, t, d):
    ships_map(cr, t, d, 2)


@reg('G11')
def g11(cr, t, d):
    big_number(cr, 'G11', t, d, '', 10, 'OF THE 35 MEN DIED', color=RD)


@reg('G12')
def g12(cr, t, d):
    big_number(cr, 'G12', t, d, '', 3, 'DIVERS HAVE DIED EXPLORING HER', 'She lies in two pieces, 110 ft down', kicker='SINCE THEN')


@reg('G13')
def g13(cr, t, d):
    title_card(cr, 'G13', t, d, 'TWO OIL PIPELINES', 'LINE 5', 'LAID 1953 · FOUR YEARS BEFORE THE BRIDGE', size=200)


@reg('G14')
def g14(cr, t, d):
    v = WESTV
    straits(cr, v, t, label='FILE 04 · LINE 5 · JUST WEST OF THE BRIDGE')
    bridge(cr, v, t, 0.0)
    line5(cr, v, t, 0.4, 2.0)
    a = ramp(t, 2.4, 0.5)
    p0 = v.xy(*P['line5_s']); p1 = v.xy(*P['line5_n'])
    miles_line(cr, (p0[0] - 150, p0[1]), (p1[0] - 150, p1[1]), '4.5 MILES', a)
    k = ramp(t, 3.6, 0.4)
    if k > 0:
        box(cr, 120, 150, 520, 150, 14, fill=(0.02, 0.07, 0.10), fa=0.85 * k, stroke=OR, sa=0.7 * k)
        font(cr, HEAD, 60); text(cr, '2 PIPES', 150, 222, OR, k)
        font(cr, MONO, 28, bold=True); text(cr, 'EACH 20 INCHES WIDE', 152, 270, WH, k, tracking=2)


@reg('G15')
def g15(cr, t, d):
    big_number(cr, 'G15', t, d, '', 23, 'MILLION GALLONS A DAY', 'Crude oil and natural gas liquids from western Canada', kicker='NEARLY')


@reg('G16')
def g16(cr, t, d):
    backdrop(cr, 'G16', t, d); hud(cr, t)
    mono(cr, 'DISCOVERED', 220, 400, 28, CY, t=t, start=0.0, bold=True)
    head(cr, 'AUGUST 2007', 214, 555, 150, WH, t=t, start=0.1)
    bar(cr, 220, 600, 560, t, 0.4)
    mono(cr, 'MACKINAC FALLS', 222, 672, 40, OR, t=t, start=0.6, bold=True)
    body(cr, 'A 100-foot cliff at the bottom of a lake', 222, 735, 34, GR, t=t, start=1.1)


_DOTS = []


def _inside(poly, lo, la):
    x, y = poly[:, 0], poly[:, 1]; xj, yj = np.roll(x, 1), np.roll(y, 1)
    c = ((y > la) != (yj > la)) & (lo < (xj - x) * (la - y) / (yj - y + 1e-12) + x)
    return bool(c.sum() % 2)


def in_water(la, lo):
    return any(_inside(p, lo, la) for p in S_LAKES) and not any(_inside(p, lo, la) for p in S_ISL)


def wreck_dots():
    if not _DOTS:
        rng = np.random.default_rng(7)
        while len(_DOTS) < 22:
            lo, la = rng.uniform(-84.82, -84.54), rng.uniform(45.755, 45.89)
            if in_water(la, lo) and abs(la - 45.787) + abs(lo + 84.671) > 0.02: _DOTS.append((la, lo))
    return _DOTS


@reg('G17')
def g17(cr, t, d):
    v = WIDEV
    straits(cr, v, t, band=8, label='FILE 04 · STRAITS OF MACKINAC SHIPWRECK PRESERVE', names=False)
    bridge(cr, v, t, 0.0)
    k = ramp(t, 0.3, 1.0)
    x0, y0 = v.xy(45.895, -84.835); x1, y1 = v.xy(45.748, -84.528)
    cr.set_dash([16, 10]); cr.set_line_width(3); cr.set_source_rgba(*OR, 0.9 * k)
    box(cr, x0, y0, x1 - x0, y1 - y0, 60, stroke=OR, sa=0.9 * k, lw=3); cr.set_dash([])
    pts = wreck_dots()
    n = int(min(22, max(0, (t - 1.4) / max(0.1, (d * 0.55 - 1.4)) * 22)))
    for i, (la, lo) in enumerate(pts[:n]):
        x, y = v.xy(la, lo); a = ramp(t, 1.4 + i * (d * 0.55 - 1.4) / 22, 0.3)
        circle(cr, x, y, 7, RD, a); circle(cr, x, y, 13, RD, 0.35 * a, fill=False, width=2)
    mark(cr, v, P['cedarville'], t, 1.0, 'CEDARVILLE', ring=True, color=OR, dy=40)
    a = ramp(t, 0.8, 0.5)
    box(cr, 110, 140, 600, 210, 14, fill=(0.02, 0.07, 0.10), fa=0.85 * a, stroke=OR, sa=0.6 * a)
    font(cr, HEAD, 64); text(cr, '148 SQ MI', 140, 215, WH, a)
    c = count(t, 1.4, d * 0.55 - 1.4, 22)
    font(cr, HEAD, 50); text(cr, '%d+ WRECKS' % c if t > 1.4 else '', 140, 285, RD, a)
    font(cr, MONO, 20); text(cr, 'DIVERS CAN VISIT · DOTS ILLUSTRATIVE', 142, 325, GR, a, tracking=2)


@reg('G18')
def g18(cr, t, d):
    backdrop(cr, 'G18', t, d, dark=0.32); hud(cr, t)
    head(cr, 'TAKE A GUESS', W / 2 - 40, 270, 96, WH, align='center', t=t, start=0.0)
    mono(cr, 'WHAT\'S STRANGEST AT THE VERY BOTTOM?', W / 2 - 40, 340, 32, OR, align='center', t=t, start=0.3, bold=True)
    choice_cards(cr, t, [('A', 'A SHIP'), ('B', 'THE PIPELINES'), ('C', 'SOMETHING OLDER')],
                 [d * 0.28, d * 0.36, d * 0.45])
    k = ramp(t, d * 0.62, 0.4)
    if k > 0:
        pulse_ = 1 + 0.05 * math.sin(t * 6)
        cr.save(); cr.translate(W / 2 - 40, 820); cr.scale(pulse_, pulse_)
        box(cr, -330, -50, 660, 92, 46, fill=(0.86, 0.13, 0.13), fa=k)
        font(cr, BODY, 40, bold=True); text(cr, 'COMMENT YOUR GUESS  ↓', 0, 14, WH, k, 'center')
        cr.restore()


@reg('G19')
def g19(cr, t, d):
    backdrop(cr, 'G19', t, d, dark=0.32); hud(cr, t)
    head(cr, 'ONE WORD IS ENOUGH', W / 2 - 40, 330, 90, WH, align='center', t=t, start=0.0)
    comment_box(cr, W / 2 - 600, 450, 1120, 'My guess: a ship', t, 0.6, cps=9)
    mono(cr, 'THEN SEE IF YOU WERE RIGHT', W / 2 - 40, 680, 32, OR, align='center', t=t, start=2.4, bold=True)


@reg('G20')
def g20(cr, t, d):
    backdrop(cr, 'G20', t, d); hud(cr, t)
    mono(cr, 'THE MACKINAC BRIDGE OPENS', 220, 400, 28, CY, t=t, start=0.0, bold=True)
    head(cr, '1 NOV 1957', 214, 560, 170, WH, t=t, start=0.1)
    bar(cr, 220, 605, 600, t, 0.4)
    k = ramp(t, d * 0.45, 0.4)
    font(cr, HEAD, 64); text(cr, '5 MILES LONG', 222, 700, OR, k)


@reg('G21')
def g21(cr, t, d):
    backdrop(cr, 'G21', t, d, dark=0.3); hud(cr, t, 'FILE 04 · ONE TOWER · TO SCALE')
    wl = 640; k = 0.8
    top = wl - 552 * k; bot = wl + 210 * k
    x = 900
    # water line and drained bed
    cr.set_source_rgba(*CY, 0.25); cr.rectangle(0, wl, W, bot - wl + 40); cr.fill()
    cr.set_dash([14, 10]); cr.set_source_rgba(*CY, 0.9); cr.set_line_width(3); cr.move_to(300, wl); cr.line_to(1500, wl); cr.stroke(); cr.set_dash([])
    font(cr, MONO, 22); text(cr, 'WATERLINE', 310, wl - 14, CY, 0.9, tracking=3)
    g = cairo.LinearGradient(0, bot, 0, bot + 80); g.add_color_stop_rgb(0, *BED); g.add_color_stop_rgb(1, *SAND_D)
    cr.set_source(g); cr.rectangle(300, bot, 1200, 120); cr.fill()
    ka = ease_out(ramp(t, 0.2, 1.2)); kb = ease_out(ramp(t, d * 0.3, 1.2))
    cr.set_source_rgba(0.88, 0.90, 0.90, 1)
    h = (wl - top) * ka
    cr.rectangle(x - 34, wl - h, 22, h); cr.fill(); cr.rectangle(x + 12, wl - h, 22, h); cr.fill()
    for f in (0.1, 0.4, 0.7):
        if wl - (wl - top) * f > wl - h: cr.rectangle(x - 34, wl - (wl - top) * (1 - f) - 10, 68, 12); cr.fill()
    cr.set_source_rgba(0.66, 0.68, 0.67, 1); cr.rectangle(x - 70, wl, 140, (bot - wl) * kb); cr.fill()
    dim_v(cr, x + 130, wl - h, wl, '552 FT', ramp(t, 1.2, 0.4), WH)
    dim_v(cr, x + 130, wl, wl + (bot - wl) * kb, '210 FT', ramp(t, d * 0.3 + 1.0, 0.4), OR)
    a = ramp(t, d * 0.62, 0.5)
    dim_v(cr, x - 200, top, bot, '760+ FT', a, OR, 'left')
    mono(cr, 'ABOVE THE WATER', x + 132, wl - h / 2 + 64, 22, GR, t=t, start=1.4, bold=True)
    mono(cr, 'BELOW IT', x + 132, wl + (bot - wl) / 2 + 64, 22, GR, t=t, start=d * 0.3 + 1.2, bold=True)


@reg('G22')
def g22(cr, t, d):
    backdrop(cr, 'G22', t, d, dark=0.4); hud(cr, t)
    mono(cr, 'FOUR SUMMERS · NO WORK IN WINTER', W / 2, 340, 30, CY, align='center', t=t, start=0.0, bold=True)
    head(cr, '$100 MILLION', W / 2, 520, 170, WH, align='center', t=t, start=0.15)
    k = ramp(t, d * 0.62, 0.3)
    if k > 0:
        font(cr, HEAD, 110); text(cr, 'AND FIVE MEN', W / 2, 690, RD, k, 'center')


@reg('G23')
def g23(cr, t, d):
    backdrop(cr, 'G23', t, d, dark=0.34); hud(cr, t)
    mono(cr, '6 JUNE 1956 · CATWALK COLLAPSE · NORTH TOWER', W / 2, 330, 28, CY, align='center', t=t, start=0.0, bold=True)
    head(cr, 'JACK BAKER, 28', W / 2, 490, 110, WH, align='center', t=t, start=0.3)
    head(cr, 'ROBERT KOPPEN, 28', W / 2, 620, 110, WH, align='center', t=t, start=0.7)
    bar(cr, W / 2 - 200, 662, 400, t, 1.1, color=OR)
    body(cr, 'It was their first day on the job.', W / 2, 735, 38, GR, align='center', t=t, start=d * 0.5)


@reg('G24')
def g24(cr, t, d):
    backdrop(cr, 'G24', t, d, dark=0.3); hud(cr, t)
    mono(cr, 'NO ONE IS BURIED INSIDE THE BRIDGE', W / 2, 360, 30, CY, align='center', t=t, start=0.0, bold=True)
    head(cr, 'ROBERT KOPPEN', W / 2, 500, 120, WH, align='center', t=t, start=0.2)
    stamp(cr, 'NEVER FOUND', W / 2, 660, t, 1.0, size=90, color=RD)


@reg('G25')
def g25(cr, t, d):
    section(cr, t, level=270, maxd=270, bridge_on=False, label='FILE 04 · LINE 5 · SIDE VIEW · NOT TO SCALE',
            pipes=ramp(t, 0.2, 0.8))
    head(cr, 'THE LOWEST POINT', 120, 800, 76, WH, t=t, start=0.2)
    x = (X0 + X1) / 2; y = SURF + 270 * PPF - 6
    a = ramp(t, 1.4, 0.4)
    if a > 0:
        sonar(cr, x, y, t - 1.4, OR, a=a, rmax=80)
        dim_v(cr, x + 150, SURF, y, '270 FT', a, OR)
    a2 = ramp(t, d * 0.45, 0.5)
    tag(cr, 'BURIED NEAR SHORE', 150, SURF + 95, WH, a2)
    tag(cr, 'ON THE BOTTOM PAST 65 FT', 470, SURF + 70, OR, a2)


@reg('G26')
def g26(cr, t, d):
    backdrop(cr, 'G26', t, d, dark=0.3); hud(cr, t, 'FILE 04 · LINE 5 · SUPPORTS')
    mono(cr, 'IN 2014 · THE RULE: A SUPPORT AT LEAST EVERY 75 FT', W / 2 - 40, 360, 32, CY, align='center', t=t, start=0.0, bold=True)
    yb = 640
    g = cairo.LinearGradient(0, yb, 0, yb + 120); g.add_color_stop_rgb(0, *BED); g.add_color_stop_rgb(1, *SAND_D)
    cr.set_source(g); cr.rectangle(140, yb, 1460, 120); cr.fill()
    yp = yb - 70
    cr.set_source_rgba(0.15, 0.16, 0.17, 1); cr.rectangle(140, yp - 18, 1460, 36); cr.fill()
    cr.set_source_rgba(*OR, 1); cr.set_line_width(3); cr.rectangle(140, yp - 18, 1460, 36); cr.stroke()
    sup = [260, 560, 860, 1490]
    for i, x in enumerate(sup):
        k = ramp(t, 0.4 + i * 0.25, 0.3)
        cr.set_source_rgba(0.75, 0.77, 0.76, k); cr.rectangle(x - 22, yp + 18, 44, yb - yp - 18); cr.fill()
        cr.rectangle(x - 40, yb - 8, 80, 10); cr.fill()
    a = ramp(t, 1.6, 0.4)
    for x0, x1 in ((260, 560), (560, 860)):
        if a > 0:
            cr.set_source_rgba(*GN, a); cr.set_line_width(3)
            cr.move_to(x0, yp - 60); cr.line_to(x1, yp - 60); cr.stroke()
            font(cr, HEAD, 40); text(cr, '75 FT', (x0 + x1) / 2, yp - 78, GN, a, 'center')
    a2 = ramp(t, d * 0.45, 0.4)
    if a2 > 0:
        cr.set_source_rgba(*RD, a2); cr.set_line_width(4); cr.move_to(860, yp - 60); cr.line_to(1490, yp - 60); cr.stroke()
        font(cr, HEAD, 44); text(cr, 'TOO FAR APART', 1175, yp - 80, RD, a2, 'center')
        sag = 26 * ease_out(ramp(t, d * 0.45, 1.0))
        cr.set_source_rgba(*RD, 0.5 * a2); cr.set_line_width(5)
        cr.move_to(860, yp); cr.curve_to(1060, yp + sag, 1290, yp + sag, 1490, yp); cr.stroke()


@reg('G27')
def g27(cr, t, d):
    backdrop(cr, 'G27', t, d, dark=0.34); hud(cr, t)
    mono(cr, '2018 · A TUGBOAT\'S ANCHOR', W / 2, 330, 30, CY, align='center', t=t, start=0.0, bold=True)
    font(cr, HEAD, 220); text(cr, '< 1 INCH', W / 2, 560, WH, ramp(t, 0.1, 0.3), 'center')
    mono(cr, 'THE DENT', W / 2, 640, 34, GR, align='center', t=t, start=0.4, bold=True)
    stamp(cr, 'THE PIPE HELD', W / 2, 770, t, max(1.0, d - 1.6), size=70, color=GN, angle=-0.05)


def lake_split(cr, v, t, a_mi=1.0, a_hu=1.0, merged=0.0):
    basemap(cr, v, labels=False)
    for which, al in (('mi', a_mi), ('hu', a_hu)):
        if al <= 0: continue
        cr.save()
        if which == 'mi':
            x0, _ = v.xy(46, -88.5); x1, _ = v.xy(46, -84.75); _, y1 = v.xy(46.25, -86); cr.rectangle(x0, y1, x1 - x0, H)
        else:
            x0, _ = v.xy(46, -84.75); x1, _ = v.xy(46, -79.5); _, y1 = v.xy(46.4, -86); cr.rectangle(x0, y1, x1 - x0, H)
        cr.clip()
        col = CY if which == 'mi' else tuple(c1 + (c2 - c1) * merged for c1, c2 in zip(GN, CY))
        _poly(cr, v.pts(UPPER)); cr.set_source_rgba(*col, 0.55 * al); cr.fill()
        for isl in ISLANDS:
            _poly(cr, v.pts(isl)); cr.set_source_rgb(*LAND); cr.fill()
        cr.restore()


@reg('G28')
def g28(cr, t, d):
    v = View(44.6, -85.0, 125)
    m = ramp(t, d * 0.42, 1.2)
    lake_split(cr, v, t, merged=m)
    hud(cr, t, 'FILE 04 · LAKE MICHIGAN + LAKE HURON', None)
    a1 = 1 - ramp(t, d * 0.42, 0.6)
    font(cr, HEAD, 44)
    x, y = v.xy(43.6, -87.05); text(cr, 'LAKE MICHIGAN', x, y, WH, ramp(t, 0.2, 0.4) * a1, 'center')
    x, y = v.xy(44.6, -82.25); text(cr, 'LAKE HURON', x, y, WH, ramp(t, 0.6, 0.4) * a1, 'center')
    xs, ys = v.xy(45.82, -84.72)
    sonar(cr, xs, ys, t, OR, a=ramp(t, 1.2, 0.4), rmax=70)
    font(cr, MONO, 22, bold=True); text(cr, 'THE STRAITS', xs + 26, ys - 26, OR, ramp(t, 1.2, 0.4), tracking=2)
    k = ramp(t, d * 0.5, 0.5)
    if k > 0:
        box(cr, 110, 700, 760, 150, 14, fill=(0.02, 0.07, 0.10), fa=0.88 * k, stroke=CY, sa=0.7 * k)
        font(cr, HEAD, 64); text(cr, 'ONE LAKE', 140, 772, CY, k)
        font(cr, MONO, 24, bold=True); text(cr, 'LARGEST FRESHWATER LAKE ON EARTH BY AREA', 142, 820, WH, ramp(t, d * 0.6, 0.4), tracking=1)


@reg('G29')
def g29(cr, t, d):
    v = STRAITS
    straits(cr, v, t, label='FILE 04 · CURRENTS THROUGH THE STRAITS', names=False)
    bridge(cr, v, t, 0.0)
    east = t < d * 0.5
    flip = ramp(t, d * 0.5 - 0.3, 0.6)
    a = 1 - abs(1 - 2 * flip) if 0 < flip < 1 else 1.0
    lanes = [45.80, 45.815, 45.83]
    for j, la in enumerate(lanes):
        for k in range(9):
            ph = ((t * 0.32 + k / 9 + j * 0.13) % 1)
            if not east: ph = 1 - ph
            lo = -84.97 + 0.56 * ph
            x, y = v.xy(la + 0.006 * math.sin(lo * 40), lo)
            dxs = 46 if east else -46
            cr.set_source_rgba(*CY, 0.85 * a); cr.set_line_width(5); cr.set_line_cap(cairo.LINE_CAP_ROUND)
            cr.move_to(x - dxs, y); cr.line_to(x, y); cr.stroke()
            cr.move_to(x, y); cr.line_to(x - dxs * 0.35, y - 12); cr.move_to(x, y); cr.line_to(x - dxs * 0.35, y + 12); cr.stroke()
    cr.set_line_cap(cairo.LINE_CAP_BUTT)
    head(cr, 'SOMETIMES EAST' if east else 'SOMETIMES WEST', 120, 190, 72, WH, a=a)
    k = ramp(t, d * 0.55, 0.5)
    if k > 0:
        box(cr, 110, 720, 860, 120, 14, fill=(0.02, 0.07, 0.10), fa=0.88 * k, stroke=OR, sa=0.7 * k)
        font(cr, HEAD, 52); text(cr, '2.5 MILLION CU FT', 140, 788, OR, k)
        font(cr, MONO, 22, bold=True); text(cr, 'PER SECOND, AT TIMES', 142, 824, WH, k, tracking=2)


@reg('G30')
def g30(cr, t, d):
    v = View(45.0, -83.6, 150)
    basemap(cr, v, labels=False)
    xs, ys = v.xy(45.82, -84.72)
    R = 30 + 290 * ease_out(ramp(t, 0.6, d * 0.55))
    cr.save(); cr.arc(xs + R * 0.55, ys + R * 0.35, R, 0, 2 * math.pi); cr.clip()
    cr.save(); _, y0 = v.xy(46.3, -84); cr.rectangle(0, y0, W, H); cr.clip()
    _poly(cr, v.pts(UPPER)); cr.set_source_rgba(*RD, 0.35); cr.fill()
    for isl in ISLANDS:
        _poly(cr, v.pts(isl)); cr.set_source_rgb(*LAND); cr.fill()
    cr.set_source_rgba(*RD, 0.95); cr.set_line_width(4); _poly(cr, v.pts(UPPER)); cr.stroke()
    cr.restore(); cr.restore()
    hud(cr, t, 'FILE 04 · UNIVERSITY OF MICHIGAN STUDY · 2016', None)
    sonar(cr, xs, ys, t, OR, a=1, rmax=60)
    font(cr, MONO, 22, bold=True); text(cr, 'LINE 5', xs - 24, ys - 24, OR, 1, 'right', tracking=2)
    k = ramp(t, 1.0, 0.5)
    box(cr, 110, 150, 700, 230, 14, fill=(0.02, 0.07, 0.10), fa=0.88 * k, stroke=RD, sa=0.7 * k)
    font(cr, MONO, 22, bold=True); text(cr, 'A LEAK HERE COULD REACH', 140, 196, WH, k, tracking=2)
    c = count(t, 1.2, d * 0.45, 700)
    font(cr, HEAD, 62); text(cr, '%d MILES' % c, 140, 262, RD, k)
    font(cr, MONO, 22, bold=True); text(cr, 'OF SHORELINE', 142, 296, WH, k, tracking=2)
    k2 = ramp(t, d * 0.6, 0.5)
    font(cr, HEAD, 40); text(cr, 'UP TO 60% OF LAKE HURON', 140, 352, OR, k2)
    font(cr, MONO, 18); text(cr, 'SPREAD SHOWN IS ILLUSTRATIVE', 112, 410, GR, k, tracking=2)


@reg('G31')
def g31(cr, t, d):
    backdrop(cr, 'G31', t, d, dark=0.32); hud(cr, t)
    y = 560; x0, x1 = 260, 1580
    k = ease_out(ramp(t, 0.0, 0.8))
    cr.set_source_rgba(*WH, 0.6); cr.set_line_width(4); cr.move_to(x0, y); cr.line_to(x0 + (x1 - x0) * k, y); cr.stroke()
    items = [(2018, 'TUNNEL PLANNED', 'Through the rock under the Straits', d * 0.66, CY),
             (2019, 'MICHIGAN SUES', 'To shut this section down', 0.3, RD),
             (2021, 'CANADA STEPS IN', 'To defend the pipeline', d * 0.3, OR)]
    for yr, title, sub, st, col in items:
        x = {2018: 430, 2019: 900, 2021: 1400}[yr]
        a = ramp(t, st, 0.4)
        if a <= 0: continue
        circle(cr, x, y, 16, col, a); circle(cr, x, y, 28, col, 0.4 * a, fill=False, width=3)
        font(cr, HEAD, 70); text(cr, str(yr), x, y - 50, WH, a, 'center')
        font(cr, MONO, 28, bold=True); text(cr, title, x, y + 80, col, a, 'center', tracking=2)
        font(cr, BODY, 26); text(cr, sub, x, y + 120, GR, a, 'center')


@reg('G32')
def g32(cr, t, d):
    section(cr, t, level=255, canyon=ramp(t, 0.2, 0.5), towers_down=1.0)
    head(cr, "IT'S A CANYON", 120, 800, 96, OR, t=t, start=0.05)


@reg('G33')
def g33(cr, t, d):
    v = View(44.3, -86.4, 150)
    basemap(cr, v, labels=False)
    a = ramp(t, 0.6, 1.2)
    x0, _ = v.xy(46, -88.5); x1, _ = v.xy(46, -84.95); _, y1 = v.xy(46.05, -86)
    cr.save(); cr.rectangle(x0, y1, x1 - x0, H); cr.clip()
    cr.set_line_join(cairo.LINE_JOIN_ROUND)
    _poly(cr, v.pts(UPPER)); cr.set_source_rgba(*SAND_D, a); cr.set_line_width(110 * a); cr.stroke()
    cr.set_dash([10, 8]); cr.set_line_width(2.5); cr.set_source_rgba(*WH, 0.6 * a)
    _poly(cr, v.pts(UPPER)); cr.stroke(); cr.set_dash([])
    cr.restore()
    hud(cr, t, 'FILE 04 · ABOUT 9,000 YEARS AGO · APPROXIMATE', None)
    x, y = v.xy(43.6, -87.0)
    font(cr, HEAD, 46); text(cr, 'LAKE CHIPPEWA', x, y, CY, ramp(t, 1.4, 0.4), 'center')
    tag(cr, "DASHED: TODAY'S LAKE MICHIGAN", 130, 220, WH, ramp(t, 1.8, 0.4))
    v3.path(cr, v, [(45.25, -86.15), (45.70, -85.35), (45.82, -84.72), (45.68, -84.15)], t, d * 0.45, 1.6, OR, 6)
    xs, ys = v.xy(45.82, -84.72)
    tag(cr, 'OUT THROUGH THE STRAITS', xs + 40, ys - 40, OR, ramp(t, d * 0.45 + 1.2, 0.4), size=24)


@reg('G34')
def g34(cr, t, d):
    title_card(cr, 'G34', t, d, 'ABOUT 9,000 YEARS AGO', 'MACKINAC FALLS', 'A WATERFALL UNDER THE BRIDGE', size=150, dark=0.34)


@reg('G35')
def g35(cr, t, d):
    like_anim(cr, 'G35', t, d)


@reg('G36')
def g36(cr, t, d):
    backdrop(cr, 'G36', t, d, dark=0.34); hud(cr, t)
    head(cr, "WHAT'S DOWN THERE?", W / 2 - 40, 330, 92, WH, align='center', t=t, start=0.0)
    mono(cr, 'LIVE NEAR THE STRAITS? DIVED THESE WRECKS?', W / 2 - 40, 400, 30, OR, align='center', t=t, start=0.3, bold=True)
    comment_box(cr, W / 2 - 600, 480, 1120, 'Tell me in the comments', t, 0.9, cps=14)


@reg('G37')
def g37(cr, t, d):
    backdrop(cr, 'G37', t, d, dark=0.32); hud(cr, t)
    head(cr, 'YOUR CALL', W / 2 - 40, 280, 96, WH, align='center', t=t, start=0.0)
    mono(cr, 'TWO 70-YEAR-OLD PIPELINES UNDER THE STRAITS', W / 2 - 40, 350, 30, OR, align='center', t=t, start=0.2, bold=True)
    choice_cards(cr, t, [('1', 'STAY'), ('2', 'TUNNEL'), ('3', 'SHUT DOWN')], [0.3, d * 0.34, d * 0.66])


@reg('G38')
def g38(cr, t, d):
    backdrop(cr, 'G38', t, d, dark=0.32); hud(cr, t)
    head(cr, 'STAY · TUNNEL · SHUT DOWN?', W / 2 - 40, 330, 80, WH, align='center', t=t, start=0.0)
    comment_box(cr, W / 2 - 600, 450, 1120, 'My answer: ', t, 0.4, cps=12)
    mono(cr, 'I READ EVERY ONE', W / 2 - 40, 680, 32, OR, align='center', t=t, start=1.2, bold=True)


@reg('G39')
def g39(cr, t, d):
    sub_anim(cr, 'G39', t, d, d * 0.5, 'NEXT: WE DRAIN THE GRAVEYARD OF THE GREAT LAKES',
             kicker='YOU WATCHED ALL THE WAY HERE')


@reg('G40')
def g40(cr, t, d):
    backdrop(cr, 'G40', t, d, blur=4, dark=0.6, n=79)
    g = cairo.LinearGradient(0, 0, W * 0.6, 0); g.add_color_stop_rgba(0, 0.01, 0.04, 0.06, 0.85); g.add_color_stop_rgba(1, 0.01, 0.04, 0.06, 0)
    cr.set_source(g); cr.paint()
    hud(cr, t, 'GREAT LAKES FILES', None)
    mono(cr, 'END OF FILE 04', 140, 360, 30, OR, t=t, start=0.2, bold=True)
    head(cr, 'THANKS FOR', 134, 500, 110, WH, t=t, start=0.4)
    head(cr, 'WATCHING', 134, 620, 110, WH, t=t, start=0.6)
    mono(cr, 'NEXT: THE GRAVEYARD OF THE GREAT LAKES  →', 140, 740, 30, CY, t=t, start=1.4, bold=True)
    mono(cr, 'SUBSCRIBE SO YOU DON\'T MISS IT', 140, 800, 28, WH, t=t, start=2.0, bold=True)
