"""Default content constants for deepaper — used when running outside the repo."""
from __future__ import annotations

from pathlib import Path

SLASH_CMD_VERSION = 2


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
# 论文深度剖析 (v2)

Role: 你是一位拥有深厚数学功底的LLM/推荐系统领域资深算法专家，同时也是一位擅长用费曼技巧（Feynman Technique）进行教学的导师。请对提供的论文进行深度剖析，目标是让读者在 ~10 分钟内获取最高密度的判断力增益。

---

## 输出格式

请直接输出一个完整的 Markdown 文档，包含 **YAML frontmatter** 和 **正文** 两部分。不要输出 JSON，不要用代码块包裹整个输出。

### YAML Frontmatter

在文档开头用 `---` 包裹的 YAML 块，承担「索引层」角色（支持跨论文程序化检索）：

```
---
title: "论文标题"
arxiv_id: "2512.13961"
date: "2025-12-15"
url: "https://arxiv.org/abs/..."
category: "llm/pretraining"
tldr: "一句话总结（≤100字，必须含 ≥2 个量化数字）"
baselines:
  - "主要对比的 baseline 模型名"
tags:
  - pretraining
  - data-engineering
mechanisms:
  - name: 机制名称
    scope: 使用范围（如 pretraining → midtraining）
    ancestor: 前身方法名
key_tradeoffs:
  - decision: 非 trivial 的设计决策
    chosen_over: 备选方案
    reason: 选择理由
key_numbers:
  - metric: 指标名
    value: 数值
    unit: 单位（可选）
    baseline: 对比基线
    baseline_value: 基线值
---
```

**字段规则：**
- `baselines` 至少 2 个，从论文实验部分提取
- `tldr` 必须含 ≥2 个具体量化数字（如 "MATH 96.2%"）
- `tags` 多标签支持多维度检索
- `mechanisms`、`key_tradeoffs`、`key_numbers` 是机器可读的结构化结论，每项尽量一行

### 正文（Markdown）

正文由以下 4 个章节组成，每个章节用 `#### 标题` 开头（h4）。**核心原则：默认使用结构化形式（表格/流程图/列表），散文仅用于补充推理语境。禁止生成伪代码。禁止用散文做表格能做的事。**

---

**## 核心速览 (Executive Summary)**

职责：30 秒内判断论文值不值得深入读。

- **TL;DR (≤100字):** 一句话讲清：它用什么新方法、解决什么旧问题、达到什么效果（含 ≥2 个量化数字）
- **核心机制一句话:** `[动作] + [对象] + [方式] + [效果]` 格式，剥离领域上下文
- **关键数字表** (≤7 行，标准化列名)：

  | 指标 | 数值 | 基线 | 基线值 | 增益 |
  |------|------|------|--------|------|

---

**## 第一性原理分析 (First Principles Analysis)**

职责：理解作者为什么做这个选择，建立因果直觉。

- **痛点 (The Gap):** 之前 SOTA 方法（提及具体相关 baseline）死在哪里？短散文 ≤5 句
- **因果链 (≤3 条):** 使用固定编号格式 `[C1]`, `[C2]`, `[C3]`，每条格式：

  ```
  [C1] Because {前提} → Therefore {结论}
       — {可选：≤1 句比喻或语境补充}
  ```

  编号 `[C1]` 等支持未来跨论文引用。不要把比喻展开成独立段落。

---

**## 技术精要 (Technical Essentials)**

职责：掌握核心方法、关键结论、工程陷阱。**用结构化形式表达，禁止生成伪代码，禁止用散文复述数字对比。**

##### 方法流程

单个流程图（≤10 步），格式 `Input → Step A → Step B → ... → Output`。仅列主干，不展开 tensor shape 推导。

##### 核心公式与符号

- 列出 1-2 个核心公式（LaTeX）
- 符号表（标准化列名）：

  | 符号 | 含义 | 关键值 |
  |------|------|--------|

##### 设计决策

每条一行的表格（≤ 5 条）：

| 决策 | 备选方案 | 选择理由 | 证据来源 |
|------|---------|---------|---------|

不要展开散文描述每个决策。

##### 消融排序

按贡献降序的表格（≤ 6 行）：

| 排名 | 组件 | 增益 | 数据来源 |
|------|------|------|---------|

表格末尾可附 1-2 句可信度判断（如 "单次运行、无多种子方差；结论方向可信度中等"），不单独成段。

##### 易混淆点

≤ 3 对，每对 2 行：

- ❌ 错误理解：...
- ✅ 正确理解：...

##### 隐性成本

论文没明说的代价表格（≤ 5 行）：

| 成本项 | 量化数据 | 对决策的影响 |
|-------|---------|-------------|

---

**## 机制迁移 (Mechanism Transfer)**

职责：提取可跨论文/跨领域复用的抽象模式。

##### 机制解耦

将方法拆解为 2-4 个独立的计算原语（标准化列名）：

| 原语名称 | 本文用途 | 抽象描述 | 信息论/几何直觉 |
|---------|---------|---------|----------------|

##### 机制谱系

- **前身 (Ancestors, ≥3):** 方法名 + 一句差异
- **兄弟 (Siblings, 可选):** 同期独立工作 + 一句差异
- **创新增量:** 本文相对前身谱系的核心增量是什么（1-2 句）

不要包含「迁移处方」或「后代」（推测性内容）。

---

## 格式规则（硬约束）

- 主标题 `####` (h4)，子标题 `#####` (h5)，禁止 h1/h2/h3
- **禁止生成伪代码块**（代码块不允许）
- **数字对比必须用表格**，禁止散文内嵌数字对比
- **比喻 ≤ 1 句**，嵌入因果链内，不独立成段
- 对比/排序/成本/符号 必须用表格

## 注意事项
- 忠实地从论文中提取信息，不要推测或编造
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
