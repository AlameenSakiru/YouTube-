"""Shared look for every graphic in the video: palette, type, easing and frame helpers."""
import math
import cairo
import numpy as np

W, H, FPS = 1920, 1080, 30

# palette (RGB 0-1)
def hexc(h):
    h = h.lstrip('#'); return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))

BG = hexc('0D1419')        # deep ink
BG2 = hexc('16212A')       # centre glow
LAND = hexc('1A252D')
WATER = hexc('2B4555')
WATER_HI = hexc('3A5C70')
COAST = hexc('5C7A8C')
BORDER = hexc('34444F')
INK = hexc('EDE8DF')       # warm paper white
MUTED = hexc('A3AEB4')
DIM = hexc('6B7A83')
AMBER = hexc('F0A43A')     # the wave, danger
STORM = hexc('8E9AA6')     # storm line
RED = hexc('D9644A')

DISPLAY = 'Inter Display'
TEXT = 'Inter'


def ease_out(x):
    x = min(max(x, 0.0), 1.0); return 1 - (1 - x) ** 3


def ease_in_out(x):
    x = min(max(x, 0.0), 1.0); return x * x * (3 - 2 * x)


def ramp(t, start, dur):
    """0 before start, eased 0..1 over dur."""
    return ease_out((t - start) / dur) if dur > 0 else float(t >= start)


def new_surface():
    s = cairo.ImageSurface(cairo.FORMAT_RGB24, W, H)
    return s, cairo.Context(s)


def background(cr, glow=True):
    cr.set_source_rgb(*BG); cr.paint()
    if glow:
        g = cairo.RadialGradient(W * 0.5, H * 0.45, 50, W * 0.5, H * 0.45, W * 0.75)
        g.add_color_stop_rgba(0, *BG2, 1); g.add_color_stop_rgba(1, *BG, 0)
        cr.set_source(g); cr.paint()


def font(cr, family=TEXT, size=40, bold=False, italic=False):
    cr.select_font_face(family, cairo.FONT_SLANT_ITALIC if italic else cairo.FONT_SLANT_NORMAL,
                        cairo.FONT_WEIGHT_BOLD if bold else cairo.FONT_WEIGHT_NORMAL)
    cr.set_font_size(size)


def text_width(cr, s, tracking=0):
    return cr.text_extents(s).x_advance + tracking * max(len(s) - 1, 0)


def text(cr, s, x, y, color=INK, alpha=1.0, align='left', tracking=0):
    """Draw s with its baseline at y. align: left, center, right."""
    w = text_width(cr, s, tracking)
    if align == 'center': x -= w / 2
    elif align == 'right': x -= w
    cr.set_source_rgba(*color, alpha)
    if tracking == 0:
        cr.move_to(x, y); cr.show_text(s)
    else:
        for ch in s:
            cr.move_to(x, y); cr.show_text(ch); x += cr.text_extents(ch).x_advance + tracking
    return w


def wrap(cr, s, max_w):
    words, lines, cur = s.split(), [], ''
    for w_ in words:
        trial = (cur + ' ' + w_).strip()
        if text_width(cr, trial) <= max_w or not cur: cur = trial
        else: lines.append(cur); cur = w_
    if cur: lines.append(cur)
    return lines


def paragraph(cr, s, x, y, max_w, line_h, color=INK, alpha=1.0, align='left'):
    lines = wrap(cr, s, max_w)
    for i, ln in enumerate(lines):
        text(cr, ln, x, y + i * line_h, color, alpha, align)
    return len(lines)


def eyebrow(cr, s, x, y, color=AMBER, alpha=1.0, align="left", size=30):
    font(cr, TEXT, size, bold=True)
    return text(cr, s.upper(), x, y, color, alpha, align, tracking=size * 0.18)


def rule(cr, x0, y, x1, color=AMBER, alpha=1.0, width=3):
    cr.set_source_rgba(*color, alpha); cr.set_line_width(width)
    cr.move_to(x0, y); cr.line_to(x1, y); cr.stroke()


def circle(cr, x, y, r, color, alpha=1.0, fill=True, width=2):
    cr.new_sub_path(); cr.arc(x, y, r, 0, 2 * math.pi)
    cr.set_source_rgba(*color, alpha)
    if fill: cr.fill()
    else: cr.set_line_width(width); cr.stroke()


def pulse(cr, x, y, t, color=AMBER, r0=10, period=1.6, alpha=1.0):
    """A dot with an expanding ring."""
    ph = (t % period) / period
    circle(cr, x, y, r0 + 40 * ph, color, alpha * (1 - ph) * 0.8, fill=False, width=3)
    circle(cr, x, y, r0, color, alpha)


def arrow(cr, pts, color, alpha=1.0, width=6, head=22, progress=1.0):
    """Polyline arrow drawn up to `progress` of its length."""
    pts = np.asarray(pts, float)
    seg = np.hypot(*np.diff(pts, axis=0).T); L = seg.sum() * progress
    if L <= 1: return
    out = [pts[0]]; acc = 0
    for i, s in enumerate(seg):
        if acc + s >= L:
            f = (L - acc) / s; out.append(pts[i] + f * (pts[i + 1] - pts[i])); break
        out.append(pts[i + 1]); acc += s
    out = np.array(out)
    cr.set_source_rgba(*color, alpha); cr.set_line_width(width)
    cr.set_line_cap(cairo.LINE_CAP_ROUND); cr.set_line_join(cairo.LINE_JOIN_ROUND)
    cr.move_to(*out[0])
    for p in out[1:]: cr.line_to(*p)
    cr.stroke()
    d = out[-1] - out[-2]; ang = math.atan2(d[1], d[0])
    tip = out[-1]
    cr.move_to(*tip)
    cr.line_to(tip[0] - head * math.cos(ang - 0.45), tip[1] - head * math.sin(ang - 0.45))
    cr.line_to(tip[0] - head * math.cos(ang + 0.45), tip[1] - head * math.sin(ang + 0.45))
    cr.close_path(); cr.fill()


def to_array(surface):
    """cairo RGB24 surface -> HxWx3 uint8 RGB."""
    buf = np.ndarray((H, W, 4), np.uint8, surface.get_data())
    return buf[:, :, 2::-1].copy()


_GRAIN = None


def grain(frame, i, strength=7):
    """Light film grain so graphics sit with the photographs."""
    global _GRAIN
    if _GRAIN is None:
        rng = np.random.default_rng(7)
        _GRAIN = [rng.normal(0, 1, (H, W, 1)).astype(np.float32) for _ in range(4)]
    f = frame.astype(np.float32) + _GRAIN[i % 4] * strength
    return np.clip(f, 0, 255).astype(np.uint8)
