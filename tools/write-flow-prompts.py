import json, csv, os, sys

LOOK = {
 "A": "Shot as a black-and-white press photograph on 35mm film in the Great Lakes region in 1954, slightly grainy with soft natural contrast. Every person, vehicle, building and item of clothing is historically accurate for the early 1950s. People are small in the frame or seen from behind. A clean image with plain, unmarked surfaces and no lettering anywhere. Cinematic 16:9 wide frame.",
 "B": "Shot as a modern colour documentary photograph with natural light, true-to-life colour and sharp detail. People are small in the frame or seen from behind. A clean image with plain, unmarked surfaces and no lettering anywhere. Cinematic 16:9 wide frame.",
 "C": "Shot as a black-and-white photograph on film in 1929, grainy with soft contrast. Every person, boat, building and item of clothing is historically accurate for the late 1920s. People are small in the frame or seen from behind. A clean image with no lettering anywhere. Cinematic 16:9 wide frame.",
 "D": "Shot as a modern colour documentary photograph deep underground, lit by bright work lights and headlights, with rich detail in the salt crystals. A clean image with no lettering anywhere. Cinematic 16:9 wide frame.",
}

P = {
1: "Extreme close-up at ground level of a man's polished leather shoe and the cuff of his uniform trousers on a weathered concrete breakwater, as a thin, glassy sheet of lake water slides across the concrete and over the toe of the shoe. Shallow depth of field, the calm lake blurred behind, bright morning sunlight glinting on the water.",
2: "Medium-wide shot from behind of a young state conservation officer in a 1950s uniform shirt and peaked cap, writing in a small ticket book beside a middle-aged fisherman in a fedora who holds a long bamboo rod. They stand on a long concrete breakwater, both turned away from the camera, the lake beyond flat and calm under a clear morning sky. 35mm lens at eye level.",
3: "Wide establishing shot of Lake Michigan lying perfectly flat and mirror-calm under bright morning sun, a long concrete breakwater stretching out from the left with tiny distant figures of fishermen along it, sunlight sparkling on the water, a peaceful clear summer sky. 28mm wide-angle lens.",
4: "High-angle wide shot looking down from a raised harbour wall as a sudden surge of lake water pours over the top of a long concrete breakwater, white foam spreading across the concrete, tiny indistinct figures far along the breakwater, bright sunny sky, a feeling of shock and sudden motion. Telephoto compression.",
5: "Wide shot from far across a harbour of a huge, smooth swell of lake water rolling through the narrow entrance between two concrete breakwaters and lifting everything around it, the harbour completely empty, bright sunlight on the water under an unsettlingly calm sky. 85mm telephoto lens.",
6: "Wide shot along a sunny 1950s Chicago lakefront promenade on a summer morning, men in short-sleeved shirts and straw hats and women in summer dresses strolling away from the camera beside the calm lake, a thin line of dark storm clouds far away on the horizon over the water, everything else bright and peaceful.",
7: "Wide landscape photograph from a sandy Chicago beach looking straight out over Lake Michigan, only open water all the way to a perfectly flat horizon, small waves rolling onto the sand, so vast it looks like an ocean. Soft late-morning light, 24mm wide-angle lens at eye level.",
8: "A lone person standing at the water's edge on a Chicago beach, seen from behind and small in the frame, looking out at the endless horizon of Lake Michigan, gentle waves at their feet, a wide composition with open water and sky. Calm early-morning light.",
9: "Wide high-angle shot of a crowded Chicago beach on a hot June day, swimmers in the shallow water, families on blankets and on the grass, striped umbrellas, the city skyline rising behind the beach in a bright summer haze, everyone small in the frame.",
10: "Wide shot from the shore end of a long, straight concrete pier reaching far out into deep, calm water, fishermen spaced along its edges with long bamboo rods, seen from behind, bright morning light, strong leading lines toward the horizon.",
11: "Wide shot of a dark, menacing shelf of storm clouds sweeping low over a city lakefront, trees bending hard in the wind, the lake surface whipped into whitecaps, sudden early-morning gloom.",
12: "Medium-wide shot from behind of people hurrying off a concrete pier in driving rain, men holding jackets and newspapers over their heads, rain streaking across the frame, wet concrete reflecting the grey sky.",
13: "Medium shot from behind of three men in 1950s hats and jackets sheltering in the doorway of a brick harbour building, watching sheets of heavy rain fall across the harbour, framed by the dark doorway.",
14: "Wide shot of the storm moving away across the lake toward the horizon, sunlight breaking through the clouds behind it, shafts of light on the water, a wet empty concrete pier in the foreground glistening with puddles, a feeling of relief.",
15: "Medium-wide shot from behind of a few fishermen walking back out along a wet concrete pier carrying their rods and tackle boxes, the sky clearing ahead of them, puddles reflecting the light.",
16: "Close-up of a fisherman's weathered hands holding a bamboo fishing rod over calm, sunlit water, the line trailing into the lake, shallow depth of field, the man's face outside the frame.",
17: "Medium shot from behind of a young lifeguard in 1950s swim trunks with a whistle on a cord around his neck, standing on the sand with his hands on his hips, looking out at a calm, sunlit lake, a wooden lifeguard chair beside him.",
18: "Wide shot of an almost empty city beach in early-morning sun, a long, low white 1950s beach house along the back of the sand, a few footprints, the calm lake to the right.",
19: "Long telephoto shot of two small fishermen far out at the end of a curved, hook-shaped concrete pier, dark shapes against bright calm water, the pier curving like a hook into the lake.",
20: "Low-angle shot of a neat row of wooden rescue rowboats pulled up on the sand in front of a white beach house, oars resting inside them, morning sunlight, calm water beyond.",
21: "Wide action shot from behind and to one side of three young lifeguards running down the sand toward a row of rowboats as lake water surges up the beach toward them, spray in the air, motion blur on their legs.",
22: "Wide shot from a distance of a wall of white water breaking over a row of wooden rowboats on a beach and rushing up the sand, figures small and indistinct, dramatic spray, bright sky.",
23: "Medium-wide shot from a distance of two young lifeguards standing up in knee-deep water after being knocked over, soaked and laughing, water streaming off them, a white beach house behind, bright morning light.",
24: "Wide shot of a man in rolled-up trousers running across wet sand, waving one arm urgently, small in the frame, a hook-shaped concrete pier in the background.",
25: "Medium shot from behind of a father in a short-sleeved shirt and fedora and his teenage son fishing side by side at the edge of a concrete pier, rods out over calm water, an ordinary, quiet summer morning.",
26: "Wide shot from the shore of a line of lifeguards linked arm in arm, wading chest-deep through rough, choppy water as they search, seen from behind, grey water and spray.",
27: "Medium-wide side view from a distance of a 1950s Chicago police car with a single roof light, stopped on the road beside a beach, an officer in uniform and cap leaning out of the driver's window.",
28: "Wide shot from across the water of a long harbour breakwater lined with dozens of fishermen in hats standing along its edge, small boats moored in the calm harbour behind them, bright morning sun, a busy summer scene.",
29: "Medium-wide shot of lake water rising fast up the side of a stone harbour wall, moored wooden boats lifted high and straining at their ropes, the water churning, bright sky above.",
30: "Wide shot of a harbour with two small police boats and divers in 1950s rubber diving suits at the surface, men on the breakwater watching in the distance, grey, sombre light.",
31: "Close-up still life at ground level of two bamboo fishing rods, an open metal tackle box and a man's straw fedora left lying on wet concrete at the edge of a breakwater, the calm lake behind out of focus, a quiet, sombre mood.",
32: "Wide shot of a long concrete breakwater, now completely empty, the lake flat and calm again, bright sunshine and a clear pale sky, an eerie stillness.",
33: "Wide interior shot of a busy 1950s newspaper newsroom, reporters in shirtsleeves at rows of desks with typewriters, telephones and hanging lamps, cigarette smoke in the air, the papers on the desks blank or blurred.",
34: "Medium-wide shot from behind of three men in suits and fedoras standing on a concrete breakwater with their hands in their pockets, looking out at a calm lake under a clear sky, serious and puzzled.",
35: "Medium side view of a 1950s scientist in shirt, tie and glasses leaning over a laboratory desk, studying a long strip of paper from a chart recorder with a jagged ink line, scientific instruments around him, soft window light.",
36: "Over-the-shoulder medium shot of a researcher at a desk in a modern laboratory, two large monitors glowing with a blue and green computer simulation of waves moving across a lake, the screens showing only colour and wave patterns, the dim room lit by the screens.",
37: "Aerial photograph from high above of a long line of towering thunderstorms marching across open water, a sharp dark edge of cloud with sunlight on the water ahead of it, dramatic scale.",
38: "Medium shot from behind of an adult pushing a small child on a playground swing at the top of its arc, the child in mid-air, a sunny park, warm afternoon light.",
39: "Wide shot of a sunny lakeshore where a sudden surge of water washes over a low concrete breakwater and spreads across the sand, blue sky, people small and far away.",
40: "Wide shot of a calm city lakefront on a bright sunny morning, a pale clear sky, gentle light on still water, a long pier in the distance, peaceful and ordinary.",
41: "Wide shot of storm waves pouring over a concrete breakwater with a small white lighthouse at its end in Michigan City, Indiana, wind-driven rain, a dark sky, violent spray.",
42: "Wide shot from behind of fishermen running up a sandy path through dune grass away from the lake in driving rain, clutching their rods and hats, a dark storm sky over the water behind them.",
43: "Wide shot of a calm open lake under a clear sky with one long, low, smooth swell approaching from the distance across the whole width of the water, barely visible, eerie and quiet.",
44: "Medium-wide shot from behind of fishermen standing on a pier looking out at a calm, sunlit lake, rods resting on the rail, relaxed and unaware.",
45: "Wide shot of a dark storm passing over the Chicago lakefront and skyline, heavy cloud over the water, rain falling in grey curtains, the lake choppy.",
46: "Medium shot from behind of a 1950s weather forecaster in shirt and tie at a desk with a black telephone to his ear, a teleprinter machine and weather maps around him, the papers blurred, office window light.",
47: "Wide shot from a distance of police officers and lifeguards waving people off a beach and pointing toward the road, beachgoers walking away carrying towels and baskets.",
48: "Wide shot of lake water flooding a beach parking lot, rounded 1950s cars standing with water around their wheels, the water rushing between them, beach buildings behind.",
49: "Medium-wide shot of lake water rushing up the wide concrete steps of a white 1950s beach house and pouring back down, foam and spray, the beach empty.",
50: "Wide shot of an empty beach under a clearing sky, wet sand, debris scattered along the waterline, calm water returning, not a single person anywhere.",
51: "Low-angle close-up of steel posts and taut steel cables running along the top of a weathered concrete breakwater as a handhold, the line receding into the distance, the lake and sky behind, late-afternoon light.",
52: "Wide interior shot of a dim records room with tall shelves of large bound newspaper volumes and metal filing cabinets, a single lamp, dust floating in the light, the spines plain and unlabelled.",
53: "Medium-wide shot of a small white water-level measuring station with a solar panel and an antenna, mounted on a concrete harbour wall beside a large lake on a clear day.",
54: "Wide shot of a long pier with a lighthouse at the end in Grand Haven, Michigan, men in flat caps and women in 1920s dresses walking along it, rough grey water after a morning thunderstorm.",
55: "Wide shot of a long sandy beach backed by tall wooded sand dunes on the Michigan shore, the sky clearing after a storm, the last dark clouds leaving over the lake.",
56: "Wide shot from behind of swimmers and families walking into the lake in bright sunshine, children running into the shallows, storm clouds receding on the horizon.",
57: "Wide shot of grey water pouring over a harbour wall in a small Michigan port town on a cold April day, waves crashing onto the walkway, an empty harbour under a grey sky.",
58: "Medium shot of a damaged wooden boat dock with broken planks and tangled debris along a lakeshore after high water, overcast light.",
59: "Medium shot from behind of a person in a winter jacket on a harbour wall holding up a phone to photograph big waves crashing over the wall, a grey spring day.",
60: "Wide shot of a rocky Lake Superior beach where the water has drained far out, leaving a wide stretch of bare stones and lake bed exposed, a few people at the edge filming with their phones, seen from behind, overcast sky.",
61: "Low-angle wide shot of lake water rushing back up over a rocky shoreline and foaming between the stones, strong motion.",
62: "Medium-wide shot of a bright yellow scientific buoy with solar panels, an antenna and instruments, floating on a large calm lake under a clear sky, the horizon in the distance.",
63: "Medium-wide shot from behind of two scientists in life jackets on the deck of a research boat preparing a yellow buoy to be lowered into the lake, a crane arm above them.",
64: "Wide shot of a beach in bright sunshine just after a storm, wet sand shining, people walking back toward the water carrying towels, seen from behind, dark clouds moving away.",
65: "Wide shot of a line of thunderstorms moving away over the lake, the sun breaking through behind an empty concrete pier, shafts of light, puddles on the pier.",
66: "Low-angle wide shot of an empty concrete pier in bright sunshine just after rain, puddles reflecting the blue sky.",
67: "Wide shot of water drawn far back from a beach, leaving a broad stretch of wet sand and rocks exposed a long way out to the waterline, strange and quiet.",
68: "Wide shot from behind of fishermen walking out onto a long concrete pier under a clear blue morning sky, carrying rods and tackle, relaxed and unhurried.",
69: "Wide shot of an empty concrete breakwater in sunshine, a single bamboo fishing rod leaning against the rail, calm water, complete stillness.",
70: "Wide shot of the modern Chicago lakefront trail on a summer day, people walking and cycling beside the lake, the city skyline rising behind, sunny.",
71: "Aerial photograph at dawn of the Chicago skyline on the shore of Lake Michigan, the vast lake stretching to the horizon in soft pink and blue light.",
72: "Wide shot inside a huge underground tunnel cut through solid white rock salt, the walls and ceiling glittering, a large mining truck approaching with bright headlights cutting through the darkness.",
73: "Extreme wide shot of a vast underground cavern of white rock salt with rows of massive pillars, a tiny truck far away for scale, lit by work lights.",
}

THUMBS = [
 "Wide shot of a towering wall of grey lake water rising behind a long concrete pier on Lake Michigan, a few small fishermen on the pier seen from behind, bright sunny sky. The wave fills the left two thirds of the frame and the right third is open sky. Shot as a high-contrast black-and-white press photograph on 35mm film in 1954, dramatic and realistic, historically accurate clothing. A clean image with no lettering anywhere. Cinematic 16:9 wide frame.",
 "Low-angle shot from the end of a concrete pier of an enormous swell of lake water towering over one small fisherman seen from behind, clear sky, the right third of the frame open sky. Shot as a high-contrast black-and-white press photograph on 35mm film in 1954, dramatic and realistic. A clean image with no lettering anywhere. Cinematic 16:9 wide frame.",
 "Wide shot of a sunny 1950s Chicago lakefront pier with a huge wall of blue-grey water rising behind small figures, a deep blue summer sky, the right third of the frame open sky. Shot as a colourised 1950s photograph, vivid but realistic, historically accurate clothing. A clean image with no lettering anywhere. Cinematic 16:9 wide frame.",
]

if __name__ == "__main__":
    plan = sys.argv[1]; outdir = sys.argv[2]
    shots = json.load(open(plan))
    flow = [s for s in shots if s["kind"] == "F"]
    assert sorted(P) == [s["img"] for s in flow], "prompt numbers do not match the plan"
    for s in flow:
        s["prompt"] = P[s["img"]] + " " + LOOK[s["style"]]
        assert s["prompt"].isascii(), s["img"]
    json.dump(shots, open(plan, "w"), indent=1)
    os.makedirs(outdir, exist_ok=True)
    lines = [s["prompt"] for s in flow]
    open(os.path.join(outdir, "flow-prompts.txt"), "w").write("\n".join(lines) + "\n")
    open(os.path.join(outdir, "flow-prompts-blank-lines.txt"), "w").write("\n\n".join(lines) + "\n")
    with open(os.path.join(outdir, "flow-prompts.csv"), "w", newline="") as f:
        w = csv.writer(f); w.writerow(["file_name", "optional", "prompt"])
        for s in flow: w.writerow(["%03d.png" % s["img"], "yes" if s.get("optional") else "no", s["prompt"]])
    open(os.path.join(outdir, "flow-thumbnails.txt"), "w").write("\n".join(THUMBS) + "\n")
    for t in THUMBS: assert t.isascii()
    print("prompts", len(lines), "longest", max(len(l) for l in lines), "chars, thumbnails", len(THUMBS))
