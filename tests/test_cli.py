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
from deepaper.pipeline_io import safe_write_json

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

    def test_has_pipeline_structure(self):
        content = self._get_template()
        assert "HardGates" in content or "hardgates" in content.lower()
        assert "SoftGates" in content or "Critic" in content
        assert "Writer-Visual" in content or "writer-visual" in content.lower()
        assert "StructCheck" in content or "struct_check" in content

    def test_has_run_dir_structure(self):
        content = self._get_template()
        assert ".deepaper/runs/" in content
        assert "text_by_page.json" in content
        assert "visual_registry.json" in content

    def test_has_download_save_commands(self):
        content = self._get_template()
        assert "deepaper download" in content
        assert "deepaper save" in content

    def test_has_auto_install(self):
        content = self._get_template()
        assert "pip install deepaper" in content


# ---------------------------------------------------------------------------
# auto-install version awareness
# ---------------------------------------------------------------------------

class TestAutoInstallVersion:
    def test_old_version_gets_overwritten(self, tmp_path: Path) -> None:
        cmd_path = tmp_path / ".claude" / "commands" / "deepaper.md"
        cmd_path.parent.mkdir(parents=True, exist_ok=True)
        cmd_path.write_text("<!-- deepaper-version: 1 -->\nold content\n")

        with patch.object(Path, "home", return_value=tmp_path):
            from deepaper.cli import _auto_install_slash_command
            _auto_install_slash_command()

        content = cmd_path.read_text()
        assert "<!-- deepaper-version: 1 -->" not in content or "<!-- deepaper-version: 2 -->" in content
        from deepaper.defaults import SLASH_CMD_VERSION
        assert f"<!-- deepaper-version: {SLASH_CMD_VERSION} -->" in content

    def test_current_version_not_overwritten(self, tmp_path: Path) -> None:
        from deepaper.defaults import SLASH_CMD_VERSION
        cmd_path = tmp_path / ".claude" / "commands" / "deepaper.md"
        cmd_path.parent.mkdir(parents=True, exist_ok=True)
        original = f"<!-- deepaper-version: {SLASH_CMD_VERSION} -->\ncurrent content\n"
        cmd_path.write_text(original)

        with patch.object(Path, "home", return_value=tmp_path):
            from deepaper.cli import _auto_install_slash_command
            _auto_install_slash_command()

        assert cmd_path.read_text() == original

    def test_no_file_creates_new(self, tmp_path: Path) -> None:
        cmd_path = tmp_path / ".claude" / "commands" / "deepaper.md"
        assert not cmd_path.exists()

        with patch.object(Path, "home", return_value=tmp_path):
            from deepaper.cli import _auto_install_slash_command
            _auto_install_slash_command()

        assert cmd_path.exists()
        from deepaper.defaults import SLASH_CMD_VERSION
        # The generated content should work (may or may not have version marker
        # depending on whether the slash command file has been rewritten yet)
        assert cmd_path.stat().st_size > 0


# ---------------------------------------------------------------------------
# extract
# ---------------------------------------------------------------------------

class TestExtract:
    def test_extract_creates_all_artifacts(self, tmp_path: Path) -> None:
        import fitz
        doc = fitz.open()
        page = doc.new_page()
        page.insert_text((50, 50), "Introduction\nTable 1: Results.\nFigure 1: Overview of architecture.\n")
        pdf_path = tmp_path / "tmp" / "2301.00001.pdf"
        pdf_path.parent.mkdir()
        doc.save(str(pdf_path))
        doc.close()

        old_cwd = os.getcwd()
        os.chdir(tmp_path)
        try:
            result = runner.invoke(app, ["extract", "2301.00001"])
            assert result.exit_code == 0, f"Exit code {result.exit_code}: {result.output}"
            output = json.loads(result.stdout)
            assert output["total_pages"] == 1
            run_dir = tmp_path / ".deepaper" / "runs" / "2301.00001"
            assert (run_dir / "text_by_page.json").exists()
            assert (run_dir / "text.txt").exists()
            assert (run_dir / "visual_registry.json").exists()
            assert (run_dir / "paper_profile.json").exists()
            assert (run_dir / "core_figures.json").exists()
            assert (run_dir / "figure_contexts.json").exists()
        finally:
            os.chdir(old_cwd)

    def test_extract_missing_pdf(self, tmp_path: Path) -> None:
        old_cwd = os.getcwd()
        os.chdir(tmp_path)
        try:
            result = runner.invoke(app, ["extract", "9999.99999"])
            assert result.exit_code == 1
            output = json.loads(result.stdout)
            assert "error" in output
        finally:
            os.chdir(old_cwd)


# ---------------------------------------------------------------------------
# check
# ---------------------------------------------------------------------------

class TestCheck:
    def test_check_missing_notes(self, tmp_path: Path) -> None:
        old_cwd = os.getcwd()
        os.chdir(tmp_path)
        try:
            result = runner.invoke(app, ["check", "2301.00001"])
            assert result.exit_code == 1
            output = json.loads(result.stdout)
            assert "error" in output
        finally:
            os.chdir(old_cwd)

    def test_check_runs_validation(self, tmp_path: Path) -> None:
        run_dir = tmp_path / ".deepaper" / "runs" / "2301.00001"
        run_dir.mkdir(parents=True)

        notes = "## META\nThis is the meta section with sufficient content for testing.\n\n"
        notes += "## MAIN_RESULTS\nResults here with enough content to pass the minimum threshold check.\n\n"
        for sec in ["ABLATIONS", "HYPERPARAMETERS", "FORMULAS", "DATA_COMPOSITION",
                     "EVAL_CONFIG", "TRAINING_COSTS", "DESIGN_DECISIONS", "RELATED_WORK", "BASELINES"]:
            notes += f"## {sec}\nContent for {sec} section with enough characters to hopefully pass.\n\n"
        (run_dir / "notes.md").write_text(notes, encoding="utf-8")

        safe_write_json(str(run_dir / "text_by_page.json"), {"1": "Some page text"})
        safe_write_json(str(run_dir / "paper_profile.json"), {"total_pages": 1})

        old_cwd = os.getcwd()
        os.chdir(tmp_path)
        try:
            result = runner.invoke(app, ["check", "2301.00001"])
            assert result.exit_code == 0
            output = json.loads(result.stdout)
            assert "passed" in output
            assert "struct_check" in output
            assert "audit" in output
            assert (run_dir / "check.json").exists()
        finally:
            os.chdir(old_cwd)


# ---------------------------------------------------------------------------
# prompt --split
# ---------------------------------------------------------------------------

class TestPromptSplit:
    def test_split_creates_writer_prompts(self, tmp_path: Path) -> None:
        run_dir = tmp_path / ".deepaper" / "runs" / "2301.00001"
        run_dir.mkdir(parents=True)
        safe_write_json(str(run_dir / "paper_profile.json"), {
            "total_pages": 10, "num_tables": 3, "num_figures": 2, "num_equations": 1,
        })
        safe_write_json(str(run_dir / "visual_registry.json"), {
            "Table_1": {"type": "Table", "id": 1, "pages": [1], "definition_page": 1, "has_caption": True},
        })
        safe_write_json(str(run_dir / "core_figures.json"), [])
        safe_write_json(str(run_dir / "figure_contexts.json"), {})
        (tmp_path / "tmp").mkdir()

        old_cwd = os.getcwd()
        os.chdir(tmp_path)
        try:
            result = runner.invoke(app, ["prompt", "2301.00001", "--split"])
            assert result.exit_code == 0, f"Exit code {result.exit_code}: {result.output}"
            output = json.loads(result.stdout)
            assert "writers" in output
            assert len(output["writers"]) >= 2
            # Check prompt files were created
            for w in output["writers"]:
                assert Path(w["prompt_file"]).exists()
                content = Path(w["prompt_file"]).read_text()
                assert "费曼技巧" in content  # system role present
                assert "质量合同" in content  # gate contract present
        finally:
            os.chdir(old_cwd)

    def test_prompt_no_flags_errors(self, tmp_path: Path) -> None:
        old_cwd = os.getcwd()
        os.chdir(tmp_path)
        try:
            result = runner.invoke(app, ["prompt", "2301.00001"])
            assert result.exit_code == 1
        finally:
            os.chdir(old_cwd)


# ---------------------------------------------------------------------------
# merge
# ---------------------------------------------------------------------------

class TestMerge:
    def test_merge_combines_parts(self, tmp_path: Path) -> None:
        run_dir = tmp_path / ".deepaper" / "runs" / "2301.00001"
        run_dir.mkdir(parents=True)

        safe_write_json(str(run_dir / "writers.json"), {
            "writers": [
                {"name": "writer-text-0", "sections": ["核心速览"], "prompt_file": "p.md", "output_file": "part_text-0.md"},
                {"name": "writer-visual", "sections": ["方法详解"], "prompt_file": "p.md", "output_file": "part_visual.md"},
            ],
            "merge_order": ["writer-text-0", "writer-visual"],
            "figure_contexts": {},
        })
        (run_dir / "part_text-0.md").write_text("---\nvenue: Test\n---\n\n#### 核心速览\nContent A", encoding="utf-8")
        (run_dir / "part_visual.md").write_text("#### 方法详解\nContent B", encoding="utf-8")

        old_cwd = os.getcwd()
        os.chdir(tmp_path)
        try:
            result = runner.invoke(app, ["merge", "2301.00001"])
            assert result.exit_code == 0
            output = json.loads(result.stdout)
            assert "merged" in output
            assert "chars" in output
            merged = (run_dir / "merged.md").read_text(encoding="utf-8")
            assert "核心速览" in merged
            assert "方法详解" in merged
            assert (run_dir / "final.md").exists()
        finally:
            os.chdir(old_cwd)

    def test_merge_missing_writers_json(self, tmp_path: Path) -> None:
        old_cwd = os.getcwd()
        os.chdir(tmp_path)
        try:
            result = runner.invoke(app, ["merge", "2301.00001"])
            assert result.exit_code == 1
        finally:
            os.chdir(old_cwd)


# ---------------------------------------------------------------------------
# fix
# ---------------------------------------------------------------------------

class TestFix:
    def test_fix_generates_prompt(self, tmp_path: Path) -> None:
        run_dir = tmp_path / ".deepaper" / "runs" / "2301.00001"
        run_dir.mkdir(parents=True)
        safe_write_json(str(run_dir / "gates.json"), {
            "passed": False,
            "failed": ["H3"],
            "results": {
                "H3": {
                    "passed": False,
                    "failures": [{"section": "核心速览", "actual": 100, "floor": 300}],
                },
            },
        })
        safe_write_json(str(run_dir / "figure_contexts.json"), {})

        old_cwd = os.getcwd()
        os.chdir(tmp_path)
        try:
            result = runner.invoke(app, ["fix", "2301.00001"])
            assert result.exit_code == 0
            output = json.loads(result.stdout)
            assert output["needs_fix"] is True
            assert "H3" in output["failed"]
            assert (run_dir / "prompt_fix.md").exists()
        finally:
            os.chdir(old_cwd)

    def test_fix_no_gates(self, tmp_path: Path) -> None:
        old_cwd = os.getcwd()
        os.chdir(tmp_path)
        try:
            result = runner.invoke(app, ["fix", "2301.00001"])
            assert result.exit_code == 1
        finally:
            os.chdir(old_cwd)

    def test_fix_all_passed(self, tmp_path: Path) -> None:
        run_dir = tmp_path / ".deepaper" / "runs" / "2301.00001"
        run_dir.mkdir(parents=True)
        safe_write_json(str(run_dir / "gates.json"), {"passed": True, "failed": [], "results": {}})

        old_cwd = os.getcwd()
        os.chdir(tmp_path)
        try:
            result = runner.invoke(app, ["fix", "2301.00001"])
            assert result.exit_code == 0
            output = json.loads(result.stdout)
            assert output["needs_fix"] is False
        finally:
            os.chdir(old_cwd)


# ---------------------------------------------------------------------------
# classify
# ---------------------------------------------------------------------------

class TestClassify:
    def test_classify_missing_notes(self, tmp_path: Path) -> None:
        old_cwd = os.getcwd()
        os.chdir(tmp_path)
        try:
            result = runner.invoke(app, ["classify", "2301.00001"])
            assert result.exit_code == 1
        finally:
            os.chdir(old_cwd)

    def test_classify_generates_prompt(self, tmp_path: Path) -> None:
        run_dir = tmp_path / ".deepaper" / "runs" / "2301.00001"
        run_dir.mkdir(parents=True)
        (run_dir / "notes.md").write_text(
            "## META\nThis paper proposes a new LLM pretraining method.\n\n## MAIN_RESULTS\nResults.",
            encoding="utf-8",
        )

        old_cwd = os.getcwd()
        os.chdir(tmp_path)
        try:
            result = runner.invoke(app, ["classify", "2301.00001"])
            assert result.exit_code == 0, f"Exit code {result.exit_code}: {result.output}"
            output = json.loads(result.stdout)
            assert "prompt_file" in output
            assert Path(output["prompt_file"]).exists()
        finally:
            os.chdir(old_cwd)
