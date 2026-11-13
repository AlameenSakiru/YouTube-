# Edit settings for video 2, read by tools/edit/build.py (VIDEO=video-02).
GFX_SET = 'video2'
PALETTE = 'storm'   # lake green-black, teal water, storm-warning red, Charter type

# dramatic pauses: (section, words that end the line, extra seconds)
PAUSES = [
    (1, 'and the lake came with it', 0.8), (1, 'seventy eight people were dead', 0.8), (1, 'last winter', 0.4),
    (2, 'it rocks', 0.5),
    (4, 'about four hundred passengers on board', 0.6),
    (5, 'the eastern end buffalo', 0.8), (5, 'from two to eight feet in depth', 0.6),
    (6, 'and floated it away', 0.7),
    (7, 'now burning the furniture', 1.0), (7, 'everyone on board was safe', 0.8),
    (8, 'seventy eight in all', 1.2), (8, 'never heard of it', 0.6),
    (9, 'waiting to come back', 0.6),
    (10, "the lake didn't", 0.8),
    (11, 'the bathtub had tilted again', 0.5),
    (12, 'it was only waiting', 0.8),
]

# name captions on 1844 reconstructions and a present-day view (no dates on modern AI images)
LOWER_THIRDS = {
    3: ('Buffalo, New York', 'October 18, 1844'),
    9: ('Buffalo, New York', 'The eastern end of Lake Erie'),
    12: ('Buffalo harbor', '1844'),
    21: ('The Julia Palmer', 'About 400 passengers'),
    29: ('Main Street, Buffalo', 'About midnight'),
    45: ('The steamboat Columbus', 'In a pasture, 200 feet from the creek'),
}

REUSE_FOCUS = [
    ('bathtub image again', (0.50, 0.50, 1.25, 1.40)),
    ('flooded lower town at night again', (0.45, 0.55, 1.30, 1.45)),
    ("video 1's image", (0.60, 0.50, 1.10, 1.25)),
    ('closer crop on the small wooden houses', (0.40, 0.55, 1.35, 1.50)),
    ('closer crop on the survivors', (0.50, 0.55, 1.35, 1.50)),
    ('push-in on the piled-up water', (0.50, 0.55, 1.20, 1.45)),
    ('closer crop on the flooded road', (0.45, 0.60, 1.35, 1.50)),
    ('push-in on the figure walking out', (0.50, 0.55, 1.25, 1.60)),
]

# subtitle spellings: what the AI voice was given -> what viewers should read
DISPLAY = [
    ('sayshes', 'seiches'), ('Sayshes', 'Seiches'), ('saysh', 'seiche'), ('Saysh', 'Seiche'),
    ('meteo-tsunami', 'meteotsunami'), ('Saint Louis', 'St. Louis'),
    ('November the fifteenth, twenty twenty', 'November 15, 2020'), ('December the twenty-ninth, twenty twenty-five', 'December 29, 2025'),
    ('October the eighteenth', 'October 18'), ('twenty twelve', '2012'),
    ('eighteen forty-four', '1844'), ('Eighteen forty-four', '1844'), ('eighteen twenty-five', '1825'),
    ('nineteen fifty-four', '1954'), ('eighteen-sixties', '1860s'),
    ('two hundred and forty miles', '240 miles'), ('about sixty feet', 'about 60 feet'), ('more than ten feet', 'more than 10 feet'),
    ('about four hundred passengers', 'about 400 passengers'), ('twenty-two feet', '22 feet'), ('two hundred feet', '200 feet'),
    ('More than eighty', 'More than 80'), ('more than two hundred', 'more than 200'), ('thirty-nine', '39'),
    ('fifty-three', '53'), ('twenty-five on the lake', '25 on the lake'), ('Seventy-eight', '78'), ('seventy-eight', '78'),
    ('fourteen feet', '14 feet'), ('fourteen hours', '14 hours'), ('sixty to eighty miles an hour', '60 to 80 miles an hour'),
]
