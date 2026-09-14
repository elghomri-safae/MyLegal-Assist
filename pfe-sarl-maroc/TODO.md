# TODO.md — Suivi des phases

> ⚠️ **Document historique (V1).** Suivi des phases de la première version du projet.
> **La référence actuelle du projet est `CONCEPTION_V2.md`**, complétée par
> `PROJECT_STATE.md`. Conservé pour la traçabilité de l'évolution.

> **PROJET TERMINÉ — Phases 0 à 7 complètes (20 juillet 2026).** Voir la section finale
> de ce document pour le bilan global et les points restant à la charge du porteur de
> projet. Voir `ARBORESCENCE.md` pour le manifeste complet des 170 fichiers du dépôt.

> Renumérotation à partir de la Phase 1 : voir `DECISIONS.md` (section « Décisions de
> Phase 1 ») pour la justification (insertion d'une phase Conception UML demandée
> explicitement par le porteur de projet).

Légende : ⏳ en attente · 🔄 en cours · ✅ terminé · 🔒 bloqué (décision requise)

## Phase 0 — Cadrage
- [x] ✅ Analyse du besoin, problématique, objectifs (`PROJECT.md`)
- [x] ✅ Proposition d'architecture initiale (`ARCHITECTURE.md`)
- [x] ✅ Planning Gantt 2 mois (`ARCHITECTURE.md`)
- [x] ✅ Registre de décisions initial (`DECISIONS.md`)

## Phase 1 — Conception UML
- [x] ✅ Besoins fonctionnels et non fonctionnels (`docs/UML.md`)
- [x] ✅ Diagramme de cas d'utilisation — acteurs entrepreneur/juriste/admin (`docs/UML.md`)
- [x] ✅ Diagramme de classes (`docs/UML.md`)
- [x] ✅ Diagrammes de séquence — 3 scénarios : chatbot RAG, dossier anti-rejet, OCR CIN (`docs/UML.md`)
- [x] ✅ Modèle de données / ERD (`docs/UML.md`)
- [x] ✅ Mise à jour `PROJECT.md` (§5.1 Acteurs), `ARCHITECTURE.md` (§7), `DECISIONS.md`
- [ ] 🔒 Validation de la Phase 1 par le porteur de projet avant Phase 2

## Phase 2 — Fondations techniques (anciennement Phase 1)
- [x] ✅ Squelette FastAPI (`backend/main.py`, routeur `/health` complet et fonctionnel)
- [x] ✅ Squelette Streamlit (`frontend/app.py`, page d'accueil + test de connectivité API)
- [x] ✅ Configuration (`backend/core/`, `backend/config/`, `.env.example`)
- [x] ✅ Modèles SQLAlchemy conformes à `docs/UML.md` §6 (12 tables) + migration Alembic initiale (`328c09bae8e8_schema_initial.py`)
- [x] ✅ `docker-compose.yml` + `backend/Dockerfile` + `frontend/Dockerfile`
- [x] ✅ `requirements.txt` (stack complète imposée)
- [x] ✅ `.gitignore`
- [x] ✅ `pyproject.toml` (black/isort/mypy/pytest) + `setup.cfg` (flake8)
- [x] ✅ Tests unitaires (`test_settings.py`, `test_models_metadata.py`) et d'intégration (`test_health.py`) — 5/5 passés, couverture 96 %
- [x] ✅ Vérification qualité : black, isort, flake8, mypy — tous propres (0 erreur)
- [ ] 🔒 Validation de la Phase 2 par le porteur de projet avant Phase 3

## Phase 3 — Système expert anti-rejet (anciennement Phase 2)
- [x] ✅ `backend/RULES.md` (catalogue de 11 règles, sources, niveaux, contradictions signalées)
- [x] ✅ `rules/capital.py` (CAP-001)
- [x] ✅ `rules/documents.py` (DOC-001, DOC-002, DOC-003)
- [x] ✅ `rules/identite.py` (ID-000, ID-001, ID-002, ID-003)
- [x] ✅ `rules/fiscalite.py` (FISC-001, FISC-002)
- [x] ✅ `rules/cnss.py` (CNSS-001)
- [x] ✅ `services/expert_service.py` (moteur d'évaluation + statut global)
- [x] ✅ `backend/schemas/dossier.py` + `evaluation.py` (DTO d'entrée/sortie)
- [x] ✅ Dossiers synthétiques de test — 7 cas (valide, incomplet, incohérent, certificat
      négatif absent, siège social manquant, mauvaise forme juridique, capital sans
      blocage) dans `data/synthetic/`
- [x] ✅ Tests unitaires (par catégorie de règle) et d'intégration (7 dossiers
      synthétiques paramétrés) — 30/30 tests passés, couverture 97 %
- [x] ✅ Vérification qualité : black, isort, flake8, mypy — tous propres
- [ ] 🔒 Validation de la Phase 3 par le porteur de projet avant Phase 4 (points signalés
      dans `backend/RULES.md` §2 : capital minimum SARL, durée de validité du certificat
      négatif, formule du droit d'enregistrement — 3 contradictions du corpus non arbitrées)

## Phase 4 — OCR CIN (anciennement Phase 3)
- [x] ✅ `backend/ocr/preprocessing.py` (prétraitement OpenCV)
- [x] ✅ `backend/ocr/extraction.py` (EasyOCR derrière une interface injectable `MoteurOCR`)
- [x] ✅ `backend/ocr/normalization.py` (nom, prénom, numéro CIN, date de naissance)
- [x] ✅ `backend/ocr/validation.py` (complétude des champs)
- [x] ✅ `backend/services/ocr_service.py` (pipeline complet + gestion d'erreurs +
      intégration au dossier via `vers_identite_personne`)
- [x] ✅ `backend/schemas/ocr.py` + ajout de `source_extraction` à `IdentitePersonneInput`
- [x] ✅ `backend/routers/ocr.py` (`POST /ocr/cin`, moteur injectable)
- [x] ✅ Rattrapage : `backend/routers/dossier.py` (`POST /dossier/evaluer`, engagement
      de Phase 2 non honoré en Phase 3)
- [x] ✅ Tests unitaires (prétraitement, extraction, normalisation, validation) et
      d'intégration (pipeline complet + 2 routeurs) — 50/50 tests passés, couverture 98 %
- [x] ✅ Vérification qualité : black, isort, flake8, mypy — tous propres (numpy épinglé
      à 1.26.4 pour compatibilité avec la cible mypy Python 3.11)
- [ ] 🔒 Validation de la Phase 4 par le porteur de projet avant Phase 5 (portée
      linguistique EasyOCR limitée au français, conventions de format CIN/date à
      valider avec des CIN réelles — voir PROJECT.md §5.2 et DECISIONS.md)

## Phase 5 — RAG juridique (anciennement Phase 4)
- [x] ✅ Corpus fermé matérialisé dans `data/raw/` (S1 à S6, fichiers texte réels)
- [x] ✅ `backend/rag/extraction.py` + `cleaning.py` (extraction et nettoyage réels)
- [x] ✅ `backend/rag/chunking.py` (LangChain `RecursiveCharacterTextSplitter`) +
      `chunk_store.py` (persistance JSON pour l'index lexical)
- [x] ✅ `backend/rag/embeddings.py` (sentence-transformers, interface injectable)
- [x] ✅ `backend/rag/indexing.py` (ChromaDB, interface injectable)
- [x] ✅ `backend/rag/lexical_search.py` (BM25 pur Python) + `hybrid_search.py` (fusion RRF)
- [x] ✅ `backend/rag/reranking.py` (priorité au niveau documentaire)
- [x] ✅ `backend/rag/generation.py` (Groq, interface injectable, prompt anti-hallucination)
- [x] ✅ `backend/services/rag_service.py` (orchestration query-time complète)
- [x] ✅ `backend/routers/chat.py` (`POST /chat`, 4 dépendances injectables)
- [x] ✅ `scripts/indexer_corpus.py` (pipeline d'indexation offline complet)
- [x] ✅ `frontend/pages/1_Chatbot_Juridique.py` (interface Streamlit du chatbot)
- [x] ✅ Tests unitaires (extraction, nettoyage, chunking, chunk_store, BM25, RRF,
      reranking, génération) et d'intégration (pipeline complet + routeur `/chat`) —
      71/71 tests passés, couverture 94 %
- [x] ✅ Vérification qualité : black, isort, flake8, mypy — tous propres (1 bug réel de
      tri détecté et corrigé dans `reranking.py` grâce aux tests)
- [ ] 🔒 Validation de la Phase 5 par le porteur de projet avant Phase 6 (dépendances
      lourdes — sentence-transformers, ChromaDB, Groq — non exercées dans ce sandbox ;
      persistance de l'historique des questions/réponses différée — voir DECISIONS.md)

## Phase 6 — Intégration API + UI (anciennement Phase 5)
- [x] ✅ Authentification JWT (`backend/core/security.py`, `backend/core/dependencies.py`)
- [x] ✅ Champ `mot_de_passe_hash` sur `Utilisateur` + migration Alembic dédiée
- [x] ✅ `backend/repositories/utilisateur_repository.py` (testé contre SQLite réelle)
- [x] ✅ `backend/services/auth_service.py` + `backend/routers/auth.py`
      (`POST /auth/inscription`, `POST /auth/connexion`)
- [x] ✅ `backend/routers/regles.py` (`GET /regles`, réservé juriste/admin — BF-05)
- [x] ✅ Assemblage : `/chat`, `/ocr/cin`, `/dossier/evaluer` exigent désormais une
      authentification (diffs sur les 3 routeurs + `main.py`)
- [x] ✅ Interface Streamlit complète (5 pages) : accueil + connexion/inscription,
      chatbot, extraction CIN, évaluation de dossier, catalogue de règles
- [x] ✅ Tests unitaires (sécurité, repository) et d'intégration (`/auth`, `/regles`,
      diffs sur `/chat`, `/ocr/cin`, `/dossier/evaluer`)
- [x] ✅ Tests end-to-end (`tests/e2e/`) : parcours complets inscription → connexion →
      usage d'un module, avec cas négatifs (401 sans jeton, 403 rôle refusé)
- [x] ✅ Vérification qualité : black, isort, flake8, mypy — tous propres ; 89/89 tests
      passés, couverture 95 %, stabilité vérifiée sur plusieurs exécutions consécutives
- [x] ✅ Bug de fragilité des tests (surcharges de dépendances partagées entre fichiers)
      détecté et corrigé (voir DECISIONS.md, ARCHITECTURE.md §14)
- [ ] 🔒 Validation de la Phase 6 par le porteur de projet avant Phase 7

## Phase 7 — Rédaction du rapport final (renommée sur demande explicite ; anciennement
« Tests & qualité », déjà couverte en continu à chaque phase — voir DECISIONS.md)
- [x] ✅ `docs/rapport/generer_figures.py` (6 figures UML/architecture en PNG, matplotlib)
- [x] ✅ `docs/rapport/rapport_helpers.js`, `chapitres_1_5.js`, `chapitres_6_10.js`,
      `build_report.js` (génération docx-js)
- [x] ✅ `docs/rapport/Rapport_PFE_Juris-IA.docx` — 28 pages (max. 40), Times New Roman 12,
      marges 2 cm, interligne simple
- [x] ✅ Page de garde, remerciements, résumé bilingue FR/EN, liste des abréviations
- [x] ✅ Table des matières statique (numéros de page vérifiés automatiquement depuis le
      PDF généré — le champ Word dynamique ne s'actualise pas hors Microsoft Word)
- [x] ✅ 10 chapitres numérotés avec sous-sections (1.1, 1.2…), équilibrés (17-20 lignes
      de contenu par sous-section en moyenne)
- [x] ✅ 6 figures UML/architecture (cas d'utilisation, classes, séquence, ERD,
      architecture globale, pipeline RAG), numérotées par chapitre
- [x] ✅ 8 tableaux comparatifs/synthétiques, numérotés par chapitre
- [x] ✅ Bibliographie à 17 entrées au format [1], [2]… (sources réelles : corpus fermé +
      documentations officielles + 2 références académiques BM25/RRF)
- [x] ✅ Conclusion générale avec limites (5 points) et perspectives (5 points)
- [x] ✅ Vérification : conversion PDF réelle (soffice), rendu de chaque page en image,
      concordance table des matières ↔ pages réelles vérifiée par script, tableaux et
      figures confirmés présents aux pages attendues (pdftotext, pdfimages)
- [ ] 🔒 Validation du rapport par le porteur de projet (champs `[Nom de l'établissement]`,
      `[Nom de l'étudiant·e]`, `[Nom de l'encadrant·e]`, `[XXXX-XXXX]` à compléter — non
      inventés, signalés comme placeholders, voir §10 de ce fichier)

## Phase 8 — Documentation technique et utilisateur complémentaires (optionnelle, non
démarrée — au-delà du périmètre demandé pour la clôture du projet)
- [ ] ⏳ Documentation technique détaillée (au-delà d'ARCHITECTURE.md/RULES.md existants)
- [ ] ⏳ Documentation utilisateur (guide de démarrage rapide, captures d'écran UI)

---

## Bilan final (20 juillet 2026)

**PROJET TERMINÉ.** Les phases 0 à 7 sont complètes, vérifiées et documentées. Résultat
global : 170 fichiers, 89 tests automatisés passés, couverture de code 95 %, aucune
erreur black/isort/flake8/mypy, rapport final de 28 pages livré. Voir `ARBORESCENCE.md`
pour le manifeste complet du dépôt et `PROJECT.md` §8 pour le tableau récapitulatif
phase par phase.

**Seule la Phase 8 (documentation technique/utilisateur complémentaire) reste optionnelle
et non démarrée** — elle n'a pas été demandée pour la clôture du projet et peut être
ajoutée ultérieurement si nécessaire.

**Points nécessitant une décision ou une action humaine avant tout usage réel** (non
résolus automatiquement, conformément à la Règle absolue n°8) :
1. Compléter les placeholders du rapport final (identité de l'établissement, de
   l'étudiant·e, de l'encadrant·e, année universitaire).
2. Trancher les 3 contradictions documentaires du corpus (`backend/RULES.md` §2) auprès
   d'une source juridique à jour.
3. Valider en conditions réelles les dépendances lourdes non exercées dans l'environnement
   de développement (EasyOCR, sentence-transformers, ChromaDB, API Groq).
4. Décider de l'implémentation de la persistance de l'historique des questions/réponses
   (modélisée en Phase 1, non implémentée).
