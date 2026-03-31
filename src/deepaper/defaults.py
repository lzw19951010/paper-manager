"""Default content constants for deepaper — used when running outside the repo."""
from __future__ import annotations

from pathlib import Path


def get_default_slash_command() -> str:
    """Load the slash command template from the package's .claude/commands/ directory."""
    cmd_path = Path(__file__).resolve().parent.parent.parent / ".claude" / "commands" / "deepaper.md"
    if cmd_path.exists():
        return cmd_path.read_text(encoding="utf-8")
    return "# deepaper slash command\n\nRun `deepaper download $ARGUMENTS` then analyze the paper.\n"


DEFAULT_CONFIG_YAML = """\
# deepaper configuration
# model: claude-opus-4-6          # Model for deep analysis (display only, uses Claude Code CLI)
# tag_model: claude-sonnet-4-6    # Model for lightweight tagging
# git_remote: ""                  # Git remote URL for syncing
# papers_dir: papers              # Directory for paper notes
# template: default               # Prompt template name
# chromadb_dir: .chromadb         # Vector database directory
# semantic_scholar_api_key: ""    # Semantic Scholar API key (free: https://www.semanticscholar.org/product/api#api-key-form)
"""

DEFAULT_TEMPLATE = """\
# 论文深度剖析

Role: 你是一位拥有深厚数学功底的LLM/推荐系统领域资深算法专家，同时也是一位擅长用费曼技巧（Feynman Technique）进行教学的导师。请对提供的论文进行深度剖析。

---

## 输出格式

请直接输出一个完整的 Markdown 文档，包含 **YAML frontmatter** 和 **正文** 两部分。不要输出 JSON，不要用代码块包裹整个输出。

### YAML Frontmatter

在文档开头用 `---` 包裹的 YAML 块，包含以下结构化元数据字段。**所有列表字段必须填写，从论文中提取，不得留空列表。**

```
---
venue: "发表场所（如 NeurIPS 2023），未找到则为 null"
publication_type: "conference/journal/preprint/workshop/thesis 之一"
doi: "DOI 标识符，未找到则为 null"
keywords:
  - 关键词1
  - 关键词2（共 5-10 个技术关键词，必填）
tldr: "一句话总结论文核心贡献（≤100字，必填）"
core_contribution: "new-method/new-dataset/new-benchmark/new-framework/survey/empirical-study/theoretical 之一或组合"
baselines:
  - "论文对比的主要baseline方法（必填，从实验部分提取）"
datasets:
  - "使用的数据集名称（必填，从实验部分提取）"
metrics:
  - "使用的评估指标（必填，如 BLEU, Recall@20, NDCG@10）"
code_url: "官方代码仓库 URL，未找到则为 null"
---
```

**重要**：baselines、datasets、metrics 三个字段必须从论文实验部分提取具体内容，不要留空。如果论文确实没有实验对比（如纯理论论文），写明 `["N/A (theoretical paper)"]`。

### 正文（Markdown）

正文由以下章节组成，每个章节用 `## 标题` 开头，章节之间用 `---` 分隔。所有内容可包含子标题、表格、代码块、公式等富格式。

---

**## 核心速览 (Executive Summary)**

- **TL;DR (≤100字):** 一句话讲清：它用什么新方法，解决了什么旧问题，实现了什么SOTA效果。
- **一图流 (Mental Model):** 用文字描述一个直观的思维模型或类比（例如："如果旧方法是查字典，新方法就是……"），帮助我瞬间建立直觉。
- **核心机制一句话 (Mechanism in One Line):** 剥离领域上下文，用一句通用语言描述本文最核心的信息处理机制。格式：`[动作] + [对象] + [方式] + [效果]`。

---

**## 动机与第一性原理 (Motivation & First Principles)**

- **痛点 (The Gap):** 之前的 SOTA 方法（提及具体相关Baseline）死在哪里？
- **核心洞察 (Key Insight):** 作者发现了什么被忽略的本质规律？请用因果链推导（Because A → B → C），而非单纯罗列。
- **物理/直觉解释:** 不要堆砌术语，用大白话解释为什么这个机制必须生效？

---

**## 方法详解 (Methodology)**

三层递进，需保障无幻觉，若原文未提及则标注"⚠️ 未提及"；若论文提及但未展开，则标注"⚡ 论文未给出细节，以下为基于上下文的合理推断"。

#### 直觉版 (Intuitive Walk-through)
引用论文的方法概览图（通常是Figure 1），逐元素解释：
- 旧方法（baseline）的数据流是怎样的？
- 新方法改了哪里？为什么？
- 图中每个新增组件/箭头/符号代表什么？

用最简单的例子（如3层网络、3个item），不写公式，纯文字走一遍"旧方法做一步 → 新方法做一步 → 差异在哪"。

#### 精确版 (Formal Specification)
- **流程图 (Text-based Flow):** Input (Shape) → Module A → Module B → Output，明确标出关键步骤的数据流转和tensor shape变化。
- **关键公式与变量:** 列出核心公式，对每个符号不仅给出数学定义，还要给出物理含义。
- **数值推演 (Numerical Example):** 【必做】假设简单输入，代入核心公式逐步推演。
- **伪代码 (Pseudocode):** 仅展示最核心逻辑（Python/PyTorch风格），关键处注释Tensor维度变化。

#### 设计决策 (Design Decisions)
对方法中的每个非trivial设计选择，回答：
- 有哪些替代方案？
- 论文是否做了对比？结果如何？
- 选择背后的核心trade-off是什么？

如果论文未讨论某个明显的替代方案，标注"论文未讨论"。

#### 易混淆点 (Potential Confusions)
主动列出读者最可能误解的2-3个点：
- ❌ 错误理解: ...
- ✅ 正确理解: ...

---

**## 实验与归因 (Experiments & Attribution)**

- **核心收益:** 相比Baseline提升了多少？（量化数据）
- **归因分析 (Ablation Study):** 论文的哪个组件贡献了最大的收益？将ablation结果按贡献大小排序。
- **可信度检查:** 实验设置是否公平？是否存在"刷榜"嫌疑（如测试集泄露、Baseline未调优、只报相对提升不报绝对值）？

---

**## 专家批判 (Critical Review)**

- **隐性成本 (Hidden Costs):** 论文没明说的代价是什么？（例如：训练慢2倍、对超参极度敏感、难以并行化）
- **工程落地建议:** 如果要复现或应用到业务中，最大的"坑"可能在哪？
- **关联思考:** 该方法与现有技术（如 LoRA, FlashAttention, MoE 等）有什么联系或冲突？

---

**## 机制迁移分析 (Mechanism Transfer Analysis)**

目标：剥离论文的领域外壳，提取可跨领域复用的计算原语，并给出具体的迁移方案。

#### 机制解耦 (Mechanism Decomposition)
将论文的方法拆解为 2-4 个独立的计算原语，每个原语用表格描述：

| 原语名称 | 本文用途 | 抽象描述 | 信息论/几何直觉 |
|---------|---------|---------|---------------|

#### 迁移处方 (Transfer Prescription)
针对每个原语，给出 1-2 个具体的跨领域应用场景，要具体到：
- 目标领域 + 具体问题
- 怎么接（输入是什么、输出是什么、替换现有pipeline的哪个组件）
- 预期收益是什么
- 可能的风险或不适用条件

#### 机制家族图谱 (Mechanism Family Tree)
将本文的核心机制放入更大的技术族谱中：
- **前身 (Ancestors):** 哪些更早的工作使用了类似机制？
- **兄弟 (Siblings):** 同一时期有哪些独立提出的类似机制？
- **后代 (Descendants):** 后续哪些工作继承或改进了该机制？

重点标注该机制在族谱中的"创新增量"是什么。

---

**## 背景知识补充 (Background Context)**

【可选】论文中引用或依赖的其他技术/做法，如果属于领域common practice，简要说明其地位和核心引用。仅在论文依赖的外部知识较多时输出此章节，否则省略。

## 注意事项
- 忠实地从论文中提取信息，不要推测或编造
- 发表场所：检查论文页眉、页脚和致谢部分
- 关键词：聚焦方法、领域和技术
- YAML frontmatter 中的字符串值如包含冒号或特殊字符，请用引号包裹
- 直接输出最终 Markdown，不要用代码块包裹
"""

DEFAULT_CLASSIFY = """\
Based on the paper summary and the category definitions below, classify this paper.

Paper summary and keywords:
{summary}

Category definitions:
{categories}

Respond with ONLY a JSON object: {{"category": "llm/pretraining"}} where the value is the category path relative to papers/. Valid top-level categories: llm, recsys, multimodal, misc. Use misc if unsure.
"""

DEFAULT_TAGS = """\
Generate 3-8 classification tags for this academic paper.

Paper summary: {summary}

Respond with ONLY a JSON object: {{"tags": ["tag1", "tag2", ...]}}
"""

DEFAULT_CATEGORIES = """\
# 论文分类规则

本文件定义了论文自动分类的规则，用于将论文归入 `papers/` 下的对应目录。

---

## llm/ — 通用大语言模型

与大语言模型本身的训练、对齐、推理能力、效率优化或 Agent 能力相关的论文。

- **pretraining/** — 预训练：数据工程、模型架构设计（Transformer 变体等）、scaling law、tokenizer 设计、预训练策略（课程学习、数据配比等）
- **alignment/** — 对齐：RLHF、DPO、RLAIF、PPO for LLM、安全对齐、红队测试、指令微调（SFT）、偏好学习
- **reasoning/** — 推理：Chain-of-Thought（CoT）、Tree-of-Thought（ToT）、thinking models（o1/o3 类）、数学推理、代码推理、逻辑推理、自我反思
- **efficiency/** — 效率：量化（GPTQ、AWQ）、知识蒸馏、剪枝、MoE（混合专家）、推理加速（FlashAttention、vLLM、PagedAttention）、LoRA 等参数高效微调方法（PEFT）
- **agent/** — Agent：tool use、function calling、planning（任务规划）、memory（记忆机制）、multi-agent 协作、ReAct、代码执行 Agent

---

## recsys/ — 推荐系统

与推荐系统的召回、排序、建模范式或工程实现相关的论文。

- **matching/** — 召回：双塔模型、图神经网络（GNN）用于推荐、序列推荐（SASRec、BERT4Rec 等）、向量检索（ANN）、用户/物品表示学习
- **ranking/** — 排序：CTR 预估（DeepFM、DCN 等）、多任务学习（MTL）、特征交互建模、重排序（re-ranking）、listwise/pairwise 排序
- **llm-as-rec/** — LLM 即推荐模型：LLM 端到端完成推荐任务，模型本身同时具备自然语言理解/生成能力和推荐能力。核心贡献在于让 LLM 直接理解用户偏好并输出推荐结果，不是简单地把推荐任务转成 NLP prompt 再调用外部 LLM。
- **generative-rec/** — 生成式推荐：用生成范式做推荐（生成 item ID 序列、token 序列等），以 next-token/next-item 预测的方式建模推荐，不一定需要 LLM 的自然语言能力
- **system/** — 推荐系统工程：embedding serving、特征工程与存储、A/B 测试框架、在线学习（online learning）、工业级推荐系统架构

---

## multimodal/ — 多模态与 CV

涉及图像、视频、音频等多种模态，或纯计算机视觉任务的论文。

- **vlm/** — 视觉语言模型：CLIP、LLaVA、BLIP、Flamingo 等多模态理解模型，图文对齐，视觉问答（VQA），多模态大模型
- **generation/** — 生成：Diffusion 模型（DDPM、Stable Diffusion）、视频生成、图像编辑、文生图（text-to-image）、图像超分
- **understanding/** — 理解：目标检测（YOLO、DETR）、图像分割（SAM）、OCR、视觉推理、图像分类、深度估计

---

## misc/ — 其他

不属于以上任何类别的论文，例如：图神经网络（非推荐场景）、强化学习（非 LLM 对齐场景）、数据库、系统、理论等。

---

## 分类规则

1. **按主要贡献归类**：跨领域论文以核心贡献所属方向为准。例如，一篇用 LLM 做推荐的论文，若核心贡献是推荐方法（如新的 ID 建模方式），归 `recsys/llm-as-rec`；若核心贡献是 LLM 本身的新能力（如 in-context learning），则归 `llm/`。
2. **llm-as-rec 优先**：当 `llm-as-rec` 和 `generative-rec` 难以区分时（例如论文同时涉及 LLM 端到端推荐和生成式 item 建模），优先归入 `recsys/llm-as-rec`。
3. **不确定时归 misc/**：若论文不明确属于上述某个子类别，或跨多个领域且无明显主导方向，归入 `misc/`。
4. **输出格式**：返回 JSON `{"category": "大类/子类"}`，例如 `{"category": "llm/pretraining"}` 或 `{"category": "misc"}`。
"""
