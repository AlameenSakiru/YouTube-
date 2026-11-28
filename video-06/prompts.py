# Flow image prompts for video 6. Each prompt is the scene (P) plus the look for its style (LOOK).
# Written for Google Flow: a full sentence scene, camera terms, positive phrasing, plain ASCII.
# Colour style for this video: November 1913 storm blues and snow, warm lamplight on the ship and the ore dock;
# the 2013 search in clean daylight; the wreck in near-black water lit only by the camera's white lights.

NOLETTER = "A clean image with plain, unmarked hulls, surfaces and signs, and no lettering, names or numbers anywhere. Cinematic 16:9 wide frame."

LOOK = {
 "O": "Shot as a cinematic still from a historical drama set on Lake Superior in 1913, cold blue-grey storm light, the warm orange glow of oil lamps and deck lights, muted colour with fine film grain. Every ship, building and item of clothing is historically accurate for 1906 to 1914. People are small in the frame or seen from behind, never close up. " + NOLETTER,
 "M": "Shot as a modern colour documentary photograph on Lake Superior in 2013, natural light, true-to-life colour, realistic modern equipment, sharp detail. People are small in the frame or seen from behind, their faces not shown. " + NOLETTER,
 "U": "Shot as a deep-water documentary still from an underwater camera lowered on a long cable 535 feet down in Lake Superior: near-total darkness, cold blue-green water, the bright white beams of the camera's own lights falling on the wreck, fine particles floating in the beams, the steel rusted brown and dusted with fine grey silt, realistic detail. No divers and no people. " + NOLETTER,
 "B": "Shot as a modern colour documentary photograph on the south shore of Lake Superior near Marquette, Michigan, cool northern light, deep blue water, true-to-life colour and sharp detail. People are small in the frame or seen from behind. " + NOLETTER,
}

SMITH = "a 1906 steel Great Lakes ore freighter about 545 feet long, with a black hull, a small white pilothouse with an open bridge on its roof at the very front and a tall mast just behind it, a long flat deck lined with a row of square cargo hatches, and at the very back a white deckhouse with one tall black funnel"
DOCK = "the huge iron ore dock at Marquette, Michigan in 1913, a long, towering wooden trestle standing on hundreds of timber legs far out into the harbour, railway ore cars lined up along its top and rows of steel chutes hanging down its side"
WRECK = "the wreck of an old steel lake freighter"

P = {
1: "Wide shot of a small modern search boat on calm, grey Lake Superior at dawn, three people seen from behind on the open rear deck lowering a yellow torpedo-shaped sonar on a cable over the stern, mist on the water, no land in sight.",
2: "Wide shot of the bow of " + WRECK + " rising out of the darkness on the lake floor, the camera's white lights falling across the rusted bow and its old railings, everything beyond the light completely black.",
3: "Epic wide shot at dusk of " + SMITH + ", moored alongside " + DOCK + ", snow falling through the warm glow of the ship's lamps, steam rising from her funnel, a dark storm sky over the lake beyond. Low angle from the water. 24mm lens.",
4: "Wide shot at dusk of " + SMITH + ", steaming out of a harbour past the end of a stone breakwater with a small lighthouse on it, the open lake beyond dark grey and rough, snow in the air, smoke streaming from her funnel.",
5: "Wide shot at night of " + SMITH + ", plunging through huge storm waves on Lake Superior, a wave bursting white over her deck, heavy snow blowing sideways through the glow of her deck lights. Seen from a distance.",
6: "Wide shot at night of an empty, storm-tossed Lake Superior in heavy snow, huge dark waves with white crests, no ship and no land anywhere, a faint grey light in the clouds.",
7: "Close shot of a single splintered wooden hatch cover and a broken oar half buried in fresh snow at the edge of a grey lake, a grey morning after a storm, small waves rolling in behind, nothing else on the beach.",
8: "Aerial wide shot of open Lake Superior on a clear day, deep blue water stretching to a perfectly flat horizon, one tiny white boat far out on the water, a vast sense of emptiness.",
9: "Shot at night from the deck of " + SMITH + ", looking forward along the long deck toward her small lit pilothouse at the bow, snow and spray blowing through the warm light of its windows, black sea beyond.",
10: "Wide shot of enormous black storm clouds massing low over Lake Superior in November 1913, a wall of snow beneath them, the water dark and rough, a small steamer far off on the horizon.",
11: "Wide shot from high on a ship's stern looking along the deck of a 1913 steel freighter as a huge wave breaks over it, green and white water pouring across the hatches, a blizzard all around.",
12: "Wide interior shot of a 1913 weather office at night, a forecaster seen from behind leaning over a large desk, drawing curved pressure lines by hand on a big paper map of plain coastlines under a green-shaded lamp, a telegraph key and stacks of paper beside him.",
13: "Wide shot from a distance of a gigantic wave smashing into the small pilothouse at the front of a 1913 steel freighter, glass and spray exploding outward, the bow buried in white water, heavy snow.",
14: "Wide shot of the forward cabins of a 1913 steel freighter after a huge wave has torn them open, walls ripped away, broken timber and snow on the deck, a grey storm sea beyond.",
15: "Wide shot of a snowy 1913 Lake Superior shoreline after a great storm, broken timber, a smashed wooden lifeboat and storm debris strewn along the beach, a grey sky and a dark, still angry lake.",
16: "Wide shot at dusk of " + SMITH + ", tied up alongside " + DOCK + ", snow drifting through the lamplight, her deck quiet, the harbour water choppy and grey, a mood of waiting.",
17: "Wide side-on shot of " + SMITH + ", brand new in 1906, steaming across a calm, sunny summer lake, her black hull gleaming, a thin trail of smoke from her funnel, blue sky.",
18: "Wide shot of a long steel lake freighter sliding sideways into a river at her launch at a 1906 Ohio shipyard, a huge wave of spray rising, crowds in Edwardian clothes lining the bank and waving hats.",
19: "Wide establishing shot of " + DOCK + ", a steel freighter tied up alongside it, an overcast November sky, the town of Marquette with its stone buildings and church spires on the hill behind.",
20: "Wide shot on top of an ore dock in falling snow, men in heavy coats and caps seen from behind standing in open railway ore cars, swinging long iron bars to break up frozen red iron ore, lantern light.",
21: "Wide shot from behind of a ship's captain of 1913 in a long dark coat and cap standing alone on the open wing of a freighter's bridge, looking out over a harbour at a dark storm on the lake, snow in the air.",
22: "Wide interior shot of a 1913 shipping company office at night, two men in dark suits seen from behind standing at a heavy wooden desk with a single letter on it, a green-shaded lamp, wood panelling, a tense mood.",
23: "Wide shot of a harbour on Lake Superior in 1913 as the storm clouds part a little, pale silver light falling on calmer grey water and on a small lighthouse at the end of a stone breakwater, the lake beyond still rolling.",
24: "Close-up at dusk of a long steel chute on an ore dock pouring a stream of red iron ore down into the open square hatch of a ship below, dust in the lamplight, snow in the air.",
25: "Wide shot at dusk of " + SMITH + ", backing away from " + DOCK + ", into the harbour, black smoke pouring from her funnel, her deck lights glowing, snow falling.",
26: "Wide shot from behind of a few townspeople in 1913 winter coats and hats standing on a snowy stone breakwater, watching a long freighter head out into the dark lake, dusk.",
27: "Wide shot at dusk on the long deck of a 1913 steel freighter, deckhands in oilskins dragging heavy hatch covers into place over the square openings in the deck and pulling canvas tarpaulins over them, many openings still uncovered, spray flying over the rail, snow.",
28: "Long telephoto shot from the shore at dusk of a long freighter heading out past the end of a stone breakwater, tiny figures still working on her deck, the waves around her starting to rise.",
29: "Wide shot of a towering wall of snow squall racing across Lake Superior toward a lone freighter far out on the water, the sky above going black, the last light disappearing.",
30: "Long telephoto shot from the shore at dusk of a long freighter far out in heavy seas, turning away to the left, snow blowing between her and the shore, her lights faint.",
31: "Wide shot at night of a blizzard over dark Lake Superior, thick snow filling the air, the faint lights of a single ship just visible and fading away into the snow.",
32: "Wide shot of a snowy sand beach on a grey morning, wreckage scattered along the waterline: broken planks, a heavy wooden hatch cover and old cork life jackets, small waves rolling in.",
33: "Wide shot of empty, grey Lake Superior from a rocky shore at dawn after a storm, the water calm and flat, thick ice coating the rocks in the foreground, a pale cold sky.",
34: "Wide shot from behind of a small group of townspeople in 1913 winter coats and hats standing on a snowy beach, looking out at a grey, empty lake.",
35: "Close-up of an old glass bottle with a rolled paper inside, lying among smooth wet pebbles at the edge of a calm lake, warm early summer light, shallow depth of field.",
36: "Wide interior shot of a 1914 office at night, three men in dark suits seen from behind leaning over a desk, studying a small unfolded piece of paper under a lamp, the paper blank from this angle.",
37: "Wide shot of endless Lake Superior seen from a high rocky clifftop with pine trees, deep blue water stretching to the horizon under a pale sky.",
38: "Wide shot of a long 1950s Great Lakes ore freighter passing a rocky, pine-covered Lake Superior shore on a calm summer day, her dark hull and white cabins reflected in the water.",
39: "Wide shot looking down into deep, dark water, the faint grey outline of a long ship barely visible far below in the blackness, a few particles drifting in a faint beam of light.",
40: "Wide shot from behind of three people on the open rear deck of a small modern research boat on Lake Superior, coils of cable and a winch beside them, a grey overcast day, the lake flat.",
41: "Wide shot of a home desk at night stacked with old archive folders and rolled-up charts beside an open laptop under a desk lamp, the papers blank, a warm quiet mood.",
42: "Wide shot of a workbench in a home garage workshop, a yellow torpedo-shaped side-scan sonar lying on it half assembled, tools, wires and cables around it, bright work light.",
43: "Top-down shot of a blank nautical chart spread on a wooden table, a pencil circle drawn on an empty area of water, a brass compass and dividers beside it, soft lamp light.",
44: "Wide shot of a small modern search boat on a calm, bright Lake Superior morning, a cable running from her stern down into the clear blue water, gentle ripples, no land in sight.",
45: "Wide shot from the deck of a small boat of a compact yellow underwater camera on a long cable tether being lowered over the side into deep blue water, hands seen from behind guiding the cable.",
46: "Close shot in black water of a camera's white light pressed against the rusted, silt-covered edge of a steel hull, its thin cable snagged on a jagged steel plate, darkness everywhere else.",
47: "Wide shot from behind of two people on a small boat's deck in June, leaning toward a monitor that glows deep blue, sunlight on the calm lake around them.",
48: "Wide shot of the bow of " + WRECK + " sitting upright on the dark lake floor, the camera's lights falling across its rusted plates and old railings, the rest of the ship fading into black.",
49: "Wide shot of the small old pilothouse on the bow of " + WRECK + ", its windows empty and dark, a tall mast still standing behind it and rising up into the black water, lit by the camera's lights.",
50: "Wide shot of the collapsed, crumpled deckhouse on the stern of " + WRECK + ", its walls crushed inward and folded, twisted metal and silt, lit by the camera's lights in the darkness.",
51: "Close shot of the camera's light moving slowly across the curved, rusted steel plating of an old ship's stern, rivet lines and silt, darkness all around.",
52: "Wide shot of a field of red iron ore spilled across the grey silt of the lake floor beside the dark, rusted side of " + WRECK + ", lit by the camera's lights.",
53: "Wide shot at night of " + SMITH + ", fighting north through huge waves in a blizzard, a dark, low headland faintly visible far away on the horizon, her deck lights glowing.",
54: "Wide shot at night on the deck of a 1913 steel freighter as a wave pours across it and cascades down into an open square cargo hatch, water rushing into the black hold below, snow and spray.",
55: "Wide shot at night from a distance of a long steel freighter of 1913 stretched across two huge waves, her bow on the crest of one and her stern on the crest of the next, the middle of her hull over the deep trough between them, snow.",
56: "Wide shot at night from a distance of a long steel freighter breaking apart in a storm, her deck buckling and tearing open across the middle, the bow and stern beginning to separate, huge waves, snow.",
57: "High-angle wide shot looking down on " + WRECK + " broken into two halves on the dark lake floor, the camera's lights sweeping across both pieces, red ore scattered between them, darkness beyond.",
58: "Wide shot of the bow of " + WRECK + " on the dark lake floor as the camera's lights slowly dim and fade, the shape of the old ship sinking back into the darkness, peaceful and still.",
59: "Wide shot of Lake Superior at sunset from a rocky shore, the sky orange and gold, the calm lake reflecting the light, empty all the way to the horizon.",
60: "Wide shot at sunset of a red brick lighthouse with a square tower standing on a rocky point above a harbour on Lake Superior, the sky orange and purple, calm water, the left half of the frame open sky and water.",
}

THUMBS = [
 "Epic underwater wide shot in the deep darkness of Lake Superior of the bow of " + SMITH + " sitting upright on the lake floor as a rusted wreck, her old pilothouse and mast lit by bright white lights from above, red iron ore spilled across the grey silt, the broken middle of the hull fading into black behind her. High contrast, vivid, cinematic, cold blue with the warm glow of rust. The left third of the frame is dark open water. " + NOLETTER,
 "Split image: the left half shows " + SMITH + " steaming out of a snowy harbour into a dark November storm in 1913, warm deck lights glowing; the right half shows the same ship as a rusted wreck broken in two on the dark lake floor, lit by a camera's lights. High contrast, cinematic, historically accurate. " + NOLETTER,
 "Wide shot at night of " + SMITH + " alone in huge storm waves on Lake Superior in a blizzard, her deck lights glowing, a wave breaking over her deck. The right third of the frame is dark stormy sky. High contrast, vivid, cinematic, historically accurate for 1913. " + NOLETTER,
]
