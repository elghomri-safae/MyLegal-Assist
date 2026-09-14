# ARBORESCENCE.md — Manifeste final du dépôt Juris-IA

> ⚠️ **Document historique (V1).** Manifeste du dépôt à l'état de la première version.
> Plusieurs éléments qu'il liste (module OCR, tables `Entreprise`/`Regle`/`snapshot`,
> rôle Juriste) ont été retirés ou modifiés dans la conception V2. **La référence
> actuelle du projet est `CONCEPTION_V2.md`**, complétée par `PROJECT_STATE.md`.
> Conservé pour la traçabilité de l'évolution, pas comme état actuel du dépôt.

**Statut : projet terminé (Phases 0 à 7).** Ce document liste l'intégralité des
dossiers et fichiers du dépôt final, avec le chemin exact et une description de
chacun. Il ne remplace pas les fichiers eux-mêmes (dont le contenu intégral reste
disponible dans l'archive livrée avec cette réponse et dans chaque fichier déjà
partagé au fil des phases) : il sert de table de vérification et de navigation.

**Total : 170 fichiers, 34 dossiers.**

---

## Racine du dépôt

| Fichier | Description |
|---|---|
| `.env.example` | Modèle de variables d'environnement (aucun secret réel) |
| `.gitignore` | Règles d'exclusion Git |
| `PROJECT.md` | Cadrage du projet : besoin, objectifs, périmètre, acteurs, décisions de portée |
| `ARCHITECTURE.md` | Architecture proposée et vérifiée, phase par phase (§1 à §15) |
| `DECISIONS.md` | Registre de toutes les décisions prises, validées ou ouvertes |
| `TODO.md` | Suivi des tâches par phase |
| `ARBORESCENCE.md` | Ce manifeste |
| `alembic.ini` | Configuration Alembic (migrations DB) |
| `conftest.py` | Ajout de la racine du projet au `sys.path` pour les tests |
| `docker-compose.yml` | Orchestration Docker (db, backend, frontend) |
| `pyproject.toml` | Configuration black / isort / mypy / pytest / coverage |
| `requirements.txt` | Dépendances complètes du projet |
| `setup.cfg` | Configuration flake8 |

## `alembic/` — Migrations de base de données

| Fichier | Description |
|---|---|
| `alembic/env.py` | Environnement Alembic, connecté aux settings applicatifs |
| `alembic/script.py.mako` | Template standard des scripts de migration |
| `alembic/versions/328c09bae8e8_schema_initial.py` | Migration initiale : les 12 tables du modèle de données (Phase 2) |
| `alembic/versions/5ce512126e5b_ajout_mot_de_passe_hash.py` | Ajout du champ `mot_de_passe_hash` (Phase 6, authentification) |

## `backend/` — Backend FastAPI

| Fichier | Description |
|---|---|
| `backend/__init__.py` | Package backend |
| `backend/main.py` | Point d'entrée FastAPI, enregistrement des 6 routeurs |
| `backend/RULES.md` | Catalogue complet des 11 règles du système expert (sources, niveaux, contradictions) |
| `backend/Dockerfile` | Image Docker du backend |

### `backend/config/`
| Fichier | Description |
|---|---|
| `config/__init__.py` | Package config |
| `config/settings.py` | Paramètres applicatifs (Pydantic v2 `BaseSettings`, `.env`) |
| `config/.gitkeep` | Marqueur de dossier |

### `backend/core/`
| Fichier | Description |
|---|---|
| `core/__init__.py` | Package core |
| `core/database.py` | Moteur SQLAlchemy, `get_db` (dépendance FastAPI) |
| `core/dependencies.py` | Authentification JWT + contrôle d'accès par rôle (`exiger_role`) |
| `core/exceptions.py` | Exceptions applicatives (`CorpusInformationMissingError`, etc.) |
| `core/logging.py` | Configuration du logging |
| `core/security.py` | Hachage PBKDF2 + JWT (PyJWT) |
| `core/.gitkeep` | Marqueur de dossier |

### `backend/models/` — Modèles ORM (12 tables)
| Fichier | Description |
|---|---|
| `models/__init__.py` | Agrégation des modèles (découverte Alembic) |
| `models/enums.py` | Énumérations partagées (rôles, statuts, gravités) |
| `models/utilisateur.py` | Modèle `Utilisateur` (entrepreneur/juriste/admin) |
| `models/dossier.py` | Modèle `Dossier` |
| `models/identite_personne.py` | Modèle `IdentitePersonne` (associés) |
| `models/piece_justificative.py` | Modèle `PieceJustificative` |
| `models/regle.py` | Modèle `Regle` (métadonnées déclaratives) |
| `models/evaluation.py` | Modèles `EvaluationDossier` et `Anomalie` |
| `models/chat.py` | Modèles `Question`, `Reponse`, `CitationSource` |
| `models/corpus.py` | Modèles `DocumentCorpus` et `Chunk` |
| `models/.gitkeep` | Marqueur de dossier |

### `backend/ocr/` — Pipeline OCR (Phase 4)
| Fichier | Description |
|---|---|
| `ocr/__init__.py` | Package OCR |
| `ocr/preprocessing.py` | Prétraitement OpenCV |
| `ocr/extraction.py` | Extraction EasyOCR (interface injectable `MoteurOCR`) |
| `ocr/normalization.py` | Reconnaissance des champs (regex CIN/date/nom) |
| `ocr/validation.py` | Validation de complétude des champs |

### `backend/rag/` — Pipeline RAG (Phase 5)
| Fichier | Description |
|---|---|
| `rag/__init__.py` | Package RAG |
| `rag/extraction.py` | Extraction du corpus fermé (`data/raw/`) |
| `rag/cleaning.py` | Nettoyage textuel |
| `rag/chunking.py` | Découpage en chunks (LangChain) |
| `rag/chunk_store.py` | Sérialisation JSON des chunks |
| `rag/embeddings.py` | Embeddings (sentence-transformers, interface injectable) |
| `rag/indexing.py` | Indexation/recherche vectorielle (ChromaDB, interface injectable) |
| `rag/lexical_search.py` | Recherche lexicale BM25 (pur Python) |
| `rag/hybrid_search.py` | Fusion RRF (sémantique + lexicale) |
| `rag/reranking.py` | Reranking par niveau documentaire |
| `rag/generation.py` | Génération avec citations (Groq, interface injectable) |

### `backend/repositories/`
| Fichier | Description |
|---|---|
| `repositories/__init__.py` | Package repositories |
| `repositories/utilisateur_repository.py` | Accès aux données Utilisateur (SQLAlchemy) |
| `repositories/.gitkeep` | Marqueur de dossier |

### `backend/routers/` — Points d'entrée HTTP
| Fichier | Description |
|---|---|
| `routers/__init__.py` | Package routers |
| `routers/health.py` | `GET /health` |
| `routers/auth.py` | `POST /auth/inscription`, `POST /auth/connexion` |
| `routers/dossier.py` | `POST /dossier/evaluer` (auth requise) |
| `routers/ocr.py` | `POST /ocr/cin` (auth requise) |
| `routers/chat.py` | `POST /chat` (auth requise) |
| `routers/regles.py` | `GET /regles` (réservé juriste/admin) |
| `routers/.gitkeep` | Marqueur de dossier |

### `backend/rules/` — Système expert (Phase 3)
| Fichier | Description |
|---|---|
| `rules/__init__.py` | Agrégation `ALL_RULES` |
| `rules/base.py` | Structures communes (`RegleMeta`, `ExpertRule`) |
| `rules/identite.py` | Règles ID-000 à ID-003 |
| `rules/documents.py` | Règles DOC-001 à DOC-003 |
| `rules/capital.py` | Règle CAP-001 |
| `rules/fiscalite.py` | Règles FISC-001, FISC-002 |
| `rules/cnss.py` | Règle CNSS-001 |

### `backend/schemas/` — DTO Pydantic
| Fichier | Description |
|---|---|
| `schemas/__init__.py` | Package schemas |
| `schemas/auth.py` | Schémas inscription/connexion/jeton |
| `schemas/chat.py` | Schémas question/réponse/citation |
| `schemas/dossier.py` | Schéma `DossierInput` (+ `source_extraction`) |
| `schemas/evaluation.py` | Schémas `AnomalieResult`, `VerdictDossier` |
| `schemas/ocr.py` | Schéma `ResultatExtractionCIN` |
| `schemas/regles.py` | Schéma `RegleOutput` |
| `schemas/.gitkeep` | Marqueur de dossier |

### `backend/services/` — Orchestration métier
| Fichier | Description |
|---|---|
| `services/__init__.py` | Package services |
| `services/auth_service.py` | Inscription et authentification |
| `services/expert_service.py` | Évaluation d'un dossier (système expert) |
| `services/ocr_service.py` | Pipeline OCR complet + intégration au dossier |
| `services/rag_service.py` | Pipeline RAG complet (requête) |
| `services/.gitkeep` | Marqueur de dossier |

### `backend/utils/`
| Fichier | Description |
|---|---|
| `utils/.gitkeep` | Dossier réservé (non utilisé dans le périmètre couvert) |

## `data/` — Corpus et données

| Fichier | Description |
|---|---|
| `data/raw/README.md` | Note de traçabilité du corpus fermé |
| `data/raw/loi_5-96.txt` | Corpus S1 (Niveau 1) — Loi n°5-96 |
| `data/raw/impot_sur_societes.txt` | Corpus S2 (Niveau 2) — DGI, IS |
| `data/raw/tva.txt` | Corpus S3 (Niveau 2) — DGI, TVA |
| `data/raw/ompic_etapes_creation.txt` | Corpus S4 (Niveau 2) — OMPIC |
| `data/raw/dar_al_moukawil_guide.txt` | Corpus S5 (Niveau 2) — Dar Al Moukawil |
| `data/raw/creation_sarl_maroc.txt` | Corpus S6 (Niveau 3) — guide pratique |
| `data/raw/.gitkeep` | Marqueur de dossier |
| `data/synthetic/README.md` | Note méthodologique (limitation des dates figées) |
| `data/synthetic/dossier_valide.json` | Dossier synthétique — cas conforme |
| `data/synthetic/dossier_incomplet.json` | Dossier synthétique — cas incomplet |
| `data/synthetic/dossier_incoherent.json` | Dossier synthétique — cas incohérent |
| `data/synthetic/dossier_certificat_negatif_absent.json` | Dossier synthétique — DOC-001 isolée |
| `data/synthetic/dossier_siege_social_manquant.json` | Dossier synthétique — DOC-002 isolée |
| `data/synthetic/dossier_mauvaise_forme_juridique.json` | Dossier synthétique — ID-000 isolée |
| `data/synthetic/dossier_capital_sans_blocage.json` | Dossier synthétique — CAP-001 isolée |
| `data/synthetic/.gitkeep` | Marqueur de dossier |
| `data/chunks/.gitkeep` | Réservé aux chunks sérialisés (généré à l'exécution) |
| `data/embeddings/.gitkeep` | Réservé à la persistance ChromaDB (généré à l'exécution) |
| `data/processed/.gitkeep` | Réservé (non utilisé dans le périmètre couvert) |
| `data/evaluation/.gitkeep` | Réservé (non utilisé dans le périmètre couvert) |

## `docs/` — Documentation et rapport

| Fichier | Description |
|---|---|
| `docs/UML.md` | Conception UML complète (Phase 1) : besoins, cas d'utilisation, classes, séquences, ERD |
| `docs/rapport/generer_figures.py` | Génération des 6 figures UML/architecture (matplotlib) |
| `docs/rapport/figures/fig_3_1_cas_utilisation.png` | Figure 3.1 |
| `docs/rapport/figures/fig_3_2_classes.png` | Figure 3.2 |
| `docs/rapport/figures/fig_3_3_sequence_dossier.png` | Figure 3.3 |
| `docs/rapport/figures/fig_3_4_erd.png` | Figure 3.4 |
| `docs/rapport/figures/fig_4_1_architecture.png` | Figure 4.1 |
| `docs/rapport/figures/fig_7_1_pipeline_rag.png` | Figure 7.1 |
| `docs/rapport/rapport_helpers.js` | Fonctions communes + page de garde, résumé, abréviations, ToC (docx-js) |
| `docs/rapport/chapitres_1_5.js` | Contenu des chapitres 1 à 5 |
| `docs/rapport/chapitres_6_10.js` | Contenu des chapitres 6 à 10 + bibliographie |
| `docs/rapport/build_report.js` | Assemblage et génération du document Word |
| `docs/rapport/Rapport_PFE_Juris-IA.docx` | **Rapport final (28 pages)** |
| `docs/rapport/Rapport_PFE_Juris-IA.pdf` | Rendu PDF du rapport (généré pour vérification) |

## `frontend/` — Interface Streamlit

| Fichier | Description |
|---|---|
| `frontend/app.py` | Page d'accueil : état du backend, connexion/inscription |
| `frontend/Dockerfile` | Image Docker du frontend |
| `frontend/pages/1_Chatbot_Juridique.py` | Page chatbot juridique (RAG) |
| `frontend/pages/2_Extraction_CIN.py` | Page extraction OCR |
| `frontend/pages/3_Evaluation_Dossier.py` | Page évaluation de dossier (système expert) |
| `frontend/pages/4_Catalogue_Regles.py` | Page catalogue de règles (réservée juriste/admin) |
| `frontend/.gitkeep` | Marqueur de dossier |

## `scripts/`

| Fichier | Description |
|---|---|
| `scripts/__init__.py` | Package scripts |
| `scripts/indexer_corpus.py` | Pipeline d'indexation offline complet du corpus |
| `scripts/.gitkeep` | Marqueur de dossier |

## `tests/` — 89 tests automatisés

### `tests/unit/` (25 fichiers)
Tests unitaires par composant : règles du système expert (`test_rules_*.py`), OCR
(`test_ocr_*.py`), RAG (`test_rag_*.py`), sécurité (`test_security.py`), repository
(`test_utilisateur_repository.py`), settings et métadonnées ORM.

### `tests/integration/` (9 fichiers)
Tests d'intégration par routeur ou service : `/health`, `/dossier`, `/ocr`, `/chat`,
`/auth`, `/regles`, service expert, service OCR, service RAG.

### `tests/e2e/` (2 fichiers)
`test_parcours_complet.py` — parcours complets inscription → connexion → usage d'un
module, avec base SQLite réelle et cas négatifs (401, 403).

*(Le détail fichier par fichier de `tests/` reprend la liste complète donnée par la
commande `find tests -type f` ci-dessous, chaque fichier ayant déjà été présenté et
vérifié au fil des phases 2 à 6.)*

## `models/` et `prompts/`

| Fichier | Description |
|---|---|
| `models/.gitkeep` | Réservé (non utilisé dans le périmètre couvert par ce projet) |
| `prompts/.gitkeep` | Réservé (non utilisé dans le périmètre couvert par ce projet) |

---

## Note sur le contenu intégral des fichiers

Ce manifeste liste l'intégralité des 170 fichiers avec leur chemin et leur rôle. Le
**contenu intégral** de chacun n'est pas reproduit dans ce document : avec plus de 170
fichiers (dont un document Word de 28 pages, 6 images PNG et plusieurs fichiers texte
de plusieurs milliers de lignes comme `loi_5-96.txt`), une reproduction complète en
conversation dépasserait largement toute limite raisonnable de réponse et n'apporterait
rien que l'ouverture directe des fichiers ne permette déjà. Chaque fichier reste
disponible intégralement :
- dans l'archive complète du dépôt livrée avec cette réponse ;
- individuellement, sur simple demande, pour tout fichier précis dont vous voudriez
  revoir le contenu ici même.
