# RULES.md — Catalogue des règles du système expert anti-rejet

**Statut : Phase 3 — En attente de validation**
**Périmètre** : SARL et SARL AU uniquement (cf. `PROJECT.md`, §5).
**Hiérarchie des sources** (rappel, cf. corpus documentaire) :
- Niveau 1 : Textes de loi (Loi 5-96)
- Niveau 2 : Sources officielles (OMPIC, Dar Al Moukawil, DGI, CNSS)
- Niveau 3 : Guides pratiques
- **Niveau 0 (convention locale, hors hiérarchie légale)** : contrainte de conception du
  projet, non issue du corpus documentaire (utilisée uniquement pour `ID-000`, qui limite
  le périmètre fonctionnel du système et non une exigence légale).

---

## 1. Catalogue des règles

| ID | Catégorie | Gravité | Niveau | Référence | Fichier |
|---|---|---|---|---|---|
| ID-000 | identite | bloquante | 0 | PROJECT.md §5 (périmètre) | `rules/identite.py` |
| ID-001 | identite | bloquante | 1 | Loi 5-96, art. 44 et 47 | `rules/identite.py` |
| ID-002 | identite | bloquante | 1 | Loi 5-96, art. 44, al. 3 | `rules/identite.py` |
| ID-003 | identite | bloquante | 2 | OMPIC FAQ Q1 ; Dar Al Moukawil p.13 | `rules/identite.py` |
| DOC-001 | documents | bloquante | 2 | OMPIC FAQ Q1, Q3 | `rules/documents.py` |
| DOC-001B | documents | bloquante | 2 | OMPIC FAQ Q3 ; guide vulgarisation §1 | `rules/documents.py` |
| DOC-002 | documents | bloquante | 1 | Loi 5-96, art. 50 (5°) | `rules/documents.py` |
| DOC-003 | documents | bloquante | 1 | Loi 5-96, art. 50, al. 1 | `rules/documents.py` |
| CAP-001 | capital | bloquante | 2 | OMPIC étape 5 ; Dar Al Moukawil p.10 ; Loi 5-96 art. 51 | `rules/capital.py` |
| FISC-001 | fiscalite | bloquante | 2 | OMPIC étape 8 (documents à présenter) | `rules/fiscalite.py` |
| FISC-002 | fiscalite | informative | 2 | OMPIC étape 6 ; Dar Al Moukawil p.11 | `rules/fiscalite.py` |
| CNSS-001 | cnss | avertissement | 2 | OMPIC étape 9 ; Dar Al Moukawil p.14 | `rules/cnss.py` |

12 règles au total, réparties sur les 5 fichiers imposés par l'arborescence du prompt
(`capital.py`, `documents.py`, `identite.py`, `fiscalite.py`, `cnss.py`).

**Mise à jour (phase de stabilisation du module Évaluation)** : `DOC-001` a été scindée
en deux règles distinctes pour corriger un défaut de logique métier. L'ancienne version
traitait « certificat déclaré disponible mais sans date de délivrance renseignée » comme
équivalent à « expiré », ce qui affirmait une information jamais demandée à l'utilisateur.
Désormais : `DOC-001` se déclenche uniquement si la case « disponible » n'est pas cochée
(aucune hypothèse de date) ; `DOC-001B` se déclenche uniquement si une date de délivrance
a été renseignée ET qu'elle dépasse la durée de validité usuelle. Si la case est cochée
sans date renseignée, aucune des deux règles ne se déclenche : le document est considéré
comme disponible, conformément au principe de cette plateforme (pré-vérification basée
sur les déclarations de l'utilisateur, pas un contrôle des documents originaux — ceux-ci
sont contrôlés ultérieurement par les juristes de MyLegal).

---

## 2. Contradictions du corpus signalées (Règle absolue n°8)

Conformément à la règle « si une information manque ou se contredit, la signaler
explicitement plutôt que de la supposer », les trois points suivants **n'ont pas été
arbitrés** par une règle de rejet automatique :

### 2.1 Capital minimum de la SARL — **non implémenté comme règle bloquante**

- Loi 5-96, art. 46 (texte fourni, Niveau 1) : « Le capital de cette société doit être
  de cent mille dirhams au moins. »
- OMPIC (Niveau 2) : « Le montant du capital social est librement fixé par les
  associés. »
- Dar Al Moukawil (Niveau 2/3) : « SARL : capital minimum 1 DH (suppression de la
  formalité de blocage...). »
- Guide de vulgarisation (Niveau 3) : « Capital minimum : Aucun (libre depuis la
  réforme de 2006). »

→ Le texte de loi fourni semble antérieur à une réforme mentionnée par les sources de
niveau 2/3 (2006) qui aurait supprimé ce minimum, mais cette réforme n'est pas incluse
dans le corpus documentaire fourni. **Aucune règle `CAP-000` de capital minimum n'a donc
été codée.** Seule la règle de blocage bancaire au-delà de 100 000 DH (`CAP-001`), qui
est concordante entre toutes les sources, a été implémentée.

### 2.2 Durée de validité du certificat négatif — **valeur retenue avec réserve documentée**

- OMPIC FAQ Q3 (Niveau 2) et guide de vulgarisation (Niveau 3) : 3 mois.
- Guide Dar Al Moukawil, infographie p.7 (Niveau 2/3) : « délai d'un an ».

→ `DOC-001B` retient 3 mois (majorité des sources, dont la FAQ officielle OMPIC), mais le
message utilisateur et la justification de la règle mentionnent explicitement cette
divergence plutôt que de la masquer. `DOC-001B` ne se déclenche que si une date de
délivrance a été renseignée par l'utilisateur (voir §1, mise à jour).

### 2.3 Formule du droit d'enregistrement des statuts — **non implémenté comme règle bloquante**

- OMPIC, étape 6 (Niveau 2) : « 1 % du capital avec un minimum de 1000 DH. »
- Dar Al Moukawil, p.11 (Niveau 2/3) : « Droit fixe de 1000 DH si le capital ne dépasse
  pas 500 000 DH ; 1 % du capital si le capital est supérieur à 500 000 DH. »

→ Ces deux formulations ne donnent pas le même résultat pour toutes les valeurs de
capital (ex. capital = 400 000 DH : 4000 DH selon OMPIC, 1000 DH selon Dar Al Moukawil).
`FISC-002` a donc été codée comme un **rappel informatif** (gravité `informative`, ne
modifiant jamais le statut global), présentant les deux formules sans en privilégier
une, avec renvoi vers la Direction Régionale des Impôts pour confirmation.

---

## 3. Logique de statut global

Le statut global d'une évaluation (`backend/services/expert_service.py`) est déduit de
la gravité maximale rencontrée parmi les anomalies déclenchées :

- Une anomalie **bloquante** → statut `non_conforme`.
- En l'absence de bloquante, une anomalie **avertissement** → statut
  `conforme_avec_reserves`.
- Les anomalies **informative** (ex. `FISC-002`) n'affectent jamais le statut : elles
  sont des rappels documentaires, pas des causes de rejet.

---

## 4. Dossiers synthétiques de test

Voir `data/synthetic/` (7 fichiers JSON) et `tests/integration/test_expert_service.py` :
`dossier_valide`, `dossier_incomplet`, `dossier_incoherent`, `dossier_certificat_
negatif_absent`, `dossier_siege_social_manquant`, `dossier_mauvaise_forme_juridique`,
`dossier_capital_sans_blocage`.


<!-- # RULES.md — Catalogue des règles du système expert anti-rejet

**Statut : Phase 3 — En attente de validation**
**Périmètre** : SARL et SARL AU uniquement (cf. `PROJECT.md`, §5).
**Hiérarchie des sources** (rappel, cf. corpus documentaire) :
- Niveau 1 : Textes de loi (Loi 5-96)
- Niveau 2 : Sources officielles (OMPIC, Dar Al Moukawil, DGI, CNSS)
- Niveau 3 : Guides pratiques
- **Niveau 0 (convention locale, hors hiérarchie légale)** : contrainte de conception du
  projet, non issue du corpus documentaire (utilisée uniquement pour `ID-000`, qui limite
  le périmètre fonctionnel du système et non une exigence légale).

---

## 1. Catalogue des règles

| ID | Catégorie | Gravité | Niveau | Référence | Fichier |
|---|---|---|---|---|---|
| ID-000 | identite | bloquante | 0 | PROJECT.md §5 (périmètre) | `rules/identite.py` |
| ID-001 | identite | bloquante | 1 | Loi 5-96, art. 44 et 47 | `rules/identite.py` |
| ID-002 | identite | bloquante | 1 | Loi 5-96, art. 44, al. 3 | `rules/identite.py` |
| ID-003 | identite | bloquante | 2 | OMPIC FAQ Q1 ; Dar Al Moukawil p.13 | `rules/identite.py` |
| DOC-001 | documents | bloquante | 2 | OMPIC FAQ Q1, Q3 | `rules/documents.py` |
| DOC-001B | documents | bloquante | 2 | OMPIC FAQ Q3 ; guide vulgarisation §1 | `rules/documents.py` |
| DOC-002 | documents | bloquante | 1 | Loi 5-96, art. 50 (5°) | `rules/documents.py` |
| DOC-003 | documents | bloquante | 1 | Loi 5-96, art. 50, al. 1 | `rules/documents.py` |
| CAP-001 | capital | bloquante | 2 | OMPIC étape 5 ; Dar Al Moukawil p.10 ; Loi 5-96 art. 51 | `rules/capital.py` |
| FISC-001 | fiscalite | bloquante | 2 | OMPIC étape 8 (documents à présenter) | `rules/fiscalite.py` |
| FISC-002 | fiscalite | informative | 2 | OMPIC étape 6 ; Dar Al Moukawil p.11 | `rules/fiscalite.py` |
| CNSS-001 | cnss | avertissement | 2 | OMPIC étape 9 ; Dar Al Moukawil p.14 | `rules/cnss.py` |

11 règles au total, réparties sur les 5 fichiers imposés par l'arborescence du prompt
(`capital.py`, `documents.py`, `identite.py`, `fiscalite.py`, `cnss.py`).

---

## 2. Contradictions du corpus signalées (Règle absolue n°8)

Conformément à la règle « si une information manque ou se contredit, la signaler
explicitement plutôt que de la supposer », les trois points suivants **n'ont pas été
arbitrés** par une règle de rejet automatique :

### 2.1 Capital minimum de la SARL — **non implémenté comme règle bloquante**

- Loi 5-96, art. 46 (texte fourni, Niveau 1) : « Le capital de cette société doit être
  de cent mille dirhams au moins. »
- OMPIC (Niveau 2) : « Le montant du capital social est librement fixé par les
  associés. »
- Dar Al Moukawil (Niveau 2/3) : « SARL : capital minimum 1 DH (suppression de la
  formalité de blocage...). »
- Guide de vulgarisation (Niveau 3) : « Capital minimum : Aucun (libre depuis la
  réforme de 2006). »

→ Le texte de loi fourni semble antérieur à une réforme mentionnée par les sources de
niveau 2/3 (2006) qui aurait supprimé ce minimum, mais cette réforme n'est pas incluse
dans le corpus documentaire fourni. **Aucune règle `CAP-000` de capital minimum n'a donc
été codée.** Seule la règle de blocage bancaire au-delà de 100 000 DH (`CAP-001`), qui
est concordante entre toutes les sources, a été implémentée.

### 2.2 Durée de validité du certificat négatif — **valeur retenue avec réserve documentée**

- OMPIC FAQ Q3 (Niveau 2) et guide de vulgarisation (Niveau 3) : 3 mois.
- Guide Dar Al Moukawil, infographie p.7 (Niveau 2/3) : « délai d'un an ».

→ `DOC-001` retient 3 mois (majorité des sources, dont la FAQ officielle OMPIC), mais le
message utilisateur et la justification de la règle mentionnent explicitement cette
divergence plutôt que de la masquer.

### 2.3 Formule du droit d'enregistrement des statuts — **non implémenté comme règle bloquante**

- OMPIC, étape 6 (Niveau 2) : « 1 % du capital avec un minimum de 1000 DH. »
- Dar Al Moukawil, p.11 (Niveau 2/3) : « Droit fixe de 1000 DH si le capital ne dépasse
  pas 500 000 DH ; 1 % du capital si le capital est supérieur à 500 000 DH. »

→ Ces deux formulations ne donnent pas le même résultat pour toutes les valeurs de
capital (ex. capital = 400 000 DH : 4000 DH selon OMPIC, 1000 DH selon Dar Al Moukawil).
`FISC-002` a donc été codée comme un **rappel informatif** (gravité `informative`, ne
modifiant jamais le statut global), présentant les deux formules sans en privilégier
une, avec renvoi vers la Direction Régionale des Impôts pour confirmation.

---

## 3. Logique de statut global

Le statut global d'une évaluation (`backend/services/expert_service.py`) est déduit de
la gravité maximale rencontrée parmi les anomalies déclenchées :

- Une anomalie **bloquante** → statut `non_conforme`.
- En l'absence de bloquante, une anomalie **avertissement** → statut
  `conforme_avec_reserves`.
- Les anomalies **informative** (ex. `FISC-002`) n'affectent jamais le statut : elles
  sont des rappels documentaires, pas des causes de rejet.

---

## 4. Dossiers synthétiques de test

Voir `data/synthetic/` (7 fichiers JSON) et `tests/integration/test_expert_service.py` :
`dossier_valide`, `dossier_incomplet`, `dossier_incoherent`, `dossier_certificat_
negatif_absent`, `dossier_siege_social_manquant`, `dossier_mauvaise_forme_juridique`,
`dossier_capital_sans_blocage`. -->
