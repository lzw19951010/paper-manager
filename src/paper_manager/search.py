"""ChromaDB-backed hybrid search (exact + semantic) over paper notes."""
from __future__ import annotations

import re
from pathlib import Path

import chromadb
import yaml
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction


def _get_embedding_function() -> SentenceTransformerEmbeddingFunction:
    """Return the shared embedding function (BAAI/bge-small-zh-v1.5)."""
    return SentenceTransformerEmbeddingFunction(model_name="BAAI/bge-small-zh-v1.5")


def get_collection(chromadb_dir: Path) -> chromadb.Collection:
    """Create or open a persistent ChromaDB collection for papers.

    Args:
        chromadb_dir: Directory where ChromaDB stores its data.

    Returns:
        A ChromaDB Collection named "papers_v2".
    """
    client = chromadb.PersistentClient(path=str(chromadb_dir))
    ef = _get_embedding_function()
    return client.get_or_create_collection("papers_v2", embedding_function=ef)


def parse_frontmatter(md_content: str) -> tuple[dict, str]:
    """Split Markdown into YAML frontmatter and body.

    Args:
        md_content: Raw markdown file content.

    Returns:
        Tuple of (frontmatter_dict, body_text).
        If no frontmatter block is present, returns ({}, md_content).
    """
    if not md_content.startswith("---"):
        return {}, md_content

    # Find closing ---
    rest = md_content[3:]
    end_idx = rest.find("\n---")
    if end_idx == -1:
        return {}, md_content

    yaml_block = rest[:end_idx]
    body = rest[end_idx + 4:].lstrip("\n")

    try:
        frontmatter = yaml.safe_load(yaml_block) or {}
        if not isinstance(frontmatter, dict):
            frontmatter = {}
    except yaml.YAMLError:
        frontmatter = {}

    return frontmatter, body


def chunk_document(body: str, max_chunk_chars: int = 2000) -> list[str]:
    """Split body text into chunks for indexing.

    Splits on ## section headers first. Sections exceeding max_chunk_chars
    are further split on paragraph boundaries (\\n\\n). If no ## headers
    are found, the whole body is split into paragraphs.

    Args:
        body: Plain text body of a markdown document.
        max_chunk_chars: Maximum characters per chunk before paragraph-splitting.

    Returns:
        List of non-empty text chunk strings.
    """
    # Split on ## headers
    parts = re.split(r"(?m)^(?=## )", body)

    # If only one part and it doesn't start with ##, no headers were found
    if len(parts) == 1 and not parts[0].startswith("## "):
        # No headers — split entire body into paragraphs
        paragraphs = [p.strip() for p in body.split("\n\n")]
        return [p for p in paragraphs if p]

    chunks: list[str] = []
    for part in parts:
        if not part.strip():
            continue

        if part.startswith("## "):
            # Reconstruct section text (already includes the ## header)
            section_text = part.rstrip()
            if len(section_text) <= max_chunk_chars:
                chunks.append(section_text)
            else:
                # Split oversized section into paragraphs
                paragraphs = [p.strip() for p in section_text.split("\n\n")]
                chunks.extend(p for p in paragraphs if p)
        else:
            # Content before any ## header
            stripped = part.strip()
            if stripped:
                if len(stripped) <= max_chunk_chars:
                    chunks.append(stripped)
                else:
                    paragraphs = [p.strip() for p in stripped.split("\n\n")]
                    chunks.extend(p for p in paragraphs if p)

    return chunks


def index_paper(md_path: Path, collection: chromadb.Collection) -> None:
    """Index a single paper markdown file into the ChromaDB collection.

    Reads the file, parses frontmatter, chunks the body, and upserts all
    chunks. Any existing chunks for this arxiv_id are deleted first to avoid
    stale entries on re-index.

    A dedicated metadata chunk (chunk_index -1) is also upserted containing
    title, arxiv_id, keywords, and tldr so exact-title searches can match it.

    Args:
        md_path: Path to the paper's .md file.
        collection: ChromaDB collection to index into.
    """
    content = md_path.read_text(encoding="utf-8")
    frontmatter, body = parse_frontmatter(content)

    arxiv_id: str = frontmatter.get("arxiv_id", "") or md_path.stem
    title: str = frontmatter.get("title", "") or ""
    tags_raw = frontmatter.get("tags", [])
    if isinstance(tags_raw, list):
        tags_str = ", ".join(str(t) for t in tags_raw)
    else:
        tags_str = str(tags_raw) if tags_raw else ""

    # Build metadata-header string for keyword searchability
    keywords_raw = frontmatter.get("keywords", [])
    if isinstance(keywords_raw, list):
        keywords_str = ", ".join(str(k) for k in keywords_raw)
    else:
        keywords_str = str(keywords_raw) if keywords_raw else ""
    tldr: str = frontmatter.get("tldr", "") or ""

    meta_text = f"Title: {title}\narxiv_id: {arxiv_id}\nKeywords: {keywords_str}\nTLDR: {tldr}"

    # Delete existing chunks for this paper to avoid stale data
    try:
        existing = collection.get(where={"arxiv_id": {"$eq": arxiv_id}})
        if existing and existing.get("ids"):
            collection.delete(ids=existing["ids"])
    except Exception:
        pass

    chunks = chunk_document(body)
    if not chunks:
        # Still upsert the metadata chunk even if body is empty
        chunks = []

    # Prepend metadata header to the first body chunk
    if chunks:
        chunks[0] = meta_text + "\n\n" + chunks[0]

    # Build all documents: metadata chunk first (chunk_index=-1), then body chunks
    all_docs: list[str] = [meta_text] + chunks
    all_ids: list[str] = [f"{arxiv_id}__chunk_-1"] + [
        f"{arxiv_id}__chunk_{i}" for i in range(len(chunks))
    ]
    all_metadatas: list[dict] = [
        {
            "arxiv_id": arxiv_id,
            "title": title,
            "tags": tags_str,
            "chunk_index": -1,
            "source": str(md_path),
        }
    ] + [
        {
            "arxiv_id": arxiv_id,
            "title": title,
            "tags": tags_str,
            "chunk_index": i,
            "source": str(md_path),
        }
        for i in range(len(chunks))
    ]

    collection.upsert(ids=all_ids, documents=all_docs, metadatas=all_metadatas)


def search_papers(
    query: str,
    collection: chromadb.Collection,
    n_results: int = 5,
    min_score: float = 0.3,
) -> list[dict]:
    """Hybrid search (exact match + semantic) over indexed papers.

    Phase 1 performs exact/substring matching on title and arxiv_id metadata.
    Phase 2 performs semantic vector search. Results are merged and deduplicated
    by arxiv_id, with exact-match papers receiving a score bonus. Results below
    min_score are excluded.

    Args:
        query: Natural language or keyword search query.
        collection: ChromaDB collection to search.
        n_results: Number of results to retrieve from ChromaDB before dedup.
        min_score: Minimum score threshold; results below this are dropped.

    Returns:
        List of result dicts sorted by score descending, deduplicated by arxiv_id.
        Each dict has keys: title, arxiv_id, score, matched_section, tags.
    """
    if collection.count() == 0:
        return []

    query_lower = query.lower()

    # ---------------------------------------------------------------------------
    # Phase 1: Exact / substring match on title and arxiv_id metadata
    # ---------------------------------------------------------------------------
    exact_arxiv_ids: set[str] = set()
    try:
        all_meta = collection.get(include=["metadatas"])
        seen_for_exact: set[str] = set()
        for meta in (all_meta.get("metadatas") or []):
            aid = meta.get("arxiv_id", "")
            if aid in seen_for_exact:
                continue
            title_val = meta.get("title", "") or ""
            if (
                query_lower in title_val.lower()
                or query_lower in aid.lower()
            ):
                exact_arxiv_ids.add(aid)
            seen_for_exact.add(aid)
    except Exception:
        pass

    # ---------------------------------------------------------------------------
    # Phase 2: Semantic vector search
    # ---------------------------------------------------------------------------
    # Fetch more results than requested to ensure good dedup pool
    fetch_n = max(n_results * 3, 15)
    results = collection.query(query_texts=[query], n_results=min(fetch_n, collection.count()))

    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]

    # Build per-paper best-score map (deduplicate by arxiv_id)
    best: dict[str, dict] = {}
    for doc, meta, dist in zip(documents, metadatas, distances):
        arxiv_id = meta.get("arxiv_id", "")
        score = 1.0 / (1.0 + dist)

        # Boost exact matches
        if arxiv_id in exact_arxiv_ids:
            score = min(1.0, score + 0.3)

        matched_section = doc[:200] + "..." if len(doc) > 200 else doc

        if arxiv_id not in best or score > best[arxiv_id]["score"]:
            best[arxiv_id] = {
                "title": meta.get("title", ""),
                "arxiv_id": arxiv_id,
                "score": score,
                "matched_section": matched_section,
                "tags": meta.get("tags", ""),
            }

    # Ensure exact-match papers always appear even if outside semantic top-N
    for arxiv_id in exact_arxiv_ids:
        if arxiv_id not in best:
            # Fetch this paper's metadata chunk directly
            try:
                got = collection.get(
                    where={"arxiv_id": {"$eq": arxiv_id}},
                    include=["metadatas", "documents"],
                )
                if got and got.get("ids"):
                    meta = got["metadatas"][0]
                    doc = (got.get("documents") or [""])[0]
                    matched_section = doc[:200] + "..." if len(doc) > 200 else doc
                    best[arxiv_id] = {
                        "title": meta.get("title", ""),
                        "arxiv_id": arxiv_id,
                        "score": 0.6,  # Default exact-match score
                        "matched_section": matched_section,
                        "tags": meta.get("tags", ""),
                    }
            except Exception:
                pass

    # Apply min_score filter, then sort
    filtered = [r for r in best.values() if r["score"] >= min_score]

    # Return top n_results
    return sorted(filtered, key=lambda r: r["score"], reverse=True)[:n_results]


def reindex_all(papers_dir: Path, collection: chromadb.Collection) -> int:
    """Delete all indexed documents and re-index all .md files in papers_dir.

    Args:
        papers_dir: Directory to search recursively for .md files.
        collection: ChromaDB collection to reindex.

    Returns:
        Number of papers indexed.
    """
    # Delete all existing documents
    try:
        existing = collection.get(where={"arxiv_id": {"$ne": ""}})
        if existing and existing.get("ids"):
            collection.delete(ids=existing["ids"])
    except Exception:
        pass

    md_files = list(papers_dir.rglob("*.md"))
    for md_path in md_files:
        index_paper(md_path, collection)

    return len(md_files)
