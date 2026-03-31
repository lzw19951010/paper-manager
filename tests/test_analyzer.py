"""Tests for deepaper.analyzer module."""
from __future__ import annotations

import pytest
from deepaper.analyzer import parse_analysis_response


class TestParseAnalysisResponse:
    def test_complete_response(self):
        response = (
            "---\nvenue: NeurIPS 2023\nkeywords:\n  - scaling\n  - LLM\n"
            "tldr: \"A paper.\"\n---\n\n## 核心速览\n\nContent.\n\n---\n\n## 方法详解\n\nMethod."
        )
        fm, body = parse_analysis_response(response)
        assert fm["venue"] == "NeurIPS 2023"
        assert fm["keywords"] == ["scaling", "LLM"]
        assert "核心速览" in body
        assert "方法详解" in body

    def test_no_frontmatter(self):
        fm, body = parse_analysis_response("## Just markdown\n\nNo frontmatter.")
        assert fm == {}
        assert "## Just markdown" in body

    def test_broken_yaml(self):
        fm, body = parse_analysis_response("---\n: broken: [[\n---\n\n## Content")
        assert fm == {}
        assert "## Content" in body

    def test_yaml_not_dict(self):
        fm, body = parse_analysis_response("---\njust a string\n---\n\n## Body")
        assert fm == {}

    def test_empty_response(self):
        fm, body = parse_analysis_response("")
        assert fm == {}
        assert body == ""

    def test_list_fields(self):
        response = "---\nbaselines:\n  - GPT-3\n  - BERT\nmetrics:\n  - BLEU\n---\n\n## Content"
        fm, body = parse_analysis_response(response)
        assert fm["baselines"] == ["GPT-3", "BERT"]
        assert fm["metrics"] == ["BLEU"]

    def test_special_chars_in_yaml(self):
        response = '---\nvenue: "ICML 2024: Spotlight"\ntldr: "用Transformer"\n---\n\n## Body'
        fm, body = parse_analysis_response(response)
        assert "ICML 2024" in fm["venue"]
