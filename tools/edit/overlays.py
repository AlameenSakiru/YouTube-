"""Burned-in captions and the depth meter (video 4 onward).

Captions: short chunks of 1 to 5 words at the bottom of the frame. Each word pops in as it is spoken and the word being
spoken is highlighted. Numbers and names are shown the way viewers read them ("295 feet", "Mackinac").
Depth meter: a gauge on the right that shows the water level falling as the Straits are "drained", then rising again.
"""
import re, math
import numpy as np
import cairo

W, H = 1920, 1080
CAP_FONT = 'Inter Display Black'
YELLOW = (1.0, 0.82, 0.24)
WHITE = (1.0, 1.0, 1.0)
BLUE = (0.31, 0.76, 0.97)


def toks(s):
    return re.sub(r"[^a-z' ]", ' ', s.lower().replace('-', ' ')).split()


def norm(s):
    return ' '.join(toks(s))


# ------------------------------------------------------------------ caption track
def caption_words(tl, sections_text, al, shift, display):
    """Display words with their start times on the final timeline.

    display: list of (spoken phrase, shown text), e.g. ("two hundred and ninety-five feet", "295 feet").
    Phrases are matched on whole words, ignoring case and punctuation; the shown text keeps the punctuation
    that followed the last spoken word.
    """
    out = []
    rules = sorted(((norm(a).split(), b) for a, b in display), key=lambda r: -len(r[0]))
    for s in tl['sections']:
        sec = s['sec']; starts = al[str(sec)]['start']
        raw = ' '.join(sections_text[sec - 1]['paras']).replace('...', '… ').split()
        k = 0          # index into the aligned tokens
        i = 0
        while i < len(raw):
            # try a display rule starting here
            hit = None
            for pat, shown in rules:
                n, acc, j = 0, [], i
                while j < len(raw) and len(acc) < len(pat):
                    acc += toks(raw[j]); j += 1
                if acc == pat:
                    tail = re.sub(r"^.*?([.,!?;:”\"…]*)$", r"\1", raw[j - 1])
                    hit = (shown + tail, j, len(pat)); break
            if hit:
                text, j, nt = hit
            else:
                text, j, nt = raw[i], i + 1, len(toks(raw[i]))
            t0 = starts[min(k, len(starts) - 1)]
            T = shift(tl['sections'], sec, t0, k)
            out.append(dict(T=T, text=text, sec=sec, end=text.rstrip('”"').endswith(('.', '?', '!', '…'))))
            k += nt; i = j
    return out


def caption_chunks(words, max_words=4, max_chars=26):
    chunks, cur = [], []
    for w in words:
        if cur and (len(cur) >= max_words or len(' '.join(x['text'] for x in cur + [w])) > max_chars or w['sec'] != cur[-1]['sec']):
            chunks.append(cur); cur = []
        cur.append(w)
        if w['end'] or w['text'].endswith(','):
            chunks.append(cur); cur = []
    if cur: chunks.append(cur)
    res = []
    for i, c in enumerate(chunks):
        nxt = chunks[i + 1][0]['T'] if i + 1 < len(chunks) else c[-1]['T'] + 1.5
        end = min(nxt, c[-1]['T'] + 1.6)
        res.append(dict(T0=c[0]['T'] - 0.05, T1=end, words=c))
    return res


class Captions:
    def __init__(self, chunks, hide=()):
        self.chunks = chunks; self.hide = hide
        self.starts = [c['T0'] for c in chunks]

    def at(self, T):
        import bisect
        k = bisect.bisect_right(self.starts, T) - 1
        if k < 0: return None
        c = self.chunks[k]
        if T > c['T1']: return None
        for a, b in self.hide:
            if a <= T <= b: return None
        return c

    def draw(self, cr, T, y=H - 128, size=68):
        c = self.at(T)
        if c is None: return
        cr.select_font_face(CAP_FONT, 0, 0); cr.set_font_size(size)
        sp = cr.text_extents(' ').x_advance + size * 0.24     # wide gaps: the black outline would otherwise close them
        segs = [w['text'].split(' ') for w in c['words']]       # "9,000 years" is one timed word but two printed ones
        segw = [[cr.text_extents(p).x_advance for p in sg] for sg in segs]
        widths = [sum(ws) + sp * (len(ws) - 1) for ws in segw]
        total = sum(widths) + sp * (len(widths) - 1)
        x = (W - total) / 2
        # soft band behind the words for readability on bright pictures
        g = cairo.LinearGradient(0, y - 120, 0, H)
        g.add_color_stop_rgba(0, 0, 0, 0, 0); g.add_color_stop_rgba(0.55, 0, 0, 0, 0.38); g.add_color_stop_rgba(1, 0, 0, 0, 0.5)
        cr.set_source(g); cr.rectangle(0, y - 120, W, H - (y - 120)); cr.fill()
        cur_k = max([i for i, w in enumerate(c['words']) if w['T'] <= T] or [0])
        for i, (w, wd) in enumerate(zip(c['words'], widths)):
            age = T - w['T']
            pop = 1.0 + 0.06 * max(0.0, 1 - age / 0.18) if 0 <= age < 0.18 else 1.0
            col = YELLOW if (i == cur_k and age >= -0.02) else WHITE
            cr.save(); cr.translate(x + wd / 2, y - size * 0.35); cr.scale(pop, pop); cr.translate(-(x + wd / 2), -(y - size * 0.35))
            xx = x
            for part, pw in zip(segs[i], segw[i]):
                cr.move_to(xx + 4, y + 5); cr.text_path(part); cr.set_source_rgba(0, 0, 0, 0.55); cr.fill()
                cr.move_to(xx, y); cr.text_path(part)
                cr.set_source_rgba(0, 0, 0, 0.95); cr.set_line_width(size * 0.16); cr.set_line_join(cairo.LINE_JOIN_ROUND); cr.stroke_preserve()
                cr.set_source_rgb(*col); cr.fill()
                xx += pw + sp
            cr.restore()
            x += wd + sp


# ------------------------------------------------------------------ depth meter
class Depth:
    """keys: list of (T, depth, ramp seconds). Shown between show_from and show_to."""
    def __init__(self, keys, show_from, show_to, max_depth=295, hide=()):
        self.keys = sorted(keys); self.a = show_from; self.b = show_to; self.max = max_depth; self.hide = hide

    def value(self, T):
        v = 0.0
        for t0, d, ramp in self.keys:
            if T <= t0: break
            f = min(1.0, (T - t0) / max(ramp, 0.01)); f = f * f * (3 - 2 * f)
            v = v + (d - v) * f
        return v

    def alpha(self, T):
        k = min(1, max(0, (T - self.a) / 0.6)) * min(1, max(0, (self.b - T) / 0.6))
        for h0, h1 in self.hide:
            if h0 - 0.4 < T < h1 + 0.4:
                k *= 1 - min(1, max(0, (T - (h0 - 0.4)) / 0.4)) * min(1, max(0, ((h1 + 0.4) - T) / 0.4))
        return k

    def draw(self, cr, T):
        a = self.alpha(T)
        if a <= 0: return
        v = self.value(T)
        x0, y0, w, h = W - 150, 300, 34, 430
        cr.save()
        # panel
        cr.set_source_rgba(0, 0.03, 0.05, 0.55 * a)
        rr(cr, x0 - 52, y0 - 92, w + 104, h + 150, 14); cr.fill()
        cr.select_font_face('JetBrains Mono', 0, 1); cr.set_font_size(17)
        label = 'WATER LEVEL'
        cr.set_source_rgba(*BLUE, 0.95 * a); cr.move_to(x0 + w / 2 - cr.text_extents(label).x_advance / 2, y0 - 60); cr.show_text(label)
        cr.select_font_face(CAP_FONT, 0, 0); cr.set_font_size(40)
        s = '0 FT' if v < 0.5 else '−%d FT' % round(v)
        cr.set_source_rgba(*YELLOW, a); cr.move_to(x0 + w / 2 - cr.text_extents(s).x_advance / 2, y0 - 18); cr.show_text(s)
        # tube
        rr(cr, x0, y0, w, h, w / 2); cr.set_source_rgba(1, 1, 1, 0.12 * a); cr.fill_preserve()
        cr.set_source_rgba(1, 1, 1, 0.7 * a); cr.set_line_width(2.5); cr.stroke()
        fill = 1 - v / self.max
        fh = max(0.0, (h - 8) * fill)
        if fh > 1:
            g = cairo.LinearGradient(0, y0 + h - fh, 0, y0 + h)
            g.add_color_stop_rgba(0, *BLUE, 0.95 * a); g.add_color_stop_rgba(1, 0.08, 0.32, 0.55, 0.95 * a)
            cr.set_source(g); rr(cr, x0 + 4, y0 + h - 4 - fh, w - 8, fh, (w - 8) / 2); cr.fill()
        # ticks
        cr.select_font_face('JetBrains Mono', 0, 0); cr.set_font_size(15)
        for d in (0, 100, 200, 295):
            yy = y0 + 4 + (h - 8) * d / self.max
            cr.set_source_rgba(1, 1, 1, 0.75 * a); cr.set_line_width(2)
            cr.move_to(x0 - 10, yy); cr.line_to(x0, yy); cr.stroke()
            t = '%d' % d
            cr.move_to(x0 - 16 - cr.text_extents(t).x_advance, yy + 5); cr.show_text(t)
        cr.restore()


def rr(cr, x, y, w, h, r):
    cr.new_sub_path()
    cr.arc(x + w - r, y + r, r, -math.pi / 2, 0); cr.arc(x + w - r, y + h - r, r, 0, math.pi / 2)
    cr.arc(x + r, y + h - r, r, math.pi / 2, math.pi); cr.arc(x + r, y + r, r, math.pi, 1.5 * math.pi); cr.close_path()


# ------------------------------------------------------------------ compositing
def composite(a, draw_fns, T, box=(0, 0, W, H)):
    """Draw cairo overlays for time T onto float RGB frame a (in place) inside box (x0, y0, x1, y1)."""
    x0, y0, x1, y1 = box
    ww, hh = x1 - x0, y1 - y0
    s = cairo.ImageSurface(cairo.FORMAT_ARGB32, ww, hh); cr = cairo.Context(s)
    cr.translate(-x0, -y0)
    for fn in draw_fns: fn(cr, T)
    s.flush()
    st = s.get_stride()
    buf = np.ndarray((hh, st // 4, 4), np.uint8, s.get_data())[:, :ww]
    al = buf[:, :, 3:4].astype(np.float32) / 255
    if al.max() == 0: return a
    rgb = buf[:, :, 2::-1].astype(np.float32)
    a[y0:y1, x0:x1] = a[y0:y1, x0:x1] * (1 - al) + rgb
    return a
