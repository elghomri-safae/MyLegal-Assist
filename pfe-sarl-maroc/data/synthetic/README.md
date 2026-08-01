# data/synthetic — Dossiers synthétiques de test (Phase 3)

Ces fichiers JSON alimentent `tests/integration/test_expert_service.py` et
couvrent les cas exigés par le cahier des charges : valide, incomplet,
incohérent, certificat négatif absent, siège social manquant, mauvaise
forme juridique — plus un cas additionnel isolant la règle de blocage du
capital (`CAP-001`).

**Limitation connue** : `certificat_negatif_date_delivrance` est une date
figée (2026-07-15), choisie pour rester dans la fenêtre de validité de 3
mois (`DUREE_VALIDITE_CERTIFICAT_NEGATIF_JOURS`, voir
`backend/rules/documents.py`) au moment de la rédaction de ce document
(2026-07-20). Si ces fixtures sont exécutées bien après octobre 2026, les
dossiers censés être "valides" ou isolant une autre règle risquent de voir
la règle `DOC-001` se déclencher par expiration du certificat. Il faudra
alors régénérer ces dates. Ce n'est pas fait automatiquement afin de garder
des fixtures statiques et lisibles.
