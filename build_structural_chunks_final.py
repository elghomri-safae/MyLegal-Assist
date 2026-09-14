"""
Chunking structurel hybride pour corpus PDF juridique.
========================================================

Usage depuis le dossier "stage" :
    python build_structural_chunks_final.py

Le script :
- lit directement les PDF du dossier ./pdfs (aucune dépendance à un output généré précédemment) ;
- extrait le texte page par page avec PyMuPDF, puis reconstruit le texte COMPLET de chaque document ;
- détecte les frontières d'articles ;
- utilise l'article comme unité atomique de découpage ;
- pour les documents sans articles (guides), chunking paragraphe-aware ;
- produit un fichier output6_structural_final/corpus_chunks.json.
"""

from __future__ import annotations

import json
import re
import statistics
from pathlib import Path
from typing import Any
from collections import defaultdict

try:
    import fitz  # PyMuPDF
except ImportError:
    print("PyMuPDF n'est pas installé.")
    print("Lance : python -m pip install pymupdf")
    raise SystemExit(1)

# ============================================================
# CONFIGURATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parent
PDF_DIR = BASE_DIR / "pdfs"

OUTPUT_DIR = BASE_DIR / "output6_structural_final"

# Paramètres validés par les tests : meilleur compromis
MAX_ARTICLE_SIZE = 1400      # Taille maximale d'un article avant sous-découpage
SUBSPLIT_OVERLAP = 200       # Chevauchement entre chunks

ARTICLE_RE = re.compile(
    r"(?im)^\s*(Article\s+(?:premier|première|\d+(?:-\d+)?(?:\s*(?:bis|ter|quater))?))\s*[:.\-]?"
)
SECTION_RE = re.compile(
    r"(?im)^\s*((?:Livre|Titre|Chapitre|Section|Sous[- ]titre|Partie)\b[^\n]*)"
)
TOC_TAIL_RE = re.compile(r"(?i)tables?\s+des\s+mati[eè]res")

# ============================================================
# EXTRACTION PDF
# ============================================================

def clean_text(text: str) -> str:
    """nettoyage leger sans destruction de la structure juridique."""
    if not text:
        return ""
    # Coupure de mot en fin de ligne 
    text = re.sub(r"(?<=\w)-\s*\n\s*(?=\w)", "", text)
    # Normalisation des espaces horizontaux
    text = re.sub(r"[ \t]+", " ", text)
    # Normalisation des retours à la ligne
    text = re.sub(r"\r\n?", "\n", text)
    # Évite les lignes vides excessives.
    text = re.sub(r"\n{3,}", "\n\n", text)
    # Supprime les espaces en début/fin de ligne
    text = "\n".join(line.strip() for line in text.splitlines())
    return text.strip()


def extract_document(pdf_path: Path) -> dict[str, Any]:
    """
    Extrait le texte complet d'un PDF, page par page, puis recolle les
    pages bout à bout pour obtenir un texte continu.
    """
    full_text = ""
    page_offsets: list[tuple[int, int]] = []

    with fitz.open(pdf_path) as doc:
        for page_number, page in enumerate(doc, start=1):
            raw = page.get_text("text")
            text = clean_text(raw)

            if not text:
                continue

            page_offsets.append((len(full_text), page_number))
            if full_text:
                full_text += "\n\n"
            full_text += text

    return {"text": full_text, "page_offsets": page_offsets}


def page_at_offset(page_offsets: list[tuple[int, int]], offset: int) -> int:
    page = page_offsets[0][1] if page_offsets else 1
    for start, p in page_offsets:
        if start <= offset:
            page = p
        else:
            break
    return page


def source_type(filename: str) -> str:
    """Classification informative, sans système de niveaux."""
    name = filename.lower()

    if "loi" in name or "code" in name:
        return "texte_legal"

    if "ompic" in name or "création et vie" in name:
        return "guide_institutionnel"

    if "cnss" in name or "damancom" in name:
        return "guide_administratif"

    if "tp" in name or "taxe" in name:
        return "document_fiscal"

    return "document_pdf"


def is_plausible_article_number(label: str) -> bool:
    """Filtre les faux positifs (notes de bas de page collées)."""
    m = re.search(r"\d+", label)
    if not m:
        return True
    return int(m.group()) <= 700


def slugify_article(label: str) -> str:
    """'Article premier' -> 'premier' ; 'Article 6' -> '6'."""
    s = re.sub(r"(?i)^article\s+", "", label.strip())
    return s.lower().replace(" ", "")


def section_before(text: str, offset: int) -> str | None:
    best = None
    for m in SECTION_RE.finditer(text, 0, offset):
        best = m
    if best:
        return re.sub(r"\s+", " ", best.group(1)).strip()
    return None

# ============================================================
# CHUNKING PARAGRAPHE-AWARE
# ============================================================

def split_into_units(text: str) -> list[str]:
    blocks = re.split(r"\n\s*\n+", text)
    return [b.strip() for b in blocks if b.strip()]


def hard_split(text: str, max_size: int) -> list[str]:
    pieces = []
    remaining = text.strip()

    while len(remaining) > max_size:
        window = remaining[:max_size]

        candidates = [
            window.rfind(". "),
            window.rfind(": "),
            window.rfind("; "),
            window.rfind(", "),
            window.rfind(" "),
        ]

        cut = max(candidates)

        if cut < int(max_size * 0.55):
            cut = max_size

        piece = remaining[:cut].strip()
        remaining = remaining[cut:].strip()

        if piece:
            pieces.append(piece)

    if remaining:
        pieces.append(remaining)

    return pieces


def prepare_units(text: str, max_size: int) -> list[str]:
    units = []

    for block in split_into_units(text):
        if len(block) <= max_size:
            units.append(block)
        else:
            units.extend(hard_split(block, max_size))

    return units


def paragraph_aware_chunks(text: str, chunk_size: int, overlap: int) -> list[str]:
    units = prepare_units(text, chunk_size)

    chunks: list[str] = []
    current: list[str] = []
    current_len = 0

    for unit in units:
        proposed_len = current_len + (2 if current else 0) + len(unit)

        if current and proposed_len > chunk_size:
            chunks.append("\n\n".join(current).strip())

            overlap_parts: list[str] = []
            overlap_len = 0
            for previous in reversed(current):
                addition = len(previous) + (2 if overlap_parts else 0)
                if overlap_len + addition > overlap:
                    break
                overlap_parts.insert(0, previous)
                overlap_len += addition

            current = overlap_parts[:]
            current_len = len("\n\n".join(current))

        current.append(unit)
        current_len = len("\n\n".join(current))

    if current:
        chunks.append("\n\n".join(current).strip())

    return [c for c in chunks if c]

# ============================================================
# CHUNKING STRUCTUREL HYBRIDE (article-first)
# ============================================================

def build_structural_chunks_for_doc(
    fn: str,
    full_text: str,
    page_offsets: list[tuple[int, int]],
) -> list[dict[str, Any]]:
    """
    Génère des chunk_id STABLES et DETERMINISTES.
    """
    matches = [
        m for m in ARTICLE_RE.finditer(full_text)
        if is_plausible_article_number(re.sub(r"\s+", " ", m.group(1)).strip())
    ]

    items: list[dict[str, Any]] = []
    src_type = source_type(fn)
    stem = Path(fn).stem
    frag_counter = [0]

    def emit(chunk_id: str, text: str, page: int, article: str | None, section: str | None):
        items.append({
            "chunk_id": chunk_id,
            "text": text,
            "metadata": {
                "filename": fn,
                "page": page,
                "type_source": src_type,
                "article": article,
                "section": section,
            },
        })

    def emit_fragment(text: str, offset: int):
        frag_counter[0] += 1
        page = page_at_offset(page_offsets, offset)
        section = section_before(full_text, offset)
        chunk_id = f"{stem}__p{page}__frag{frag_counter[0]}"
        emit(chunk_id, text, page, None, section)

    # Détection de la table des matières en fin de document
    toc_tail_match = None
    if matches:
        for tm in TOC_TAIL_RE.finditer(full_text):
            if tm.start() > matches[-1].start():
                toc_tail_match = tm
                break
    doc_end = toc_tail_match.start() if toc_tail_match else len(full_text)

    # Documents sans articles (guides, doc fiscal)
    if not matches:
        for piece in paragraph_aware_chunks(full_text, MAX_ARTICLE_SIZE, SUBSPLIT_OVERLAP):
            offset = max(full_text.find(piece[:60]), 0)
            emit_fragment(piece, offset)
        return items

    # Préambule avant le premier article
    preamble = full_text[: matches[0].start()].strip()
    if preamble:
        for piece in paragraph_aware_chunks(preamble, MAX_ARTICLE_SIZE, SUBSPLIT_OVERLAP):
            offset = max(full_text.find(piece[:60]), 0)
            emit_fragment(piece, offset)

    # Chaque article = une unité de découpage
    for i, m in enumerate(matches):
        start = m.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else doc_end
        article_text = full_text[start:end].strip()
        label = re.sub(r"\s+", " ", m.group(1)).strip()
        slug = slugify_article(label)
        page = page_at_offset(page_offsets, start)
        section = section_before(full_text, start)

        if len(article_text) <= MAX_ARTICLE_SIZE:
            chunk_id = f"{stem}__p{page}__art{slug}"
            emit(chunk_id, article_text, page, label, section)
        else:
            sub_pieces = paragraph_aware_chunks(article_text, MAX_ARTICLE_SIZE, SUBSPLIT_OVERLAP)
            for part_i, sub in enumerate(sub_pieces, start=1):
                sub_offset_local = max(article_text.find(sub[:60]), 0)
                sub_page = page_at_offset(page_offsets, start + sub_offset_local)
                chunk_id = f"{stem}__p{page}__art{slug}__part{part_i}"
                emit(chunk_id, sub, sub_page, label, section)

    return items

# ============================================================
# MÉTRIQUES
# ============================================================

def starts_mid_word(text: str) -> bool:
    return bool(text) and bool(re.match(r"^[a-zà-ÿ]", text)) and not re.match(
        r"^(Article|Livre|Titre|Chapitre|Section|Sous[- ]titre)\b",
        text,
        flags=re.I,
    )


def ends_mid_word(text: str) -> bool:
    if not text:
        return False
    return bool(re.search(r"[A-Za-zÀ-ÿ]$", text)) and not bool(
        re.search(r"[.!?:;,)»\]\"']$", text)
    )


def article_splits_in_chunk(chunks_text: list[str]) -> int:
    count = 0
    for t in chunks_text:
        matches = ARTICLE_RE.findall(t)
        if len(matches) > 1:
            count += len(matches) - 1
    return count


def article_completeness(chunks: list[dict[str, Any]]) -> dict[str, Any]:
    by_article: dict[tuple[str, str], int] = defaultdict(int)
    for c in chunks:
        art = c["metadata"].get("article")
        if art:
            by_article[(c["metadata"]["filename"], art)] += 1

    total = len(by_article)
    split = sum(1 for v in by_article.values() if v > 1)
    intact = total - split

    return {
        "articles_distincts": total,
        "articles_intacts": intact,
        "articles_sous_decoupes": split,
        "taux_intact_pct": round(intact / total * 100, 1) if total else None,
    }


def calculate_metrics(chunks: list[dict[str, Any]], pages_with_text: int) -> dict[str, Any]:
    lengths = [len(c["text"]) for c in chunks]

    metrics = {
        "chunks": len(chunks),
        "pages_with_text": pages_with_text,
        "min_chars": min(lengths) if lengths else 0,
        "max_chars": max(lengths) if lengths else 0,
        "mean_chars": round(statistics.mean(lengths), 2) if lengths else 0,
        "median_chars": round(statistics.median(lengths), 2) if lengths else 0,
        "chunks_starts_suspect": sum(starts_mid_word(c["text"]) for c in chunks),
        "chunks_ends_suspect": sum(ends_mid_word(c["text"]) for c in chunks),
        "chunks_multi_articles": article_splits_in_chunk([c["text"] for c in chunks]),
        "chunks_too_short_under_50": sum(1 for l in lengths if l < 50),
    }
    metrics.update(article_completeness(chunks))
    return metrics

# ============================================================
# TRAITEMENT DU CORPUS
# ============================================================

def build_corpus() -> dict[str, Any]:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    pdfs = sorted(PDF_DIR.glob("*.pdf"))
    if not pdfs:
        raise FileNotFoundError(f"Aucun PDF trouvé dans : {PDF_DIR}")

    print(f"PDF trouvés : {len(pdfs)}")

    all_chunks: list[dict[str, Any]] = []
    document_stats = []
    total_pages = 0

    for pdf_path in pdfs:
        doc = extract_document(pdf_path)
        total_pages += len(doc["page_offsets"])

        doc_chunks = build_structural_chunks_for_doc(
            pdf_path.name, doc["text"], doc["page_offsets"]
        )
        all_chunks.extend(doc_chunks)

        document_stats.append({
            "filename": pdf_path.name,
            "pages_with_text": len(doc["page_offsets"]),
            "chunks": len(doc_chunks),
        })

        print(f"{pdf_path.name}\n  Pages texte : {len(doc['page_offsets'])}\n  Chunks      : {len(doc_chunks)}")

    metrics = calculate_metrics(all_chunks, total_pages)

    result = {
        "metadata": {
            "nombre_documents": len(pdfs),
            "nombre_chunks": len(all_chunks),
            "max_article_size": MAX_ARTICLE_SIZE,
            "subsplit_overlap": SUBSPLIT_OVERLAP,
        },
        "documents": document_stats,
        "metrics": metrics,
        "chunks": all_chunks,
    }

    out_json = OUTPUT_DIR / "corpus_chunks.json"
    with out_json.open("w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    metrics_path = BASE_DIR / "metrics_structural.json"
    with metrics_path.open("w", encoding="utf-8") as f:
        json.dump(metrics, f, ensure_ascii=False, indent=2)

    print("\nMétriques :", json.dumps(metrics, ensure_ascii=False, indent=2))
    print("\nFichiers écrits :")
    print(" -", out_json)
    print(" -", metrics_path)

    return result

# ============================================================
# MAIN
# ============================================================

def main() -> None:
    print("CHUNKING STRUCTUREL HYBRIDE DU CORPUS PDF")
    print(f"Dossier du script : {BASE_DIR}")
    print(f"Dossier PDF       : {PDF_DIR}")

    if not PDF_DIR.exists():
        print(f"\nERREUR : dossier introuvable : {PDF_DIR}")
        print("Crée un dossier 'pdfs' à côté du script et mets-y les PDF.")
        raise SystemExit(1)

    result = build_corpus()

    print("\nTERMINE.")
    print(f"Résultats dans : {OUTPUT_DIR / 'corpus_chunks.json'}")

if __name__ == "__main__":
    main()