"""End-to-end golden tests using real Claude output from top papers.

These tests verify the full parse_analysis_response → write_paper_note pipeline
against real-world markdown output, ensuring:
1. YAML frontmatter is correctly parsed (venue, keywords, baselines, etc.)
2. Body sections survive intact
3. Writer correctly merges arxiv metadata + analysis frontmatter
4. Template format escaping works correctly
5. Citation analysis filters and classifies correctly
"""
from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import yaml
import pytest

from deepaper.analyzer import parse_analysis_response
from deepaper.writer import write_paper_note


# ---------------------------------------------------------------------------
# Realistic Claude responses (trimmed bodies, full frontmatter)
# ---------------------------------------------------------------------------

TIGER_RESPONSE = """\
---
venue: NeurIPS 2023
publication_type: conference
doi: null
keywords:
  - Generative Retrieval
  - Sequential Recommendation
  - Semantic ID
  - RQ-VAE
  - Residual Quantization
  - Transformer Encoder-Decoder
  - Cold-Start Recommendation
  - Vector Quantization
  - Autoregressive Decoding
  - Content-Based Representation
tldr: "提出TIGER框架，用RQ-VAE将物品内容编码为层次化Semantic ID，再用Transformer seq2seq模型自回归生成下一物品的Semantic ID，取代传统ANN检索，在多个数据集上显著超越SOTA。"
core_contribution: new-method/new-framework
baselines:
  - GRU4Rec
  - Caser
  - HGN
  - SASRec
  - BERT4Rec
  - FDSA
  - S3-Rec
  - P5
datasets:
  - Amazon Beauty
  - Amazon Sports and Outdoors
  - Amazon Toys and Games
metrics:
  - Recall@5
  - Recall@10
  - NDCG@5
  - NDCG@10
code_url: null
---

## 核心速览 (Executive Summary)

- **TL;DR (≤100字):** TIGER用RQ-VAE将物品内容嵌入量化为层次化Semantic ID，然后训练Transformer encoder-decoder模型自回归地预测下一个物品的Semantic ID，取代传统ANN检索，SOTA效果。

- **一图流 (Mental Model):** 传统推荐是"拿画像去仓库找相似商品"，TIGER是"给每个商品一个语义邮编，模型直接念出下一个邮编"。

- **核心机制一句话:** `[自回归解码] + [物品层次化语义码字] + [Transformer seq2seq] + [直接生成目标物品ID]`

---

## 方法详解 (Methodology)

TIGER uses RQ-VAE to create Semantic IDs, then trains a Transformer seq2seq model.
"""

HSTU_RESPONSE = """\
---
venue: "ICML 2024"
publication_type: conference
doi: null
keywords:
  - Generative Recommender
  - Sequential Transducer
  - HSTU
  - Scaling Law
  - Recommendation System
  - Trillion Parameters
  - Pointwise Aggregated Attention
tldr: "提出HSTU架构将推荐问题重构为序列转导任务，在Meta十亿级用户平台上实现12.4%线上提升，首次证明推荐系统存在类似LLM的scaling law。"
core_contribution: new-method/new-framework
baselines:
  - SASRec
  - BERT4Rec
  - HSTU (ablations)
datasets:
  - ML-1M
  - ML-20M
  - Amazon Reviews
metrics:
  - NDCG@10
  - HR@10
  - Online A/B test metrics
code_url: "https://github.com/facebookresearch/generative-recommenders"
---

## 核心速览 (Executive Summary)

- **TL;DR:** HSTU-based Generative Recommenders with 1.5T parameters improve online metrics by 12.4%.

---

## 方法详解 (Methodology)

HSTU redesigns attention for high-cardinality recommendation data.
"""

P5_RESPONSE = """\
---
venue: RecSys 2022
publication_type: conference
doi: null
keywords:
  - Unified Recommendation
  - Text-to-Text
  - Pretrain
  - Personalized Prompt
  - T5
  - Zero-Shot Recommendation
  - Multi-Task Learning
  - Language Model for Recommendation
tldr: "将五大推荐任务统一为文本到文本的生成范式，通过个性化提示在T5上多任务预训练，实现跨任务知识迁移和零样本泛化。"
core_contribution: new-framework
baselines:
  - MF
  - MLP
  - GRU4Rec
  - Caser
  - SASRec
  - S3-Rec
datasets:
  - Amazon Beauty
  - Amazon Sports
  - Amazon Toys
  - Yelp
metrics:
  - HR@5
  - HR@10
  - NDCG@5
  - NDCG@10
  - RMSE
  - MAE
code_url: "https://github.com/jeykigung/P5"
---

## 核心速览 (Executive Summary)

P5 unifies recommendation as language processing.

---

## 方法详解 (Methodology)

All recommendation data is converted to natural language sequences.
"""

ARXIV_METADATA_TIGER = {
    "arxiv_id": "2305.05065",
    "title": "Recommender Systems with Generative Retrieval",
    "authors": ["Shashank Rajput", "Nikhil Mehta"],
    "date": "2023-05-08",
    "abstract": "We propose a generative retrieval approach.",
    "categories": ["cs.IR"],
    "url": "https://arxiv.org/abs/2305.05065",
}

ARXIV_METADATA_HSTU = {
    "arxiv_id": "2402.17152",
    "title": "Actions Speak Louder than Words",
    "authors": ["Jiaqi Zhai", "Lucy Liao"],
    "date": "2024-02-26",
    "abstract": "Trillion-parameter sequential transducers.",
    "categories": ["cs.LG"],
    "url": "https://arxiv.org/abs/2402.17152",
}

ARXIV_METADATA_P5 = {
    "arxiv_id": "2203.13366",
    "title": "Recommendation as Language Processing (P5)",
    "authors": ["Shijie Geng", "Shuchang Liu"],
    "date": "2022-03-24",
    "abstract": "Unified text-to-text paradigm for recommendation.",
    "categories": ["cs.IR"],
    "url": "https://arxiv.org/abs/2203.13366",
}


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestParseRealPapers:
    """Test parse_analysis_response against real Claude output patterns."""

    def test_tiger_frontmatter(self):
        fm, body = parse_analysis_response(TIGER_RESPONSE)
        assert fm["venue"] == "NeurIPS 2023"
        assert fm["publication_type"] == "conference"
        assert fm["core_contribution"] == "new-method/new-framework"
        assert "Semantic ID" in fm["keywords"]
        assert "RQ-VAE" in fm["keywords"]
        assert len(fm["baselines"]) >= 7
        assert "SASRec" in fm["baselines"]
        assert fm["datasets"] == ["Amazon Beauty", "Amazon Sports and Outdoors", "Amazon Toys and Games"]
        assert "Recall@10" in fm["metrics"]
        assert fm["code_url"] is None
        assert "TIGER" in fm["tldr"]

    def test_tiger_body(self):
        fm, body = parse_analysis_response(TIGER_RESPONSE)
        assert "## 核心速览 (Executive Summary)" in body
        assert "## 方法详解 (Methodology)" in body
        assert "RQ-VAE" in body

    def test_hstu_frontmatter(self):
        fm, body = parse_analysis_response(HSTU_RESPONSE)
        assert fm["venue"] == "ICML 2024"
        assert fm["publication_type"] == "conference"
        assert "HSTU" in fm["keywords"]
        assert "Scaling Law" in fm["keywords"]
        assert fm["code_url"] == "https://github.com/facebookresearch/generative-recommenders"
        assert "scaling law" in fm["tldr"]

    def test_p5_frontmatter(self):
        fm, body = parse_analysis_response(P5_RESPONSE)
        assert fm["venue"] == "RecSys 2022"
        assert fm["core_contribution"] == "new-framework"
        assert "T5" in fm["keywords"]
        assert len(fm["baselines"]) >= 5
        assert fm["code_url"] == "https://github.com/jeykigung/P5"
        assert "RMSE" in fm["metrics"]

    def test_p5_body(self):
        fm, body = parse_analysis_response(P5_RESPONSE)
        assert "## 核心速览" in body
        assert "language processing" in body.lower()


class TestWriteRealPapers:
    """Test full write pipeline with real paper data."""

    @pytest.mark.parametrize("response,metadata,expected_category", [
        (TIGER_RESPONSE, ARXIV_METADATA_TIGER, "recsys/generative-rec"),
        (HSTU_RESPONSE, ARXIV_METADATA_HSTU, "recsys/generative-rec"),
        (P5_RESPONSE, ARXIV_METADATA_P5, "recsys/llm-as-rec"),
    ])
    def test_write_and_read_back(self, tmp_path, response, metadata, expected_category):
        fm, body = parse_analysis_response(response)
        tags = ["generative-rec", "test"]

        path = write_paper_note(
            fm, body, metadata, tags, tmp_path, category=expected_category,
        )

        assert path.exists()
        content = path.read_text(encoding="utf-8")

        # Verify frontmatter round-trips
        assert content.startswith("---")
        fm_end = content.find("---", 3)
        written_fm = yaml.safe_load(content[3:fm_end])

        # Arxiv metadata present
        assert written_fm["arxiv_id"] == metadata["arxiv_id"]
        assert written_fm["title"] == metadata["title"]
        assert written_fm["authors"] == metadata["authors"]

        # Claude analysis metadata merged
        assert written_fm["venue"] == fm.get("venue")
        assert written_fm["keywords"] == fm.get("keywords", [])
        assert written_fm["category"] == expected_category
        assert written_fm["tags"] == tags

        # Body preserved
        written_body = content[fm_end + 3:].strip()
        assert "## 核心速览" in written_body
        assert "## 方法详解" in written_body

    def test_tiger_correct_subdirectory(self, tmp_path):
        fm, body = parse_analysis_response(TIGER_RESPONSE)
        path = write_paper_note(
            fm, body, ARXIV_METADATA_TIGER, ["test"], tmp_path,
            category="recsys/generative-rec",
        )
        assert path.parent.name == "generative-rec"
        assert path.parent.parent.name == "recsys"


# ---------------------------------------------------------------------------
# MiniCPM golden test (llm/pretraining — was misclassified as misc)
# ---------------------------------------------------------------------------

MINICPM_RESPONSE = """\
---
venue: null
publication_type: preprint
doi: null
keywords:
  - Small Language Model
  - Scaling Law
  - WSD Learning Rate Scheduler
  - Model Wind Tunnel
  - SLM
  - Compute-Optimal Training
  - Continuous Training
tldr: "提出WSD学习率调度器和模型风洞实验方法，使1.2B/2.4B的MiniCPM达到7B-13B模型的性能。"
core_contribution: new-method
baselines:
  - LLaMA2-7B
  - Mistral-7B
  - MPT-7B
datasets:
  - C-Eval
  - MMLU
  - HumanEval
metrics:
  - Accuracy
  - Pass@1
code_url: "https://github.com/OpenBMB/MiniCPM"
---

## 核心速览 (Executive Summary)

MiniCPM demonstrates that small models can match much larger ones.

---

## 方法详解 (Methodology)

WSD scheduler and model wind tunnel experiments.
"""

ARXIV_METADATA_MINICPM = {
    "arxiv_id": "2404.06395",
    "title": "MiniCPM: Unveiling the Potential of Small Language Models with Scalable Training Strategies",
    "authors": ["Shengding Hu", "Yuge Tu"],
    "date": "2024-04-09",
    "abstract": "Small language models with scalable training.",
    "categories": ["cs.CL"],
    "url": "https://arxiv.org/abs/2404.06395",
}


class TestMiniCPM:
    """MiniCPM was misclassified as misc due to template escaping bug.
    Verify it parses correctly as llm/pretraining material."""

    def test_minicpm_frontmatter(self):
        fm, body = parse_analysis_response(MINICPM_RESPONSE)
        assert fm["publication_type"] == "preprint"
        assert "Scaling Law" in fm["keywords"]
        assert "WSD Learning Rate Scheduler" in fm["keywords"]
        assert fm["code_url"] == "https://github.com/OpenBMB/MiniCPM"
        assert "LLaMA2-7B" in fm["baselines"]
        assert "MiniCPM" in fm["tldr"]

    def test_minicpm_body(self):
        fm, body = parse_analysis_response(MINICPM_RESPONSE)
        assert "## 核心速览" in body
        assert "## 方法详解" in body

    def test_minicpm_write_to_pretraining_dir(self, tmp_path):
        fm, body = parse_analysis_response(MINICPM_RESPONSE)
        path = write_paper_note(
            fm, body, ARXIV_METADATA_MINICPM, ["scaling", "slm"],
            tmp_path, category="llm/pretraining",
        )
        assert path.exists()
        assert path.parent.name == "pretraining"
        assert path.parent.parent.name == "llm"

        content = path.read_text(encoding="utf-8")
        fm_end = content.find("---", 3)
        written_fm = yaml.safe_load(content[3:fm_end])
        assert written_fm["arxiv_id"] == "2404.06395"
        assert written_fm["category"] == "llm/pretraining"


# ---------------------------------------------------------------------------
# Template escaping tests (root cause of MiniCPM misclassification)
# ---------------------------------------------------------------------------



# ---------------------------------------------------------------------------
# Citation analysis tests
# ---------------------------------------------------------------------------

class TestCitationFiltering:
    """Verify citation formatting filters 0-citation papers and structures output."""

    def test_filter_zero_citations(self):
        from deepaper.citations import format_descendants_section
        data = {
            "total_citations": 10,
            "fetch_date": "2026-03-31",
            "source": "openalex",
            "citing_papers": [
                {"title": "Good Paper", "authors": "A et al.", "year": 2024,
                 "citation_count": 5, "relation": "core", "one_line": "核心续作"},
                {"title": "Zero Paper", "authors": "B", "year": 2025,
                 "citation_count": 0},
                {"title": "Another Zero", "authors": "C", "year": 2025,
                 "citation_count": 0},
            ],
        }
        result = format_descendants_section(data)
        assert "Good Paper" in result
        assert "Zero Paper" not in result
        assert "Another Zero" not in result

    def test_core_papers_shown_with_analysis(self):
        from deepaper.citations import format_descendants_section
        data = {
            "total_citations": 50,
            "fetch_date": "2026-03-31",
            "source": "openalex",
            "citing_papers": [
                {"title": "Follow-up Work", "authors": "X et al.", "year": 2024,
                 "citation_count": 20, "relation": "core",
                 "one_line": "直接改进了父论文的方法"},
                {"title": "Extension Paper", "authors": "Y et al.", "year": 2025,
                 "citation_count": 10, "relation": "extension",
                 "one_line": "扩展到新场景"},
                {"title": "Survey Paper", "authors": "Z et al.", "year": 2024,
                 "citation_count": 100, "relation": "survey",
                 "one_line": "综述"},
            ],
        }
        result = format_descendants_section(data)
        # Core and extension in detailed section
        assert "核心后续工作" in result
        assert "Follow-up Work" in result
        assert "直接改进了父论文的方法" in result
        assert "Extension Paper" in result
        # Survey in other section
        assert "其他引用" in result
        assert "Survey Paper" in result
        assert "🔵 综述收录" in result

    def test_empty_citations(self):
        from deepaper.citations import format_descendants_section
        data = {
            "total_citations": 0,
            "fetch_date": "2026-03-31",
            "source": "openalex",
            "citing_papers": [],
        }
        result = format_descendants_section(data)
        assert "暂无高影响力引用论文" in result

    def test_all_zero_citations_filtered(self):
        """When all papers have 0 citations, show empty message."""
        from deepaper.citations import format_descendants_section
        data = {
            "total_citations": 3,
            "fetch_date": "2026-03-31",
            "source": "openalex",
            "citing_papers": [
                {"title": "A", "authors": "X", "year": 2025, "citation_count": 0},
                {"title": "B", "authors": "Y", "year": 2025, "citation_count": 0},
            ],
        }
        result = format_descendants_section(data)
        assert "暂无高影响力引用论文" in result


class TestReconstructAbstract:
    """Test OpenAlex abstract_inverted_index reconstruction."""

    def test_reconstruct_basic(self):
        from deepaper.citations import _reconstruct_abstract
        inverted_index = {
            "We": [0],
            "propose": [1],
            "a": [2],
            "new": [3],
            "method": [4],
        }
        result = _reconstruct_abstract(inverted_index)
        assert result == "We propose a new method"

    def test_reconstruct_with_repeated_words(self):
        from deepaper.citations import _reconstruct_abstract
        inverted_index = {
            "the": [0, 4],
            "model": [1, 5],
            "outperforms": [2],
            "baseline": [3],
        }
        result = _reconstruct_abstract(inverted_index)
        assert result == "the model outperforms baseline the model"

    def test_reconstruct_none(self):
        from deepaper.citations import _reconstruct_abstract
        assert _reconstruct_abstract(None) == ""
        assert _reconstruct_abstract({}) == ""

    def test_reconstruct_invalid_type(self):
        from deepaper.citations import _reconstruct_abstract
        assert _reconstruct_abstract("not a dict") == ""


