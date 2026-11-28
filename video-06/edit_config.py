# Edit settings for video 6, read by tools/edit/build.py (VIDEO=video-06).
GFX_SET = 'video6'
PALETTE = 'smith'       # November 1913: storm navy, frost-blue coasts, lamplight amber
FORMAT = 'casefile'     # dissolves, chapter titles over pictures, colour grade, grain, sound bed
GRADE = 'moody'         # darker than videos 4 and 5: a 1913 storm and a wreck in the dark
XFADE = 0.45
CAPTIONS = True
LT_POS = 'top'
WM_POS = 'top'
ACC, ACC2 = (1.0, 0.66, 0.23), (0.70, 0.86, 0.97)     # lamplight amber, frost blue

CHAPTERS = {
    2: 'The White Hurricane', 3: 'Three days in Marquette', 4: 'Thirty-two hatches', 5: 'Two clues',
    6: 'A hundred years', 7: 'North', 8: 'What the camera saw', 9: 'Three suspects', 10: 'Your verdict',
}
CHAPTER_SKIP = set()

# dramatic pauses: (section, words that end the line, extra seconds)
PAUSES = [
    (1, 'broken in two', 0.7), (1, 'a hundred years', 0.7), (1, 'and then she vanished', 1.0),
    (1, 'somewhere else entirely', 0.6),
    (2, 'the white hurricane', 0.5), (2, 'had already changed', 0.4), (2, 'history of the great lakes', 0.6),
    (3, 'the story has never gone away', 0.6), (3, 'the wind dropped', 0.5), (3, "didn't wait", 0.4),
    (4, 'the first real clue', 0.4), (4, 'normally took hours', 0.4), (4, 'with its full force', 0.8),
    (4, 'it was a gap', 0.5), (4, 'she was gone', 0.9), (4, 'it matters later', 0.6),
    (5, 'laughing fish point', 0.5), (5, 'were ever found', 0.8), (5, 'twelve miles east of marquette', 0.6),
    (5, 'east again', 0.4), (5, 'it was a fake', 0.6),
    (6, 'kept her secret', 0.6), (6, 'in the dark waiting', 0.6),
    (7, 'there she was', 0.9), (7, 'north of marquette', 0.5), (7, 'you were right', 0.6), (7, "couldn't prove it was her", 0.4),
    (8, 'read her name henry b smith', 0.8), (8, 'carrying that night', 0.6), (8, 'and she never made it', 0.7),
    (9, 'three suspects', 0.5), (9, 'she broke near the middle', 0.7), (9, 'it was gone', 0.9), (9, 'able to settle it', 0.6),
    (10, 'i read every single one', 0.5), (10, 'nobody even knew where it was', 0.9), (10, 'never been found', 0.6),
]

# name captions on the pictures, keyed by image number (the scenes are AI illustrations, so no claim that they
# show the real people or the real ship)
LOWER_THIRDS = {
    1: ('24 May 2013', 'Lake Superior, north of Marquette'),
    3: ('Henry B. Smith', 'Steel ore freighter · 1906'),
    13: ('L. C. Waldo', 'Lake Superior · 8 Nov 1913'),
    19: ('Marquette, Michigan', 'The ore dock · November 1913'),
    21: ('Capt. James Owen', 'Henry B. Smith · 1913'),
    32: ('East of Marquette', 'Wreckage on the beaches · 11 Nov 1913'),
    35: ('The note in a bottle', 'Found June 1914'),
    44: ('24 May 2013', 'Lake Superior'),
    48: ('Henry B. Smith', '535 feet down · June 2013'),
}

# camera moves for reused pictures: description keyword -> (focus x, focus y, zoom start, zoom end)
REUSE_FOCUS = [
    ("the bottle at the water's edge again", (0.50, 0.55, 1.20, 1.35)), ('the watchers on the breakwater again', (0.55, 0.45, 1.15, 1.28)),
    ('the wreckage on the beach again', (0.45, 0.60, 1.18, 1.32)), ('the captain on the bridge wing again', (0.50, 0.40, 1.15, 1.30)),
    ('the lull over the harbour again', (0.55, 0.45, 1.12, 1.24)), ('the smith steaming out of the harbour again', (0.50, 0.50, 1.15, 1.28)),
    ('the smith waiting at the ore dock again', (0.60, 0.50, 1.18, 1.30)), ('the open lake from above again', (0.55, 0.50, 1.10, 1.22)),
    ('the smith in the storm again', (0.45, 0.50, 1.18, 1.32)), ('the planks and hatch cover on the beach again', (0.50, 0.60, 1.15, 1.28)),
    ('the faint ship in the dark water again', (0.50, 0.60, 1.10, 1.25)), ('the snow squall racing toward the ship again', (0.55, 0.50, 1.12, 1.26)),
    ('ore freighter at night in a snowstorm', (0.50, 0.50, 1.04, 1.16)), ('the rusted bow of a huge ship', (0.50, 0.50, 1.05, 1.18)),
    ('the upturned stern', (0.50, 0.50, 1.05, 1.18)),
]

# what viewers read: spoken words -> shown text (captions and the .srt). Matched on whole words, any case.
DISPLAY = [
    ('the twenty-fourth of May, twenty thirteen', 'May 24, 2013'), ('thirty miles', '30 miles'),
    ('Five hundred and thirty-five feet', '535 feet'), ('a hundred years', '100 years'), ('nineteen thirteen', '1913'),
    ('twenty-five men', '25 men'), ('Twenty minutes', '20 minutes'), ('sixty-two years', '62 years'),
    ('the seventh of November', 'November 7'), ('ninety miles an hour', '90 miles an hour'), ('thirty-five feet', '35 feet'),
    ('two hundred and fifty people', '250 people'), ('nineteen ships', '19 ships'), ('the ninth of November', 'November 9'),
    ('Five hundred and forty-five feet', '545 feet'), ('nineteen-oh-six', '1906'), ('the sixth of November', 'November 6'),
    ('thirty-two miles an hour', '32 miles an hour'), ('thirty-two hatches', '32 hatches'),
    ('seventy miles an hour', '70 miles an hour'), ('June of nineteen fourteen', 'June 1914'), ('seven months', '7 months'),
    ('twelve miles', '12 miles'), ('the twelfth of November', 'November 12'), ('nineteen seventy-five', '1975'),
    ('all twenty-nine men', 'all 29 men'), ('twenty years', '20 years'), ('three days', '3 days'), ('two days', '2 days'), ('five hundred feet long', '500 feet long'),
]

# sound: extra hits on graphics (seconds after the graphic starts)
SOUND = dict(
    boom={'G02': [0.1], 'G04': [0.1], 'G11': [0.1], 'G13': [0.1], 'G25': [0.1], 'G28': ['half'], 'G36': ['half'],
          'G41': ['half'], 'G20': [0.2]},
    ping={'G03': [0.1, 1.0], 'G22': [1.8], 'G24': [0.5], 'G35': [0.9], 'G38': [1.3]},
    click={'G08': [2.0, 2.5], 'G51': [2.0, 2.5], 'G37': [1.4]},
    bell={'G50': [0.2]},
)
