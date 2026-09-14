# DECISIONS.md — Registre des décisions

> ⚠️ **Document historique (V1).** Registre des décisions prises pendant la première
> version du projet. **La référence actuelle du projet est `CONCEPTION_V2.md`** (§9/§10
> de ce document tiennent lieu de registre de décisions pour la V2), complétée par
> `PROJECT_STATE.md`. Conservé pour la traçabilité de l'évolution.

Format : `[DATE] Décision — Statut — Justification`

## Décisions validées (imposées par le cadrage initial)

- **[2026-07-20] Stack backend** : Python 3.11, FastAPI, SQLAlchemy 2.x, Alembic,
  Pydantic v2, Uvicorn — **Validée** — Imposée par le cahier des charges.
- **[2026-07-20] Base de données** : PostgreSQL — **Validée** — Imposée.
- **[2026-07-20] Frontend** : Streamlit — **Validée** — Imposée.
- **[2026-07-20] RAG** : LangChain + ChromaDB + sentence-transformers
  (multilingual-e5-large) + Groq API — **Validée** — Imposée.
- **[2026-07-20] OCR** : EasyOCR + OpenCV + Pillow — **Validée** — Imposée.
- **[2026-07-20] Système expert** : rule-based strict, sans ML — **Validée** — Imposée.
- **[2026-07-20] Corpus documentaire fermé** : aucune donnée juridique hors des documents
  fournis (S1 à S6) — **Validée** — Règle absolue n°1 et n°7.

## Décisions à trancher par le porteur de projet (bloquant pour Phase 1/2)

1. **Montant de référence du certificat négatif dans le système expert.**
   Le corpus contient deux valeurs : 170 DH (50+100+20, source OMPIC/[S4]/[S5], Niveau 2)
   et ~230 DH (source [S6], Niveau 3). *Statut : à valider — proposition par défaut :
   utiliser la valeur Niveau 2 (170 DH) comme référence, et mentionner la variante
   Niveau 3 comme information complémentaire dans les réponses du chatbot.*
2. **Authentification / gestion des utilisateurs.** Le corpus ne précise rien.
   *Statut : à valider — proposition par défaut : pas d'authentification en V1
   (usage mono-utilisateur local), à réévaluer si besoin multi-utilisateurs.*
3. **Hébergement cible / volumétrie attendue.** Non précisé dans le corpus.
   *Statut : à valider — proposition par défaut : exécution locale via `docker compose`,
   sans hypothèse de charge.*
4. **Formats de dossiers synthétiques pour les tests du système expert.**
   *Statut : à valider en Phase 2 — proposition : au moins 6 cas (valide, incomplet,
   incohérent, certificat négatif absent, siège social manquant, mauvaise forme
   juridique), conformément à la consigne du prompt.*
5. **Périmètre des formes juridiques couvertes par le système expert.**
   *Statut : à valider — proposition par défaut : SARL et SARL AU uniquement en V1
   (cf. `PROJECT.md`, section périmètre).*

## Décisions de Phase 1 (Conception UML)

- **[2026-07-20] Insertion d'une phase « Conception UML » entre le Cadrage et les
  Fondations techniques.** — **Validée** — Justification : demande explicite du porteur
  de projet (« Passe maintenant à la Phase 1 — Conception UML »). Conséquence :
  renumérotation du planning — l'ancienne « Phase 1 — Fondations » devient
  **Phase 2**, et toutes les phases suivantes sont décalées d'un rang (voir `TODO.md`
  mis à jour). Ceci ne modifie aucune décision de contenu déjà validée, seulement leur
  numérotation séquentielle — conforme à la Règle absolue n°2 (justification fournie).
- **[2026-07-20] Rôles applicatifs (entrepreneur / juriste / admin).** — **Validée
  définitivement par le porteur de projet.** Le corpus ne définit aucun rôle métier ;
  ce découpage reste une hypothèse de conception (non issue du corpus documentaire),
  mais elle est maintenant figée pour la suite du projet (modèles ORM, schémas, règles
  d'accès). Toute modification ultérieure devra être justifiée ici, conformément à la
  Règle absolue n°2.
- **[2026-07-20] Protection des données personnelles (CIN extraite par OCR).** — **À
  valider** — Le corpus ne contient aucune disposition sur la protection des données
  personnelles (aucune source de type loi 09-08 ou équivalent fournie). *Aucune règle
  juridique ne sera donc invoquée à ce sujet.* Recommandation technique par défaut
  (non juridique) : ne pas persister l'image brute de la CIN, ne conserver que les
  champs extraits normalisés, chiffrement applicatif à évaluer en Phase « Fondations ».
- **[2026-07-20] Multiplicité `Dossier` ↔ `IdentitePersonne`.** — **Validée** — Un
  dossier peut comporter un ou plusieurs associés (1 pour SARL AU, 1 à 50 pour SARL,
  cf. Loi 5-96 art. 44 et 47 [S1, Niveau 1]) → cardinalité modélisée `1..*` dans
  `docs/UML.md`.
- **[2026-07-20] Seuils de performance (temps de réponse chatbot, etc.).** — **À
  valider** — Non spécifiés dans le corpus. Valeur indicative proposée dans
  `docs/UML.md` (NFR-05) à titre de cible technique par défaut, explicitement non
  issue d'une source documentaire.

## Décisions de Phase 2 (Architecture technique / Fondations)

- **[2026-07-20] Ajout d'un dossier `alembic/` et de deux `Dockerfile` (backend,
  frontend) non listés dans l'arborescence minimale du prompt.** — **Validée** —
  Justification : Alembic (imposé par la stack) nécessite un dossier de migrations
  dédié pour fonctionner ; `docker compose up` (exigence de reproductibilité) nécessite
  des Dockerfile pour construire les images `backend` et `frontend`. Aucun fichier de
  l'arborescence minimale n'est supprimé ou déplacé — ajout strictement additif.
- **[2026-07-20] Portée des routers en Phase 2 : seul `/health` est implémenté.** —
  **Validée** — Justification : la Règle absolue n°4 interdit tout pseudo-code ou
  fonction incomplète. Les routers `chat`, `ocr` et `dossier` dépendent de services
  qui n'existent pas encore (RAG, OCR, système expert) ; ils seront créés **complets
  et fonctionnels** dans leurs phases respectives (5, 4, 3) plutôt que comme des
  fichiers vides ou des stubs `NotImplementedError`.
- **[2026-07-20] Pilote PostgreSQL : `psycopg` (v3) plutôt que `psycopg2`.** —
  **Validée** — Driver recommandé pour SQLAlchemy 2.x, actif et maintenu.
- **[2026-07-20] La table `regles` stocke uniquement les métadonnées déclaratives
  d'une règle (catégorie, gravité, justification, référence, niveau) ; la logique de
  condition exécutable reste en code Python dans `backend/rules/*.py`.** — **Validée**
  — Cohérent avec l'exigence « système expert rule-based, pas de ML » et avec la
  structure de règle imposée par le prompt.

## Décisions de Phase 3 (Système expert anti-rejet)

- **[2026-07-20] Trois contradictions du corpus ne sont PAS arbitrées par une règle
  automatique.** — **Validée** — Conformément à la Règle absolue n°8, le système
  n'invente ni ne choisit arbitrairement entre des sources contradictoires : (1) le
  capital minimum de la SARL (Loi 5-96 art. 46 = 100 000 DH vs OMPIC/Dar Al
  Moukawil/guide = aucun minimum depuis 2006) n'est codé comme aucune règle de rejet ;
  (2) la durée de validité du certificat négatif retient 3 mois avec réserve documentée
  (2 sources sur 3) plutôt que d'ignorer la 3e source (« un an ») ; (3) la formule du
  droit d'enregistrement est traitée comme un rappel informatif (gravité non bloquante)
  présentant les deux formulations. Détail complet dans `backend/RULES.md` §2.
- **[2026-07-20] Statut global calculé sur la gravité maximale, les anomalies
  "informative" ne dégradent jamais le statut.** — **Validée** — Sans cette règle,
  le rappel systématique FISC-002 aurait empêché tout dossier d'être déclaré
  "conforme", ce qui aurait été trompeur pour l'entrepreneur.
- **[2026-07-20] CNSS-001 est un avertissement, pas une règle bloquante.** — **Validée**
  — L'affiliation CNSS intervient après l'immatriculation dans le parcours documenté
  par l'OMPIC (étape 9, après l'étape 8) ; elle ne bloque donc pas l'immatriculation
  elle-même.

## Décisions de Phase 4 (Module OCR)

- **[2026-07-20] Confirmation du choix EasyOCR (imposé) plutôt que Tesseract, avec
  justification technique.** — **Validée** — EasyOCR est fondé sur des modèles de
  détection/reconnaissance par apprentissage profond (CRAFT + CRNN), plus robuste que
  Tesseract sur des photographies prises au smartphone (éclairage, angle, arrière-plan)
  que sur des scans plats propres. Surtout, EasyOCR est un package Python pur
  (installable uniquement via `pip install -r requirements.txt`), alors que Tesseract
  nécessite un binaire système (`tesseract-ocr`) et des paquets de langues installés au
  niveau de l'OS, ce qui casserait l'exigence de reproductibilité (clone + install sans
  étape manuelle). Le choix technologique lui-même reste celui imposé par le cahier des
  charges ; cette décision n'en est que la justification documentée.
- **[2026-07-20] Langue OCR limitée au français (écriture latine) en V1.** — **Validée**
  — Aucune certitude issue du corpus ou d'une documentation fiable sur la compatibilité
  exacte d'EasyOCR pour la combinaison français + arabe simultanée. Plutôt que de
  supposer un comportement, le système se limite au français ; l'extraction de
  l'écriture arabe est explicitement hors périmètre V1 (voir PROJECT.md §5.2).
- **[2026-07-20] Moteur OCR injectable via une dépendance FastAPI
  (`obtenir_moteur_ocr`), substituable en test.** — **Validée** — Permet de tester
  l'intégralité du pipeline (prétraitement, normalisation, validation, gestion
  d'erreurs, routage HTTP) sans charger les modèles EasyOCR réels (dépendance lourde).
  Le moteur réel est mis en cache (`lru_cache`) après son premier chargement.
- **[2026-07-20] Formats de reconnaissance (numéro CIN, date) non issus du corpus.** —
  **Validée à titre de convention technique**, à affiner avec des CIN réelles — le
  corpus ne fournit aucune image ni spécification de CIN (voir PROJECT.md §5.2).
- **[2026-07-20] Rattrapage : ajout du routeur `/dossier/evaluer` (engagement de Phase 2
  non honoré en Phase 3).** — **Validée** — Corrige un oubli : la décision de Phase 2
  prévoyait explicitement un routeur `dossier` complet dès la Phase 3. Il est livré ici,
  avant le routeur `/ocr/cin` propre à cette Phase 4, pour rétablir la cohérence entre
  code et documentation (Règle absolue n°6).

## Décisions de Phase 5 (Module RAG juridique)

- **[2026-07-20] Recherche lexicale : BM25 implémenté en pur Python, aucune dépendance
  ajoutée.** — **Validée** — La stack imposée (LangChain, ChromaDB, sentence-transformers,
  Groq) ne prévoit pas de bibliothèque de recherche lexicale dédiée. Plutôt que d'ajouter
  une dépendance non imposée (ex. `rank_bm25`), la formule BM25 (Robertson & Zaragoza) est
  implémentée directement dans `backend/rag/lexical_search.py`.
- **[2026-07-20] Fusion hybride par Reciprocal Rank Fusion (RRF).** — **Validée** — RRF
  combine deux classements (score cosinus vectoriel, score BM25) sans nécessiter de
  normaliser des échelles de score différentes, contrairement à une simple somme
  pondérée. Constante RRF = 60 (valeur usuelle de la littérature).
- **[2026-07-20] Reranking par niveau documentaire plutôt que cross-encoder neuronal.**
  — **Validée** — Aucun modèle de reranking multilingue français fiable n'a été identifié
  avec certitude dans la stack imposée ; en inventer un (nom de modèle non vérifié)
  aurait violé la Règle absolue n°1. Le reranking utilise à la place un signal
  documentaire explicite et déjà défini par le projet : à score de fusion comparable, un
  extrait de niveau 1 est priorisé sur un extrait de niveau 2, puis 3.
- **[2026-07-20] Chunking via `langchain_text_splitters.RecursiveCharacterTextSplitter`
  (taille 800 caractères, chevauchement 120).** — **Validée** — Utilisation réelle de
  LangChain (imposé), plutôt qu'un découpage fait main, pour un respect des frontières
  naturelles du texte (paragraphes, phrases) avant coupe forcée. Valeurs de taille/
  chevauchement empiriques, non issues du corpus — à ajuster si la qualité de recherche
  observée en production le justifie.
- **[2026-07-20] Le prompt système impose la citation et l'aveu d'absence de réponse,
  mais ceci reste une consigne au modèle, pas une garantie technique absolue.** — **Point
  ouvert, à surveiller** — Aucun mécanisme de vérification automatique ne confirme que le
  LLM a bien respecté cette consigne (pas de "citation checking" implémenté en V1). Risque
  résiduel d'hallucination non totalement éliminé ; à évaluer lors de tests utilisateurs
  réels avec une vraie clé API Groq.
- **[2026-07-20] Dépendances lourdes non exercées dans l'environnement de
  vérification : sentence-transformers, ChromaDB, Groq (+ modèles EasyOCR de la Phase
  4).** — **Validée, limitation documentée** — Ces bibliothèques nécessitent des
  téléchargements de modèles ou un accès réseau externe non disponibles dans ce sandbox
  (`api.groq.com` n'est pas dans la liste des domaines autorisés). Le contrat de chacune
  est testé via une interface (`Protocol`) et un adaptateur factice, selon le principe déjà
  appliqué à EasyOCR en Phase 4 (voir ARCHITECTURE.md §11 et §13). Ce choix est cohérent et
  documenté, mais l'exécution réelle du pipeline complet reste à valider dans
  l'environnement de déploiement cible.
- **[2026-07-20] Persistance de l'historique des questions/réponses différée.** —
  **Validée, hors périmètre V1** — Les modèles `Question`, `Reponse`, `CitationSource`
  existent depuis la Phase 1 (`docs/UML.md`) mais ne sont pas encore alimentés par
  `rag_service.py` (pas de couche `repositories/` implémentée à ce stade du projet). Le
  routeur `/chat` retourne la réponse sans la persister. À traiter en Phase 6
  (Intégration) si le porteur de projet le confirme nécessaire.

## Décisions de Phase 6 (Intégration API + UI complète)

- **[2026-07-20] Réintroduction de l'authentification, révisant la décision de Phase 2.**
  — **Validée** — Justification : demande explicite du porteur de projet en Phase 6
  (« assemblage des 3 modules... authentification et gestion des rôles »). La proposition
  par défaut de Phase 2 (« pas d'authentification en V1 ») est donc formellement révisée,
  conformément à la Règle absolue n°2 qui exige une justification pour toute modification
  d'une décision validée — justification fournie ici.
- **[2026-07-20] Authentification simplifiée : jeton JWT porteur, pas un flux OAuth2
  complet.** — **Validée** — `OAuth2PasswordBearer` n'est utilisé que pour le bouton
  « Authorize » de Swagger ; le routeur `/auth/connexion` accepte un corps JSON classique,
  pas un encodage de formulaire OAuth2. Suffisant pour les besoins du projet (Streamlit +
  API interne), pas conçu comme un fournisseur d'identité tiers.
- **[2026-07-20] Hachage de mot de passe par PBKDF2-HMAC-SHA256 (stdlib), pas
  bcrypt/argon2.** — **Validée** — Cohérent avec le principe « dépendances minimales »
  déjà observé (BM25 pur Python en Phase 5, etc.). `hashlib.pbkdf2_hmac` est disponible
  nativement en Python, sans dépendance C additionnelle à compiler dans les images
  Docker.
- **[2026-07-20] Répartition des accès par rôle : `/regles` réservé juriste/admin ;
  `/chat`, `/ocr/cin`, `/dossier/evaluer` ouverts à tout rôle authentifié.** — **Validée**
  — Reflète les cas d'usage définis en Phase 1 (docs/UML.md, BF-01 à BF-05) sans sur-
  restreindre des modules dont rien n'indique qu'ils doivent être réservés à
  l'entrepreneur exclusivement (un juriste ou un admin peut vouloir tester le chatbot).
- **[2026-07-20] Repository `UtilisateurRepository` testé contre une vraie base SQLite en
  mémoire (StaticPool), pas contre une session factice.** — **Validée** — Première
  couche de persistance réellement exercée en test dans ce projet (toutes les phases
  précédentes utilisaient des sessions factices ou évitaient la base). Nécessaire car la
  logique d'unicité de l'email et de récupération d'utilisateur dépend de vraies requêtes
  SQL, qu'un mock ne peut pas valider de façon significative.
- **[2026-07-20] Ajout d'un dossier `tests/e2e/` non prévu dans l'arborescence
  minimale.** — **Validée** — Additif, comme `alembic/` et les `Dockerfile` en Phase 2 :
  nécessaire pour distinguer les tests de parcours HTTP complets (inscription → connexion
  → usage d'un module) des tests d'intégration par routeur isolé.
- **[2026-07-20] Bug de fragilité des tests détecté et corrigé : les surcharges de
  dépendances FastAPI partagées entre fichiers de test (`get_db`,
  `obtenir_utilisateur_connecte`) ne doivent jamais être posées au niveau module puis
  retirées (`pop`) dans une fonction de test — un autre fichier peut voir sa propre
  surcharge effacée selon l'ordre d'exécution.** — **Corrigé** — Tous les tests
  concernés posent et retirent désormais leur surcharge à l'intérieur de chaque fonction
  de test. Vérifié stable sur plusieurs exécutions consécutives (voir ARCHITECTURE.md
  §14).
- **[2026-07-20] Interface Streamlit complète : connexion/inscription (page d'accueil),
  chatbot, extraction CIN, évaluation de dossier, catalogue de règles (5 pages).** —
  **Validée** — Le jeton JWT est stocké en `st.session_state` (mémoire de session
  Streamlit, jamais persisté sur disque) et transmis en en-tête `Authorization` à chaque
  appel API.

## Décisions de Phase 7 (Rédaction du rapport final)

- **[2026-07-20] La Phase 7 devient « Rédaction du rapport final » (au lieu de « Tests &
  qualité globale » prévue dans la renumérotation de Phase 1).** — **Validée** —
  Justification : demande explicite du porteur de projet. Les tests et la qualité de
  code ont en réalité déjà été maintenus en continu à chaque phase (5, 30, 50, 71 puis
  89 tests cumulés, couverture ≥ 94 % à chaque étape, black/isort/flake8/mypy propres à
  chaque livraison — voir TODO.md), ce qui rend une phase de consolidation dédiée
  redondante à ce stade. Une passe de consolidation finale reste possible plus tard si
  le porteur de projet le demande explicitement.
- **[2026-07-20] Nom de projet « Juris-IA » adopté pour la page de garde et le rapport.**
  — **Validée à titre de convention de présentation**, non une exigence du corpus — le
  porteur de projet a demandé un rapport « style Juris-IA » ; ce nom est utilisé comme
  titre du projet dans le document, sans incidence sur le code ou l'architecture.
- **[2026-07-20] Génération du rapport via docx-js (Node.js) plutôt que python-docx.** —
  **Validée** — Conforme au skill `docx` disponible dans l'environnement, qui prescrit
  cette approche pour la création de nouveaux documents Word.
- **[2026-07-20] Figures UML rendues en PNG statique (matplotlib) plutôt qu'en Mermaid.**
  — **Validée** — Aucun outil de rendu Mermaid-vers-image n'était disponible sans
  dépendance lourde (mermaid-cli nécessite Puppeteer/Chromium, non installable dans ce
  sandbox) ; les figures reprennent fidèlement le contenu déjà validé de `docs/UML.md`
  (Phase 1), simplement rendues autrement.
- **[2026-07-20] Table des matières statique (numéros de page calculés et vérifiés par
  script) plutôt que champ Word dynamique.** — **Corrigé** — Le champ `TableOfContents`
  de docx-js ne se calcule qu'à l'ouverture dans Microsoft Word (mise à jour manuelle du
  champ) ; LibreOffice ne le calcule pas automatiquement lors d'une conversion PDF
  headless, ce qui aurait produit une table des matières vide pour tout lecteur n'ouvrant
  pas le fichier dans Word. Une table des matières statique, avec numéros de page extraits
  et vérifiés automatiquement depuis le PDF réellement généré, a été substituée pour
  garantir un rendu correct dans tous les lecteurs (Word, LibreOffice, visionneuses PDF).
- **[2026-07-20] Rapport de 28 pages (sur un maximum de 40 imposé par le cahier des
  charges).** — **Validée** — Le contenu vise l'exhaustivité sur les points exigés
  (page de garde, remerciements, résumé bilingue, abréviations, table des matières,
  10 chapitres numérotés, 6 figures, 8 tableaux, bibliographie à 17 entrées, conclusion
  avec limites et perspectives) sans remplissage artificiel.
- **[2026-07-20] Bibliographie limitée aux sources réellement vérifiables.** — **Validée**
  — Les 6 sources du corpus fermé (entrées [1] à [6]) et les documentations officielles
  des technologies employées (entrées [9] à [17]) sont citées sans détail inventé
  (dates de version, auteurs précis non vérifiés) ; les deux références académiques sur
  BM25 et RRF (entrées [7], [8], déjà utilisées comme justification dans le code de la
  Phase 5) sont citées avec les éléments dont l'exactitude est raisonnablement établie
  (auteurs, titre, année), sans invention de détails bibliographiques supplémentaires.

## Décisions en attente de code (à formaliser si le projet se poursuit)

- Stratégie de migration Alembic (une migration initiale vs. migrations incrémentales
  par module).
- Politique de gestion des secrets (`.env` + `pydantic-settings`, non versionné).
- Stratégie de logging (format, niveau, sortie).

> Rappel Règle absolue n°2 : toute décision marquée **Validée** ne sera modifiée qu'avec
> justification explicite consignée ici.
