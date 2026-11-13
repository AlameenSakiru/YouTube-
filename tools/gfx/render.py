"""Render graphics to video clips, or to preview stills.

python3 render.py preview OUT.jpg G01 G02 ...     contact sheet of keyframes
python3 render.py clips PLAN.json OUTDIR [G..]   one ProRes-free H.264 clip per graphic, timed from the plan
"""
import sys, os, json, subprocess
from multiprocessing import Pool
import numpy as np
from PIL import Image
sys.path.insert(0, os.path.dirname(__file__))
from style import *
import graphics
import graphics_more
from PIL import Image as _I
_bg = os.path.join(os.path.dirname(__file__), '../../video-01/images/072.jpg')
if os.path.exists(_bg):
    _png = '/tmp/end-bg-072.png'
    if not os.path.exists(_png): _I.open(_bg).convert('RGB').resize((1920, 1080)).save(_png)
    graphics_more.END_BG = _png


GFX_SET = os.environ.get('GFX_SET', 'video1')
if GFX_SET == 'video2':
    import video2
    REG = video2.G
else:
    REG = graphics.G


def frame(gid, t, d, i=0):
    s, cr = new_surface()
    REG[gid](cr, t, d)
    s.flush()
    return grain(to_array(s), 0, 4)  # one still grain pattern: keeps the files small


def preview(out, gids, durs):
    tiles = []
    for gid in gids:
        d = durs.get(gid, 6.0)
        for f in (0.12, 0.5, 0.92):
            im = Image.fromarray(frame(gid, d * f, d)).resize((480, 270))
            tiles.append((gid, f, im))
    cols = 3; rows = len(gids)
    sheet = Image.new('RGB', (cols * 484, rows * 274), 'white')
    for k, (gid, f, im) in enumerate(tiles):
        sheet.paste(im, ((k % cols) * 484 + 2, (k // cols) * 274 + 2))
    sheet.save(out, quality=85)


def clip(args):
    gid, d, out = args
    n = int(round(d * FPS))
    p = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}',
                          '-r', str(FPS), '-i', '-', '-c:v', 'libx264', '-preset', 'medium', '-crf', '18',
                          '-pix_fmt', 'yuv420p', out], stdin=subprocess.PIPE)
    for i in range(n):
        p.stdin.write(frame(gid, i / FPS, d, i).tobytes())
    p.stdin.close(); p.wait()
    return gid, n


if __name__ == '__main__':
    mode = sys.argv[1]
    if mode == 'preview':
        out, gids = sys.argv[2], sys.argv[3:]
        plan = json.load(open(os.path.join(os.path.dirname(__file__), '../..', os.environ.get('VIDEO', 'video-01'), 'edit-plan.json')))
        durs = {s['gid']: s['d'] for s in plan if s['kind'] == 'G'}
        preview(out, gids, durs)
    elif mode == 'clips':
        plan = json.load(open(sys.argv[2])); outdir = sys.argv[3]; only = set(sys.argv[4:])
        os.makedirs(outdir, exist_ok=True)
        jobs = [(s['gid'], s['dur_final'] if 'dur_final' in s else s['d'], os.path.join(outdir, s['gid'] + '.mp4'))
                for s in plan if s['kind'] == 'G' and (not only or s['gid'] in only)]
        with Pool(4) as pool:
            for gid, n in pool.imap_unordered(clip, jobs):
                print(gid, n, 'frames', flush=True)
