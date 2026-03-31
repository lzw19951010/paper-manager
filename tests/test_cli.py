"""Tests for deepaper.cli commands."""
from __future__ import annotations

import json
import os
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
import yaml
from typer.testing import CliRunner

from deepaper.cli import app

runner = CliRunner()

SAMPLE_METADATA = {
    "arxiv_id": "2301.00001",
    "title": "Test Paper: A Survey of Testing",
    "authors": ["Alice Smith"],
    "date": "2023-01-01",
    "abstract": "Abstract text.",
    "categories": ["cs.SE"],
    "url": "https://arxiv.org/abs/2301.00001",
}


# ---------------------------------------------------------------------------
# install
# ---------------------------------------------------------------------------

class TestInstall:
    def test_install_creates_global_slash_command(self, tmp_path: Path) -> None:
        cmd_path = tmp_path / ".claude" / "commands" / "deepaper.md"
        with patch.object(Path, "home", return_value=tmp_path):
            result = runner.invoke(app, ["install"])
        assert result.exit_code == 0
        assert cmd_path.exists()
        content = cmd_path.read_text()
        assert "deepaper download" in content
        assert "deepaper save" in content


# ---------------------------------------------------------------------------
# init
# ---------------------------------------------------------------------------

class TestInit:
    def test_init_creates_project(self, tmp_path: Path) -> None:
        old_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            result = runner.invoke(app, ["init"], catch_exceptions=False)
        finally:
            os.chdir(old_cwd)

        assert result.exit_code == 0
        assert (tmp_path / "config.yaml").exists()
        assert (tmp_path / "papers").exists()
        assert (tmp_path / ".claude" / "commands" / "deepaper.md").exists()

    def test_init_idempotent(self, tmp_path: Path) -> None:
        old_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            runner.invoke(app, ["init"], catch_exceptions=False)
            result = runner.invoke(app, ["init"], catch_exceptions=False)
        finally:
            os.chdir(old_cwd)
        assert result.exit_code == 0
        assert "already exists" in result.output


# ---------------------------------------------------------------------------
# download
# ---------------------------------------------------------------------------

class TestDownload:
    def test_outputs_json(self, tmp_path: Path) -> None:
        pdf_path = tmp_path / "tmp" / "2301.00001.pdf"
        pdf_path.parent.mkdir(parents=True)
        pdf_path.write_bytes(b"%PDF-1.4 test content here for size")

        old_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            with (
                patch("deepaper.downloader.parse_arxiv_id", return_value="2301.00001"),
                patch("deepaper.downloader.fetch_metadata", return_value=SAMPLE_METADATA),
                patch("deepaper.downloader.download_pdf", return_value=pdf_path),
            ):
                result = runner.invoke(app, ["download", "2301.00001"])
        finally:
            os.chdir(old_cwd)

        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["arxiv_id"] == "2301.00001"
        assert data["title"] == "Test Paper: A Survey of Testing"
        assert data["pdf_path"].endswith(".pdf")
        assert "size_mb" in data

    def test_invalid_url(self, tmp_path: Path) -> None:
        old_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            with patch("deepaper.downloader.parse_arxiv_id", side_effect=ValueError("bad")):
                result = runner.invoke(app, ["download", "not-a-url"])
        finally:
            os.chdir(old_cwd)
        assert result.exit_code == 1
        data = json.loads(result.output)
        assert "error" in data


# ---------------------------------------------------------------------------
# save
# ---------------------------------------------------------------------------

class TestSave:
    def _invoke_save(self, tmp_path, md_content, extra_args=None):
        (tmp_path / "papers").mkdir(exist_ok=True)
        input_file = tmp_path / "analysis.md"
        input_file.write_text(md_content, encoding="utf-8")
        args = ["save", "2301.00001", "--input", str(input_file)]
        if extra_args:
            args.extend(extra_args)
        old_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            with (
                patch("deepaper.downloader.parse_arxiv_id", return_value="2301.00001"),
                patch("deepaper.downloader.fetch_metadata", return_value=SAMPLE_METADATA),
            ):
                return runner.invoke(app, args)
        finally:
            os.chdir(old_cwd)

    def test_save_from_file(self, tmp_path: Path) -> None:
        md = "---\nvenue: NeurIPS 2023\nkeywords:\n  - test\n---\n\n## 核心速览\n\nContent."
        result = self._invoke_save(tmp_path, md, ["--category", "llm/pretraining"])
        assert result.exit_code == 0
        notes = list((tmp_path / "papers" / "llm" / "pretraining").glob("*.md"))
        assert len(notes) == 1
        content = notes[0].read_text(encoding="utf-8")
        assert "NeurIPS 2023" in content
        assert "2301.00001" in content

    def test_save_keywords_as_default_tags(self, tmp_path: Path) -> None:
        result = self._invoke_save(tmp_path, "---\nkeywords:\n  - scaling\n  - LLM\n---\n\n## Body")
        assert result.exit_code == 0
        notes = list((tmp_path / "papers" / "misc").glob("*.md"))
        fm = yaml.safe_load(notes[0].read_text()[3:notes[0].read_text().find("---", 3)])
        assert fm["tags"] == ["scaling", "LLM"]

    def test_save_explicit_tags(self, tmp_path: Path) -> None:
        result = self._invoke_save(tmp_path, "---\nkeywords:\n  - old\n---\n\n## Body",
                                   ["--tags", "new-1,new-2"])
        assert result.exit_code == 0
        notes = list((tmp_path / "papers" / "misc").glob("*.md"))
        fm = yaml.safe_load(notes[0].read_text()[3:notes[0].read_text().find("---", 3)])
        assert fm["tags"] == ["new-1", "new-2"]

    def test_save_empty_input_errors(self, tmp_path: Path) -> None:
        result = self._invoke_save(tmp_path, "")
        assert result.exit_code == 1

    def test_save_no_frontmatter(self, tmp_path: Path) -> None:
        result = self._invoke_save(tmp_path, "## Raw markdown\n\nNo YAML.", ["--category", "misc"])
        assert result.exit_code == 0
        notes = list((tmp_path / "papers" / "misc").glob("*.md"))
        content = notes[0].read_text(encoding="utf-8")
        assert "Raw markdown" in content
        assert "2301.00001" in content


# ---------------------------------------------------------------------------
# slash command template
# ---------------------------------------------------------------------------

class TestSlashCommandTemplate:
    def _get_template(self):
        cmd_path = Path(__file__).resolve().parent.parent / ".claude" / "commands" / "deepaper.md"
        assert cmd_path.exists()
        return cmd_path.read_text(encoding="utf-8")

    def test_has_done_definitions(self):
        content = self._get_template()
        assert "Done =" in content
        assert "至少2张" in content  # experiment tables
        assert "至少3个" in content  # hidden costs
        assert "缺一不可" in content  # transfer prescription
        assert "至少3" in content and "前身" in content

    def test_has_page_coverage_check(self):
        content = self._get_template()
        assert "coverage check" in content.lower() or "Page coverage" in content

    def test_has_download_save_commands(self):
        content = self._get_template()
        assert "deepaper download" in content
        assert "deepaper save" in content

    def test_has_auto_install(self):
        content = self._get_template()
        assert "pip install deepaper" in content
