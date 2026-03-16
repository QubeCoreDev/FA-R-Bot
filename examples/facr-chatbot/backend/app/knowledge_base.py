"""
RAG knowledge base built from FAČR markdown documents.

Loads markdown files, splits them into heading-based chunks with overlap,
embeds each chunk with OpenAI, and exposes cosine-similarity search
plus structured browsing (TOC, sequential reading, neighbor context).
"""

from __future__ import annotations

import hashlib
import logging
import re
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
from openai import OpenAI

logger = logging.getLogger(__name__)

EMBEDDING_MODEL = "text-embedding-3-small"
EMBEDDING_DIMENSIONS = 1536
MAX_CHUNK_TOKENS_ESTIMATE = 600
OVERLAP_PARAGRAPHS = 2
CACHE_DIR = Path(__file__).resolve().parent.parent / ".embedding_cache"

DOCUMENT_LABELS: dict[str, str] = {
    "stanovy": "Stanovy FAČR",
    "sr-od": "Soutěžní řád FAČR",
    "disciplinarni-rad": "Disciplinární řád FAČR",
    "prestupni-rad": "Přestupní řád FAČR",
    "registracni-rad": "Registrační řád FAČR",
    "procesni-rad": "Procesní řád FAČR",
    "rad-agentu": "Řád agentů FAČR",
    "rad-treneru": "Řád trenérů FAČR",
    "rad-rozhodcich": "Řád rozhodčích a delegátů FAČR",
    "licencni-rad": "Licenční řád talentované mládeže FAČR",
    "zasady": "Zásady FAČR pro ochranu dětí",
    "vykladove": "Výkladové stanovisko – Řád agentů",
    "narizeni": "Nařízení Komise pro činnost agentů",
    "sazebnik": "Sazebník odměn rozhodčích a delegátů",
    "vzor-ligove": "Vzor ligové profesionální smlouvy",
    "vzor-standardni": "Vzor standardní profesionální smlouvy",
    "draft-standard": "Draft Standard Professional Contract",
    "priloha-radu": "Příloha řádu rozhodčích – sazebník odměn",
}


@dataclass
class DocumentChunk:
    chunk_id: int
    doc_filename: str
    doc_label: str
    heading_path: list[str]
    heading_level: int
    text: str
    char_offset: int = 0


@dataclass
class DocumentTOCEntry:
    chunk_id: int
    level: int
    heading: str
    preview: str


@dataclass
class DocumentInfo:
    filename: str
    label: str
    chunk_start: int
    chunk_end: int
    toc: list[DocumentTOCEntry]


@dataclass
class SearchResult:
    chunk: DocumentChunk
    score: float


@dataclass
class KnowledgeBase:
    chunks: list[DocumentChunk] = field(default_factory=list)
    documents: list[DocumentInfo] = field(default_factory=list)
    embeddings: np.ndarray | None = None
    _client: OpenAI | None = None

    @property
    def client(self) -> OpenAI:
        if self._client is None:
            self._client = OpenAI()
        return self._client

    @property
    def document_names(self) -> list[dict[str, str]]:
        return [{"filename": d.filename, "label": d.label} for d in self.documents]

    def doc_by_keyword(self, keyword: str) -> DocumentInfo | None:
        kw = keyword.lower()
        for doc in self.documents:
            if kw in doc.label.lower() or kw in doc.filename.lower():
                return doc
        return None


def _label_for_file(filename: str) -> str:
    lower = filename.lower()
    for key, label in DOCUMENT_LABELS.items():
        if key in lower:
            return label
    stem = Path(filename).stem.replace("-", " ").replace("_", " ")
    return stem.title()


_HEADING_RE = re.compile(r"^(#{1,4})\s+(.*)", re.MULTILINE)


def _split_by_headings(
    text: str, filename: str, label: str, id_offset: int
) -> tuple[list[DocumentChunk], list[DocumentTOCEntry]]:
    """Split markdown into chunks at heading boundaries with paragraph overlap."""
    headings: list[tuple[int, int, str]] = []
    for m in _HEADING_RE.finditer(text):
        level = len(m.group(1))
        title = m.group(2).strip()
        headings.append((m.start(), level, title))

    if not headings:
        chunks = _force_split_chunk(text.strip(), filename, label, [label], 0, id_offset, 0)
        toc = [DocumentTOCEntry(
            chunk_id=id_offset, level=0, heading=label,
            preview=text.strip()[:120].replace("\n", " "),
        )]
        return chunks, toc

    raw_sections: list[tuple[int, str, list[str], int]] = []
    heading_stack: list[str] = []

    if headings[0][0] > 0:
        preamble = text[: headings[0][0]].strip()
        if preamble:
            raw_sections.append((0, preamble, [label, "Úvod"], 0))

    for i, (start, level, title) in enumerate(headings):
        end = headings[i + 1][0] if i + 1 < len(headings) else len(text)
        body = text[start:end].strip()
        if not body:
            continue
        while len(heading_stack) >= level:
            heading_stack.pop()
        heading_stack.append(title)
        raw_sections.append((start, body, list(heading_stack), level))

    all_chunks: list[DocumentChunk] = []
    toc: list[DocumentTOCEntry] = []
    current_id = id_offset

    for sec_idx, (offset, body, hpath, hlevel) in enumerate(raw_sections):
        overlap_prefix = ""
        if OVERLAP_PARAGRAPHS > 0 and sec_idx > 0:
            prev_paragraphs = raw_sections[sec_idx - 1][1].split("\n\n")
            tail = prev_paragraphs[-OVERLAP_PARAGRAPHS:]
            overlap_prefix = "\n\n".join(tail).strip()
            if overlap_prefix:
                overlap_prefix = f"[…kontextu z předchozí sekce:]\n{overlap_prefix}\n\n---\n\n"

        full_text = overlap_prefix + body
        sub_chunks = _force_split_chunk(
            full_text, filename, label, hpath, offset, current_id, hlevel
        )

        first_chunk_id = current_id
        preview = body[:150].replace("\n", " ").strip()
        heading_display = hpath[-1] if hpath else label
        toc.append(DocumentTOCEntry(
            chunk_id=first_chunk_id, level=hlevel,
            heading=heading_display, preview=preview,
        ))

        all_chunks.extend(sub_chunks)
        current_id += len(sub_chunks)

    return all_chunks, toc


def _force_split_chunk(
    text: str,
    filename: str,
    label: str,
    heading_path: list[str],
    offset: int,
    start_id: int,
    hlevel: int,
) -> list[DocumentChunk]:
    if _estimate_tokens(text) <= MAX_CHUNK_TOKENS_ESTIMATE:
        return [DocumentChunk(
            chunk_id=start_id,
            doc_filename=filename,
            doc_label=label,
            heading_path=heading_path,
            heading_level=hlevel,
            text=text,
            char_offset=offset,
        )]

    parts = _split_long_text(text, MAX_CHUNK_TOKENS_ESTIMATE)
    chunks: list[DocumentChunk] = []
    for j, part in enumerate(parts):
        suffix = [f"(část {j+1}/{len(parts)})"] if len(parts) > 1 else []
        chunks.append(DocumentChunk(
            chunk_id=start_id + j,
            doc_filename=filename,
            doc_label=label,
            heading_path=heading_path + suffix,
            heading_level=hlevel,
            text=part,
            char_offset=offset,
        ))
    return chunks


def _estimate_tokens(text: str) -> int:
    return len(text) // 3


def _split_long_text(text: str, max_tokens: int) -> list[str]:
    max_chars = max_tokens * 3
    paragraphs = text.split("\n\n")
    parts: list[str] = []
    current: list[str] = []
    current_len = 0

    for para in paragraphs:
        para_len = len(para)
        if current_len + para_len > max_chars and current:
            parts.append("\n\n".join(current))
            current = [para]
            current_len = para_len
        else:
            current.append(para)
            current_len += para_len

    if current:
        parts.append("\n\n".join(current))
    return parts or [text]


def _content_hash(chunks: list[DocumentChunk]) -> str:
    hasher = hashlib.sha256()
    for c in chunks:
        hasher.update(c.text.encode("utf-8"))
    return hasher.hexdigest()[:16]


def _load_cached_embeddings(cache_key: str, expected_count: int) -> np.ndarray | None:
    cache_file = CACHE_DIR / f"{cache_key}.npy"
    if not cache_file.exists():
        return None
    try:
        arr = np.load(str(cache_file))
        if arr.shape[0] == expected_count:
            logger.info("Loaded cached embeddings from %s", cache_file)
            return arr
    except Exception:
        pass
    return None


def _save_cached_embeddings(cache_key: str, embeddings: np.ndarray) -> None:
    try:
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        np.save(str(CACHE_DIR / f"{cache_key}.npy"), embeddings)
        logger.info("Saved embedding cache (%d vectors)", embeddings.shape[0])
    except Exception as exc:
        logger.warning("Could not write embedding cache: %s", exc)


def load_documents(docs_dir: str | Path) -> tuple[list[DocumentChunk], list[DocumentInfo]]:
    """Recursively load all .md files, split into chunks, build TOCs."""
    docs_path = Path(docs_dir)
    if not docs_path.exists():
        logger.error("Documents directory does not exist: %s", docs_path)
        return [], []

    md_files = sorted(docs_path.rglob("*.md"))
    logger.info("Found %d markdown files in %s", len(md_files), docs_path)

    all_chunks: list[DocumentChunk] = []
    all_docs: list[DocumentInfo] = []
    global_id = 0

    for md_file in md_files:
        text = md_file.read_text(encoding="utf-8")
        label = _label_for_file(md_file.name)
        chunk_start = global_id
        chunks, toc = _split_by_headings(text, md_file.name, label, global_id)
        all_chunks.extend(chunks)
        global_id += len(chunks)
        all_docs.append(DocumentInfo(
            filename=md_file.name, label=label,
            chunk_start=chunk_start, chunk_end=global_id - 1,
            toc=toc,
        ))
        logger.info("  %s → %d chunks, %d TOC entries", md_file.name, len(chunks), len(toc))

    logger.info("Total chunks: %d across %d documents", len(all_chunks), len(all_docs))
    return all_chunks, all_docs


def build_knowledge_base(docs_dir: str | Path) -> KnowledgeBase:
    """Load documents, create embeddings, return a ready KnowledgeBase."""
    chunks, docs = load_documents(docs_dir)
    if not chunks:
        logger.warning("No document chunks loaded — knowledge base will be empty")
        return KnowledgeBase(chunks=[], documents=docs, embeddings=np.zeros((0, EMBEDDING_DIMENSIONS)))

    kb = KnowledgeBase(chunks=chunks, documents=docs)

    cache_key = _content_hash(chunks)
    cached = _load_cached_embeddings(cache_key, len(chunks))
    if cached is not None:
        kb.embeddings = cached
        return kb

    logger.info("Creating embeddings for %d chunks (model=%s)…", len(chunks), EMBEDDING_MODEL)
    texts = [_chunk_embed_text(c) for c in chunks]

    batch_size = 100
    all_embeddings: list[list[float]] = []
    for i in range(0, len(texts), batch_size):
        batch = texts[i : i + batch_size]
        response = kb.client.embeddings.create(model=EMBEDDING_MODEL, input=batch)
        all_embeddings.extend([d.embedding for d in response.data])

    kb.embeddings = np.array(all_embeddings, dtype=np.float32)
    _save_cached_embeddings(cache_key, kb.embeddings)
    logger.info("Knowledge base ready (%d chunks, %s embeddings)", len(chunks), kb.embeddings.shape)
    return kb


def _chunk_embed_text(chunk: DocumentChunk) -> str:
    heading_ctx = " > ".join(chunk.heading_path)
    return f"[{chunk.doc_label}] {heading_ctx}\n\n{chunk.text[:3000]}"


# ---------------------------------------------------------------------------
# Search & retrieval functions
# ---------------------------------------------------------------------------

def search(kb: KnowledgeBase, query: str, top_k: int = 8) -> list[SearchResult]:
    """Return the *top_k* most relevant chunks for *query*."""
    if kb.embeddings is None or len(kb.chunks) == 0:
        return []

    response = kb.client.embeddings.create(model=EMBEDDING_MODEL, input=[query])
    q_vec = np.array(response.data[0].embedding, dtype=np.float32)

    norms = np.linalg.norm(kb.embeddings, axis=1)
    q_norm = np.linalg.norm(q_vec)
    similarities = (kb.embeddings @ q_vec) / (norms * q_norm + 1e-10)

    top_indices = np.argsort(similarities)[::-1][:top_k]
    return [
        SearchResult(chunk=kb.chunks[idx], score=float(similarities[idx]))
        for idx in top_indices
    ]


def search_multi(kb: KnowledgeBase, queries: list[str], top_k: int = 8) -> list[SearchResult]:
    """Search with multiple queries, deduplicate and rank by best score."""
    if kb.embeddings is None or len(kb.chunks) == 0:
        return []

    response = kb.client.embeddings.create(model=EMBEDDING_MODEL, input=queries)
    q_vecs = np.array([d.embedding for d in response.data], dtype=np.float32)

    norms = np.linalg.norm(kb.embeddings, axis=1)

    best_score: dict[int, float] = {}
    for q_vec in q_vecs:
        q_norm = np.linalg.norm(q_vec)
        sims = (kb.embeddings @ q_vec) / (norms * q_norm + 1e-10)
        for idx in np.argsort(sims)[::-1][:top_k]:
            score = float(sims[idx])
            if idx not in best_score or score > best_score[idx]:
                best_score[idx] = score

    ranked = sorted(best_score.items(), key=lambda x: x[1], reverse=True)[:top_k]
    return [SearchResult(chunk=kb.chunks[idx], score=score) for idx, score in ranked]


def read_chunk(kb: KnowledgeBase, chunk_id: int) -> DocumentChunk | None:
    """Read a specific chunk by its global ID."""
    if 0 <= chunk_id < len(kb.chunks):
        return kb.chunks[chunk_id]
    return None


def read_chunk_with_neighbors(
    kb: KnowledgeBase, chunk_id: int, before: int = 1, after: int = 1
) -> list[DocumentChunk]:
    """Read a chunk plus its neighbors within the same document."""
    if chunk_id < 0 or chunk_id >= len(kb.chunks):
        return []

    target = kb.chunks[chunk_id]
    doc_info = None
    for d in kb.documents:
        if d.filename == target.doc_filename:
            doc_info = d
            break

    if doc_info is None:
        return [target]

    start = max(doc_info.chunk_start, chunk_id - before)
    end = min(doc_info.chunk_end, chunk_id + after)
    return kb.chunks[start : end + 1]


def get_document_toc(kb: KnowledgeBase, doc_keyword: str) -> DocumentInfo | None:
    """Find a document by keyword and return its info with TOC."""
    return kb.doc_by_keyword(doc_keyword)


def get_document_section(
    kb: KnowledgeBase, doc_keyword: str, section_keyword: str
) -> list[DocumentChunk]:
    """Find chunks whose document label and heading path match the keywords."""
    doc_kw = doc_keyword.lower()
    sec_kw = section_keyword.lower()
    matches: list[DocumentChunk] = []
    for chunk in kb.chunks:
        label_match = doc_kw in chunk.doc_label.lower() or doc_kw in chunk.doc_filename.lower()
        heading_text = " ".join(chunk.heading_path).lower()
        section_match = sec_kw in heading_text or sec_kw in chunk.text[:300].lower()
        if label_match and section_match:
            matches.append(chunk)
    return matches[:12]


# ---------------------------------------------------------------------------
# Formatting helpers
# ---------------------------------------------------------------------------

def format_search_results(results: list[SearchResult]) -> str:
    if not results:
        return "Nebyly nalezeny žádné relevantní informace."

    parts: list[str] = []
    for i, r in enumerate(results, 1):
        heading = " > ".join(r.chunk.heading_path)
        parts.append(
            f"--- Výsledek {i} (relevance: {r.score:.2f}, chunk_id: {r.chunk.chunk_id}) ---\n"
            f"Dokument: {r.chunk.doc_label}\n"
            f"Sekce: {heading}\n\n"
            f"{r.chunk.text}\n"
        )
    return "\n".join(parts)


def format_chunk(chunk: DocumentChunk) -> str:
    heading = " > ".join(chunk.heading_path)
    return (
        f"[chunk_id: {chunk.chunk_id}] Dokument: {chunk.doc_label}\n"
        f"Sekce: {heading}\n\n"
        f"{chunk.text}"
    )


def format_chunks(chunks: list[DocumentChunk]) -> str:
    return "\n\n---\n\n".join(format_chunk(c) for c in chunks)


def format_toc(doc: DocumentInfo) -> str:
    lines = [f"# Obsah dokumentu: {doc.label}"]
    lines.append(f"  (chunk rozsah: {doc.chunk_start}–{doc.chunk_end})\n")
    for entry in doc.toc:
        indent = "  " * entry.level
        lines.append(
            f"{indent}• [{entry.chunk_id}] {entry.heading} — {entry.preview}"
        )
    return "\n".join(lines)


def format_document_list(kb: KnowledgeBase) -> str:
    lines = ["Dostupné dokumenty ve znalostní bázi:\n"]
    for i, d in enumerate(kb.documents, 1):
        lines.append(
            f"{i}. {d.label} ({d.filename}) — "
            f"{d.chunk_end - d.chunk_start + 1} sekcí, "
            f"chunk_id {d.chunk_start}–{d.chunk_end}"
        )
    return "\n".join(lines)
