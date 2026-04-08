"""Tests for visual registry, core figure detection, and paper profiling."""

import pytest


# ---------------------------------------------------------------------------
# Helpers to build sample text_by_page dicts
# ---------------------------------------------------------------------------

def _simple_text_by_page():
    """Paper with 10 pages, tables, figures, sections."""
    return {
        1: (
            "Introduction\n"
            "We study deep learning. See Table 1 and Figure 1.\n"
            "Table 1: Comparison of baselines on CIFAR-10 dataset with various methods.\n"
            "Figure 1: Overview of the proposed architecture showing all major components in detail clearly.\n"
        ),
        2: (
            "Related Work\n"
            "Prior approaches use Fig. 2 for illustration.\n"
            "Fig. 2: Visualization of the attention mechanism across multiple transformer layers in detail.\n"
            "As shown in Table 1, our method outperforms baselines.\n"
        ),
        3: (
            "Method\n"
            "Our method is described below. See Figure 1 for details.\n"
            "We also reference Table 2.\n"
            "Table 2: Hyperparameter settings used in all experiments across datasets.\n"
        ),
        4: (
            "Experiments\n"
            "Results are in Table 3.\n"
            "Table 3: Main results on ImageNet showing improvements over all previous state of the art methods.\n"
            "Figure 1 shows the pipeline clearly and comprehensively.\n"
        ),
        5: (
            "We also present Figure 3.\n"
            "Figure 3: Ablation study results.\n"
            "As seen in Figure 1, the architecture is modular.\n"
        ),
        6: "More analysis follows. Table 3 confirms the trend.\n",
        7: "Discussion of results continues here.\n",
        8: "Additional experiments and analysis.\n",
        9: "Conclusion\nWe presented a novel approach.\n",
        10: "References\n[1] Some reference.\n",
    }


# ===========================================================================
# TestBuildVisualRegistry
# ===========================================================================

class TestBuildVisualRegistry:
    """Tests for build_visual_registry."""

    def test_detects_tables_and_figures(self):
        from deepaper.registry import build_visual_registry
        text = _simple_text_by_page()
        reg = build_visual_registry(text)
        assert "Table_1" in reg
        assert "Table_2" in reg
        assert "Table_3" in reg
        assert "Figure_1" in reg
        assert reg["Table_1"]["type"] == "Table"
        assert reg["Figure_1"]["type"] == "Figure"

    def test_fig_dot_normalized_to_figure(self):
        from deepaper.registry import build_visual_registry
        text = {
            1: "See Fig. 5 and Fig 3 in the results section.\n"
                "Fig. 5: Some caption for figure five with enough detail.\n"
                "Fig 3: Another caption text.\n",
        }
        reg = build_visual_registry(text)
        # Both should be normalized to "Figure"
        assert "Figure_5" in reg
        assert "Figure_3" in reg
        assert reg["Figure_5"]["type"] == "Figure"
        assert reg["Figure_3"]["type"] == "Figure"

    def test_reference_without_caption(self):
        from deepaper.registry import build_visual_registry
        text = {
            1: "As shown in Table 7, our method wins.\n",
        }
        reg = build_visual_registry(text)
        assert "Table_7" in reg
        assert reg["Table_7"]["has_caption"] is False

    def test_empty_input(self):
        from deepaper.registry import build_visual_registry
        reg = build_visual_registry({})
        assert reg == {}

    def test_numbering_gap_detected(self):
        from deepaper.registry import build_visual_registry, verify_registry_completeness
        text = {
            1: "Table 1: First table caption.\nTable 3: Third table caption.\n",
        }
        reg = build_visual_registry(text)
        issues = verify_registry_completeness(reg)
        # Should flag that Table 2 is missing
        assert any("Table" in i and "2" in i for i in issues)


# ===========================================================================
# TestCoreFigures
# ===========================================================================

class TestCoreFigures:
    """Tests for identify_core_figures and extract_figure_contexts."""

    def test_identifies_core_figure(self):
        from deepaper.registry import build_visual_registry, identify_core_figures
        text = _simple_text_by_page()
        reg = build_visual_registry(text)
        cores = identify_core_figures(reg, text, total_pages=10)
        # Figure 1 is referenced many times, in intro, early, id<=2 => high score
        assert len(cores) >= 1
        keys = [c["key"] for c in cores]
        assert "Figure_1" in keys

    def test_max_budget_respected(self):
        from deepaper.registry import build_visual_registry, identify_core_figures
        # Create a paper with many figures all heavily referenced
        text = {}
        for p in range(1, 21):
            lines = []
            for fig_id in range(1, 8):
                lines.append(f"See Figure {fig_id} here.")
            if p <= 4:
                lines.append(f"Figure {p}: Caption for figure {p} that is long enough to pass the eighty character threshold definitely.")
            text[p] = "\n".join(lines) + "\n"
        reg = build_visual_registry(text)
        cores = identify_core_figures(reg, text, total_pages=20)
        # MAX_CORE = 3
        assert len(cores) <= 3

    def test_no_figures(self):
        from deepaper.registry import build_visual_registry, identify_core_figures
        text = {1: "No visual elements here.\n"}
        reg = build_visual_registry(text)
        cores = identify_core_figures(reg, text, total_pages=1)
        assert cores == []

    def test_extract_figure_contexts(self):
        from deepaper.registry import (
            build_visual_registry,
            identify_core_figures,
            extract_figure_contexts,
        )
        text = _simple_text_by_page()
        reg = build_visual_registry(text)
        cores = identify_core_figures(reg, text, total_pages=10)
        contexts = extract_figure_contexts(text, cores)
        # Figure 1 should be in contexts
        assert "Figure_1" in contexts
        ctx = contexts["Figure_1"]
        # Should have caption text
        assert "caption" in ctx
        assert len(ctx["caption"]) > 0
        # Should have referencing paragraphs
        assert "references" in ctx
        assert len(ctx["references"]) >= 1


# ===========================================================================
# TestPaperProfile
# ===========================================================================

class TestPaperProfile:
    """Tests for compute_paper_profile."""

    def test_basic_profile(self):
        from deepaper.registry import build_visual_registry, compute_paper_profile
        text = _simple_text_by_page()
        reg = build_visual_registry(text)
        profile = compute_paper_profile(text, reg)
        assert profile["total_pages"] == 10
        assert profile["total_chars"] > 0
        assert profile["num_tables"] >= 3
        assert profile["num_figures"] >= 1

    def test_empty_input(self):
        from deepaper.registry import compute_paper_profile
        profile = compute_paper_profile({}, {})
        assert profile["total_pages"] == 0
        assert profile["total_chars"] == 0
        assert profile["num_tables"] == 0
        assert profile["num_figures"] == 0

    def test_section_detection(self):
        from deepaper.registry import build_visual_registry, compute_paper_profile
        text = _simple_text_by_page()
        reg = build_visual_registry(text)
        profile = compute_paper_profile(text, reg)
        section_chars = profile["section_chars"]
        # Should detect Introduction, Method, Experiments at minimum
        assert "Introduction" in section_chars
        assert "Method" in section_chars
        assert "Experiments" in section_chars


# ===========================================================================
# TestCoreTables
# ===========================================================================

class TestCoreTables:
    """Tests for identify_core_tables."""

    def test_identifies_core_tables(self):
        from deepaper.registry import build_visual_registry, identify_core_tables
        text = _simple_text_by_page()
        reg = build_visual_registry(text)
        cores = identify_core_tables(reg, text, total_pages=10)
        assert len(cores) >= 1
        keys = [c["key"] for c in cores]
        assert "Table_1" in keys or "Table_3" in keys

    def test_max_core_cap(self):
        from deepaper.registry import build_visual_registry, identify_core_tables
        text = {}
        for p in range(1, 21):
            lines = []
            for t in range(1, 31):
                lines.append(f"See Table {t} here.")
            if p <= 10:
                lines.append(f"Table {p}: Caption for table {p} with sufficient detail to pass threshold.")
            text[p] = "\n".join(lines) + "\n"
        reg = build_visual_registry(text)
        cores = identify_core_tables(reg, text, total_pages=20)
        assert len(cores) <= 8
        assert len(cores) >= 3

    def test_no_tables(self):
        from deepaper.registry import build_visual_registry, identify_core_tables
        text = {1: "No tables here.\n"}
        reg = build_visual_registry(text)
        cores = identify_core_tables(reg, text, total_pages=1)
        assert cores == []

    def test_scoring_prefers_early_referenced_tables(self):
        from deepaper.registry import build_visual_registry, identify_core_tables
        text = {
            1: "Table 1: Main results with detailed caption explaining everything.\nSee Table 1.\n",
            2: "We also reference Table 1 again here.\n",
            3: "Table 1 is important. See Table 1 for proof.\n",
            9: "Table 5: Appendix table.\n",
            10: "See Table 5.\n",
        }
        reg = build_visual_registry(text)
        cores = identify_core_tables(reg, text, total_pages=10)
        if len(cores) >= 2:
            assert cores[0]["key"] == "Table_1"


# ===========================================================================
# TestCoverageChecklist
# ===========================================================================

class TestCoverageChecklist:
    """Tests for build_coverage_checklist."""

    def test_builds_from_registry(self):
        from deepaper.registry import (
            build_visual_registry,
            compute_paper_profile,
            identify_core_figures,
            build_coverage_checklist,
        )
        text = _simple_text_by_page()
        reg = build_visual_registry(text)
        profile = compute_paper_profile(text, reg)
        cores = identify_core_figures(reg, text, total_pages=10)
        checklist = build_coverage_checklist(
            text, reg, profile.get("subsection_headings", [])
        )
        # Should have some entries
        assert len(checklist) > 0
        # Each entry should have source and either match_pattern or match_text
        for key, entry in checklist.items():
            assert "source" in entry
            assert "match_pattern" in entry or "match_text" in entry

    def test_empty_inputs(self):
        from deepaper.registry import build_coverage_checklist
        checklist = build_coverage_checklist({}, {}, [])
        assert checklist == {} or len(checklist) == 0


# ===========================================================================
# TestSubsectionHeadingFilter
# ===========================================================================

class TestSubsectionHeadingFilter:
    """Subsection detection must not match table row labels."""

    def test_legitimate_subsection_detected(self):
        from deepaper.registry import compute_paper_profile
        text_by_page = {
            1: "intro",
            2: "3.1 Main Results for Olmo 3 Base\nSome body text here.\n"
               "3.2 Modeling and Architecture\nMore body text.\n",
        }
        registry = {}
        profile = compute_paper_profile(text_by_page, registry)
        headings = profile["subsection_headings"]
        assert any("Main Results for Olmo 3 Base" in h for h in headings)
        assert any("Modeling and Architecture" in h for h in headings)

    def test_table_row_labels_filtered(self):
        from deepaper.registry import compute_paper_profile
        text_by_page = {
            1: "2.3 HarmBench\n"
               "1.0 Bits-per-byte\n"
               "14.5 GPQA\n"
               "3.1 Our Real Section Name Here\n",
        }
        registry = {}
        profile = compute_paper_profile(text_by_page, registry)
        headings = profile["subsection_headings"]
        # Only the multi-word section name should be detected
        assert any("Our Real Section Name Here" in h for h in headings)
        # Single-word table labels should be filtered
        assert not any("HarmBench" in h and len(h.split()) <= 2 for h in headings)
        assert not any("Bits-per-byte" in h and len(h.split()) <= 2 for h in headings)
        assert not any("GPQA" in h and len(h.split()) <= 2 for h in headings)
