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
    # Video 3: deep water and sonar. Blue-green black, cold cyan coasts, ship-light orange, heavy display type.
    'deep': dict(
        BG=(0x05, 0x12, 0x17), BG2=(0x0B, 0x24, 0x2D), LAND=(0x0A, 0x16, 0x1B), WATER=(0x0F, 0x36, 0x42),
        WATER_HI=(0x18, 0x50, 0x5F), COAST=(0x5F, 0xC4, 0xC8), BORDER=(0x17, 0x2C, 0x33), INK=(0xEC, 0xF3, 0xF2),
        MUTED=(0x9C, 0xB9, 0xBC), DIM=(0x5A, 0x78, 0x7E), AMBER=(0xFF, 0x8A, 0x3D), STORM=(0x7F, 0xA6, 0xAE),
        RED=(0xFF, 0x5A, 0x3C), DISPLAY='Inter Display', TEXT='Inter',
    ),
    # Video 4: brighter. Clear lake blue, sky-blue coasts, gold highlights.
    'drain': dict(
        BG=(0x06, 0x13, 0x1B), BG2=(0x0C, 0x26, 0x33), LAND=(0x15, 0x1F, 0x21), WATER=(0x14, 0x4C, 0x68),
        WATER_HI=(0x1F, 0x66, 0x86), COAST=(0x8C, 0xD9, 0xF2), BORDER=(0x24, 0x35, 0x3A), INK=(0xF2, 0xF6, 0xF6),
        MUTED=(0xAA, 0xC2, 0xC8), DIM=(0x5E, 0x7A, 0x82), AMBER=(0xFF, 0xC9, 0x3C), STORM=(0x86, 0xAA, 0xB4),
        RED=(0xFF, 0x5C, 0x42), DISPLAY='Inter Display', TEXT='Inter',
    ),
    # Video 5: Lake Superior in November. Slate blue, ice-blue coasts, signal orange.
    'superior': dict(
        BG=(0x07, 0x0D, 0x16), BG2=(0x0F, 0x1C, 0x2A), LAND=(0x17, 0x1D, 0x24), WATER=(0x16, 0x3D, 0x5A),
        WATER_HI=(0x20, 0x55, 0x78), COAST=(0xA6, 0xD8, 0xF5), BORDER=(0x26, 0x31, 0x3D), INK=(0xF2, 0xF5, 0xF8),
        MUTED=(0xAE, 0xBE, 0xCC), DIM=(0x60, 0x72, 0x84), AMBER=(0xFF, 0x73, 0x42), STORM=(0x8A, 0xA4, 0xB8),
        RED=(0xFF, 0x54, 0x4D), DISPLAY='Inter Display', TEXT='Inter',
    ),
}

MODULES = ('style', 'maps', 'graphics', 'graphics_more', 'video2', 'video3', 'video4', 'video5', 'render')


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
