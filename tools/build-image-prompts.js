const fs = require("fs");
const path = require("path");
const {
  Document, Packer, Paragraph, TextRun, HeadingLevel, AlignmentType, ShadingType, BorderStyle,
  LevelFormat, PageBreak, Footer, Header, PageNumber,
} = require("docx");

const shots = JSON.parse(fs.readFileSync(process.argv[3] || path.join(__dirname, "shots.json"), "utf8"));
const sections = JSON.parse(fs.readFileSync(process.argv[4] || path.join(__dirname, "sections.json"), "utf8"));
const OUT = process.argv[2];

const FONT = "Arial", INK = "1F2933", MUTED = "5B6675", ACCENT = "1F5A7A", BOX = "EEF3F7", OPT = "8A5A00";

const STYLE = {
  A: "Black-and-white documentary photograph from 1954, Great Lakes region of the United States, 35mm film grain, soft natural light, realistic, no modern objects, no text, no watermark, wide 16:9 frame.",
  B: "Colour documentary photograph, present day, Great Lakes region, natural light, realistic, no text, no watermark, wide 16:9 frame.",
  C: "Black-and-white documentary photograph from 1929, Michigan harbour town on Lake Michigan, film grain, realistic, no modern objects, no text, no watermark, wide 16:9 frame.",
  D: "Colour documentary photograph, present day, deep underground salt mine, dramatic artificial light, realistic, no text, no watermark, wide 16:9 frame.",
};
const STYLE_NAME = { A: "1954, black and white", B: "present day, colour", C: "1929, black and white", D: "underground, colour" };

// map a normalized token index back to the original words of a section
function snippet(secIdx, tokenIdx, n = 11) {
  const words = sections[secIdx - 1].paras.join(" ").split(/\s+/);
  const map = [];
  words.forEach((w, wi) => {
    const t = w.toLowerCase().replace(/-/g, " ").replace(/[^a-z' ]/g, " ").split(/\s+/).filter(Boolean);
    t.forEach(() => map.push(wi));
  });
  const start = map[tokenIdx] ?? 0;
  const out = [];
  for (let k = start; k < words.length && out.length < 14; k++) {
    out.push(words[k]);
    if (out.length >= 4 && /[.?!]["”]?$/.test(words[k]) && !/\.\.\.$/.test(words[k])) return out.join(" ").replace(/^["“]/, "");
  }
  return out.join(" ").replace(/^["“]/, "").replace(/[,.;:!?"]+$/, "") + "…";
}

const run = (text, o = {}) => new TextRun({ text, font: FONT, size: o.size ?? 22, color: o.color ?? INK, bold: o.bold, italics: o.italics });
const p = (children, o = {}) => new Paragraph({ spacing: { after: o.after ?? 120, before: o.before ?? 0, line: 276 }, keepNext: o.keepNext, keepLines: true, children: Array.isArray(children) ? children : [run(children, o)] });
const numbered = (t) => new Paragraph({ numbering: { reference: "steps", level: 0 }, spacing: { after: 80, line: 276 }, children: [run(t)] });
const bullet = (t) => new Paragraph({ numbering: { reference: "bullets", level: 0 }, spacing: { after: 80, line: 276 }, children: [run(t)] });
const h2 = (t) => new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun({ text: t, font: FONT })] });
const promptBox = (t) => new Paragraph({
  spacing: { before: 60, after: 280, line: 300 }, keepLines: true,
  shading: { type: ShadingType.CLEAR, color: "auto", fill: BOX },
  border: { left: { style: BorderStyle.SINGLE, size: 24, color: ACCENT, space: 12 } },
  indent: { left: 240, right: 240 },
  children: [run(t, { size: 21 })],
});

const flow = shots.filter((s) => s.kind === "F");
const reusedCount = {};
shots.filter((s) => s.kind === "R").forEach((s) => (reusedCount[s.img] = (reusedCount[s.img] || 0) + 1));
const nOpt = flow.filter((s) => s.optional).length;

const children = [];
children.push(new Paragraph({ heading: HeadingLevel.TITLE, children: [new TextRun({ text: "Image prompts", font: FONT })] }));
children.push(p([run("Video 1: ", { bold: true, size: 26, color: ACCENT }), run("Lake Michigan Has Tsunamis, and Nobody in Chicago Saw This One Coming", { size: 26, color: ACCENT })], { after: 80 }));
children.push(p(`${flow.length} images · ${flow.length - nOpt} needed and ${nOpt} optional · plus 3 thumbnail versions`, { color: MUTED, after: 240 }));

children.push(h2("How to use this list"));
[
  "Copy the whole shaded box for each image into Flow. Every prompt is complete: the picture and the style are already in it.",
  "Choose the wide 16:9 shape and the largest size Flow offers.",
  "Save each image with its number: 001.png, 002.png, up to " + String(flow.length).padStart(3, "0") + ".png. If you make two versions, name the second one with a b, for example 004b.png, and I will use the better one.",
  "Images marked Optional are nice to have. If you skip one, I will cover it with a nearby image.",
  "Send them to me the same way you sent the voice files.",
].forEach((t) => children.push(numbered(t)));

children.push(h2("Generate it again if you see"));
[
  "Any readable text, letters, signs or newspaper headlines.",
  "Modern things in a 1954 or 1929 picture: phones, modern cars, modern clothes, plastic.",
  "Colour in a picture that should be black and white.",
  "Faces shown close up. People should be small, far away or seen from behind.",
  "Warped hands, extra limbs, or bodies that look wrong.",
  "Anyone shown drowning, injured or dead.",
].forEach((t) => children.push(bullet(t)));

children.push(h2("Why the timing matters"));
children.push(p("Each image shows how long it stays on screen, timed to your voiceover. I add slow zooms and pans in the edit, so a picture never sits still. The line under each number is the narration it goes with, so you can check that the picture matches the words."));

let lastSec = 0;
flow.forEach((s) => {
  if (s.sec !== lastSec) {
    children.push(new Paragraph({ children: [new PageBreak()] }));
    children.push(new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun({ text: `Section ${s.sec}: ${sections[s.sec - 1].title}`, font: FONT })] }));
    lastSec = s.sec;
  }
  const num = String(s.img).padStart(3, "0");
  const meta = [run(`${num}`, { bold: true, size: 26, color: ACCENT }), run(`     about ${Math.max(1, Math.round(s.d))} s on screen`, { color: MUTED, size: 20 }), run(`     ${STYLE_NAME[s.style]}`, { color: MUTED, size: 20 })];
  if (reusedCount[s.img]) meta.push(run(`     used again later`, { color: MUTED, size: 20 }));
  if (s.optional) meta.push(run(`     Optional`, { bold: true, color: OPT, size: 20 }));
  children.push(p(meta, { after: 40, keepNext: true }));
  children.push(p([run("With the words: ", { italics: true, color: MUTED, size: 20 }), run(`“${snippet(s.sec, s.word)}”`, { italics: true, color: MUTED, size: 20 })], { after: 40, keepNext: true }));
  children.push(promptBox(`${s.desc}. ${STYLE[s.style]}`));
});

// thumbnails
children.push(new Paragraph({ children: [new PageBreak()] }));
children.push(new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun({ text: "Thumbnail", font: FONT })] }));
children.push(p("Make all three. I will add the text (\"10 FEET\" and \"CHICAGO, 1954\") and we will pick the one that reads best at phone size. Each prompt leaves empty sky on the right for the text."));
const thumbs = [
  ["thumb-1.png", "A towering wall of grey lake water rising behind a long concrete pier on Lake Michigan, a few small fishermen on the pier seen from behind, bright sunny sky, the wave fills the left two thirds of the frame and the right third is empty sky. Black-and-white documentary photograph from 1954, high contrast, film grain, realistic, no text, no watermark, wide 16:9 frame."],
  ["thumb-2.png", "Low angle from the end of a concrete pier, an enormous swell of lake water towering over one small fisherman seen from behind, clear sky, the right third of the frame is empty sky. Black-and-white documentary photograph from 1954, high contrast, dramatic, realistic, no text, no watermark, wide 16:9 frame."],
  ["thumb-3.png", "A sunny 1950s Chicago lakefront pier with a huge wall of blue-grey water rising behind small figures, deep blue summer sky, the right third of the frame is empty sky. Colourised 1950s photograph, vivid but realistic, no modern objects, no text, no watermark, wide 16:9 frame."],
];
thumbs.forEach(([name, t]) => {
  children.push(p([run(name, { bold: true, size: 26, color: ACCENT })], { after: 40, keepNext: true }));
  children.push(promptBox(t));
});

const doc = new Document({
  creator: "Five Lakes Files",
  title: "Video 1 image prompts",
  styles: {
    default: { document: { run: { font: FONT, size: 22, color: INK } } },
    paragraphStyles: [
      { id: "Title", name: "Title", basedOn: "Normal", next: "Normal", run: { font: FONT, size: 48, bold: true, color: INK }, paragraph: { spacing: { before: 0, after: 120 }, keepNext: true } },
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true, run: { font: FONT, size: 32, bold: true, color: ACCENT }, paragraph: { spacing: { before: 0, after: 200 }, keepNext: true, outlineLevel: 0 } },
      { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true, run: { font: FONT, size: 26, bold: true, color: INK }, paragraph: { spacing: { before: 240, after: 100 }, keepNext: true, outlineLevel: 1 } },
    ],
  },
  numbering: {
    config: [
      { reference: "steps", levels: [{ level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 540, hanging: 360 } } } }] },
      { reference: "bullets", levels: [{ level: 0, format: LevelFormat.BULLET, text: "•", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 540, hanging: 360 } } } }] },
    ],
  },
  sections: [{
    properties: { page: { size: { width: 12240, height: 15840 }, margin: { top: 1440, bottom: 1440, left: 1440, right: 1440 } } },
    headers: { default: new Header({ children: [new Paragraph({ alignment: AlignmentType.RIGHT, children: [run("Video 1 image prompts", { size: 18, color: MUTED })] })] }) },
    footers: { default: new Footer({ children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ children: ["Page ", PageNumber.CURRENT, " of ", PageNumber.TOTAL_PAGES], font: FONT, size: 18, color: MUTED })] })] }) },
    children,
  }],
});
Packer.toBuffer(doc).then((b) => { fs.writeFileSync(OUT, b); console.log("wrote", OUT, "images", flow.length, "optional", nOpt); });
