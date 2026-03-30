"""Tests for paper_manager.search."""
from __future__ import annotations

from pathlib import Path

import chromadb
import pytest

from paper_manager.search import (
    _get_embedding_function,
    chunk_document,
    index_paper,
    parse_frontmatter,
    reindex_all,
    search_papers,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_collection() -> chromadb.Collection:
    """Return a fresh in-memory ChromaDB collection for each test."""
    client = chromadb.EphemeralClient()
    ef = _get_embedding_function()
    return client.get_or_create_collection("test_papers", embedding_function=ef)


def _write_paper(tmp_path: Path, filename: str, content: str) -> Path:
    p = tmp_path / filename
    p.write_text(content, encoding="utf-8")
    return p


PAPER_1 = """\
---
arxiv_id: "2301.00001"
title: "Attention Is All You Need"
tags:
  - transformers
  - nlp
---

## Introduction

The transformer architecture revolutionised natural language processing.

## Method

We propose a novel self-attention mechanism that replaces recurrence entirely.
"""

PAPER_2 = """\
---
arxiv_id: "2301.00002"
title: "Deep Residual Learning"
tags:
  - deep-learning
  - vision
---

## Introduction

Residual connections allow training of very deep networks.

## Experiments

We evaluate on ImageNet and achieve state-of-the-art results.
"""


# ---------------------------------------------------------------------------
# parse_frontmatter
# ---------------------------------------------------------------------------

def test_parse_frontmatter_with_yaml():
    md = "---\narxiv_id: '2301.00001'\ntitle: 'My Paper'\n---\n\nBody text here."
    fm, body = parse_frontmatter(md)
    assert fm["arxiv_id"] == "2301.00001"
    assert fm["title"] == "My Paper"
    assert "Body text here." in body


def test_parse_frontmatter_without_yaml():
    md = "# Just a heading\n\nSome content without frontmatter."
    fm, body = parse_frontmatter(md)
    assert fm == {}
    assert body == md


# ---------------------------------------------------------------------------
# chunk_document
# ---------------------------------------------------------------------------

def test_chunk_document_by_headers():
    body = "## Section1\n\nContent of section one.\n\n## Section2\n\nContent of section two."
    chunks = chunk_document(body)
    assert len(chunks) == 2
    assert "Section1" in chunks[0]
    assert "Section2" in chunks[1]


def test_chunk_document_no_headers():
    body = "First paragraph.\n\nSecond paragraph.\n\nThird paragraph."
    chunks = chunk_document(body)
    assert len(chunks) == 3
    assert chunks[0] == "First paragraph."
    assert chunks[1] == "Second paragraph."
    assert chunks[2] == "Third paragraph."


# ---------------------------------------------------------------------------
# index_paper
# ---------------------------------------------------------------------------

def test_index_paper_creates_entries(tmp_path: Path):
    md_path = _write_paper(tmp_path, "2301.00001.md", PAPER_1)
    collection = _make_collection()

    index_paper(md_path, collection)

    results = collection.get(where={"arxiv_id": {"$eq": "2301.00001"}})
    assert len(results["ids"]) >= 1
    # Verify metadata fields are stored
    meta = results["metadatas"][0]
    assert meta["arxiv_id"] == "2301.00001"
    assert meta["title"] == "Attention Is All You Need"


# ---------------------------------------------------------------------------
# search_papers
# ---------------------------------------------------------------------------

def test_search_papers_returns_results(tmp_path: Path):
    md1 = _write_paper(tmp_path, "2301.00001.md", PAPER_1)
    md2 = _write_paper(tmp_path, "2301.00002.md", PAPER_2)
    collection = _make_collection()

    index_paper(md1, collection)
    index_paper(md2, collection)

    results = search_papers("transformer self-attention nlp", collection, n_results=5)

    assert len(results) >= 1
    # Each result must have the required keys
    for r in results:
        assert "title" in r
        assert "arxiv_id" in r
        assert "score" in r
        assert "matched_section" in r
        assert "tags" in r


# ---------------------------------------------------------------------------
# reindex_all
# ---------------------------------------------------------------------------

def test_reindex_all_counts_papers(tmp_path: Path):
    papers_dir = tmp_path / "papers"
    papers_dir.mkdir()

    for i in range(3):
        content = (
            f"---\narxiv_id: '2301.0000{i}'\ntitle: 'Paper {i}'\n---\n\n"
            f"## Introduction\n\nContent for paper {i}.\n"
        )
        (papers_dir / f"paper{i}.md").write_text(content, encoding="utf-8")

    collection = _make_collection()
    count = reindex_all(papers_dir, collection)

    assert count == 3


# ---------------------------------------------------------------------------
# Deduplication
# ---------------------------------------------------------------------------

def test_search_deduplicates_by_arxiv_id(tmp_path: Path):
    # Paper with many sections → multiple chunks
    body_sections = "\n\n".join(
        f"## Section {i}\n\nContent about transformers and attention in section {i}."
        for i in range(6)
    )
    content = (
        "---\narxiv_id: '2301.00001'\ntitle: 'Multi-Chunk Paper'\ntags:\n  - transformers\n---\n\n"
        + body_sections
    )
    md_path = _write_paper(tmp_path, "2301.00001.md", content)
    collection = _make_collection()

    index_paper(md_path, collection)

    # Request more results than chunks to stress dedup
    results = search_papers("transformers attention", collection, n_results=10)

    arxiv_ids = [r["arxiv_id"] for r in results]
    # All results belong to the same paper — deduplicated to exactly 1
    assert len(results) == 1
    assert arxiv_ids[0] == "2301.00001"


# ---------------------------------------------------------------------------
# Hybrid Search Tests
# ---------------------------------------------------------------------------

class TestHybridSearch:
    """Tests for improved hybrid search (exact + semantic)."""

    def test_exact_title_match(self, tmp_path: Path):
        """Search by exact title should return that paper as #1."""
        content = (
            "---\narxiv_id: '2412.00001'\ntitle: 'OLMo 3'\ntags:\n  - llm\n---\n\n"
            "## Introduction\n\nOLMo 3 is an open language model.\n"
        )
        md_path = _write_paper(tmp_path, "2412.00001.md", content)
        collection = _make_collection()
        index_paper(md_path, collection)

        results = search_papers("OLMo 3", collection, n_results=5)

        assert len(results) >= 1
        assert results[0]["arxiv_id"] == "2412.00001"

    def test_partial_title_match(self, tmp_path: Path):
        """Search by partial title should find matching papers."""
        content_v3 = (
            "---\narxiv_id: '2412.10001'\ntitle: 'DeepSeek-V3 Technical Report'\n"
            "tags:\n  - llm\n---\n\n## Introduction\n\nDeepSeek-V3 technical details.\n"
        )
        content_r1 = (
            "---\narxiv_id: '2501.12948'\ntitle: 'DeepSeek-R1 Report'\n"
            "tags:\n  - reasoning\n---\n\n## Introduction\n\nDeepSeek-R1 reasoning model.\n"
        )
        _write_paper(tmp_path, "v3.md", content_v3)
        _write_paper(tmp_path, "r1.md", content_r1)
        collection = _make_collection()
        index_paper(tmp_path / "v3.md", collection)
        index_paper(tmp_path / "r1.md", collection)

        results = search_papers("deepseek", collection, n_results=5)

        arxiv_ids = {r["arxiv_id"] for r in results}
        assert "2412.10001" in arxiv_ids
        assert "2501.12948" in arxiv_ids

    def test_arxiv_id_search(self, tmp_path: Path):
        """Search by arxiv_id should return the corresponding paper."""
        content = (
            "---\narxiv_id: '2512.13961'\ntitle: 'Some Paper'\ntags:\n  - misc\n---\n\n"
            "## Introduction\n\nThis paper describes something.\n"
        )
        md_path = _write_paper(tmp_path, "2512.13961.md", content)
        collection = _make_collection()
        index_paper(md_path, collection)

        results = search_papers("2512.13961", collection, n_results=5)

        assert len(results) >= 1
        assert results[0]["arxiv_id"] == "2512.13961"

    def test_keyword_search(self, tmp_path: Path):
        """Search by keyword in frontmatter should find papers with that keyword."""
        content = (
            "---\narxiv_id: '2412.00002'\ntitle: 'MoE Paper'\n"
            "keywords:\n  - mixture-of-experts\n  - training\ntags:\n  - llm\n---\n\n"
            "## Introduction\n\nThis paper explores mixture-of-experts training.\n"
        )
        md_path = _write_paper(tmp_path, "2412.00002.md", content)
        collection = _make_collection()
        index_paper(md_path, collection)

        results = search_papers("mixture-of-experts", collection, n_results=5)

        assert len(results) >= 1
        assert results[0]["arxiv_id"] == "2412.00002"

    def test_semantic_search_chinese(self, tmp_path: Path):
        """Chinese semantic search should find relevant papers."""
        content = (
            "---\narxiv_id: '2412.00003'\ntitle: 'MoE Chinese Paper'\n"
            "tags:\n  - llm\n---\n\n"
            "## 介绍\n\n本文研究混合专家模型的训练效率与性能优化方法。\n\n"
            "## 方法\n\n通过改进路由策略提升混合专家模型的计算效率。\n"
        )
        md_path = _write_paper(tmp_path, "2412.00003.md", content)
        collection = _make_collection()
        index_paper(md_path, collection)

        results = search_papers("混合专家模型训练效率", collection, n_results=5)

        assert len(results) >= 1
        assert results[0]["arxiv_id"] == "2412.00003"

    def test_semantic_search_english(self, tmp_path: Path):
        """English semantic search should find relevant papers."""
        content = (
            "---\narxiv_id: '2412.00004'\ntitle: 'RL Reasoning Paper'\n"
            "tags:\n  - reasoning\n---\n\n"
            "## Introduction\n\nThis paper uses reinforcement learning to improve reasoning.\n\n"
            "## Method\n\nWe train a language model with RLHF to enhance logical reasoning.\n"
        )
        md_path = _write_paper(tmp_path, "2412.00004.md", content)
        collection = _make_collection()
        index_paper(md_path, collection)

        results = search_papers("reinforcement learning reasoning", collection, n_results=5)

        assert len(results) >= 1
        assert results[0]["arxiv_id"] == "2412.00004"

    def test_exact_match_scores_higher(self, tmp_path: Path):
        """Exact title match should score higher than semantic-only match."""
        content_exact = (
            "---\narxiv_id: '1706.03762'\ntitle: 'Attention Is All You Need'\n"
            "tags:\n  - transformers\n---\n\n"
            "## Introduction\n\nTransformer architecture using self-attention.\n"
        )
        content_survey = (
            "---\narxiv_id: '2001.00001'\ntitle: 'Transformer Survey'\n"
            "tags:\n  - survey\n---\n\n"
            "## Introduction\n\nA survey of transformer models and attention mechanisms.\n"
        )
        _write_paper(tmp_path, "1706.03762.md", content_exact)
        _write_paper(tmp_path, "2001.00001.md", content_survey)
        collection = _make_collection()
        index_paper(tmp_path / "1706.03762.md", collection)
        index_paper(tmp_path / "2001.00001.md", collection)

        results = search_papers("Attention Is All You Need", collection, n_results=5)

        assert len(results) >= 1
        assert results[0]["arxiv_id"] == "1706.03762"
        # The exact match should score higher than the survey
        if len(results) >= 2:
            assert results[0]["score"] > results[1]["score"]

    def test_no_results_for_nonexistent(self, tmp_path: Path):
        """Search with a strict min_score should exclude semantically unrelated papers."""
        content = (
            "---\narxiv_id: '2301.00001'\ntitle: 'Attention Is All You Need'\n"
            "tags:\n  - transformers\n---\n\n"
            "## Introduction\n\nTransformer architecture using self-attention.\n"
        )
        md_path = _write_paper(tmp_path, "2301.00001.md", content)
        collection = _make_collection()
        index_paper(md_path, collection)

        # Use strict min_score to ensure completely unrelated queries return nothing
        results = search_papers(
            "一篇完全不存在的论文xyz123abc", collection, n_results=5, min_score=0.75
        )

        assert results == []

    def test_dedup_still_works(self, tmp_path: Path):
        """Multiple chunks from same paper should be deduplicated."""
        body_sections = "\n\n".join(
            f"## Section {i}\n\nDetailed content about language models in section {i}."
            for i in range(8)
        )
        content = (
            "---\narxiv_id: '2412.00005'\ntitle: 'Large Language Model Study'\n"
            "tags:\n  - llm\n---\n\n" + body_sections
        )
        md_path = _write_paper(tmp_path, "2412.00005.md", content)
        collection = _make_collection()
        index_paper(md_path, collection)

        results = search_papers("language models", collection, n_results=20)

        arxiv_ids = [r["arxiv_id"] for r in results]
        assert len(results) == 1
        assert arxiv_ids[0] == "2412.00005"
