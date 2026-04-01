"""Tests for deepaper.writer module."""
from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from deepaper.writer import (
    find_existing,
    sanitize_filename,
    update_frontmatter,
    write_paper_note,
)


# ---------------------------------------------------------------------------
# Inline fixtures (mirrors conftest.py fixtures as plain dicts for use below)
# ---------------------------------------------------------------------------

def _sample_metadata() -> dict:
    return {
        "arxiv_id": "2301.00001",
        "title": "Test Paper: A Survey of Testing",
        "authors": ["Alice Smith", "Bob Jones"],
        "date": "2023-01-01",
        "abstract": "This paper surveys testing methodologies.",
        "categories": ["cs.SE"],
        "url": "https://arxiv.org/abs/2301.00001",
    }


def _sample_analysis_fm() -> dict:
    return {
        "venue": "ICSE 2023",
        "publication_type": "conference",
        "doi": "10.1234/test.2023",
        "keywords": ["testing", "software quality", "automation"],
        "tldr": "A structure-guided test generation framework that improves coverage by 30%.",
        "core_contribution": "new-method",
        "baselines": ["EvoSuite", "Randoop"],
        "datasets": ["Defects4J", "SF110"],
        "metrics": ["branch coverage", "mutation score"],
        "code_url": "https://github.com/example/test-framework",
    }


def _sample_analysis_body() -> str:
    return (
        "## 核心速览 (Executive Summary)\n\n"
        "**TL;DR:** 新测试框架提升覆盖率30%。\n\n"
        "**一图流:** 旧方法是手动找针，新方法是磁铁吸针。\n\n"
        "---\n\n"
        "## 动机与第一性原理 (Motivation & First Principles)\n\n"
        "**痛点:** 传统方法覆盖率低。\n\n**核心洞察:** 利用代码结构信息引导测试生成。\n\n"
        "---\n\n"
        "## 方法详解 (Methodology)\n\n"
        "### 直觉版\n旧方法随机生成，新方法按结构引导。\n\n### 精确版\nInput → Analyzer → Generator → Output\n\n"
        "---\n\n"
        "## 实验与归因 (Experiments & Attribution)\n\n"
        "**核心收益:** 覆盖率提升30%。\n\n**归因分析:** 结构引导贡献最大。\n\n"
        "---\n\n"
        "## 专家批判 (Critical Review)\n\n"
        "**隐性成本:** 分析阶段耗时增加2倍。\n\n**工程落地建议:** 注意大型项目的内存占用。\n\n"
        "---\n\n"
        "## 机制迁移分析 (Mechanism Transfer Analysis)\n\n"
        "### 机制解耦\n结构引导生成可迁移到其他领域。\n\n### 迁移处方\n可用于API测试生成。"
    )


# ---------------------------------------------------------------------------
# sanitize_filename
# ---------------------------------------------------------------------------

def test_sanitize_filename_basic() -> None:
    assert sanitize_filename("Attention Is All You Need") == "attention-is-all-you-need"


def test_sanitize_filename_special_chars() -> None:
    result = sanitize_filename('No/Bad\\Chars:Here*Or?Here"And<These>Too|Done')
    # None of the unsafe chars should survive
    for ch in r'/\:*?"<>|':
        assert ch not in result
    # Content words should still be present
    assert "no" in result
    assert "bad" in result


def test_sanitize_filename_unicode_preserved() -> None:
    # Chinese characters
    result = sanitize_filename("深度学习 Deep Learning")
    assert "深度学习" in result
    # Accented characters
    result2 = sanitize_filename("Réseau de Neurones")
    assert "é" in result2


def test_sanitize_filename_empty_fallback() -> None:
    # A title consisting entirely of unsafe chars should fall back to arxiv_id
    result = sanitize_filename('/:*?"<>|\\', arxiv_id="2301.99999")
    assert result == "2301.99999"


def test_sanitize_filename_truncation() -> None:
    long_title = "word " * 40  # 200 characters
    result = sanitize_filename(long_title)
    assert len(result) <= 80
    # Should not end with a hyphen (truncated at word boundary)
    assert not result.endswith("-")


# ---------------------------------------------------------------------------
# find_existing
# ---------------------------------------------------------------------------

def test_find_existing_finds_match(tmp_path: Path) -> None:
    papers_dir = tmp_path / "papers"
    papers_dir.mkdir()
    note = papers_dir / "some-paper.md"
    note.write_text(
        "---\narxiv_id: 2301.00001\ntitle: Some Paper\n---\n\n## Body\nContent here.\n",
        encoding="utf-8",
    )

    found = find_existing("2301.00001", papers_dir)
    assert found == note


def test_find_existing_returns_none(tmp_path: Path) -> None:
    papers_dir = tmp_path / "papers"
    papers_dir.mkdir()
    note = papers_dir / "other-paper.md"
    note.write_text(
        "---\narxiv_id: 9999.99999\ntitle: Other Paper\n---\n\n## Body\n",
        encoding="utf-8",
    )

    found = find_existing("2301.00001", papers_dir)
    assert found is None


# ---------------------------------------------------------------------------
# update_frontmatter
# ---------------------------------------------------------------------------

def test_update_frontmatter_preserves_body(tmp_path: Path) -> None:
    md = tmp_path / "paper.md"
    original_body = "\n## Notes\nMy hand-written notes go here.\n\nImportant insight!\n"
    md.write_text(
        f"---\narxiv_id: 2301.00001\ntitle: Old Title\n---{original_body}",
        encoding="utf-8",
    )

    new_fm = {"arxiv_id": "2301.00001", "title": "New Title", "status": "complete"}
    update_frontmatter(md, new_fm)

    updated = md.read_text(encoding="utf-8")

    # Body must be unchanged
    assert original_body in updated

    # New frontmatter must be present
    fm_end = updated.find("---", 3)
    fm_text = updated[3:fm_end]
    parsed = yaml.safe_load(fm_text)
    assert parsed["title"] == "New Title"
    assert parsed["arxiv_id"] == "2301.00001"


# ---------------------------------------------------------------------------
# write_paper_note
# ---------------------------------------------------------------------------

def test_write_paper_note_creates_file(tmp_path: Path) -> None:
    metadata = _sample_metadata()
    analysis_fm = _sample_analysis_fm()
    analysis_body = _sample_analysis_body()
    tags = ["machine-learning", "testing"]

    path = write_paper_note(analysis_fm, analysis_body, metadata, tags, tmp_path, category="llm/pretraining")

    assert path.exists()
    content = path.read_text(encoding="utf-8")

    # Check frontmatter is valid YAML
    assert content.startswith("---")
    fm_end = content.find("---", 3)
    assert fm_end != -1
    fm = yaml.safe_load(content[3:fm_end])
    assert fm["arxiv_id"] == "2301.00001"
    assert fm["title"] == metadata["title"]
    assert fm["tags"] == tags
    assert fm["venue"] == "ICSE 2023"
    assert fm["category"] == "llm/pretraining"
    assert fm["publication_type"] == "conference"
    assert fm["doi"] == "10.1234/test.2023"
    assert fm["tldr"] is not None
    assert fm["baselines"] == ["EvoSuite", "Randoop"]
    assert fm["datasets"] == ["Defects4J", "SF110"]
    assert fm["abstract"] == metadata["abstract"]
    assert fm["arxiv_categories"] == metadata["categories"]

    # Check category-based subdirectory (llm/pretraining)
    assert path.parent.name == "pretraining"
    assert path.parent.parent.name == "llm"

    # Check body sections are present (written by Claude, passed through as-is)
    assert "## 核心速览 (Executive Summary)" in content
    assert "## 动机与第一性原理" in content
    assert "## 方法详解 (Methodology)" in content
    assert "## 实验与归因" in content
    assert "## 专家批判 (Critical Review)" in content
    assert "## 机制迁移分析" in content


def test_write_paper_note_skip_duplicate(tmp_path: Path) -> None:
    metadata = _sample_metadata()
    analysis_fm = _sample_analysis_fm()
    analysis_body = _sample_analysis_body()
    tags = ["ml"]

    write_paper_note(analysis_fm, analysis_body, metadata, tags, tmp_path)

    with pytest.raises(FileExistsError) as exc_info:
        write_paper_note(analysis_fm, analysis_body, metadata, tags, tmp_path)

    assert "2301.00001" in str(exc_info.value)


def test_write_paper_note_force_overwrites(tmp_path: Path) -> None:
    metadata = _sample_metadata()
    analysis_fm = _sample_analysis_fm()
    analysis_body = _sample_analysis_body()
    tags = ["ml"]

    first_path = write_paper_note(analysis_fm, analysis_body, metadata, tags, tmp_path)
    assert first_path.exists()

    # Should not raise
    second_path = write_paper_note(analysis_fm, analysis_body, metadata, tags, tmp_path, force=True)

    # File should still exist and contain valid frontmatter
    content = second_path.read_text(encoding="utf-8")
    fm_end = content.find("---", 3)
    fm = yaml.safe_load(content[3:fm_end])
    assert fm["arxiv_id"] == "2301.00001"


def test_write_paper_note_with_quality_fields(tmp_path):
    """write_paper_note should include quality, failed_gates, pipeline_version in frontmatter."""
    import re
    from deepaper.writer import write_paper_note
    import yaml

    metadata = {
        "title": "Test Paper",
        "authors": ["Author A"],
        "date": "2024-01-01",
        "arxiv_id": "2401.99999",
        "url": "https://arxiv.org/abs/2401.99999",
    }
    analysis_fm = {"venue": "arxiv", "tldr": "A test paper"}
    result = write_paper_note(
        analysis_fm, "Body content", metadata, ["test"],
        tmp_path, category="misc",
        quality="partial", failed_gates=["S5", "S7"], pipeline_version=2,
    )

    content = result.read_text()
    fm_match = re.match(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
    fm = yaml.safe_load(fm_match.group(1))
    assert fm["quality"] == "partial"
    assert fm["failed_gates"] == ["S5", "S7"]
    assert fm["pipeline_version"] == 2
