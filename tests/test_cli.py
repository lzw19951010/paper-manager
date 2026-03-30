"""Tests for paper_manager.cli commands."""
from __future__ import annotations

import json
import os
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from typer.testing import CliRunner

from paper_manager.cli import app

runner = CliRunner()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_config(tmp_path: Path) -> MagicMock:
    """Build a mock Config pointing at tmp_path."""
    cfg = MagicMock()
    cfg.api_key = "test-key"
    cfg.model = "claude-opus-4-6"
    cfg.tag_model = "claude-opus-4-6"
    cfg.papers_dir = "papers"
    cfg.template = "default"
    cfg.chromadb_dir = ".chromadb"
    cfg.git_remote = ""
    cfg.root_dir = tmp_path
    cfg.papers_path = tmp_path / "papers"
    cfg.chromadb_path = tmp_path / ".chromadb"
    cfg.templates_path = tmp_path / "templates"
    cfg.tmp_path = tmp_path / "tmp"
    return cfg


def _write_paper_note(papers_dir: Path, arxiv_id: str = "2301.00001", date: str = "2023-01-01") -> Path:
    """Write a minimal paper note for use in tests."""
    year_dir = papers_dir / date[:4]
    year_dir.mkdir(parents=True, exist_ok=True)
    note = year_dir / f"{arxiv_id}.md"
    note.write_text(
        f"---\narxiv_id: {arxiv_id}\ntitle: Test Paper\ndate: {date}\n"
        "tags:\n- ml\nkeywords:\n- testing\n---\n\n"
        "## 核心速览 (Executive Summary)\n\n**TL;DR:** X solves Y.\n\n"
        "## 方法详解 (Methodology)\n\nWe use Y approach.\n",
        encoding="utf-8",
    )
    return note


# ---------------------------------------------------------------------------
# init
# ---------------------------------------------------------------------------

class TestInit:
    def test_init_creates_config_from_example(self, tmp_path: Path) -> None:
        (tmp_path / "config.yaml.example").write_text(
            "anthropic_api_key: \"\"\n", encoding="utf-8"
        )

        old_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            result = runner.invoke(app, ["init"], catch_exceptions=False)
        finally:
            os.chdir(old_cwd)

        assert result.exit_code == 0
        assert (tmp_path / "config.yaml").exists()

    def test_init_creates_obsidian_config(self, tmp_path: Path) -> None:
        (tmp_path / "config.yaml.example").write_text(
            "anthropic_api_key: \"\"\n", encoding="utf-8"
        )

        old_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            result = runner.invoke(app, ["init"], catch_exceptions=False)
        finally:
            os.chdir(old_cwd)

        assert result.exit_code == 0
        app_json = tmp_path / ".obsidian" / "app.json"
        assert app_json.exists()
        data = json.loads(app_json.read_text(encoding="utf-8"))
        assert "userIgnoreFilters" in data
        assert "src/" in data["userIgnoreFilters"]

    def test_init_idempotent(self, tmp_path: Path) -> None:
        """Running init twice should not raise errors."""
        (tmp_path / "config.yaml.example").write_text(
            "anthropic_api_key: \"\"\n", encoding="utf-8"
        )

        old_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            result1 = runner.invoke(app, ["init"], catch_exceptions=False)
            result2 = runner.invoke(app, ["init"], catch_exceptions=False)
        finally:
            os.chdir(old_cwd)

        assert result1.exit_code == 0
        assert result2.exit_code == 0
        # Second run should note that files already exist
        assert "already exists" in result2.output


# ---------------------------------------------------------------------------
# add
# ---------------------------------------------------------------------------

SAMPLE_METADATA = {
    "arxiv_id": "2301.00001",
    "title": "Test Paper: A Survey of Testing",
    "authors": ["Alice Smith"],
    "date": "2023-01-01",
    "abstract": "Abstract text.",
    "categories": ["cs.SE"],
    "url": "https://arxiv.org/abs/2301.00001",
}

SAMPLE_ANALYSIS = {
    "research_question": "How can we improve testing?",
    "background": "Testing matters.",
    "method": "We propose a framework.",
    "results": "30% improvement.",
    "conclusions": "It works.",
    "limitations": None,
    "future_work": None,
    "venue": None,
    "keywords": ["testing", "automation"],
}


class TestAdd:
    def test_add_processes_paper(self, tmp_path: Path) -> None:
        """add command should fetch metadata, analyze, and write a note."""
        cfg = _make_config(tmp_path)
        cfg.papers_path.mkdir(parents=True)
        cfg.tmp_path.mkdir(parents=True)
        cfg.templates_path.mkdir(parents=True)
        (cfg.templates_path / "default.md").write_text("Analyze this.", encoding="utf-8")

        pdf_path = cfg.tmp_path / "2301.00001.pdf"
        note_path = tmp_path / "papers" / "llm" / "pretraining" / "test-paper.md"

        with (
            patch("paper_manager.config.load_config", return_value=cfg),
            patch("paper_manager.downloader.parse_arxiv_id", return_value="2301.00001"),
            patch("paper_manager.writer.find_existing", return_value=None),
            patch("paper_manager.downloader.fetch_metadata", return_value=SAMPLE_METADATA),
            patch("paper_manager.downloader.download_pdf", return_value=pdf_path),
            patch("paper_manager.templates.load_template", return_value="Analyze this."),
            patch("paper_manager.templates.render_prompt", return_value="prompt text"),
            patch("paper_manager.analyzer.analyze_paper", return_value=SAMPLE_ANALYSIS),
            patch("paper_manager.analyzer.generate_tags", return_value=["ml", "testing"]),
            patch("paper_manager.analyzer.classify_paper", return_value="llm/pretraining"),
            patch("paper_manager.writer.write_paper_note", return_value=note_path),
            patch("paper_manager.search.get_collection", return_value=MagicMock()),
            patch("paper_manager.search.index_paper"),
        ):
            result = runner.invoke(app, ["add", "https://arxiv.org/abs/2301.00001"])

        assert result.exit_code == 0
        assert "Done" in result.output
        assert "llm/pretraining" in result.output

    def test_add_skips_existing_without_force(self, tmp_path: Path) -> None:
        """Without --force, existing papers should be skipped."""
        cfg = _make_config(tmp_path)
        existing_note = tmp_path / "papers" / "2023" / "test.md"

        with (
            patch("paper_manager.config.load_config", return_value=cfg),
            patch("paper_manager.downloader.parse_arxiv_id", return_value="2301.00001"),
            patch("paper_manager.writer.find_existing", return_value=existing_note),
            patch("paper_manager.downloader.fetch_metadata") as mock_fetch,
        ):
            result = runner.invoke(app, ["add", "2301.00001"])

        assert result.exit_code == 0
        assert "Skipping" in result.output
        mock_fetch.assert_not_called()

    def test_add_invalid_url_continues(self, tmp_path: Path) -> None:
        """Invalid URL should print error and continue without crashing."""
        cfg = _make_config(tmp_path)

        with (
            patch("paper_manager.config.load_config", return_value=cfg),
            patch("paper_manager.downloader.parse_arxiv_id", side_effect=ValueError("bad url")),
        ):
            result = runner.invoke(app, ["add", "not-a-url"])

        assert result.exit_code == 0
        assert "Error" in result.output

    def test_add_force_flag_passes_to_writer(self, tmp_path: Path) -> None:
        """--force flag must be forwarded to write_paper_note."""
        cfg = _make_config(tmp_path)
        cfg.papers_path.mkdir(parents=True)
        cfg.tmp_path.mkdir(parents=True)
        cfg.templates_path.mkdir(parents=True)
        (cfg.templates_path / "default.md").write_text("Analyze.", encoding="utf-8")

        pdf_path = cfg.tmp_path / "2301.00001.pdf"
        mock_write = MagicMock(return_value=tmp_path / "papers" / "test.md")

        with (
            patch("paper_manager.config.load_config", return_value=cfg),
            patch("paper_manager.downloader.parse_arxiv_id", return_value="2301.00001"),
            patch("paper_manager.writer.find_existing", return_value=tmp_path / "papers" / "existing.md"),
            patch("paper_manager.downloader.fetch_metadata", return_value=SAMPLE_METADATA),
            patch("paper_manager.downloader.download_pdf", return_value=pdf_path),
            patch("paper_manager.templates.load_template", return_value="Analyze."),
            patch("paper_manager.templates.render_prompt", return_value="prompt"),
            patch("paper_manager.analyzer.analyze_paper", return_value=SAMPLE_ANALYSIS),
            patch("paper_manager.analyzer.generate_tags", return_value=["ml"]),
            patch("paper_manager.analyzer.classify_paper", return_value="misc"),
            patch("paper_manager.writer.write_paper_note", mock_write),
            patch("paper_manager.search.get_collection", return_value=MagicMock()),
            patch("paper_manager.search.index_paper"),
        ):
            result = runner.invoke(app, ["add", "--force", "2301.00001"])

        assert result.exit_code == 0
        # write_paper_note must be called with force=True
        call_kwargs = mock_write.call_args
        assert call_kwargs.kwargs.get("force") is True or (
            len(call_kwargs.args) >= 5 and call_kwargs.args[4] is True
        )


# ---------------------------------------------------------------------------
# search
# ---------------------------------------------------------------------------

class TestSearch:
    def test_search_displays_results(self, tmp_path: Path) -> None:
        cfg = _make_config(tmp_path)
        cfg.chromadb_path.mkdir(parents=True)

        mock_results = [
            {
                "title": "Attention Is All You Need",
                "arxiv_id": "1706.03762",
                "score": 0.923,
                "matched_section": "We propose a new architecture called the Transformer.",
                "tags": "NLP, transformer",
            }
        ]

        with (
            patch("paper_manager.config.load_config", return_value=cfg),
            patch("paper_manager.search.get_collection", return_value=MagicMock()),
            patch("paper_manager.search.search_papers", return_value=mock_results),
        ):
            result = runner.invoke(app, ["search", "attention mechanism"])

        assert result.exit_code == 0
        assert "Attention Is All You Need" in result.output
        assert "1706.03762" in result.output
        assert "0.923" in result.output

    def test_search_no_index(self, tmp_path: Path) -> None:
        """Should exit non-zero when ChromaDB index directory does not exist."""
        cfg = _make_config(tmp_path)
        # chromadb_path intentionally NOT created

        with patch("paper_manager.config.load_config", return_value=cfg):
            result = runner.invoke(app, ["search", "transformers"])

        assert result.exit_code != 0

    def test_search_no_results_message(self, tmp_path: Path) -> None:
        cfg = _make_config(tmp_path)
        cfg.chromadb_path.mkdir(parents=True)

        with (
            patch("paper_manager.config.load_config", return_value=cfg),
            patch("paper_manager.search.get_collection", return_value=MagicMock()),
            patch("paper_manager.search.search_papers", return_value=[]),
        ):
            result = runner.invoke(app, ["search", "nothing here"])

        assert result.exit_code == 0
        assert "No matching papers found" in result.output


# ---------------------------------------------------------------------------
# reindex
# ---------------------------------------------------------------------------

class TestReindex:
    def test_reindex_reports_count(self, tmp_path: Path) -> None:
        cfg = _make_config(tmp_path)
        cfg.papers_path.mkdir(parents=True)

        with (
            patch("paper_manager.config.load_config", return_value=cfg),
            patch("paper_manager.search.get_collection", return_value=MagicMock()),
            patch("paper_manager.search.reindex_all", return_value=7),
        ):
            result = runner.invoke(app, ["reindex"])

        assert result.exit_code == 0
        assert "7" in result.output

    def test_reindex_no_papers_dir(self, tmp_path: Path) -> None:
        """Should exit non-zero when papers directory does not exist."""
        cfg = _make_config(tmp_path)
        # papers_path intentionally NOT created

        with patch("paper_manager.config.load_config", return_value=cfg):
            result = runner.invoke(app, ["reindex"])

        assert result.exit_code != 0


# ---------------------------------------------------------------------------
# tag
# ---------------------------------------------------------------------------

class TestTag:
    def test_tag_updates_frontmatter(self, tmp_path: Path) -> None:
        cfg = _make_config(tmp_path)
        cfg.papers_path.mkdir(parents=True)
        _write_paper_note(cfg.papers_path)

        with (
            patch("paper_manager.config.load_config", return_value=cfg),
            patch("paper_manager.analyzer.generate_tags", return_value=["new-tag", "ml"]),
            patch("paper_manager.writer.update_frontmatter") as mock_update,
        ):
            result = runner.invoke(app, ["tag"])

        assert result.exit_code == 0
        mock_update.assert_called_once()
        new_fm = mock_update.call_args.args[1]
        assert new_fm["tags"] == ["new-tag", "ml"]

    def test_tag_limit_respected(self, tmp_path: Path) -> None:
        """--limit N should process at most N papers."""
        cfg = _make_config(tmp_path)
        cfg.papers_path.mkdir(parents=True)
        for i in range(5):
            _write_paper_note(cfg.papers_path, arxiv_id=f"2301.0000{i}")

        with (
            patch("paper_manager.config.load_config", return_value=cfg),
            patch("paper_manager.analyzer.generate_tags", return_value=["ml"]),
            patch("paper_manager.writer.update_frontmatter") as mock_update,
        ):
            result = runner.invoke(app, ["tag", "--limit", "2"])

        assert result.exit_code == 0
        assert mock_update.call_count == 2

    def test_tag_since_filter(self, tmp_path: Path) -> None:
        """--since should exclude papers before the given date."""
        cfg = _make_config(tmp_path)
        cfg.papers_path.mkdir(parents=True)
        _write_paper_note(cfg.papers_path, arxiv_id="2101.00001", date="2021-06-01")
        _write_paper_note(cfg.papers_path, arxiv_id="2301.00001", date="2023-01-01")

        with (
            patch("paper_manager.config.load_config", return_value=cfg),
            patch("paper_manager.analyzer.generate_tags", return_value=["ml"]),
            patch("paper_manager.writer.update_frontmatter") as mock_update,
        ):
            result = runner.invoke(app, ["tag", "--since", "2022-01-01"])

        assert result.exit_code == 0
        # Only the 2023 paper should be tagged
        assert mock_update.call_count == 1

    def test_tag_no_papers(self, tmp_path: Path) -> None:
        """Empty papers dir should print a message and exit cleanly."""
        cfg = _make_config(tmp_path)
        cfg.papers_path.mkdir(parents=True)

        with patch("paper_manager.config.load_config", return_value=cfg):
            result = runner.invoke(app, ["tag"])

        assert result.exit_code == 0
        assert "No papers" in result.output


# ---------------------------------------------------------------------------
# config
# ---------------------------------------------------------------------------

class TestConfigCmd:
    def test_config_shows_settings(self, tmp_path: Path) -> None:
        cfg = _make_config(tmp_path)

        mock_proc = MagicMock()
        mock_proc.returncode = 0
        mock_proc.stdout = "OK"

        with (
            patch("paper_manager.config.load_config", return_value=cfg),
            patch("subprocess.run", return_value=mock_proc),
        ):
            result = runner.invoke(app, ["config"])

        assert result.exit_code == 0
        assert "claude-opus-4-6" in result.output
        assert "Claude Code CLI" in result.output

    def test_config_api_error_reported(self, tmp_path: Path) -> None:
        """A failed CLI check should report 'could not validate'."""
        cfg = _make_config(tmp_path)

        with (
            patch("paper_manager.config.load_config", return_value=cfg),
            patch("subprocess.run", side_effect=Exception("connection error")),
        ):
            result = runner.invoke(app, ["config"])

        assert result.exit_code == 0
        assert "could not validate" in result.output
