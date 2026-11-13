"""Every graphic in video 2 (the 1844 Lake Erie seiche), keyed by its G number in video-02/edit-plan.json.

Each is draw(cr, t, d). Selected by render.py when GFX_SET=video2.
"""
import math, os
import numpy as np
import cairo
from style import *
from maps import *
from graphics import fade_all, big_line, quote_card, word_card, mini_map, GREAT_LAKES2, dim_line
from graphics_more import water, ground, label, rounded, caption, bgimg, XS, bump

G = {}


def reg(gid):
    def deco(fn):
        G[gid] = fn; return fn
    return deco


PLACES.update({
    'Toledo': (41.65, -83.54), 'Buffalo': (42.886, -78.878), 'Erie': (42.13, -80.09),
    'Dunkirk': (42.48, -79.33), 'Sturgeon Point': (42.69, -79.05), 'Albany': (42.65, -73.75),
    'New York City': (40.71, -74.01), 'Rochester': (43.16, -77.61), 'Syracuse': (43.05, -76.15),
    'Utica': (43.10, -75.23),
})
ERIE = View(42.25, -81.15, 400)
EAST_END = View(42.70, -79.12, 1700)
CANAL = View(42.15, -76.2, 270)


def _erie_poly():
    best = None
    for a in LAKES:
        x0, x1, y0, y1 = a[:, 0].min(), a[:, 0].max(), a[:, 1].min(), a[:, 1].max()
        if x0 < -81.2 < x1 and y0 < 42.2 < y1:
            area = (x1 - x0) * (y1 - y0)
            if best is None or area < best[0]: best = (area, a)
    return best[1] if best else None


ERIE_POLY = _erie_poly()


# ---------------------------------------------------------------- building blocks
def date_card(cr, t, d, date, place_line, lat, lon, scale, lake):
    background(cr)
    a0 = fade_all(cr, t, d)
    a = ramp(t, 0.15, 0.6) * a0
    font(cr, DISPLAY, 104, bold=True); text(cr, date, 170, 560 + 16 * (1 - a), INK, a)
    a = ramp(t, 0.55, 0.6) * a0
    font(cr, TEXT, 44); text(cr, place_line, 170, 640, MUTED, a)
    mini_map(cr, 1560, 540, scale, lat, lon, t, 0.5, lake[0], lake[1], box=440)


def number_card(cr, t, d, num, line1, line2=None, eyebrow_s=None, color=AMBER):
    background(cr); a0 = fade_all(cr, t, d)
    if eyebrow_s: eyebrow(cr, eyebrow_s, W / 2, 330, AMBER, ramp(t, 0, 0.5) * a0, 'center')
    a = ramp(t, 0.1, 0.6) * a0
    font(cr, DISPLAY, 230, bold=True); text(cr, num, W / 2, 610 + 20 * (1 - a), color, a, 'center')
    a = ramp(t, 0.6, 0.6) * a0
    font(cr, TEXT, 50, bold=True); text(cr, line1, W / 2, 720, INK, a, 'center')
    if line2:
        a = ramp(t, 1.1, 0.6) * a0
        font(cr, TEXT, 38); text(cr, line2, W / 2, 790, MUTED, a, 'center')


def lines_card(cr, t, d, lines, y0=470, gap=100, eyebrow_s=None, step=0.7):
    """lines: (text, size, color, bold)."""
    background(cr); a0 = fade_all(cr, t, d)
    if eyebrow_s: eyebrow(cr, eyebrow_s, W / 2, y0 - 110, AMBER, ramp(t, 0, 0.5) * a0, 'center')
    for i, (s, size, color, bold) in enumerate(lines):
        a = ramp(t, 0.15 + i * step, 0.6) * a0
        font(cr, DISPLAY if bold else TEXT, size, bold=bold)
        text(cr, s, W / 2, y0 + i * gap + 14 * (1 - a), color, a, 'center')


def erie_map(cr, v, t, labels=True, glow=None, glow_a=1.0):
    basemap(cr, v, labels=False)
    if ERIE_POLY is not None:
        cr.save(); cr.set_source_rgba(*COAST, 0.9); cr.set_line_width(2.4)
        p = v.pts(ERIE_POLY); cr.move_to(*p[0])
        for q in p[1:]: cr.line_to(*q)
        cr.close_path(); cr.stroke(); cr.restore()
    if glow:
        x, y = v.xy(*PLACES[glow])
        g = cairo.RadialGradient(x, y, 10, x, y, 260)
        g.add_color_stop_rgba(0, *AMBER, 0.55 * glow_a); g.add_color_stop_rgba(1, *AMBER, 0)
        cr.set_source(g); cr.arc(x, y, 260, 0, 2 * math.pi); cr.fill()
    if labels:
        place(cr, v, 'Toledo', t, 0.2, INK, dx=-16, dy=50, size=32, align='right', bold=True)
        place(cr, v, 'Buffalo', t, 0.4, INK, dx=18, dy=-14, size=32, bold=True)
        font(cr, TEXT, 30, italic=True)
        x, y = v.xy(42.25, -81.3); text(cr, 'LAKE ERIE', x, y, MUTED, 0.7, 'center', tracking=6)


def lake_axis(v):
    a = np.array(v.xy(*PLACES['Toledo'])); b = np.array(v.xy(*PLACES['Buffalo']))
    return a, b


def wind_arrows(cr, v, t, direction=1, alpha=1.0, n=5, spread=150, speed=0.35):
    """Animated arrows along the lake axis. direction 1: southwest wind (toward Buffalo), -1: east wind (toward Toledo)."""
    a, b = lake_axis(v)
    u = (b - a) / np.linalg.norm(b - a); nrm = np.array([-u[1], u[0]])
    L = np.linalg.norm(b - a)
    for k in range(n):
        off = (k - (n - 1) / 2) * spread / (n - 1) * 2 / 2
        ph = ((t * speed + k * 0.23) % 1.0)
        s0 = 0.08 + ph * 0.62
        p0 = a + u * L * s0 + nrm * off
        p1 = p0 + u * L * 0.22
        if direction < 0: p0, p1 = a + u * L * (1 - s0) + nrm * off, a + u * L * (1 - s0 - 0.22) + nrm * off
        fade = math.sin(math.pi * ph)
        arrow(cr, [p0, p1], INK, alpha * 0.85 * fade, 6, 24)


def rotate_arrows(cr, v, t, f, alpha=1.0):
    """Arrows turning from an east wind (pointing west) to a southwest wind (pointing to Buffalo), f from 0 to 1."""
    a, b = lake_axis(v); c = (a + b) / 2
    u = (b - a) / np.linalg.norm(b - a)
    ang0 = math.pi; ang1 = math.atan2(u[1], u[0])
    ang = ang0 + (ang1 - ang0 + (2 * math.pi if ang1 - ang0 < -math.pi else 0)) * ease_in_out(f)
    d = np.array([math.cos(ang), math.sin(ang)])
    for k in range(-2, 3):
        p = c + np.array([k * 210, (k % 2) * 60 - 30])
        arrow(cr, [p - d * 90, p + d * 90], AMBER if f > 0.95 else INK, alpha * 0.9, 7, 26)


# ---------------------------------------------------------------- side view of the lake ("the bathtub")
BX0, BX1, RIM, BED = 230, 1690, 470, 760


def bed_y(x):
    f = np.clip((x - BX0) / (BX1 - BX0), 0, 1)
    return RIM + (BED - RIM) * np.sin(np.pi * f) ** 0.35


def tub(cr, t, tilt, wind=0, wind_a=1.0, labels=True, surge=None):
    """tilt in pixels: positive raises the Buffalo (right) end. surge: (x, height) of a moving bump."""
    background(cr, glow=False)
    xs = np.linspace(BX0, BX1, 300)
    f = (xs - BX0) / (BX1 - BX0)
    ys = 600 - tilt * (2 * f - 1)
    if surge is not None:
        ys = ys - bump(xs, surge[0], surge[1], 120)
    water(cr, xs, ys, BED + 10)
    prof = [(0, RIM), (BX0, RIM)] + [(x, float(bed_y(x))) for x in np.linspace(BX0, BX1, 120)] + [(BX1, RIM), (W, RIM)]
    ground(cr, prof)
    if wind:
        for k in range(4):
            ph = (t * 0.6 + k * 0.25) % 1
            x0 = BX0 + 80 + ph * (BX1 - BX0 - 400)
            if wind < 0: x0 = BX1 - 80 - ph * (BX1 - BX0 - 400)
            y = 300 + (k % 2) * 46
            arrow(cr, [(x0, y), (x0 + 240 * wind, y)], INK, wind_a * 0.8 * math.sin(math.pi * ph), 6, 22)
        font(cr, TEXT, 30, bold=True)
        text(cr, 'WIND', BX0 if wind > 0 else BX1, 250, MUTED, wind_a, 'left' if wind > 0 else 'right', tracking=6)
    if labels:
        label(cr, 'Toledo', BX0 - 10, RIM - 30, 36, INK, 1, 'left')
        label(cr, 'Buffalo', BX1 + 10, RIM - 30, 36, INK, 1, 'right')


def end_note(cr, s, side, t, start, color=AMBER):
    a = ramp(t, start, 0.5)
    x = BX0 + 40 if side == 'left' else BX1 - 40
    font(cr, TEXT, 34, bold=True); text(cr, s, x, 880, color, a, side)


# ---------------------------------------------------------------- section 1
@reg('G01')
def g01(cr, t, d):
    date_card(cr, t, d, 'October 18, 1844', 'Buffalo, New York', PLACES['Buffalo'][0], PLACES['Buffalo'][1], 150, (42.45, -79.7))


@reg('G02')
def g02(cr, t, d):
    v = View(ERIE.lat, ERIE.lon, ERIE.scale * (1 + 0.03 * t / max(d, 1)))
    erie_map(cr, v, t, glow='Buffalo', glow_a=ramp(t, 1.4, 1.0))
    a, b = lake_axis(v)
    arrow(cr, [a + (b - a) * 0.05, a + (b - a) * 0.93], AMBER, 1.0, 10, 40, ramp(t, 0.6, 1.6))
    caption(cr, 'From the southwest, straight down the lake', t, 0.8)


@reg('G03')
def g03(cr, t, d):
    lines_card(cr, t, d, [('2 to 8 feet', 170, AMBER, True), ('of water in the streets', 52, INK, False),
                          ('in less than half an hour', 40, MUTED, False)], y0=540, gap=110)


@reg('G04')
def g04(cr, t, d):
    number_card(cr, t, d, '78', 'people dead')


@reg('G05')
def g05(cr, t, d):
    hold = d * 0.5
    if t < hold:
        tilt = -110 + 4 * math.sin(t * 2.5); wind = -1; wa = 1 - ramp(t, hold - 0.6, 0.6)
    else:
        u = t - hold; tilt = -110 + 250 * ease_out(min(u / 1.6, 1)) - 60 * math.sin(min(u, 6) * 1.2) * math.exp(-u / 3) * min(u / 1.6, 1)
        wind = 0; wa = 0
    tub(cr, t, tilt, wind, wa)
    end_note(cr, 'Held here by the wind', 'left', t, 0.5, MUTED)
    if t > hold: end_note(cr, 'Then let go', 'right', t, hold + 0.3)


# ---------------------------------------------------------------- section 2
@reg('G06')
def g06(cr, t, d):
    f = ramp(t, 0.2, min(2.6, d * 0.6))
    v = View.lerp(GREAT_LAKES2, ERIE, f)
    basemap(cr, v, labels=f < 0.4, highlight=ERIE_POLY if f > 0.5 else None)
    if f > 0.9: erie_map(cr, v, t - (0.2 + min(2.6, d * 0.6)), labels=True)


@reg('G07')
def g07(cr, t, d):
    v = ERIE; erie_map(cr, v, t)
    a, b = lake_axis(v)
    al = ramp(t, 0.9, 0.7)
    if al > 0:
        u = (b - a) / np.linalg.norm(b - a); nrm = np.array([-u[1], u[0]])
        p0, p1 = a + nrm * 120, b + nrm * 120
        cr.set_source_rgba(*AMBER, al); cr.set_line_width(3); cr.move_to(*p0); cr.line_to(*p1); cr.stroke()
        for p in (p0, p1):
            cr.move_to(*(p - u * 0 + nrm * 16)); cr.line_to(*(p - nrm * 16)); cr.stroke()
        mx, my = (p0 + p1) / 2
        cr.save(); cr.translate(mx, my); cr.rotate(math.atan2(u[1], u[0]))
        font(cr, DISPLAY, 46, bold=True); text(cr, 'about 240 miles', 0, 70, INK, al, 'center'); cr.restore()
    a2 = ramp(t, 1.8, 0.6)
    font(cr, TEXT, 30, bold=True)
    x, y = a; text(cr, 'SOUTHWEST', x - 20, y + 110, MUTED, a2, 'right', tracking=5)
    x, y = b; text(cr, 'NORTHEAST', x + 20, y - 70, MUTED, a2, 'left', tracking=5)


@reg('G08')
def g08(cr, t, d):
    background(cr); a0 = fade_all(cr, t, d)
    lakes = [('Superior', 483), ('Michigan', 279), ('Huron', 195), ('Erie', 62), ('Ontario', 283)]
    top, scale, bw, gap = 300, 1.15, 200, 90
    x0 = (W - (len(lakes) * bw + (len(lakes) - 1) * gap)) / 2
    a = ramp(t, 0, 0.5) * a0
    eyebrow(cr, 'Average depth', W / 2, 190, AMBER, a, 'center')
    cr.set_source_rgba(*COAST, a); cr.set_line_width(3); cr.move_to(x0 - 40, top); cr.line_to(W - x0 + 40, top); cr.stroke()
    for i, (name, dep) in enumerate(lakes):
        p = ramp(t, 0.3 + i * 0.25, 1.0)
        x = x0 + i * (bw + gap); h = dep * scale * p
        col = AMBER if name == 'Erie' else WATER_HI
        cr.set_source_rgba(*col, a0); cr.rectangle(x, top, bw, h); cr.fill()
        font(cr, TEXT, 34, bold=True); text(cr, name, x + bw / 2, top - 30, INK if name == 'Erie' else MUTED, a0, 'center')
        font(cr, DISPLAY, 40, bold=True); text(cr, '%d ft' % dep, x + bw / 2, top + h + 54, AMBER if name == 'Erie' else INK, a0 * p, 'center')


@reg('G09')
def g09(cr, t, d):
    erie_map(cr, ERIE, t, glow='Buffalo', glow_a=ramp(t, 1.0, 1.0))
    wind_arrows(cr, ERIE, t, 1, ramp(t, 0.2, 0.6))
    caption(cr, 'Strong winds from the southwest', t, 0.6)


@reg('G10')
def g10(cr, t, d):
    quote_card(cr, t, d, ['a giant bathtub'], 'National Weather Service', 'Describing Lake Erie', size=110)


@reg('G11')
def g11(cr, t, d):
    tilt = 130 * ease_in_out(min(t / max(d * 0.7, 0.1), 1))
    tub(cr, t, tilt, 1, 1.0)
    end_note(cr, 'Water drops', 'left', t, d * 0.35, MUTED)
    end_note(cr, 'Water piles up', 'right', t, d * 0.35)


@reg('G12')
def g12(cr, t, d):
    background(cr); a0 = fade_all(cr, t, d)
    base = 700; xs = (620, 1300); lv = (-90, 210)
    p = ramp(t, 0.4, 1.4)
    for (x, h, name) in ((xs[0], lv[0], 'Toledo'), (xs[1], lv[1], 'Buffalo')):
        cr.set_source_rgba(*MUTED, 0.6 * a0); cr.set_line_width(3); cr.move_to(x, 260); cr.line_to(x, 900); cr.stroke()
        y = base - h * p
        cr.set_source_rgba(*WATER_HI, a0); cr.rectangle(x - 110, y, 220, 900 - y); cr.fill()
        cr.set_source_rgba(*INK, a0); cr.set_line_width(4); cr.move_to(x - 110, y); cr.line_to(x + 110, y); cr.stroke()
        label(cr, name, x, 960, 40, INK, a0)
    cr.set_source_rgba(*MUTED, 0.5 * a0); cr.set_dash([10, 8]); cr.set_line_width(2)
    cr.move_to(500, base); cr.line_to(1420, base); cr.stroke(); cr.set_dash([])
    a = ramp(t, 1.8, 0.6) * a0
    if a > 0:
        y1, y2 = base - lv[1], base - lv[0]
        dim_line(cr, (1500, y1), (1500, y2), '', a, vertical=True)
        font(cr, DISPLAY, 56, bold=True); text(cr, 'more than', 1540, (y1 + y2) / 2 - 20, INK, a)
        text(cr, '10 feet', 1540, (y1 + y2) / 2 + 50, AMBER, a)
    eyebrow(cr, 'In an extreme case', W / 2, 170, AMBER, ramp(t, 0, 0.5) * a0, 'center')


@reg('G13')
def g13(cr, t, d):
    erie_map(cr, ERIE, t, glow='Toledo', glow_a=ramp(t, 1.0, 1.0))
    wind_arrows(cr, ERIE, t, -1, ramp(t, 0.2, 0.6))
    caption(cr, 'East wind: the water piles up at Toledo', t, 0.6)


@reg('G14')
def g14(cr, t, d):
    word_card(cr, t, d, 'seiche', 'say it “saysh”', 'S · E · I · C · H · E')


# ---------------------------------------------------------------- section 3
@reg('G15')
def g15(cr, t, d):
    v = CANAL; basemap(cr, v, labels=False)
    font(cr, TEXT, 30, italic=True); x, y = v.xy(43.65, -77.9); text(cr, 'LAKE ONTARIO', x, y, MUTED, 0.7, 'center', tracking=6)
    route = [PLACES[n] for n in ('Buffalo',)] + [(43.17, -78.69), PLACES['Rochester'], PLACES['Syracuse'], (43.21, -75.46),
                                                PLACES['Utica'], (42.81, -73.94), PLACES['Albany']]
    pts = [v.xy(*p) for p in route]
    arrow(cr, pts, AMBER, 1, 8, 30, ramp(t, 0.5, 1.8))
    hud = [v.xy(*PLACES['Albany']), v.xy(41.70, -73.95), v.xy(*PLACES['New York City'])]
    p2 = ramp(t, 2.3, 1.0)
    if p2 > 0:
        cr.set_dash([12, 9]); arrow(cr, hud, INK, 0.8, 5, 22, p2); cr.set_dash([])
    place(cr, v, 'Buffalo', t, 0.2, INK, dx=-16, dy=50, size=34, align='right', bold=True)
    place(cr, v, 'Albany', t, 2.0, INK, dx=18, dy=-10, size=32)
    place(cr, v, 'New York City', t, 3.0, INK, dx=18, dy=10, size=32)
    a = ramp(t, 1.2, 0.6)
    eyebrow(cr, 'The Erie Canal', 120, H - 210, AMBER, a)
    font(cr, DISPLAY, 70, bold=True); text(cr, 'Opened in 1825', 120, H - 125, INK, a)


# ---------------------------------------------------------------- section 4
@reg('G16')
def g16(cr, t, d):
    erie_map(cr, ERIE, t, glow='Toledo', glow_a=ramp(t, 1.2, 1.2))
    wind_arrows(cr, ERIE, t, -1, ramp(t, 0.2, 0.6))
    caption(cr, 'For several days: a stiff wind from the east', t, 0.6)


@reg('G17')
def g17(cr, t, d):
    quote_card(cr, t, d, ['had driven the water', 'up the lake'], 'Buffalo newspapers', 'October 1844', size=92)


@reg('G18')
def g18(cr, t, d):
    tub(cr, t, -115 + 5 * math.sin(t * 2.2), -1, 1.0)
    end_note(cr, 'Higher at Toledo', 'left', t, 0.6)
    end_note(cr, 'Lower at Buffalo', 'right', t, 1.0, MUTED)


@reg('G19')
def g19(cr, t, d):
    background(cr); a0 = fade_all(cr, t, d)
    eyebrow(cr, 'Left Buffalo on Friday evening', 200, 300, AMBER, ramp(t, 0, 0.5) * a0)
    names = [('St. Louis', ''), ('Robert Fulton', ''), ('Indian Queen', ''), ('Julia Palmer', 'about 400 passengers')]
    for i, (n_, s_) in enumerate(names):
        a = ramp(t, 0.4 + i * 0.55, 0.5) * a0
        font(cr, DISPLAY, 76, bold=True); text(cr, n_, 200, 420 + i * 120, AMBER if s_ else INK, a)
        if s_:
            w = text_width(cr, n_); font(cr, TEXT, 38); text(cr, s_, 200 + w + 30, 420 + i * 120, MUTED, a)


# ---------------------------------------------------------------- section 5
@reg('G20')
def g20(cr, t, d):
    f = ramp(t, 0.8, min(2.0, d * 0.5))
    erie_map(cr, ERIE, t, glow='Buffalo', glow_a=ramp(t, 0.8 + min(2.0, d * 0.5), 1.0))
    rotate_arrows(cr, ERIE, t, f)
    caption(cr, 'About midnight: the wind swings to the southwest', t, 0.4)


@reg('G21')
def g21(cr, t, d):
    quote_card(cr, t, d, ['with a tremendous force', 'never before or since known', 'to the inhabitants of Buffalo'],
               'A later history of Buffalo', 'On the night of October 18, 1844', size=70)


@reg('G22')
def g22(cr, t, d):
    u = ramp(t, 0.6, d * 0.75)
    tilt = -115 + 265 * ease_in_out(u)
    sx = BX0 + 150 + (BX1 - BX0 - 260) * ease_in_out(u)
    tub(cr, t, tilt, 1 if t > 0.5 else 0, ramp(t, 0.5, 0.4), surge=(sx, 70 * math.sin(math.pi * min(u * 1.1, 1))))
    end_note(cr, 'Let go', 'left', t, 0.6, MUTED)
    end_note(cr, 'Toward Buffalo', 'right', t, d * 0.5)


@reg('G23')
def g23(cr, t, d):
    quote_card(cr, t, d, ['as if a dam had', 'broken away'], 'Buffalo newspapers', 'October 1844', size=100)


@reg('G24')
def g24(cr, t, d):
    number_card(cr, t, d, '22 feet', 'above where the lake stood that evening', eyebrow_s="By the newspaper's measure")


@reg('G25')
def g25(cr, t, d):
    quote_card(cr, t, d, ['the whole lower part of the city', 'south of the canal … was submerged', 'from two to eight feet in depth'],
               'Buffalo newspapers', 'October 1844', size=64)


# ---------------------------------------------------------------- section 6
@reg('G26')
def g26(cr, t, d):
    quote_card(cr, t, d, ['an avalanche of waters', 'upon a sleeping community'], 'A later history of Buffalo', 'On the flood of 1844', size=84)


@reg('G27')
def g27(cr, t, d):
    background(cr); a0 = fade_all(cr, t, d)
    rows = [('6 ft', 'Main and Ohio Streets'), ('6 ft', "Huff's Hotel, Main and Scott")]
    eyebrow(cr, 'How deep it was', 360, 370, AMBER, ramp(t, 0, 0.5) * a0)
    for i, (n_, s_) in enumerate(rows):
        a = ramp(t, 0.4 + i * 0.8, 0.6) * a0
        font(cr, DISPLAY, 130, bold=True); text(cr, n_, 360, 530 + i * 190, AMBER, a)
        font(cr, TEXT, 52, bold=True); text(cr, s_, 700, 515 + i * 190, INK, a)


@reg('G28')
def g28(cr, t, d):
    quote_card(cr, t, d, ['the most fearful midnight voyaging', 'that ever a man, wife and child', 'underwent'],
               'An account of the 1844 flood', 'Two families adrift on a split roof', size=66)


# ---------------------------------------------------------------- section 7
@reg('G29')
def g29(cr, t, d):
    v = EAST_END; basemap(cr, v, labels=False)
    font(cr, TEXT, 30, italic=True); x, y = v.xy(42.62, -79.45); text(cr, 'LAKE ERIE', x, y, MUTED, 0.7, 'center', tracking=6)
    place(cr, v, 'Buffalo', t, 0.2, INK, dx=0, dy=-26, size=36, align='center', bold=True)
    marks = [('Dunkirk', 'St. Louis: broke her shaft, 4 lost', 0.8, 'right'),
             ('Sturgeon Point', 'Robert Fulton: wrecked on the beach', 1.8, 'left'),
             ((42.865, -78.92), 'Julia Palmer: anchored off Main Street', 2.8, 'right')]
    for name, note, st, side in marks:
        a = ramp(t, st, 0.5)
        if a <= 0: continue
        ll = PLACES[name] if isinstance(name, str) else name
        x, y = v.xy(*ll)
        pulse(cr, x, y, t, AMBER, 9, alpha=a)
        if isinstance(name, str):
            font(cr, TEXT, 30); text(cr, name, x + (18 if side == 'left' else -18), y + 44, MUTED, a, side)
        font(cr, TEXT, 34, bold=True)
        dy = 50 if not isinstance(name, str) else 6
        text(cr, note, x + (24 if side == 'left' else -24), y + dy, INK, a, side)


@reg('G30')
def g30(cr, t, d):
    quote_card(cr, t, d, ['now burning the furniture'], 'A letter tied to a horse’s mane', 'From the steamboat Julia Palmer', size=96)


# ---------------------------------------------------------------- section 8
@reg('G31')
def g31(cr, t, d):
    background(cr); a0 = fade_all(cr, t, d)
    for i, (n_, s_) in enumerate((('80+', 'canal boats driven ashore'), ('200+', 'small buildings destroyed'))):
        a = ramp(t, 0.2 + i * 0.9, 0.6) * a0
        x = W / 2 + (i - 0.5) * 760
        font(cr, DISPLAY, 190, bold=True); text(cr, n_, x, 560, AMBER, a, 'center')
        font(cr, TEXT, 46, bold=True); text(cr, s_, x, 660, INK, a, 'center')


@reg('G32')
def g32(cr, t, d):
    number_card(cr, t, d, '39', 'dead in the first count', '“besides several who are missing”', eyebrow_s='The newspapers, October 1844')


@reg('G33')
def g33(cr, t, d):
    background(cr); a0 = fade_all(cr, t, d)
    eyebrow(cr, 'Later records', W / 2, 330, AMBER, ramp(t, 0, 0.5) * a0, 'center')
    for i, (n_, s_) in enumerate((('53', 'in Buffalo'), ('25', 'on the lake'))):
        a = ramp(t, 0.3 + i * 0.9, 0.6) * a0
        x = W / 2 + (i - 0.5) * 700
        font(cr, DISPLAY, 210, bold=True); text(cr, n_, x, 600, INK, a, 'center')
        font(cr, TEXT, 48, bold=True); text(cr, s_, x, 700, MUTED, a, 'center')
    a = ramp(t, 1.0, 0.5) * a0
    font(cr, DISPLAY, 140, bold=True); text(cr, '+', W / 2, 580, AMBER, a, 'center')


@reg('G34')
def g34(cr, t, d):
    number_card(cr, t, d, '78', 'in all')


@reg('G35')
def g35(cr, t, d):
    quote_card(cr, t, d, ['the most destructive documented', 'seiche in Western New York'], 'New York Sea Grant', 'On the Buffalo flood of October 1844', size=72)


# ---------------------------------------------------------------- section 9
def compare_card(cr, t, d, place_s, struck, word, line, word_color):
    background(cr); a0 = fade_all(cr, t, d)
    eyebrow(cr, place_s, W / 2, 360, AMBER, ramp(t, 0, 0.5) * a0, 'center')
    y = 540
    if struck:
        a = ramp(t, 0.2, 0.5) * a0
        font(cr, DISPLAY, 110, bold=True); w = text_width(cr, struck)
        text(cr, struck, W / 2, y, MUTED, a, 'center')
        p = ramp(t, 0.9, 0.5)
        cr.set_source_rgba(*RED, a0); cr.set_line_width(9); cr.move_to(W / 2 - w / 2 - 10, y - 38); cr.line_to(W / 2 - w / 2 - 10 + (w + 20) * p, y - 38); cr.stroke()
        y += 150
    a = ramp(t, 1.3 if struck else 0.2, 0.6) * a0
    font(cr, DISPLAY, 120, bold=True); text(cr, word, W / 2, y, word_color, a, 'center')
    a = ramp(t, 1.9 if struck else 0.8, 0.6) * a0
    font(cr, TEXT, 46); text(cr, line, W / 2, y + 90, INK, a, 'center')


@reg('G36')
def g36(cr, t, d):
    compare_card(cr, t, d, 'Chicago, 1954', 'seiche', 'meteotsunami', 'One fast wave, over in minutes', INK)


@reg('G37')
def g37(cr, t, d):
    compare_card(cr, t, d, 'Buffalo, 1844', None, 'seiche', 'The real thing: the whole lake rocking', AMBER)


@reg('G38')
def g38(cr, t, d):
    tub(cr, t, 125 * math.cos(2 * math.pi * t / 4.5))
    a = ramp(t, 0.3, 0.5)
    label(cr, 'The whole lake rocks, end to end', W / 2, 180, 46, INK, a)


@reg('G39')
def g39(cr, t, d):
    ph = min(t / max(d - 0.5, 1), 1)
    tub(cr, t, 125 * math.cos(2 * math.pi * ph))
    cx, cy, r = 1650, 200, 90
    a = ramp(t, 0.2, 0.5)
    circle(cr, cx, cy, r, MUTED, 0.5 * a, fill=False, width=4)
    cr.set_source_rgba(*AMBER, a); cr.set_line_width(14)
    cr.arc(cx, cy, r - 16, -math.pi / 2, -math.pi / 2 + 2 * math.pi * max(ph, 0.001)); cr.stroke()
    font(cr, DISPLAY, 46, bold=True); text(cr, '%d h' % round(14 * ph), cx, cy + 16, INK, a, 'center')
    label(cr, 'One full rock: about 14 hours', 200, 200, 46, INK, a, 'left')


@reg('G40')
def g40(cr, t, d):
    tub(cr, t, -125 + 6 * math.sin(t * 1.8))
    end_note(cr, 'Piled up at one end', 'left', t, 0.4)
    a = ramp(t, 1.2, 0.6)
    arrow(cr, [(760, 420), (1300, 420)], AMBER, a * (0.6 + 0.4 * math.sin(t * 3)), 6, 26, ramp(t, 1.2, 1.0))
    end_note(cr, 'waiting to come back', 'right', t, 1.4, MUTED)


# ---------------------------------------------------------------- section 10
@reg('G41')
def g41(cr, t, d):
    lines_card(cr, t, d, [('No known pictures of that night', 76, INK, True), ('Not a photograph. Not even a drawing.', 46, MUTED, False),
                          ('Only newspaper columns.', 46, AMBER, False)], y0=480, gap=110, step=0.9)


@reg('G42')
def g42(cr, t, d):
    number_card(cr, t, d, '2 to 3', 'seiches a year at Buffalo', 'The breakwater takes most of their force')


@reg('G43')
def g43(cr, t, d):
    background(cr); fade_all(cr, t, d)
    big_line(cr, 'The city changed.', 500, t, 0.0, size=110)
    big_line(cr, 'The lake did not.', 650, t, 0.9, size=110, color=AMBER)


# ---------------------------------------------------------------- section 11
@reg('G44')
def g44(cr, t, d):
    date_card(cr, t, d, 'November 15, 2020', 'A storm warning for all of Lake Erie', PLACES['Buffalo'][0], PLACES['Buffalo'][1], 110, (42.25, -81.15))


@reg('G45')
def g45(cr, t, d):
    background(cr); a0 = fade_all(cr, t, d)
    base = 640; k = 3.0  # pixels per inch
    p = ramp(t, 0.4, 1.4)
    eyebrow(cr, 'Water level, November 15, 2020', W / 2, 150, AMBER, ramp(t, 0, 0.5) * a0, 'center')
    cr.set_source_rgba(*MUTED, 0.6 * a0); cr.set_dash([10, 8]); cr.set_line_width(2)
    cr.move_to(380, base); cr.line_to(1540, base); cr.stroke(); cr.set_dash([])
    font(cr, TEXT, 26); text(cr, 'chart level', 380, base - 14, MUTED, a0)
    for x, inches, name, sub in ((700, -34.5, 'Toledo', 'about 3 feet below'), (1220, 133.5, 'Buffalo', 'about 11 feet above')):
        h = inches * k * p
        col = AMBER if inches > 0 else WATER_HI
        cr.set_source_rgba(*col, a0); cr.rectangle(x - 120, base - max(h, 0), 240, abs(h)); cr.fill()
        label(cr, name, x, base + (60 if inches > 0 else -h + 70), 42, INK, a0)
        font(cr, TEXT, 32); text(cr, sub, x, base + (110 if inches > 0 else -h + 120), MUTED, a0 * ramp(t, 1.6, 0.5), 'center')
    a = ramp(t, 2.2, 0.6) * a0
    if a > 0:
        y1, y2 = base - 133.5 * k, base + 34.5 * k
        dim_line(cr, (1440, y1), (1440, y2), '', a, vertical=True)
        font(cr, DISPLAY, 70, bold=True); text(cr, '14 feet', 1480, (y1 + y2) / 2 + 24, AMBER, a)
    font(cr, TEXT, 26); text(cr, 'Source: National Weather Service, Cleveland', W / 2, 1010, MUTED, a0 * 0.8, 'center')


@reg('G46')
def g46(cr, t, d):
    tub(cr, t, 135 * ease_in_out(min(t / max(d * 0.6, 0.1), 1)), 1, 1.0)
    end_note(cr, 'November 15, 2020', 'left', t, 0.4, MUTED)


@reg('G47')
def g47(cr, t, d):
    date_card(cr, t, d, 'December 29, 2025', 'Gusts of 60 to 80 mph set off a seiche', PLACES['Buffalo'][0], PLACES['Buffalo'][1], 110, (42.25, -81.15))


@reg('G48')
def g48(cr, t, d):
    erie_map(cr, ERIE, t, glow='Buffalo', glow_a=ramp(t, 1.0, 1.0))
    wind_arrows(cr, ERIE, t, 1, ramp(t, 0.2, 0.6))
    caption(cr, 'A strong seiche like this comes every few years', t, 0.6)


# ---------------------------------------------------------------- section 12
@reg('G49')
def g49(cr, t, d):
    background(cr); a0 = fade_all(cr, t, d)
    big_line(cr, 'Two dangerous moments', 400, t, 0.0, size=96)
    for i, s_ in enumerate(('The water arriving', 'The lake pulling back')):
        a = ramp(t, 0.9 + i * 0.9, 0.6) * a0
        font(cr, DISPLAY, 70, bold=True); text(cr, str(i + 1), 620, 580 + i * 130, AMBER, a)
        font(cr, TEXT, 60, bold=True); text(cr, s_, 720, 580 + i * 130, INK, a)


@reg('G50')
def g50(cr, t, d):
    background(cr); a0 = fade_all(cr, t, d)
    eyebrow(cr, 'If you live by a lake', 220, 360, AMBER, ramp(t, 0, 0.5) * a0)
    rows = ["If the lake pulls back after a storm,", "don't walk out after it.", "", "If there's a lakeshore flood warning,", "believe it."]
    for i, s_ in enumerate(rows):
        if not s_: continue
        a = ramp(t, 0.3 + (0 if i < 2 else 1.2), 0.6) * a0
        font(cr, DISPLAY if i in (1, 4) else TEXT, 66 if i in (1, 4) else 52, bold=i in (1, 4))
        text(cr, s_, 220, 470 + i * 88, AMBER if i in (1, 4) else INK, a)


@reg('G51')
def g51(cr, t, d):
    background(cr); fade_all(cr, t, d)
    big_line(cr, 'Nothing told them', 500, t, 0.0, size=100)
    big_line(cr, 'it was only waiting.', 640, t, 0.9, size=100, color=AMBER)


END_BG = None
_bg = os.path.join(os.path.dirname(__file__), '../../video-02/images/061.jpg')
if os.path.exists(_bg):
    from PIL import Image as _I
    END_BG = '/tmp/v2-end-bg-061.png'
    if not os.path.exists(END_BG): _I.open(_bg).convert('RGB').resize((1920, 1080)).save(END_BG)


@reg('G52')
def g52(cr, t, d):
    bgimg(cr, END_BG, 0.35)
    a = ramp(t, 0.3, 0.6)
    eyebrow(cr, 'Great Lakes Files', 140, 430, AMBER, a)
    font(cr, DISPLAY, 92, bold=True); text(cr, 'Subscribe to open', 140, 540, INK, a); text(cr, 'the next file', 140, 640, INK, a)
    font(cr, TEXT, 40); text(cr, 'True stories from the Great Lakes', 140, 720, MUTED, a)


import palettes  # noqa: E402
palettes.apply('storm')
