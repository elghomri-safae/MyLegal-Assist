# PROJECT.md — Cadrage du projet

> ⚠️ **Document historique (V1).** Décrit l'état du projet tel que cadré et livré en
> première version (Phases 0 à 7, 20 juillet 2026). Ce cadrage a depuis été audité et
> substantiellement révisé. **La référence actuelle du projet est `CONCEPTION_V2.md`**
> (conception fonctionnelle validée), complétée par `PROJECT_STATE.md` (mémoire de
> travail à jour). Ce document est conservé pour la traçabilité de l'évolution du
> projet, pas comme spécification à implémenter telle quelle.

**Statut : PROJET TERMINÉ (Phases 0 à 7 complètes, 20 juillet 2026).**
Voir `TODO.md` pour le détail phase par phase et `ARBORESCENCE.md` pour le manifeste
complet des 170 fichiers du dépôt final. Les points nécessitant une validation humaine
avant tout usage réel ou dépôt académique sont listés en fin de `TODO.md`.

**Corpus documentaire disponible à ce jour :**
- [S1] Loi n°5-96 sur la SNC, SCS, SCA, SARL et société en participation (Niveau 1 — texte de loi)
- [S2] Note DGI — Impôt sur les Sociétés (I.S.) (Niveau 2 — source officielle)
- [S3] Note DGI — Taxe sur la Valeur Ajoutée (TVA) (Niveau 2 — source officielle)
- [S4] OMPIC — « Création et vie de l'entreprise » (Niveau 2 — source officielle)
- [S5] Guide « Démarches administratives de création d'entreprise » — Dar Al Moukawil / Attijariwafa bank, certifié Mazars (Niveau 3 — guide pratique, à recouper avec sources officielles avant citation à valeur juridique)
- [S6] Synthèse de vulgarisation « Création SARL / SARL AU au Maroc » (Niveau 3 — documentation pratique secondaire)

---

## 1. Analyse du besoin

La création d'une SARL ou SARL AU au Maroc implique un enchaînement de démarches
administratives réparties entre plusieurs organismes (OMPIC, DGI, greffe du tribunal
de commerce, CNSS, imprimerie officielle). Le corpus documentaire disponible (S1 à S6)
montre que :

- Les démarches sont bien documentées mais dispersées entre plusieurs sources de niveaux
  différents (texte de loi, sites institutionnels, guides pratiques), avec des montants
  et délais qui peuvent varier légèrement selon la source (ex. coût du certificat négatif :
  ~230 DH selon [S6], ou 50 DH + 100 DH + 20 DH de timbre selon [S4]/[S5] — **information à
  clarifier, voir DECISIONS.md**).
- Un porteur de projet non-initié doit collecter et interpréter lui-même les pièces à
  fournir (CIN, statuts, certificat négatif, attestation de blocage de capital…), avec un
  risque élevé d'erreurs ou d'oublis entraînant un rejet de dossier (mauvaise forme
  juridique, capital mal renseigné, siège social non justifié, etc.).
- Il n'existe pas, dans le corpus fourni, d'outil unique combinant : réponse aux questions
  juridiques, extraction automatique des données d'identité (CIN), et contrôle de
  cohérence du dossier avant dépôt.

**Constat :** il y a un besoin d'un outil d'accompagnement qui (1) répond aux questions
juridiques du porteur de projet à partir de sources fiables et citées, (2) automatise la
saisie de l'identité via OCR de la CIN, et (3) détecte en amont les causes de rejet d'un
dossier de création de SARL/SARL AU, avant le dépôt effectif auprès des administrations.

## 2. Problématique du PFE

> Comment concevoir un système logiciel capable d'assister un porteur de projet dans la
> création d'une SARL/SARL AU au Maroc, en combinant recherche documentaire juridique
> fiable (RAG), extraction automatisée de données d'identité (OCR) et détection
> explicable des causes de rejet de dossier (système expert à base de règles), tout en
> garantissant la traçabilité de chaque réponse à une source documentaire de niveau
> connu ?

## 3. Objectifs fonctionnels

1. **Chatbot juridique** : répondre en langage naturel aux questions sur la création de
   SARL/SARL AU (étapes, pièces, délais, coûts, obligations fiscales/sociales) avec
   citation systématique de la source et de son niveau (1/2/3).
2. **OCR CIN** : à partir d'une image de CIN marocaine, extraire nom, prénom, numéro CIN,
   date de naissance ; normaliser et valider le format des champs extraits.
3. **Système expert anti-rejet** : à partir d'un dossier de création (formulaire structuré),
   évaluer sa conformité selon des règles documentées (capital, documents, identité,
   fiscalité, CNSS) et produire un verdict avec justification traçable (règle, source,
   article) pour chaque anomalie détectée.
4. Interface utilisateur unique (Streamlit) permettant d'utiliser les 3 modules.

## 4. Objectifs techniques

- Architecture modulaire et testable : séparation API (FastAPI) / Services / Repositories
  / Models, conforme aux principes SOLID.
- Pipeline RAG complet et traçable (extraction → nettoyage → chunking → embeddings →
  indexation → recherche → reranking → LLM → réponse avec citations).
- Système expert 100% rule-based, sans ML, avec règles documentées et testées
  individuellement.
- Projet reproductible : `git clone` + `docker compose up` (ou `pip install -r
  requirements.txt`), sans secret en dur (`.env`).
- Couverture de tests (pytest) sur chaque module, y compris dossiers synthétiques pour le
  système expert (valide, incomplet, incohérent, certificat négatif absent, siège social
  manquant, mauvaise forme juridique…).

## 5. Périmètre précis

### Inclus dans le périmètre
- SARL et SARL AU (personne morale), au sens de la loi 5-96 [S1].
- Les 3 modules décrits ci-dessus (chatbot RAG, OCR CIN, système expert anti-rejet).
- Corpus documentaire = exclusivement les documents fournis dans cette conversation
  (S1 à S6). Aucune information ne sera recherchée sur Internet pour les réponses
  juridiques.

### Hors périmètre (à ce stade, sauf décision contraire)
- Les autres formes juridiques (SA, SAS, SNC, SCS, SCA, coopératives, associations,
  auto-entrepreneur) : mentionnées dans le corpus mais **non couvertes fonctionnellement**
  par le système expert dans une première version — seulement en information
  conversationnelle via le chatbot.
- Dépôt effectif des dossiers auprès des administrations (le système n'automatise pas
  la soumission réelle à l'OMPIC/DGI/greffe/CNSS — il prépare et fiabilise le dossier).
- Signature électronique, paiement en ligne des taxes/frais.
- Authentification multi-utilisateurs avancée / gestion de rôles (à confirmer, voir
  DECISIONS.md).

### Information manquante à signaler (Règle absolue n°8)
- Le corpus ne précise pas le montant exact et unique des frais du certificat négatif :
  [S4]/[S5] indiquent 50 DH (recherche) + 100 DH (certificat) + 20 DH (timbre) = 170 DH,
  tandis que [S6] indique « environ 230 DH ». Les deux valeurs seront conservées et
  attribuées chacune à sa source ; aucune valeur unique ne sera inventée.
- Aucune information dans le corpus sur un éventuel besoin d'authentification, de
  multi-tenant, de volumétrie attendue, ou de contraintes d'hébergement — à clarifier
  avec le porteur de projet avant la Phase 1.

## 5.1 Acteurs et utilisateurs (ajouté en Phase 1)

Trois acteurs sont identifiés pour la conception UML :

- **Entrepreneur** (porteur de projet) : pose des questions au chatbot juridique,
  soumet une image de CIN pour extraction OCR, remplit et soumet un dossier de création
  au système expert, consulte le verdict de conformité.
- **Juriste** : consulte le catalogue de règles du système expert (`backend/RULES.md`)
  et le corpus documentaire indexé, peut proposer une évolution de règle (avec
  justification documentaire — validée hors-ligne, jamais générée automatiquement sans
  source, conformément à la Règle absolue n°1), consulte l'historique des évaluations
  de dossiers à titre d'audit.
- **Admin** : supervise l'état technique du système (santé API, connexions base de
  données/ChromaDB, journaux d'erreurs), gère la configuration non sensible. La gestion
  des secrets reste hors interface (fichier `.env`, jamais exposée en UI).

*Information manquante signalée* : le corpus ne définit aucun rôle applicatif ; ce
découpage (entrepreneur/juriste/admin) est une proposition de conception à valider par
le porteur de projet, non une exigence issue du corpus documentaire.

## 5.2 Périmètre du module OCR (ajouté en Phase 4)

Le module OCR (`backend/ocr/`, `backend/services/ocr_service.py`) couvre en V1
uniquement les champs en écriture latine de la CIN (nom, prénom, numéro de CIN, date de
naissance). L'écriture arabe présente sur la CIN marocaine n'est pas traitée : ce n'est
pas une exigence du corpus (qui ne fournit aucune image ni spécification de CIN), mais
une limitation de portée assumée par manque de certitude sur la compatibilité
multilingue exacte du modèle EasyOCR pour la combinaison français + arabe (voir
DECISIONS.md, Phase 4, et `backend/ocr/extraction.py`).

*Information manquante signalée* : le corpus ne contient aucune image de CIN ni de
spécification officielle de son format ; les motifs de reconnaissance (format du numéro
de CIN, format de date) sont des conventions techniques à valider avec des CIN réelles,
pas des règles issues du corpus.

## 5.3 Périmètre du module RAG (ajouté en Phase 5)

Le chatbot juridique (`backend/rag/`) répond exclusivement à partir du corpus fermé
matérialisé dans `data/raw/` (S1 à S6). Le pipeline de recherche hybride (sémantique +
lexicale) et le reranking par niveau documentaire sont des choix d'architecture
techniques, non issus du corpus : ils visent à maximiser la probabilité de retrouver les
extraits pertinents et à privilégier les sources de niveau 1/2 sur les guides de niveau 3
en cas d'ambiguïté, mais ne garantissent pas l'exhaustivité de la réponse. Le prompt
système impose explicitement au modèle de ne répondre qu'à partir des extraits fournis et
de signaler l'absence de réponse plutôt que d'inventer (Règle absolue n°1/n°8) ; ceci est
une consigne au modèle, pas une garantie technique absolue contre les hallucinations —
point à surveiller lors des tests utilisateurs réels (voir DECISIONS.md, Phase 5).

## 5.4 Authentification et rôles (ajouté en Phase 6)

L'authentification était explicitement hors périmètre en Phase 2 (`DECISIONS.md`,
« proposition par défaut : pas d'authentification en V1 »). Le porteur de projet l'a
demandée explicitement en Phase 6 ; cette décision est donc révisée avec justification
(Règle absolue n°2, voir `DECISIONS.md`, Phase 6). L'authentification est simplifiée
(jeton JWT porteur, pas un flux OAuth2 complet) et sert principalement à appliquer le
contrôle d'accès par rôle défini en Phase 1 (`PROJECT.md` §5.1) : `/regles` (catalogue du
système expert, BF-05) est réservé aux rôles juriste et admin ; `/chat`, `/ocr/cin` et
`/dossier/evaluer` exigent une authentification (tout rôle).

*Information manquante signalée* : le corpus ne définit aucune politique de mot de passe,
de durée de session ou de gestion des rôles ; les choix techniques (PBKDF2, durée de
validité du jeton de 60 minutes) sont des conventions de développement, pas des exigences
issues du corpus ou du cahier des charges initial.

## 5.5 Rapport final (ajouté en Phase 7)

Le rapport final (`docs/rapport/Rapport_PFE_Juris-IA.docx`, 28 pages) contient plusieurs
champs volontairement laissés en placeholder (`[Nom de l'établissement]`,
`[Nom de l'étudiant·e]`, `[Nom de l'encadrant·e]`, `[XXXX-XXXX]`), faute d'information
disponible dans le corpus ou dans les échanges du projet sur l'identité de
l'établissement, de l'étudiant ou de l'encadrant. Conformément à la Règle absolue n°8,
ces informations ne sont pas inventées ; elles doivent être complétées par le porteur de
projet avant tout dépôt académique du rapport.

## 6. Contraintes

- **Juridiques** : toute règle citée doit indiquer sa source, son niveau (1/2/3) et sa
  référence précise (article/chapitre/section) — Règle absolue n°7.
- **Techniques** : stack imposée (Python 3.11, FastAPI, SQLAlchemy 2.x, Alembic,
  Pydantic v2, PostgreSQL, Streamlit, LangChain, ChromaDB, sentence-transformers
  multilingual-e5-large, Groq API, EasyOCR, OpenCV, Pillow, pytest, black, isort,
  flake8, mypy).
- **Documentaires** : pas de recours à des sources externes au corpus fourni pour les
  réponses juridiques.
- **Qualité** : PEP8, typage, docstrings, architecture SOLID, code exécutable après
  chaque phase.
- **Temporelles** : planning académique de 2 mois (voir section 7).
- **Reproductibilité** : aucune clé API en dur, exécution possible via clone + install
  seuls.

## 7. Planning (Gantt — 2 mois indicatif)

Voir `ARCHITECTURE.md` pour le diagramme Gantt (Mermaid) et sa version visuelle.

## 8. Clôture du projet (Phase 7, 20 juillet 2026)

Toutes les phases prévues (0 à 7) sont terminées et vérifiées :

| Phase | Livrable principal | Statut |
|---|---|---|
| 0 | Cadrage, architecture proposée, planning | ✅ |
| 1 | Conception UML complète | ✅ |
| 2 | Fondations techniques (FastAPI, SQLAlchemy, Alembic, Docker) | ✅ |
| 3 | Système expert anti-rejet (11 règles) | ✅ |
| 4 | Module OCR (EasyOCR, pipeline complet) | ✅ |
| 5 | Module RAG juridique (recherche hybride, reranking, génération) | ✅ |
| 6 | Intégration, authentification JWT, rôles, UI Streamlit (5 pages) | ✅ |
| 7 | Rapport final (28 pages) et manifeste final du dépôt | ✅ |

**Résultat global** : 170 fichiers, 89 tests automatisés passés, couverture de code 95 %,
aucune erreur black/isort/flake8/mypy. Voir `ARBORESCENCE.md` pour le détail fichier par
fichier et `TODO.md` pour l'historique complet, phase par phase.

**Points restant à la charge du porteur de projet avant tout usage réel** (non résolus
par le système, conformément à la Règle absolue n°8 — signalés, non inventés) :
1. Compléter les champs placeholder du rapport (`[Nom de l'établissement]`, etc. — §5.5).
2. Trancher les 3 contradictions documentaires identifiées (capital minimum SARL, durée
   de validité du certificat négatif, formule du droit d'enregistrement — voir
   `backend/RULES.md` §2) auprès d'une source juridique à jour.
3. Valider le pipeline OCR/RAG avec des données réelles (CIN authentiques, clé API Groq
   active) : les dépendances lourdes n'ont pas été exercées de bout en bout dans
   l'environnement de vérification (voir `ARCHITECTURE.md` §11.5, §13.4).
4. Décider si la persistance de l'historique des questions/réponses (modélisée mais non
   implémentée) doit être ajoutée.

