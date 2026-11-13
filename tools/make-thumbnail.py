"""Make a 1280x720 YouTube thumbnail: a picture, lifted for small screens, with two lines of text.

    python3 tools/make-thumbnail.py IMAGE OUT.jpg --big MIDNIGHT --small "BUFFALO, 1844" \
        [--crop x0,y0,x1,y1] [--pos top|right|left] [--palette storm] [--lift 1.25]
"""
import argparse, os, sys
import numpy as np
import cairo
from PIL import Image, ImageEnhance

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'gfx'))
import style  # noqa: E402

W, H = 1280, 720


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('image'); ap.add_argument('out')
    ap.add_argument('--big', required=True); ap.add_argument('--small', required=True)
    ap.add_argument('--crop'); ap.add_argument('--pos', default='top')
    ap.add_argument('--palette'); ap.add_argument('--lift', type=float, default=1.0)
    a = ap.parse_args()
    if a.palette:
        import palettes
        palettes.apply(a.palette)
    im = Image.open(a.image).convert('RGB')
    if a.crop: im = im.crop(tuple(int(v) for v in a.crop.split(',')))
    w, h = im.size
    if w / h > 16 / 9: nw = int(h * 16 / 9); im = im.crop(((w - nw) // 2, 0, (w - nw) // 2 + nw, h))
    else: nh = int(w * 9 / 16); im = im.crop((0, (h - nh) // 2, w, (h - nh) // 2 + nh))
    im = im.resize((W, H), Image.LANCZOS)
    if a.lift != 1.0:  # brighten the shadows and add contrast so night scenes read at phone size
        arr = np.asarray(im, np.float32) / 255
        arr = arr ** (1 / a.lift)
        im = Image.fromarray(np.clip(arr * 255, 0, 255).astype(np.uint8))
        im = ImageEnhance.Contrast(im).enhance(1.12)
        im = ImageEnhance.Color(im).enhance(1.1)
    rgba = np.dstack([np.asarray(im), np.full((H, W), 255, np.uint8)])
    s = cairo.ImageSurface.create_for_data(bytearray(rgba[:, :, [2, 1, 0, 3]].tobytes()), cairo.FORMAT_ARGB32, W, H)
    cr = cairo.Context(s)
    # darken behind the text
    if a.pos == 'top':
        g = cairo.LinearGradient(0, 0, 0, H * 0.55); g.add_color_stop_rgba(0, 0, 0, 0, 0.55); g.add_color_stop_rgba(1, 0, 0, 0, 0)
    else:
        x0, x1 = (W, W * 0.35) if a.pos == 'right' else (0, W * 0.65)
        g = cairo.LinearGradient(x0, 0, x1, 0); g.add_color_stop_rgba(0, 0, 0, 0, 0.6); g.add_color_stop_rgba(1, 0, 0, 0, 0)
    cr.set_source(g); cr.paint()

    def line(txt, size, color, y):
        cr.select_font_face(style.DISPLAY, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD); cr.set_font_size(size)
        e = cr.text_extents(txt)
        if a.pos == 'top': x = (W - e.x_advance) / 2
        elif a.pos == 'right': x = W - 60 - e.x_advance
        else: x = 60
        for dx, dy, al in ((7, 7, 0.55), (4, 4, 0.5)):
            cr.move_to(x + dx, y + dy); cr.set_source_rgba(0, 0, 0, al); cr.show_text(txt)
        cr.move_to(x, y); cr.text_path(txt); cr.set_source_rgba(0, 0, 0, 0.9); cr.set_line_width(size * 0.06); cr.stroke()
        cr.move_to(x, y); cr.set_source_rgb(*color); cr.show_text(txt)

    if a.pos == 'top':
        line(a.big, 170, style.AMBER, 205); line(a.small, 76, (1, 1, 1), 300)
    else:
        line(a.big, 150, style.AMBER, 320); line(a.small, 70, (1, 1, 1), 410)
    s.flush()
    out = np.ndarray((H, W, 4), np.uint8, s.get_data())[:, :, [2, 1, 0]]
    Image.fromarray(out.copy()).save(a.out, quality=92)
    print('wrote', a.out)


if __name__ == '__main__':
    main()
