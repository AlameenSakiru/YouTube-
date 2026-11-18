"""Every graphic in video 3 (Superior Shoal and the Edmund Fitzgerald), keyed by its G number in video-03/edit-plan.json.

A new look for this video: the "case file". Graphics sit on a blurred, darkened copy of the scene they follow,
inside a sonar-style frame (corner brackets, coordinates, typed mono labels), with heavy display type and
ship-light orange. Each graphic is draw(cr, t, d). Selected by render.py when GFX_SET=video3.
"""
import math, os, json
import numpy as np
import cairo
from PIL import Image, ImageFilter, ImageEnhance
from style import *
from maps import *

G = {}
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
V3 = os.path.join(ROOT, 'video-03')

HEAD = 'Inter Display Black'
MONO = 'JetBrains Mono'
BODY = 'Inter'
OR = (1.0, 0.54, 0.24)        # ship-light orange
CY = (0.37, 0.83, 0.82)       # sonar cyan
WH = (0.93, 0.96, 0.95)
GR = (0.62, 0.73, 0.74)
RD = (1.0, 0.33, 0.24)


def reg(gid):
    def deco(fn):
        G[gid] = fn; return fn
    return deco


# ---------------------------------------------------------------- which picture sits behind each graphic
def _prev_images():
    try:
        plan = json.load(open(os.path.join(V3, 'edit-plan.json')))
    except Exception:
        return {}
    out, prev = {}, 1
    for s in plan:
        if s['kind'] == 'G': out[s['gid']] = prev
        elif s.get('img'): prev = s['img']
    return out


BACK = _prev_images()
BACK.update({'G07': 9, 'G08': 1, 'G72': 84, 'G54': 74, 'G65': 83, 'G41': 52, 'G48': 58})
_SURF = {}


def _bg_png(n, blur=16, dark=0.42):
    d = os.path.join(V3, 'build', 'bg'); os.makedirs(d, exist_ok=True)
    out = os.path.join(d, '%03d-%d-%d.png' % (n, blur, int(dark * 100)))
    if not os.path.exists(out):
        crops = json.load(open(os.path.join(V3, 'images', 'crops.json')))
        im = Image.open(os.path.join(V3, 'images', '%03d.jpg' % n)).convert('RGB')
        if '%03d' % n in crops: im = im.crop(tuple(crops['%03d' % n]))
        im = im.resize((2112, 1188), Image.LANCZOS)
        if blur: im = im.filter(ImageFilter.GaussianBlur(blur))
        im = ImageEnhance.Brightness(im).enhance(dark)
        a = np.asarray(im, np.float32)
        a = a * np.array([0.82, 0.97, 1.05]) + np.array([0, 4, 8])     # pull toward deep blue-green
        Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).save(out)
    return out


def backdrop(cr, gid, t, d, blur=16, dark=0.42, n=None):
    n = n or BACK.get(gid, 1)
    key = (n, blur, dark)
    if key not in _SURF: _SURF[key] = cairo.ImageSurface.create_from_png(_bg_png(n, blur, dark))
    s = _SURF[key]
    z = 1.0 + 0.04 * (t / max(d, 0.1))
    cr.save(); cr.translate(W / 2, H / 2); cr.scale(z * W / 2112 * 1.0, z * H / 1188 * 1.0)
    cr.translate(-2112 / 2, -1188 / 2); cr.set_source_surface(s, 0, 0); cr.paint(); cr.restore()
    g = cairo.RadialGradient(W / 2, H / 2, 200, W / 2, H / 2, W * 0.75)
    g.add_color_stop_rgba(0, 0, 0, 0, 0.0); g.add_color_stop_rgba(1, 0.0, 0.03, 0.05, 0.65)
    cr.set_source(g); cr.paint()


def hud(cr, t, label='FILE 03 · SUPERIOR SHOAL', coords='48°04′N  87°05′W', a=1.0):
    """The case-file frame: corner brackets, a file label, coordinates and a slow scan line."""
    m, L = 56, 46
    cr.set_line_width(3); cr.set_source_rgba(*CY, 0.55 * a)
    for x, y, sx, sy in ((m, m, 1, 1), (W - m, m, -1, 1), (m, H - m, 1, -1), (W - m, H - m, -1, -1)):
        cr.move_to(x, y + sy * L); cr.line_to(x, y); cr.line_to(x + sx * L, y); cr.stroke()
    font(cr, MONO, 20); text(cr, label, m + 18, m + 44, CY, 0.75 * a, tracking=2)
    if coords: text(cr, coords, W - m - 18, m + 44, CY, 0.6 * a, 'right', tracking=2)
    y = (t * 90) % (H + 200) - 100
    g = cairo.LinearGradient(0, y - 60, 0, y + 2)
    g.add_color_stop_rgba(0, *CY, 0); g.add_color_stop_rgba(1, *CY, 0.05 * a)
    cr.set_source(g); cr.rectangle(0, y - 60, W, 62); cr.fill()


def fade(t, d, fin=0.3):
    return ramp(t, 0, fin)


# ---------------------------------------------------------------- type helpers
def head(cr, s, x, y, size, color=WH, a=1.0, align='left', rise=24, t=None, start=0.0, dur=0.55):
    if t is not None:
        k = ramp(t, start, dur); a *= k; y += rise * (1 - k)
    if a <= 0: return 0
    font(cr, HEAD, size)
    return text(cr, s, x, y, color, a, align, tracking=-size * 0.01)


def mono(cr, s, x, y, size=28, color=CY, a=1.0, align='left', t=None, start=0.0, cps=34, bold=False):
    """Typed text: characters appear one by one from `start`."""
    if t is not None:
        n = int(max(0, t - start) * cps)
        if n <= 0: return 0
        s_show = s[:n]
    else:
        s_show = s
    font(cr, MONO, size, bold=bold)
    full = text_width(cr, s, 2)
    if align == 'center': x -= full / 2
    elif align == 'right': x -= full
    text(cr, s_show, x, y, color, a, tracking=2)
    if t is not None and len(s_show) < len(s) and int(t * 3) % 2 == 0:
        cr.set_source_rgba(*color, a); cr.rectangle(x + text_width(cr, s_show, 2) + 4, y - size * 0.8, size * 0.55, size * 0.95); cr.fill()
    return full


def body(cr, s, x, y, size=40, color=WH, a=1.0, align='left', t=None, start=0.0, bold=False):
    if t is not None:
        k = ramp(t, start, 0.5); a *= k; y += 12 * (1 - k)
    if a <= 0: return
    font(cr, BODY, size, bold=bold); text(cr, s, x, y, color, a, align)


def bar(cr, x, y, w, t, start=0.0, dur=0.6, color=OR, h=6, a=1.0):
    k = ramp(t, start, dur)
    cr.set_source_rgba(*color, a); cr.rectangle(x, y, w * k, h); cr.fill()


def box(cr, x, y, w, h, r, fill=None, fa=1.0, stroke=None, sa=1.0, lw=2):
    cr.new_sub_path()
    cr.arc(x + w - r, y + r, r, -math.pi / 2, 0); cr.arc(x + w - r, y + h - r, r, 0, math.pi / 2)
    cr.arc(x + r, y + h - r, r, math.pi / 2, math.pi); cr.arc(x + r, y + r, r, math.pi, 1.5 * math.pi); cr.close_path()
    if fill: cr.set_source_rgba(*fill, fa); cr.fill_preserve() if stroke else cr.fill()
    if stroke: cr.set_source_rgba(*stroke, sa); cr.set_line_width(lw); cr.stroke()


def stamp(cr, s, cx, cy, t, start, size=64, color=RD, angle=-0.08):
    """A rubber-stamp label that slams in."""
    k = ramp(t, start, 0.25)
    if k <= 0: return
    sc = 1.6 - 0.6 * k
    cr.save(); cr.translate(cx, cy); cr.rotate(angle); cr.scale(sc, sc)
    font(cr, HEAD, size); w = text_width(cr, s, 2)
    box(cr, -w / 2 - 28, -size * 0.95, w + 56, size * 1.35, 8, stroke=color, sa=0.9 * k, lw=6)
    text(cr, s, -w / 2, size * 0.18, color, 0.92 * k, tracking=2)
    cr.restore()


def count(t, start, dur, n):
    return int(round(n * ease_out((t - start) / dur))) if t > start else 0


# ---------------------------------------------------------------- card layouts
def card_quote(cr, gid, t, d, lines, source, size=74, y0=None):
    backdrop(cr, gid, t, d); hud(cr, t)
    n = len(lines); y0 = y0 or (H / 2 - (n - 1) * size * 0.62 + 10)
    k = ramp(t, 0, 0.35)
    cr.set_source_rgba(*OR, k); cr.rectangle(210, y0 - size * 0.95, 8, (n - 1) * size * 1.22 + size * 1.25); cr.fill()
    for i, ln in enumerate(lines):
        head(cr, ln, 260, y0 + i * size * 1.22, size, WH, t=t, start=0.15 + i * 0.35)
    mono(cr, source, 262, y0 + (n - 1) * size * 1.22 + 90, 26, GR, t=t, start=0.5 + n * 0.35)


def card_number(cr, gid, t, d, num, label, sub=None, prefix='', suffix='', color=OR):
    backdrop(cr, gid, t, d); hud(cr, t)
    v = count(t, 0.1, min(1.2, d * 0.45), num)
    s = prefix + '{:,}'.format(v) + suffix
    font(cr, HEAD, 300); text(cr, s, W / 2, 590, color, ramp(t, 0, 0.3), 'center', tracking=-3)
    mono(cr, label, W / 2, 690, 40, WH, align='center', t=t, start=0.5, bold=True)
    if sub: body(cr, sub, W / 2, 760, 34, GR, align='center', t=t, start=0.9)


def card_date(cr, gid, t, d, date, line, sub=None):
    backdrop(cr, gid, t, d); hud(cr, t)
    mono(cr, 'DATE', 220, 430, 26, CY, t=t, start=0.0)
    head(cr, date, 214, 580, 150, WH, t=t, start=0.1)
    bar(cr, 220, 620, 520, t, 0.4)
    mono(cr, line, 222, 690, 34, OR, t=t, start=0.6, bold=True)
    if sub: body(cr, sub, 222, 750, 32, GR, t=t, start=1.0)


def card_lines(cr, gid, t, d, title, items, step=0.55, start=0.3, size=52, y0=440):
    backdrop(cr, gid, t, d); hud(cr, t)
    if title: mono(cr, title, 220, y0 - 90, 28, CY, t=t, start=0.0, bold=True)
    for i, it in enumerate(items):
        k = ramp(t, start + i * step, 0.4)
        if k <= 0: continue
        y = y0 + i * size * 1.75
        cr.set_source_rgba(*OR, k); cr.rectangle(220, y - size * 0.62, 14, 14); cr.fill()
        head(cr, it, 262, y, size, WH, a=k)


def card_title(cr, gid, t, d, kicker, lines, size=120):
    backdrop(cr, gid, t, d, dark=0.32); hud(cr, t)
    mono(cr, kicker, W / 2, 380, 30, OR, align='center', t=t, start=0.0, bold=True)
    for i, ln in enumerate(lines):
        head(cr, ln, W / 2, 520 + i * size * 1.05, size, WH, align='center', t=t, start=0.2 + i * 0.25)


# ---------------------------------------------------------------- Lake Superior maps
PLACES.update({
    'Copper Harbor': (47.468, -87.888), 'Superior Shoal': (48.067, -87.083), 'Isle Royale': (48.00, -88.90),
    'Keweenaw Point': (47.42, -87.70), 'Caribou Island': (47.36, -85.83), 'Whitefish Point': (46.77, -84.96),
    'Wreck': (46.9985, -85.11), 'Fort William': (48.38, -89.25), 'Superior': (46.72, -92.10),
    'Grand Marais': (46.67, -85.98), 'Michipicoten Island': (47.73, -85.80), 'The Soo': (46.50, -84.35),
    'Sixfathom': (47.43, -85.95), 'Bannock': (48.30, -87.60),
})
SUP = View(47.55, -88.0, 205)
EASTV = View(47.35, -86.2, 330)
SHOALV = View(47.80, -87.5, 520)
FITZ_ROUTE = [(46.72, -92.10), (47.10, -91.0), (47.60, -89.75), (47.95, -88.55), (48.05, -87.10), (47.85, -86.15),
              (47.42, -85.90), (47.20, -85.55), (46.9985, -85.11)]
SWEEP_ROUTE = [(48.38, -89.25), (48.25, -88.95), (47.58, -87.08), (46.77, -84.96), (46.50, -84.35)]


def sonar(cr, x, y, t, color=OR, r0=9, rings=3, period=2.2, a=1.0, rmax=120):
    for k in range(rings):
        ph = ((t + k * period / rings) % period) / period
        circle(cr, x, y, r0 + rmax * ph, color, a * (1 - ph) * 0.7, fill=False, width=2.5)
    circle(cr, x, y, r0, color, a)


def grid(cr, v, a=0.18):
    cr.set_line_width(1); cr.set_source_rgba(*CY, a)
    for lat in np.arange(46, 50.01, 0.5):
        x0, y = v.xy(lat, -95); cr.move_to(0, y); cr.line_to(W, y); cr.stroke()
    for lon in np.arange(-93, -83, 1.0):
        x, y0 = v.xy(50, lon); cr.move_to(x, 0); cr.line_to(x, H); cr.stroke()


def map_base(cr, v, t, label=None, lakelabel=True):
    basemap(cr, v, labels=False)
    grid(cr, v)
    if lakelabel:
        font(cr, MONO, 26); x, y = v.xy(47.25, -88.9)
        if 0 < x < W: text(cr, 'LAKE SUPERIOR', x, y, CY, 0.55, 'center', tracking=8)
    hud(cr, t, label or 'FILE 03 · CHART', None)


def pin(cr, v, name, t, start, lab=None, color=WH, dx=18, dy=10, size=30, align='left', bold=True, ring=False):
    a = ramp(t, start, 0.4)
    if a <= 0: return
    x, y = v.xy(*PLACES[name]) if isinstance(name, str) else v.xy(*name)
    if ring: sonar(cr, x, y, t - start, color, a=a)
    else: circle(cr, x, y, 7, color, a)
    font(cr, BODY, size, bold=bold)
    s = lab if lab is not None else name
    if align == 'left': text(cr, s, x + dx, y + dy, color, a)
    else: text(cr, s, x - dx, y + dy, color, a, 'right')


def path(cr, v, pts, t, start, dur, color=OR, width=5, dash=None, a=1.0, arrow_head=True):
    p = [v.xy(*q) for q in pts]
    prog = ease_in_out((t - start) / dur) if t > start else 0
    if prog <= 0: return
    if dash: cr.set_dash(dash)
    arrow(cr, p, color, a, width, 22 if arrow_head else 0.1, prog)
    cr.set_dash([])


def miles_line(cr, p0, p1, s, a, color=WH):
    if a <= 0: return
    cr.set_source_rgba(*color, a); cr.set_line_width(2.5); cr.set_dash([10, 8])
    cr.move_to(*p0); cr.line_to(*p1); cr.stroke(); cr.set_dash([])
    mx, my = (p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2
    font(cr, MONO, 26, bold=True); w = text_width(cr, s, 2)
    box(cr, mx - w / 2 - 14, my - 26, w + 28, 40, 6, fill=(0.02, 0.07, 0.09), fa=0.85 * a)
    text(cr, s, mx - w / 2, my + 4, color, a, tracking=2)


def shoal_mark(cr, v, t, start, label=True, big=False):
    a = ramp(t, start, 0.5)
    if a <= 0: return
    x, y = v.xy(*PLACES['Superior Shoal'])
    sonar(cr, x, y, t - start, OR, a=a, rmax=160 if big else 110)
    if label:
        font(cr, HEAD, 34); text(cr, 'SUPERIOR SHOAL', x + 24, y - 20, OR, a)
        font(cr, MONO, 22); text(cr, 'TOP: 21 FT DOWN', x + 26, y + 14, WH, a * 0.85, tracking=2)


# ---------------------------------------------------------------- the cutaway (lake in cross-section)
SURF_Y = 330


def bed(x, peak_x=1000, peak_y=None, scale=1.0):
    """Lake floor profile: deep, with one steep mountain."""
    base = 960 + 30 * math.sin(x / 260)
    py = peak_y if peak_y is not None else SURF_Y + 32
    w = 330 * scale
    m = max(0.0, 1 - abs(x - peak_x) / w) ** 1.55
    jag = 10 * math.sin(x / 23) + 6 * math.sin(x / 9)
    return base - (base - py) * m + jag * m


def water_column(cr, t, wave=1.0):
    g = cairo.LinearGradient(0, SURF_Y, 0, H)
    g.add_color_stop_rgb(0, 0.07, 0.30, 0.36); g.add_color_stop_rgb(0.5, 0.03, 0.15, 0.20); g.add_color_stop_rgb(1, 0.01, 0.05, 0.07)
    cr.set_source(g)
    cr.move_to(0, H)
    for x in range(0, W + 41, 40):
        cr.line_to(x, SURF_Y + wave * 6 * math.sin(x / 70 + t * 2.2))
    cr.line_to(W, H); cr.close_path(); cr.fill()
    g = cairo.LinearGradient(0, 0, 0, SURF_Y)
    g.add_color_stop_rgb(0, 0.02, 0.05, 0.07); g.add_color_stop_rgb(1, 0.08, 0.14, 0.17)
    cr.set_source(g); cr.rectangle(0, 0, W, SURF_Y - 8); cr.fill()
    for k in range(7):   # light shafts
        x = 200 + k * 260 + 40 * math.sin(t * 0.4 + k)
        g = cairo.LinearGradient(x, SURF_Y, x + 120, H)
        g.add_color_stop_rgba(0, 0.5, 0.85, 0.85, 0.07); g.add_color_stop_rgba(1, 0.5, 0.85, 0.85, 0)
        cr.set_source(g); cr.move_to(x, SURF_Y); cr.line_to(x + 60, SURF_Y); cr.line_to(x + 260, H); cr.line_to(x + 120, H); cr.close_path(); cr.fill()


def mountain(cr, rise=1.0, peak_x=1000, peak_y=None, color=(0.05, 0.08, 0.09)):
    py = peak_y if peak_y is not None else SURF_Y + 32
    py = 1000 - (1000 - py) * rise
    cr.move_to(0, H)
    for x in range(0, W + 9, 8): cr.line_to(x, bed(x, peak_x, py))
    cr.line_to(W, H); cr.close_path()
    g = cairo.LinearGradient(0, py, 0, H)
    g.add_color_stop_rgb(0, 0.16, 0.20, 0.20); g.add_color_stop_rgb(1, *color)
    cr.set_source(g); cr.fill_preserve()
    cr.set_source_rgba(*CY, 0.35); cr.set_line_width(2); cr.stroke()


def ship(cr, x, y, L=900, a=1.0, sink=0.0, tilt=0.0, draft=34):
    """Side view of a 1970s laker: pilothouse at the very front, engine house and funnel at the very back.
    (x, y) is the bow at the waterline; draws toward the left (stern at x - L)."""
    cr.save(); cr.translate(x, y + sink); cr.rotate(tilt)
    hull = [(0, -26), (-L, -26), (-L - 6, 0), (-L + 10, draft), (-18, draft), (12, -2)]
    cr.move_to(*hull[0])
    for p in hull[1:]: cr.line_to(*p)
    cr.close_path(); cr.set_source_rgba(0.10, 0.10, 0.11, a); cr.fill_preserve()
    cr.set_source_rgba(*OR, 0.6 * a); cr.set_line_width(2); cr.stroke()
    cr.set_source_rgba(0.85, 0.86, 0.84, a)
    cr.rectangle(-110, -78, 92, 52); cr.fill(); cr.rectangle(-96, -104, 64, 26); cr.fill()      # pilothouse forward
    cr.rectangle(-L + 10, -84, 130, 58); cr.fill()                                              # engine house aft
    cr.set_source_rgba(0.15, 0.15, 0.16, a); cr.rectangle(-L + 46, -132, 34, 50); cr.fill()      # funnel
    for k in range(6):
        cr.set_source_rgba(*OR, 0.9 * a); cr.arc(-150 - k * (L - 300) / 5, -32, 3.5, 0, 2 * math.pi); cr.fill()
    cr.restore()


def depth_scale(cr, t, a=1.0, px_per_ft=None, label_every=50, x=150, max_ft=400):
    ppf = px_per_ft or (630 / 400)
    cr.set_source_rgba(*CY, 0.6 * a); cr.set_line_width(2); cr.move_to(x, SURF_Y); cr.line_to(x, min(H - 40, SURF_Y + max_ft * ppf)); cr.stroke()
    font(cr, MONO, 20)
    f = 0
    while f <= max_ft:
        y = SURF_Y + f * ppf
        if y > H - 40: break
        cr.move_to(x, y); cr.line_to(x + 14, y); cr.stroke()
        text(cr, '%d FT' % f, x - 12, y + 7, CY, 0.7 * a, 'right', tracking=1)
        f += label_every


def dim_v(cr, x, y0, y1, s, a, color=OR, side='right'):
    if a <= 0: return
    cr.set_source_rgba(*color, a); cr.set_line_width(3)
    cr.move_to(x, y0); cr.line_to(x, y1); cr.stroke()
    for y in (y0, y1): cr.move_to(x - 12, y); cr.line_to(x + 12, y); cr.stroke()
    font(cr, HEAD, 54)
    if side == 'right': text(cr, s, x + 26, (y0 + y1) / 2 + 20, color, a)
    else: text(cr, s, x - 26, (y0 + y1) / 2 + 20, color, a, 'right')


def cutaway(cr, t, d, rise=1.0, ship_x=None, ship_a=0.0, peak_label=True, sink=0.0, tilt=0.0, label=True):
    water_column(cr, t)
    mountain(cr, rise)
    if ship_x is not None and ship_a > 0: ship(cr, ship_x, SURF_Y, a=ship_a, sink=sink, tilt=tilt)
    hud(cr, t, 'FILE 03 · CROSS-SECTION, NOT TO SCALE', None)
    if label:
        font(cr, MONO, 24); text(cr, 'SURFACE', 90, SURF_Y - 16, CY, 0.75, tracking=3)


# ---------------------------------------------------------------- side view of the seiche
def seiche(cr, t, d, amp=1.0):
    background(cr)
    x0, x1, y0 = 180, W - 180, 560
    ph = math.sin(t * 1.4) * amp
    cr.move_to(x0, y0 + 300)
    for x in np.linspace(x0, x1, 80):
        f = (x - x0) / (x1 - x0)
        cr.line_to(x, y0 + 90 * ph * (2 * f - 1))
    cr.line_to(x1, y0 + 300); cr.close_path()
    g = cairo.LinearGradient(0, y0 - 100, 0, y0 + 300)
    g.add_color_stop_rgb(0, 0.10, 0.40, 0.46); g.add_color_stop_rgb(1, 0.02, 0.10, 0.14)
    cr.set_source(g); cr.fill()
    cr.set_source_rgba(*GR, 0.8); cr.set_line_width(5)
    cr.move_to(x0 - 20, y0 - 160); cr.line_to(x0, y0 + 300); cr.line_to(x1, y0 + 300); cr.line_to(x1 + 20, y0 - 160); cr.stroke()
    hud(cr, t, 'FILE 03 · LAKE SUPERIOR, SIDE VIEW', None)
    head(cr, 'THE LAKE ROCKED', W / 2, 250, 84, WH, align='center', t=t, start=0.1)
    mono(cr, 'A SEICHE: THE WHOLE LAKE SLOSHING END TO END', W / 2, 320, 28, OR, align='center', t=t, start=0.5, bold=True)
    font(cr, MONO, 26); text(cr, 'WEST', x0 + 10, y0 + 360, CY, 0.8, tracking=3); text(cr, 'EAST · THE SOO', x1 - 10, y0 + 360, CY, 0.8, 'right', tracking=3)


# ---------------------------------------------------------------- engagement graphics
def cursor(cr, x, y, a=1.0, press=0.0):
    s = 1.0 - 0.15 * press
    cr.save(); cr.translate(x, y); cr.scale(s * 1.6, s * 1.6)
    cr.move_to(0, 0); cr.line_to(0, 34); cr.line_to(9, 26); cr.line_to(15, 40); cr.line_to(21, 37); cr.line_to(15, 24); cr.line_to(27, 24); cr.close_path()
    cr.set_source_rgba(1, 1, 1, a); cr.fill_preserve(); cr.set_source_rgba(0, 0, 0, a); cr.set_line_width(2); cr.stroke()
    cr.restore()


def bell(cr, x, y, s, a, ring=0.0, filled=False):
    cr.save(); cr.translate(x, y); cr.rotate(0.35 * math.sin(ring * 18) * math.exp(-ring * 3) if ring > 0 else 0); cr.scale(s, s)
    cr.move_to(-30, 22); cr.curve_to(-30, -10, -24, -36, 0, -38); cr.curve_to(24, -36, 30, -10, 30, 22); cr.line_to(38, 30); cr.line_to(-38, 30); cr.close_path()
    cr.set_source_rgba(*WH, a)
    if filled: cr.fill()
    else: cr.set_line_width(6); cr.stroke()
    cr.arc(0, 40, 8, 0, 2 * math.pi); cr.fill()
    cr.restore()


def thumb(cr, x, y, s, a, filled):
    cr.save(); cr.translate(x, y); cr.scale(s, s)
    cr.move_to(-40, -6); cr.line_to(-18, -6); cr.line_to(-18, 46); cr.line_to(-40, 46); cr.close_path()
    cr.move_to(-10, -6); cr.line_to(6, -44); cr.curve_to(16, -54, 30, -48, 26, -32); cr.line_to(20, -10)
    cr.line_to(46, -10); cr.curve_to(58, -10, 60, 2, 54, 8); cr.curve_to(60, 16, 56, 26, 48, 28)
    cr.curve_to(52, 36, 46, 46, 36, 46); cr.line_to(-10, 46); cr.close_path()
    cr.set_source_rgba(*WH, a)
    if filled: cr.fill()
    else: cr.set_line_width(6); cr.set_line_join(cairo.LINE_JOIN_ROUND); cr.stroke()
    cr.restore()


def sub_button(cr, cx, cy, t, click_at, a=1.0, scale=1.0):
    clicked = t > click_at
    press = max(0.0, 1 - abs(t - click_at) / 0.15)
    s = scale * (1 - 0.06 * press)
    w, h = 460 * s, 112 * s
    box(cr, cx - w / 2, cy - h / 2, w, h, h / 2, fill=(0.30, 0.33, 0.34) if clicked else (0.86, 0.13, 0.13), fa=a)
    font(cr, BODY, 52 * s, bold=True)
    text(cr, 'SUBSCRIBED' if clicked else 'SUBSCRIBE', cx, cy + 18 * s, WH, a, 'center')
    return clicked


def subscribe_anim(cr, gid, t, d, big='SUBSCRIBE', line='It\'s free. It takes one second.', y=560):
    backdrop(cr, gid, t, d, dark=0.34); hud(cr, t)
    k = ramp(t, 0, 0.4)
    click = min(2.2, d * 0.45)
    sub_button(cr, W / 2 - 80, y, t, click, k)
    bell(cr, W / 2 + 260, y, 1.3, k, ring=max(0, t - click - 0.5), filled=t > click + 0.5)
    if t > click + 0.5:
        sonar(cr, W / 2 + 260, y, t - click - 0.5, OR, r0=0.1, rings=2, a=0.9, rmax=90)
    cx = W / 2 + 260 * min(1, max(0, (t - click - 0.15) / 0.3)) * (t > click) - 60 + 300 * (1 - ramp(t, 0.4, click - 0.4))
    cy = y + 10 + 220 * (1 - ramp(t, 0.4, click - 0.4))
    cursor(cr, cx, cy, k, press=max(0.0, 1 - abs(t - click) / 0.15))
    mono(cr, line.upper(), W / 2, y + 160, 30, WH, align='center', t=t, start=0.6, bold=True)


def like_anim(cr, gid, t, d):
    backdrop(cr, gid, t, d, dark=0.34); hud(cr, t)
    k = ramp(t, 0, 0.4); y = 540
    c1, c2 = 1.3, 3.2
    liked = t > c1
    pop = 1 + 0.25 * max(0.0, 1 - abs(t - c1) / 0.25)
    box(cr, W / 2 - 520, y - 80, 300, 160, 80, fill=(0.2, 0.24, 0.26), fa=0.85 * k)
    thumb(cr, W / 2 - 370, y + 4, 1.25 * pop, k, liked)
    if liked: sonar(cr, W / 2 - 370, y, t - c1, OR, r0=0.1, rings=2, a=0.8, rmax=110)
    sub_button(cr, W / 2 + 230, y, t, c2, k)
    if t < c1: cx, cy = W / 2 - 380 + 300 * (1 - ramp(t, 0.2, c1 - 0.2)), y + 260 * (1 - ramp(t, 0.2, c1 - 0.2))
    else: f = ramp(t, c1 + 0.3, c2 - c1 - 0.5); cx, cy = W / 2 - 380 + 620 * f, y + 10
    cursor(cr, cx, cy + 10, k, press=max(0.0, 1 - min(abs(t - c1), abs(t - c2)) / 0.15))
    mono(cr, 'LIKE  +  SUBSCRIBE', W / 2, 340, 34, OR, align='center', t=t, start=0.2, bold=True)
    mono(cr, 'IT HELPS A SMALL CHANNEL MORE THAN YOU THINK', W / 2, y + 190, 28, WH, align='center', t=t, start=0.8, bold=True)


def comment_box(cr, x, y, w, typed, t, start, a=1.0, cps=8):
    box(cr, x, y, w, 120, 18, fill=(0.06, 0.12, 0.14), fa=0.92 * a, stroke=CY, sa=0.6 * a)
    circle(cr, x + 62, y + 60, 30, OR, a)
    font(cr, HEAD, 30); text(cr, 'Y', x + 62, y + 71, (0.05, 0.1, 0.12), a, 'center')
    n = int(max(0, t - start) * cps); s = typed[:n]
    font(cr, BODY, 46, bold=True); text(cr, s, x + 120, y + 76, WH, a)
    if int(t * 3) % 2 == 0:
        cr.set_source_rgba(*WH, a); cr.rectangle(x + 124 + text_width(cr, s), y + 38, 4, 50); cr.fill()


# ================================================================ the graphics, in order
@reg('G01')
def g01(cr, t, d):
    card_quote(cr, 'G01', t, d, ['"We are holding', 'our own."'], 'CAPT. ERNEST McSORLEY · 7:10 P.M. · 10 NOVEMBER 1975', size=96)


@reg('G02')
def g02(cr, t, d):
    card_number(cr, 'G02', t, d, 29, 'MEN ON BOARD', 'No mayday. No bodies ever recovered.')


@reg('G03')
def g03(cr, t, d):
    map_base(cr, SUP, t, 'FILE 03 · LAKE SUPERIOR')
    pin(cr, SUP, 'Wreck', t, 0.2, 'EDMUND FITZGERALD', OR, dx=-22, dy=-18, size=30, align='right', ring=True)
    pin(cr, SUP, 'Whitefish Point', t, 0.8, 'Whitefish Point', WH, dx=16, dy=36, size=26, bold=False)


@reg('G04')
def g04(cr, t, d):
    map_base(cr, SUP, t, 'FILE 03 · LAKE SUPERIOR')
    pin(cr, SUP, 'Wreck', t, 0.0, 'THE WRECK', OR, dx=-22, dy=-18, size=28, align='right', ring=True)
    a = ramp(t, 0.6, 1.4)
    p0 = SUP.xy(*PLACES['Wreck']); p1 = SUP.xy(*PLACES['Superior Shoal'])
    if a > 0:
        q = (p0[0] + (p1[0] - p0[0]) * a, p0[1] + (p1[1] - p0[1]) * a)
        miles_line(cr, p0, q, 'ABOUT 120 MILES' if a > 0.9 else '', 1.0)
    shoal_mark(cr, SUP, t, 2.0)


@reg('G05')
def g05(cr, t, d):
    rise = ease_out((t - 0.2) / 2.0) if t > 0.2 else 0
    cr.save()
    z = 1.0 + 0.9 * ease_in_out((t - 2.6) / 2.2) if t > 2.6 else 1.0
    cr.translate(1000, SURF_Y + 40); cr.scale(z, z); cr.translate(-1000, -(SURF_Y + 40))
    cutaway(cr, t, d, rise=rise)
    cr.restore()
    depth_scale(cr, t, 1 - ramp(t, 2.4, 0.4))
    a = ramp(t, 3.4, 0.5)
    dim_v(cr, 1060, SURF_Y, SURF_Y + 32 * 1.9, '21 FT', a)
    head(cr, 'A MOUNTAIN', 120, 210, 80, WH, t=t, start=0.4)
    mono(cr, 'IN THE MIDDLE OF LAKE SUPERIOR', 124, 262, 26, CY, t=t, start=0.8, bold=True)


@reg('G06')
def g06(cr, t, d):
    z = 1.9
    cr.save(); cr.translate(1000, SURF_Y + 40); cr.scale(z, z); cr.translate(-1000, -(SURF_Y + 40))
    sx = 2300 - 1150 * ease_out(t / 2.2)
    cutaway(cr, t, d, ship_x=sx, ship_a=1.0, label=False)
    cr.restore()
    a = ramp(t, 2.2, 0.5)
    dim_v(cr, 760, SURF_Y, SURF_Y + 34 * 1.9 + 4, '25 FT', a, OR, 'left')
    dim_v(cr, 1080, SURF_Y, SURF_Y + 32 * 1.9, '21 FT', ramp(t, 2.8, 0.5), CY)
    head(cr, 'FULLY LOADED', 120, 960, 80, WH, t=t, start=0.3)
    mono(cr, 'THE FITZGERALD SAT ABOUT 25 FT DEEP', 124, 1012, 26, OR, t=t, start=0.7, bold=True)


@reg('G07')
def g07(cr, t, d):
    backdrop(cr, 'G07', t, d, dark=0.3); hud(cr, t)
    mono(cr, 'YOU ARE WATCHING', W / 2, 430, 30, CY, align='center', t=t, start=0.0, bold=True)
    head(cr, 'GREAT LAKES FILES', W / 2, 580, 140, WH, align='center', t=t, start=0.15)
    bar(cr, W / 2 - 300, 620, 600, t, 0.4)
    mono(cr, 'THE PLACES HIDDEN IN AND UNDER THESE LAKES', W / 2, 690, 28, OR, align='center', t=t, start=0.6, bold=True)


@reg('G08')
def g08(cr, t, d):
    subscribe_anim(cr, 'G08', t, d)


@reg('G09')
def g09(cr, t, d):
    v = View.lerp(SUP, SHOALV, (t - 1.6) / 2.6) if t > 1.6 else SUP
    map_base(cr, v, t, 'FILE 03 · SUPERIOR SHOAL')
    pin(cr, v, 'Copper Harbor', t, 1.0, 'Copper Harbor', WH, dx=16, dy=36, size=28)
    pin(cr, v, 'Keweenaw Point', t, 1.4, 'KEWEENAW PENINSULA', GR, dx=18, dy=50, size=22, bold=False)
    shoal_mark(cr, v, t, 2.2, big=True)
    a = ramp(t, 4.6, 0.6)
    if a > 0: miles_line(cr, v.xy(*PLACES['Copper Harbor']), v.xy(*PLACES['Superior Shoal']), '50 MILES OUT', a)
    k = 1 - ramp(t, 1.4, 0.5)
    if k > 0:
        cr.set_source_rgba(0.02, 0.06, 0.08, 0.7 * k); cr.paint()
        head(cr, 'SUPERIOR SHOAL', W / 2, 560, 150, WH, a=k, align='center', t=t, start=0.0)


@reg('G10')
def g10(cr, t, d):
    map_base(cr, SHOALV, t, 'FILE 03 · SUPERIOR SHOAL')
    x, y = SHOALV.xy(*PLACES['Superior Shoal'])
    k = max(0.02, ease_out(t / 1.2))
    cr.save(); cr.translate(x, y); cr.scale(k, k)
    cr.move_to(-120, -10)
    for ang in np.linspace(0, 2 * math.pi, 40):
        r = 110 + 18 * math.sin(ang * 3) + 10 * math.sin(ang * 7)
        cr.line_to(r * 1.5 * math.cos(ang), r * math.sin(ang))
    cr.close_path(); cr.set_source_rgba(*OR, 0.22); cr.fill_preserve(); cr.set_source_rgba(*OR, 0.9); cr.set_line_width(3); cr.stroke()
    cr.restore()
    head(cr, 'ABOUT 20 SQ MILES', x, y + 230, 64, WH, align='center', t=t, start=0.6)


@reg('G11')
def g11(cr, t, d):
    map_base(cr, SUP, t, 'FILE 03 · GEOLOGY')
    pts = [(46.5, -92.4), (47.3, -90.5), (47.9, -88.6), (48.1, -87.0), (47.6, -85.6), (46.8, -84.9)]
    p = [SUP.xy(*q) for q in pts]
    prog = ease_in_out(t / 1.6)
    cr.set_dash([16, 10]); arrow(cr, p, OR, 0.9, 7, 0.1, prog); cr.set_dash([])
    head(cr, '1.1 BILLION YEARS AGO', 140, 900, 66, WH, t=t, start=0.6)
    mono(cr, 'THE CONTINENT TRIED TO SPLIT · LAVA POURED OUT', 144, 955, 26, OR, t=t, start=1.0, bold=True)


@reg('G12')
def g12(cr, t, d):
    background(cr); hud(cr, t, 'FILE 03 · SUPERIOR SHOAL, RELIEF', None)
    # four ridges as layered sonar-style contour lines
    cx, cy = W / 2, 600
    rid = [('NORTH RIDGE', -230, 0.55), ('CENTRAL RIDGE', -60, 1.0), ('HALFWAY RIDGE', 90, 0.85), ('SOUTH RIDGE', 230, 0.6)]
    for i, (name, dy, hgt) in enumerate(rid):
        a = ramp(t, 0.3 + i * 0.45, 0.5)
        if a <= 0: continue
        for k in range(6):
            cr.set_source_rgba(*CY, a * (0.25 + 0.12 * k)); cr.set_line_width(2)
            cr.move_to(cx - 640, cy + dy + 40)
            for x in np.linspace(-640, 640, 90):
                y = cy + dy + 40 - hgt * (60 - k * 8) * math.exp(-((x + 80 * i - 120) / 330) ** 2) * (1 + 0.15 * math.sin(x / 40 + i))
                cr.line_to(cx + x, y - k * 9)
            cr.stroke()
        font(cr, MONO, 22, bold=True); text(cr, name, cx + 680, cy + dy + 30, OR if i == 1 else WH, a, tracking=2)
    a = ramp(t, 2.4, 0.5)
    if a > 0:
        cr.set_source_rgba(*RD, 0.8 * a); cr.set_line_width(4); cr.set_dash([14, 10])
        cr.move_to(cx - 700, cy - 150); cr.line_to(cx + 600, cy - 130); cr.stroke(); cr.set_dash([])
        font(cr, MONO, 22, bold=True); text(cr, 'GORGE · ISLE ROYALE FAULT', cx - 690, cy - 170, RD, a, tracking=2)
    head(cr, 'FOUR RIDGES. A FEW PEAKS.', 140, 230, 70, WH, t=t, start=0.1)


@reg('G13')
def g13(cr, t, d):
    map_base(cr, SUP, t, 'FILE 03 · CHART, BEFORE 1929', lakelabel=False)
    font(cr, MONO, 22)
    for i, (la, lo) in enumerate([(48.2, -88.0), (47.9, -87.6), (48.0, -86.6), (47.6, -86.9), (48.25, -86.9)]):
        a = ramp(t, 0.2 + i * 0.15, 0.3); x, y = SUP.xy(la, lo); text(cr, '?', x, y, WH, 0.7 * a, 'center')
    x, y = SUP.xy(*PLACES['Superior Shoal'])
    head(cr, '"HUNDREDS OF FEET DEEP"', x, y - 140, 56, WH, align='center', t=t, start=0.6)
    mono(cr, 'NOTHING MARKED HERE', x, y - 90, 26, OR, align='center', t=t, start=1.1, bold=True)


@reg('G14')
def g14(cr, t, d):
    card_date(cr, 'G14', t, d, '21 NOV 1902', 'THE BANNOCKBURN', 'Canadian steel freighter, heading east with grain')


@reg('G15')
def g15(cr, t, d):
    card_number(cr, 'G15', t, d, 85000, 'BUSHELS OF WHEAT', 'Loaded at Fort William')


@reg('G16')
def g16(cr, t, d):
    backdrop(cr, 'G16', t, d); hud(cr, t)
    mono(cr, 'CREW', 220, 360, 28, CY, t=t, start=0.0, bold=True)
    rows = [('CAPTAIN, OLDEST ON BOARD', '37'), ('MOST OF THE CREW', '17–20'), ('ONE WHEELSMAN', '16')]
    for i, (a_, b_) in enumerate(rows):
        y = 470 + i * 150; k = ramp(t, 0.2 + i * 0.5, 0.4)
        head(cr, b_, 220, y + 30, 110, OR if i == 2 else WH, a=k)
        mono(cr, a_, 620, y, 32, WH, a=k, bold=True)
        cr.set_source_rgba(*CY, 0.3 * k); cr.rectangle(220, y + 56, 1300, 2); cr.fill()


@reg('G17')
def g17(cr, t, d):
    v = View.lerp(SUP, View(48.1, -87.8, 420), t / 2.0)
    map_base(cr, v, t, 'FILE 03 · 21 NOVEMBER 1902, ABOUT NOON')
    pin(cr, v, 'Isle Royale', t, 0.4, 'Isle Royale', WH, dx=-16, dy=-20, size=28, align='right')
    b = PLACES['Bannock']; alg = (48.38, -87.78)
    pin(cr, v, alg, t, 1.0, 'ALGONQUIN', WH, dx=18, dy=-12, size=26)
    a_vis = ramp(t, 1.4, 0.4) * (1 - ramp(t, d - 1.3, 0.3))
    pin(cr, v, b, t, 1.4, 'BANNOCKBURN', OR, dx=18, dy=34, size=26, ring=True) if a_vis > 0.02 else None
    a = ramp(t, 2.2, 0.5)
    if a > 0: miles_line(cr, v.xy(*alg), v.xy(*b), '7 MILES', a)
    mono(cr, 'SHE WAS THERE · THEN SHE WASN\'T', 140, 960, 28, OR, t=t, start=d - 1.4, bold=True)


@reg('G18')
def g18(cr, t, d):
    map_base(cr, SUP, t, 'FILE 03 · THE BANNOCKBURN\'S COURSE')
    path(cr, SUP, [(48.38, -89.25), (48.15, -88.3), PLACES['Bannock']], t, 0.0, 1.2, WH, 5, arrow_head=False)
    path(cr, SUP, [PLACES['Bannock'], (47.6, -86.3), (46.8, -84.95), (46.5, -84.35)], t, 1.2, 1.4, GR, 4, dash=[10, 10], a=0.6)
    pin(cr, SUP, 'The Soo', t, 1.6, 'Sault Ste. Marie', WH, dx=-16, dy=40, size=26, align='right')
    stamp(cr, 'NEVER ARRIVED', W / 2 + 300, 280, t, 2.4, 52)


@reg('G19')
def g19(cr, t, d):
    card_quote(cr, 'G19', t, d, ['"The steamer Bannockburn has been', 'located... Crew safe."'], 'NEWSPAPER, NOVEMBER 1902', size=68)
    stamp(cr, 'NOT TRUE', W - 460, 820, t, 3.0, 60)


@reg('G20')
def g20(cr, t, d):
    backdrop(cr, 'G20', t, d); hud(cr, t)
    head(cr, 'NO WRECK.', W / 2, 500, 140, WH, align='center', t=t, start=0.0)
    head(cr, 'NO BODIES.', W / 2, 660, 140, OR, align='center', t=t, start=0.6)


@reg('G21')
def g21(cr, t, d):
    card_lines(cr, 'G21', t, d, 'THEORIES', ['A boiler explosion', 'A reef near Caribou Island', 'Superior Shoal'], step=0.9)
    if t > 3.0:
        a = ramp(t, 3.0, 0.4); cr.set_source_rgba(*OR, a); cr.set_line_width(4)
        box(cr, 236, 440 + 2 * 91 - 60, 680, 84, 10, stroke=OR, sa=a, lw=4)


@reg('G22')
def g22(cr, t, d):
    v = View.lerp(SUP, View(47.9, -87.6, 330), t / 2.5)
    map_base(cr, v, t, 'FILE 03 · THE OPEN WATER')
    b = v.xy(*PLACES['Bannock'])
    a = ramp(t, 0.3, 0.5)
    if a > 0:
        g = cairo.RadialGradient(b[0], b[1], 10, b[0], b[1], 130); g.add_color_stop_rgba(0, *WH, 0.25 * a); g.add_color_stop_rgba(1, *WH, 0)
        cr.set_source(g); cr.arc(b[0], b[1], 130, 0, 2 * math.pi); cr.fill()
        font(cr, BODY, 26, bold=True); text(cr, 'Last seen (approx.)', b[0], b[1] - 140, WH, a, 'center')
    shoal_mark(cr, v, t, 2.0, big=True)
    a = ramp(t, 3.6, 0.6)
    if a > 0: mono(cr, 'IN 1902: ON NO CHART AT ALL', 140, 960, 30, OR, t=t, start=3.6, bold=True)


@reg('G23')
def g23(cr, t, d):
    backdrop(cr, 'G23', t, d); hud(cr, t)
    mono(cr, 'FRENCH NAVY · NAVARIN CLASS · BUILT 1918', 220, 380, 28, CY, t=t, start=0.0, bold=True)
    head(cr, '12 MINESWEEPERS', 214, 520, 120, WH, t=t, start=0.2)
    head(cr, '135 FT · 2 DECK GUNS', 214, 660, 84, OR, t=t, start=0.8)
    mono(cr, 'BUILT AT FORT WILLIAM, ONTARIO', 220, 740, 28, WH, t=t, start=1.4, bold=True)


@reg('G24')
def g24(cr, t, d):
    card_date(cr, 'G24', t, d, '11 NOV 1918', 'THE WAR IS OVER', 'But the ships still had to sail to France')


@reg('G25')
def g25(cr, t, d):
    backdrop(cr, 'G25', t, d); hud(cr, t)
    mono(cr, 'LATE NOVEMBER 1918 · THREE SHIPS SAIL TOGETHER', W / 2, 330, 28, CY, align='center', t=t, start=0.0, bold=True)
    for i, n in enumerate(['SEBASTOPOL', 'INKERMAN', 'CERISOLES']):
        head(cr, n, W / 2, 480 + i * 150, 110, WH, align='center', t=t, start=0.3 + i * 0.6)


@reg('G26')
def g26(cr, t, d):
    backdrop(cr, 'G26', t, d); hud(cr, t)
    v = count(t, 0.1, 1.2, 78)
    font(cr, HEAD, 300); text(cr, str(v), W / 2, 560, OR, ramp(t, 0, 0.3), 'center')
    mono(cr, 'MEN LOST', W / 2, 660, 40, WH, align='center', t=t, start=0.5, bold=True)
    body(cr, 'The worst loss of life Lake Superior has ever seen', W / 2, 740, 36, GR, align='center', t=t, start=1.0)
    stamp(cr, 'NEVER FOUND', W / 2, 880, t, 2.4, 50)


@reg('G27')
def g27(cr, t, d):
    card_title(cr, 'G27', t, d, '1918', ['THE LAST WARSHIPS', 'EVER LOST ON', 'THE GREAT LAKES'], 104)


@reg('G28')
def g28(cr, t, d):
    map_base(cr, SUP, t, 'FILE 03 · 24 NOVEMBER 1918')
    pin(cr, SUP, 'Fort William', t, 0.0, 'Fort William', WH, dx=-16, dy=-14, size=28, align='right')
    path(cr, SUP, SWEEP_ROUTE, t, 0.6, 3.2, WH, 5)
    pin(cr, SUP, 'The Soo', t, 3.6, 'The locks', WH, dx=-16, dy=40, size=26, align='right')
    shoal_mark(cr, SUP, t, 4.2)
    a = ramp(t, 5.4, 0.6)
    if a > 0:
        miles_line(cr, SUP.xy(47.58, -87.08), SUP.xy(*PLACES['Superior Shoal']), 'ABOUT 35 MILES', a)
    mono(cr, 'ROUTE APPROXIMATE', 140, 990, 22, GR, t=t, start=1.0)


@reg('G29')
def g29(cr, t, d):
    map_base(cr, SUP, t, 'FILE 03 · CHART, 1929')
    k = ramp(t, 0.3, 0.6)
    font(cr, HEAD, 120); text(cr, '1929', 160, 260, OR, k)
    mono(cr, 'U.S. LAKE SURVEY CHARTS THE SHOAL', 166, 320, 28, WH, t=t, start=0.6, bold=True)
    shoal_mark(cr, SUP, t, 1.2, big=True)
    path(cr, SUP, SWEEP_ROUTE, t, 0.0, 0.01, GR, 3, dash=[6, 10], a=0.5, arrow_head=False)
    path(cr, SUP, [(48.38, -89.25), (48.0, -88.6), (47.35, -87.3), (46.85, -85.2), (46.5, -84.35)], t, 2.6, 2.4, OR, 5)
    mono(cr, 'SHIPPING ROUTES CHANGE', 166, 980, 28, OR, t=t, start=3.2, bold=True)


@reg('G30')
def g30(cr, t, d):
    background(cr); hud(cr, t, 'FILE 03 · SS EDMUND FITZGERALD', None)
    sx = 1700 - 300 * (1 - ease_out(t / 1.2))
    cr.save(); cr.translate(0, 0)
    ship(cr, sx, 640, L=1400, a=ramp(t, 0, 0.3))
    cr.restore()
    head(cr, '729 FT', W / 2, 420, 170, OR, align='center', t=t, start=0.2)
    mono(cr, 'BIGGEST SHIP ON THE GREAT LAKES · 1958', W / 2, 820, 28, WH, align='center', t=t, start=0.6, bold=True)


@reg('G31')
def g31(cr, t, d):
    card_number(cr, 'G31', t, d, 26116, 'TONS OF TACONITE', 'Iron ore pellets, bound for Detroit')


@reg('G32')
def g32(cr, t, d):
    map_base(cr, SUP, t, 'FILE 03 · 9 NOVEMBER 1975, EVENING')
    path(cr, SUP, FITZ_ROUTE[:3], t, 0.2, 1.4, WH, 5)
    pin(cr, SUP, 'Superior', t, 0.0, 'Superior, Wis.', WH, dx=-16, dy=40, size=26, align='right')
    a = ramp(t, 1.8, 0.8)
    if a > 0:
        cr.set_source_rgba(*RD, 0.06 * a); cr.paint()
        stamp(cr, 'GALE WARNING · WHOLE LAKE', W / 2 + 160, 260, t, 2.2, 50)
        for k in range(14):
            ph = ((t * 0.5 + k * 0.07) % 1.0)
            x = 300 + (k % 7) * 230 + ph * 200; y = 380 + (k // 7) * 320 + 40 * math.sin(k)
            arrow(cr, [(x, y), (x + 120, y + 30)], WH, 0.55 * a * math.sin(math.pi * ph), 4, 16)


@reg('G33')
def g33(cr, t, d):
    card_quote(cr, 'G33', t, d, ['"We\'re going to try', 'for some lee from', 'Isle Royale."'], 'CAPT. McSORLEY, OVERHEARD ON THE RADIO · 10 NOV 1975, AFTER 1 A.M.', size=86)


@reg('G34')
def g34(cr, t, d):
    v = View.lerp(SUP, View(47.85, -88.0, 300), (t - 5.0) / 3.0) if t > 5.0 else SUP
    map_base(cr, v, t, 'FILE 03 · THE NORTHERN COURSE')
    pin(cr, v, 'Isle Royale', t, 0.2, 'Isle Royale', WH, dx=-16, dy=-20, size=30, align='right', ring=True)
    b = v.xy(*PLACES['Bannock'])
    a = ramp(t, 1.6, 0.5)
    if a > 0:
        circle(cr, b[0], b[1], 9, GR, a); font(cr, BODY, 24); text(cr, 'Bannockburn last seen, 1902', b[0] + 16, b[1] - 14, GR, a)
    path(cr, v, FITZ_ROUTE[:6], t, 3.0, 4.5, OR, 6)
    shoal_mark(cr, v, t, 6.0)
    mono(cr, 'COURSE APPROXIMATE · AFTER HAINAULT', 140, 990, 22, GR, t=t, start=3.0)


@reg('G35')
def g35(cr, t, d):
    card_title(cr, 'G35', t, d, 'WHAT SANK HER?', ['FOUR ANSWERS'], 140)


@reg('G36')
def g36(cr, t, d):
    background(cr); hud(cr, t, 'FILE 03 · ANSWER 1 · U.S. COAST GUARD, 1977', None)
    # deck seen from above: hatch covers, water seeping in
    x0, y0 = 260, 470
    box(cr, x0 - 40, y0 - 90, 1480, 300, 30, fill=(0.12, 0.13, 0.14), fa=1)
    for k in range(10):
        x = x0 + k * 140; seep = ramp(t, 1.0 + k * 0.25, 1.0)
        box(cr, x, y0 - 50, 110, 220, 6, fill=(0.35, 0.18, 0.12), fa=1, stroke=(0, 0, 0), sa=0.6)
        if seep > 0:
            cr.set_source_rgba(*CY, 0.7 * seep); cr.set_line_width(3)
            for j in range(3):
                yy = y0 - 50 + 220 * ((t * 0.7 + j * 0.33 + k * 0.1) % 1)
                cr.move_to(x - 4, yy); cr.line_to(x - 4, yy + 18); cr.stroke(); cr.move_to(x + 114, yy); cr.line_to(x + 114, yy + 18); cr.stroke()
    head(cr, 'THE HATCH COVERS', 220, 250, 90, WH, t=t, start=0.2)
    mono(cr, 'WATER GOT IN SLOWLY, ALL DAY', 226, 830, 32, CY, t=t, start=1.6, bold=True)
    mono(cr, 'ANSWER 2 · NTSB, 1978: THE COVERS CAVED IN UNDER GIANT WAVES', 226, 890, 26, OR, t=t, start=4.6, bold=True)


@reg('G37')
def g37(cr, t, d):
    v = View.lerp(SUP, EASTV, t / 2.0)
    map_base(cr, v, t, 'FILE 03 · ANSWER 3 · THE SHIPPING COMPANIES')
    pin(cr, v, 'Caribou Island', t, 1.2, 'Caribou Island', WH, dx=18, dy=40, size=28)
    pin(cr, v, 'Sixfathom', t, 1.8, 'SIX FATHOM SHOAL', OR, dx=-18, dy=-16, size=26, align='right', ring=True)
    pin(cr, v, 'Wreck', t, 2.4, 'The wreck', WH, dx=18, dy=-10, size=24, bold=False)
    mono(cr, '"SHE HIT THE BOTTOM HERE"', 140, 980, 30, OR, t=t, start=3.0, bold=True)


@reg('G38')
def g38(cr, t, d):
    cutaway(cr, t, d)
    head(cr, 'AND THE MOUNTAIN', 120, 210, 80, OR, t=t, start=0.1)


@reg('G39')
def g39(cr, t, d):
    backdrop(cr, 'G39', t, d, dark=0.32); hud(cr, t)
    mono(cr, 'YOUR GUESS · BEFORE THE EVIDENCE', W / 2, 270, 32, OR, align='center', t=t, start=0.0, bold=True)
    names = ['WAVES', 'HATCHES', 'MOUNTAIN']; starts = [1.6, 2.3, 3.2]
    for i, n in enumerate(names):
        k = ramp(t, starts[i], 0.35)
        if k <= 0: continue
        x = W / 2 + (i - 1) * 520; y = 560
        s = 1.25 - 0.25 * k
        cr.save(); cr.translate(x, y); cr.scale(s, s)
        box(cr, -230, -170, 460, 340, 22, fill=(0.04, 0.10, 0.12), fa=0.9 * k, stroke=OR if i == 2 else CY, sa=k, lw=4)
        font(cr, HEAD, 74); text(cr, n, 0, 26, WH, k, 'center')
        font(cr, MONO, 26, bold=True); text(cr, str(i + 1), 0, -110, OR, k, 'center')
        cr.restore()
    k = ramp(t, 4.2, 0.4)
    if k > 0:
        font(cr, HEAD, 60); text(cr, 'PUT IT IN THE COMMENTS', W / 2, 900, WH, k, 'center')


@reg('G40')
def g40(cr, t, d):
    backdrop(cr, 'G40', t, d, dark=0.32); hud(cr, t)
    head(cr, 'ONE WORD IS ENOUGH', W / 2, 360, 96, WH, align='center', t=t, start=0.0)
    comment_box(cr, W / 2 - 520, 470, 1040, 'Mountain', t, 0.6, a=ramp(t, 0.3, 0.3))
    mono(cr, 'SEE IF YOU CHANGE YOUR MIND AT THE END', W / 2, 720, 28, OR, align='center', t=t, start=1.8, bold=True)


@reg('G41')
def g41(cr, t, d):
    backdrop(cr, 'G41', t, d); hud(cr, t)
    mono(cr, 'HAINAULT\'S THEORY · 10 NOVEMBER 1975', 220, 400, 28, CY, t=t, start=0.0, bold=True)
    head(cr, '9:30 A.M.', 214, 590, 200, OR, t=t, start=0.2)
    mono(cr, 'THE FITZGERALD RUNS OVER SUPERIOR SHOAL', 222, 680, 34, WH, t=t, start=0.8, bold=True)
    body(cr, 'Nearly ten hours before she sank', 222, 745, 34, GR, t=t, start=1.6)


@reg('G42')
def g42(cr, t, d):
    z = 1.9
    cr.save(); cr.translate(1000, SURF_Y + 40); cr.scale(z, z); cr.translate(-1000, -(SURF_Y + 40))
    cutaway(cr, t, d, ship_x=1150, ship_a=1.0, label=False)
    cr.restore()
    dim_v(cr, 1080, SURF_Y, SURF_Y + 32 * 1.9, '21 FT  THE PEAK', ramp(t, 0.6, 0.5), CY)
    dim_v(cr, 760, SURF_Y, SURF_Y + 34 * 1.9 + 4, 'THE SHIP  25 FT', ramp(t, 1.8, 0.5), OR, 'left')
    a = ramp(t, 3.2, 0.5)
    if a > 0:
        cr.set_source_rgba(*RD, a); cr.set_line_width(5); cr.arc(1000, SURF_Y + 60, 70, 0, 2 * math.pi); cr.stroke()
        head(cr, '4 FEET TOO DEEP', W - 120, 1000, 70, RD, a=a, align='right')
    head(cr, 'REMEMBER THE NUMBERS', 120, 1000, 70, WH, t=t, start=0.1)


@reg('G43')
def g43(cr, t, d):
    seiche(cr, t, d)
    mono(cr, 'THAT DAY: WATER 3 FT OVER THE SOO LOCK GATES', W / 2, 1000, 26, WH, align='center', t=t, start=2.5, bold=True)


@reg('G44')
def g44(cr, t, d):
    z = 1.9
    drop = 22 * (0.5 - 0.5 * math.cos(min(t, 3.0) * 2.1)) if t < 3.0 else 22
    cr.save(); cr.translate(1000, SURF_Y + 40); cr.scale(z, z); cr.translate(-1000, -(SURF_Y + 40))
    water_column(cr, t, wave=3.0); mountain(cr, 1.0)
    ship(cr, 1150, SURF_Y, a=1.0, sink=drop * 0.6)
    cr.restore()
    hud(cr, t, 'FILE 03 · HAINAULT\'S THEORY', None)
    head(cr, 'IN THE TROUGH OF A WAVE', 120, 960, 70, WH, t=t, start=0.2)
    mono(cr, 'THE SLOSH AND THE STORM DROP THE SHIP ONTO THE ROCK', 124, 1012, 26, OR, t=t, start=0.8, bold=True)
    if t > 2.8:
        a = ramp(t, 2.8, 0.2); cr.set_source_rgba(*RD, 0.35 * a * (1 - ramp(t, 3.2, 0.6))); cr.paint()


@reg('G45')
def g45(cr, t, d):
    background(cr); hud(cr, t, 'FILE 03 · HAINAULT\'S THEORY', None)
    L = 1500; x = W / 2 + L / 2; y = 560
    ship(cr, x, y, L=L, a=1.0)
    k = ramp(t, 0.6, 1.8)
    mid = x - L / 2
    if k > 0:
        w = L * 200 / 729 * k
        cr.set_source_rgba(*RD, 0.85); cr.rectangle(mid - L * 100 / 729, y + 20, w, 18); cr.fill()
        for j in range(int(18 * k)):
            sx = mid - L * 100 / 729 + j * 22
            cr.set_source_rgba(*OR, 0.8); cr.move_to(sx, y + 40); cr.line_to(sx + 8, y + 60); cr.stroke()
    a = ramp(t, 2.4, 0.5)
    if a > 0:
        cr.set_source_rgba(*WH, a); cr.set_line_width(3)
        x0 = mid - L * 100 / 729; x1 = mid + L * 100 / 729
        cr.move_to(x0, y + 110); cr.line_to(x1, y + 110); cr.stroke()
        for xx in (x0, x1): cr.move_to(xx, y + 95); cr.line_to(xx, y + 125); cr.stroke()
        head(cr, '200 FEET OF HULL', mid, y + 210, 70, OR, a=a, align='center')
        mono(cr, 'SCRAPED ACROSS THE SHOAL · PUNCTURED IN THE MIDDLE', mid, y + 260, 26, WH, a=a, align='center', bold=True)


@reg('G46')
def g46(cr, t, d):
    background(cr); hud(cr, t)
    mono(cr, 'REMEMBER THIS NUMBER TOO', W / 2, 400, 32, CY, align='center', t=t, start=0.0, bold=True)
    head(cr, '200 FEET', W / 2, 620, 220, OR, align='center', t=t, start=0.2)


@reg('G47')
def g47(cr, t, d):
    like_anim(cr, 'G47', t, d)


@reg('G48')
def g48(cr, t, d):
    backdrop(cr, 'G48', t, d); hud(cr, t)
    mono(cr, 'WHAT WE KNOW FOR CERTAIN', 220, 400, 30, CY, t=t, start=0.0, bold=True)
    head(cr, 'THE AFTERNOON', 214, 560, 140, WH, t=t, start=0.2)
    mono(cr, '10 NOVEMBER 1975', 222, 640, 36, OR, t=t, start=0.7, bold=True)


@reg('G49')
def g49(cr, t, d):
    backdrop(cr, 'G49', t, d); hud(cr, t)
    mono(cr, 'JUST AFTER 3:30 P.M. · McSORLEY TO THE ANDERSON', 220, 300, 28, CY, t=t, start=0.0, bold=True)
    items = [('A FENCE RAIL DOWN', 0.6), ('TWO VENTS LOST OR DAMAGED', 1.8), ('A LIST · LEANING TO ONE SIDE', 3.4), ('TWO PUMPS RUNNING NON-STOP', 6.0)]
    for i, (s, st) in enumerate(items):
        k = ramp(t, st, 0.4)
        if k <= 0: continue
        y = 440 + i * 140
        cr.set_source_rgba(*OR, k); cr.rectangle(220, y - 46, 14, 14); cr.fill()
        head(cr, s, 262, y, 74, WH, a=k)


@reg('G50')
def g50(cr, t, d):
    background(cr); hud(cr, t, 'FILE 03 · WHY THE RAIL MATTERS', None)
    L = 1400; x0 = W / 2 - L / 2; y = 620
    bend = ramp(t, 2.5, 3.0)
    n = 60
    top = []; bot = []
    for i in range(n + 1):
        f = i / n; xx = x0 + f * L
        dy = -110 * bend * math.exp(-((f - 0.5) / 0.22) ** 2) + 30 * bend
        top.append((xx, y - 60 + dy)); bot.append((xx, y + 30 + dy))
    cr.move_to(*top[0])
    for p in top[1:]: cr.line_to(*p)
    for p in reversed(bot): cr.line_to(*p)
    cr.close_path(); cr.set_source_rgba(0.13, 0.13, 0.14, 1); cr.fill_preserve(); cr.set_source_rgba(*OR, 0.6); cr.set_line_width(2); cr.stroke()
    tension = bend
    cr.set_source_rgba(*(RD if tension > 0.6 else WH), 0.9); cr.set_line_width(4)
    cr.move_to(top[0][0], top[0][1] - 30)
    for p in top[1:]: cr.line_to(p[0], p[1] - 30 + 0 * tension)
    cr.stroke()
    rx = W / 2
    cr.move_to(rx - 160, y + 160); cr.line_to(rx, y + 40 + 30 * bend - 110 * bend + 70); cr.line_to(rx + 160, y + 160); cr.close_path()
    cr.set_source_rgba(0.2, 0.24, 0.25, ramp(t, 1.5, 0.6)); cr.fill()
    head(cr, 'SAGGING AT BOTH ENDS. MIDDLE PUSHED UP.', W / 2, 250, 60, WH, align='center', t=t, start=0.3)
    if tension > 0.6:
        stamp(cr, 'RAIL SNAPS', rx + 380, y - 260, t, 5.6, 48)
    mono(cr, 'WHAT A HULL DOES WHEN IT DRAGS OVER ROCK', W / 2, 960, 28, OR, align='center', t=t, start=1.0, bold=True)


@reg('G51')
def g51(cr, t, d):
    v = EASTV
    map_base(cr, v, t, 'FILE 03 · THE SHIPPING COMPANIES\' SHOAL')
    path(cr, v, FITZ_ROUTE[5:], t, 0.2, 2.6, OR, 6)
    pin(cr, v, 'Caribou Island', t, 0.6, 'Caribou Island', WH, dx=18, dy=40, size=28)
    pin(cr, v, 'Sixfathom', t, 1.6, 'SIX FATHOM SHOAL', RD, dx=-18, dy=-16, size=26, align='right', ring=True)
    mono(cr, 'SHE HAD JUST PASSED IT', 140, 980, 30, WH, t=t, start=3.0, bold=True)


@reg('G52')
def g52(cr, t, d):
    card_quote(cr, 'G52', t, d, ['"Don\'t allow', 'nobody on deck."'], 'CAPT. McSORLEY, OVERHEARD BY ANOTHER CAPTAIN', size=110)


@reg('G53')
def g53(cr, t, d):
    card_quote(cr, 'G53', t, d, ['"We are holding', 'our own."'], '7:10 P.M. · THE LAST WORDS', size=120)


@reg('G54')
def g54(cr, t, d):
    card_title(cr, 'G54', t, d, 'PART 9', ['THE CASE', 'AGAINST THE', 'MOUNTAIN'], 130)


@reg('G55')
def g55(cr, t, d):
    background(cr); hud(cr, t, 'FILE 03 · THE TIMING', None)
    x0, x1, y = 260, 1660, 560
    k = ramp(t, 0.3, 0.6)
    cr.set_source_rgba(*GR, k); cr.set_line_width(4); cr.move_to(x0, y); cr.line_to(x1, y); cr.stroke()
    marks = [('9:30 A.M.', 0.0, 'Hits the mountain?', OR), ('3:30 P.M.', 0.6, 'First report of damage', WH), ('7:10 P.M.', 0.98, 'Last words', GR)]
    for i, (lab, f, sub, col) in enumerate(marks):
        a = ramp(t, 0.6 + i * 0.8, 0.4)
        x = x0 + f * (x1 - x0)
        circle(cr, x, y, 14, col, a)
        head(cr, lab, x, y - 50, 60, col, a=a, align='center')
        body(cr, sub, x, y + 70, 30, WH, a=a, align='center')
    a = ramp(t, 3.4, 0.6)
    if a > 0:
        xa, xb = x0, x0 + 0.6 * (x1 - x0)
        cr.set_source_rgba(*RD, a); cr.set_line_width(6); cr.move_to(xa, y + 140); cr.line_to(xb, y + 140); cr.stroke()
        head(cr, '6 HOURS OF SILENCE', (xa + xb) / 2, y + 230, 76, RD, a=a, align='center')
    head(cr, 'FIRST: THE TIMING', 220, 250, 80, WH, t=t, start=0.0)


@reg('G56')
def g56(cr, t, d):
    backdrop(cr, 'G56', t, d); hud(cr, t)
    head(cr, 'SECOND: THE INVESTIGATIONS', 220, 260, 72, WH, t=t, start=0.0)
    for i, (who, yr, verdict) in enumerate([('U.S. COAST GUARD', '1977', 'THE HATCH COVERS'), ('NTSB', '1978', 'THE HATCH COVERS')]):
        x = 220 + i * 760; k = ramp(t, 0.8 + i * 1.2, 0.5)
        if k <= 0: continue
        box(cr, x, 380, 700, 420, 18, fill=(0.03, 0.09, 0.11), fa=0.88 * k, stroke=CY, sa=0.6 * k)
        mono(cr, who, x + 40, 450, 32, CY, a=k, bold=True)
        head(cr, yr, x + 40, 580, 110, WH, a=k)
        mono(cr, 'FINDING:', x + 40, 680, 26, GR, a=k)
        head(cr, verdict, x + 40, 750, 56, OR, a=k)
    stamp(cr, 'NOT A SHOAL', W / 2, 920, t, 4.0, 52)


@reg('G57')
def g57(cr, t, d):
    background(cr); hud(cr, t, 'FILE 03 · WHERE THE DAMAGE WOULD BE', None)
    L = 1500; x = W / 2 + L / 2; y = 560
    ship(cr, x, y, L=L, a=1.0)
    a = ramp(t, 0.8, 0.5); mid = x - L / 2
    if a > 0:
        cr.set_source_rgba(*RD, 0.25 * a); cr.rectangle(mid - 220, y - 160, 440, 260); cr.fill()
        cr.set_source_rgba(*RD, a); cr.set_line_width(4); cr.rectangle(mid - 220, y - 160, 440, 260); cr.stroke()
        head(cr, 'THE MIDDLE', mid, y + 200, 84, RD, a=a, align='center')
    font(cr, MONO, 24, bold=True)
    text(cr, 'STERN: NO DAMAGE FOUND', x - L + 40, y + 140, WH, ramp(t, 0.2, 0.4), tracking=2)
    head(cr, 'NOT THE STERN.', 220, 250, 80, WH, t=t, start=0.0)


def wreck_layout(cr, t, gap_hi=0.0, show_nums=0.0):
    background(cr); hud(cr, t, 'FILE 03 · THE WRECK, 530 FT DOWN (U.S. NAVY SURVEY, 1976)', None)
    s = 1500 / 729; x0 = W / 2 - 729 * s / 2; y = 560
    bow = 276 * s; stern = 253 * s
    cr.set_source_rgba(0.16, 0.16, 0.17, 1); cr.rectangle(x0 + 729 * s - bow, y - 40, bow, 80); cr.fill()
    cr.rectangle(x0, y - 40, stern, 80); cr.fill()
    gx0 = x0 + stern; gx1 = x0 + 729 * s - bow
    rng = np.random.default_rng(3)
    for k in range(70):
        px = gx0 + rng.random() * (gx1 - gx0); py = y + rng.normal(0, 26)
        cr.set_source_rgba(0.3, 0.3, 0.3, 0.9); cr.arc(px, py, 3 + rng.random() * 5, 0, 2 * math.pi); cr.fill()
    if gap_hi > 0:
        cr.set_source_rgba(*RD, 0.22 * gap_hi); cr.rectangle(gx0, y - 70, gx1 - gx0, 140); cr.fill()
        cr.set_source_rgba(*RD, gap_hi); cr.set_line_width(4); cr.rectangle(gx0, y - 70, gx1 - gx0, 140); cr.stroke()
    return x0, s, y, bow, stern, gx0, gx1


@reg('G58')
def g58(cr, t, d):
    x0, s, y, bow, stern, gx0, gx1 = wreck_layout(cr, t)
    def dim(xa, xb, yy, lab, a, col=WH):
        if a <= 0: return
        cr.set_source_rgba(*col, a); cr.set_line_width(3); cr.move_to(xa, yy); cr.line_to(xb, yy); cr.stroke()
        for xx in (xa, xb): cr.move_to(xx, yy - 14); cr.line_to(xx, yy + 14); cr.stroke()
        head(cr, lab, (xa + xb) / 2, yy - 24, 56, col, a=a, align='center')
    dim(x0 + 729 * s - bow, x0 + 729 * s, y - 110, 'BOW 276 FT', ramp(t, 0.8, 0.5))
    dim(x0, x0 + stern, y - 110, 'STERN 253 FT', ramp(t, 3.0, 0.5))
    dim(x0, x0 + 729 * s, y + 170, 'THE SHIP: 729 FT', ramp(t, 6.4, 0.5), OR)


@reg('G59')
def g59(cr, t, d):
    x0, s, y, bow, stern, gx0, gx1 = wreck_layout(cr, t, gap_hi=ramp(t, 0.2, 0.5))
    font(cr, MONO, 26, bold=True); text(cr, '729 − 276 − 253 =', W / 2, y - 200, WH, ramp(t, 0.0, 0.4), 'center', tracking=2)
    head(cr, 'ABOUT 200 FT MISSING', W / 2, y + 220, 90, RD, align='center', t=t, start=0.8)


@reg('G60')
def g60(cr, t, d):
    background(cr); hud(cr, t, 'FILE 03 · TWO NUMBERS', None)
    for i, (big, lab, col) in enumerate([('200 FT', 'SCRAPED ACROSS THE MOUNTAIN · HAINAULT', OR), ('200 FT', 'MISSING FROM THE MIDDLE OF THE WRECK', RD)]):
        x = W / 2 + (i - 0.5) * 760; k = ramp(t, 0.3 + i * 1.4, 0.5)
        head(cr, big, x, 560, 170, col, a=k, align='center')
        mono(cr, lab, x, 640, 24, WH, a=k, align='center', bold=True)
    a = ramp(t, 3.6, 0.5)
    if a > 0:
        head(cr, '=', W / 2, 545, 120, WH, a=a, align='center')
    mono(cr, 'COULD BE COINCIDENCE · A SHIP THAT BREAKS IN TWO LOSES ITS MIDDLE', W / 2, 860, 26, GR, align='center', t=t, start=5.0, bold=True)


@reg('G61')
def g61(cr, t, d):
    backdrop(cr, 'G61', t, d); hud(cr, t)
    head(cr, 'INKERMAN', 220, 420, 110, WH, t=t, start=0.0)
    head(cr, 'CERISOLES', 220, 540, 110, WH, t=t, start=0.4)
    stamp(cr, 'NEVER FOUND', 1420, 480, t, 1.2, 60)
    mono(cr, '"THE HOLY GRAIL OF LAKE SUPERIOR"  · TREASURE HUNTERS', 222, 680, 28, OR, t=t, start=2.2, bold=True)
    head(cr, 'BANNOCKBURN', 220, 860, 80, GR, t=t, start=4.6)
    stamp(cr, 'NEVER FOUND', 1100, 830, t, 5.4, 44, color=GR)


@reg('G62')
def g62(cr, t, d):
    backdrop(cr, 'G62', t, d); hud(cr, t)
    mono(cr, 'THE EDMUND FITZGERALD · 530 FT DOWN', 220, 360, 28, CY, t=t, start=0.0, bold=True)
    head(cr, 'NO DIVING', 214, 520, 150, WH, t=t, start=0.2)
    head(cr, 'WITHOUT A LICENCE', 214, 640, 90, WH, t=t, start=0.6)
    mono(cr, 'ONTARIO HERITAGE ACT · FINES UP TO CA$1,000,000', 222, 730, 30, OR, t=t, start=1.2, bold=True)
    head(cr, 'IT\'S A GRAVE.', 214, 880, 84, GR, t=t, start=5.4)


@reg('G63')
def g63(cr, t, d):
    backdrop(cr, 'G63', t, d, dark=0.3); hud(cr, t)
    n = min(29, int(max(0, t - 0.2) / max(0.06, (d - 0.9) / 29)) + 1) if t > 0.2 else 0
    font(cr, HEAD, 260); text(cr, str(n), W / 2, 600, WH, ramp(t, 0, 0.2), 'center')
    mono(cr, 'ONCE FOR EACH MAN', W / 2, 700, 36, OR, align='center', t=t, start=0.2, bold=True)
    for k in range(29):
        a = 1.0 if k < n else 0.18
        circle(cr, W / 2 - 14 * 38 + k * 38, 800, 9, OR if k < n else GR, a)


@reg('G64')
def g64(cr, t, d):
    backdrop(cr, 'G64', t, d, dark=0.32); hud(cr, t)
    head(cr, 'TELL ME IN THE COMMENTS', W / 2, 330, 90, WH, align='center', t=t, start=0.0)
    mono(cr, 'DID ANYONE EVER TALK ABOUT SUPERIOR SHOAL?', W / 2, 400, 30, OR, align='center', t=t, start=0.5, bold=True)
    comment_box(cr, W / 2 - 600, 500, 1200, 'My grandfather fished the shoal...', t, 1.4, a=ramp(t, 1.0, 0.4), cps=14)
    mono(cr, 'THE BEST STORIES MIGHT END UP IN A FUTURE VIDEO', W / 2, 740, 28, CY, align='center', t=t, start=4.5, bold=True)


@reg('G65')
def g65(cr, t, d):
    card_title(cr, 'G65', t, d, 'THE VERDICT', ['DID A HIDDEN MOUNTAIN', 'SINK THE', 'EDMUND FITZGERALD?'], 96)


def verdict(cr, gid, t, d, rows, active):
    backdrop(cr, gid, t, d, dark=0.34); hud(cr, t)
    mono(cr, 'THE VERDICT', 220, 260, 30, OR, bold=True)
    for i, (who, what, col) in enumerate(rows):
        y = 400 + i * 200
        on = i < active or (i == active and True)
        k = 1.0 if i < active else (ramp(t, 0.2, 0.5) if i == active else 0)
        if k <= 0: continue
        head(cr, who, 220, y, 76, WH, a=k * (0.55 if i < active else 1))
        mono(cr, what, 222, y + 60, 32, col, a=k * (0.55 if i < active else 1), bold=True)


V_ROWS = [('THE WARSHIPS, 1918', 'ONE OF THE STRONGEST SUSPECTS', OR), ('THE BANNOCKBURN, 1902', 'ONE POSSIBILITY AMONG SEVERAL', WH),
          ('THE FITZGERALD, 1975', 'OFFICIAL ANSWER: THE HATCH COVERS · THE MOUNTAIN: A THEORY', CY)]


@reg('G66')
def g66(cr, t, d):
    verdict(cr, 'G66', t, d, V_ROWS, 0)


@reg('G67')
def g67(cr, t, d):
    verdict(cr, 'G67', t, d, V_ROWS, 1)


@reg('G68')
def g68(cr, t, d):
    verdict(cr, 'G68', t, d, V_ROWS, 2)


@reg('G69')
def g69(cr, t, d):
    cutaway(cr, t, d)
    dim_v(cr, 1060, SURF_Y, SURF_Y + 32 * 1.0 + 30, '21 FT', ramp(t, 0.4, 0.5))
    head(cr, 'STILL THERE', 120, 210, 80, WH, t=t, start=0.1)


@reg('G70')
def g70(cr, t, d):
    backdrop(cr, 'G70', t, d, dark=0.32); hud(cr, t)
    head(cr, 'YOUR VERDICT?', W / 2, 420, 150, WH, align='center', t=t, start=0.0)
    for i, (s, col) in enumerate([('YES', OR), ('NO', CY)]):
        k = ramp(t, 1.4 + i * 0.4, 0.4)
        x = W / 2 + (i - 0.5) * 520
        box(cr, x - 200, 500, 400, 160, 20, fill=(0.04, 0.10, 0.12), fa=0.9 * k, stroke=col, sa=k, lw=4)
        font(cr, HEAD, 90); text(cr, s, x, 615, col, k, 'center')
    mono(cr, 'TELL ME WHY IN THE COMMENTS · I READ EVERY ONE', W / 2, 760, 30, WH, align='center', t=t, start=3.0, bold=True)


@reg('G71')
def g71(cr, t, d):
    subscribe_anim(cr, 'G71', t, d, line='Tap the bell for the next file')


@reg('G72')
def g72(cr, t, d):
    backdrop(cr, 'G72', t, d, blur=4, dark=0.55)
    g = cairo.LinearGradient(0, 0, W * 0.6, 0); g.add_color_stop_rgba(0, 0.01, 0.04, 0.06, 0.85); g.add_color_stop_rgba(1, 0.01, 0.04, 0.06, 0)
    cr.set_source(g); cr.paint()
    hud(cr, t, 'GREAT LAKES FILES', None)
    mono(cr, 'END OF FILE 03', 140, 360, 30, OR, t=t, start=0.2, bold=True)
    head(cr, 'THANKS FOR', 134, 500, 110, WH, t=t, start=0.4)
    head(cr, 'WATCHING', 134, 620, 110, WH, t=t, start=0.6)
    mono(cr, 'WATCH THE NEXT FILE  →', 140, 740, 34, CY, t=t, start=1.4, bold=True)
    mono(cr, 'AND SUBSCRIBE FOR MORE', 140, 800, 28, WH, t=t, start=2.0, bold=True)
