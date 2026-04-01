"""Tests for HardGates programmatic quality checks (H1-H8)."""

import pytest


# ===========================================================================
# TestH1BaselinesFormat
# ===========================================================================

class TestH1BaselinesFormat:
    """H1: YAML frontmatter has baselines list with >= 2 entries."""

    def test_valid_baselines(self):
        from deepaper.gates import check_baselines_format

        md = (
            "---\n"
            "title: Test Paper\n"
            "baselines:\n"
            "  - ModelA\n"
            "  - ModelB\n"
            "  - ModelC\n"
            "tldr: A new method achieves 95.2% accuracy.\n"
            "---\n"
            "#### Some content\n"
        )
        result = check_baselines_format(md)
        assert result["passed"] is True
        assert result["count"] >= 2

    def test_missing_baselines(self):
        from deepaper.gates import check_baselines_format

        md = (
            "---\n"
            "title: Test Paper\n"
            "tldr: A new method.\n"
            "---\n"
            "#### Some content\n"
        )
        result = check_baselines_format(md)
        assert result["passed"] is False
        assert "reason" in result


# ===========================================================================
# TestH2Coverage
# ===========================================================================

class TestH2Coverage:
    """H2: Coverage >= 60% of structural elements."""

    def test_good_coverage(self):
        from deepaper.gates import check_structural_coverage

        # Merged markdown that mentions equation (1), (2), Table 1
        merged = (
            "#### Method\n"
            "We use equation (1) and (2).\n"
            "Table 1: Results are great.\n"
            "3.1 Our Approach\n"
            "3.2 Training Details\n"
        )
        checklist = {
            "equation:1": {"source": "equation", "match_pattern": r"\(1\)"},
            "equation:2": {"source": "equation", "match_pattern": r"\(2\)"},
            "table:Table_1": {"source": "table_caption", "match_pattern": r"Table\s+1\s*:"},
            "subsection:3.1 Our Approach": {"source": "subsection_heading", "match_text": "3.1 Our Approach"},
            "subsection:3.2 Training Details": {"source": "subsection_heading", "match_text": "3.2 Training Details"},
        }
        result = check_structural_coverage(merged, checklist)
        assert result["passed"] is True
        assert result["coverage"] >= 0.6

    def test_low_coverage(self):
        from deepaper.gates import check_structural_coverage

        merged = "#### Method\nSome text without any references.\n"
        checklist = {
            "equation:1": {"source": "equation", "match_pattern": r"\(1\)"},
            "equation:2": {"source": "equation", "match_pattern": r"\(2\)"},
            "equation:3": {"source": "equation", "match_pattern": r"\(3\)"},
            "table:Table_1": {"source": "table_caption", "match_pattern": r"Table\s+1\s*:"},
            "table:Table_2": {"source": "table_caption", "match_pattern": r"Table\s+2\s*:"},
        }
        result = check_structural_coverage(merged, checklist)
        assert result["passed"] is False
        assert result["coverage"] < 0.6
        assert len(result["missing"]) > 0

    def test_empty_checklist_passes(self):
        from deepaper.gates import check_structural_coverage

        merged = "#### Method\nSome content.\n"
        result = check_structural_coverage(merged, {})
        assert result["passed"] is True


# ===========================================================================
# TestH3CharFloors
# ===========================================================================

class TestH3CharFloors:
    """H3: Each h4 section meets minimum char floor."""

    def test_passes_when_sufficient(self):
        from deepaper.gates import check_char_floors

        md = (
            "---\ntitle: Test\n---\n"
            "#### 方法详解\n" + ("详" * 2100) + "\n"
            "#### 实验与归因\n" + ("实" * 1600) + "\n"
            "#### 核心速览\n" + ("核" * 600) + "\n"
            "#### 动机与第一性原理\n" + ("动" * 900) + "\n"
            "#### 专家批判\n" + ("专" * 900) + "\n"
            "#### 机制迁移分析\n" + ("机" * 900) + "\n"
            "#### 背景知识补充\n" + ("背" * 400) + "\n"
        )
        result = check_char_floors(md)
        assert result["passed"] is True
        assert result["failures"] == []

    def test_fails_when_degenerate(self):
        from deepaper.gates import check_char_floors

        md = (
            "---\ntitle: Test\n---\n"
            "#### 方法详解\nshort\n"
            "#### 实验与归因\nshort\n"
            "#### 核心速览\nshort\n"
        )
        result = check_char_floors(md)
        assert result["passed"] is False
        assert len(result["failures"]) > 0


# ===========================================================================
# TestH5TldrNumbers
# ===========================================================================

class TestH5TldrNumbers:
    """H5: TL;DR in YAML frontmatter contains >= 2 numbers."""

    def test_enough_numbers(self):
        from deepaper.gates import check_tldr_numbers

        md = (
            "---\n"
            "title: Test\n"
            "tldr: Achieves 95.2% accuracy and 3x speedup on ImageNet.\n"
            "---\n"
            "#### Content\n"
        )
        result = check_tldr_numbers(md)
        assert result["passed"] is True
        assert result["count"] >= 2

    def test_too_few_numbers(self):
        from deepaper.gates import check_tldr_numbers

        md = (
            "---\n"
            "title: Test\n"
            "tldr: A new method for better results.\n"
            "---\n"
            "#### Content\n"
        )
        result = check_tldr_numbers(md)
        assert result["passed"] is False
        assert result["count"] < 2


# ===========================================================================
# TestH6HeadingLevels
# ===========================================================================

class TestH6HeadingLevels:
    """H6: Body only uses h4/h5/h6. Reject h1/h2/h3/h7+."""

    def test_valid_h4_h5_h6(self):
        from deepaper.gates import check_heading_levels

        md = (
            "---\ntitle: Test\n---\n"
            "#### Section One\n"
            "Some content.\n"
            "##### Subsection\n"
            "More content.\n"
            "###### Detail\n"
            "Even more.\n"
        )
        result = check_heading_levels(md)
        assert result["passed"] is True
        assert result["violations"] == []

    def test_rejects_h1(self):
        from deepaper.gates import check_heading_levels

        md = (
            "---\ntitle: Test\n---\n"
            "# Top Level Bad\n"
            "#### Good Section\n"
        )
        result = check_heading_levels(md)
        assert result["passed"] is False
        assert len(result["violations"]) > 0

    def test_rejects_h2(self):
        from deepaper.gates import check_heading_levels

        md = (
            "---\ntitle: Test\n---\n"
            "## Second Level Bad\n"
            "#### Good Section\n"
        )
        result = check_heading_levels(md)
        assert result["passed"] is False
        assert len(result["violations"]) > 0


# ===========================================================================
# TestH8NumberFingerprint
# ===========================================================================

class TestH8NumberFingerprint:
    """H8: Number fingerprint cross-validation."""

    def test_traceable_numbers(self):
        from deepaper.gates import check_number_fingerprint

        # Source pages contain Table 1 definition with numbers
        text_by_page = {
            3: (
                "Table 1: Results\n"
                "Model A achieved 95.2 accuracy.\n"
                "Model B achieved 87.3 accuracy.\n"
                "Improvement of 7.9 points.\n"
            ),
        }
        registry = {
            "Table_1": {
                "type": "Table",
                "id": 1,
                "pages": [3],
                "definition_page": 3,
                "has_caption": True,
            },
        }
        # Writer markdown references these same numbers
        md = (
            "---\ntitle: Test\n---\n"
            "#### Results\n"
            "| Model | Accuracy |\n"
            "| --- | --- |\n"
            "| A | 95.2 |\n"
            "| B | 87.3 |\n"
        )
        result = check_number_fingerprint(md, text_by_page, registry)
        assert result["passed"] is True

    def test_fabricated_numbers(self):
        from deepaper.gates import check_number_fingerprint

        # Source pages contain different numbers
        text_by_page = {
            3: (
                "Table 1: Results\n"
                "Model A achieved 50.0 accuracy.\n"
                "Model B achieved 40.0 accuracy.\n"
            ),
        }
        registry = {
            "Table_1": {
                "type": "Table",
                "id": 1,
                "pages": [3],
                "definition_page": 3,
                "has_caption": True,
            },
        }
        # Writer markdown has completely different numbers
        md = (
            "---\ntitle: Test\n---\n"
            "#### Results\n"
            "| Model | Accuracy |\n"
            "| --- | --- |\n"
            "| A | 99.9 |\n"
            "| B | 98.7 |\n"
            "| C | 97.5 |\n"
            "| D | 96.3 |\n"
        )
        result = check_number_fingerprint(md, text_by_page, registry)
        assert result["passed"] is False


# ===========================================================================
# TestRunHardGates
# ===========================================================================

class TestRunHardGates:
    """Orchestrator: run_hard_gates."""

    def test_skips_gates_when_data_unavailable(self):
        from deepaper.gates import run_hard_gates

        md = (
            "---\n"
            "title: Test\n"
            "baselines:\n"
            "  - A\n"
            "  - B\n"
            "tldr: Achieves 95.2% accuracy and 3x speedup.\n"
            "---\n"
            "#### 核心速览\n" + ("核" * 600) + "\n"
            "#### 方法详解\n" + ("方" * 2100) + "\n"
            "#### 实验与归因\n" + ("实" * 1600) + "\n"
            "#### 动机与第一性原理\n" + ("动" * 900) + "\n"
            "#### 专家批判\n" + ("专" * 900) + "\n"
            "#### 机制迁移分析\n" + ("机" * 900) + "\n"
            "#### 背景知识补充\n" + ("背" * 400) + "\n"
        )
        result = run_hard_gates(
            merged_md=md,
            coverage_checklist={},
            core_figures=[],
            text_by_page=None,
            registry=None,
        )
        # H4, H7, H8 should be skipped
        assert result["results"]["H4"]["skipped"] is True
        assert result["results"]["H7"]["skipped"] is True
        assert result["results"]["H8"]["skipped"] is True
        # Skipped gates still count as passed
        assert result["results"]["H4"]["passed"] is True
        assert result["results"]["H7"]["passed"] is True
        assert result["results"]["H8"]["passed"] is True
