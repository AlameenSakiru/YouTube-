// Word file with the Flow prompts laid out for copy-and-paste into a batch tool:
// one prompt per paragraph, nothing else between them.
const fs = require("fs");
const { Document, Packer, Paragraph, TextRun, HeadingLevel, AlignmentType, PageBreak, Header, Footer, PageNumber, LevelFormat } = require("docx");
const [OUT, PROMPTS, THUMBS, OPTS] = process.argv.slice(2);
const opt = OPTS ? JSON.parse(fs.readFileSync(OPTS, "utf8")) : {};
const prompts = fs.readFileSync(PROMPTS, "utf8").trim().split("\n");
const thumbs = fs.readFileSync(THUMBS, "utf8").trim().split("\n");
const FONT = "Arial", INK = "1F2933", MUTED = "5B6675", ACCENT = "1F5A7A";
const run = (t, o = {}) => new TextRun({ text: t, font: FONT, size: o.size ?? 22, color: o.color ?? INK, bold: o.bold });
const para = (t, o = {}) => new Paragraph({ spacing: { after: o.after ?? 120, line: 276 }, children: [run(t, o)] });
const step = (t) => new Paragraph({ numbering: { reference: "steps", level: 0 }, spacing: { after: 80, line: 276 }, children: [run(t)] });
const promptPara = (t) => new Paragraph({ spacing: { after: 200, line: 264 }, keepLines: true, children: [run(t, { size: 20 })] });
const h = (t, level) => new Paragraph({ heading: level, children: [new TextRun({ text: t, font: FONT })] });

const children = [
  h(opt.title || "Flow prompts for automation", HeadingLevel.TITLE),
  para("Video 1: Lake Michigan Has Tsunamis, and Nobody in Chicago Saw This One Coming", { color: ACCENT, size: 24, after: 80 }),
  para(opt.summary || `${prompts.length} image prompts, then ${thumbs.length} thumbnail prompts on the last page.`, { color: MUTED, after: 240 }),
  h("How to use it", HeadingLevel.HEADING_2),
  step("Set your Flow tool to the wide 16:9 shape and the highest image quality your plan allows."),
  step("Go to the next page. Select from the first word of the first prompt to the last word of prompt " + prompts.length + ", copy, and paste it into your tool."),
  step(opt.order || "Each prompt is one paragraph, so it pastes as one line. Line 1 is image 001, line 2 is image 002, and so on."),
  step("Run the thumbnail prompts on the last page separately."),
  step("Send me the images when they are done, whatever the tool names them. I will match each one to its shot."),
  para("Do not copy this first page into your tool. If your tool needs an empty line between prompts, tell me and I will send that version.", { color: MUTED, after: 0 }),
  new Paragraph({ children: [new PageBreak()] }),
  ...prompts.map(promptPara),
  new Paragraph({ children: [new PageBreak()] }),
  h("Thumbnail prompts (run separately)", HeadingLevel.HEADING_2),
  para("Save them as thumb-1, thumb-2 and thumb-3.", { color: MUTED, after: 200 }),
  ...thumbs.map(promptPara),
];

const doc = new Document({
  title: "Video 1 Flow prompts for automation",
  styles: {
    default: { document: { run: { font: FONT, size: 22, color: INK } } },
    paragraphStyles: [
      { id: "Title", name: "Title", basedOn: "Normal", next: "Normal", run: { font: FONT, size: 44, bold: true, color: INK }, paragraph: { spacing: { before: 0, after: 120 }, keepNext: true } },
      { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true, run: { font: FONT, size: 26, bold: true, color: INK }, paragraph: { spacing: { before: 200, after: 100 }, keepNext: true, outlineLevel: 1 } },
    ],
  },
  numbering: { config: [{ reference: "steps", levels: [{ level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 540, hanging: 360 } } } }] }] },
  sections: [{
    properties: { page: { size: { width: 12240, height: 15840 }, margin: { top: 1440, bottom: 1440, left: 1440, right: 1440 } } },
    headers: { default: new Header({ children: [new Paragraph({ alignment: AlignmentType.RIGHT, children: [run("Video 1 Flow prompts", { size: 18, color: MUTED })] })] }) },
    footers: { default: new Footer({ children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ children: ["Page ", PageNumber.CURRENT, " of ", PageNumber.TOTAL_PAGES], font: FONT, size: 18, color: MUTED })] })] }) },
    children,
  }],
});
Packer.toBuffer(doc).then((b) => { fs.writeFileSync(OUT, b); console.log("wrote", OUT, prompts.length, "prompts"); });
