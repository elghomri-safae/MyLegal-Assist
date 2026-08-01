# Audit technique — Juris-IA (PFE SARL Maroc)

> ⚠️ **Document historique (V1).** Corrections de bugs appliquées à la première version
> du code, dont plusieurs concernent le module OCR — retiré dans la conception V2 (voir
> `CONCEPTION_V2.md` §7). Conservé pour la traçabilité, pas comme référence de l'état
> actuel du code.

Baseline avant audit : 89/89 tests, black/isort/flake8/mypy propres (confirmé).
Après audit : **100/100 tests**, qualité toujours propre, aucune régression.

## Bugs corrigés

### 1. Normalisation du numéro de CIN (bug bloquant signalé initialement)
- **Fichier** : `backend/ocr/normalization.py`
- **Cause** : regex à correspondance exacte, sans tolérance aux séparateurs
  (`BE 123456`, `BE-123456`) ni aux confusions visuelles classiques d'EasyOCR
  (`8E123456`, `BEI23456`).
- **Correctif** : normalisation des séparateurs, correction positionnelle des
  confusions caractères (jamais globale), tolérance 5–7 chiffres.
- **Tests** : `tests/unit/test_ocr_normalization.py` (+4 tests).

### 2. Conversion couleur RGB traitée comme BGR
- **Fichier** : `backend/ocr/preprocessing.py`
- **Cause** : `cv2.COLOR_BGR2GRAY` appliqué à un tableau numpy en réalité RGB
  (Pillow) — inversait les poids des canaux rouge/bleu dans la luminance.
- **Correctif** : `cv2.COLOR_RGB2GRAY`.
- **Tests** : `tests/unit/test_ocr_preprocessing.py` (+1 test).

### 3. Clé JWT par défaut acceptée silencieusement en production
- **Fichier** : `backend/config/settings.py`
- **Correctif** : validateur Pydantic qui refuse le démarrage si
  `app_env=="production"` et `secret_key` vaut encore la valeur par défaut.
- **Tests** : `tests/unit/test_settings.py` (+2 tests).

### 4. Timing side-channel sur `/auth/connexion` (énumération d'emails)
- **Fichiers** : `backend/core/security.py`, `backend/services/auth_service.py`
- **Cause** : `verifier_mot_de_passe` n'était jamais appelée pour un email
  inexistant (court-circuit du `or`), rendant la réponse quasi instantanée
  vs. ~260 000 itérations PBKDF2 pour un email existant.
- **Correctif** : hash factice de référence, vérification systématique.
- **Tests** : `tests/unit/test_auth_service.py` (nouveau fichier).

### 5. Email non normalisé (doublons de compte, échecs de connexion)
- **Fichier** : `backend/services/auth_service.py`
- **Cause** : la colonne `email` a une contrainte `unique=True` sensible à la
  casse ; sans normalisation, "Test@x.com" et "test@x.com" sont deux comptes
  distincts, et un utilisateur ne peut pas se reconnecter avec une casse
  différente de celle utilisée à l'inscription.
- **Correctif** : normalisation (`strip().lower()`) systématique.
- **Tests** : `tests/integration/test_router_auth.py` (+2 tests).

### 6. Métrique ChromaDB non explicite (L2 au lieu de cosinus)
- **Fichier** : `backend/rag/indexing.py`
- **Cause** : les embeddings sont normalisés (cosinus), mais la collection
  ChromaDB utilisait la métrique par défaut (L2) ; le classement restait
  correct par coïncidence mathématique, mais le score n'aurait pas été fiable
  si affiché ou seuillé.
- **Correctif** : `metadata={"hnsw:space": "cosine"}` explicite.

### 7. `capital_social` sans borne (négatif/nul accepté silencieusement)
- **Fichiers** : `backend/schemas/dossier.py`
- **Correctif** : `Field(gt=0)`.
- **Tests** : `tests/integration/test_router_dossier.py` (+1 test).

### 8. Migrations non exécutées automatiquement au démarrage Docker
- **Fichier** : `backend/Dockerfile`
- **Cause** : `docker compose up` seul laissait la base Postgres vide (aucune
  migration Alembic exécutée), en contradiction avec l'exigence de
  reproductibilité (`git clone` + `docker compose up`).
- **Correctif** : `CMD` modifié pour exécuter `alembic upgrade head` avant de
  lancer `uvicorn`.
- **Validation** : logique vérifiée (lecture de `DATABASE_URL` depuis
  `Settings`, cohérente avec la configuration `docker-compose.yml`) ; non
  exécutée de bout en bout faute de Postgres/Docker dans ce sandbox (limite
  déjà documentée par le projet pour les dépendances lourdes).

### 9. Interaction frontend/backend sur `capital_social`
- **Fichier** : `frontend/pages/3_Evaluation_Dossier.py`
- **Cause** : le formulaire Streamlit autorisait `capital_social = 0`
  (incompatible avec le correctif n°7) et n'affichait pas le détail des
  erreurs 422 (contrairement à la page OCR).
- **Correctif** : `min_value=1.0` + affichage du détail de validation sur 422.

## Point de sécurité important signalé, non corrigé automatiquement

**`POST /auth/inscription` permet à tout visiteur anonyme de s'auto-inscrire
avec le rôle `admin` ou `juriste`**, sans restriction ni validation. Ce
comportement est actuellement **testé et attendu** par la suite e2e
(`tests/e2e/test_parcours_complet.py`), qui inscrit délibérément un « juriste »
via cet endpoint public — ce n'est donc pas un oubli isolé mais un choix
d'architecture simplifié, documenté comme tel (PROJECT.md §5.4 : « pas un
flux OAuth2 complet »).

Le corriger proprement nécessite une décision produit (invitation, validation
par un admin existant, endpoint d'élévation de rôle séparé), pas un simple
bug fix — le changement casserait le contrat API actuel et le test e2e qui le
valide explicitement. **C'est le point à trancher en priorité avant tout
usage réel au-delà d'une démonstration académique.**

## Modules audités sans anomalie trouvée
Validation OCR, système expert (règles + agrégation de verdict), BM25
lexical, fusion RRF, reranking, service RAG, génération Groq, repository
utilisateur, chunking/chunk_store RAG, migration Alembic (logique), routeurs
`/dossier`, `/chat`, `/regles`, pages Streamlit OCR/chatbot/catalogue de
règles, `.env.example`/`.gitignore`.

## Suite de tests finale
100/100 tests passés (89 initiaux + 11 nouveaux), couverture qualité
(black/isort/flake8/mypy) intégralement propre.
