"""Tests for prompt_builder: template parsing, auto-split."""
import pytest


class TestParseTemplateSections:
    def test_extracts_all_four_sections(self):
        from deepaper.prompt_builder import parse_template_sections
        from deepaper.defaults import DEFAULT_TEMPLATE

        sections = parse_template_sections(DEFAULT_TEMPLATE)
        expected_keys = [
            "核心速览",
            "第一性原理分析",
            "技术精要",
            "机制迁移",
        ]
        assert set(sections.keys()) == set(expected_keys)
        for key in expected_keys:
            assert len(sections[key]) > 100, f"Section {key} too short: {len(sections[key])}"

    def test_sections_contain_key_markers(self):
        from deepaper.prompt_builder import parse_template_sections
        from deepaper.defaults import DEFAULT_TEMPLATE

        sections = parse_template_sections(DEFAULT_TEMPLATE)
        # 核心速览: TL;DR + 核心机制一句话 + 关键数字表
        assert "TL;DR" in sections["核心速览"]
        assert "核心机制" in sections["核心速览"]
        assert "关键数字" in sections["核心速览"]
        # 第一性原理分析: 痛点 + 因果链 with [C1] prefix
        assert "痛点" in sections["第一性原理分析"]
        assert "[C1]" in sections["第一性原理分析"]
        assert "Because" in sections["第一性原理分析"]
        # 技术精要: method flow + formula table + design decisions + ablation + confusions + hidden costs
        assert "方法流程" in sections["技术精要"]
        assert "设计决策" in sections["技术精要"]
        assert "消融排序" in sections["技术精要"]
        assert "易混淆点" in sections["技术精要"]
        assert "隐性成本" in sections["技术精要"]
        # 机制迁移: decomposition table + lineage (Ancestors)
        assert "机制解耦" in sections["机制迁移"]
        assert "前身" in sections["机制迁移"] or "Ancestors" in sections["机制迁移"]


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
        # Required new fields
        assert "tldr" in spec
        assert "baselines" in spec
        assert "tags" in spec
        assert "mechanisms" in spec
        assert "key_tradeoffs" in spec
        assert "key_numbers" in spec
        # Removed fields should NOT be present
        assert "datasets" not in spec
        assert "metrics" not in spec
        assert "keywords" not in spec


class TestAutoSplit:
    def _profile(self, pages=10, tables=3, figures=4, equations=2):
        return {
            "total_pages": pages,
            "num_tables": tables,
            "num_figures": figures,
            "num_equations": equations,
        }

    def test_produces_exactly_three_writers(self):
        from deepaper.prompt_builder import auto_split
        tasks = auto_split(self._profile())
        assert len(tasks) == 3
        names = [t.name for t in tasks]
        assert names == ["writer-overview", "writer-principle", "writer-technical"]

    def test_overview_writer_owns_speed_and_transfer(self):
        from deepaper.prompt_builder import auto_split
        tasks = auto_split(self._profile())
        overview = next(t for t in tasks if t.name == "writer-overview")
        assert overview.sections == ["核心速览", "机制迁移"]

    def test_principle_writer_owns_first_principles(self):
        from deepaper.prompt_builder import auto_split
        tasks = auto_split(self._profile())
        principle = next(t for t in tasks if t.name == "writer-principle")
        assert principle.sections == ["第一性原理分析"]

    def test_technical_writer_owns_consolidated_technical(self):
        from deepaper.prompt_builder import auto_split
        tasks = auto_split(self._profile())
        technical = next(t for t in tasks if t.name == "writer-technical")
        assert technical.sections == ["技术精要"]
        assert technical.needs_pdf_pages is True

    def test_long_paper_same_three_writers(self):
        """Long papers do not add more writers (content grows via tables, not prose)."""
        from deepaper.prompt_builder import auto_split
        tasks = auto_split(self._profile(pages=120, tables=50, figures=30))
        assert len(tasks) == 3


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
        # H4 removed: no table count constraint
        assert "（H4）" not in constraints
        # But should have core table guidance
        assert "核心表格" in constraints or "核心行" in constraints
        # H8 still present
        assert "H8" in constraints


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
        task = WriterTask(name="writer-technical", sections=["技术精要"], needs_pdf_pages=True)
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
        assert "设计決策" in prompt or "设计决策" in prompt
        assert "易混淆点" in prompt
        assert "消融排序" in prompt or "隐性成本" in prompt

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


class TestReadStrategy:
    """Writer prompts should include read strategy based on file sizes."""

    def test_prompt_contains_read_strategy(self):
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
            pdf_path="",
            table_def_pages=[],
            file_info={"notes_lines": 500, "text_lines": 3500},
        )
        assert "读取策略" in prompt
        # Should have exact Read commands with offset/limit for text.txt (3500 lines = 2 reads)
        assert "offset=0" in prompt
        assert "offset=2000" in prompt
        assert "limit=2000" in prompt
        # notes.md (500 lines) should be one read, no offset
        assert "notes.md" in prompt

    def test_no_read_strategy_when_no_file_info(self):
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
            pdf_path="",
            table_def_pages=[],
        )
        assert "读取策略" not in prompt


class TestTemplateEnhancements:
    """Verify DEFAULT_TEMPLATE contains v2 content and formatting guidance."""

    def test_structured_form_guidance(self):
        from deepaper.defaults import DEFAULT_TEMPLATE
        # v2 core principle: structured forms over prose
        assert "结构化形式" in DEFAULT_TEMPLATE
        assert "禁止生成伪代码" in DEFAULT_TEMPLATE

    def test_causal_chain_format(self):
        from deepaper.defaults import DEFAULT_TEMPLATE
        # v2 因果链 uses fixed [C1]/[C2] labels
        assert "[C1]" in DEFAULT_TEMPLATE
        assert "Because" in DEFAULT_TEMPLATE

    def test_table_format_guidance(self):
        from deepaper.defaults import DEFAULT_TEMPLATE
        # v2 requires tables for number comparisons
        assert "表格" in DEFAULT_TEMPLATE
        assert "禁止散文" in DEFAULT_TEMPLATE or "禁止用散文" in DEFAULT_TEMPLATE

    def test_h4_h5_heading_rules(self):
        from deepaper.defaults import DEFAULT_TEMPLATE
        # v2 uses h4/h5, forbids h1/h2/h3
        assert "h4" in DEFAULT_TEMPLATE
        assert "h5" in DEFAULT_TEMPLATE
        assert "h1/h2/h3" in DEFAULT_TEMPLATE

    def test_key_sections_present(self):
        from deepaper.defaults import DEFAULT_TEMPLATE
        assert "核心速览" in DEFAULT_TEMPLATE
        assert "第一性原理分析" in DEFAULT_TEMPLATE
        assert "技术精要" in DEFAULT_TEMPLATE
        assert "机制迁移" in DEFAULT_TEMPLATE
