const H = require("./rapport_helpers.js");
const { p, h1, h2, h3, bulletItem, figure, table, tableCaption } = H;

// ===========================================================================
// CHAPITRE 6 — MODULE OCR
// ===========================================================================
const ocrCompareRows = [
  ["Approche", "Détection + reconnaissance par apprentissage profond (CRAFT + CRNN)", "Moteur historique (LSTM depuis v4), plus sensible aux conditions de capture"],
  ["Robustesse (photo smartphone)", "Meilleure, conçu pour des scènes naturelles", "Optimisé pour des scans plats et propres"],
  ["Installation", "Package Python pur (pip install)", "Binaire système (tesseract-ocr) + paquets de langues, hors pip"],
  ["Impact reproductibilité", "Compatible avec « clone + install sans étape manuelle »", "Nécessiterait une installation système supplémentaire"],
  ["Support multilingue", "Natif (Reader multilingue)", "Paquets de langues séparés (fra, ara)"],
];

const chapitre6 = [
  h1("Chapitre 6 — Module OCR d'extraction de CIN"),

  h2("6.1 Choix d'EasyOCR : justification"),
  p("EasyOCR figurait déjà parmi les technologies imposées par le cahier des charges pour le module OCR. Ce choix a été confirmé et documenté sur des critères techniques objectifs, résumés dans le tableau 6.1 : robustesse face aux photographies prises au smartphone (éclairage, angle, arrière-plan), par opposition à un moteur plus adapté aux scans plats ; et surtout, compatibilité avec l'exigence de reproductibilité du projet, puisqu'EasyOCR est un package Python pur installable uniquement par `pip`, alors que Tesseract nécessite l'installation d'un binaire système et de paquets de langues distincts, ce qui aurait complexifié la construction de l'image Docker."),
  tableCaption("Tableau 6.1 — Comparatif EasyOCR / Tesseract"),
  table(["Critère", "EasyOCR", "Tesseract"], ocrCompareRows, [4, 6, 6]),
  p("Par prudence méthodologique, la reconnaissance a été limitée à l'écriture latine (langue française) en version actuelle du système, faute de certitude sur la compatibilité exacte du modèle EasyOCR pour la combinaison simultanée du français et de l'arabe. Ce choix, documenté dans le journal de décisions du projet, est une limitation de portée assumée plutôt qu'une contrainte issue du corpus."),

  h2("6.2 Pipeline d'extraction"),
  p("Le pipeline OCR se décompose en quatre étapes successives. Le prétraitement (module `preprocessing`, OpenCV) convertit l'image en niveaux de gris, réduit le bruit et égalise l'histogramme, afin d'améliorer la lisibilité du texte avant transmission au moteur de reconnaissance. L'extraction (module `extraction`) délègue la détection et la reconnaissance de texte à EasyOCR, encapsulé derrière une interface permettant sa substitution en test. La normalisation (module `normalization`) applique des expressions régulières pour reconnaître, parmi les lignes de texte détectées, le numéro de CIN (motif : une à deux lettres majuscules suivies de cinq à six chiffres), la date de naissance (formats JJ/MM/AAAA, JJ.MM.AAAA ou JJ-MM-AAAA) et les lignes correspondant au nom et au prénom. La validation (module `validation`) vérifie enfin que les quatre champs attendus ont été effectivement reconnus."),

  h2("6.3 Gestion des erreurs et intégration au dossier"),
  p("Deux cas d'erreur explicites sont gérés par le service d'orchestration (`ocr_service`) : l'absence totale de texte détecté sur l'image (exception `ImageIllisibleError`, traduite en réponse HTTP 422 par le routeur) et l'incomplétude d'un ou plusieurs champs après normalisation (exception `ChampsIdentiteIncompletsError`, accompagnée de la liste précise des champs manquants). Le routeur `/ocr/cin` rejette également, avant tout appel au moteur OCR, tout fichier qui ne peut être décodé comme une image valide. Une fonction de conversion (`vers_identite_personne`) permet d'intégrer directement le résultat d'une extraction réussie au schéma d'entrée du dossier de création, en marquant explicitement l'origine de l'identité (« OCR ») pour préserver la traçabilité prévue dès la conception (chapitre 3)."),

  h2("6.4 Tests et limites"),
  p("Le contrat de chaque composant du pipeline (prétraitement, extraction, normalisation, validation, orchestration, routage HTTP) a été testé unitairement et en intégration. Le moteur EasyOCR réel n'a en revanche pas été exercé de bout en bout dans l'environnement de vérification utilisé pour ce projet, les modèles de détection et de reconnaissance nécessitant un téléchargement et une inférence par apprentissage profond incompatibles avec les contraintes de temps et de réseau du sandbox de développement. Cette limitation, documentée au chapitre 9, n'affecte pas la validité des tests portant sur la logique environnante (prétraitement d'image réel via OpenCV, expressions régulières de normalisation, gestion d'erreurs), mais implique qu'une validation complémentaire avec des CIN réelles reste nécessaire avant mise en production."),
];

// ===========================================================================
// CHAPITRE 7 — MODULE RAG JURIDIQUE
// ===========================================================================
const chapitre7 = [
  h1("Chapitre 7 — Module RAG juridique"),

  h2("7.1 Corpus documentaire fermé et pipeline d'indexation"),
  p("Le chatbot juridique s'appuie exclusivement sur le corpus fermé décrit au chapitre 2 (six documents, niveaux 1 à 3). Le pipeline d'indexation (figure 7.1, partie supérieure), exécuté hors ligne par le script `indexer_corpus.py`, enchaîne l'extraction du texte brut depuis les fichiers sources, un nettoyage textuel (uniformisation des espaces et des sauts de ligne), un découpage en fragments indexables (module `chunking`, utilisant `RecursiveCharacterTextSplitter` de LangChain avec une taille de 800 caractères et un chevauchement de 120 caractères), le calcul des vecteurs d'embedding (sentence-transformers, modèle multilingue) et l'indexation dans ChromaDB. Les fragments sont également sérialisés en JSON pour permettre la reconstruction de l'index lexical décrit au paragraphe suivant."),
  ...figure("fig_7_1_pipeline_rag.png", "Figure 7.1 — Pipeline RAG complet (indexation et requête)", 15.5),

  h2("7.2 Recherche hybride : fusion sémantique et lexicale"),
  p("Au moment de la requête (figure 7.1, partie inférieure), la question de l'utilisateur est transformée en vecteur d'embedding, puis soumise à deux recherches en parallèle : une recherche sémantique (similarité vectorielle dans ChromaDB) et une recherche lexicale, fondée sur l'algorithme BM25 [7]. Ce dernier a été implémenté directement en Python, sans dépendance supplémentaire, la stack imposée ne prévoyant pas de bibliothèque de recherche lexicale dédiée. Les deux classements sont combinés par Reciprocal Rank Fusion (RRF) [8], une méthode qui attribue à chaque résultat un score égal à la somme de l'inverse de son rang dans chaque classement où il apparaît, évitant ainsi d'avoir à normaliser des échelles de score hétérogènes (similarité cosinus contre score BM25)."),

  h2("7.3 Reranking par niveau documentaire"),
  p("Plutôt qu'un reranking neuronal par modèle cross-encoder — pour lequel aucun modèle multilingue français fiable n'a pu être identifié avec certitude dans la stack imposée, et qu'il aurait été risqué de citer sans vérification —, le système applique un signal de reranking documentaire explicite et vérifiable : à score de fusion comparable, un extrait provenant d'une source de niveau 1 (texte de loi) est priorisé sur un extrait de niveau 2, lui-même priorisé sur un extrait de niveau 3, conformément à la hiérarchie des sources définie au chapitre 2. Ce choix de conception a permis de détecter, lors des tests, une erreur de logique dans l'implémentation initiale du tri (les résultats les moins pertinents étaient par erreur priorisés) — bug corrigé et revérifié (chapitre 9)."),

  h2("7.4 Génération de la réponse et garde-fous anti-hallucination"),
  p("La génération de la réponse finale est déléguée à un modèle de langage accessible via l'API Groq. Le prompt système impose explicitement au modèle de répondre uniquement à partir des extraits fournis en contexte, de citer chaque affirmation selon le format [Titre du document, Niveau N], et de signaler explicitement l'absence de réponse dans le corpus plutôt que d'inventer une information. Les citations retournées par l'API ne sont cependant pas extraites du texte généré par expression régulière — jugé trop fragile — mais correspondent exactement à l'ensemble des extraits transmis en contexte au modèle, garantissant une traçabilité par construction plutôt que par vérification a posteriori."),
  p("Il est important de souligner qu'il s'agit là d'une consigne donnée au modèle, non d'une garantie technique absolue : aucun mécanisme de vérification automatique ne contrôle, dans la version actuelle du système, que le modèle a effectivement respecté cette consigne lors de la génération. Ce point est identifié comme un risque résiduel à surveiller (chapitre 9 et chapitre 10)."),

  h2("7.5 Tests et limites"),
  p("Chaque étape du pipeline a été testée unitairement (extraction, nettoyage, découpage, sérialisation des fragments, recherche BM25, fusion RRF, reranking, construction du prompt) ainsi qu'en intégration (pipeline de requête complet, routeur HTTP `/chat`). Comme pour le module OCR, les dépendances les plus lourdes (sentence-transformers, ChromaDB, API Groq) n'ont pas été exercées de bout en bout dans l'environnement de vérification : leur contrat est testé via des adaptateurs factices respectant les mêmes interfaces que les implémentations réelles. L'appel réel à l'API Groq n'a par ailleurs pas pu être testé, le domaine correspondant n'étant pas accessible depuis l'environnement réseau utilisé pour ce projet."),
];

// ===========================================================================
// CHAPITRE 8 — INTEGRATION, AUTHENTIFICATION ET UI
// ===========================================================================
const chapitre8 = [
  h1("Chapitre 8 — Intégration, authentification et interface utilisateur"),

  h2("8.1 Assemblage des trois modules"),
  p("Les trois modules développés indépendamment (système expert, OCR, RAG) sont assemblés derrière une couche d'authentification et de contrôle d'accès commune. Les points d'entrée `/dossier/evaluer`, `/ocr/cin` et `/chat` exigent tous une authentification valide (tout rôle applicatif), tandis que le point d'entrée `/regles`, qui expose le catalogue de règles du système expert, est réservé aux rôles juriste et administrateur, conformément au besoin fonctionnel BF-05 défini en phase de conception (chapitre 3)."),

  h2("8.2 Authentification JWT et contrôle d'accès par rôle"),
  p("L'authentification n'était pas prévue dans le périmètre initial du projet ; elle a été réintroduite sur demande explicite en cours de développement, décision documentée et justifiée dans le journal de décisions du projet. Le mécanisme retenu repose sur des jetons JWT porteurs, avec un hachage de mot de passe par PBKDF2-HMAC-SHA256 (bibliothèque standard Python), plutôt que bcrypt ou argon2, afin de limiter les dépendances externes du projet. L'implémentation reste volontairement simplifiée : l'interface `OAuth2PasswordBearer` de FastAPI n'est utilisée que pour bénéficier du bouton d'autorisation de la documentation Swagger générée automatiquement ; le point d'entrée de connexion accepte un corps de requête JSON classique, non un encodage de formulaire OAuth2 complet."),
  p("Le contrôle d'accès par rôle est implémenté par une fabrique de dépendances FastAPI (`exiger_role`), qui vérifie que le rôle porté par le jeton décodé figure parmi les rôles autorisés pour le point d'entrée concerné, renvoyant une erreur HTTP 403 dans le cas contraire."),

  h2("8.3 Interface utilisateur Streamlit"),
  p("L'interface utilisateur se compose de cinq pages. La page d'accueil regroupe l'état de santé du backend et un formulaire de connexion/inscription ; le jeton d'accès obtenu est conservé en mémoire de session (jamais persisté sur disque) et transmis en en-tête d'autorisation à chaque appel de l'API. Les quatre pages suivantes correspondent chacune à un module fonctionnel : chatbot juridique (historique de conversation, citations affichées sous chaque réponse), extraction de CIN (dépôt de fichier image, affichage des champs extraits), évaluation de dossier (formulaire structuré reprenant les champs du système expert, affichage du verdict et de chaque anomalie avec sa justification) et catalogue de règles (visible uniquement si le rôle courant est juriste ou administrateur, illustrant concrètement le contrôle d'accès côté interface, en complément du contrôle côté serveur)."),

  h2("8.4 Tests end-to-end"),
  p("Des tests de bout en bout ont été ajoutés pour ce chapitre, distincts des tests d'intégration par routeur isolé utilisés dans les phases précédentes : ils enchaînent plusieurs appels HTTP représentant un parcours utilisateur réel (inscription, connexion, puis utilisation d'un module), contre une base de données SQLite en mémoire réellement interrogée (et non simulée), première étape du projet à exercer une véritable couche de persistance en test. Ces tests couvrent notamment le parcours complet d'un entrepreneur soumettant un dossier valide, le rejet d'une requête sans jeton d'authentification, et le contraste entre l'accès autorisé d'un juriste et l'accès refusé d'un entrepreneur au catalogue de règles."),
];

// ===========================================================================
// CHAPITRE 9 — RESULTATS, QUALITE ET DISCUSSION
// ===========================================================================
const testsParPhaseRows = [
  ["Phase 2 — Fondations techniques", "5", "96 %"],
  ["Phase 3 — Système expert anti-rejet", "30 (cumulé)", "97 %"],
  ["Phase 4 — Module OCR", "50 (cumulé)", "98 %"],
  ["Phase 5 — Module RAG juridique", "71 (cumulé)", "94 %"],
  ["Phase 6 — Intégration, auth, UI", "89 (cumulé)", "95 %"],
];

const chapitre9 = [
  h1("Chapitre 9 — Résultats, qualité et discussion"),

  h2("9.1 Synthèse des résultats de tests par phase"),
  p("Le tableau 9.1 synthétise l'évolution du nombre de tests automatisés et de la couverture de code au fil des phases de développement. Chaque phase a fait l'objet d'une vérification complète (compilation, exécution des tests, contrôle de format et de typage statique) avant d'être considérée comme terminée."),
  tableCaption("Tableau 9.1 — Synthèse des résultats de tests par phase"),
  table(["Phase", "Tests (cumulés)", "Couverture"], testsParPhaseRows, [8, 4, 4]),

  h2("9.2 Qualité du code"),
  p("L'ensemble du code source a été systématiquement vérifié à l'aide de quatre outils : `black` et `isort` pour le formatage, `flake8` pour l'analyse statique de style, et `mypy` pour la vérification de typage statique, configuré avec `ignore_missing_imports = true` afin de tolérer l'absence des bibliothèques les plus lourdes dans l'environnement de vérification (voir §9.3) sans renoncer à la vérification de typage du reste du code. Ces quatre outils ne relèvent aucune erreur sur l'état final du dépôt."),

  h2("9.3 Limitations de l'environnement de vérification"),
  p("Plusieurs dépendances lourdes n'ont pas pu être exercées de bout en bout dans l'environnement utilisé pour développer et vérifier ce projet : les modèles de détection et de reconnaissance d'EasyOCR, le modèle d'embeddings sentence-transformers (multilingual-e5-large), la base vectorielle ChromaDB, et l'API Groq (dont le domaine réseau n'était pas accessible). Pour chacune de ces dépendances, le code de production reste complet et fonctionnel — aucune fonction incomplète ni pseudo-code n'a été produite —, mais leur contrat a été testé via des interfaces (protocoles Python) et des adaptateurs factices, plutôt que par exécution réelle. Cette approche, appliquée de façon cohérente à partir de la phase OCR et généralisée aux phases suivantes, permet de vérifier la logique métier environnante (prétraitement, normalisation, fusion, reranking, gestion d'erreurs, contrats HTTP) sans dépendre de ressources indisponibles dans le sandbox de développement, mais implique qu'une campagne de validation complémentaire, dans l'environnement de déploiement cible et avec de vraies données (CIN réelles, clé API Groq active), reste nécessaire avant une mise en production."),
  p("Un bug réel a par ailleurs été détecté et corrigé grâce à la suite de tests, concernant la fragilité de certaines substitutions de dépendances FastAPI partagées entre fichiers de test : plusieurs fichiers substituaient la même dépendance sans coordination, ce qui provoquait des échecs intermittents selon l'ordre d'exécution des tests. La correction (confinement de chaque substitution à l'intérieur de sa propre fonction de test) illustre l'utilité de la vérification continue mise en place à chaque phase."),

  h2("9.4 Discussion critique"),
  p("Le principal risque identifié concerne la fiabilité juridique des réponses générées par le chatbot : bien que le prompt système impose explicitement la citation des sources et l'aveu d'absence de réponse, ceci reste une consigne donnée au modèle de langage, non une garantie technique vérifiée automatiquement. Un mécanisme de vérification des citations produites (par exemple, un contrôle de cohérence entre le texte généré et les extraits fournis) constituerait une amélioration prioritaire avant toute utilisation en conditions réelles impliquant des décisions à valeur juridique. De façon plus générale, les contradictions identifiées dans le corpus documentaire (chapitre 2) rappellent que ce système constitue une aide à la décision et non une source d'autorité juridique substituable à un professionnel du droit ou aux administrations compétentes."),
];

// ===========================================================================
// CHAPITRE 10 — CONCLUSION
// ===========================================================================
const chapitre10 = [
  h1("Chapitre 10 — Conclusion générale, limites et perspectives"),

  h2("10.1 Bilan du projet"),
  p("Ce projet a permis de concevoir et développer Juris-IA, un système logiciel assemblant trois modules complémentaires — chatbot juridique fondé sur une architecture RAG, extraction OCR d'identité, et système expert anti-rejet — au service de l'accompagnement à la création de SARL et SARL AU au Maroc. Le développement, conduit par phases successives depuis le cadrage initial jusqu'à l'intégration complète avec authentification et interface utilisateur, a fait l'objet d'une vérification systématique à chaque étape, aboutissant à une suite de 89 tests automatisés passant avec une couverture de code de 95 %. Une attention particulière a été portée à la traçabilité de chaque affirmation juridique à sa source documentaire, ainsi qu'au signalement explicite des informations manquantes ou contradictoires plutôt qu'à leur résolution arbitraire."),

  h2("10.2 Limites"),
  bulletItem("Le corpus documentaire fermé, bien qu'il garantisse la traçabilité, ne couvre qu'un sous-ensemble des questions qu'un porteur de projet réel pourrait poser, et contient lui-même des contradictions non résolues (chapitre 2) ;"),
  bulletItem("Les dépendances les plus lourdes du système (OCR, embeddings, base vectorielle, API de génération) n'ont pas été exercées de bout en bout dans l'environnement de développement, ce qui implique une campagne de validation complémentaire avant mise en production ;"),
  bulletItem("Aucun mécanisme automatique ne vérifie que le modèle de langage respecte effectivement sa consigne de citation et de non-invention lors de la génération des réponses du chatbot ;"),
  bulletItem("La persistance de l'historique des questions et réponses, bien que modélisée dès la conception, n'a pas été implémentée dans le périmètre couvert par ce rapport ;"),
  bulletItem("Le système ne couvre que la SARL et la SARL AU ; les autres formes juridiques mentionnées dans le corpus ne sont traitées qu'à titre informationnel."),

  h2("10.3 Perspectives d'évolution"),
  bulletItem("Mettre en œuvre un mécanisme de vérification des citations produites par le chatbot, par exemple par comparaison automatique entre le texte généré et les extraits fournis en contexte ;"),
  bulletItem("Élargir le corpus documentaire à d'autres formes juridiques et le maintenir à jour au fil des évolutions réglementaires, en particulier sur les points de contradiction identifiés (réforme du capital minimum de la SARL, durée de validité du certificat négatif) ;"),
  bulletItem("Valider le pipeline complet (OCR, RAG) avec des données réelles (CIN authentiques, clé API Groq active) dans l'environnement de déploiement cible ;"),
  bulletItem("Implémenter la couche de persistance de l'historique des questions, réponses et évaluations, déjà modélisée, afin de permettre l'audit prévu pour le rôle juriste (BF-06) ;"),
  bulletItem("Étudier l'introduction d'un reranking neuronal multilingue, sous réserve de l'identification d'un modèle fiable et documenté pour le français juridique."),
];

// ===========================================================================
// BIBLIOGRAPHIE
// ===========================================================================
const biblioRows = [
  ["[1]", "Royaume du Maroc, Loi n°5-96 sur la société en nom collectif, la société en commandite simple, la société en commandite par actions, la société à responsabilité limitée et la société en participation, promulguée par le Dahir n°1-97-49 du 13 février 1997, Bulletin Officiel n°4478 du 1er mai 1997."],
  ["[2]", "Direction Générale des Impôts (Royaume du Maroc), Note de synthèse — Impôt sur les Sociétés, portail officiel de la DGI."],
  ["[3]", "Direction Générale des Impôts (Royaume du Maroc), Note de synthèse — Taxe sur la Valeur Ajoutée, portail officiel de la DGI."],
  ["[4]", "Office Marocain de la Propriété Industrielle et Commerciale (OMPIC), « Création et vie de l'entreprise », Registre Central du Commerce, www.ompic.ma."],
  ["[5]", "Dar Al Moukawil (service Attijariwafa bank), Guide n°1 — Démarches administratives de création d'entreprise, contenu certifié par Mazars."],
  ["[6]", "Documentation pratique de vulgarisation juridique — Création de SARL / SARL AU au Maroc (guide pratique secondaire, niveau 3)."],
  ["[7]", "S. Robertson, H. Zaragoza, The Probabilistic Relevance Framework: BM25 and Beyond, Foundations and Trends in Information Retrieval, 2009."],
  ["[8]", "G. V. Cormack, C. L. A. Clarke, S. Büttcher, Reciprocal Rank Fusion outperforms Condorcet and Individual Rank Learning Methods, Proceedings of SIGIR, 2009."],
  ["[9]", "Documentation officielle FastAPI, https://fastapi.tiangolo.com/."],
  ["[10]", "Documentation officielle SQLAlchemy 2.x, https://www.sqlalchemy.org/."],
  ["[11]", "Documentation officielle LangChain, https://python.langchain.com/."],
  ["[12]", "Documentation officielle ChromaDB, https://docs.trychroma.com/."],
  ["[13]", "Documentation officielle sentence-transformers, https://www.sbert.net/."],
  ["[14]", "Documentation officielle EasyOCR (JaidedAI), https://github.com/JaidedAI/EasyOCR."],
  ["[15]", "Documentation officielle Streamlit, https://docs.streamlit.io/."],
  ["[16]", "Documentation officielle Groq API, https://console.groq.com/docs."],
  ["[17]", "Documentation officielle PyJWT, https://pyjwt.readthedocs.io/."],
];

const bibliographie = [
  h1("Bibliographie"),
  ...biblioRows.map(([num, texte]) =>
    new (require("docx").Paragraph)({
      spacing: { after: 160 },
      alignment: require("docx").AlignmentType.JUSTIFIED,
      children: [
        new (require("docx").TextRun)({ text: `${num} `, bold: true }),
        new (require("docx").TextRun)({ text: texte }),
      ],
    })
  ),
];

module.exports = { chapitre6, chapitre7, chapitre8, chapitre9, chapitre10, bibliographie };
