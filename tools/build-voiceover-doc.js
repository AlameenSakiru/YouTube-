const fs = require("fs");
const path = require("path");
const {
  Document, Packer, Paragraph, TextRun, HeadingLevel, AlignmentType, Table, TableRow, TableCell,
  WidthType, ShadingType, BorderStyle, LevelFormat, PageBreak, Footer, Header, PageNumber,
} = require("docx");

// Usage: node build-voiceover-doc.js OUT.docx SECTIONS.json
// SECTIONS.json is either a list of sections (video 1's format) or an object:
// { "video": 2, "title": "...", "folder": "video-02/voice", "voice": "...", "pron": [[word, sound, type]], "pronNote": "...", "sections": [...] }
const data = JSON.parse(fs.readFileSync(process.argv[3] || path.join(__dirname, "sections.json"), "utf8"));
const OUT = process.argv[2];
const VIDEO1_PRON = [
  ["Saysh (seiche)", "SAYSH, one syllable: \"say\" with \"sh\" on the end", "saish, or say-sh"],
  ["Meteo-tsunami", "MEE-tee-oh soo-NAH-mee", "meetee-oh tsunami"],
  ["Noah (NOAA)", "NO-uh, like the name Noah", "Already spelled for the ear"],
  ["Riederer", "REE-der-er (my best guess)", "Reederer"],
  ["Pecararo", "peck-uh-RAH-roh (my best guess)", "Peckarahro"],
  ["Jaworski", "juh-WOR-skee", "Jaworskee"],
  ["Stempinski", "stem-PIN-skee", "Stempinskee"],
  ["Wilmette", "wil-MET", "Wilmet"],
  ["La Crosse", "luh-KROSS", "La Cross"],
  ["Ludington", "LUD-ing-tun", "Luddington"],
];
const meta = Array.isArray(data)
  ? { video: 1, title: "Lake Michigan Has Tsunamis, and Nobody in Chicago Saw This One Coming", folder: "video-01/voice", pron: VIDEO1_PRON,
      pronNote: "These are the words an AI voice is most likely to say wrong. The two surnames marked as my best guess are not confirmed." }
  : data;
const sections = Array.isArray(data) ? data : data.sections;

const FONT = "Arial";
const INK = "1F2933";
const MUTED = "5B6675";
const ACCENT = "1F5A7A";
const BOX = "EEF3F7";
const CONTENT_W = 9360; // US Letter, 1" margins

const words = (t) => t.split(/\s+/).filter(Boolean).length;
const totalWords = sections.reduce((n, s) => n + s.paras.reduce((m, p) => m + words(p), 0), 0);
const dur = (n) => {
  const sec = Math.round((n / 150) * 60);
  const m = Math.floor(sec / 60), s = sec % 60;
  if (m === 0) return `about ${s} seconds`;
  return `about ${m} min ${String(s).padStart(2, "0")} s`;
};

const p = (text, opts = {}) =>
  new Paragraph({
    spacing: { after: opts.after ?? 120, line: opts.line ?? 276 },
    alignment: opts.align,
    keepNext: opts.keepNext,
    children: Array.isArray(text) ? text : [new TextRun({ text, font: FONT, size: opts.size ?? 22, color: opts.color ?? INK, bold: opts.bold, italics: opts.italics })],
  });
const run = (text, o = {}) => new TextRun({ text, font: FONT, size: o.size ?? 22, color: o.color ?? INK, bold: o.bold, italics: o.italics });

const numbered = (text, ref = "steps") =>
  new Paragraph({ numbering: { reference: ref, level: 0 }, spacing: { after: 80, line: 276 }, children: [run(text)] });
const bullet = (children) =>
  new Paragraph({ numbering: { reference: "bullets", level: 0 }, spacing: { after: 80, line: 276 }, children: Array.isArray(children) ? children : [run(children)] });

const cell = (text, w, o = {}) =>
  new TableCell({
    width: { size: w, type: WidthType.DXA },
    shading: o.fill ? { type: ShadingType.CLEAR, color: "auto", fill: o.fill } : undefined,
    margins: { top: 80, bottom: 80, left: 120, right: 120 },
    children: [new Paragraph({ spacing: { after: 0 }, children: [run(text, { bold: o.bold, size: 20, color: o.color })] })],
  });

const pron = meta.pron;
const W = [2400, 4160, 2800];
const pronTable = new Table({
  width: { size: CONTENT_W, type: WidthType.DXA },
  columnWidths: W,
  rows: [
    new TableRow({ tableHeader: true, children: [
      cell("Word in the script", W[0], { fill: "DCE6EE", bold: true }),
      cell("How it should sound", W[1], { fill: "DCE6EE", bold: true }),
      cell("If the AI gets it wrong, type", W[2], { fill: "DCE6EE", bold: true }),
    ] }),
    ...pron.map((r) => new TableRow({ children: r.map((t, i) => cell(t, W[i])) })),
  ],
});

const children = [];

// ---------- Front page ----------
children.push(new Paragraph({ heading: HeadingLevel.TITLE, children: [new TextRun({ text: "Voiceover script", font: FONT })] }));
children.push(p([run(`Video ${meta.video}: `, { bold: true, size: 26, color: ACCENT }), run(meta.title, { size: 26, color: ACCENT })], { after: 80 }));
children.push(p(`${sections.length} sections · ${totalWords.toLocaleString("en-US")} words · about ${Math.round(totalWords / 150)} minutes`, { color: MUTED, after: 240 }));

children.push(new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun({ text: "How to use this script", font: FONT })] }));
[
  `Make one audio file per section. Each section starts on a new page and gives its file name, 01.mp3 to ${String(sections.length).padStart(2, "0")}.mp3.`,
  "Paste only the text inside the shaded box. Never paste the heading, the file name or the \"How to read it\" line: the AI will read them aloud.",
  "Use the \"How to read it\" line to set the tone. If your tool has a style or emotion setting, use it there; otherwise just pick the take that sounds closest.",
  `Use the same voice and the same settings for all ${sections.length} sections, so the video sounds like one narrator.`,
  "Listen to every section before you upload. If one word comes out wrong, fix it with the table below and regenerate only that paragraph.",
  `Upload the ${sections.length} files to ${meta.folder}/ in the GitHub repository.`,
].forEach((t) => children.push(numbered(t)));

children.push(new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun({ text: "Voice settings", font: FONT })] }));
[
  ...(meta.voice ? [meta.voice] : []),
  "Voice: a calm, low, clear documentary narrator with an American accent.",
  "Speed: slightly slower than normal. If your tool has a speed control, try about 0.9.",
  "Consistency: if your tool has a \"stability\" setting, set it fairly high so the voice does not change between sections.",
  "Emotion: keep it restrained. Turn down any \"style\" or \"exaggeration\" setting. The facts carry the drama.",
  "Format: MP3 at the highest quality your tool offers.",
].forEach((t) => children.push(bullet(t)));

children.push(new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun({ text: "What is already done for the AI", font: FONT })] }));
(meta.done || [
  "Every number, year and date is written out in words, so the AI cannot read 1954 as \"one thousand nine hundred and fifty-four\".",
  "Hard words are spelled the way they sound: \"saysh\" for seiche, \"meteo-tsunami\", and \"Noah\" for NOAA. The subtitles and on-screen text will use the correct spellings.",
  "Three dots (...) mark the short dramatic pauses. Most voice tools pause there. Leave them in.",
  "Quotes are set up so the AI reads them cleanly, and contractions such as \"it's\" and \"don't\" make it sound like natural speech.",
  "Longer pauses, music, waves, wind and thunder are added in the edit. Do not add sound effects or pause tags to the voice.",
]).forEach((t) => children.push(bullet(t)));

children.push(new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun({ text: "Words to listen for", font: FONT })] }));
children.push(p(meta.pronNote || "These are the words an AI voice is most likely to say wrong.", { color: MUTED }));
children.push(pronTable);

// ---------- Sections ----------
sections.forEach((s, i) => {
  const n = String(i + 1).padStart(2, "0");
  const wc = s.paras.reduce((m, t) => m + words(t), 0);
  children.push(new Paragraph({ children: [new PageBreak()] }));
  children.push(new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun({ text: `${n}  ${s.title}`, font: FONT })] }));
  children.push(p([run("Save as: ", { bold: true, color: MUTED, size: 20 }), run(`${n}.mp3`, { color: MUTED, size: 20 }), run(`     Length: ${dur(wc)}`, { color: MUTED, size: 20 })], { after: 160 }));
  children.push(p([run("How to read it (do not paste): ", { bold: true, italics: true, color: MUTED, size: 20 }), run(s.dir, { italics: true, color: MUTED, size: 20 })], { after: 240 }));
  s.paras.forEach((t, k) => {
    children.push(new Paragraph({
      spacing: { before: k === 0 ? 120 : 0, after: k === s.paras.length - 1 ? 120 : 180, line: 336 },
      shading: { type: ShadingType.CLEAR, color: "auto", fill: BOX },
      border: { left: { style: BorderStyle.SINGLE, size: 24, color: ACCENT, space: 12 } },
      indent: { left: 240, right: 240 },
      children: [new TextRun({ text: t, font: FONT, size: 25, color: INK })],
    }));
  });
});

const doc = new Document({
  creator: "Great Lakes Files",
  title: `Video ${meta.video} voiceover script`,
  styles: {
    default: { document: { run: { font: FONT, size: 22, color: INK } } },
    paragraphStyles: [
      { id: "Title", name: "Title", basedOn: "Normal", next: "Normal", run: { font: FONT, size: 48, bold: true, color: INK }, paragraph: { spacing: { before: 0, after: 120 }, keepNext: true } },
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true, run: { font: FONT, size: 34, bold: true, color: ACCENT }, paragraph: { spacing: { before: 0, after: 80 }, keepNext: true, outlineLevel: 0 } },
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
    headers: { default: new Header({ children: [new Paragraph({ alignment: AlignmentType.RIGHT, children: [run(`Video ${meta.video} voiceover script`, { size: 18, color: MUTED })] })] }) },
    footers: { default: new Footer({ children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ children: ["Page ", PageNumber.CURRENT, " of ", PageNumber.TOTAL_PAGES], font: FONT, size: 18, color: MUTED })] })] }) },
    children,
  }],
});

Packer.toBuffer(doc).then((buf) => { fs.writeFileSync(OUT, buf); console.log("wrote", OUT, "words", totalWords); });
