# UML.md — Conception UML (Phase 1)

**Statut : Phase 1 — En attente de validation**
**Dépend de** : `PROJECT.md` (§5.1 Acteurs), `ARCHITECTURE.md` (§7), `DECISIONS.md`
(section « Décisions de Phase 1 »).

---

## 1. Besoins fonctionnels (BF)

| ID | Acteur(s) | Besoin |
|---|---|---|
| BF-01 | Entrepreneur | Poser une question juridique en langage naturel et recevoir une réponse citant systématiquement source, niveau (1/2/3) et référence précise. |
| BF-02 | Entrepreneur | Soumettre une image de CIN et obtenir nom, prénom, numéro CIN, date de naissance, normalisés et validés. |
| BF-03 | Entrepreneur | Saisir un dossier structuré (forme juridique, capital, pièces fournies, siège social, identités des associés) et le soumettre à évaluation. |
| BF-04 | Entrepreneur | Consulter le verdict de conformité de son dossier : liste des anomalies, gravité, message utilisateur, justification et référence documentaire pour chacune. |
| BF-05 | Juriste | Consulter le catalogue des règles du système expert (catégorie, condition, source, niveau). |
| BF-06 | Juriste | Consulter l'historique des évaluations de dossiers (audit / amélioration continue des règles). |
| BF-07 | Juriste | Proposer une évolution de règle avec justification documentaire (validation hors-ligne humaine avant intégration au code — Règle absolue n°1 et n°2). |
| BF-08 | Admin | Consulter l'état de santé du système (API, base de données, index vectoriel). |
| BF-09 | Admin | Consulter les journaux d'erreurs applicatifs. |
| BF-10 | Tous | Recevoir un signalement explicite lorsque le corpus documentaire ne permet pas de répondre (plutôt qu'une réponse inventée — Règle absolue n°8). |

## 2. Besoins non fonctionnels (BNF)

| ID | Besoin | Statut |
|---|---|---|
| NFR-01 | Traçabilité : toute réponse/verdict doit référencer une règle et une source documentaire précise. | Exigence du prompt (Règle absolue n°7) |
| NFR-02 | Corpus fermé : aucune information juridique hors des documents fournis. | Exigence du prompt (Règle absolue n°1) |
| NFR-03 | Reproductibilité : `git clone` + `docker compose up` ou `pip install -r requirements.txt`, sans modification manuelle, sans secret en dur. | Exigence du prompt |
| NFR-04 | Protection des données personnelles extraites par OCR (minimisation, pas de stockage de l'image brute). | **Proposition technique — non issue du corpus**, à valider (cf. DECISIONS.md) |
| NFR-05 | Temps de réponse cible du chatbot RAG (indicatif). | **Proposition technique — non issue du corpus**, à valider |
| NFR-06 | Testabilité : couverture pytest (unitaire + intégration) sur chaque module. | Exigence du prompt |
| NFR-07 | Maintenabilité : architecture SOLID, séparation API/Services/Repositories/Models. | Exigence du prompt |
| NFR-08 | Portabilité : exécution via Docker, environnement standard. | Exigence du prompt |
| NFR-09 | Disponibilité mono-utilisateur local en V1 (pas de haute disponibilité requise). | Proposition validée dans DECISIONS.md |

---

## 3. Diagramme de cas d'utilisation

> Mermaid ne dispose pas d'une notation UML "cas d'utilisation" native ; la
> représentation ci-dessous utilise un flowchart avec une frontière de système
> (`subgraph`) contenant les cas d'utilisation, et les acteurs à l'extérieur —
> convention usuelle pour ce type de diagramme en Markdown/Mermaid.

```mermaid
flowchart LR
    Entrepreneur([Entrepreneur])
    Juriste([Juriste])
    Admin([Admin])

    subgraph Systeme["Systeme d'accompagnement creation SARL"]
        UC1(("Poser une question juridique"))
        UC2(("Extraire donnees CIN (OCR)"))
        UC3(("Soumettre un dossier de creation"))
        UC4(("Consulter le verdict de conformite"))
        UC5(("Consulter le catalogue de regles"))
        UC6(("Proposer une evolution de regle"))
        UC7(("Consulter l'historique des evaluations"))
        UC8(("Superviser l'etat du systeme"))
        UC9(("Consulter les journaux d'erreurs"))
    end

    Entrepreneur --> UC1
    Entrepreneur --> UC2
    Entrepreneur --> UC3
    UC3 -.include.-> UC4
    Entrepreneur --> UC4

    Juriste --> UC5
    Juriste --> UC6
    Juriste --> UC7

    Admin --> UC8
    Admin --> UC9
    Admin --> UC7
```

**Relations notables** :
- `UC3 (Soumettre un dossier)` **include** `UC4 (Consulter le verdict)` : toute
  soumission produit systématiquement un verdict (aucune évaluation silencieuse).
- `UC7 (Consulter l'historique)` est partagé entre Juriste (amélioration des règles)
  et Admin (audit technique).

---

## 4. Diagramme de classes

```mermaid
classDiagram
    class Utilisateur {
        +UUID id
        +string nom
        +string email
        +RoleEnum role
    }

    class Dossier {
        +UUID id
        +UUID entrepreneur_id
        +string forme_juridique
        +decimal capital_social
        +string siege_social
        +datetime date_creation
        +StatutDossierEnum statut
    }

    class IdentitePersonne {
        +UUID id
        +UUID dossier_id
        +string nom
        +string prenom
        +string numero_cin
        +date date_naissance
        +SourceExtractionEnum source_extraction
    }

    class PieceJustificative {
        +UUID id
        +UUID dossier_id
        +string type_piece
        +string reference_fichier
        +bool fournie
    }

    class Regle {
        +string id
        +string categorie
        +string description
        +string condition
        +GraviteEnum gravite
        +string message_utilisateur
        +string justification
        +string reference_documentaire
        +int niveau_documentaire
    }

    class EvaluationDossier {
        +UUID id
        +UUID dossier_id
        +datetime date_evaluation
        +StatutGlobalEnum statut_global
    }

    class Anomalie {
        +UUID id
        +UUID evaluation_id
        +string regle_id
        +string message
        +GraviteEnum gravite
    }

    class Question {
        +UUID id
        +UUID utilisateur_id
        +string texte
        +datetime date
    }

    class Reponse {
        +UUID id
        +UUID question_id
        +string texte
    }

    class CitationSource {
        +UUID id
        +UUID reponse_id
        +string document
        +int niveau
        +string reference
    }

    class DocumentCorpus {
        +UUID id
        +string titre
        +int niveau
        +string type_source
    }

    class Chunk {
        +UUID id
        +UUID document_id
        +string texte
        +string embedding_ref
    }

    Utilisateur "1" --> "0..*" Dossier : cree
    Dossier "1" --> "1..*" IdentitePersonne : concerne
    Dossier "1" --> "1..*" PieceJustificative : comprend
    Dossier "1" --> "0..*" EvaluationDossier : historique
    EvaluationDossier "1" --> "0..*" Anomalie : contient
    Anomalie "1" --> "1" Regle : reference
    Utilisateur "1" --> "0..*" Question : pose
    Question "1" --> "1" Reponse : recoit
    Reponse "1" --> "1..*" CitationSource : cite
    DocumentCorpus "1" --> "0..*" Chunk : decoupe_en
```

**Note de conception** : `Regle` reste alignée sur la structure imposée par le prompt
(id, catégorie, description, condition, gravité, message_utilisateur, justification,
référence_documentaire, niveau_documentaire) — aucun champ ajouté ni retiré.

---

## 5. Diagrammes de séquence

### Scénario 1 — Question juridique au chatbot (module RAG)

```mermaid
sequenceDiagram
    actor E as Entrepreneur
    participant UI as Streamlit
    participant API as FastAPI (router chat)
    participant SVC as rag_service
    participant IDX as ChromaDB
    participant LLM as Groq API

    E->>UI: Saisit une question
    UI->>API: POST /chat {question}
    API->>SVC: traiter_question(question)
    SVC->>SVC: nettoyage + embedding de la question
    SVC->>IDX: recherche_similarite(embedding)
    IDX-->>SVC: chunks pertinents (+ metadata source/niveau)
    SVC->>SVC: reranking des chunks
    SVC->>LLM: generer_reponse(question, chunks_selectionnes)
    LLM-->>SVC: reponse brute
    SVC->>SVC: assembler reponse + citations (source, niveau, reference)
    SVC-->>API: reponse structuree
    API-->>UI: 200 OK {reponse, citations}
    UI-->>E: Affiche reponse avec citations
```

### Scénario 2 — Soumission d'un dossier au système expert anti-rejet

```mermaid
sequenceDiagram
    actor E as Entrepreneur
    participant UI as Streamlit
    participant API as FastAPI (router dossier)
    participant SVC as expert_service
    participant RULES as rules/*.py
    participant REPO as repositories

    E->>UI: Remplit le formulaire de dossier
    UI->>API: POST /dossier {donnees_dossier}
    API->>SVC: evaluer_dossier(donnees_dossier)
    SVC->>RULES: charger_regles_applicables(forme_juridique)
    RULES-->>SVC: liste de regles (capital, documents, identite, fiscalite, cnss)
    loop pour chaque regle
        SVC->>SVC: evaluer_condition(regle, donnees_dossier)
        alt condition non respectee
            SVC->>SVC: creer_anomalie(regle, gravite, justification)
        end
    end
    SVC->>REPO: persister(EvaluationDossier, Anomalies)
    REPO-->>SVC: confirmation
    SVC-->>API: verdict {statut_global, anomalies}
    API-->>UI: 200 OK {verdict}
    UI-->>E: Affiche le verdict avec justification par anomalie
```

### Scénario 3 — Extraction OCR d'une CIN

```mermaid
sequenceDiagram
    actor E as Entrepreneur
    participant UI as Streamlit
    participant API as FastAPI (router ocr)
    participant SVC as ocr_service
    participant CV as OpenCV
    participant OCR as EasyOCR

    E->>UI: Depose une image de CIN
    UI->>API: POST /ocr {image}
    API->>SVC: extraire_identite(image)
    SVC->>CV: pretraitement(image)
    CV-->>SVC: image_pretraitee
    SVC->>OCR: extraire_texte(image_pretraitee)
    OCR-->>SVC: texte_brut
    SVC->>SVC: normaliser_champs(texte_brut)
    SVC->>SVC: valider_format(champs)
    alt champs invalides
        SVC-->>API: erreur_validation {champs_manquants}
        API-->>UI: 422 {details}
    else champs valides
        SVC-->>API: IdentitePersonne {nom, prenom, cin, date_naissance}
        API-->>UI: 200 OK {identite}
    end
    UI-->>E: Affiche les champs extraits (a confirmer/corriger)
```

---

## 6. Modèle de données

```mermaid
erDiagram
    UTILISATEURS ||--o{ DOSSIERS : cree
    DOSSIERS ||--|{ IDENTITES_PERSONNES : concerne
    DOSSIERS ||--|{ PIECES_JUSTIFICATIVES : comprend
    DOSSIERS ||--o{ EVALUATIONS_DOSSIER : historique
    EVALUATIONS_DOSSIER ||--o{ ANOMALIES : contient
    ANOMALIES }o--|| REGLES : reference
    UTILISATEURS ||--o{ QUESTIONS : pose
    QUESTIONS ||--|| REPONSES : recoit
    REPONSES ||--|{ CITATIONS_SOURCES : cite
    DOCUMENTS_CORPUS ||--o{ CHUNKS : decoupe_en

    UTILISATEURS {
        uuid id PK
        string nom
        string email
        string role
    }
    DOSSIERS {
        uuid id PK
        uuid entrepreneur_id FK
        string forme_juridique
        numeric capital_social
        string siege_social
        timestamp date_creation
        string statut
    }
    IDENTITES_PERSONNES {
        uuid id PK
        uuid dossier_id FK
        string nom
        string prenom
        string numero_cin
        date date_naissance
        string source_extraction
    }
    PIECES_JUSTIFICATIVES {
        uuid id PK
        uuid dossier_id FK
        string type_piece
        string reference_fichier
        bool fournie
    }
    REGLES {
        string id PK
        string categorie
        string description
        string condition_texte
        string gravite
        string message_utilisateur
        string justification
        string reference_documentaire
        int niveau_documentaire
    }
    EVALUATIONS_DOSSIER {
        uuid id PK
        uuid dossier_id FK
        timestamp date_evaluation
        string statut_global
    }
    ANOMALIES {
        uuid id PK
        uuid evaluation_id FK
        string regle_id FK
        string message
        string gravite
    }
    QUESTIONS {
        uuid id PK
        uuid utilisateur_id FK
        string texte
        timestamp date
    }
    REPONSES {
        uuid id PK
        uuid question_id FK
        string texte
    }
    CITATIONS_SOURCES {
        uuid id PK
        uuid reponse_id FK
        string document
        int niveau
        string reference
    }
    DOCUMENTS_CORPUS {
        uuid id PK
        string titre
        int niveau
        string type_source
    }
    CHUNKS {
        uuid id PK
        uuid document_id FK
        text texte
        string embedding_ref
    }
```

**Correspondance avec la stack imposée** : ce modèle logique sera implémenté en
`backend/models/*.py` (SQLAlchemy 2.x, tables `PostgreSQL`) et migré via Alembic en
Phase 2 (Fondations techniques). `CHUNKS.embedding_ref` référence un identifiant côté
`ChromaDB` (les vecteurs eux-mêmes ne sont pas dupliqués en PostgreSQL).

---

## 7. Information manquante signalée (Règle absolue n°8)

- Aucune donnée du corpus ne définit un modèle de rôles applicatifs, un modèle de
  données technique, ou des seuils de performance : tout le contenu de ce document
  au-delà des règles métier (capital, formes juridiques, documents) est une
  **proposition de conception**, pas une extraction du corpus documentaire.
- Les règles métier elles-mêmes (`Regle.condition`, `reference_documentaire`,
  `niveau_documentaire`) ne seront formalisées avec leur contenu réel qu'en Phase 3
  (Système expert) — ce document ne fait qu'en fixer la structure.
