Analyze an arxiv paper and save to the deepaper knowledge base using a multi-agent pipeline.

## Step 0: Setup

Run `which deepaper` to check. If not found: `pip install deepaper && deepaper init`.
If papers/ directory exists, skip init.

## Step 1: Download & Prepare

```bash
deepaper download $ARGUMENTS
```
Parse the JSON output to get `pdf_path` and `arxiv_id`.

Then **always** extract full text (mandatory, not optional):
```bash
python3 -c "
import fitz
doc = fitz.open('PDF_PATH')
with open('/tmp/ARXIV_ID.txt', 'w') as f:
    for i, page in enumerate(doc):
        f.write(f'--- PAGE {i+1} ---\n{page.get_text()}\n')
print(f'Total pages: {len(doc)}')
"
```

Also count tables and figures:
```bash
grep -o "Table [0-9]*" /tmp/ARXIV_ID.txt | sort -t' ' -k2 -n -u | tail -1
grep -o "Figure [0-9]*" /tmp/ARXIV_ID.txt | sort -t' ' -k2 -n -u | tail -1
```

Record: `TOTAL_PAGES`, `MAX_TABLE`, `MAX_FIGURE`, `PDF_PATH`, `TEXT_PATH=/tmp/ARXIV_ID.txt`.

## Step 2: Multi-Agent Pipeline

You are the **Conductor**. You do NOT read the paper yourself or write the analysis yourself. You orchestrate 4 agents:

```
Conductor (you)
  ├→ [1] Extractor    — reads paper, outputs structured notes
  ├→ [2] Writer-A     — writes Part A (frontmatter → methodology)     ┐ parallel
  ├→ [3] Writer-B     — writes Part B (experiments → background)      ┘
  ├→ [4] Critic       — quality gate audit, outputs verdict
  └→ [5] (if needed)  — fix specific sections per Critic's verdict
```

### Step 2.1: Spawn Extractor

Launch one Agent (subagent_type: `executor`, name: `extractor`):

**Prompt to Extractor — copy EXACTLY, filling in PDF_PATH, TEXT_PATH, TOTAL_PAGES, ARXIV_ID:**

```
You are a paper extraction specialist. Your ONLY job is to read an academic paper and output structured notes. Do NOT write any analysis or opinions.

## Paper
- PDF: {PDF_PATH}
- Text: {TEXT_PATH}
- Pages: {TOTAL_PAGES}
- ID: {ARXIV_ID}

## Task

Read the ENTIRE paper (every page including Appendix) using the PDF Read tool. Read in chunks of 20 pages, issue 2-3 parallel Read calls per round. You MUST cover pages 1 through {TOTAL_PAGES} — no skipping.

After reading, write structured notes to `/tmp/{ARXIV_ID}_notes.md` in EXACTLY this format. Every number MUST include its source (Table/Figure/Page number). Do not invent numbers.

```markdown
# Notes: {ARXIV_ID}

## META
- title:
- authors (first 5 + "et al."):
- date:
- pages: / tables: / figures:
- code_url:
- venue:

## MAIN RESULTS (copy every number from main result tables)
### Table X: [title]
[reproduce the full table in markdown — ALL rows, ALL columns, no omissions]
### Table Y: ...
(repeat for every main result table: base model tables, post-training tables, instruct tables)

## ABLATIONS (every ablation table with deltas)
### Table X: [title]
[full table + compute delta for key comparisons]
(repeat for all ablation tables)

## HYPERPARAMETERS (from Appendix)
### Table X: [title] (e.g. architecture, training config, SFT/DPO/RL params)
[full table in markdown]
(repeat for every hyperparameter table in the Appendix)

## FORMULAS
### Eq.N: [name]
- formula: (LaTeX)
- each symbol: name = definition (physical meaning)
- key parameter values from paper: ε=..., β=..., etc.
(repeat for every important equation)

## DATA COMPOSITION
### Pretraining
- Source | Type | Pool Size | Final Mix Size | Percentage
(full table)
### Midtraining / Post-training
(same format for each data stage, with token counts)

## EVAL CONFIG (from Appendix evaluation details table)
- Task | Format | Metric | Temp | Top-p | Max Tokens | N | # Subtasks
(full table)

## TRAINING COSTS & TIMELINE
- (every concrete number: days, GPUs, dollars, tokens/sec, etc.)

## DESIGN DECISIONS (non-obvious choices the authors made)
- Decision: X. Alternative: Y. Reason: Z. Evidence: Table/Section.
(list all)

## KEY FINDINGS (verbatim from paper's "Key Findings" sections)
- finding: "..." (section X.Y)
(list all)

## BASELINES (every model compared against, across ALL tables)
- model name (parameter count, type: fully-open/open-weight/closed)
(deduplicated list)
```

IMPORTANT:
- Reproduce tables COMPLETELY — every row, every column. Partial tables are a failure.
- If a table has >15 rows, still include ALL rows.
- Include numbers from the Appendix — hyperparameter tables, eval config tables, data composition tables.
- The notes should be 8,000-15,000 characters. If shorter, you missed tables.
- After writing notes, run: `wc -c /tmp/{ARXIV_ID}_notes.md` and report the count.
```

Wait for Extractor to complete. Verify notes exist and are >5,000 chars:
```bash
wc -c /tmp/ARXIV_ID_notes.md
```
If <5,000 chars, the extraction failed — re-run with explicit instructions to include all tables.

### Step 2.2: Spawn Writer-A and Writer-B in parallel

Launch TWO agents simultaneously (both subagent_type: `executor`), named `writer-a` and `writer-b`.

**Prompt to Writer-A — copy EXACTLY, filling in variables:**

```
You are a technical paper analyst writing Part A of a structured analysis. Write in Chinese (中文).

## Inputs
- Structured notes: /tmp/{ARXIV_ID}_notes.md (READ THIS FIRST)
- Full text for grep: {TEXT_PATH}
- PDF for visual verification: {PDF_PATH}

## Your job
Write ONLY these sections to `/tmp/{ARXIV_ID}_part_a.md`. Follow the format exactly.

### Section 1: YAML Frontmatter

```yaml
---
venue: "发表场所，未找到则 null"
publication_type: "conference/journal/preprint/workshop/thesis"
doi: null
keywords:
  - 5-10个技术关键词
tldr: "一句话核心贡献（≤100字，必须含具体数字如 MATH 96.2%）"
core_contribution: "new-method/new-dataset/new-benchmark/new-framework/survey/empirical-study/theoretical"
baselines:
  - (从notes的BASELINES段落复制完整列表)
datasets:
  - "每个数据集必须标注 token 数/样本数和组成比例"
  - "格式: DatasetName (X tokens/samples: A% Source1 + B% Source2)"
  - "从 notes 的 DATA COMPOSITION 段逐项转换"
  - "评测数据集也列出"
metrics:
  - "每个指标必须标注评测配置"
  - "格式: MetricName (format, temp=X, top-p=Y, max_tokens=Z, N=K)"
  - "从 notes 的 EVAL CONFIG 表逐项转换"
code_url: "(从 notes META 段)"
---
```

**Frontmatter GATE:** 写完 frontmatter 后立即检查：
- datasets 每项是否有 token 数？如缺，grep TEXT_PATH 找到并补充
- metrics 每项是否有 eval config？如缺，grep "Table" TEXT_PATH 找到 Appendix eval table 的页码，Read PDF 那几页补充

### Section 2: 核心速览 (Executive Summary)

- **TL;DR:** 必须含具体量化数字（如"MATH 96.2%"），不接受"显著提升"
- **一图流:** "旧方法是X → 新方法是Y"的对比结构
- **核心机制一句话:** `[动作] + [对象] + [方式] + [效果]`

### Section 3: 动机与第一性原理 (Motivation & First Principles)

- **痛点:** 引用≥2个baseline的具体数字（从notes MAIN RESULTS段取）
- **核心洞察:** Because→Therefore因果链≥3步，每步有论据
- **物理/直觉解释:** 一个完整类比

### Section 4: 方法详解 (Methodology)

**字符数 GATE: ≥12,000 字符。写完后立即 `wc -c` 检查。不足则从 notes 的 HYPERPARAMETERS 和 FORMULAS 段补充。**

包含：
- **直觉版:** 引用 Figure (方法概览图)，旧→新对比
- **精确版:**
  - 完整数据流图 (Input→...→Output)，从 notes DATA COMPOSITION 段取数字
  - 关键公式：从 notes FORMULAS 段复制，补充物理含义
  - 数值推演：用具体数字走一遍核心算法
  - 伪代码：Python/PyTorch 风格
  - **超参数表：** 从 notes HYPERPARAMETERS 段复制为 markdown 表格（必须包含 Appendix 的完整表）
- **设计决策:** 从 notes DESIGN DECISIONS 段展开，每个标注替代方案和 trade-off
- **易混淆点:** ≥3个 "❌错误理解 / ✅正确理解" 对

**写完后执行：**
```bash
# 字符数检查
python3 -c "
text = open('/tmp/{ARXIV_ID}_part_a.md').read()
method_start = text.find('#### 方法详解')
method_end = text.find('#### 实验') if '#### 实验' in text else len(text)
method_chars = len(text[method_start:method_end]) if method_start >= 0 else 0
print(f'Methodology chars: {method_chars}')
if method_chars < 12000: print('WARNING: BELOW 12K GATE — add more hyperparameter tables and formulas')
"
```
如果 <12,000，从 notes 补充直到达标。
```

**Prompt to Writer-B — copy EXACTLY:**

```
You are a technical paper analyst writing Part B of a structured analysis. Write in Chinese (中文).

## Inputs
- Structured notes: /tmp/{ARXIV_ID}_notes.md (READ THIS FIRST)
- Full text for grep: {TEXT_PATH}
- PDF for visual verification: {PDF_PATH}

## Your job
Write ONLY these sections to `/tmp/{ARXIV_ID}_part_b.md`. Follow the format exactly.

### Section 5: 实验与归因 (Experiments & Attribution)

- **对比表格:** ≥2张完整 markdown 表格。从 notes MAIN RESULTS 段的完整表格转录。**包含 ALL baselines，不能只挑 top-3。** 如果 notes 有4张主表，输出4张。
- **归因排序:** 从 notes ABLATIONS 段按 delta 大小排序，每个组件标注具体数字
- **可信度检查:** ≥3个维度（去污染、baseline公平性、未报告负面结果——从 notes KEY FINDINGS 段找线索）

### Section 6: 专家批判 (Critical Review)

- **隐性成本:** ≥3个论文未明说的代价，必须含数字。从 notes TRAINING COSTS 段 + 论文 footnotes 提取。如不足3个，grep TEXT_PATH 搜索 "day" "hour" "cost" "GPU" "node" "Lambda" 等关键词定位隐藏成本。
- **最值得复用的技术:** 1-2个可直接复用的方法
- **最大的坑:** 1-2个复现/落地的坑
- **关联技术:** ≥2个同期/经典方法对比

### Section 7: 机制迁移分析 (Mechanism Transfer Analysis)

- **机制解耦表格:** 2-4个计算原语，四列全填（名称/本文用途/抽象描述/信息论直觉）
- **迁移处方:** 每个原语≥1个跨领域场景，四要素缺一不可（目标领域+怎么接+预期收益+风险）
- **机制家族图谱:**
  - 前身(Ancestors)：≥3个，标注与本文关系
  - 兄弟(Siblings)：≥2个同期工作
  - 后代(Descendants)：从引用提取或标注"暂无"
  - 创新增量：一句话

### Section 8: 背景知识补充 (Background Context)

论文中每个被依赖的外部技术：一句话定义 + 在本文中的角色 + 核心引用。

**写完后执行隐性成本计数：**
```bash
python3 -c "
text = open('/tmp/{ARXIV_ID}_part_b.md').read()
import re
cost_section = text[text.find('隐性成本'):text.find('最值得复用')] if '隐性成本' in text else ''
numbers = re.findall(r'\d+[\d,.]*\s*(?:天|day|hour|小时|GPU|node|节点|美元|\$|%|倍|x|Mtok|万|M|B|K|T)', cost_section)
print(f'Hidden costs with numbers: {len(numbers)} occurrences found')
if len(numbers) < 3: print('WARNING: BELOW 3 HIDDEN COSTS GATE')
"
```
```

### Step 2.3: Concatenate

After both writers complete, concatenate:

```bash
cat /tmp/ARXIV_ID_part_a.md /tmp/ARXIV_ID_part_b.md > /tmp/deepaper_analysis.md
wc -c /tmp/deepaper_analysis.md
```

### Step 2.4: Spawn Critic

Launch one Agent (subagent_type: `code-reviewer` or `critic`, name: `critic`):

**Prompt to Critic — copy EXACTLY:**

```
You are a quality auditor for academic paper analyses. Your job is to check a draft analysis against mandatory quality gates and output a structured verdict. You do NOT rewrite — you only diagnose.

## Input
- Draft analysis: /tmp/deepaper_analysis.md
- Paper notes (ground truth for fact-checking): /tmp/{ARXIV_ID}_notes.md

Read both files completely.

## Quality Gates — check each one

Run the following checks and report results:

### Gate 1: TL;DR contains specific numbers
- Look for the TL;DR line. Does it contain at least 2 specific benchmark numbers (e.g., "MATH 96.2%")?
- PASS/FAIL

### Gate 2: Pain points cite baseline numbers
- In "动机与第一性原理", are there ≥2 specific baseline numbers (e.g., "OLMo 2 MATH 49.2%")?
- PASS/FAIL

### Gate 3: Causal chain ≥3 steps
- Count Because→Therefore or numbered causal steps
- PASS(N steps)/FAIL

### Gate 4: Methodology ≥12,000 characters
```bash
python3 -c "
text = open('/tmp/deepaper_analysis.md').read()
# Find methodology section
starts = ['#### 方法详解', '## 方法详解', '### 方法详解']
end_markers = ['#### 实验', '## 实验', '### 实验']
start = -1
for s in starts:
    if s in text: start = text.find(s); break
end = len(text)
for e in end_markers:
    if e in text and text.find(e) > start: end = text.find(e); break
if start >= 0:
    chars = len(text[start:end])
    print(f'Methodology: {chars} chars')
    print('PASS' if chars >= 12000 else 'FAIL')
else:
    print('FAIL: methodology section not found')
"
```
- PASS(N chars)/FAIL(N chars, need +M more)

### Gate 5: ≥2 complete comparison tables
- Count markdown tables in 实验 section that have ≥5 rows and ≥4 columns
- PASS(N tables)/FAIL

### Gate 6: Attribution has specific numbers
- In 归因排序, does each component cite a specific delta number?
- PASS/FAIL + list components missing numbers

### Gate 7: ≥3 hidden costs with numbers
- In 隐性成本, count distinct cost items that include a number
- PASS(N costs)/FAIL

### Gate 8: Transfer prescriptions complete
- For each 迁移处方, check all 4 elements: 目标领域, 怎么接, 预期收益, 风险
- PASS/FAIL + which prescriptions are incomplete

### Gate 9: Mechanism family counts
- Ancestors ≥3, Siblings ≥2
- PASS(A ancestors, S siblings)/FAIL

### Gate 10: Frontmatter completeness
- datasets: each entry has token count or sample count?
- metrics: each entry has eval config (temp, N, max_tokens)?
- PASS/FAIL + list incomplete entries

### Gate 11: Factual consistency with notes
- Sample 5 numbers from the draft analysis. Look up each in the notes. Do they match?
- PASS/FAIL + list mismatches

## Output format

Write your verdict to `/tmp/{ARXIV_ID}_verdict.md`:

```markdown
# Quality Verdict: {ARXIV_ID}

## Gate Results
| # | Gate | Result | Details |
|---|------|--------|---------|
| 1 | TL;DR numbers | PASS/FAIL | ... |
| 2 | Pain point baselines | PASS/FAIL | ... |
...

## Failed Gates — Required Actions
(only if any gate failed)

### Gate N: [name] — FAIL
**Problem:** ...
**Action:** [specific instruction for what to add/fix, referencing notes sections]
**Location:** [which section of the draft to modify]

## Factual Issues
(if any numbers don't match notes)

## Overall: PASS / NEEDS REVISION (N gates failed)
```
```

### Step 2.5: Handle Critic Verdict

Read `/tmp/ARXIV_ID_verdict.md`.

**If PASS:** Go to Step 3.

**If NEEDS REVISION:** For each failed gate, either:
- (a) Fix it yourself (for simple additions like adding a missing number), OR
- (b) Spawn a targeted `executor` agent with a specific fix prompt:

```
Fix the following issues in /tmp/deepaper_analysis.md:

1. [paste failed gate action from verdict]
2. [paste failed gate action from verdict]

Reference data is in /tmp/{ARXIV_ID}_notes.md.
Paper text for grep is at {TEXT_PATH}.

Edit the file directly using the Edit tool. Do NOT rewrite the entire file — only patch the specific sections mentioned above.
```

After fixes, optionally re-run Critic (max 2 total rounds). If still failing after 2 rounds, save anyway with a note.

## Step 3: Save

```bash
deepaper save ARXIV_ID --category CATEGORY --input /tmp/deepaper_analysis.md
```

Category choices:
- `llm/pretraining` `llm/alignment` `llm/reasoning` `llm/efficiency` `llm/agent`
- `recsys/matching` `recsys/ranking` `recsys/llm-as-rec` `recsys/generative-rec` `recsys/system`
- `multimodal/vlm` `multimodal/generation` `multimodal/understanding`
- `misc`

## Step 4: Citations (optional)

```bash
deepaper cite ARXIV_ID --update
```

## Reference: Section Template (for Writer agents)

Each section heading uses `####` (h4). The full analysis structure is:

```
---
(YAML frontmatter)
---
#### 核心速览 (Executive Summary)
#### 动机与第一性原理 (Motivation & First Principles)
#### 方法详解 (Methodology)
#### 实验与归因 (Experiments & Attribution)
#### 专家批判 (Critical Review)
#### 机制迁移分析 (Mechanism Transfer Analysis)
#### 背景知识补充 (Background Context)
```
