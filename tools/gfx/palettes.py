"""Colour and type styles for the graphics. Video 1 uses the defaults in style.py.

apply(name) swaps the colours and fonts in every graphics module that is loaded, and in style.py
so modules loaded afterwards pick them up too.
"""
import sys

PALETTES = {
    # Video 2: a storm warning on Lake Erie. Lake green-black, teal water, signal red, newspaper serif.
    'storm': dict(
        BG=(0x0B, 0x17, 0x18), BG2=(0x15, 0x28, 0x2A), LAND=(0x1B, 0x28, 0x26), WATER=(0x1E, 0x4B, 0x50),
        WATER_HI=(0x2E, 0x6A, 0x70), COAST=(0x79, 0xA3, 0xA3), BORDER=(0x2C, 0x3F, 0x3D), INK=(0xF2, 0xED, 0xE3),
        MUTED=(0xA2, 0xB5, 0xB2), DIM=(0x6C, 0x83, 0x80), AMBER=(0xE0, 0x4E, 0x39), STORM=(0x93, 0xA6, 0xA4),
        RED=(0xE0, 0x4E, 0x39), DISPLAY='Bitstream Charter', TEXT='Bitstream Charter',
    ),
}

MODULES = ('style', 'maps', 'graphics', 'graphics_more', 'video2', 'render')


_ORIGINAL = None


def apply(name):
    """Swap module-level colours and fonts, and the same values used as default arguments of functions."""
    global _ORIGINAL
    import types
    style = sys.modules.get('style') or __import__('style')
    p = PALETTES[name]
    vals = {k: (tuple(c / 255 for c in v) if isinstance(v, tuple) else v) for k, v in p.items()}
    if _ORIGINAL is None:
        _ORIGINAL = {k: getattr(style, k) for k in vals if hasattr(style, k)}
    swap = {}
    for k, v in _ORIGINAL.items():
        if isinstance(v, tuple): swap[tuple(round(c, 4) for c in v)] = vals[k]
        else: swap[v] = vals[k]
    swap['Inter Display'] = vals.get('DISPLAY', 'Inter Display'); swap['Inter'] = vals.get('TEXT', 'Inter')

    def fix(x):
        if isinstance(x, tuple) and len(x) == 3 and all(isinstance(c, float) for c in x):
            return swap.get(tuple(round(c, 4) for c in x), x)
        if isinstance(x, str):
            return swap.get(x, x)
        return x

    for m in MODULES:
        mod = sys.modules.get(m)
        if mod is None:
            continue
        for k, v in vals.items():
            if hasattr(mod, k):
                setattr(mod, k, v)
        for f in list(vars(mod).values()):
            if isinstance(f, types.FunctionType) and f.__module__ == m:
                if f.__defaults__: f.__defaults__ = tuple(fix(x) for x in f.__defaults__)
                if f.__kwdefaults__: f.__kwdefaults__ = {a: fix(x) for a, x in f.__kwdefaults__.items()}
    return vals
