# Edit settings for video 4, read by tools/edit/build.py (VIDEO=video-04).
GFX_SET = 'video4'
PALETTE = 'drain'       # brighter than video 3: clear lake blue, sky-blue coasts, gold
FORMAT = 'casefile'     # dissolves, chapter titles over pictures, colour grade, grain, sound bed
GRADE = 'bright'        # lighter, cleaner, more colourful than video 3's moody grade
XFADE = 0.45
CAPTIONS = True         # burned-in captions, word by word, the spoken word highlighted
LT_POS = 'top'          # name captions top left (the bottom belongs to the captions)
WM_POS = 'top'          # channel name top right
ACC, ACC2 = (1.0, 0.79, 0.24), (0.31, 0.76, 0.97)     # gold, sky blue

CHAPTERS = {
    2: 'The drain begins', 3: 'Thirty-five feet', 4: 'Sixty-five feet', 5: 'The waterfall', 6: 'The graveyard',
    7: 'Two hundred and ten feet', 8: 'Two hundred and seventy feet', 9: 'The river', 10: 'Let the water back',
    11: 'Your call',
}
CHAPTER_SKIP = set()

# dramatic pauses: (section, words that end the line, extra seconds)
PAUSES = [
    (1, "so let's drain it", 0.7), (1, 'hundreds of miles of shoreline', 0.6),
    (2, "let's start the drain", 0.6), (2, 'divers call it the rock maze', 0.4), (2, 'something long is waiting', 0.8),
    (3, "the top of a ship's hull", 0.6), (3, 'neither did', 0.8), (3, 'and went down', 0.6),
    (3, 'ten of the thirty five men died', 1.0),
    (4, 'about these two pipes', 0.8),
    (5, 'in the middle of a lake', 0.5), (5, 'about a hundred feet high', 0.6), (5, 'the answer is at the very bottom', 0.8),
    (6, 'look like a graveyard', 0.5),
    (7, 'and five men', 0.9), (7, 'he died of the bends', 0.8), (7, 'was never recovered', 0.8), (7, 'was never found', 0.8),
    (8, 'the pipe held', 0.8),
    (9, "it's a canyon", 0.9), (9, 'mackinaw falls', 0.8), (9, 'people lived there', 0.8),
    (10, 'and the lake is calm again', 0.8),
    (11, 'or be shut down', 0.5),
]

# name captions on the pictures, keyed by the first words of the line the shot starts on
# (the scenes are AI illustrations, so no claim that they show the real people)
LOWER_THIRDS = {
    'divers call it the': ('The Rock Maze', 'Off Mackinac Island · 0–35 ft'),
    'the fog that morning was': ('Straits of Mackinac', '7 May 1965 · dense fog'),
    'came out of the fog': ('The Topdalsfjord', 'Norwegian freighter · bow built for ice'),
    'they were laid across the': ('Line 5', 'Laid across the Straits · 1953'),
    'as the water keeps falling off': ('Arch Rock', 'Mackinac Island · east shore'),
    'in september nineteen fifty four': ('Frank Pepper', 'Diver · September 1954'),
    'a month later james lesarge': ('James LeSarge', 'October 1954'),
    'two weeks after that albert': ('Albert Abbott', 'October 1954'),
    'in september nineteen seventy eight': ('September 1978', 'Heavy fog at the bridge'),
    'enbridge says the pipes under': ('Enbridge', 'Runs Line 5'),
    'about nine thousand years ago': ('About 9,000 years ago', 'The end of the last ice age'),
    'in lake huron archaeologists have': ('Alpena–Amberley Ridge', 'Lake Huron · now deep underwater'),
    "because next we're going to": ('Next file', 'The Graveyard of the Great Lakes'),
}

# reuse shots: description keyword -> (focus x, focus y, zoom start, zoom end)
REUSE_FOCUS = [
    ('closer on the rock maze', (0.50, 0.58, 1.35, 1.52)), ('closer on the ship rolling', (0.50, 0.50, 1.35, 1.50)),
    ('pipelines on the dry bed again', (0.45, 0.60, 1.25, 1.40)), ("cedarville's two halves again", (0.50, 0.55, 1.20, 1.35)),
    ('pipelines across the canyon again', (0.50, 0.55, 1.15, 1.30)), ('the exposed tower again', (0.50, 0.40, 1.30, 1.45)),
    ('the worn pipeline again', (0.50, 0.50, 1.30, 1.45)), ('the bridge at dawn again', (0.50, 0.45, 1.15, 1.28)),
    ('the waterfall again', (0.50, 0.45, 1.25, 1.40)), ('calm sunrise under the bridge again', (0.50, 0.50, 1.10, 1.22)),
    ('cars on the bridge at dusk again', (0.50, 0.50, 1.20, 1.32)), ('pipelines under the bridge at dusk again', (0.50, 0.55, 1.20, 1.32)),
    ('bridge over the dry canyon again', (0.50, 0.50, 1.18, 1.32)),
]

# what viewers read: spoken words -> shown text (captions and the .srt). Matched on whole words, any case.
DISPLAY = [
    ('Mackinaw Island', 'Mackinac Island'), ('Mackinaw Bridge', 'Mackinac Bridge'), ('Mackinaw Falls', 'Mackinac Falls'),
    ('two hundred and ninety-five feet', '295 feet'), ('two hundred and seventy feet', '270 feet'),
    ('two hundred and fifty feet', '250 feet'), ('two hundred and ten feet', '210 feet'), ('two hundred feet', '200 feet'),
    ('seven hundred and sixty feet', '760 feet'), ('five hundred and fifty-two feet', '552 feet'),
    ('Five hundred and eighty-eight feet', '588 feet'), ('a hundred and forty feet', '140 feet'),
    ('a hundred and ten feet', '110 feet'), ('a hundred feet', '100 feet'), ('forty feet', '40 feet'),
    ('thirty-five feet', '35 feet'), ('sixty-five feet', '65 feet'), ('Ten feet', '10 feet'), ('Twenty feet', '20 feet'),
    ('Thirty feet', '30 feet'), ('eighty feet', '80 feet'),
    ('a hundred and forty-eight square miles', '148 square miles'), ('twenty-two wrecks', '22 wrecks'),
    ('at eighty-five', 'at 85'), ('a hundred and twenty-four', '124'), ('a hundred and twenty', '120'),
    ('a hundred and eleven', '111'), ('a hundred and forty-five', '145'),
    ('May the seventh, nineteen sixty-five', 'May 7, 1965'), ('November the first, nineteen fifty-seven', 'November 1, 1957'),
    ('June the sixth, nineteen fifty-six', 'June 6, 1956'), ('September, nineteen fifty-four', 'September 1954'),
    ('September, nineteen seventy-eight', 'September 1978'), ('August, two thousand seven', 'August 2007'),
    ('nineteen fifty-three', '1953'), ('two thousand fourteen', '2014'), ('two thousand eighteen', '2018'),
    ('two thousand nineteen', '2019'),
    ('fourteen thousand tons', '14,000 tons'), ('Ten of the thirty-five men', '10 of the 35 men'), ('thirty-five men', '35 men'),
    ('took ten men', 'took 10 men'), ('ten twenty-five', '10:25'), ('four miles', '4 miles'), ('two miles', '2 miles'),
    ('five-mile', '5-mile'), ('five miles long', '5 miles long'), ('four and a half miles', '4.5 miles'),
    ('twenty inches', '20 inches'), ('twenty-three million gallons', '23 million gallons'), ('Line Five', 'Line 5'),
    ('three divers', '3 divers'), ('a hundred million dollars', '$100 million'), ('both twenty-eight', 'both 28'),
    ('seventy years', '70 years'), ('two and a half million cubic feet', '2.5 million cubic feet'),
    ('seven hundred miles', '700 miles'), ('sixty percent', '60%'), ('nine thousand years', '9,000 years'),
    ('sixty stone structures', '60 stone structures'), ('less than an inch', 'less than an inch'),
]

# the depth meter: (section, words it starts on, depth in feet, seconds to get there)
DEPTH_SHOW = ((2, "let's start the drain"), (10, 'tomorrow thousands of cars'))
DEPTH_KEYS = [
    (2, 'ten feet', 10, 1.4), (2, 'twenty feet', 20, 1.4), (2, 'thirty feet', 30, 1.4),
    (3, 'at thirty five feet', 35, 1.2),
    (4, 'at sixty five feet', 65, 2.0),
    (5, 'as the water keeps falling', 75, 3.0),
    (6, 'as the water keeps falling', 80, 2.0), (6, 'the m stalker', 85, 1.0), (6, 'the william young', 120, 1.2),
    (6, 'the minneapolis', 124, 1.0), (6, 'the eber ward', 145, 1.6),
    (7, 'as the water falls toward', 200, 3.0), (7, 'their foundations go down', 210, 1.5),
    (8, 'under the middle of the bridge', 250, 2.0), (8, 'and here at about two hundred', 270, 2.0),
    (9, 'now the very bottom', 295, 2.5),
    (10, 'the river canyon fills first', 240, 2.0), (10, 'then the waterfall disappears', 180, 1.8),
    (10, 'then the pipelines', 120, 1.8), (10, 'the water climbs the bridge towers', 60, 3.0),
    (10, 'the cedarville slips under', 40, 1.8), (10, 'then the top of her hull', 30, 1.6), (10, 'then the rock maze', 0, 2.6),
]
DEPTH_HIDE = {'G18', 'G19', 'G35', 'G36'}     # call-to-action graphics use the full width

# sound: extra hits on graphics (seconds after the graphic starts)
SOUND = dict(
    boom={'G01': [0.1], 'G07': [0.1], 'G11': [0.1], 'G13': [0.15], 'G22': [2.8], 'G24': [1.0], 'G32': [0.1], 'G34': [0.1]},
    ping={'G02': [0.4, 1.4, 2.3], 'G09': [2.9], 'G10': [2.4], 'G17': [1.0], 'G25': [1.4], 'G30': [0.6]},
    click={'G04': [1.3, 1.8], 'G35': [1.3, 3.2], 'G39': ['half', 'half+0.5']},
)
