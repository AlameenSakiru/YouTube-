"""Graphics G08 to G51. Registered into graphics.G."""
import math
import numpy as np
import cairo
from style import *
from maps import *
from graphics import G, reg, fade_all, big_line, quote_card, word_card, date_card, mini_map, shore_pair, GREAT_LAKES2, POINTS_106

# ---------------------------------------------------------------- storm and wave maps
REGION = View(42.95, -89.0, 255)
STORM_VIEW = View(41.95, -87.25, 900)
CHI = PLACES['Chicago']; MC = PLACES['Michigan City']
SE = np.array([0.6, -0.8])  # direction of travel in (dlon, dlat) per unit, roughly south-east


def front(cr, v, center, t, length_deg=3.0, color=STORM, alpha=1.0, label=None):
    """A storm front: a thick band at right angles to its south-east travel, with rain behind it."""
    la, lo = center
    d = np.array([0.8, 0.6])  # along-front direction (dlon, dlat), north-east
    pts = [v.xy(la + s * d[1], lo + s * d[0]) for s in np.linspace(-length_deg / 2, length_deg / 2, 30)]
    # rain streaks trailing behind (north-west)
    rng = np.random.default_rng(int(t * 10) % 7)
    cr.set_line_width(2)
    for k in range(0, 30, 2):
        x, y = pts[k]
        for j in range(3):
            off = rng.uniform(10, 90)
            cr.set_source_rgba(*color, 0.25 * alpha)
            cr.move_to(x - off * 0.6, y - off * 0.8); cr.line_to(x - off * 0.6 - 10, y - off * 0.8 + 18); cr.stroke()
    cr.set_line_cap(cairo.LINE_CAP_ROUND)
    for w_, a_ in ((80, 0.08), (40, 0.18), (16, 0.5), (5, 1.0)):
        cr.set_source_rgba(*color, a_ * alpha); cr.set_line_width(w_)
        cr.move_to(*pts[0])
        for p in pts[1:]: cr.line_to(*p)
        cr.stroke()
    if label:
        x, y = pts[-1]
        font(cr, TEXT, 28, bold=True); text(cr, label, x + 16, y - 10, color, alpha)


def wave_front(cr, v, center, height=1.0, alpha=1.0, length_deg=0.55):
    la, lo = center
    d = np.array([0.8, 0.6])
    pts = [v.xy(la + s * d[1], lo + s * d[0]) for s in np.linspace(-length_deg / 2, length_deg / 2, 30)]
    cr.set_line_cap(cairo.LINE_CAP_ROUND)
    for w_, a_ in ((10 + 22 * height, 0.22), (4 + 8 * height, 0.95)):
        cr.set_source_rgba(*AMBER, a_ * alpha); cr.set_line_width(w_)
        cr.move_to(*pts[0])
        for p in pts[1:]: cr.line_to(*p)
        cr.stroke()


def clock(cr, s, t, start=0.0, sub='Saturday, June 26, 1954'):
    a = ramp(t, start, 0.4)
    cr.set_source_rgba(*BG, 0.75 * a); rounded(cr, 80, 70, 470, 170, 16); cr.fill()
    font(cr, DISPLAY, 92, bold=True); text(cr, s, 115, 175, INK, a)
    font(cr, TEXT, 26); text(cr, sub, 118, 218, MUTED, a)


def rounded(cr, x, y, w, h, r):
    cr.new_sub_path()
    cr.arc(x + w - r, y + r, r, -math.pi / 2, 0); cr.arc(x + w - r, y + h - r, r, 0, math.pi / 2)
    cr.arc(x + r, y + h - r, r, math.pi / 2, math.pi); cr.arc(x + r, y + r, r, math.pi, 1.5 * math.pi)
    cr.close_path()


def caption(cr, s, t, start=0.3, y=H - 110):
    a = ramp(t, start, 0.5)
    font(cr, TEXT, 40, bold=True)
    w = text_width(cr, s)
    cr.set_source_rgba(*BG, 0.78 * a); rounded(cr, W / 2 - w / 2 - 36, y - 52, w + 72, 76, 14); cr.fill()
    text(cr, s, W / 2, y, INK, a, 'center')


def lerp_ll(a, b, f):
    return (a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f)


@reg('G08')
def g08(cr, t, d):
    v = REGION; basemap(cr, v)
    start, end = (44.55, -91.0), (42.2, -87.95)
    f = ramp(t, 0.3, d - 0.6) if True else 0
    f = min(max((t - 0.3) / (d - 0.8), 0), 1)
    c = lerp_ll(start, end, f)
    for k, (p, at) in enumerate([('La Crosse', 0.0), ('Madison', 0.35), ('Rockford', 0.55), ('Milwaukee', 0.55), ('Chicago', 0.98)]):
        place(cr, v, p, t, 0.2 + at * (d - 0.8), INK if at < 0.98 else AMBER, 7, size=30)
    front(cr, v, c, t, 4.2)
    caption(cr, 'A line of storms heading south-east', t, 0.4)


@reg('G09')
def g09(cr, t, d):
    v = STORM_VIEW; basemap(cr, v)
    place(cr, v, 'Chicago', 99, 0, INK, 8, size=32, align='right')
    place(cr, v, 'Michigan City', 99, 0, INK, 8, size=32)
    f = min(max(t / d, 0), 1)
    c = lerp_ll((42.15, -87.85), (41.95, -87.45), f)
    front(cr, v, c, t, 1.2)
    clock(cr, '7:30 a.m.', t, 0.0)
    caption(cr, 'Close to 60 miles an hour', t, 0.8)


@reg('G24')
def g24(cr, t, d):
    v = STORM_VIEW; basemap(cr, v)
    place(cr, v, 'Chicago', 99, 0, INK, 8, size=32, align='right')
    place(cr, v, 'Michigan City', 99, 0, INK, 8, size=32)
    f = min(max(t / d, 0), 1)
    c = lerp_ll((42.05, -87.65), (41.85, -87.2), f)
    front(cr, v, c, t, 1.2, label='Pressure jump')
    caption(cr, 'Crossing the lake at about 60 mph', t, 0.5)


def storm_wave(cr, t, d, f0, f1, clock_s, cap, bounce=False, wave_h=(0.4, 1.0)):
    v = STORM_VIEW; basemap(cr, v)
    place(cr, v, 'Chicago', 99, 0, INK, 8, size=32, align='right')
    place(cr, v, 'Michigan City', 99, 0, INK, 8, size=32)
    f = f0 + (f1 - f0) * min(max(t / d, 0), 1)
    a_start, a_end = (41.98, -87.55), (41.78, -86.98)
    c = lerp_ll(a_start, a_end, f)
    if not bounce:
        front(cr, v, (c[0] - 0.035, c[1] + 0.03), t, 1.2, alpha=1.0)
        wave_front(cr, v, c, wave_h[0] + (wave_h[1] - wave_h[0]) * f)
    else:
        g = min(max(t / d, 0), 1)
        sc = lerp_ll(a_end, (41.55, -86.55), g)
        front(cr, v, sc, t, 1.2, alpha=1 - g)
        c = lerp_ll(a_end, lerp_ll(a_end, a_start, 0.35), g)
        wave_front(cr, v, c, 0.8)
        if g > 0.05:
            arrow(cr, [v.xy(*c), v.xy(*lerp_ll(c, a_start, 0.3))], AMBER, 0.95, 8, 28)
    clock(cr, clock_s, t)
    caption(cr, cap, t, 0.5)


@reg('G32')
def g32(cr, t, d):
    storm_wave(cr, t, d, 0.0, 0.45, '7:30 a.m.', 'The wave forms under the storm, heading away from Chicago')


@reg('G33')
def g33(cr, t, d):
    storm_wave(cr, t, d, 0.6, 1.0, '8:10 a.m.', 'Michigan City: a five-foot wall of water')
    if t > d * 0.7:
        x, y = STORM_VIEW.xy(*MC); pulse(cr, x, y, t, AMBER, 12)


@reg('G34')
def g34(cr, t, d):
    storm_wave(cr, t, d, 1.0, 1.0, '8:10 a.m.', 'It hits the shore, and bounces back', bounce=True)


@reg('G35')
def g35(cr, t, d):
    v = STORM_VIEW; basemap(cr, v)
    place(cr, v, 'Chicago', 99, 0, AMBER, 8, size=32, align='right')
    place(cr, v, 'Michigan City', 99, 0, INK, 8, size=32)
    f = min(max(t / (d * 0.8), 0), 1)
    a_start, a_end = (41.98, -87.55), (41.78, -86.98)
    c = lerp_ll(lerp_ll(a_end, a_start, 0.6), a_start, f)
    wave_front(cr, v, c, 0.9)
    x, y = v.xy(*CHI)
    if f > 0.9: pulse(cr, x, y, t, AMBER, 12)
    clock(cr, '9:30 a.m.', t)
    caption(cr, 'It reaches Chicago under a clear sky', t, 0.3)


@reg('G36')
def g36(cr, t, d):
    v = STORM_VIEW; basemap(cr, v)
    place(cr, v, 'Chicago', 99, 0, INK, 8, size=32, align='right')
    place(cr, v, 'Michigan City', 99, 0, INK, 8, size=32)
    p_out = [v.xy(41.93, -87.56), v.xy(41.80, -87.02)]
    p_back = [v.xy(41.74, -86.98), v.xy(41.87, -87.52)]
    arrow(cr, [(x, y - 28) for x, y in p_out], STORM, 1.0, 6, 22, ramp(t, 0.2, 1.6))
    arrow(cr, [(x, y + 28) for x, y in p_back], AMBER, 1.0, 7, 24, ramp(t, 2.0, 1.8))
    a = ramp(t, 0.4, 0.5); font(cr, TEXT, 30, bold=True)
    x, y = v.xy(41.90, -87.30); text(cr, 'Storm out, 7:30 to 8:10', x, y - 70, STORM, a, 'center')
    a = ramp(t, 2.3, 0.5)
    x, y = v.xy(41.78, -87.28); text(cr, 'Wave back, 8:10 to 9:30', x, y + 105, AMBER, a, 'center')


# ---------------------------------------------------------------- Chicago shoreline maps
def shore_view(lat, scale=3600):
    return View(lat, -87.70, scale)


def beach_mark(cr, v, name, t, start=0.0, color=AMBER, size=34, label=None, side='right'):
    la = PLACES[name][0]; lo = shore_lon(la) + 0.004
    x, y = v.xy(la, lo); a = ramp(t, start, 0.5)
    if a <= 0: return
    pulse(cr, x, y, t, color, 10, alpha=a)
    font(cr, TEXT, size, bold=True)
    text(cr, label or name, x + 28 if side == 'right' else x - 28, y + 12, INK, a, 'left' if side == 'right' else 'right')


def city_label(cr, v, t):
    font(cr, TEXT, 30, italic=True)
    x, y = v.xy(41.90, -87.78); text(cr, 'CHICAGO', x, y, MUTED, 0.7, 'center', tracking=6)
    x, y = v.xy(41.98, -87.50); text(cr, 'LAKE MICHIGAN', x, y, MUTED, 0.7, 'center', tracking=6)


@reg('G10')
def g10(cr, t, d):
    v = shore_view(41.93); basemap(cr, v, labels=False, borders=False); city_label(cr, v, t)
    beach_mark(cr, v, 'North Avenue Beach', t, 0.3)


@reg('G13')
def g13(cr, t, d):
    v = View.lerp(shore_view(41.915), shore_view(41.963), ramp(t, 0.0, d * 0.85))
    basemap(cr, v, labels=False, borders=False); city_label(cr, v, t)
    beach_mark(cr, v, 'North Avenue Beach', t, 0.0, MUTED, 30)
    beach_mark(cr, v, 'Montrose Harbor', t, d * 0.6)


@reg('G17')
def g17(cr, t, d):
    v = View(41.985, -87.70, 3300); basemap(cr, v, labels=False, borders=False); city_label(cr, v, t)
    seg = shore_segment(41.889, 42.08, 80)
    pts = [v.xy(la, lo + 0.002) for la, lo in seg]
    arrow_free(cr, pts, ramp(t, 0.3, d * 0.6))
    for nm, st in (('Chicago River', 0.2), ('Wilmette', d * 0.6)):
        la = PLACES[nm][0]; x, y = v.xy(la, shore_lon(la) + 0.004)
        a = ramp(t, st, 0.5); circle(cr, x, y, 9, INK, a)
        font(cr, TEXT, 32, bold=True); text(cr, nm, x + 26, y + 12, INK, a)


def arrow_free(cr, pts, progress):
    """A glowing line along the shore drawn up to progress."""
    n = max(2, int(len(pts) * progress))
    cr.set_line_cap(cairo.LINE_CAP_ROUND); cr.set_line_join(cairo.LINE_JOIN_ROUND)
    for w_, a_ in ((22, 0.2), (8, 0.95)):
        cr.set_source_rgba(*AMBER, a_); cr.set_line_width(w_)
        cr.move_to(*pts[0])
        for p in pts[1:n]: cr.line_to(*p)
        cr.stroke()


@reg('G47')
def g47(cr, t, d):
    v = View(43.8, -87.0, 128); basemap(cr, v)
    x, y = v.xy(43.2, -87.15)
    pulse(cr, x, y, t, AMBER, 12)
    a = ramp(t, 0.4, 0.5); font(cr, TEXT, 34, bold=True)
    text(cr, 'NOAA meteotsunami buoy', x + 34, y - 6, INK, a)
    font(cr, TEXT, 26); text(cr, 'position shown approximately', x + 34, y + 32, MUTED, a)


@reg('G39')
def g39(cr, t, d):
    v = GREAT_LAKES2
    hl = UPPER if t > d * 0.62 else None
    basemap(cr, v)
    n = int(len(POINTS_106) * ramp(t, 0.2, d * 0.45))
    for la, lo in POINTS_106[:n]:
        x, y = v.xy(la, lo); circle(cr, x, y, 5, AMBER, 0.85)
    cnt = int(106 * ramp(t, 0.2, d * 0.45))
    a = ramp(t, 0.2, 0.5)
    font(cr, DISPLAY, 150, bold=True); text(cr, str(cnt), 120, 250, AMBER, a)
    font(cr, DISPLAY, 46); text(cr, 'dangerous meteotsunamis a year,', 120, 320, INK, a)
    text(cr, 'on average', 120, 378, INK, a)
    font(cr, TEXT, 26); text(cr, '2016 study of Great Lakes water-level records', 120, 428, MUTED, a)
    if t > d * 0.62:
        a = ramp(t, d * 0.62, 0.6)
        x, y = v.xy(42.6, -86.0)
        font(cr, TEXT, 34, bold=True); text(cr, 'Lake Michigan gets the most', x + 30, y + 12, AMBER, a)


# ---------------------------------------------------------------- cards
@reg('G11')
def g11(cr, t, d):
    quote_card(cr, t, d, ['And when we did…', 'there was a wave.'], 'Joseph Pecararo', 'Lifeguard captain, North Avenue Beach', size=88)


@reg('G12')
def g12(cr, t, d):
    cr.set_source_rgb(0, 0, 0); cr.paint()
    a = ramp(t, 0.1, 0.4)
    font(cr, DISPLAY, 100, bold=True); text(cr, '“Dozens down at Montrose.”', W / 2, 570, INK, a, 'center')


@reg('G15')
def g15(cr, t, d):
    quote_card(cr, t, d, ['She was riding the crest of this', 'huge wave into the harbor mouth…', 'then she disappeared.'],
               'Herbert Riederer', 'State conservation officer, Montrose Harbor', size=70)


@reg('G16')
def g16(cr, t, d):
    cr.set_source_rgb(0, 0, 0); cr.paint()
    a0 = fade_all(cr, t, d, 0.5, 0.5)
    for i, (nm, age) in enumerate((('Mae Gabriel', '48'), ('Edward Gabriel', '49'))):
        a = ramp(t, 0.4 + i * 1.2, 0.9) * a0
        font(cr, DISPLAY, 84); w = text(cr, nm, W / 2 - 40, 500 + i * 140, INK, a, 'right')
        font(cr, DISPLAY, 84); text(cr, age, W / 2 + 40, 500 + i * 140, MUTED, a, 'left')
    a = ramp(t, 3.0, 1.0) * a0
    font(cr, TEXT, 34); text(cr, 'Among the eight who drowned at Montrose Harbor and North Avenue Beach', W / 2, 780, MUTED, a, 'center')


@reg('G18')
def g18(cr, t, d):
    word_card(cr, t, d, 'seiche', 'say: saysh', 'A slosh: a lake’s water rocking from end to end')


@reg('G21')
def g21(cr, t, d):
    word_card(cr, t, d, 'meteotsunami', 'say: mee-tee-oh-tsoo-nah-mee', '')


@reg('G23')
def g23(cr, t, d):
    background(cr); a0 = fade_all(cr, t, d)
    a = ramp(t, 0.0, 0.6) * a0
    font(cr, DISPLAY, 150, bold=True)
    w1 = text_width(cr, 'meteo'); w2 = text_width(cr, 'tsunami'); x0 = W / 2 - (w1 + w2) / 2
    text(cr, 'meteo', x0, 470, AMBER, a); text(cr, 'tsunami', x0 + w1, 470, INK, a)
    a = ramp(t, 2.0, 0.6) * a0
    font(cr, TEXT, 50, italic=True); text(cr, 'meteo, as in meteorology', W / 2, 580, MUTED, a, 'center')
    a = ramp(t, 4.5, 0.7) * a0
    font(cr, DISPLAY, 80, bold=True); text(cr, 'A tsunami made by weather', W / 2, 760, INK, a, 'center')


@reg('G37')
def g37(cr, t, d):
    background(cr); a0 = fade_all(cr, t, d)
    days = [('JUNE', n) for n in range(26, 31)] + [('JULY', n) for n in range(1, 7)]
    k = min(len(days) - 1, int(max(t - 0.6, 0) / ((d - 2.0) / (len(days) - 1))))
    mon, day = days[k]
    cr.set_source_rgba(*INK, 0.08 * a0); rounded(cr, W / 2 - 230, 250, 460, 520, 28); cr.fill()
    cr.set_source_rgba(*AMBER, a0); rounded(cr, W / 2 - 230, 250, 460, 120, 28); cr.fill()
    cr.rectangle(W / 2 - 230, 330, 460, 40); cr.fill()
    font(cr, TEXT, 54, bold=True); text(cr, mon + ' 1954', W / 2, 335, BG, a0, 'center', tracking=6)
    font(cr, DISPLAY, 300, bold=True); text(cr, str(day), W / 2, 680, INK, a0, 'center')
    if k == len(days) - 1:
        a = ramp(t, 0.6 + (d - 2.0), 0.5) * a0
        font(cr, TEXT, 44, bold=True); text(cr, 'Ten days later', W / 2, 880, AMBER, a, 'center')


@reg('G38')
def g38(cr, t, d):
    background(cr); a0 = fade_all(cr, t, d)
    for i, (date, big, small, col) in enumerate((('June 26, 1954', 'Eight dead', 'No warning', INK),
                                                ('July 6, 1954', 'None', 'A warning was given', AMBER))):
        x = 560 + i * 800; a = ramp(t, 0.2 + i * 1.2, 0.6) * a0
        font(cr, TEXT, 40, bold=True); text(cr, date, x, 400, MUTED, a, 'center')
        font(cr, DISPLAY, 130, bold=True); text(cr, big, x, 560, col, a, 'center')
        font(cr, TEXT, 42); text(cr, small, x, 650, MUTED, a, 'center')
    cr.set_source_rgba(*MUTED, 0.3 * a0); cr.set_line_width(2); cr.move_to(W / 2, 330); cr.line_to(W / 2, 700); cr.stroke()


@reg('G40')
def g40(cr, t, d):
    date_card(cr, t, d, 'July 4, 1929', 'Grand Haven, Michigan', *PLACES['Grand Haven'])


@reg('G41')
def g41(cr, t, d):
    date_card(cr, t, d, 'July 4, 2003', 'Warren Dunes, Michigan', *PLACES['Warren Dunes'])


@reg('G43')
def g43(cr, t, d):
    date_card(cr, t, d, 'April 13, 2018', 'Ludington, Michigan', *PLACES['Ludington'])


@reg('G44')
def g44(cr, t, d):
    date_card(cr, t, d, 'June 21, 2025', 'Lake Superior', *PLACES['Whitefish Bay'], scale=75, lake=(47.4, -87.6))


@reg('G45')
def g45(cr, t, d):
    background(cr); a0 = fade_all(cr, t, d)
    a = ramp(t, 0.0, 0.6) * a0
    font(cr, DISPLAY, 230, bold=True); text(cr, '45 inches', W / 2, 560, AMBER, a, 'center')
    a = ramp(t, 0.7, 0.6) * a0
    font(cr, DISPLAY, 56); text(cr, 'the largest rise in 30 years of records', W / 2, 660, INK, a, 'center')
    font(cr, TEXT, 32); text(cr, 'Point Iroquois gauge, Whitefish Bay, Lake Superior', W / 2, 730, MUTED, a, 'center')


@reg('G46')
def g46(cr, t, d):
    background(cr); a0 = fade_all(cr, t, d)
    for i, y_ in enumerate(('1929', '1954', '2003')):
        a = ramp(t, 0.3 + i * 0.9, 0.5) * a0
        font(cr, DISPLAY, 130, bold=True); text(cr, y_, 440 + i * 520, 450, INK, a, 'center')
    for i, s in enumerate(('A storm.', 'Then sunshine.', 'Then the water.')):
        a = ramp(t, 4.0 + i * 1.6, 0.6) * a0
        font(cr, DISPLAY, 58, bold=i == 2); text(cr, s, 440 + i * 520, 640, AMBER if i == 2 else INK, a, 'center')


@reg('G48')
def g48(cr, t, d):
    background(cr); a0 = fade_all(cr, t, d)
    eyebrow(cr, 'Today', W / 2, 400, AMBER, ramp(t, 0, 0.4) * a0, 'center')
    big_line(cr, 'Still no meteotsunami', 530, t, 0.2, size=96)
    big_line(cr, 'warning system', 650, t, 0.5, size=96)


@reg('G49')
def g49(cr, t, d):
    background(cr); a0 = fade_all(cr, t, d)
    font(cr, DISPLAY, 200, bold=True); text(cr, '“', 200, 380, AMBER, 0.9 * ramp(t, 0, 0.5) * a0)
    part2 = t > d * 0.42
    lines = (['However, these meteotsunami waves can be', 'deadly and destructive, and continue to', 'impact the lakes for hours after the', 'rain and thunder have stopped.'] if part2 else
             ['Most people are used to thinking', 'that once the sun comes out, the', 'dangers of a storm have passed.'])
    st = d * 0.42 if part2 else 0.2
    for i, ln in enumerate(lines):
        a = ramp(t, st + i * 0.35, 0.5) * a0
        if not part2: a *= 1 - ramp(t, d * 0.42 - 0.3, 0.3)
        font(cr, DISPLAY, 66); text(cr, ln, 300, 360 + i * 92, INK, a)
    a = ramp(t, 0.8, 0.5) * a0
    rule(cr, 300, 780, 380, AMBER, a)
    font(cr, TEXT, 40, bold=True); text(cr, 'Bryan Mroczka', 300, 845, INK, a)
    font(cr, TEXT, 30); text(cr, 'Physical scientist and meteorologist, NOAA Great Lakes Environmental Research Laboratory', 300, 893, MUTED, a)


@reg('G50')
def g50(cr, t, d):
    background(cr)
    big_line(cr, 'Don’t go and look.', 500, t, 0.0, size=110)
    big_line(cr, 'Go up.', 660, t, 0.6, size=140, color=AMBER)


@reg('G51')
def g51(cr, t, d):
    bgimg(cr, END_BG, 0.35)
    a = ramp(t, 0.3, 0.6)
    eyebrow(cr, 'Next video', 140, 430, AMBER, a)
    font(cr, DISPLAY, 92, bold=True); text(cr, 'The city under Detroit', 140, 540, INK, a)
    font(cr, TEXT, 40); text(cr, '1,200 feet down. Still being dug.', 140, 610, MUTED, a)


END_BG = None


def bgimg(cr, path, alpha):
    global END_BG
    cr.set_source_rgb(*BG); cr.paint()
    if path:
        img = cairo.ImageSurface.create_from_png(path)
        cr.save(); cr.scale(W / img.get_width(), H / img.get_height()); cr.set_source_surface(img, 0, 0); cr.paint_with_alpha(alpha); cr.restore()
    g = cairo.LinearGradient(0, 0, W, 0); g.add_color_stop_rgba(0, *BG, 0.9); g.add_color_stop_rgba(0.6, *BG, 0.3); g.add_color_stop_rgba(1, *BG, 0.1)
    cr.set_source(g); cr.paint()


# ---------------------------------------------------------------- side-view diagrams
SEA_Y = 560


def water(cr, xs, ys, floor_y, color=WATER, top=None):
    """Fill water between the surface (xs, ys) and the floor."""
    cr.move_to(xs[0], floor_y)
    for x, y in zip(xs, ys): cr.line_to(x, y)
    cr.line_to(xs[-1], floor_y); cr.close_path()
    g = cairo.LinearGradient(0, min(ys), 0, floor_y)
    g.add_color_stop_rgb(0, *WATER_HI); g.add_color_stop_rgb(1, *WATER)
    cr.set_source(g); cr.fill()
    cr.set_source_rgba(*INK, 0.85); cr.set_line_width(3)
    cr.move_to(xs[0], ys[0])
    for x, y in zip(xs[1:], ys[1:]): cr.line_to(x, y)
    cr.stroke()


def ground(cr, pts):
    cr.move_to(*pts[0])
    for p in pts[1:]: cr.line_to(*p)
    cr.line_to(pts[-1][0], H); cr.line_to(pts[0][0], H); cr.close_path()
    cr.set_source_rgb(*LAND); cr.fill_preserve(); cr.set_source_rgba(*COAST, 0.8); cr.set_line_width(2); cr.stroke()


def cloud(cr, x, y, s=1.0, alpha=1.0, color=STORM):
    cr.set_source_rgba(*color, alpha)
    for dx, dy, r in ((-90, 10, 55), (-30, -20, 75), (50, -5, 65), (110, 15, 45), (0, 25, 60)):
        cr.new_sub_path(); cr.arc(x + dx * s, y + dy * s, r * s, 0, 2 * math.pi)
    cr.fill()
    cr.rectangle(x - 140 * s, y + 10 * s, 280 * s, 50 * s); cr.fill()


def down_arrows(cr, x, y, n=4, s=1.0, alpha=1.0, t=0.0):
    for k in range(n):
        xx = x + (k - (n - 1) / 2) * 60 * s; ph = (t * 1.5 + k * 0.3) % 1
        arrow(cr, [(xx, y + 20 * ph), (xx, y + 70 * s + 20 * ph)], AMBER, alpha * (0.4 + 0.6 * (1 - ph)), 4, 14)


def label(cr, s, x, y, size=36, color=INK, alpha=1.0, align='center', bold=True):
    font(cr, TEXT, size, bold=bold); text(cr, s, x, y, color, alpha, align)


def bump(xs, center, height, width):
    return height * np.exp(-((xs - center) / width) ** 2)


XS = np.linspace(0, W, 400)


@reg('G14')
def g14(cr, t, d):
    background(cr, glow=False)
    a = ramp(t, 0.2, 0.5)
    # left panel: ocean wave curls and breaks
    cr.save(); cr.rectangle(0, 0, W / 2 - 10, H); cr.clip()
    ph = (t % 3.0) / 3.0
    xs = np.linspace(80, W / 2 - 80, 200)
    cx = 160 + ph * 620
    ys = SEA_Y - bump(xs, cx, 170, 80) * np.where(xs > cx, 1.0, 1.0) + 6 * np.sin(xs / 40)
    water(cr, xs, ys, 820)
    # the curling lip and spray
    tip_y = SEA_Y - 170
    cr.set_source_rgba(*INK, 0.9); cr.set_line_width(6); cr.set_line_cap(cairo.LINE_CAP_ROUND)
    cr.move_to(cx - 10, tip_y + 4); cr.curve_to(cx + 60, tip_y - 30, cx + 120, tip_y + 20, cx + 95, tip_y + 70); cr.stroke()
    for k in range(10):
        circle(cr, cx + 90 + 12 * math.sin(k * 7.1), tip_y + 70 + 18 * math.cos(k * 3.3), 4, INK, 0.6)
    label(cr, 'Ocean wave', W / 4, 260, 48, INK, a); label(cr, 'Curls over and breaks', W / 4, 320, 34, MUTED, a, bold=False)
    cr.restore()
    # right panel: the whole water level rises
    xs = np.linspace(W / 2 + 80, W - 80, 200)
    rise = 170 * ease_in_out(min(t / (d * 0.7), 1))
    cr.set_source_rgb(*hexc('4A565E')); cr.rectangle(W - 330, SEA_Y - 20, 250, 300); cr.fill()  # breakwater
    label(cr, 'Breakwater', W - 205, SEA_Y + 330, 28, MUTED, a, 'center', False)
    ys = SEA_Y + 60 - rise + 4 * np.sin(xs / 50 + t)
    cr.push_group(); water(cr, xs, ys, 820); cr.pop_group_to_source(); cr.paint_with_alpha(0.88)
    label(cr, 'Surge', 3 * W / 4, 260, 48, AMBER, a); label(cr, 'The whole lake rises', 3 * W / 4, 320, 34, MUTED, a, bold=False)
    cr.set_source_rgba(*MUTED, 0.3); cr.set_line_width(2); cr.move_to(W / 2, 200); cr.line_to(W / 2, 880); cr.stroke()


@reg('G19')
def g19(cr, t, d):
    background(cr, glow=False)
    x0, x1, yb = 360, 1560, 820
    cr.set_source_rgba(*MUTED, 0.8); cr.set_line_width(5)
    cr.move_to(x0, 380); cr.line_to(x0, yb); cr.line_to(x1, yb); cr.line_to(x1, 380); cr.stroke()
    tilt = 110 * math.sin(2 * math.pi * t / 4.0)
    xs = np.linspace(x0 + 3, x1 - 3, 200)
    ys = 600 + tilt * np.cos(np.pi * (xs - x0) / (x1 - x0))
    water(cr, xs, ys, yb - 3)
    a = ramp(t, 0.3, 0.5)
    label(cr, 'A seiche', W / 2, 220, 56, INK, a)
    label(cr, 'The water rocks from end to end, over hours', W / 2, 290, 36, MUTED, a, bold=False)


@reg('G20')
def g20(cr, t, d):
    background(cr, glow=False)
    ox, oy, gw, gh = 260, 820, 1440, 520
    cr.set_source_rgba(*MUTED, 0.7); cr.set_line_width(3)
    cr.move_to(ox, oy - gh); cr.line_to(ox, oy); cr.line_to(ox + gw, oy); cr.stroke()
    label(cr, 'Water level', ox - 20, oy - gh - 24, 30, MUTED, 1, 'left', False)
    label(cr, 'Time', ox + gw, oy + 50, 30, MUTED, 1, 'right', False)
    p1 = ramp(t, 0.3, d * 0.4)
    xs = np.linspace(0, 1, 300)
    ys = 0.22 * np.sin(xs * 2 * np.pi * 1.2)
    _plot(cr, ox, oy - gh * 0.45, gw, gh, xs, ys, p1, MUTED)
    if p1 > 0.2: label(cr, 'Seiche: rises and falls over hours', ox + gw * 0.2, oy - gh * 0.45 - gh * 0.3, 34, MUTED, ramp(t, 0.8, 0.5), 'left', False)
    p2 = ramp(t, d * 0.5, d * 0.25)
    ys2 = np.where(xs < 0.55, 0.0, np.where(xs < 0.6, (xs - 0.55) / 0.05 * 0.85, np.maximum(0.85 - (xs - 0.6) / 0.06 * 0.85, 0)))
    _plot(cr, ox, oy - gh * 0.1, gw, gh, xs, ys2, p2, AMBER, 5)
    if p2 > 0.6: label(cr, 'June 26, 1954: more than ten feet in minutes', ox + gw * 0.56, oy - gh * 0.86, 34, AMBER, ramp(t, d * 0.65, 0.5), 'right')


def _plot(cr, ox, base, gw, gh, xs, ys, prog, color, width=4):
    n = max(2, int(len(xs) * prog))
    cr.set_source_rgba(*color, 1); cr.set_line_width(width)
    cr.move_to(ox + xs[0] * gw, base - ys[0] * gh)
    for x, y in zip(xs[1:n], ys[1:n]): cr.line_to(ox + x * gw, base - y * gh)
    cr.stroke()


@reg('G22')
def g22(cr, t, d):
    background(cr, glow=False)
    up = 70 * ramp(t, 1.0, 0.4)
    fl = 860
    ground(cr, [(0, fl), (900, fl), (900, fl - up), (W, fl - up)])
    sp = max(t - 1.2, 0) * 260
    h = 90 * ramp(t, 1.1, 0.4) * (1 - 0.3 * min(sp / 900, 1))
    ys = SEA_Y - (bump(XS, 900 - sp, h, 110) + bump(XS, 900 + sp, h, 110) if sp > 0 else bump(XS, 900, h, 110))
    water(cr, XS, ys, fl - 2)
    ground(cr, [(0, fl), (900, fl), (900, fl - up), (W, fl - up)])
    a = ramp(t, 0.2, 0.5)
    label(cr, 'An ordinary tsunami', W / 2, 220, 56, INK, a)
    label(cr, 'The sea floor moves, and shoves the water above it', W / 2, 290, 36, MUTED, a, bold=False)
    if t > 1.0: label(cr, 'Earthquake', 900, fl - up + 60, 32, AMBER, ramp(t, 1.0, 0.4))


def storm_bump_scene(cr, t, d, storm_x, wave_x, wave_h, cap1, cap2, show_arrows=True, cap_color=INK):
    background(cr, glow=False)
    fl = 880
    ys = SEA_Y - bump(XS, wave_x, wave_h, 160) + 3 * np.sin(XS / 35 + t * 2)
    water(cr, XS, ys, fl)
    ground(cr, [(0, fl), (W, fl)])
    cloud(cr, storm_x, 300, 1.0, 0.95)
    if show_arrows: down_arrows(cr, storm_x, 380, 4, 1.0, 1.0, t)
    a = ramp(t, 0.2, 0.5)
    label(cr, cap1, W / 2, 140, 52, cap_color, a)
    if cap2: label(cr, cap2, W / 2, 205, 34, MUTED, a, bold=False)


@reg('G25')
def g25(cr, t, d):
    sx = 500 + 600 * t / d
    storm_bump_scene(cr, t, d, sx, sx, 22 * ramp(t, 0.5, 1.5), 'A jump in air pressure pushes on the water', 'A small wave forms underneath: a few inches high')


@reg('G27')
def g27(cr, t, d):
    sx = 300 + 1300 * t / d
    storm_bump_scene(cr, t, d, sx, sx, 20 + 150 * ramp(t, 0.3, d * 0.9), 'Same speed: every push adds to the last', 'The storm stays on top of its wave, and the wave grows', cap_color=AMBER)


@reg('G26')
def g26(cr, t, d):
    background(cr, glow=False)
    a = ramp(t, 0.2, 0.5)
    label(cr, 'This kind of wave goes faster in deeper water', W / 2, 140, 50, INK, a)
    rows = ((360, 300, 1.0, 'Deep water: fast', 'At Lake Michigan’s average depth of 279 feet: about 65 mph'),
            (760, 110, 0.33, 'Shallow water: slow', 'In 30 feet of water: about 21 mph'))
    for yc, depth, spd, l1, l2 in rows:
        top = yc; fl = yc + depth * 0.9
        x = 160 + ((t * 600 * spd) % 1600)
        ys = top - bump(XS, x, 40, 90)
        water(cr, XS, ys, fl)
        ground(cr, [(0, fl), (W, fl)])
        label(cr, l1, 160, top - 110, 38, AMBER if spd == 1.0 else INK, a, 'left')
        label(cr, l2, 160, top - 66, 28, MUTED, a, 'left', False)


@reg('G28')
def g28(cr, t, d):
    background(cr, glow=False)
    rows = ((270, 'Too slow', 0.55, 1.0, 22), (560, 'Too fast', 1.6, 1.0, 22), (850, 'Just right', 1.0, 1.0, 95))
    for i, (yc, name, sspd, wspd, hmax) in enumerate(rows):
        a = ramp(t, 0.2 + i * 0.6, 0.5)
        if a <= 0: continue
        tt = max(t - (0.2 + i * 0.6), 0)
        wx = 260 + (tt * 160 * wspd) % 1500; sx = 260 + (tt * 160 * sspd) % 1500
        h = hmax * min(tt / 3, 1) if i == 2 else 22
        cr.save(); cr.rectangle(0, yc - 200, W, 280); cr.clip()
        ys = yc - bump(XS, wx, h, 120)
        cr.push_group()
        water(cr, XS, ys, yc + 70)
        cloud(cr, sx, yc - 150, 0.45, 0.9)
        cr.pop_group_to_source(); cr.paint_with_alpha(a)
        cr.restore()
        label(cr, name, 80, yc - 120, 40, AMBER if i == 2 else INK, a, 'left')


@reg('G29')
def g29(cr, t, d):
    background(cr, glow=False)
    fl = 880; f = t / d
    sx = 200 + 1450 * f
    h = 30 + 120 * ease_in_out(f)
    ys = SEA_Y - bump(XS, sx, h, 170) + 3 * np.sin(XS / 35 + t * 2)
    water(cr, XS, ys, fl); ground(cr, [(0, fl), (W, fl)])
    cloud(cr, sx, 300, 1.0, 0.9)
    label(cr, 'Chicago', 120, fl + 60, 34, MUTED, 1, 'left'); label(cr, 'Michigan City', W - 120, fl + 60, 34, MUTED, 1, 'right')
    label(cr, 'The wave keeps growing, all the way across', W / 2, 140, 50, INK, ramp(t, 0.2, 0.5))


@reg('G30')
def g30(cr, t, d):
    background(cr, glow=False)
    f = ease_in_out(t / d)
    shore = [(0, 860), (1000, 860), (1650, 640), (W, 600)]
    x = 300 + 1150 * (1 - (1 - f) ** 1.6)
    h = 40 + 170 * max(0, (x - 900) / 600) ** 1.4
    ys = SEA_Y - bump(XS, x, h, 140 - 60 * min(max((x - 900) / 600, 0), 1))
    water(cr, XS, np.minimum(ys, 860), 860)
    ground(cr, shore)
    label(cr, 'In shallow water it slows down and piles up', W / 2, 140, 50, INK, ramp(t, 0.2, 0.5))


@reg('G31')
def g31(cr, t, d):
    background(cr, glow=False)
    cr.set_source_rgb(*WATER); cr.rectangle(0, 0, W, H); cr.fill()
    cr.set_source_rgb(*LAND)
    cr.move_to(0, 0); cr.line_to(820, 540); cr.line_to(820, H); cr.line_to(0, H); cr.fill()
    cr.move_to(W, 0); cr.line_to(1100, 540); cr.line_to(1100, H); cr.line_to(W, H); cr.fill()
    f = (t % 2.0) / 2.0
    for k in range(3):
        g = (f + k / 3) % 1; y = 60 + 820 * g
        half = max(140, 900 - 760 * min(g * 1.4, 1))
        cr.set_source_rgba(*AMBER, 0.4 + 0.6 * g); cr.set_line_width(4 + 14 * g)
        cr.move_to(W / 2 - half, y); cr.line_to(W / 2 + half, y); cr.stroke()
    label(cr, 'A harbor squeezes it higher still', W / 2, 140, 50, INK, ramp(t, 0.1, 0.4))


@reg('G42')
def g42(cr, t, d):
    background(cr, glow=False)
    cr.set_source_rgb(*WATER); cr.rectangle(0, 0, W, 760); cr.fill()
    cr.set_source_rgb(*hexc('6E6A5E')); cr.rectangle(0, 760, W, H - 760); cr.fill()
    for k in range(5):
        y = (t * 70 + k * 150) % 760
        cr.set_source_rgba(*INK, 0.35); cr.set_line_width(3)
        cr.move_to(0, y); cr.line_to(W / 2 - 160, y); cr.stroke(); cr.move_to(W / 2 + 160, y); cr.line_to(W, y); cr.stroke()
    cr.set_source_rgba(*BG, 0.35); cr.rectangle(W / 2 - 120, 180, 240, 580); cr.fill()
    for k in range(4):
        y = 740 - ((t * 160 + k * 190) % 560)
        arrow(cr, [(W / 2, y), (W / 2, y - 130)], AMBER, 0.95, 9, 30)
    sy = 700 - 380 * ramp(t, 1.0, d - 1.5)
    circle(cr, W / 2 + 30, sy, 12, INK)
    label(cr, 'Rip current', W / 2 + 200, 420, 44, AMBER, ramp(t, 0.3, 0.5), 'left')
    label(cr, 'Pulls away from the beach, for hours after the wave', W / 2, 140, 46, INK, ramp(t, 0.3, 0.5))
