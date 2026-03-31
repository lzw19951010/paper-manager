Analyze an arxiv paper and save to the deepaper knowledge base.

## Step 0: Ensure deepaper is installed

Run `which deepaper` to check. If not found, run:
```bash
pip install deepaper && deepaper init
```
If `deepaper init` has already been run (papers/ directory exists), skip init.

## Step 1: Download

Run `deepaper download $ARGUMENTS` to get the paper metadata and file paths. Parse the JSON output.

## Step 2: Read the paper COMPLETELY

**Critical: You must read the entire paper. Incomplete reading produces inferior analysis.**

Use the Read tool to read the PDF at `pdf_path` from the download output. Read ALL pages in chunks of 20:
```
Read(pdf_path, pages="1-20")
Read(pdf_path, pages="21-40")
Read(pdf_path, pages="41-60")
... keep going until you get an error (no more pages) or reach References
```

**Page coverage check:** After reading, count how many pages you actually read. If the PDF's `size_mb` > 3 and you read fewer than 30 pages, you likely stopped too early — keep reading.

**Content coverage check:** Verify you have seen ALL of the following before proceeding:
- [ ] Abstract and Introduction
- [ ] Full methodology / model architecture
- [ ] ALL main result tables (not just Table 1 — look for Table 2, 3, 4...)
- [ ] Ablation studies
- [ ] Key findings / discussion

If any of these is missing, keep reading more pages.

## Step 3: Analyze

Write a comprehensive analysis. Quality standard: an expert researcher reading your note should get 90% of the paper's value without reading the original.

Write the complete analysis to `/tmp/deepaper_analysis.md`.

**每个章节有明确的"完成定义"（Definition of Done），不满足则该章节不合格。**

### Output format

````
---
venue: "发表场所（如 NeurIPS 2023），未找到则为 null"
publication_type: "conference/journal/preprint/workshop/thesis"
doi: "DOI，未找到则为 null"
keywords:
  - 5-10个技术关键词（必填，聚焦方法和领域）
tldr: "一句话核心贡献（≤100字，必填，必须包含具体量化数字）"
core_contribution: "new-method/new-dataset/new-benchmark/new-framework/survey/empirical-study/theoretical"
baselines:
  - 必填：从实验表格提取所有对比方法，不得遗漏
datasets:
  - 必填：训练数据源（含上游来源和token数）+ 评测数据集
metrics:
  - 必填：从实验表格提取所有评估指标
code_url: "代码仓库URL，未找到则为 null"
---
````

#### 核心速览 (Executive Summary)

**Done = 以下三项全部完成：**
- **TL;DR:** 包含具体量化数字（如"MATH 96.2%"），不接受"显著提升"
- **一图流:** 必须有"旧方法是X → 新方法是Y"的对比结构
- **核心机制一句话:** 格式 `[动作] + [对象] + [方式] + [效果]`

---

#### 动机与第一性原理 (Motivation & First Principles)

**Done = 以下三项全部完成：**
- **痛点:** 引用至少2个具体baseline的具体数字（如"OLMo 2在MATH仅49.2% vs Qwen 2.5的80.2%"）
- **核心洞察:** Because→Therefore因果链至少3步，每步有论据支撑
- **物理/直觉解释:** 用一个完整类比覆盖整个方法，不堆砌术语

---

#### 方法详解 (Methodology)

**Done = 以下所有子节全部完成：**

**直觉版:** 引用论文的方法概览图（如Figure 1），逐元素解释旧→新的变化。用简单例子走一遍"旧做一步 → 新做一步 → 差异在哪"。

**精确版:**
- 流程图：完整的 Input→...→Output 数据流，标注每步的数据shape变化
- 关键公式：每个核心公式列出，每个符号给出数学定义+物理含义
- 数值推演：代入具体数字（如batch=2, dim=4）逐步推演，展示中间结果
- 伪代码：Python/PyTorch风格，关键处注释Tensor维度

**设计决策:** 对每个非trivial设计选择：替代方案是什么？论文是否对比？核心trade-off？

**易混淆点:** 至少2个"❌错误理解 / ✅正确理解"对

---

#### 实验与归因 (Experiments & Attribution)

**Done = 以下全部完成：**
- **对比表格:** 至少输出2张markdown表格（如base model结果表 + post-train结果表），数字从论文原文提取，不得编造
- **归因排序:** 按贡献大小排列各组件，每个组件引用ablation中的具体数字（如"CraneMath 5.6B tokens → MATH +18.5pt"）
- **可信度检查:** 至少检查3个维度：评估去污染？baseline调优公平性？是否有未报告的负面结果？

---

#### 专家批判 (Critical Review)

**Done = 以下全部完成：**
- **隐性成本:** 列出至少3个论文未明说的具体代价，必须包含数字（如"训练因稳定性问题浪费1天"、"评估占总计算10-20%"、"32B推理需20个H100节点"）
- **最值得复用的技术:** 明确指出1-2个可以直接拿来用的方法，说明为什么
- **最大的坑:** 明确指出复现/落地中最可能踩的1-2个坑
- **关联技术:** 与至少2个现有技术（如其他同期论文、经典方法）做具体对比

---

#### 机制迁移分析 (Mechanism Transfer Analysis)

**Done = 以下全部完成：**

**机制解耦表格:** 拆解为2-4个计算原语，每个原语四列全部填写（名称/本文用途/抽象描述/信息论直觉）

**迁移处方:** 每个原语至少1个跨领域场景，四要素缺一不可：
- 目标领域+具体问题
- 怎么接（输入→替换哪个组件→输出）
- 预期收益
- 风险或不适用条件

**机制家族图谱:**
- 前身(Ancestors)：至少3个，标注每个与本文的具体关系
- 兄弟(Siblings)：至少2个同期工作
- 后代(Descendants)：从论文正文引用中提取，或标注"暂无（新论文）"
- 创新增量：一句话总结本文在族谱中的独特位置

---

#### 背景知识补充 (Background Context)

**Done = 论文中每个被依赖的外部技术/概念，给出：**
- 一句话定义
- 在本文中的具体角色（如"用作X的Y组件"）
- 核心引用

如果论文不依赖大量外部知识，可省略此节。

---

### 质量自检（写完后逐项核实）

- [ ] TL;DR 包含具体数字
- [ ] 痛点引用了具体baseline数字
- [ ] 因果链至少3步
- [ ] 方法详解有公式+数值推演+伪代码
- [ ] 实验部分有至少2张对比表格
- [ ] 归因分析每个组件有具体数字
- [ ] 专家批判有至少3个带数字的隐性成本
- [ ] 机制迁移每个原语有完整迁移处方（4要素）
- [ ] 机制家族前身/兄弟各至少3/2个
- [ ] 所有分析用中文

## Step 4: Save to knowledge base

```bash
deepaper save <arxiv_id> --category <category> --input /tmp/deepaper_analysis.md
```

Category 选择（按论文主要贡献）：
- `llm/pretraining` `llm/alignment` `llm/reasoning` `llm/efficiency` `llm/agent`
- `recsys/matching` `recsys/ranking` `recsys/llm-as-rec` `recsys/generative-rec` `recsys/system`
- `multimodal/vlm` `multimodal/generation` `multimodal/understanding`
- `misc`

## Step 5: Citations (optional)

Run `deepaper cite <arxiv_id> --update` to fetch real citation data and inject into the note.
