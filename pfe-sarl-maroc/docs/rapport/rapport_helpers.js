/* Génération du rapport final (Phase 7) — docx-js.
 * Times New Roman 12, marges 2cm, interligne simple, figures/tableaux
 * numérotés par chapitre, bibliographie [1][2]... — conformément au
 * cahier des charges (RÈGLES ABSOLUES, section "Rapport final").
 */
const {
  Document, Packer, Paragraph, TextRun, HeadingLevel, AlignmentType,
  Table, TableRow, TableCell, WidthType, ShadingType, ImageRun, PageBreak,
  TableOfContents, Header, Footer, PageNumber, BorderStyle, VerticalAlign,
  LevelFormat, PositionalTab, PositionalTabAlignment, PositionalTabLeader,
} = require("docx");
const fs = require("fs");

const CM = 566.929; // twips par centimetre
const MARGE = Math.round(2 * CM); // 2 cm
const FIG_DIR = "/home/claude/pfe-sarl-maroc/docs/rapport/figures";

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------
function p(text, opts = {}) {
  const { bold, italic, align, spacingAfter = 120, spacingBefore = 0 } = opts;
  return new Paragraph({
    alignment: align || AlignmentType.JUSTIFIED,
    spacing: { after: spacingAfter, before: spacingBefore },
    children: [new TextRun({ text, bold: !!bold, italics: !!italic })],
  });
}

function pRuns(runs, opts = {}) {
  const { align, spacingAfter = 120 } = opts;
  return new Paragraph({
    alignment: align || AlignmentType.JUSTIFIED,
    spacing: { after: spacingAfter },
    children: runs.map((r) => new TextRun(r)),
  });
}

function h1(text, pageBreak = true) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_1,
    pageBreakBefore: pageBreak,
    spacing: { before: 240, after: 240 },
    children: [new TextRun({ text, bold: true })],
  });
}

function h2(text) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_2,
    spacing: { before: 240, after: 160 },
    children: [new TextRun({ text, bold: true })],
  });
}

function h3(text) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_3,
    spacing: { before: 200, after: 120 },
    children: [new TextRun({ text, bold: true })],
  });
}

function bulletItem(text) {
  return new Paragraph({
    numbering: { reference: "bullets", level: 0 },
    spacing: { after: 60 },
    children: [new TextRun(text)],
  });
}

function caption(text) {
  return new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { before: 80, after: 240 },
    children: [new TextRun({ text, italics: true, size: 20 })],
  });
}

function figure(fileName, captionText, widthCm = 15) {
  const data = fs.readFileSync(`${FIG_DIR}/${fileName}`);
  return [
    new Paragraph({
      alignment: AlignmentType.CENTER,
      spacing: { before: 160, after: 0 },
      children: [
        new ImageRun({
          data,
          type: "png",
          transformation: { width: Math.round(widthCm * 37.8), height: Math.round(widthCm * 37.8 * 0.62) },
        }),
      ],
    }),
    caption(captionText),
  ];
}

function cell(text, opts = {}) {
  const { bold, shading, widthDxa, align } = opts;
  return new TableCell({
    width: widthDxa ? { size: widthDxa, type: WidthType.DXA } : undefined,
    shading: shading ? { fill: shading, type: ShadingType.CLEAR } : undefined,
    verticalAlign: VerticalAlign.CENTER,
    margins: { top: 60, bottom: 60, left: 100, right: 100 },
    children: [
      new Paragraph({
        alignment: align || AlignmentType.LEFT,
        children: [new TextRun({ text: String(text), bold: !!bold, size: 20 })],
      }),
    ],
  });
}

function table(headers, rows, widthsCm) {
  const widthsDxa = widthsCm.map((w) => Math.round(w * CM));
  const tableWidth = widthsDxa.reduce((a, b) => a + b, 0);
  const headerRow = new TableRow({
    tableHeader: true,
    children: headers.map((htext, i) => cell(htext, { bold: true, shading: "D9E4F0", widthDxa: widthsDxa[i] })),
  });
  const bodyRows = rows.map(
    (row) => new TableRow({ children: row.map((c, i) => cell(c, { widthDxa: widthsDxa[i] })) })
  );
  return new Table({
    width: { size: tableWidth, type: WidthType.DXA },
    columnWidths: widthsDxa,
    rows: [headerRow, ...bodyRows],
  });
}

function tableCaption(text) {
  return new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { before: 100, after: 60 },
    children: [new TextRun({ text, italics: true, size: 20, bold: true })],
  });
}

function tocEntry(text, page, level = 0) {
  return new Paragraph({
    spacing: { after: level === 0 ? 100 : 40 },
    indent: { left: level * 340 },
    children: [
      new TextRun({ text, bold: level === 0, size: level === 0 ? 22 : 20 }),
      new TextRun({
        children: [
          new PositionalTab({
            alignment: PositionalTabAlignment.RIGHT,
            leader: PositionalTabLeader.DOT,
          }),
        ],
      }),
      new TextRun({ text: String(page), size: level === 0 ? 22 : 20 }),
    ],
  });
}

const PAGE_BREAK = new Paragraph({ children: [new PageBreak()] });

// ---------------------------------------------------------------------------
// PAGE DE GARDE
// ---------------------------------------------------------------------------
const pageDeGarde = [
  new Paragraph({ spacing: { after: 400 }, children: [new TextRun({ text: "[Nom de l'établissement]", size: 24 })], alignment: AlignmentType.CENTER }),
  new Paragraph({ spacing: { after: 200 }, children: [new TextRun({ text: "[Filière / Département]", size: 24 })], alignment: AlignmentType.CENTER }),
  new Paragraph({ spacing: { after: 800 }, children: [new TextRun({ text: "Projet de Fin d'Études", size: 24, italics: true })], alignment: AlignmentType.CENTER }),
  new Paragraph({ spacing: { before: 600, after: 200 }, children: [new TextRun({ text: "JURIS-IA", size: 56, bold: true })], alignment: AlignmentType.CENTER }),
  new Paragraph({
    spacing: { after: 600 },
    alignment: AlignmentType.CENTER,
    children: [new TextRun({
      text: "Assistant intelligent d'accompagnement à la création de SARL et SARL AU au Maroc — " +
        "chatbot juridique (RAG), extraction OCR de la Carte d'Identité Nationale et système expert anti-rejet",
      size: 26, bold: true,
    })],
  }),
  new Paragraph({ spacing: { before: 800, after: 100 }, children: [new TextRun({ text: "Présenté par :", size: 24 })], alignment: AlignmentType.CENTER }),
  new Paragraph({ spacing: { after: 400 }, children: [new TextRun({ text: "[Nom de l'étudiant·e]", size: 24, bold: true })], alignment: AlignmentType.CENTER }),
  new Paragraph({ spacing: { after: 100 }, children: [new TextRun({ text: "Encadré par :", size: 24 })], alignment: AlignmentType.CENTER }),
  new Paragraph({ spacing: { after: 600 }, children: [new TextRun({ text: "[Nom de l'encadrant·e]", size: 24, bold: true })], alignment: AlignmentType.CENTER }),
  new Paragraph({ spacing: { before: 1000 }, children: [new TextRun({ text: "Année universitaire [XXXX-XXXX]", size: 22 })], alignment: AlignmentType.CENTER }),
  new Paragraph({ children: [new TextRun({ text: "Rédigé le 20 juillet 2026", size: 20, italics: true })], alignment: AlignmentType.CENTER }),
];

// ---------------------------------------------------------------------------
// REMERCIEMENTS
// ---------------------------------------------------------------------------
const remerciements = [
  h1("Remerciements", true),
  p("Nous tenons à exprimer notre sincère gratitude à toutes les personnes qui ont contribué, de près ou de loin, à la réalisation de ce projet de fin d'études."),
  p("Nos remerciements s'adressent en premier lieu à notre encadrant·e pédagogique, pour sa disponibilité, ses conseils avisés et son accompagnement méthodologique tout au long de ce projet, notamment dans la structuration par phases successives et la rigueur exigée sur la traçabilité des sources juridiques."),
  p("Nous remercions également le corps enseignant et administratif de [Nom de l'établissement] pour la qualité de la formation dispensée, ainsi que pour les moyens mis à disposition pour la conduite de ce travail."),
  p("Enfin, nous adressons nos remerciements à nos familles et proches pour leur soutien constant durant cette période de travail intensif."),
];

// ---------------------------------------------------------------------------
// RESUME / ABSTRACT
// ---------------------------------------------------------------------------
const resume = [
  h1("Résumé", true),
  p(
    "La création d'une société à responsabilité limitée (SARL) ou d'une SARL à associé " +
    "unique (SARL AU) au Maroc implique un enchaînement de démarches administratives " +
    "réparties entre plusieurs organismes (OMPIC, DGI, greffe du tribunal de commerce, " +
    "CNSS). Ce projet de fin d'études propose Juris-IA, un système logiciel " +
    "d'accompagnement combinant trois modules complémentaires : un chatbot juridique " +
    "fondé sur une architecture de génération augmentée par récupération (RAG), un " +
    "module d'extraction automatique de l'identité par reconnaissance optique de " +
    "caractères (OCR) appliqué à la Carte d'Identité Nationale (CIN), et un système " +
    "expert à base de règles détectant en amont les causes fréquentes de rejet d'un " +
    "dossier de création."
  ),
  p(
    "Le chatbot juridique s'appuie sur un corpus documentaire fermé (loi n°5-96, notes " +
    "de la Direction Générale des Impôts, documentation de l'OMPIC et guides pratiques) " +
    "et combine recherche sémantique (ChromaDB, sentence-transformers) et recherche " +
    "lexicale (BM25), fusionnées par Reciprocal Rank Fusion puis reclassées selon la " +
    "hiérarchie documentaire des sources, avant génération de la réponse par un modèle " +
    "de langage (API Groq) contraint de citer ses sources. Le module OCR (EasyOCR, " +
    "OpenCV) extrait nom, prénom, numéro de CIN et date de naissance. Le système expert " +
    "évalue la conformité d'un dossier à partir de onze règles documentées, chacune " +
    "reliée à sa source et à son niveau d'autorité (texte de loi, source officielle ou " +
    "guide pratique)."
  ),
  p(
    "L'ensemble est exposé via une API FastAPI sécurisée par authentification JWT et " +
    "contrôle d'accès par rôle (entrepreneur, juriste, administrateur), et une interface " +
    "Streamlit à cinq pages. Le développement, conduit par phases successives (cadrage, " +
    "conception UML, architecture, système expert, OCR, RAG, intégration), a été " +
    "systématiquement vérifié : 89 tests automatisés passent avec une couverture de " +
    "code de 95 %, et plusieurs contradictions internes au corpus documentaire ont été " +
    "explicitement signalées plutôt qu'arbitrées arbitrairement."
  ),
  p("Mots-clés : SARL, SARL AU, Maroc, RAG, système expert, OCR, FastAPI, ChromaDB, chatbot juridique, création d'entreprise.", { italic: true }),
  h1("Abstract", true),
  p(
    "Creating a limited liability company (SARL) or a single-shareholder SARL (SARL AU) " +
    "in Morocco involves a sequence of administrative procedures spread across several " +
    "institutions (OMPIC, the tax authority, the commercial court registry, and the " +
    "social security fund CNSS). This capstone project presents Juris-IA, a software " +
    "assistant combining three complementary modules: a legal chatbot built on a " +
    "Retrieval-Augmented Generation (RAG) architecture, an Optical Character " +
    "Recognition (OCR) module that extracts identity fields from the Moroccan National " +
    "ID card, and a rule-based expert system that proactively detects frequent causes " +
    "of application rejection."
  ),
  p(
    "The legal chatbot relies on a closed documentary corpus (Law No. 5-96, notes from " +
    "the tax authority, OMPIC documentation, and practical guides) and combines " +
    "semantic search (ChromaDB, sentence-transformers) with lexical search (BM25), " +
    "fused through Reciprocal Rank Fusion and re-ranked according to the documentary " +
    "source hierarchy, before an answer is generated by a language model (Groq API) " +
    "instructed to cite its sources. The OCR module (EasyOCR, OpenCV) extracts last " +
    "name, first name, ID number and date of birth. The expert system evaluates the " +
    "conformity of a dossier against eleven documented rules, each traceable to its " +
    "source and authority level (statute, official source, or practical guide)."
  ),
  p(
    "The whole system is exposed through a FastAPI backend secured with JWT " +
    "authentication and role-based access control (entrepreneur, legal expert, " +
    "administrator), and a five-page Streamlit interface. Development proceeded " +
    "through successive phases (scoping, UML design, architecture, expert system, " +
    "OCR, RAG, integration), each systematically verified: 89 automated tests pass with " +
    "95% code coverage, and several internal contradictions in the documentary corpus " +
    "were explicitly flagged rather than arbitrarily resolved."
  ),
  p("Keywords: SARL, SARL AU, Morocco, RAG, expert system, OCR, FastAPI, ChromaDB, legal chatbot, business creation.", { italic: true }),
];

// ---------------------------------------------------------------------------
// ABREVIATIONS
// ---------------------------------------------------------------------------
const abrevRows = [
  ["API", "Application Programming Interface (interface de programmation applicative)"],
  ["BM25", "Best Matching 25 (algorithme de pondération lexicale en recherche d'information)"],
  ["CIN", "Carte d'Identité Nationale"],
  ["CNSS", "Caisse Nationale de Sécurité Sociale"],
  ["DGI", "Direction Générale des Impôts"],
  ["DTO", "Data Transfer Object (objet de transfert de données)"],
  ["ERD", "Entity-Relationship Diagram (diagramme entité-association)"],
  ["IS", "Impôt sur les Sociétés"],
  ["JWT", "JSON Web Token"],
  ["OCR", "Optical Character Recognition (reconnaissance optique de caractères)"],
  ["OMPIC", "Office Marocain de la Propriété Industrielle et Commerciale"],
  ["ORM", "Object-Relational Mapping (correspondance objet-relationnel)"],
  ["PFE", "Projet de Fin d'Études"],
  ["RAG", "Retrieval-Augmented Generation (génération augmentée par récupération)"],
  ["RC", "Registre de Commerce"],
  ["RRF", "Reciprocal Rank Fusion (fusion de classements par rang réciproque)"],
  ["SARL", "Société à Responsabilité Limitée"],
  ["SARL AU", "Société à Responsabilité Limitée à Associé Unique"],
  ["SQL", "Structured Query Language"],
  ["TVA", "Taxe sur la Valeur Ajoutée"],
  ["UML", "Unified Modeling Language (langage de modélisation unifié)"],
];
const abreviations = [
  h1("Liste des abréviations", true),
  table(["Sigle", "Signification"], abrevRows, [3, 13]),
];

// ---------------------------------------------------------------------------
// TABLE DES MATIERES
// ---------------------------------------------------------------------------
const tableDesMatieres = [
  h1("Table des matières", true),
  tocEntry("Remerciements", 3),
  tocEntry("Résumé", 4),
  tocEntry("Abstract", 5),
  tocEntry("Liste des abréviations", 6),
  tocEntry("Liste des figures et des tableaux", 8),
  tocEntry("Chapitre 1 — Introduction générale", 9),
  tocEntry("1.1 Contexte et analyse du besoin", 9, 1),
  tocEntry("1.2 Problématique", 9, 1),
  tocEntry("1.3 Objectifs du projet", 9, 1),
  tocEntry("1.4 Périmètre et limites assumées", 10, 1),
  tocEntry("1.5 Plan du rapport", 10, 1),
  tocEntry("Chapitre 2 — Cadre juridique et contexte", 11),
  tocEntry("2.1 Sources documentaires et hiérarchie", 11, 1),
  tocEntry("2.2 Étapes de création d'une SARL/SARL AU", 11, 1),
  tocEntry("2.3 Comparatifs SARL / SARL AU / Auto-entrepreneur", 11, 1),
  tocEntry("2.4 Fiscalité applicable (synthèse)", 12, 1),
  tocEntry("2.5 Contradictions identifiées dans le corpus", 12, 1),
  tocEntry("Chapitre 3 — Analyse et conception (UML)", 13),
  tocEntry("3.1 Acteurs et besoins fonctionnels/non fonctionnels", 13, 1),
  tocEntry("3.2 Diagramme de cas d'utilisation", 13, 1),
  tocEntry("3.3 Diagramme de classes", 14, 1),
  tocEntry("3.4 Diagrammes de séquence", 14, 1),
  tocEntry("3.5 Modèle de données", 15, 1),
  tocEntry("Chapitre 4 — Architecture technique globale", 16),
  tocEntry("4.1 Stack technologique imposée et justifications", 16, 1),
  tocEntry("4.2 Architecture globale et arborescence du dépôt", 16, 1),
  tocEntry("4.3 Principes d'architecture", 17, 1),
  tocEntry("4.4 Reproductibilité et configuration", 17, 1),
  tocEntry("Chapitre 5 — Système expert anti-rejet", 18),
  tocEntry("5.1 Principe et structure d'une règle", 18, 1),
  tocEntry("5.2 Catalogue synthétique des règles", 18, 1),
  tocEntry("5.3 Moteur d'évaluation et statut global", 18, 1),
  tocEntry("5.4 Dossiers synthétiques et résultats de tests", 18, 1),
  tocEntry("Chapitre 6 — Module OCR d'extraction de CIN", 20),
  tocEntry("6.1 Choix d'EasyOCR : justification", 20, 1),
  tocEntry("6.2 Pipeline d'extraction", 20, 1),
  tocEntry("6.3 Gestion des erreurs et intégration au dossier", 20, 1),
  tocEntry("6.4 Tests et limites", 21, 1),
  tocEntry("Chapitre 7 — Module RAG juridique", 22),
  tocEntry("7.1 Corpus documentaire fermé et pipeline d'indexation", 22, 1),
  tocEntry("7.2 Recherche hybride : fusion sémantique et lexicale", 22, 1),
  tocEntry("7.3 Reranking par niveau documentaire", 22, 1),
  tocEntry("7.4 Génération de la réponse et garde-fous anti-hallucination", 23, 1),
  tocEntry("7.5 Tests et limites", 23, 1),
  tocEntry("Chapitre 8 — Intégration, authentification et interface utilisateur", 24),
  tocEntry("8.1 Assemblage des trois modules", 24, 1),
  tocEntry("8.2 Authentification JWT et contrôle d'accès par rôle", 24, 1),
  tocEntry("8.3 Interface utilisateur Streamlit", 24, 1),
  tocEntry("8.4 Tests end-to-end", 24, 1),
  tocEntry("Chapitre 9 — Résultats, qualité et discussion", 25),
  tocEntry("9.1 Synthèse des résultats de tests par phase", 25, 1),
  tocEntry("9.2 Qualité du code", 25, 1),
  tocEntry("9.3 Limitations de l'environnement de vérification", 25, 1),
  tocEntry("9.4 Discussion critique", 25, 1),
  tocEntry("Chapitre 10 — Conclusion générale, limites et perspectives", 27),
  tocEntry("10.1 Bilan du projet", 27, 1),
  tocEntry("10.2 Limites", 27, 1),
  tocEntry("10.3 Perspectives d'évolution", 27, 1),
  tocEntry("Bibliographie", 28),
];

const listeFiguresTableaux = [
  PAGE_BREAK,
  h2("Liste des figures"),
  p("Figure 3.1 — Diagramme de cas d'utilisation"),
  p("Figure 3.2 — Diagramme de classes (simplifié)"),
  p("Figure 3.3 — Diagramme de séquence : évaluation d'un dossier"),
  p("Figure 3.4 — Modèle de données (ERD simplifié)"),
  p("Figure 4.1 — Architecture globale du système"),
  p("Figure 7.1 — Pipeline RAG complet (indexation et requête)"),
  h2("Liste des tableaux"),
  p("Tableau 2.1 — Comparatif SARL / SARL AU"),
  p("Tableau 2.2 — Comparatif Auto-entrepreneur / SARL AU"),
  p("Tableau 2.3 — Hiérarchie des sources documentaires"),
  p("Tableau 2.4 — Contradictions identifiées dans le corpus"),
  p("Tableau 4.1 — Stack technologique imposée"),
  p("Tableau 5.1 — Catalogue synthétique des règles du système expert"),
  p("Tableau 6.1 — Comparatif EasyOCR / Tesseract"),
  p("Tableau 9.1 — Synthèse des résultats de tests par phase"),
];

module.exports = {
  p, pRuns, h1, h2, h3, bulletItem, caption, figure, cell, table, tableCaption, tocEntry, PAGE_BREAK,
  pageDeGarde, remerciements, resume, abreviations, tableDesMatieres, listeFiguresTableaux,
  Document, Packer, Paragraph, TextRun, HeadingLevel, AlignmentType, Table, TableRow,
  TableCell, WidthType, ShadingType, ImageRun, PageBreak, TableOfContents, Header, Footer,
  PageNumber, BorderStyle, VerticalAlign, LevelFormat, MARGE,
};
