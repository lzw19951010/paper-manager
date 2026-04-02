"""Tests for prompt_builder: template parsing, auto-split."""
import pytest


class TestParseTemplateSections:
    def test_extracts_all_seven_sections(self):
        from deepaper.prompt_builder import parse_template_sections
        from deepaper.defaults import DEFAULT_TEMPLATE

        sections = parse_template_sections(DEFAULT_TEMPLATE)
        expected_keys = [
            "核心速览",
            "动机与第一性原理",
            "方法详解",
            "实验与归因",
            "专家批判",
            "机制迁移分析",
            "背景知识补充",
        ]
        for key in expected_keys:
            assert key in sections, f"Missing section: {key}"
            assert len(sections[key]) > 50, f"Section {key} too short: {len(sections[key])}"

    def test_sections_contain_key_markers(self):
        from deepaper.prompt_builder import parse_template_sections
        from deepaper.defaults import DEFAULT_TEMPLATE

        sections = parse_template_sections(DEFAULT_TEMPLATE)
        assert "TL;DR" in sections["核心速览"]
        assert "一图流" in sections["核心速览"]
        assert "Because" in sections["动机与第一性原理"]
        assert "数值推演" in sections["方法详解"]
        assert "伪代码" in sections["方法详解"]
        assert "易混淆点" in sections["方法详解"]
        assert "归因分析" in sections["实验与归因"]
        assert "隐性成本" in sections["专家批判"]
        assert "机制解耦" in sections["机制迁移分析"]
        assert "迁移处方" in sections["机制迁移分析"]


class TestExtractSystemRole:
    def test_extract_system_role(self):
        from deepaper.prompt_builder import extract_system_role
        from deepaper.defaults import DEFAULT_TEMPLATE

        role = extract_system_role(DEFAULT_TEMPLATE)
        assert "费曼技巧" in role
        assert "算法专家" in role


class TestExtractFrontmatterSpec:
    def test_extracts_frontmatter_section(self):
        from deepaper.prompt_builder import extract_frontmatter_spec
        from deepaper.defaults import DEFAULT_TEMPLATE

        spec = extract_frontmatter_spec(DEFAULT_TEMPLATE)
        assert "venue" in spec
        assert "baselines" in spec
        assert "datasets" in spec
        assert "metrics" in spec
        assert "tldr" in spec


class TestAutoSplit:
    def _profile(self, pages=10, tables=3, figures=4, equations=2):
        return {
            "total_pages": pages,
            "num_tables": tables,
            "num_figures": figures,
            "num_equations": equations,
        }

    def test_short_paper_two_writers(self):
        from deepaper.prompt_builder import auto_split
        tasks = auto_split(self._profile(pages=8, tables=3, figures=2, equations=1))
        assert len(tasks) == 2
        assert tasks[0].name == "writer-visual"
        assert set(tasks[0].sections) == {"方法详解", "实验与归因"}
        text_sections = set()
        for t in tasks[1:]:
            text_sections.update(t.sections)
        assert "核心速览" in text_sections
        assert "机制迁移分析" in text_sections

    def test_long_paper_three_writers(self):
        from deepaper.prompt_builder import auto_split
        tasks = auto_split(self._profile(pages=120, tables=20, figures=22, equations=10))
        assert len(tasks) == 3
        assert tasks[0].name == "writer-visual"

    def test_visual_sections_always_together(self):
        from deepaper.prompt_builder import auto_split
        for pages in [8, 30, 120]:
            tasks = auto_split(self._profile(pages=pages))
            visual = tasks[0]
            assert visual.name == "writer-visual"
            assert "方法详解" in visual.sections
            assert "实验与归因" in visual.sections

    def test_all_sections_covered(self):
        from deepaper.prompt_builder import auto_split, SECTION_ORDER
        tasks = auto_split(self._profile(pages=50))
        all_sections = set()
        for t in tasks:
            all_sections.update(t.sections)
        assert all_sections == set(SECTION_ORDER)
