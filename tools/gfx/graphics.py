"""Every graphic in video 1, keyed by its G number in edit-plan.json. Each is draw(cr, t, d)."""
import math
import numpy as np
from style import *
from maps import *

G = {}


def reg(gid):
    def deco(fn):
        G[gid] = fn; return fn
    return deco


# ---------- card building blocks ----------
def fade_all(cr, t, d, fin=0.35, fout=0.25):
    """Overall opacity for a card: quick fade in, short fade out at the end."""
    return min(ramp(t, 0, fin), 1 - ramp(t, d - fout, fout) if d > 1 else 1)


def big_line(cr, s, y, t, start, size=96, color=INK, family=DISPLAY, bold=True, x=W / 2, align='center', rise=18):
    a = ramp(t, start, 0.6)
    font(cr, family, size, bold=bold)
    text(cr, s, x, y + rise * (1 - a), color, a, align)


def quote_card(cr, t, d, quote_lines, who, role, size=62):
    background(cr)
    a0 = fade_all(cr, t, d)
    font(cr, DISPLAY, 220, bold=True)
    text(cr, '“', 230, 430, AMBER, 0.9 * ramp(t, 0, 0.5) * a0)
    y = 420
    for i, ln in enumerate(quote_lines):
        a = ramp(t, 0.25 + i * 0.55, 0.6) * a0
        font(cr, DISPLAY, size, bold=False)
        text(cr, ln, 340, y + i * (size * 1.35) + 14 * (1 - a), INK, a)
    yb = y + len(quote_lines) * size * 1.35 + 40
    a = ramp(t, 0.6 + len(quote_lines) * 0.5, 0.6) * a0
    rule(cr, 340, yb, 420, AMBER, a, 3)
    font(cr, TEXT, 40, bold=True); text(cr, who, 340, yb + 64, INK, a)
    font(cr, TEXT, 32); text(cr, role, 340, yb + 112, MUTED, a)


def word_card(cr, t, d, word, say, meaning):
    background(cr)
    a0 = fade_all(cr, t, d)
    big_line(cr, word, 520, t, 0.0, size=150, color=INK)
    a = ramp(t, 0.6, 0.6) * a0
    font(cr, TEXT, 44, italic=True); text(cr, say, W / 2, 620, AMBER, a, 'center')
    if meaning:
        a = ramp(t, 1.4, 0.7) * a0
        font(cr, TEXT, 36); text(cr, meaning, W / 2, 720, MUTED, a, 'center')


def mini_map(cr, cx, cy, view_scale, lat, lon, t, start=0.6, lake_lat=43.9, lake_lon=-86.9, box=520):
    """A small locator map inside a rounded panel, with a pulsing dot."""
    a = ramp(t, start, 0.6)
    if a <= 0: return
    cr.save()
    cr.rectangle(cx - box / 2, cy - box / 2, box, box); cr.clip()
    cr.push_group()
    v = View(lake_lat, lake_lon, view_scale)
    # shift view so lake centre is at panel centre
    cr.translate(cx - W / 2, cy - H / 2)
    basemap(cr, v, borders=False, labels=False)
    x, y = v.xy(lat, lon)
    pulse(cr, x, y, t, AMBER, 9)
    cr.pop_group_to_source(); cr.paint_with_alpha(a)
    cr.restore()
    cr.set_source_rgba(*MUTED, 0.35 * a); cr.set_line_width(2)
    cr.rectangle(cx - box / 2, cy - box / 2, box, box); cr.stroke()


def date_card(cr, t, d, date, place_line, lat=None, lon=None, scale=95, lake=(43.9, -86.9), eyebrow_s=None):
    background(cr)
    a0 = fade_all(cr, t, d)
    x0 = 200
    if eyebrow_s:
        eyebrow(cr, eyebrow_s, x0, 430, AMBER, ramp(t, 0, 0.5) * a0)
    a = ramp(t, 0.15, 0.6) * a0
    font(cr, DISPLAY, 110, bold=True); text(cr, date, x0, 560 + 16 * (1 - a), INK, a)
    a = ramp(t, 0.55, 0.6) * a0
    font(cr, TEXT, 44); text(cr, place_line, x0, 640, MUTED, a)
    if lat is not None:
        mini_map(cr, 1440, 540, scale, lat, lon, t, 0.5, lake[0], lake[1])


# ---------- section 1 ----------
@reg('G01')
def g01(cr, t, d):
    background(cr); a0 = fade_all(cr, t, d)
    big_line(cr, 'Eight people drowned.', 580, t, 0.0, size=110)


@reg('G02')
def g02(cr, t, d):
    quote_card(cr, t, d, ['under calm winds and', 'a bright sunny sky'], 'National Weather Service', 'Describing June 26, 1954', size=88)


@reg('G03')
def g03(cr, t, d):
    v = LAKE_MICH; v = View(v.lat, v.lon, v.scale * (1 + 0.04 * t / max(d, 1)))
    basemap(cr, v, borders=False, labels=False)
    cr.set_source_rgba(*BG, 0.55); cr.paint()
    a0 = fade_all(cr, t, d)
    big_line(cr, 'A tsunami.', 520, t, 0.0, size=130)
    big_line(cr, 'On a lake.', 670, t, 0.7, size=130, color=AMBER)


@reg('G04')
def g04(cr, t, d):
    v = GREAT_LAKES2
    basemap(cr, v)
    pts = POINTS_106
    n = int(len(pts) * ramp(t, 0.3, d * 0.7))
    for i, (la, lo) in enumerate(pts[:n]):
        x, y = v.xy(la, lo); circle(cr, x, y, 5, AMBER, 0.85)
    a = ramp(t, 0.4, 0.6)
    eyebrow(cr, 'The Great Lakes', 120, 140, AMBER, a)
    font(cr, DISPLAY, 84, bold=True); text(cr, 'More than 100 a year', 120, 240, INK, a)


GREAT_LAKES2 = View(45.2, -84.0, 118)
POINTS_106 = lake_points(106)


# ---------- section 2 ----------
@reg('G05')
def g05(cr, t, d):
    f = ramp(t, 0, min(2.2, d * 0.5))
    v = View.lerp(GREAT_LAKES2, View(43.8, -87.0, 128), f)
    basemap(cr, v, labels=f < 0.5)
    a = ramp(t, 2.0, 0.7)
    if a > 0:
        xl = v.xy(43.8, -88.55)[0]
        dim_line(cr, (xl, v.xy(46.10, 0)[1]), (xl, v.xy(41.62, 0)[1]), '307 miles', a, vertical=True)
        w_, e_ = shore_pair(43.95)
        ya = v.xy(43.95, 0)[1]
        dim_line(cr, (v.xy(43.95, w_)[0], ya), (v.xy(43.95, e_)[0], ya), '118 miles', a)


def shore_pair(lat):
    """West and east shore longitudes of Lake Michigan at a latitude."""
    a = UPPER; xs = []
    for k in range(len(a) - 1):
        (x1, y1), (x2, y2) = a[k], a[k + 1]
        if (y1 - lat) * (y2 - lat) <= 0 and y1 != y2:
            x = x1 + (lat - y1) * (x2 - x1) / (y2 - y1)
            if -88.3 < x < -85.5: xs.append(x)
    return min(xs), max(xs)


def dim_line(cr, p0, p1, label, a, vertical=False):
    cr.set_source_rgba(*AMBER, a); cr.set_line_width(3)
    cr.move_to(*p0); cr.line_to(*p1); cr.stroke()
    for p in (p0, p1):
        if vertical: cr.move_to(p[0] - 16, p[1]); cr.line_to(p[0] + 16, p[1])
        else: cr.move_to(p[0], p[1] - 16); cr.line_to(p[0], p[1] + 16)
        cr.stroke()
    font(cr, DISPLAY, 46, bold=True)
    mx, my = (p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2
    if vertical: text(cr, label, mx - 24, my + 16, INK, a, 'right')
    else: text(cr, label, mx, my + 64, INK, a, 'center')


@reg('G06')
def g06(cr, t, d):
    v = View(43.8, -85.0, 128)
    basemap(cr, v, labels=False)
    g = cairo.LinearGradient(1000, 0, 1500, 0)
    g.add_color_stop_rgba(0, *BG, 0); g.add_color_stop_rgba(1, *BG, 0.92)
    cr.set_source(g); cr.rectangle(1000, 0, W - 1000, H); cr.fill()
    for i, (p, al) in enumerate([('Green Bay', 'right'), ('Milwaukee', 'right'), ('Chicago', 'right'),
                                 ('Michigan City', 'left'), ('Grand Haven', 'left'), ('Ludington', 'left')]):
        place(cr, v, p, t, 0.1 + i * 0.12, INK, 6, size=26, align=al)
    a = ramp(t, 0.2, 0.6)
    font(cr, DISPLAY, 150, bold=True); text(cr, '12 million', 1250, 520, AMBER, a)
    font(cr, DISPLAY, 58); text(cr, 'people live along', 1250, 610, INK, a)
    text(cr, 'its shores', 1250, 685, INK, a)


@reg('G07')
def g07(cr, t, d):
    date_card(cr, t, d, 'June 26, 1954', 'Chicago, Illinois', 41.88, -87.63, eyebrow_s='Saturday')
