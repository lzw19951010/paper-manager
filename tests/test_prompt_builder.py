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


class TestGatesToConstraints:
    def test_char_floor_in_constraints(self):
        from deepaper.prompt_builder import gates_to_constraints
        constraints = gates_to_constraints(
            sections=["方法详解", "实验与归因"],
            profile={"total_pages": 10, "num_tables": 5, "num_equations": 3},
            registry={"Table_1": {"type": "Table"}, "Table_2": {"type": "Table"}},
            core_figures=[{"id": 1, "key": "Figure_1"}],
        )
        assert "方法详解" in constraints
        assert "1,500" in constraints  # floor value
        assert "Figure 1" in constraints  # H7
        assert "h1/h2/h3" in constraints  # H6

    def test_tldr_constraint_for_executive_summary(self):
        from deepaper.prompt_builder import gates_to_constraints
        constraints = gates_to_constraints(
            sections=["核心速览", "动机与第一性原理"],
            profile={"total_pages": 10},
            registry={},
            core_figures=[],
        )
        assert "TL;DR" in constraints
        assert "≥2" in constraints or ">=2" in constraints

    def test_content_markers_for_methodology(self):
        from deepaper.prompt_builder import gates_to_constraints
        constraints = gates_to_constraints(
            sections=["方法详解"],
            profile={"total_pages": 10},
            registry={},
            core_figures=[],
        )
        assert "数值推演" in constraints
        assert "伪代码" in constraints
        assert "易混淆点" in constraints

    def test_table_count_for_experiments(self):
        from deepaper.prompt_builder import gates_to_constraints
        registry = {f"Table_{i}": {"type": "Table"} for i in range(1, 8)}
        constraints = gates_to_constraints(
            sections=["方法详解", "实验与归因"],
            profile={"total_pages": 30, "num_tables": 7},
            registry=registry,
            core_figures=[],
        )
        assert "6" in constraints  # min(7, 6)
        assert "表格" in constraints


class TestGenerateWriterPrompt:
    def test_prompt_contains_system_role(self):
        from deepaper.prompt_builder import (
            generate_writer_prompt, WriterTask, parse_template_sections,
            extract_system_role,
        )
        from deepaper.defaults import DEFAULT_TEMPLATE

        task = WriterTask(name="writer-text-0", sections=["核心速览"])
        prompt = generate_writer_prompt(
            task=task,
            run_dir="/tmp/test",
            template_sections=parse_template_sections(DEFAULT_TEMPLATE),
            system_role=extract_system_role(DEFAULT_TEMPLATE),
            figure_contexts={},
            constraints="- test constraint",
            pdf_path="",
            table_def_pages=[],
        )
        assert "费曼技巧" in prompt
        assert "算法专家" in prompt

    def test_prompt_contains_template_text_verbatim(self):
        from deepaper.prompt_builder import (
            generate_writer_prompt, WriterTask, parse_template_sections,
            extract_system_role,
        )
        from deepaper.defaults import DEFAULT_TEMPLATE

        sections = parse_template_sections(DEFAULT_TEMPLATE)
        task = WriterTask(name="writer-visual", sections=["方法详解"], needs_pdf_pages=True)
        prompt = generate_writer_prompt(
            task=task,
            run_dir="/tmp/test",
            template_sections=sections,
            system_role=extract_system_role(DEFAULT_TEMPLATE),
            figure_contexts={},
            constraints="",
            pdf_path="/tmp/test.pdf",
            table_def_pages=[7, 9],
        )
        assert "数值推演" in prompt
        assert "【必做】" in prompt
        assert "伪代码" in prompt
        assert "易混淆点" in prompt

    def test_prompt_contains_figure_contexts(self):
        from deepaper.prompt_builder import (
            generate_writer_prompt, WriterTask, parse_template_sections,
            extract_system_role,
        )
        from deepaper.defaults import DEFAULT_TEMPLATE

        fig_ctx = {"Figure_1": {"caption": "Test caption", "references": ["ref1"]}}
        task = WriterTask(name="writer-text-0", sections=["核心速览"])
        prompt = generate_writer_prompt(
            task=task,
            run_dir="/tmp/test",
            template_sections=parse_template_sections(DEFAULT_TEMPLATE),
            system_role=extract_system_role(DEFAULT_TEMPLATE),
            figure_contexts=fig_ctx,
            constraints="",
            pdf_path="",
            table_def_pages=[],
        )
        assert "Test caption" in prompt
        assert "灵魂图" in prompt

    def test_visual_writer_gets_pdf_pages(self):
        from deepaper.prompt_builder import (
            generate_writer_prompt, WriterTask, parse_template_sections,
            extract_system_role,
        )
        from deepaper.defaults import DEFAULT_TEMPLATE

        task = WriterTask(name="writer-visual", sections=["方法详解"], needs_pdf_pages=True)
        prompt = generate_writer_prompt(
            task=task,
            run_dir="/tmp/test",
            template_sections=parse_template_sections(DEFAULT_TEMPLATE),
            system_role=extract_system_role(DEFAULT_TEMPLATE),
            figure_contexts={},
            constraints="",
            pdf_path="/tmp/paper.pdf",
            table_def_pages=[7, 9, 10],
        )
        assert "/tmp/paper.pdf" in prompt
        assert "[7, 9, 10]" in prompt

    def test_text_writer_no_pdf_pages(self):
        from deepaper.prompt_builder import (
            generate_writer_prompt, WriterTask, parse_template_sections,
            extract_system_role,
        )
        from deepaper.defaults import DEFAULT_TEMPLATE

        task = WriterTask(name="writer-text-0", sections=["核心速览"])
        prompt = generate_writer_prompt(
            task=task,
            run_dir="/tmp/test",
            template_sections=parse_template_sections(DEFAULT_TEMPLATE),
            system_role=extract_system_role(DEFAULT_TEMPLATE),
            figure_contexts={},
            constraints="",
            pdf_path="/tmp/paper.pdf",
            table_def_pages=[7, 9],
        )
        assert "PDF" not in prompt or "paper.pdf" not in prompt


class TestWriterTypeConstraints:
    """gates_to_constraints should inject different clauses for visual vs text writers."""

    def test_visual_writer_gets_flowchart_constraint(self):
        from deepaper.prompt_builder import gates_to_constraints
        constraints = gates_to_constraints(
            sections=["方法详解", "实验与归因"],
            profile={"total_pages": 10, "num_tables": 5, "num_equations": 3},
            registry={"Table_1": {"type": "Table"}, "Table_2": {"type": "Table"}},
            core_figures=[{"id": 1, "key": "Figure_1"}],
        )
        assert "数据流图" in constraints
        assert "≥3" in constraints or "3 个" in constraints

    def test_visual_writer_gets_figure_density_constraint(self):
        from deepaper.prompt_builder import gates_to_constraints
        constraints = gates_to_constraints(
            sections=["方法详解", "实验与归因"],
            profile={"total_pages": 10},
            registry={},
            core_figures=[{"id": 1, "key": "Figure_1"}, {"id": 3, "key": "Figure_3"}],
        )
        assert "至少出现 2 次" in constraints

    def test_text_writer_gets_metaphor_constraint(self):
        from deepaper.prompt_builder import gates_to_constraints
        constraints = gates_to_constraints(
            sections=["核心速览", "动机与第一性原理"],
            profile={"total_pages": 10},
            registry={},
            core_figures=[],
        )
        assert "比喻" in constraints

    def test_text_writer_gets_simple_example_constraint(self):
        from deepaper.prompt_builder import gates_to_constraints
        constraints = gates_to_constraints(
            sections=["核心速览", "动机与第一性原理", "方法详解"],
            profile={"total_pages": 10},
            registry={},
            core_figures=[],
        )
        assert "简化示例" in constraints

    def test_incremental_annotation_for_experiments(self):
        from deepaper.prompt_builder import gates_to_constraints
        constraints = gates_to_constraints(
            sections=["方法详解", "实验与归因"],
            profile={"total_pages": 10, "num_tables": 3},
            registry={"Table_1": {"type": "Table"}},
            core_figures=[],
        )
        assert "95.9(+0.3)" in constraints or "增量" in constraints


class TestTemplateEnhancements:
    """Verify DEFAULT_TEMPLATE contains new content and formatting guidance."""

    def test_simple_example_guidance(self):
        from deepaper.defaults import DEFAULT_TEMPLATE
        assert "1000篇文档" in DEFAULT_TEMPLATE
        assert "手指头跟着算" in DEFAULT_TEMPLATE

    def test_metaphor_guidance(self):
        from deepaper.defaults import DEFAULT_TEMPLATE
        assert "鸡尾酒调配" in DEFAULT_TEMPLATE
        assert "精准映射到技术机制" in DEFAULT_TEMPLATE

    def test_section_separator_guidance(self):
        from deepaper.defaults import DEFAULT_TEMPLATE
        assert "水平线分隔" in DEFAULT_TEMPLATE

    def test_bullet_format_guidance(self):
        from deepaper.defaults import DEFAULT_TEMPLATE
        assert "**粗体标题:**" in DEFAULT_TEMPLATE

    def test_incremental_annotation_guidance(self):
        from deepaper.defaults import DEFAULT_TEMPLATE
        assert "95.9(+0.3)" in DEFAULT_TEMPLATE
