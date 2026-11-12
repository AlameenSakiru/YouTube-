"""Map drawing for the Great Lakes graphics, from the GSHHS coastline data shipped with basemap-data."""
import math
import numpy as np
import cairo
from style import *

D = '/usr/local/lib/python3.13/site-packages/mpl_toolkits/basemap_data'


def _load(kind, res='i'):
    meta = [l.split() for l in open(f'{D}/{kind}meta_{res}.dat')]
    raw = open(f'{D}/{kind}_{res}.dat', 'rb').read()
    out = []
    for m in meta:
        off, cnt = int(m[5]), int(m[6])
        a = np.frombuffer(raw[off:off + cnt], dtype='<f4').reshape(-1, 2).astype(float)
        if len(a) and a[:, 0].max() > -100 and a[:, 0].min() < -70 and a[:, 1].max() > 38 and a[:, 1].min() < 52:
            out.append((int(m[0]), a))
    return out


SHORES = _load("gshhs")
LAKES = [a for lvl, a in SHORES if lvl == 2 and len(a) > 40]
ISLANDS = [a for lvl, a in SHORES if lvl == 3]
STATES = [a for _, a in _load('states')]
COUNTRIES = [a for _, a in _load('countries')]
UPPER = max(LAKES, key=len)  # Superior + Michigan + Huron, joined in the data

PLACES = {
    'Chicago': (41.88, -87.63), 'Milwaukee': (43.04, -87.91), 'Madison': (43.07, -89.40),
    'La Crosse': (43.80, -91.24), 'Rockford': (42.27, -89.09), 'Michigan City': (41.72, -86.90),
    'Grand Haven': (43.06, -86.23), 'Warren Dunes': (41.91, -86.60), 'Ludington': (43.95, -86.45),
    'Detroit': (42.33, -83.05), 'Green Bay': (44.51, -88.01), 'Gary': (41.60, -87.35),
    'Duluth': (46.79, -92.10), 'Thunder Bay': (48.38, -89.25), 'Sault Ste. Marie': (46.50, -84.35),
    'Whitefish Bay': (46.60, -84.75), 'Toronto': (43.65, -79.38), 'Cleveland': (41.50, -81.69),
    'North Avenue Beach': (41.915, -87.625), 'Montrose Harbor': (41.963, -87.637),
    'Wilmette': (42.08, -87.69), 'Chicago River': (41.889, -87.612), 'Loyola Beach': (42.01, -87.66),
}
LAKE_LABELS = {'LAKE SUPERIOR': (47.65, -87.6), 'LAKE MICHIGAN': (43.9, -87.0), 'LAKE HURON': (44.75, -82.3),
               'LAKE ERIE': (42.2, -81.2), 'LAKE ONTARIO': (43.65, -77.9)}


class View:
    """Equirectangular view centred on (lat, lon); scale in pixels per degree of latitude."""
    def __init__(self, lat, lon, scale):
        self.lat, self.lon, self.scale = lat, lon, scale
        self.kx = scale * math.cos(math.radians(lat))

    def xy(self, lat, lon):
        return (W / 2 + (lon - self.lon) * self.kx, H / 2 - (lat - self.lat) * self.scale)

    def pts(self, a):
        x = W / 2 + (a[:, 0] - self.lon) * self.kx
        y = H / 2 - (a[:, 1] - self.lat) * self.scale
        return np.stack([x, y], 1)

    @staticmethod
    def lerp(a, b, f):
        f = ease_in_out(f)
        return View(a.lat + (b.lat - a.lat) * f, a.lon + (b.lon - a.lon) * f,
                    math.exp(math.log(a.scale) + (math.log(b.scale) - math.log(a.scale)) * f))


def _poly(cr, p):
    cr.move_to(*p[0])
    for q in p[1:]: cr.line_to(*q)
    cr.close_path()


def basemap(cr, v, borders=True, labels=True, highlight=None, dim_others=False, label_alpha=1.0):
    cr.set_source_rgb(*LAND); cr.paint()
    g = cairo.RadialGradient(W * 0.5, H * 0.5, 100, W * 0.5, H * 0.5, W * 0.8)
    g.add_color_stop_rgba(0, 1, 1, 1, 0.03); g.add_color_stop_rgba(1, 0, 0, 0, 0.25)
    if borders:
        cr.set_line_width(1.2); cr.set_source_rgba(*BORDER, 1)
        for a in STATES:
            p = v.pts(a); cr.move_to(*p[0])
            for q in p[1:]: cr.line_to(*q)
            cr.stroke()
        cr.set_dash([8, 6]); cr.set_line_width(1.6); cr.set_source_rgba(*MUTED, 0.35)
        for a in COUNTRIES:
            p = v.pts(a); cr.move_to(*p[0])
            for q in p[1:]: cr.line_to(*q)
            cr.stroke()
        cr.set_dash([])
    for a in LAKES:
        _poly(cr, v.pts(a)); cr.set_source_rgb(*WATER); cr.fill_preserve()
        cr.set_source_rgba(*COAST, 0.9); cr.set_line_width(1.6); cr.stroke()
    for a in ISLANDS:
        _poly(cr, v.pts(a)); cr.set_source_rgb(*LAND); cr.fill()
    if highlight is not None:
        cr.save(); cr.set_source_rgba(*AMBER, 0.85); cr.set_line_width(4)
        _poly(cr, v.pts(highlight)); cr.stroke(); cr.restore()
    cr.set_source(g); cr.paint()
    if labels:
        font(cr, TEXT, max(16, min(30, v.scale / 9)), italic=True)
        for name, (la, lo) in LAKE_LABELS.items():
            x, y = v.xy(la, lo)
            if -200 < x < W + 200 and -50 < y < H + 50:
                text(cr, name, x, y, MUTED, 0.75 * label_alpha, 'center', tracking=4)


def place(cr, v, name, t=99, appear=0.0, color=INK, dot=7, dx=14, dy=8, size=28, align='left', label=None, bold=False):
    a = ramp(t, appear, 0.5)
    if a <= 0: return
    x, y = v.xy(*PLACES[name]) if isinstance(name, str) else v.xy(*name)
    circle(cr, x, y, dot, color, a)
    font(cr, TEXT, size, bold=bold)
    lab = label if label is not None else name
    if align == 'left': text(cr, lab, x + dx, y + dy, color, a)
    elif align == 'right': text(cr, lab, x - dx, y + dy, color, a, 'right')
    else: text(cr, lab, x, y + dy, color, a, 'center')


def shore_lon(lat, lo=-88.6, hi=-86.0):
    """Longitude of Lake Michigan's west shore at this latitude (from the coastline data)."""
    a = UPPER; xs = []
    for i in range(len(a) - 1):
        (x1, y1), (x2, y2) = a[i], a[i + 1]
        if (y1 - lat) * (y2 - lat) <= 0 and y1 != y2:
            x = x1 + (lat - y1) * (x2 - x1) / (y2 - y1)
            if lo < x < hi: xs.append(x)
    return min(xs) if xs else None


def shore_segment(lat0, lat1, n=60):
    lats = np.linspace(lat0, lat1, n)
    return [(la, shore_lon(la)) for la in lats if shore_lon(la) is not None]


def in_lake(lat, lon):
    for a in LAKES:
        x, y = a[:, 0], a[:, 1]
        inside = False; j = len(a) - 1
        for i in range(len(a)):
            if (y[i] > lat) != (y[j] > lat) and lon < (x[j] - x[i]) * (lat - y[i]) / (y[j] - y[i] + 1e-12) + x[i]:
                inside = not inside
            j = i
        if inside: return True
    return False


def lake_points(n, seed=3):
    """Random points in the lakes, weighted toward southern Lake Michigan."""
    rng = np.random.default_rng(seed); out = []
    while len(out) < n:
        if rng.random() < 0.38:
            la, lo = rng.uniform(41.6, 44.5), rng.uniform(-87.9, -86.2)
        else:
            la, lo = rng.uniform(41.4, 49.0), rng.uniform(-92.2, -76.0)
        if in_lake(la, lo): out.append((la, lo))
    return out


GREAT_LAKES = View(45.2, -84.2, 82)
LAKE_MICH = View(43.9, -86.9, 175)
SOUTH_LM = View(42.25, -87.2, 520)
CHICAGO_SHORE = View(41.97, -87.66, 4200)
