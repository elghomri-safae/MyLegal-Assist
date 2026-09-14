# PROJECT_STATE.md — Mémoire de travail Juris-IA

> Ce fichier fait référence, avec `CONCEPTION_V2.md`, pour la suite de la collaboration.
> Il est mis à jour à chaque nouvelle étape (audit, conception, puis implémentation).
> **Statut au 30/07 : phase de conception terminée. `CONCEPTION_V2.md` est validé et
> figé comme référence fonctionnelle du projet (voir §14). Le projet passe en phase
> d'implémentation.**

---

## 1. Identité du projet

- **Nom** : Juris-IA
- **Objectif** : accompagner un entrepreneur marocain dans la création d'une SARL / SARL AU
- **Stack imposée** : Python 3.11, FastAPI, PostgreSQL (SQLAlchemy 2.x, Alembic), Streamlit,
  ChromaDB, LangChain, Groq (LLM), sentence-transformers (multilingual-e5-large), EasyOCR,
  OpenCV, Pillow, JWT (PyJWT), Docker, pytest, black/isort/flake8/mypy.
- **Statut annoncé par la doc** : "PROJET TERMINÉ", Phases 0 à 7 closes (20 juillet 2026).
  170 fichiers, 89 tests, couverture 95 %, qualité (black/isort/flake8/mypy) propre.
- **Objectif réel de la mission actuelle** : transformer ce projet en démonstration de PFE
  **cohérente**, pas juste ajouter des features. Remise en question de l'architecture
  autorisée et souhaitée. Suppression > artificialité.

## 2. Les 3 modules fonctionnels

| Module | Rôle | Statut déclaré |
|---|---|---|
| Chatbot juridique (RAG) | Répond aux questions sur la création SARL/SARL AU à partir d'un corpus fermé de 6 documents (S1-S6), avec citation systématique source + niveau (1/2/3) | Codé, testé via doublures (dépendances lourdes jamais exécutées réellement) |
| OCR CIN | Extrait nom, prénom, n° CIN, date de naissance depuis une image CIN (écriture latine seulement, pas l'arabe) | Codé, testé via un moteur factice (EasyOCR réel jamais exécuté dans l'environnement de dev) |
| Système expert anti-rejet | Évalue un dossier structuré selon 11 règles documentées (capital, documents, identité, fiscalité, CNSS) → verdict conforme / conforme_avec_reserves / non_conforme + justification traçable | Codé, rule-based strict (aucun ML), 30/30 tests passés |

Interface unique : Streamlit, 5 pages (accueil/connexion, chatbot, OCR, dossier, catalogue de règles).

## 3. Corpus documentaire (fermé, aucune recherche web autorisée pour le juridique)

- **S1** — Loi n°5-96 (SNC/SCS/SCA/SARL/société en participation) — Niveau 1 (texte de loi)
- **S2** — Note DGI, Impôt sur les Sociétés — Niveau 2
- **S3** — Note DGI, TVA — Niveau 2
- **S4** — OMPIC, "Création et vie de l'entreprise" — Niveau 2
- **S5** — Guide Dar Al Moukawil / Attijariwafa, certifié Mazars — Niveau 3
- **S6** — Synthèse vulgarisée "Création SARL/SARL AU au Maroc" — Niveau 3

## 4. Rôles applicatifs (RBAC)

- **Entrepreneur** : chatbot, OCR, soumission/consultation de dossier.
- **Juriste** : consulte `GET /regles` (catalogue système expert) + corpus indexé, historique
  des évaluations à titre d'audit. *(⚠️ point à challenger — voir §7 : semble exister
  uniquement pour justifier une route protégée)*.
- **Admin** : supervision technique (santé API, connexions DB/ChromaDB, logs), pas de gestion
  de secrets en UI (`.env` uniquement).
- **Auth** : JWT porteur (pas OAuth2 complet), hash PBKDF2-HMAC-SHA256, durée jeton 60 min.
  Introduite en Phase 6 alors qu'explicitement exclue en Phase 2 — revirement assumé et
  documenté, mais à vérifier si le reste de l'archi (dossier, OCR, historique) a été
  repensé autour de l'utilisateur authentifié ou juste "plaqué" après coup.

## 5. Endpoints connus (déclaratif, pas encore vérifié dans le code)

- `POST /auth/inscription`, `POST /auth/connexion`
- `POST /chat` (auth requise, tout rôle) → RAG
- `POST /ocr/cin` (auth requise, tout rôle) → OCR
- `POST /dossier/evaluer` (auth requise, tout rôle) → système expert
- `GET /regles` (réservé juriste/admin) → catalogue des 11 règles
- `GET /health`

## 6. Points déjà signalés par la doc elle-même (non résolus, honnêtes)

1. **3 contradictions du corpus jamais arbitrées** (`backend/RULES.md` §2) :
   - capital minimum SARL
   - durée de validité du certificat négatif
   - formule du droit d'enregistrement
2. **Dépendances lourdes jamais exécutées réellement** : EasyOCR, sentence-transformers,
   ChromaDB, API Groq — tout testé via interfaces/doublures (`MoteurOCR`, `ModeleEmbedding`,
   `IndexVectoriel`, `ClientLLM`). **Donc "89/89 tests passent" ne prouve pas que le produit
   fonctionne réellement de bout en bout.**
3. **Persistance de l'historique Q/R modélisée (`Question`, `Reponse`, `CitationSource`) mais
   non implémentée** — tables potentiellement mortes.
4. Placeholders non complétés dans le rapport final (nom établissement/étudiant/encadrant,
   année universitaire).
5. Montant du certificat négatif incohérent entre sources (170 DH vs ~230 DH) — les deux
   valeurs sont conservées et attribuées, pas arbitrées.
6. OCR : conventions de format CIN/numéro/date non validées avec de vraies CIN (aucune image
   CIN dans le corpus).

## 7. Mon évaluation initiale (couche 1, avant lecture du code) — à confirmer/infirmer

**Points forts**
- Traçabilité systématique source + niveau de fiabilité (1/2/3).
- Discipline "signaler plutôt qu'inventer" appliquée partout, y compris dans le rapport.
- Séparation SOLID claire (routers/services/repositories/rules).
- Système expert explicable, rule-based assumé (pas de ML injustifié).

**Doutes / suspects d'artificialité (à vérifier dans le code)**
- Rôle **Juriste** : semble exister pour justifier une seule route protégée (`GET /regles`).
  Risque de fonctionnalité "pour faire complet" plutôt que besoin réel démontrable.
- **170 fichiers** pour 3 modules / 2 mois de PFE : à juger une fois le code vu — soit vraie
  modularité, soit sur-ingénierie qui dilue l'effort loin des 3 fonctionnalités clés.
- Recherche hybride (sémantique + BM25 + RRF + reranking par niveau) sur un corpus de
  **seulement 6 documents** : complexité potentiellement disproportionnée par rapport au
  volume réel de données — à challenger.

**Incohérences à surveiller**
- Auth ajoutée tardivement (Phase 6) après avoir été explicitement exclue (Phase 2).
- Système "anti-rejet" dont certains seuils métier sont eux-mêmes incertains dans le corpus.

## 8. Ordre de lecture du code prévu (proposé, modifiable)

1. Modèles SQLAlchemy (`backend/models/`) + ERD/UML → cohérence données ↔ 3 modules réels.
2. Système expert (`rules/*.py`, `RULES.md`, `expert_service.py`) → cœur métier démontrable.
3. Pipeline RAG (`rag/*.py`, `rag_service.py`) → juger si la complexité est justifiée pour
   6 documents.
4. OCR (dernier, scope le plus limité).

## 9. Règles de travail convenues avec l'utilisateur

- Une seule chose modifiée à la fois.
- Toujours analyser avant de coder.
- Toujours expliquer le "pourquoi".
- Toujours attendre validation avant implémentation.
- Tout ce qui est modifié doit être testé.
- Documentation mise à jour si nécessaire.
- Préférence : supprimer plutôt que garder de l'artificiel.

## 10. AUDIT CODE — Module Données/Persistance (couche 2, basé sur le code)

**Source** : archive `claude.rar` extraite dans `/home/claude/juris-ia/claude/pfe-sarl-maroc`.
Vérifié par grep exhaustif (`.add(`, `db.commit`, `session.commit`) sur tout `backend/`.

### Constat central (confirmé dans le code)
Sur les 12 tables ORM déclarées (`backend/models/`), **une seule est réellement écrite en
base : `Utilisateur`**, via `backend/repositories/utilisateur_repository.py:25-26`
(`self._db.add(utilisateur)` / `self._db.commit()`). C'est le seul repository qui existe
dans `backend/repositories/`. Les 11 autres tables (`Dossier`, `IdentitePersonne`,
`PieceJustificative`, `EvaluationDossier`, `Anomalie`, `Regle`, `Question`, `Reponse`,
`CitationSource`, `DocumentCorpus`, `Chunk`) ne sont **jamais instanciées ni persistées**
nulle part dans `backend/services/`, `backend/routers/`, `backend/repositories/`.

### Détail par endpoint
- **`POST /dossier/evaluer`** (`routers/dossier.py`) → `expert_service.evaluer_dossier()`
  est une fonction pure, **aucune session DB en paramètre**. Aucun endpoint de création de
  `Dossier` n'existe dans toute l'API (pas de `POST /dossier`).
- **`POST /chat`** (`routers/chat.py`) → retourne directement le résultat, aucune écriture
  de `Question`/`Reponse`/`CitationSource` malgré les relations ORM complètes déclarées.
- **`GET /regles`** (`routers/regles.py`) → lit `ALL_RULES`, une liste Python
  (`rules/__init__.py`, dataclasses `RegleMeta`), **pas la table SQL `Regle`**, qui duplique
  exactement les mêmes champs sans jamais être peuplée ni lue.
- **`POST /ocr/cin`** (`routers/ocr.py`) → aucun paramètre `dossier_id`, ne peut de toute
  façon rattacher une identité à un dossier (FK `dossier_id` non nullable sur
  `IdentitePersonne`).

### Conséquences factuelles
1. Le rôle **Juriste** n'a qu'un seul privilège réel dans le code : `GET /regles`, qui lit
   un fichier Python statique — aucune dépendance DB.
2. Le cycle "créer dossier → attacher identité OCR → évaluer → consulter historique" décrit
   dans l'UML **n'existe pas dans le code exposé** : seule l'évaluation stateless existe.
3. Les 3 modules (`chat`, `dossier`, `ocr`) sont **juxtaposés, pas intégrés** : aucun état
   partagé entre eux. L'OCR ne nourrit jamais un dossier ; un dossier évalué n'est jamais
   retrouvable ensuite.

## 11. AUDIT CODE — Pipeline RAG (couche 3, basé exclusivement sur le code)

**Fichiers lus intégralement** : `backend/rag/*.py` (11 fichiers, 682 lignes),
`backend/services/rag_service.py`, `scripts/indexer_corpus.py`, `data/raw/*.txt`.

### Correction factuelle
Le corpus n'est **pas du PDF** : `data/raw/` contient 6 fichiers `.txt` bruts, lus par
`Path.read_text()` (`rag/extraction.py`). Pas de parsing PDF/OCR sur le corpus.

### Taille réelle du corpus (mesurée)
~95 000 caractères / ~14 000 mots au total. Avec chunk_size=800 / overlap=120
(`chunking.py`), **environ 130-140 chunks au total** sur les 6 documents.

### Pipeline exact (fichier → rôle)
| Étape | Fichier | Détail vérifié |
|---|---|---|
| Lecture | `rag/extraction.py` | `CATALOGUE_CORPUS` figé, 6 `DocumentBrut`, texte brut |
| Nettoyage | `rag/cleaning.py` | regex espaces/\n multiples, strip — minimal |
| Chunking | `rag/chunking.py` | LangChain `RecursiveCharacterTextSplitter`, 800/120 |
| Cache chunks | `rag/chunk_store.py` | JSON plat, `data/chunks/corpus_chunks.json` |
| Embeddings | `rag/embeddings.py` | `intfloat/multilingual-e5-large`, normalisés |
| Index vectoriel | `rag/indexing.py` | ChromaDB, métrique cosine explicite |
| Recherche lexicale | `rag/lexical_search.py` | BM25 pur Python (K1=1.5, B=0.75), en mémoire |
| Fusion | `rag/hybrid_search.py` | RRF, constante=60, top5+top5 |
| Reranking | `rag/reranking.py` | Priorité niveau documentaire si écart score ≤0.02 |
| Génération | `rag/generation.py` | Groq `llama-3.3-70b-versatile`, top 4 extraits |
| Orchestration offline | `scripts/indexer_corpus.py` | extraction→nettoyage→chunking→embeddings→ChromaDB |
| Orchestration online | `services/rag_service.py` | encode→hybride→rerank[:4]→génération |

### Constats factuels significatifs
1. **Métadonnées de chunk limitées** : `document_titre`, `niveau`, `type_source`,
   `position` uniquement. Aucune référence d'article/section de loi extraite — citation
   finale = `"extrait n°{position}"`, pas une référence légale précise.
2. **Citations garanties par construction** (`generation.py`) : toujours les extraits
   envoyés au LLM, jamais extraites du texte généré — fiable, mais les 4 extraits sont
   cités même si le LLM n'en a utilisé qu'une partie.
3. **Complexité vs volume** : hybride + RRF + reranking sur ~130-140 chunks seulement —
   confirmé par calcul direct, sujet ouvert à trancher.
4. **Aucune dépendance lourde jamais exécutée réellement** (sentence-transformers,
   ChromaDB, Groq) — reconfirmé en lisant le code.

## 12. Nouvelle mission (29/07) — "Architecte logiciel principal"

L'utilisateur a fourni une vision produit révisée à trancher en 8 décisions :
1. **Workflow inter-modules** : chatbot/OCR/évaluation doivent collaborer, pas juste
   coexister (confirme l'audit §10).
2. **Modélisation des données** : Utilisateur → Entreprise (à justifier) → Dossier →
   Evaluations → Anomalies. Un utilisateur peut avoir plusieurs entreprises ; une
   entreprise plusieurs dossiers (si pertinent — à trancher par Claude).
3. **Persistance réelle des dossiers** : sauvegarde, reprise à J+n, réévaluation,
   historique conservé — répond directement au constat §10.
4. **Réévaluation de la valeur métier de l'OCR** : analyse argumentée sur le code
   attendue avant toute décision de suppression/remplacement. **Pas encore fait.**
5. **Chatbot "compagnon du dossier"** : contextualisé (pourquoi refusé, pièces
   manquantes, explication d'anomalie, prochaines étapes) — pas juste Q/R générique.
6. **Tableau de bord** : dossiers, état, progression, anomalies, historique.
7. **Notifications** : non prioritaire, plus tard.
8. **Audit RAG avant toute modif** : **fait, voir §11 ci-dessus.**

Positionnement produit clarifié : Juris-IA devient un outil de **préparation** de dossier
pour les clients d'un cabinet ("MyLegal"), pas un dépôt officiel. Le dépôt réel reste fait
par le cabinet/client auprès d'OMPIC/CRI/DGI. Comptes créés par MyLegal (pas
d'auto-inscription entrepreneur implicite).

**Prochaine étape convenue** : auditer la valeur métier réelle de l'OCR (décision 4) sur
la base du code (`backend/ocr/*.py`, `backend/services/ocr_service.py`), avant de statuer
sur la modélisation des données (décision 2) et le workflow (décision 1), car l'OCR
conditionne en partie la modélisation d'`IdentitePersonne`. Pas encore fait.

## 13. AUDIT CODE — Valeur métier réelle du module OCR (couche 4, décision 4 de la nouvelle mission)

**Fichiers lus intégralement** : `backend/ocr/*.py` (4 fichiers, 300 lignes),
`backend/services/ocr_service.py` (78 lignes), `backend/routers/ocr.py`,
`backend/schemas/ocr.py`, `backend/schemas/dossier.py`, `backend/rules/identite.py`,
`frontend/pages/2_Extraction_CIN.py`, `frontend/pages/3_Evaluation_Dossier.py` (début),
`requirements.txt`.

### Constat central (confirmé dans le code, pas une supposition)
**Le module OCR n'est intégré à rien**, à aucun niveau :
- `POST /ocr/cin` ne prend aucun `dossier_id` — aucun moyen API de le rattacher à un dossier.
- Sur les 4 champs extraits (nom, prénom, numero_cin, date_naissance), **un seul est
  consommé par le système expert** : `numero_cin`, et uniquement sa **présence** (règle
  ID-003, `backend/rules/identite.py`). `nom`, `prenom`, `date_naissance` ne sont testés
  par aucune règle métier dans tout `backend/rules/`.
- Le champ `source_extraction` (OCR vs MANUEL) existe dans `IdentitePersonneInput` mais
  n'est exploité nulle part (aucune règle, aucun affichage différencié).
- Côté UI : `frontend/pages/2_Extraction_CIN.py` affiche le résultat avec `st.json()` —
  aucune écriture en `st.session_state`. `frontend/pages/3_Evaluation_Dossier.py` a des
  champs de saisie manuelle vides par défaut, sans lien de code avec la page OCR.
  **L'utilisateur doit retaper à la main ce que l'OCR vient d'extraire.**

### Coût technique mesuré
- ~424 lignes de code applicatif (pipeline + service + router + schéma).
- 382 lignes de tests (6 fichiers).
- Dépendance `easyocr==1.7.2` → tire transitivement PyTorch/torchvision (non épinglés
  explicitement, mais obligatoires), jamais exécutée réellement dans l'environnement de
  dev (confirmé une 3e fois, cette fois en lisant `ocr/extraction.py` : import différé
  `import easyocr` à l'instanciation).
- Premier appel réel : 1-2 min de chargement de modèles (avertissement explicite dans
  `frontend/pages/2_Extraction_CIN.py`).

### Verdict argumenté
Coût technique (dépendance ML lourde, jamais testée en conditions réelles, fragile en
Docker) objectivement disproportionné par rapport à la valeur produite actuelle (un JSON
affiché à l'écran, non relié au reste de l'application). **Le défaut est dans
l'intégration manquante, pas dans l'idée du module.** Deux options soumises à
l'utilisateur, non tranchées par Claude (décision produit) :
- **Option A — Compléter** : brancher `/ocr/cin` sur le futur cycle de vie du dossier
  (`POST /dossier/{id}/identites/ocr`), donner enfin un sens à `source_extraction`.
- **Option B — Remplacer** : si le risque technique est jugé trop élevé pour une
  démo, réallouer l'effort vers le chatbot compagnon du dossier ou le tableau de bord
  (décisions 5/6 de la nouvelle mission).

**Décision utilisateur : Option B retenue — suppression complète du module OCR.**
Confirmée et détaillée dans `CONCEPTION_V2.md` §7 (conséquences exhaustives vérifiées :
modèles, routes, services, UI, dépendances, tests).

---

## 14. CONCEPTION V2 — validée et figée (30/07)

**`CONCEPTION_V2.md` est la version finale de la conception fonctionnelle.** Confirmé
après une revue critique dédiée (relations entre entités, cycle de vie du dossier, rôle
du chatbot vs système expert vs RAG, responsabilités des modules, redondances,
fonctionnalités manquantes) qui a abouti à 4 corrections appliquées au document
(ambiguïté progression/validité clarifiée, historique des évaluations ajouté comme
fonctionnalité manquante, `Question.dossier_id` acté plutôt que laissé ouvert, portée des
compteurs du tableau de bord précisée) avant validation finale : *« La conception est
cohérente et je n'ai plus de remarque majeure. »*

### 14.1 Décisions actées (résumé — détail complet dans `CONCEPTION_V2.md`)

| Sujet | Décision |
|---|---|
| Rôles | `Entrepreneur` + `Admin` uniquement. **Rôle Juriste supprimé** (pas de justification métier indispensable — le cabinet a ses outils internes). |
| Modèle de données | **Fusion `Entreprise`/`Dossier`** en une seule entité `Dossier` (+ champ `nom_projet`) — la relation 1:1 sans cycle de vie indépendant ne justifiait pas deux tables. |
| `Evaluation` | Historisée (plusieurs évaluations par dossier conservées), **sans `snapshot_dossier`** — les `Anomalie` (règle, gravité, message, justification, référence documentaire) suffisent à comprendre a posteriori un verdict passé. |
| Cycle de vie du dossier | Simplifié à **`brouillon → évalué`** (état `soumis` du code V1 abandonné). Indicateur « prêt pour dépôt » dérivé du verdict, jamais un verrou. |
| Chatbot | **Devient la façade du système expert et du RAG**, avec une hiérarchie stricte : le système expert reste l'unique source de vérité sur l'état du dossier ; le RAG n'intervient jamais pour déduire cet état, uniquement pour l'expliquer juridiquement une fois connu. Séquence : anomalies du dossier d'abord (réponse factuelle, sans LLM) → RAG + LLM seulement pour les questions explicatives. |
| Catalogue de règles | **`GET /regles` supprimé de la conception.** Les règles ne sont visibles qu'à travers les anomalies d'une évaluation et les explications du chatbot — plus de vue catalogue statique hors contexte. |
| Tableau de bord | Abandon du pourcentage de complétude initial ; puis abandon du compteur « règles validées » (ambigu — confond « non applicable » et « respectée »). Design final : erreurs bloquantes / avertissements (fusion visuelle `avertissement`+`informative`, le modèle garde les 3 valeurs réelles) / indicateur de progression de saisie (complétude, pas conformité) / dernière évaluation / statut. Ajout d'une **vue historique des évaluations** (fonctionnalité manquante identifiée en revue finale). |
| Validation progressive | **Nouveau** : niveau 1 (structurel, immédiat, non persisté) distinct du niveau 2 (11 règles métier, sur demande, persisté) — formalise une distinction déjà présente en germe dans le code V1 (contraintes Pydantic vs règles `rules/*.py`). |
| Module OCR | **Supprimé intégralement** — coût technique (dépendance PyTorch, jamais éprouvée) très supérieur à la valeur produite (aucune intégration constatée dans le code V1, confirmé par audit §13). Conséquences exhaustives listées dans `CONCEPTION_V2.md` §7. |
| Comptes utilisateurs | Création par Admin (MyLegal), pas d'auto-inscription libre pour l'Entrepreneur — *décision encore ouverte formellement, voir §10.1 de `CONCEPTION_V2.md`*. |

### 14.2 Points encore ouverts (mineurs, non bloquants pour démarrer l'implémentation)

Reportés de `CONCEPTION_V2.md` §10 — à trancher au fil de l'implémentation, dès qu'ils
deviennent concrètement nécessaires :
1. Auto-inscription Entrepreneur vs création exclusive par Admin.
2. Suppression de la table SQL `Regle` (déjà inutilisée en V1, indépendamment de la V2).
3. Indicateur « prêt pour dépôt » : `conforme` seul, ou aussi `conforme_avec_reserves` ?
   (proposition de Claude : inclure les deux — un avertissement n'empêche pas le dépôt).
4. Détail exact des champs comptabilisés par l'indicateur de progression de saisie.

### 14.3 Cohérence documentaire vérifiée et corrigée

Un bandeau de renvoi a été ajouté en tête de chacun des 6 documents V1
(`PROJECT.md`, `ARCHITECTURE.md`, `TODO.md`, `ARBORESCENCE.md`, `DECISIONS.md`,
`AUDIT_TECHNIQUE.md`), les signalant explicitement comme documentation **historique**
et renvoyant vers `CONCEPTION_V2.md` + ce fichier comme référence actuelle. Choix
délibéré : **ne pas réécrire ces documents** plutôt que les corriger ligne à ligne —
ils restent des témoins fidèles et utiles de l'état V1 et de l'évolution du projet
(narratif défendable en soutenance : cadrage → audit critique → refonte), et une
réécriture complète aurait été un risque d'erreur plus grand qu'un bandeau clair. Les
deux documents de référence actuels (`CONCEPTION_V2.md`, `PROJECT_STATE.md`) sont
désormais copiés à la racine du dépôt du projet, aux côtés des documents historiques.

Aucune contradiction restante identifiée entre `CONCEPTION_V2.md` et `PROJECT_STATE.md`
eux-mêmes (même relecture croisée effectuée dans le cadre de cette mise à jour).

---

## 15. Prochaine phase : implémentation

Conformément aux règles de travail convenues (§9) et aux consignes explicites données
pour cette phase :
- Respecter strictement `CONCEPTION_V2.md`.
- Ne plus modifier l'architecture sans validation explicite de l'utilisateur.
- Travailler par petites étapes.
- Après chaque étape : exécuter les tests, corriger les régressions, **attendre la
  validation de l'utilisateur avant de continuer**.
- Mettre à jour ce fichier (`PROJECT_STATE.md`) au fur et à mesure de l'avancement de
  l'implémentation (nouvelle section par étape significative, sur le même modèle que
  les audits ci-dessus).

*Statut de ce fichier : phase de conception terminée. Prêt pour le démarrage de
l'implémentation.*
