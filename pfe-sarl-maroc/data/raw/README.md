# data/raw — Corpus documentaire fermé (S1 à S6)

Ces 6 fichiers matérialisent le corpus documentaire fermé défini en Phase 0 (`PROJECT.md`),
utilisé exclusivement par le pipeline RAG (`backend/rag/`, Phase 5). Aucune source externe
n'est ajoutée (Règle absolue n°1/n°2).

| Fichier | Source | Niveau |
|---|---|---|
| `loi_5-96.txt` | Loi n°5-96 (SARL, SNC, SCS, SCA, société en participation) | 1 |
| `impot_sur_societes.txt` | DGI — Impôt sur les sociétés | 2 |
| `tva.txt` | DGI — Taxe sur la valeur ajoutée | 2 |
| `ompic_etapes_creation.txt` | OMPIC — Registre Central du Commerce | 2 |
| `dar_al_moukawil_guide.txt` | Guide Dar Al Moukawil n°1 (Attijariwafa bank), certifié Mazars | 2 |
| `creation_sarl_maroc.txt` | Documentation pratique de vulgarisation | 3 |

**Note sur `loi_5-96.txt`** : les articles activement cités par le système expert
(`backend/rules/*.py`, `backend/RULES.md`) — notamment les art. 44, 46, 47, 50, 51 — sont
reproduits intégralement. Certains articles purement procéduraux et répétitifs (ex. régime
détaillé de la gérance de la SCA, sanctions pénales article par article) ont été condensés en
résumé fidèle plutôt que reproduits mot à mot, uniquement pour la lisibilité du corpus ; ceci
est signalé explicitement ici plutôt que masqué (Règle absolue n°8).
