const fs = require("fs");
const H = require("./rapport_helpers.js");
const C15 = require("./chapitres_1_5.js");
const C610 = require("./chapitres_6_10.js");
const {
  Document, Packer, Paragraph, TextRun, AlignmentType, Header, Footer,
  PageNumber, LevelFormat, MARGE,
} = H;

const footer = new Footer({
  children: [
    new Paragraph({
      alignment: AlignmentType.CENTER,
      children: [
        new TextRun({ text: "Juris-IA — Rapport de PFE — Page ", size: 18 }),
        new TextRun({ children: [PageNumber.CURRENT], size: 18 }),
        new TextRun({ text: " / ", size: 18 }),
        new TextRun({ children: [PageNumber.TOTAL_PAGES], size: 18 }),
      ],
    }),
  ],
});

const doc = new Document({
  numbering: {
    config: [
      {
        reference: "bullets",
        levels: [
          { level: 0, format: LevelFormat.BULLET, text: "•", alignment: AlignmentType.LEFT,
            style: { paragraph: { indent: { left: 720, hanging: 360 } } } },
        ],
      },
    ],
  },
  styles: {
    default: {
      document: { run: { font: "Times New Roman", size: 24 } }, // 12pt
      heading1: { run: { font: "Times New Roman", size: 32, bold: true, color: "1F3864" }, paragraph: { spacing: { before: 240, after: 240 } } },
      heading2: { run: { font: "Times New Roman", size: 28, bold: true, color: "2C4A6E" }, paragraph: { spacing: { before: 200, after: 140 } } },
      heading3: { run: { font: "Times New Roman", size: 26, bold: true, color: "2C4A6E" }, paragraph: { spacing: { before: 160, after: 100 } } },
    },
  },
  sections: [
    // Page de garde (pas de numero de page, pas d'en-tete)
    {
      properties: { page: { margin: { top: MARGE, bottom: MARGE, left: MARGE, right: MARGE } } },
      children: H.pageDeGarde,
    },
    // Corps du rapport
    {
      properties: { page: { margin: { top: MARGE, bottom: MARGE, left: MARGE, right: MARGE } } },
      footers: { default: footer },
      children: [
        ...H.remerciements,
        ...H.resume,
        ...H.abreviations,
        ...H.tableDesMatieres,
        ...H.listeFiguresTableaux,
        ...C15.chapitre1,
        ...C15.chapitre2,
        ...C15.chapitre3,
        ...C15.chapitre4,
        ...C15.chapitre5,
        ...C610.chapitre6,
        ...C610.chapitre7,
        ...C610.chapitre8,
        ...C610.chapitre9,
        ...C610.chapitre10,
        H.PAGE_BREAK,
        ...C610.bibliographie,
      ],
    },
  ],
});

Packer.toBuffer(doc).then((buffer) => {
  fs.writeFileSync("/home/claude/pfe-sarl-maroc/docs/rapport/Rapport_PFE_Juris-IA.docx", buffer);
  console.log("Rapport genere avec succes.");
});
