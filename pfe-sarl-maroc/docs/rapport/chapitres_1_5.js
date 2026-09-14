const H = require("./rapport_helpers.js");
const { p, pRuns, h1, h2, h3, bulletItem, figure, table, tableCaption, PAGE_BREAK } = H;

// ===========================================================================
// CHAPITRE 1 — INTRODUCTION GENERALE
// ===========================================================================
const chapitre1 = [
  h1("Chapitre 1 — Introduction générale"),

  h2("1.1 Contexte et analyse du besoin"),
  p("La création d'une société commerciale au Maroc, notamment sous la forme d'une Société à Responsabilité Limitée (SARL) ou d'une SARL à associé unique (SARL AU), constitue une étape déterminante pour tout porteur de projet entrepreneurial. Cette démarche implique un enchaînement de formalités administratives réparties entre plusieurs institutions : l'Office Marocain de la Propriété Industrielle et Commerciale (OMPIC) pour le certificat négatif, la Direction Générale des Impôts (DGI) pour l'enregistrement des actes et la taxe professionnelle, le greffe du tribunal de commerce pour l'immatriculation au Registre de Commerce, et la Caisse Nationale de Sécurité Sociale (CNSS) pour l'affiliation [1][4][5]."),
  p("Un porteur de projet non initié à ces procédures doit collecter et interpréter lui-même les pièces justificatives requises (certificat négatif, statuts, attestation de blocage bancaire, pièces d'identité des associés), avec un risque non négligeable d'erreur ou d'omission pouvant entraîner un rejet de dossier lors de son dépôt. Ce constat, établi à partir de l'analyse du corpus documentaire disponible (voir chapitre 2), motive la conception d'un outil numérique d'accompagnement."),

  h2("1.2 Problématique"),
  p("La problématique retenue pour ce projet peut être formulée ainsi : comment concevoir un système logiciel capable d'assister un porteur de projet dans la création d'une SARL ou d'une SARL AU au Maroc, en combinant recherche documentaire juridique fiable, extraction automatisée de données d'identité et détection explicable des causes de rejet de dossier, tout en garantissant la traçabilité de chaque réponse à une source documentaire de niveau connu ?", { spacingAfter: 240 }),

  h2("1.3 Objectifs du projet"),
  h3("1.3.1 Objectifs fonctionnels"),
  bulletItem("Répondre en langage naturel aux questions relatives à la création de SARL/SARL AU, avec citation systématique de la source et de son niveau documentaire ;"),
  bulletItem("Extraire automatiquement, à partir d'une image de Carte d'Identité Nationale (CIN), les champs nom, prénom, numéro de CIN et date de naissance ;"),
  bulletItem("Évaluer la conformité d'un dossier de création à partir de règles documentées et tracables, avant son dépôt effectif auprès des administrations ;"),
  bulletItem("Proposer une interface utilisateur unique donnant accès à ces trois fonctionnalités, avec gestion des rôles applicatifs."),
  h3("1.3.2 Objectifs techniques"),
  bulletItem("Concevoir une architecture modulaire et testable (séparation API / services / repositories / modèles), conforme aux principes SOLID ;"),
  bulletItem("Mettre en œuvre un pipeline RAG complet, de l'extraction du corpus à la génération de réponses citées ;"),
  bulletItem("Implémenter un système expert entièrement fondé sur des règles explicites, sans recours à l'apprentissage automatique ;"),
  bulletItem("Garantir la reproductibilité du projet (installation et exécution sans intervention manuelle) et une couverture de tests significative à chaque étape du développement."),

  h2("1.4 Périmètre et limites assumées"),
  p("Le périmètre fonctionnel du système est volontairement restreint à la SARL et à la SARL AU ; les autres formes juridiques mentionnées dans le corpus documentaire (SA, SAS, SNC, SCS, SCA, coopératives, associations, auto-entrepreneur) ne sont couvertes qu'à titre informationnel par le chatbot, sans évaluation par le système expert. Le corpus documentaire utilisé est fermé : il se limite aux six documents fournis en début de projet (voir chapitre 2), à l'exclusion de toute recherche sur Internet. Cette fermeture du corpus, bien que limitant l'exhaustivité des réponses possibles, garantit la traçabilité de chaque affirmation à une source identifiée et évite l'introduction d'informations juridiques non vérifiées."),
  p("Certaines limitations techniques de l'environnement de développement et de vérification sont également assumées et documentées : les modèles d'apprentissage profond (EasyOCR, sentence-transformers), la base vectorielle ChromaDB et l'API Groq n'ont pas pu être exercés de bout en bout dans l'environnement de vérification utilisé pour ce projet, en raison de contraintes réseau et de la taille des modèles concernés. Ce point est développé au chapitre 9."),

  h2("1.5 Plan du rapport"),
  p("Ce rapport est structuré en dix chapitres. Le chapitre 2 présente le cadre juridique et le corpus documentaire mobilisé. Le chapitre 3 détaille la conception UML du système (besoins, cas d'utilisation, classes, séquences, modèle de données). Le chapitre 4 décrit l'architecture technique globale. Les chapitres 5, 6 et 7 sont consacrés respectivement au système expert anti-rejet, au module OCR et au module RAG juridique. Le chapitre 8 traite de l'intégration des trois modules, de l'authentification et de l'interface utilisateur. Le chapitre 9 présente une synthèse des résultats de tests et une discussion critique. Le chapitre 10 conclut le rapport et ouvre sur les limites et perspectives du projet."),
];

// ===========================================================================
// CHAPITRE 2 — CADRE JURIDIQUE ET CONTEXTE
// ===========================================================================
const hierarchieRows = [
  ["1 — Primaire", "Loi n°5-96 sur la SARL (et autres formes visées)", "Texte de loi, autorité maximale"],
  ["2 — Officielle", "OMPIC, DGI (notes IS et TVA), Dar Al Moukawil (Attijariwafa bank, certifié Mazars)", "Institution publique ou source institutionnelle certifiée"],
  ["3 — Pratique", "Guide de vulgarisation juridique", "Documentation pratique secondaire, jamais citée comme source légale directe"],
];

const sarlAuRows = [
  ["Nombre d'associés", "1 (associé unique)", "2 à 50"],
  ["Personnalité morale", "Oui, distincte de l'associé", "Oui"],
  ["Responsabilité", "Limitée aux apports", "Limitée aux apports de chacun"],
  ["Gérance", "L'associé unique peut être son propre gérant", "Gérant désigné parmi ou hors associés"],
  ["Capital minimum", "Aucun (selon OMPIC/Dar Al Moukawil/guide — voir §2.5)", "Idem — voir §2.5"],
];

const autoEntSarlRows = [
  ["Nature juridique", "Personne physique", "Société commerciale (personnalité morale propre)"],
  ["Responsabilité", "Illimitée (patrimoine personnel exposé)", "Limitée aux apports"],
  ["Plafond de chiffre d'affaires", "500 000 MAD/an (commerce) / 200 000 MAD/an (services)", "Aucun"],
  ["Fiscalité", "Impôt libératoire sur le CA (1 % commerce / 2 % services)", "Impôt sur les sociétés (IS), taux progressif"],
  ["Comptabilité", "Simplifiée, pas de bilan annuel obligatoire", "Rigoureuse, bilan annuel obligatoire"],
  ["Registre", "RNAE (ae.gov.ma)", "Registre de Commerce"],
];

const contradictionsRows = [
  ["Capital minimum SARL", "100 000 DH minimum (art. 46 du texte fourni)", "Aucun minimum depuis la réforme de 2006", "Aucune règle de rejet codée sur ce point (§5.2)"],
  ["Validité du certificat négatif", "3 mois (FAQ OMPIC, guide de vulgarisation)", "« un an » (infographie Dar Al Moukawil, p.7)", "3 mois retenu (majorité des sources), divergence documentée dans le message d'anomalie"],
  ["Droit d'enregistrement des statuts", "1 % du capital, minimum 1000 DH (OMPIC)", "Droit fixe 1000 DH si capital ≤ 500 000 DH, sinon 1 % (Dar Al Moukawil)", "Traité en rappel informatif (non bloquant), les deux formules sont présentées"],
];

const chapitre2 = [
  h1("Chapitre 2 — Cadre juridique et contexte de la création d'entreprise au Maroc"),

  h2("2.1 Sources documentaires et hiérarchie"),
  p("Conformément à la méthodologie retenue pour ce projet, le corpus documentaire est fermé : il se compose exclusivement des six documents suivants, classés selon trois niveaux d'autorité décroissante. Aucune information extérieure à ce corpus n'a été mobilisée pour la construction des règles métier ou des réponses du chatbot."),
  tableCaption("Tableau 2.3 — Hiérarchie des sources documentaires"),
  table(["Niveau", "Sources", "Justification"], hierarchieRows, [3, 7, 6]),
  p("Les six documents du corpus sont : la loi n°5-96 relative à la SNC, la SCS, la SCA, la SARL et la société en participation [1] ; la note de synthèse de la DGI sur l'Impôt sur les Sociétés [2] ; la note de synthèse de la DGI sur la Taxe sur la Valeur Ajoutée [3] ; la page « Création et vie de l'entreprise » du site de l'OMPIC [4] ; le guide « Démarches administratives de création d'entreprise » de Dar Al Moukawil (Attijariwafa bank, certifié Mazars) [5] ; et un guide de vulgarisation juridique sur la création de SARL/SARL AU [6]."),

  h2("2.2 Étapes de création d'une SARL/SARL AU (synthèse)"),
  p("D'après les sources de niveau 1 et 2 [1][4][5], la création d'une SARL ou SARL AU suit un enchaînement d'étapes principales : (1) obtention du certificat négatif auprès de l'OMPIC, attestant la disponibilité de la dénomination sociale ; (2) rédaction et signature des statuts par l'ensemble des associés ; (3) blocage du capital social en banque, formalité supprimée pour les sociétés dont le capital ne dépasse pas 100 000 DH [4][5] ; (4) enregistrement des actes auprès de la Direction Régionale des Impôts ; (5) inscription à la taxe professionnelle ; (6) immatriculation au Registre de Commerce, qui confère la personnalité morale à la société [1, art. 2] ; (7) affiliation à la CNSS si la société emploie des salariés ; (8) publication d'un extrait des statuts au Journal d'Annonces Légales et au Bulletin Officiel [1, art. 96]."),

  h2("2.3 Comparatifs SARL / SARL AU / Auto-entrepreneur"),
  tableCaption("Tableau 2.1 — Comparatif SARL / SARL AU"),
  table(["Critère", "SARL AU", "SARL"], sarlAuRows, [4, 6.5, 6.5]),
  tableCaption("Tableau 2.2 — Comparatif Auto-entrepreneur / SARL AU"),
  table(["Critère", "Auto-entrepreneur", "SARL AU"], autoEntSarlRows, [4, 6.5, 6.5]),

  h2("2.4 Fiscalité applicable (synthèse)"),
  p("La SARL et la SARL AU sont soumises à l'Impôt sur les Sociétés (IS), au taux normal de 30 % (37 % pour les établissements de crédit et assimilés), avec des taux spécifiques réduits pour certaines catégories d'entreprises (zones franches, Casablanca Finance City, exportateurs, etc.) [2]. Une cotisation minimale s'applique, sauf exonération pendant les 36 premiers mois d'activité [2]. La Taxe sur la Valeur Ajoutée (TVA), au taux normal de 20 %, s'applique aux opérations de nature industrielle, commerciale, artisanale ou libérale réalisées au Maroc, sous réserve d'exonérations et de taux réduits (7 %, 10 %, 14 %) définis par le Code Général des Impôts [3]."),

  h2("2.5 Contradictions identifiées dans le corpus"),
  p("L'analyse croisée des six documents du corpus a révélé trois contradictions ou divergences factuelles, qu'il n'appartient pas au système de trancher arbitrairement (conformément au principe méthodologique retenu : signaler explicitement une information manquante ou contradictoire plutôt que de la supposer). Ces divergences sont résumées dans le tableau 2.4 et détaillées dans le catalogue de règles (chapitre 5) et dans le journal de décisions du projet."),
  tableCaption("Tableau 2.4 — Contradictions identifiées dans le corpus"),
  table(["Point", "Version A", "Version B", "Traitement retenu"], contradictionsRows, [3.5, 4, 4, 5]),
];

// ===========================================================================
// CHAPITRE 3 — ANALYSE ET CONCEPTION (UML)
// ===========================================================================
const besoinsFuncRows = [
  ["BF-01", "Entrepreneur", "Poser une question juridique et recevoir une réponse citée"],
  ["BF-02", "Entrepreneur", "Extraire l'identité depuis une image de CIN"],
  ["BF-03", "Entrepreneur", "Soumettre un dossier structuré au système expert"],
  ["BF-04", "Entrepreneur", "Consulter le verdict de conformité et ses justifications"],
  ["BF-05", "Juriste", "Consulter le catalogue de règles du système expert"],
  ["BF-06", "Juriste", "Consulter l'historique des évaluations de dossiers"],
  ["BF-07", "Juriste", "Proposer une évolution de règle avec justification documentaire"],
  ["BF-08", "Admin", "Consulter l'état de santé du système"],
];

const chapitre3 = [
  h1("Chapitre 3 — Analyse et conception (UML)"),

  h2("3.1 Acteurs et besoins fonctionnels/non fonctionnels"),
  p("Trois acteurs ont été définis pour la conception du système : l'Entrepreneur (porteur de projet, utilisateur principal des trois modules), le Juriste (consulte et fait évoluer le catalogue de règles, audite l'historique des évaluations) et l'Administrateur (supervise l'état technique du système). Ce découpage de rôles est une proposition de conception, non une exigence issue du corpus documentaire, validée explicitement par le porteur de projet avant son implémentation."),
  tableCaption("Tableau 3.1 — Extrait des besoins fonctionnels"),
  table(["ID", "Acteur", "Besoin"], besoinsFuncRows, [2, 3, 11]),
  p("Les besoins non fonctionnels retenus couvrent la traçabilité (toute réponse ou verdict doit référencer une règle et une source documentaire précise), la fermeture du corpus (aucune information juridique hors des documents fournis), la reproductibilité (exécution possible sans modification manuelle du code), la testabilité (couverture par des tests unitaires et d'intégration) et la maintenabilité (architecture en couches séparées)."),

  h2("3.2 Diagramme de cas d'utilisation"),
  p("Le diagramme de cas d'utilisation (figure 3.1) formalise les interactions entre les trois acteurs et le système. La relation d'inclusion entre la soumission d'un dossier et la consultation du verdict traduit le fait que toute évaluation produit systématiquement un résultat, sans exception silencieuse."),
  ...figure("fig_3_1_cas_utilisation.png", "Figure 3.1 — Diagramme de cas d'utilisation", 15),

  h2("3.3 Diagramme de classes"),
  p("Le diagramme de classes (figure 3.2) formalise les entités persistées par le système : utilisateurs, dossiers, identités des associés, pièces justificatives, règles, évaluations et anomalies pour le système expert ; questions, réponses et citations pour le chatbot ; documents et fragments (chunks) pour le corpus indexé. La structure de la classe Règle reprend exactement les champs imposés par le cahier des charges (identifiant, catégorie, description, condition, gravité, message utilisateur, justification, référence documentaire, niveau documentaire)."),
  ...figure("fig_3_2_classes.png", "Figure 3.2 — Diagramme de classes (simplifié)", 15.5),

  h2("3.4 Diagrammes de séquence"),
  p("Trois scénarios de séquence ont été modélisés lors de la phase de conception, correspondant chacun à l'un des trois modules du système : la soumission d'une question au chatbot juridique, l'extraction d'identité depuis une CIN, et la soumission d'un dossier au système expert. La figure 3.3 présente ce dernier scénario, illustrant le parcours complet depuis la saisie du formulaire jusqu'à l'affichage du verdict."),
  ...figure("fig_3_3_sequence_dossier.png", "Figure 3.3 — Diagramme de séquence : évaluation d'un dossier", 15),

  h2("3.5 Modèle de données"),
  p("Le modèle de données (figure 3.4) traduit le diagramme de classes en schéma relationnel, destiné à une implémentation PostgreSQL via SQLAlchemy. Douze tables ont été définies, couvrant l'authentification, le système expert, l'OCR et le module RAG."),
  ...figure("fig_3_4_erd.png", "Figure 3.4 — Modèle de données (ERD simplifié)", 15.5),
];

// ===========================================================================
// CHAPITRE 4 — ARCHITECTURE TECHNIQUE GLOBALE
// ===========================================================================
const stackRows = [
  ["Backend", "Python 3.11, FastAPI, SQLAlchemy 2.x, Alembic, Pydantic v2, Uvicorn"],
  ["Base de données", "PostgreSQL"],
  ["Frontend", "Streamlit"],
  ["RAG", "LangChain, ChromaDB, sentence-transformers (multilingual-e5-large), API Groq"],
  ["OCR", "EasyOCR, OpenCV, Pillow"],
  ["Authentification", "PyJWT, hachage PBKDF2-HMAC (bibliothèque standard)"],
  ["Tests", "pytest, pytest-cov"],
  ["Qualité", "black, isort, flake8, mypy"],
];

const chapitre4 = [
  h1("Chapitre 4 — Architecture technique globale"),

  h2("4.1 Stack technologique imposée et justifications"),
  p("La stack technologique du projet a été imposée dès le cadrage initial (chapitre 1). Le tableau 4.1 en présente la synthèse."),
  tableCaption("Tableau 4.1 — Stack technologique imposée"),
  table(["Composant", "Technologies"], stackRows, [4, 12]),
  p("Deux choix technologiques ont fait l'objet d'une justification approfondie dans ce rapport : EasyOCR plutôt que Tesseract pour le module OCR (chapitre 6), et l'implémentation d'un moteur de recherche lexicale BM25 en Python pur plutôt que l'ajout d'une dépendance supplémentaire, pour le module RAG (chapitre 7)."),

  h2("4.2 Architecture globale et arborescence du dépôt"),
  p("L'architecture globale (figure 4.1) assemble les trois modules fonctionnels derrière une couche d'authentification et de contrôle d'accès commune. Chaque module dispose de son propre espace de stockage (PostgreSQL pour les données relationnelles, fichiers texte et JSON pour le corpus documentaire, ChromaDB pour l'index vectoriel)."),
  ...figure("fig_4_1_architecture.png", "Figure 4.1 — Architecture globale du système", 15),
  p("L'arborescence du dépôt suit un découpage par responsabilité technique : backend/routers (contrats HTTP), backend/services (orchestration métier), backend/repositories (accès aux données), backend/models (entités ORM), backend/schemas (objets de transfert), backend/rules (règles du système expert), backend/ocr et backend/rag (pipelines spécialisés), frontend/pages (interface Streamlit), tests/unit, tests/integration et tests/e2e."),

  h2("4.3 Principes d'architecture"),
  p("L'architecture respecte les principes SOLID par une séparation stricte des responsabilités : les routeurs FastAPI ne contiennent aucune logique métier et se limitent à la validation d'entrée/sortie (schémas Pydantic) et à l'appel des services ; les services orchestrent la logique métier et dépendent des repositories et des règles, jamais l'inverse ; les repositories isolent l'accès aux données de la logique métier. Les dépendances externes coûteuses (modèles d'apprentissage automatique, bases vectorielles, clients d'API tierces) sont systématiquement encapsulées derrière des interfaces (protocoles Python), avec import différé à l'instanciation, permettant leur substitution par des adaptateurs factices en test — principe appliqué de façon cohérente aux modules OCR (EasyOCR), RAG (sentence-transformers, ChromaDB, Groq) et authentification."),

  h2("4.4 Reproductibilité et configuration"),
  p("Conformément à l'exigence de reproductibilité du cahier des charges, le projet peut être cloné et exécuté par `docker compose up` ou par installation des dépendances (`pip install -r requirements.txt`), sans modification manuelle du code. Aucun secret (clé API, mot de passe, clé de signature JWT) n'est codé en dur : toute la configuration transite par des variables d'environnement chargées depuis un fichier `.env` non versionné, dont un modèle (`.env.example`) est fourni dans le dépôt."),
];

// ===========================================================================
// CHAPITRE 5 — SYSTEME EXPERT ANTI-REJET
// ===========================================================================
const reglesRows = [
  ["ID-000", "identite", "bloquante", "0", "Forme juridique hors périmètre (SARL/SARL AU uniquement)"],
  ["ID-001", "identite", "bloquante", "1", "Nombre d'associés SARL hors de [1, 50]"],
  ["ID-002", "identite", "bloquante", "1", "SARL AU sans associé unique exact"],
  ["ID-003", "identite", "bloquante", "2", "Pièce d'identité manquante pour un associé"],
  ["DOC-001", "documents", "bloquante", "2", "Certificat négatif absent ou périmé"],
  ["DOC-002", "documents", "bloquante", "1", "Justificatif de siège social manquant"],
  ["DOC-003", "documents", "bloquante", "1", "Statuts non fournis"],
  ["CAP-001", "capital", "bloquante", "2", "Blocage bancaire manquant (> 100 000 DH)"],
  ["FISC-001", "fiscalite", "bloquante", "2", "Déclaration de taxe professionnelle manquante"],
  ["FISC-002", "fiscalite", "informative", "2", "Rappel : droit d'enregistrement (formules divergentes)"],
  ["CNSS-001", "cnss", "avertissement", "2", "Salariés employés sans affiliation CNSS"],
];

const chapitre5 = [
  h1("Chapitre 5 — Système expert anti-rejet"),

  h2("5.1 Principe et structure d'une règle"),
  p("Le système expert anti-rejet est entièrement fondé sur des règles explicites, sans recours à l'apprentissage automatique, conformément à l'exigence du cahier des charges. Chaque règle est décrite par neuf champs imposés : identifiant, catégorie, description, condition, gravité, message utilisateur, justification, référence documentaire et niveau documentaire. Cette structure garantit qu'aucune décision du système expert ne peut être produite sans une justification tracée à une source précise (règle de traçabilité, chapitre 3)."),
  p("Trois niveaux de gravité sont définis : bloquante (le dossier est jugé non conforme), avertissement (le dossier est conforme avec réserves) et informative (simple rappel documentaire, sans effet sur le statut global). Cette distinction a permis de traiter les points de divergence documentaire identifiés au chapitre 2 sans affirmer une valeur incertaine comme une cause de rejet : le seuil de capital minimum de la SARL, par exemple, n'a fait l'objet d'aucune règle bloquante compte tenu de la contradiction relevée entre les sources (tableau 2.4)."),

  h2("5.2 Catalogue synthétique des règles"),
  tableCaption("Tableau 5.1 — Catalogue synthétique des règles du système expert"),
  table(["ID", "Catégorie", "Gravité", "Niveau", "Description"], reglesRows, [2, 2.5, 2.5, 1.5, 9.5]),
  p("Le niveau documentaire « 0 » de la règle ID-000 est une convention locale au projet, réservée aux contraintes de périmètre fonctionnel qui ne sont pas issues du corpus légal (une forme juridique hors SARL/SARL AU n'est pas interdite par la loi, elle est simplement hors périmètre de ce système)."),

  h2("5.3 Moteur d'évaluation et statut global"),
  p("Le moteur d'évaluation (module `expert_service`) parcourt l'ensemble des règles applicables à un dossier soumis et agrège les anomalies détectées. Le statut global est déduit de la gravité maximale rencontrée : la présence d'au moins une anomalie bloquante entraîne un statut « non conforme » ; en son absence, un avertissement entraîne un statut « conforme avec réserves » ; les anomalies informatives ne dégradent jamais le statut, afin d'éviter qu'un rappel purement documentaire (tel que FISC-002) n'empêche un dossier par ailleurs complet d'être déclaré conforme."),

  h2("5.4 Dossiers synthétiques et résultats de tests"),
  p("Sept dossiers synthétiques ont été construits pour couvrir les cas exigés par le cahier des charges : dossier valide, dossier incomplet, dossier incohérent (nombre d'associés incompatible avec la forme juridique), certificat négatif absent, siège social manquant, mauvaise forme juridique, et capital social sans attestation de blocage. Chaque cas isole, autant que possible, une cause précise de non-conformité, afin de vérifier que le moteur d'évaluation déclenche exactement les règles attendues, ni plus ni moins. L'ensemble des tests associés (unitaires par catégorie de règle et d'intégration sur les sept dossiers synthétiques) est détaillé au chapitre 9."),
];

module.exports = { chapitre1, chapitre2, chapitre3, chapitre4, chapitre5 };
