# CONCEPTION_V2.md — Refonte fonctionnelle Juris-IA (suivi intelligent de dossier)

> Document de conception uniquement. Aucun code. Base : audit du code V1 consigné dans
> `PROJECT_STATE.md` (§10 à §13). Version 4 de ce document : corrections issues de la
> revue critique finale (ambiguïté progression/validité clarifiée, historique des
> évaluations ajouté comme fonctionnalité manquante, `Question.dossier_id` acté plutôt
> que laissé ouvert, portée des compteurs du tableau de bord précisée). Chaque décision
> indique si elle est actée ou encore ouverte.

---

## 1. Vision produit (rappel, inchangé)

Juris-IA V2 n'est plus trois modules juxtaposés. C'est **un outil de suivi intelligent
d'un dossier de création de SARL/SARL AU**, utilisé par les clients d'un cabinet
("MyLegal"), pour préparer, corriger et fiabiliser leur dossier **avant** dépôt réel
(dépôt toujours effectué par le cabinet ou le client lui-même auprès d'OMPIC/CRI/DGI —
hors périmètre du logiciel, décision déjà actée).

Le cœur du produit est le **Dossier persistant**, autour duquel gravitent le **système
expert** (source de vérité sur l'état du dossier — moteur de validation inchangé dans sa
logique de règles), le **chatbot** (compagnon contextuel du dossier, façade du système
expert et du corpus juridique — voir §6), le **tableau de bord**, et une **validation
progressive** à la saisie.

---

## 2. Parcours utilisateur cible

1. MyLegal (rôle Admin) crée le compte du client (rôle Entrepreneur) → identifiants transmis.
2. Le client se connecte.
3. Le client crée un **Dossier** (« Créer une entreprise » côté interface — une seule
   entité technique, voir §4.2) : nom de projet, forme juridique visée.
4. Le client remplit le dossier **progressivement**. À chaque champ saisi, le système
   signale immédiatement les problèmes structurels simples (§8) — sans attendre un clic
   sur « Évaluer ».
5. À chaque visite, le dossier est retrouvé **pré-rempli** avec ce qui a déjà été saisi.
6. Le client peut interroger le **chatbot** à tout moment : celui-ci s'appuie d'abord sur
   l'état réel de son dossier (issu du système expert), puis mobilise le corpus juridique
   si une explication légale est nécessaire (voir §6).
7. Le client déclenche une **évaluation complète** (système expert, 11 règles) quand il
   le souhaite, autant de fois qu'il veut.
8. Chaque évaluation produit un verdict + une liste d'anomalies, et est **conservée**
   (historique).
9. Le client peut demander au chatbot d'expliquer une anomalie précise, ou comment la
   corriger.
10. Il corrige les champs concernés, relance une évaluation.
11. Sans anomalie bloquante restante, le dossier est signalé **« prêt pour dépôt »**
    (indicateur, pas un verrou — voir §5).
12. Le tableau de bord donne une vue d'ensemble de tous ses dossiers : statut, compteurs
    par gravité, progression de saisie, dernière évaluation.

---

## 3. Rôles et acteurs

| Rôle | Statut V2 | Justification |
|---|---|---|
| **Entrepreneur** | Conservé | Utilisateur principal du produit. Compte créé par Admin (pas d'auto-inscription — décision reportée en §10, toujours ouverte). |
| **Admin** | Conservé | Provisionnement des comptes clients + supervision technique. |
| ~~Juriste~~ | **Supprimé** | Aucune justification métier indispensable trouvée : le produit s'adresse aux clients de MyLegal, pas au cabinet lui-même, qui dispose déjà de ses outils internes. |

Le seul privilège que portait le rôle Juriste (`GET /regles`) n'existe plus du tout en
V2, indépendamment des rôles restants — voir §6.4.

---

## 4. Modèle de données cible

### 4.1 Vue d'ensemble

```
Utilisateur (rôle: entrepreneur | admin)
  │
  ├── Dossier  [0..N]                      (fusion Entreprise+Dossier)
  │     │
  │     ├── IdentitePersonne [0..N]         (inchangé, sans le champ source_extraction)
  │     ├── PieceJustificative [0..N]       (inchangé)
  │     │
  │     └── Evaluation [0..N]               (historisée, sans snapshot)
  │           │
  │           └── Anomalie [0..N]           (inchangé — porte règle, gravité, message,
  │                                            justification, référence documentaire)
  │
  └── Question [0..N]                       (dossier_id nullable)
        └── Reponse [1..1] → CitationSource [0..N]
```

### 4.2 Fusion Entreprise + Dossier (acté)

Une seule entité `Dossier`, enrichie d'un champ `nom_projet`. La relation était
strictement 1:1 sans cycle de vie indépendant : deux tables pour un seul objet
fonctionnel n'apportaient qu'un join permanent sans valeur ajoutée. Le vocabulaire
produit (« créer une entreprise » côté interface) reste possible sans entité technique
séparée — distinction UX/label, pas de modélisation.

### 4.3 `Evaluation` sans `snapshot_dossier` (acté)

L'`Evaluation` conserve : `dossier_id`, `date_evaluation`, `statut_global`, et sa liste
d'`Anomalie`. Chaque `Anomalie` porte déjà la règle déclenchée, sa gravité, son message
utilisateur, sa justification et sa référence documentaire — suffisant pour comprendre,
*a posteriori*, pourquoi une évaluation a échoué, sans reconstituer un instantané complet
des champs du dossier à cet instant.

### 4.4 Ce qui reste inchangé

- `Utilisateur`, `IdentitePersonne` (moins `source_extraction`), `PieceJustificative`,
  `Anomalie`.
- Le moteur de règles (`rules/*.py`) et son orchestration (`expert_service.py`).
- Le pipeline RAG (`backend/rag/*.py`) — inchangé dans sa mécanique, son rôle dans
  l'architecture est précisé au §6.

### 4.5 Toujours candidats à la suppression (hors périmètre de cette refonte)

- Table `Regle` (SQL, inutilisée). Sa disparition potentielle est indépendante du fait
  que le catalogue ne soit plus exposé (§6.4) : la table était déjà inutilisée avant
  cette décision, elle le reste.
- `DocumentCorpus`, `Chunk` (tables SQL inutilisées par le RAG, hors périmètre).

---

## 5. Cycle de vie du `Dossier` (simplifié)

**Décision actée : suppression définitive de l'état `soumis`.**

Le cycle de vie devient strictement à deux temps :

```
[brouillon]  ──(première évaluation déclenchée)──▶  [évalué]
                                                          │
                                              verdict = StatutGlobalEnum existant :
                                              conforme | conforme_avec_reserves | non_conforme
                                                          │
                                    conforme (ou conforme_avec_reserves, à trancher §10)
                                                          │
                                                          ▼
                                         indicateur « prêt pour dépôt » = vrai
```

- **`brouillon`** : dossier créé, jamais évalué.
- **`évalué`** : au moins une évaluation effectuée. Le verdict affiché est celui de la
  **dernière** évaluation (`StatutGlobalEnum`, déjà existant dans le code — `conforme`,
  `conforme_avec_reserves`, `non_conforme`).
- **Indicateur « prêt pour dépôt »** : booléen dérivé, vrai lorsque le dernier verdict est
  `conforme` (aucune anomalie bloquante ni avertissement) — **point à trancher** : doit-il
  être vrai aussi pour `conforme_avec_reserves` (aucune anomalie bloquante, mais des
  avertissements restants) ? Je recommande que oui : un avertissement, par construction du
  système expert, n'empêche pas le dépôt, seule une anomalie bloquante le fait. *(À
  valider — voir §10.)* C'est un simple indicateur, jamais un verrou qui empêcherait une
  action.

La valeur `soumis` de `StatutDossierEnum` (présente dans le code V1) n'est **pas
utilisée** en V2 — aucune action du parcours ne la justifie, et la garder aurait
recréé une ambiguïté déjà signalée dans la version précédente de ce document (distinction
« prêt selon le client » vs « prêt selon le système » jamais réellement nécessaire).

Toute modification du dossier après une évaluation ne change pas rétroactivement le
verdict affiché tant qu'une nouvelle évaluation n'a pas été relancée explicitement.

---

## 6. Rôle central du chatbot (renforcé)

### 6.1 Principe directeur

**Le système expert reste l'unique source de vérité sur l'état du dossier.** Le RAG et le
LLM n'interviennent jamais pour décrire ou déduire cet état — uniquement pour
l'expliquer une fois qu'il est connu avec certitude. Cette hiérarchie n'est pas nouvelle
(déjà esquissée dans la V1 de ce document), mais elle devient ici le principe de
conception explicite du chatbot, pas une option parmi d'autres.

### 6.2 Séquence de traitement d'une question contextuelle

1. **Chargement du contexte dossier** (toujours en premier, obligatoire) : dernière
   `Evaluation` du dossier concerné + ses `Anomalie` associées (règle, gravité, message,
   justification, référence documentaire — déjà présentes dans `RegleMeta`).
2. **Question factuelle sur l'état du dossier** (« quelles pièces me manquent ? »,
   « pourquoi mon dossier est-il refusé ? ») : réponse construite **directement à partir
   des `Anomalie`** chargées à l'étape 1, formatée en langage naturel. Aucun appel au RAG
   ni au LLM n'est nécessaire pour cette catégorie — la donnée est déjà connue avec
   certitude, la reformuler via un LLM n'apporterait aucune valeur et introduirait un
   risque d'erreur évitable.
3. **Question explicative** (« explique-moi cette anomalie », « comment la corriger »,
   « pourquoi cette règle existe légalement ») : c'est **uniquement à cette étape** que le
   RAG est sollicité — pour retrouver les extraits du corpus juridique qui justifient la
   règle en question, et les fournir au LLM aux côtés de l'anomalie déjà identifiée à
   l'étape 1. Le RAG agit comme **source documentaire d'appui**, jamais comme moyen de
   déterminer l'état du dossier lui-même.
4. **Question générale, sans lien avec un dossier précis** (« quel est le délai pour un
   certificat négatif ? ») : comportement RAG existant, inchangé, `dossier_id = NULL`.

### 6.3 Pourquoi cette hiérarchie plutôt qu'un chatbot qui interroge le RAG en premier ?

Si le RAG était sollicité en premier pour répondre à « pourquoi mon dossier est-il
refusé », le LLM pourrait produire une explication juridique plausible mais **déconnectée
du verdict réel** du dossier de l'utilisateur (les extraits récupérés parlent de la loi en
général, pas de son dossier précis). En imposant que l'état du dossier soit toujours
résolu par le système expert d'abord, puis éventuellement enrichi par le RAG, on élimine
structurellement ce risque : le chatbot ne peut pas halluciner un état de dossier, parce
que cet état ne lui est jamais laissé à déduire.

### 6.4 Catalogue des règles : plus d'exposition directe (décision actée)

**`GET /regles` disparaît entièrement de la conception.** Les règles ne sont plus
visibles qu'à travers deux canaux, tous deux déjà prévus :
- les `Anomalie` d'une évaluation (règle déclenchée, avec sa justification et sa
  référence documentaire),
- les explications du chatbot (§6.2, étape 3), qui peut détailler une règle précise sur
  demande, avec le support du RAG pour la contextualiser juridiquement.

Aucune vue « liste complète et statique des 11 règles » n'est prévue en dehors de ces
deux canaux — cohérent avec le principe de ne montrer une règle que lorsqu'elle a un
sens concret pour l'utilisateur (une anomalie réelle, ou une question posée), plutôt
qu'un catalogue générique consulté hors contexte.

### 6.5 Conséquence sur le modèle de données

`Question.dossier_id` nullable — `NULL` pour une question générale, renseigné pour une
question contextuelle. **Acté** (corrige une incohérence relevée en revue finale : ce
point figurait auparavant en « point ouvert » alors que toute la logique du §6.2 en
dépend structurellement — accepter le §6 implique nécessairement d'accepter ce champ,
il n'y a pas de version cohérente du chatbot contextuel sans lui).

---

## 7. Suppression du module OCR — conséquences exhaustives (vérifiées dans le code)

Décision confirmée par l'utilisateur. Vérifications faites par grep sur l'ensemble de
`backend/` pour s'assurer qu'aucune conséquence n'est oubliée :

| Élément | Action | Vérification |
|---|---|---|
| `backend/ocr/` (4 fichiers : preprocessing, extraction, normalization, validation) | Suppression complète | — |
| `backend/services/ocr_service.py` | Suppression | — |
| `backend/routers/ocr.py` | Suppression + retrait de l'enregistrement dans `main.py` | `main.py` enregistre 6 routeurs actuellement, passera à 5 |
| `backend/schemas/ocr.py` (`ResultatExtractionCIN`) | Suppression | — |
| `IdentitePersonne.source_extraction` (colonne modèle) + `IdentitePersonneInput.source_extraction` (schéma) | Suppression | Sans OCR, une seule source possible (saisie manuelle) |
| `SourceExtractionEnum` (`backend/models/enums.py`) | Suppression | Plus aucun consommateur une fois le champ ci-dessus retiré |
| `easyocr`, `opencv-python-headless` (`requirements.txt`) | Suppression | **Vérifié par grep** : `cv2`/`opencv` et `numpy` ne sont utilisés nulle part ailleurs dans `backend/` que dans le module OCR |
| `frontend/pages/2_Extraction_CIN.py` | Suppression | Aucun lien de code avec `frontend/pages/3_Evaluation_Dossier.py` (déjà confirmé non câblé lors de l'audit) |
| `tests/unit/test_ocr_*.py` (4), `tests/integration/test_ocr_service.py`, `test_router_ocr.py` | Suppression | 6 fichiers de test à retirer |
| Règle métier **ID-003** (`backend/rules/identite.py`) | **Inchangée** | Elle vérifie uniquement la présence de `numero_cin`, indépendamment de la façon dont il a été saisi |
| `PROJECT.md` §5.2, `ARBORESCENCE.md` | À mettre à jour plus tard | Documentation V1 obsolète — pas traité maintenant (phase de conception) |

Aucune conséquence cachée identifiée : la suppression est propre, confirmée par grep sur
tout `backend/`, pas seulement par lecture du module OCR isolément.

---

## 8. Validation progressive

### 8.1 Principe

Le code V1 contient déjà, sans le formaliser comme tel, une distinction entre deux
niveaux de validation :
- **Contrainte structurelle** : ex. `DossierInput.capital_social: float = Field(gt=0)`
  (`backend/schemas/dossier.py`) — une donnée sans sens intrinsèque, vérifiable sans
  référence légale.
- **Règle métier/légale** : ex. CAP-001 — nécessite une justification documentaire et une
  référence de source.

| Niveau | Déclenchement | Exemples | Persistance |
|---|---|---|---|
| **1 — Structurel** | Immédiat, à la saisie | Champ obligatoire vide, capital ≤ 0, date de naissance dans le futur, date de certificat négatif incohérente | **Aucune** — retour immédiat, non historisé |
| **2 — Métier/légal** | Sur demande explicite (« Évaluer ») | Les 11 règles actuelles (`rules/*.py`) | Persisté en `Evaluation` + `Anomalie[]` |

### 8.2 Pourquoi ne pas tout faire passer par le système expert existant ?

Les 11 règles actuelles supposent un dossier déjà structurellement valide. Le niveau 1
intervient en amont, sur des champs isolés — un rôle différent, pas un doublon. Le
niveau 2 reste l'unique moteur de validation métier, conformément au principe du §6.1
(le système expert est la seule source de vérité sur l'état du dossier).

### 8.3 Conséquence sur le modèle de données

Aucune nouvelle entité nécessaire — s'appuie sur les contraintes déjà présentes dans
`DossierInput` (Pydantic) et quelques vérifications ponctuelles supplémentaires.

---

## 9. Tableau de bord (révisé une seconde fois)

### 9.1 Design retenu

Pour chaque dossier, affichage de :
- **Nombre d'erreurs bloquantes** (`GraviteEnum.BLOQUANTE`)
- **Nombre d'avertissements** (`GraviteEnum.AVERTISSEMENT` **et** `GraviteEnum.INFORMATIVE`
  fusionnés — voir §9.2)
- **Indicateur de progression du dossier** (voir §9.3) — remplace le compteur « nombre de
  règles validées »
- **Date de la dernière évaluation**
- **Statut du dossier** (`brouillon` / verdict de `StatutGlobalEnum`) + indicateur
  « prêt pour dépôt » (§5)

**Précision (corrige une ambiguïté relevée en revue finale)** : les compteurs
d'erreurs bloquantes et d'avertissements portent exclusivement sur la **dernière**
évaluation du dossier, jamais sur un cumul de toutes les évaluations passées — cohérent
avec la règle déjà énoncée au §5 pour le verdict global (« le verdict affiché est celui
de la dernière évaluation »). L'historique complet reste consultable séparément (§9.4).

### 9.2 Fusion `informative` + `avertissement` à l'affichage (acté)

Seules **deux catégories visibles** en interface : `erreurs bloquantes` et
`avertissements`. Cette fusion est **strictement une décision d'affichage** : le modèle
de données garde les 3 valeurs réelles de `GraviteEnum` (`bloquante`, `avertissement`,
`informative` — répartition actuelle 9/1/1 sur les 11 règles, vérifiée par grep) sans
modification. Une `Anomalie` de gravité `informative` reste distinguable dans le détail
d'une évaluation ou dans une explication du chatbot ; elle est seulement regroupée avec
les avertissements au niveau du compteur global du tableau de bord, pour ne pas
complexifier la lecture d'ensemble avec une 3e catégorie peu représentée (1 règle sur 11
actuellement).

### 9.3 Indicateur de progression du dossier (remplace « nombre de règles validées »)

**Le compteur « nombre de règles validées » est retiré.** Justification déjà actée dans
la version précédente : le système ne distingue pas aujourd'hui une règle *non
applicable* (ex. CNSS-001 si le dossier ne déclare pas de salariés) d'une règle
*effectivement respectée* — les deux valent `False` pour `est_declenchee()`. Présenter ce
nombre comme « validé » est trompeur pour l'utilisateur final.

**Remplacement proposé** : un indicateur de **progression de saisie**, conceptuellement
différent et non ambigu — proportion de champs attendus effectivement renseignés dans le
dossier (ex. « 8 informations sur 12 complétées »), **indépendant de toute conformité
légale**. C'est un indicateur purement déclaratif sur l'état de saisie, pas un jugement de
conformité — il ne dit jamais « votre dossier est à 70 % correct », seulement « vous avez
renseigné 70 % des champs attendus ». Cette distinction est importante pour ne pas
recréer, sous un autre nom, l'ambiguïté qui a justifié la suppression du compteur
précédent.

**Précision (corrige une ambiguïté relevée en revue finale)** : un champ ne compte comme
« complété » que s'il est à la fois **renseigné et valide au sens de la validation
structurelle de niveau 1** (§8). Un champ rempli mais rejeté par le niveau 1 (ex. capital
saisi à une valeur négative) ne doit pas être compté comme complété — sinon l'indicateur
donnerait une fausse impression de bon état, exactement le défaut qui a justifié la
suppression du compteur « règles validées ». Cette règle rattache explicitement
l'indicateur de progression (§9.3) à la validation progressive (§8) : ce sont deux angles
de vue différents (complétude vs conformité légale) mais tous deux subordonnés à la même
condition de base — un champ invalide n'est jamais compté comme acquis.

Le détail exact des champs comptabilisés (quels champs du dossier + combien d'identités
d'associés attendues selon la forme juridique, etc.) est un détail d'implémentation, à
définir lors de la phase de conception technique, pas ici.

### 9.4 Historique des évaluations (nouveau — corrige une fonctionnalité oubliée relevée en revue finale)

Le modèle de données permet plusieurs `Evaluation` par `Dossier` (§4.1, §4.3), et le
parcours utilisateur (§2, étape 8) promet explicitement que chaque évaluation est
« conservée ». Cette promesse n'avait cependant, jusqu'ici, aucune traduction
fonctionnelle décrite — le tableau de bord (§9.1) ne montrait que la date de la dernière
évaluation, pas un accès à l'historique complet.

**Ajout** : depuis la fiche d'un dossier, une vue « historique des évaluations » liste,
par ordre chronologique, chaque évaluation passée avec sa date, son verdict
(`StatutGlobalEnum`), et son nombre d'anomalies par gravité (selon le regroupement du
§9.2). C'est une vue de lecture pure sur les `Evaluation` existantes, sans nouvelle
entité ni nouvelle logique métier — elle rend simplement visible ce que le modèle de
données permettait déjà sans être exploité.

---

## 10. Points ouverts restants

| # | Sujet | Statut |
|---|---|---|
| 10.1 | Auto-inscription Entrepreneur → remplacée par création via Admin | Toujours ouvert |
| 10.2 | Suppression de la table `Regle` (SQL, inutilisée) | Toujours ouvert, indépendant de cette refonte |
| 10.3 | Indicateur « prêt pour dépôt » : vrai uniquement si `conforme`, ou aussi si `conforme_avec_reserves` ? | **Proposition de Claude (inclure aussi conforme_avec_reserves), à valider** |
| 10.4 | Détail exact des champs comptabilisés par l'indicateur de progression (§9.3) | Reporté à la phase de conception technique |

Points tranchés dans ce tour et retirés de la liste : exposition du catalogue de règles
(§6.4), état `soumis` (§5), fusion `informative`/`avertissement` (§9.2), remplacement du
compteur de règles validées (§9.3), hiérarchie système expert / RAG dans le chatbot (§6),
`Question.dossier_id` (§6.5 — acté par dépendance structurelle avec §6), ambiguïté
progression/validité (§9.3), historique des évaluations ajouté (§9.4), portée des
compteurs du tableau de bord (§9.1).

---

## 11. Ce que cette conception ne couvre pas volontairement

- Notifications — non prioritaire, non traité.
- Schémas Pydantic / migrations Alembic / endpoints précis — phase d'implémentation.
- Modification du moteur de règles ou du pipeline RAG eux-mêmes — logique interne non
  remise en cause, seule leur intégration change.

---

*Ce document reste une conception ouverte tant que les points du §10 ne sont pas
arbitrés. Reporté dans `PROJECT_STATE.md` uniquement une fois validé dans son ensemble.*
