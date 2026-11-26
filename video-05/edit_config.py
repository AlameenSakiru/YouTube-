# Edit settings for video 5, read by tools/edit/build.py (VIDEO=video-05).
GFX_SET = 'video5'
PALETTE = 'superior'    # Lake Superior in November: slate blue, ice-blue coasts, signal orange
FORMAT = 'casefile'     # dissolves, chapter titles over pictures, colour grade, grain, sound bed
GRADE = 'bright'
XFADE = 0.45
CAPTIONS = True
LT_POS = 'top'
WM_POS = 'top'
ACC, ACC2 = (1.0, 0.45, 0.26), (0.62, 0.86, 1.0)     # signal orange, ice blue

CHAPTERS = {
    2: 'Three killers', 3: 'Twenty feet', 4: 'Fifty feet', 5: 'A hundred feet', 6: 'Two hundred feet',
    7: 'Two hundred and seventy feet', 8: 'Five hundred and thirty feet', 9: 'Her own hull', 10: 'Let the water back',
    11: 'Your verdict',
}
CHAPTER_SKIP = set()

# dramatic pauses: (section, words that end the line, extra seconds)
PAUSES = [
    (1, 'seventeen miles', 0.5), (1, 'just over an hour', 0.5), (1, 'we are holding our own', 0.8),
    (1, 'twenty nine men', 1.0), (1, "so let's drain it", 0.7), (1, 'every one of those killers was waiting for her', 0.6),
    (2, 'three things kill them here', 0.6), (2, 'she seldom gives up her dead', 0.6), (2, "let's start the drain", 0.6),
    (3, 'seven men died the storm', 0.6), (3, 'not every crew here was that lucky', 0.6),
    (4, 'her name is the myron', 0.5), (4, 'she sank in four minutes', 0.9), (4, 'he was the only survivor', 0.9),
    (4, 'called mission hill', 0.6),
    (5, 'one of the lucky ones', 0.4), (5, 'the dark becomes the killer', 0.7),
    (6, 'the comet', 0.6), (6, 'ten men died', 0.7), (6, 'is still unknown', 0.8),
    (7, 'twenty nine people died', 0.8), (7, 'remember that number twenty nine', 1.0),
    (8, 'she appears', 0.6), (8, 'the edmund fitzgerald', 0.9), (8, "he learned it wasn't working", 0.6),
    (8, 'the lake kept them all', 0.9), (8, 'fifty five years earlier', 0.6),
    (9, 'the ship herself', 0.6), (9, 'was not seaworthy', 0.9), (9, "she's a grave", 1.2),
    (10, 'now let the water back in', 0.5), (10, 'the same way again', 0.6),
    (11, 'carrying more than she was built for', 0.6),
]

# name captions on the pictures, keyed by the first words of the line the shot starts on
# (the scenes are AI illustrations, so no claim that they show the real people)
LOWER_THIRDS = {
    'twenty feet just west of the': ('Whitefish Point Light', 'First lit 1849'),
    'in november eighteen seventy two': ('The Saturn', 'Schooner barge · 27 Nov 1872'),
    'and the lifesaving crew from': ('Vermilion Point', 'Life-Saving Station · 1913'),
    'on the twenty second of november': ('Munising, Michigan', '22 November 1919'),
    'her captain was still inside the': ('Capt. Walter Neal', 'Myron · 23 Nov 1919'),
    'people from the towns around the': ('Mission Hill Cemetery', 'Bay Mills Township, Michigan'),
    'in september eighteen eighty seven she': ('The Niagara', 'Schooner barge · 7 Sep 1887'),
    'she sank in eighteen seventy three': ('The Vienna', 'Wooden steamer · 1873'),
    'on a clear starlit night in': ('The Comet', 'Wooden steamer · 26 Aug 1875'),
    'the canadian steamer manitoba struck her': ('The Manitoba', 'Canadian steamer'),
    'when she was launched in eighteen': ('Superior City', 'Launched 1898 · Lorain, Ohio'),
    'in the dark another freighter the': ('Willis L. King', 'Upbound, empty'),
    'her steward who sailed on her': ('George "Red" Burgner', 'Steward · ten seasons'),
    'and one of the engineers who': ('Raymond Ramsay', 'Naval architect · her hull design team'),
    'stories from people like you are': ('Great Lakes Shipwreck Museum', 'Whitefish Point'),
}

# camera moves for reused pictures: description keyword -> (focus x, focus y, zoom start, zoom end)
REUSE_FOCUS = [
    ('the drained graveyard again', (0.50, 0.55, 1.18, 1.32)), ('the lighthouse at dusk again', (0.55, 0.45, 1.15, 1.28)),
    ('the lighthouse above the lowered water again', (0.52, 0.45, 1.25, 1.38)),
    ("the clear-water wreck in a diver's light again", (0.45, 0.50, 1.30, 1.45)),
    ('the calm lighthouse at dawn again', (0.50, 0.45, 1.10, 1.22)),
    ('ore freighter at night in a snowstorm', (0.50, 0.50, 1.04, 1.16)), ('inside a 1970s pilothouse', (0.50, 0.50, 1.05, 1.15)),
    ('empty storm-tossed lake', (0.50, 0.50, 1.02, 1.12)), ('the rusted bow of a huge ship', (0.50, 0.50, 1.05, 1.18)),
    ('from a pilothouse window', (0.50, 0.50, 1.04, 1.14)), ('emerging from fog', (0.50, 0.50, 1.04, 1.16)),
    ('huge waves in darkness', (0.50, 0.50, 1.04, 1.14)), ('a dead radar screen', (0.50, 0.50, 1.05, 1.18)),
    ('a lighthouse on a point in a night storm', (0.50, 0.45, 1.04, 1.16)), ('a giant wave crashing', (0.50, 0.50, 1.04, 1.15)),
    ('the upturned stern', (0.50, 0.50, 1.05, 1.18)), ('a heap of ore pellets', (0.50, 0.50, 1.05, 1.18)),
    ("a polished bronze ship's bell", (0.50, 0.45, 1.05, 1.20)), ("waves pouring over a freighter's deck", (0.50, 0.50, 1.04, 1.16)),
]

# what viewers read: spoken words -> shown text (captions and the .srt). Matched on whole words, any case.
DISPLAY = [
    ('seventeen miles', '17 miles'), ('two hundred and forty ships', '240 ships'), ('seventy tons', '70 tons'),
    ('twenty hours', '20 hours'), ('five hundred and thirty feet', '530 feet'), ('two hundred years', '200 years'),
    ('a hundred and sixty miles', '160 miles'), ('thirty feet', '30 feet'), ('Twenty feet', '20 feet'),
    ('eighteen forty-nine', '1849'), ('November, eighteen seventy-two', 'November 1872'), ('Seven men died', '7 men died'),
    ('nineteen thirteen', '1913'), ('fifty feet', '50 feet'), ('a mile and a half', '1.5 miles'),
    ('the twenty-second of November, nineteen nineteen', 'November 22, 1919'), ('sixty miles an hour', '60 miles an hour'),
    ('four minutes', '4 minutes'), ('All seventeen men', 'All 17 men'), ('all seven of her crew', 'all 7 of her crew'),
    ('A hundred feet', '100 feet'), ('Seven miles', '7 miles'), ('September, eighteen eighty-seven', 'September 1887'),
    ('All nine people', 'All 9 people'), ('a hundred and twenty feet', '120 feet'), ('eighteen seventy-three', '1873'),
    ('Three hundred and seventy-six square miles', '376 square miles'), ('two hundred feet', '200 feet'),
    ('July, nineteen-oh-nine', 'July 1909'), ('Fourteen of her twenty-four crew', '14 of her 24 crew'),
    ('August, eighteen seventy-five', 'August 1875'), ('Ten men died', '10 men died'), ('five hundred tons', '500 tons'),
    ('eighteen seventy-six', '1876'), ('nineteen thirty-eight', '1938'), ('nineteen seventies', '1970s'),
    ('two hundred and seventy feet', '270 feet'), ('eighteen ninety-eight', '1898'), ('ten past nine', '9:10'),
    ('the twentieth of August, nineteen twenty', 'August 20, 1920'), ('seven thousand six hundred tons', '7,600 tons'),
    ('Twenty-eight men', '28 men'), ('Only four survived', 'Only 4 survived'),
    ('Seven hundred and twenty-nine feet', '729 feet'), ('November the tenth, nineteen seventy-five', 'November 10, 1975'),
    ('thirty-five feet', '35 feet'), ('ten past seven', '7:10'), ('fifty-five years', '55 years'),
    ('nineteen sixty-nine, nineteen seventy-one and nineteen seventy-three', '1969, 1971 and 1973'),
    ('more than three feet', 'more than 3 feet'), ('eleven and a half feet', '11.5 feet'), ('ten seasons', '10 seasons'),
    ('seven winters', '7 winters'), ('the tenth of November, nineteen seventy-five', 'November 10, 1975'),
    ('a hundred and seventy feet', '170 feet'), ('nineteen ninety-five', '1995'), ('all twenty-nine men', 'all 29 men'),
    ('a hundred and seventy years', '170 years'), ('Twenty-nine', '29'),
]

# the depth meter: (section, words it starts on, depth in feet, seconds to get there)
DEPTH_MAX = 530
DEPTH_SHOW = ((2, "let's start the drain"), (10, 'tomorrow freighters will pass'))
DEPTH_KEYS = [
    (3, 'twenty feet', 20, 1.4), (3, 'thirty feet', 30, 1.4),
    (4, 'at fifty feet', 50, 1.6),
    (5, 'a hundred feet', 100, 2.0), (5, 'at a hundred and twenty feet', 120, 1.4),
    (6, 'as the water falls toward two', 200, 3.0),
    (7, 'below two hundred feet', 230, 2.0), (7, 'and at the deepest point', 270, 2.0),
    (8, 'now the water keeps falling', 530, 7.0),
    (10, 'lake superior rises over the fitzgerald', 300, 2.5), (10, 'the superior city disappears', 230, 1.6),
    (10, 'then the comet', 180, 1.4), (10, 'the cowle the vienna the niagara', 100, 2.0),
    (10, 'the myron and the miztec', 45, 1.6), (10, "then the saturn's broken timbers", 0, 2.6),
]
DEPTH_HIDE = {'G21', 'G22', 'G40'}     # the guess and the like ask use the full width

# sound: extra hits on graphics (seconds after the graphic starts)
SOUND = dict(
    boom={'G03': [0.1], 'G04': [0.1], 'G14': [0.6], 'G17': [0.1], 'G18': [0.8], 'G19': [2.0], 'G23': [0.1], 'G25': [0.1],
          'G28': [1.0], 'G32': [0.1], 'G33': [1.5], 'G34': [0.2], 'G36': [0.1], 'G38': [0.6], 'G39': [0.2, 3.6], 'G46': [0.5]},
    ping={'G01': [0.5, 1.2], 'G05': [0.4, 1.2, 2.0], 'G16': [0.2], 'G20': [0.4], 'G35': [1.2], 'G37': [1.8, 2.9, 4.0]},
    click={'G08': [1.2, 1.7], 'G40': [1.3, 3.2], 'G53': ['half', 'half+0.5']},
    bell={'G49': [0.2]},
)
