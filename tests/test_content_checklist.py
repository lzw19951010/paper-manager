"""Tests for H9 ContentMarkers gate."""
import pytest


class TestV2ContentMarkers:
    """Test that CONTENT_MARKERS covers the new 4-section structure."""

    def test_markers_exist_for_all_four_sections(self):
        from deepaper.content_checklist import CONTENT_MARKERS
        expected_sections = ["核心速览", "第一性原理分析", "技术精要", "机制迁移"]
        for sec in expected_sections:
            assert sec in CONTENT_MARKERS, f"Missing section: {sec}"
            assert len(CONTENT_MARKERS[sec]) >= 1

    def test_v2_markers_catch_table_requirements(self):
        from deepaper.content_checklist import check_content_markers
        # Good md: has all required structural markers
        md = (
            "#### 核心速览\n"
            "TL;DR: MATH 96.2%, AIME 80.6%.\n"
            "[动作] + [对象] + [方式] + [效果]\n"
            "| 指标 | 数值 | 基线 | 基线值 | 增益 |\n"
            "|------|------|------|--------|------|\n"
            "| MATH | 96.2 | Qwen | 95.4 | +0.8 |\n"
            "\n"
            "#### 第一性原理分析\n"
            "痛点：基线死在数据质量。\n"
            "[C1] Because A → Therefore B — 比喻：像厨房备料\n"
            "\n"
            "#### 技术精要\n"
            "##### 方法流程\n"
            "Input → Step A → Step B → Step C → Output\n"
            "##### 设计决策\n"
            "| 决策 | 备选方案 | 选择理由 | 证据来源 |\n"
            "|------|---------|---------|---------|\n"
            "| X | Y | Z | W |\n"
            "##### 消融排序\n"
            "| 排名 | 组件 | 增益 | 数据来源 |\n"
            "|------|------|------|---------|\n"
            "| 1 | A | +3.0 | Table 1 |\n"
            "##### 易混淆点\n"
            "❌ 错误 ✅ 正确\n"
            "##### 隐性成本\n"
            "| 成本项 | 量化数据 | 对决策的影响 |\n"
            "|-------|---------|-------------|\n"
            "| X | 5 days | delayed |\n"
            "\n"
            "#### 机制迁移\n"
            "| 原语名称 | 本文用途 | 抽象描述 | 信息论/几何直觉 |\n"
            "|---------|---------|---------|----------------|\n"
            "| A | X | Y | Z |\n"
            "前身 (Ancestors): A, B, C\n"
        )
        result = check_content_markers(md)
        assert result["passed"] is True, f"Failed: missing={result['missing']}"

    def test_v2_markers_reject_prose_only(self):
        from deepaper.content_checklist import check_content_markers
        # Bad md: prose only, no tables, no causal chain, no flowchart
        md = (
            "#### 核心速览\nJust some prose without structure.\n"
            "#### 第一性原理分析\nPain points described in sentences.\n"
            "#### 技术精要\nMethodology explained in paragraphs.\n"
            "#### 机制迁移\nRelated work listed as text.\n"
        )
        result = check_content_markers(md)
        assert result["passed"] is False
