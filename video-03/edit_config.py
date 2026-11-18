# Edit settings for video 3, read by tools/edit/build.py (VIDEO=video-03).
GFX_SET = 'video3'
PALETTE = 'deep'        # deep blue-green, sonar cyan, ship-light orange, Inter Display Black and JetBrains Mono
FORMAT = 'casefile'     # dissolves, chapter titles over pictures, new captions, colour grade, film grain, sound bed
XFADE = 0.45

CHAPTERS = {
    2: 'The mountain nobody could see', 3: 'Gone in minutes', 4: 'Two warships', 5: 'The Fitzgerald',
    6: 'Make your guess', 7: 'Nine thirty in the morning', 8: 'The longest afternoon', 9: 'The case against the mountain',
    10: 'Still down there', 11: 'Your verdict',
}
CHAPTER_SKIP = set()

# dramatic pauses: (section, words that end the line, extra seconds)
PAUSES = [
    (1, 'we are holding our own', 0.9), (1, 'the fitzgerald was gone', 0.5), (1, 'twenty one feet below the surface', 0.6),
    (1, 'twenty five feet deep in the water', 0.9), (1, "she wasn't the first ship it took", 0.8),
    (2, 'while the mountain was still a secret', 0.6),
    (3, 'and she was gone', 1.0), (3, "it wasn't true", 0.5), (3, 'no bodies', 0.6), (3, 'a ghost ship', 0.6),
    (3, 'on no chart at all', 0.6),
    (4, 'did not', 0.6), (4, 'not a plank', 0.8), (4, "it wasn't", 1.2),
    (5, 'toward the mountain', 0.8),
    (6, "and then there's the mountain", 0.9), (6, 'changes everything', 0.6),
    (7, 'about twenty five feet deep', 0.8), (7, 'water was getting in', 0.8),
    (8, 'she was blind', 0.4), (8, 'we are holding our own', 1.2), (8, 'then nothing', 1.8),
    (9, "and it's a real one", 0.4), (9, 'would no one have felt it', 0.8), (9, 'it was in the middle', 0.6),
    (9, 'about two hundred feet of her middle is missing', 1.0), (9, "that's where it is", 1.0),
    (10, "it's a grave", 1.0), (10, 'once for each man', 1.6),
    (11, 'nobody knew it was there', 1.0), (11, 'i read every one', 0.4),
]

# name captions on the pictures (the scenes are AI illustrations, so no claim that they show the real people)
LOWER_THIRDS = {
    2: ('Capt. Ernest McSorley', 'Edmund Fitzgerald · 10 Nov 1975'),
    18: ('U.S. Lake Survey', 'Charts Superior Shoal · 1929'),
    21: ('Capt. George Wood', 'The Bannockburn · 1902'),
    23: ('Capt. James McMaugh', 'The Algonquin · about noon'),
    33: ('Fort William, Ontario', '1918 · now Thunder Bay'),
    41: ('Launched 1958', 'Biggest ship on the Great Lakes'),
    45: ('Fitzgerald and Arthur M. Anderson', '9 Nov 1975 · late afternoon'),
    50: ('Paul Hainault', 'Retired professor · Michigan Tech'),
    54: ('The Soo Locks', '10 Nov 1975 · the seiche'),
    63: ('Whitefish Point', 'Radio beacon off'),
    66: ('Arthur M. Anderson', 'About 6:30 p.m.'),
    70: ('1994 expedition', '530 feet down'),
    79: ('The Fitzgerald\'s bell', 'Raised 1995 · Whitefish Point'),
    80: ('Mariners\' Church, Detroit', '29 rings, the day after'),
}

REUSE_FOCUS = [
    ('the lava ridge again', (0.55, 0.55, 1.25, 1.40)), ('the freighter in the storm again', (0.35, 0.55, 1.30, 1.42)),
    ('closer on the storm', (0.60, 0.45, 1.30, 1.45)), ('closer on the life jacket', (0.55, 0.62, 1.45, 1.60)),
    ('the wave over the hatches again', (0.55, 0.50, 1.25, 1.40)), ('the wreck again', (0.45, 0.50, 1.25, 1.40)),
    ('the bow in the dark again', (0.50, 0.45, 1.20, 1.35)), ('the ship over the peak again', (0.50, 0.55, 1.20, 1.35)),
    ('open lake superior again', (0.50, 0.60, 1.10, 1.22)), ('the listing freighter again', (0.45, 0.55, 1.30, 1.45)),
    ('a single light fading', (0.62, 0.40, 1.35, 1.55)), ('the torn middle again', (0.45, 0.55, 1.30, 1.50)),
    ('lake trout again', (0.55, 0.55, 1.25, 1.40)), ('closer on the bell', (0.30, 0.55, 1.50, 1.65)),
    ('aerial lake again', (0.50, 0.60, 1.20, 1.32)),
]

# subtitle spellings: what the AI voice was given -> what viewers should read
DISPLAY = [
    ('saysh', 'seiche'), ('Saysh', 'Seiche'), ('Sault Sainte Marie', 'Sault Ste. Marie'),
    ('seven hundred and twenty-nine feet', '729 feet'), ('five hundred and thirty feet', '530 feet'),
    ('two hundred and seventy-six feet', '276 feet'), ('two hundred and fifty-three', '253'),
    ('a hundred and thirty-five feet', '135 feet'), ('eighty-five thousand', '85,000'),
    ('twenty-six thousand tons', '26,000 tons'), ('nineteen seventy-five', '1975'), ('nineteen-oh-two', '1902'),
    ('nineteen eighteen', '1918'), ('nineteen twenty-nine', '1929'), ('nineteen fifty-eight', '1958'),
    ('nineteen ninety-four', '1994'), ('nineteen ninety-five', '1995'), ('eighteen forty-four', '1844'),
    ('November the twenty-first', 'November 21'), ('November the tenth', 'November 10'), ('November the ninth', 'November 9'),
    ('the twenty-fourth', 'the 24th'), ('twenty-one feet', '21 feet'), ('twenty-five feet', '25 feet'),
    ('two hundred feet', '200 feet'), ('twenty-nine', '29'), ('Twenty-nine', '29'), ('Seventy-eight', '78'),
    ('seventy-eight', '78'), ('fifty miles', '50 miles'), ('twenty square miles', '20 square miles'),
    ('forty miles', '40 miles'), ('seven miles', '7 miles'), ('sixteen miles', '16 miles'), ('fifty knots', '50 knots'),
    ('thirty to thirty-five feet', '30 to 35 feet'), ('nine thirty', '9:30'), ('three thirty', '3:30'),
    ('six thirty', '6:30'), ('a hundred miles', '100 miles'), ('three feet', '3 feet'),
]
