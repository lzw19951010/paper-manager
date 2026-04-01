# deepaper 管线纪律性增强设计

> 核心目标：让执行过程更有纪律性，保障论文分析的完整性与质量。

## 1. 增强后的管线架构

```
Download
  → 文本提取 + text_by_page + visual_registry + 灵魂图识别 + figure_contexts（全部程序化）
  → Extractor（读纯文本，轻量串联，产出结构化大纲）
  → StructCheck（程序化：11 个 section header 存在性 + 动态最小字符数）
      → 缺失 section → Extractor 补写（仅补缺失部分，最多 1 次）
  → Auditor（程序化：页码覆盖率审计）
      → 发现整段页面被跳过 → Extractor 针对性补充
  → Writer-Visual / Writer-Text-1 / Writer-Text-2 并行
      ├─ Writer-Visual：notes + figure_contexts + Table PDF 页（按需）
      ├─ Writer-Text-1：notes + figure_contexts
      └─ Writer-Text-2：notes + figure_contexts
  → Merge（固定顺序拼接）
  → HardGates（程序化：8 项可量化规则，毫秒级）
      → 失败直接进 Fixer，不浪费 Critic token
  → SoftGates / Critic（LLM 语义审查：7 项语义规则）
  → Fixer（最多 2 轮，选最佳版本）
      → 仍失败 → 降级保存 (quality: partial)
  → Save + Pipeline Report + Frontmatter 质量标记
```

### 实现路径

Slash command 重写（`.claude/commands/deepaper.md`）+ 新增 Python 模块。Agent 编排只能在 Claude Code slash command 中执行，这是架构硬约束。程序化校验作为 CLI 子命令，slash command 调用。

## 2. 文件结构

### 新增模块

```
src/deepaper/
  ├── registry.py      # visual_registry 构建 + 灵魂图识别 + figure_context 提取
  ├── gates.py          # HardGates 程序化校验 + 覆盖率检查 + 数字指纹
  ├── extractor.py      # StructCheck + Auditor
  ├── analyzer.py       # 现有，不变
  ├── writer.py         # 现有，write_paper_note 增加 quality/failed_gates/pipeline_version 字段
  ├── cli.py            # 现有，新增子命令 gates / registry / report
  └── ...
```

### 运行时目录（项目内，gitignore）

```
.deepaper/
  └── runs/
      └── {ARXIV_ID}/
          ├── text.txt               # 全文文本
          ├── text_by_page.json      # 按页分段
          ├── visual_registry.json   # 图表注册表
          ├── figure_contexts.json   # 灵魂图文本描述
          ├── notes.md               # Extractor 笔记
          ├── part_visual.md         # Writer-Visual 输出
          ├── part_text1.md          # Writer-Text-1 输出
          ├── part_text2.md          # Writer-Text-2 输出
          ├── merged.md              # 合并后全文
          └── report.json            # Pipeline Report
```

`.gitignore` 新增：`.deepaper/`

## 3. registry.py — 图表注册表与灵魂图

### 3.1 build_visual_registry(text_by_page) → dict

从提取的文本中构建图表注册表。通过正则匹配 `Table/Figure/Fig. + 编号` 找到所有引用，通过 caption 模式（`Table 1:` / `Figure 2.`）定位定义页。

包含完整性校验：编号连续性检查，有引用无 caption 则报警。

产出示例：

```json
{
  "Table_1": {"type": "Table", "id": "1", "pages": [3,5,8], "definition_page": 8, "has_caption": true},
  "Figure_1": {"type": "Figure", "id": "1", "pages": [1,3,5,8,12], "definition_page": 2, "has_caption": true, "is_core": true, "core_score": 5}
}
```

### 3.2 identify_core_figures(registry, text_by_page, total_pages) → list

识别论文的"灵魂图"——承载核心 idea 的 Figure。

**5 个评分信号**：

| 信号 | 条件 | 分值 |
|------|------|------|
| 全文引用频次 | ≥ 3 次 | +1 |
| 在 Introduction 中被引用 | 前 20% 页面 | +1 |
| 定义位置靠前 | 前 30% 页面 | +1 |
| Caption 长度 | > 80 字符 | +1 |
| 编号 | ≤ 2 | +1 |

**反通胀机制**：

- 硬顶：MAX_CORE = 3
- 比例上限：不超过总 Figure 数的 20%
- 竞争上岗：按 score 排序取 top-K，不是达标即入选
- 最低分门槛：score ≥ 3
- budget = min(MAX_CORE, max(1, int(total_figures * 0.2)))

### 3.3 extract_figure_contexts(text_by_page, core_figures) → dict

对每个灵魂图，从正文中提取其 caption + 所有引用该 Figure 的段落。

**设计决策：不读 PDF 图片**。原因：LLM 处理图片的信息密度低于文本。一段 200-500 tokens 的文字描述对 LLM 来说信息量大于一张 3000-4000 tokens 的图片。论文的文字描述 + caption 足以传达 Figure 的核心思想。

产出示例：

```json
{
  "Figure_1": {
    "caption": "Overview of our MoE architecture with auxiliary-loss-free load balancing...",
    "references": [
      "As illustrated in Figure 1, we replace the traditional top-k routing with...",
      "The key insight behind our design (Figure 1) is that by decoupling..."
    ]
  }
}
```

## 4. extractor.py — StructCheck + Auditor

### 4.1 StructCheck

Extractor 产出 `notes.md` 后，程序化检查 11 个必需 section header 是否存在，以及每个 section 的动态最小字符数。

**11 个必需 section**：META, MAIN_RESULTS, ABLATIONS, HYPERPARAMETERS, FORMULAS, DATA_COMPOSITION, EVAL_CONFIG, TRAINING_COSTS, DESIGN_DECISIONS, RELATED_WORK, BASELINES

**阈值来源**：`paper_profile`（论文原文的物理特征），不依赖任何 LLM 输出。

变量映射（来自 `paper_profile["section_chars"]`）：
- `experiment_chars` = `section_chars.get("Experiments", 0) + section_chars.get("Results", 0)`
- `method_chars` = `section_chars.get("Method", 0) + section_chars.get("Methodology", 0) + section_chars.get("Approach", 0)`
- `related_chars` = `section_chars.get("Related Work", 0) + section_chars.get("Background", 0)`

```python
extractor_thresholds = {
    "META":             200,   # 固定，元信息量稳定
    "MAIN_RESULTS":     max(300, int(experiment_chars * 0.3)),
    "ABLATIONS":        max(200, int(experiment_chars * 0.15)),
    "HYPERPARAMETERS":  max(100, int(total_pages * 20)),
    "FORMULAS":         max(50,  num_equations * 30),
    "DATA_COMPOSITION": max(100, int(total_pages * 15)),
    "EVAL_CONFIG":      max(100, int(experiment_chars * 0.1)),
    "TRAINING_COSTS":   100,   # 固定，论文可能未提供
    "DESIGN_DECISIONS": max(100, int(method_chars * 0.15)),
    "RELATED_WORK":     max(200, int(related_chars * 0.3)),
    "BASELINES":        max(100, num_tables * 50),
}
```

**失败处理**：将 missing/thin sections 列表回传给 Extractor，要求仅补充这些 section。

### 4.2 Auditor

程序化对比论文页码范围与 notes 内容覆盖情况。

- 将论文分为若干区段（每 10 页一段）
- 每个区段提取特征词（高频专有名词、数字）
- 检查 notes 中是否包含每个区段的特征词
- 覆盖率 < 30% 的区段视为未覆盖

**失败处理**：要求 Extractor 针对性读取未覆盖区段的文本并补充 notes。

### 4.3 重试纪律

StructCheck + Auditor 合计给 Extractor **最多 1 次补充机会**。补充后仍不通过的 section 标记为 `"⚠️ 论文未提供该信息"`，不再循环。

## 5. paper_profile — 独立于 LLM 的 Ground Truth

所有阈值的锚点。完全从 PDF 文本提取中程序化获得，不依赖任何 LLM 输出。

```python
def compute_paper_profile(text_by_page, visual_registry):
    full_text = "\n".join(text_by_page.values())
    total_pages = len(text_by_page)
    
    paper_sections = detect_paper_sections(full_text)
    # e.g. {"Introduction": 4200, "Method": 8500, "Experiments": 12000}
    
    subsection_headings = detect_subsection_headings(full_text)
    # e.g. ["2.1 Multi-Head Latent Attention", "2.2 DeepSeekMoE ..."]
    
    num_tables = sum(1 for v in visual_registry.values()
                     if v["type"].startswith("Table") and v.get("has_caption"))
    num_figures = sum(1 for v in visual_registry.values()
                      if v["type"].startswith("Fig") and v.get("has_caption"))
    num_equations = len(re.findall(r'(?:Eq\.|Equation)\s*\(?(\d+)', full_text))
    
    return {
        "total_pages": total_pages,
        "total_chars": len(full_text),
        "section_chars": paper_sections,
        "subsection_headings": subsection_headings,
        "num_tables": num_tables,
        "num_figures": num_figures,
        "num_equations": num_equations,
    }
```

**Fallback**：如果 `detect_paper_sections()` 检测不到 section 结构，用 `total_pages` 作为粗粒度锚点，仅影响 extractor_thresholds 的动态计算（退化为固定下限值）。

```python
if not profile["section_chars"]:
    # 所有动态阈值退化为固定下限
    experiment_chars = 0
    method_chars = 0
    related_chars = 0
    # extractor_thresholds 中的 max() 确保每个 section 仍有合理最小值
```

### 依赖链（无循环）

```
PDF 原文（不可变 ground truth）
    ↓ 程序化提取
paper_profile（页数、section 字符数、表格数、公式数）
    ↓ 推导
thresholds
    ↓ 校验
Extractor notes（StructCheck / Auditor）
Writer output（HardGates）
```

## 6. gates.py — HardGates + 覆盖率检查 + 数字指纹

### 6.1 HardGates（程序化，8 项）

在 Critic 之前执行，毫秒级。

| ID | 检查内容 | 依据来源 | 说明 |
|----|---------|---------|------|
| H1 | Baselines 格式 | YAML 字段正则 | 一行一个，含参数量和类型 |
| H2 | 结构元素覆盖率 ≥ 60% | 论文自身 heading/equation/table/figure | 见 6.2 |
| H3 | 各 section 字符下限 | 固定极低值（防白卷） | 方法 2K, 实验 1.5K, 速览 500 等 |
| H4 | 实验表格数 ≥ registry Table 数 | visual_registry | markdown table 正则计数 |
| H5 | TL;DR ≥ 2 个数字 | 固定 | tldr YAML 字段正则 |
| H6 | 标题层级 h4/h5/h6 only | 固定 | 不存在 `^#{1,3}\s` 或 `^#{7,}\s` |
| H7 | 灵魂图全部被引用 | core_figures | 每个 core figure ID 在输出中出现 |
| H8 | 数字指纹可追溯 | text_by_page 中 Table 页数字集合 | 见 6.3 |

### 6.2 结构元素覆盖率（H2）

覆盖清单来源于论文**显式声明**了重要性的结构元素，不做语义推断：

- **子章节标题**：论文的 subsection heading（作者认为重要到需要单独一节）
- **编号公式**：Eq. 1 ... Eq. N（作者认为重要到需要编号）
- **Table 引用**：registry 中有 caption 的 Table
- **灵魂图引用**：core_figures

校验方式：正则匹配每个元素是否在 merged output 中出现。覆盖率 ≥ 60% 通过。

60% 而非更高，因为背景补充类 section 可能合理省略某些公式，不是每张 Table 都需要在分析中单独引用。

### 6.3 数字指纹校验（H8）

防止 Writer 编造实验数据。

1. 从 `text_by_page` 中每个 Table 定义页提取所有数值，构建指纹集合
2. 从 Writer 输出的 markdown 表格中提取数字
3. 交叉校验：>30% 的数字无法追溯到源文本 → 标记为可疑

**H8 失败时的特殊处理**：识别 suspect_tables → 读取该 Table 定义页的 PDF → 喂给 Fixer 重写。这是整条管线中唯一因质量校验触发 PDF 读取的场景。

### 6.4 行列覆盖率

源文本数字量远大于 Writer 输出（`len(source) > 5 and len(writer) < len(source) * 0.5`）→ 可能省略了行。作为 H8 的补充信号。

### 6.5 CLI 接口

```bash
deepaper gates hard --input .deepaper/runs/{ARXIV_ID}/merged.md \
                    --registry .deepaper/runs/{ARXIV_ID}/visual_registry.json \
                    --profile .deepaper/runs/{ARXIV_ID}/paper_profile.json
```

输出 JSON：

```json
{
  "passed": false,
  "results": {
    "H1": {"passed": true},
    "H2": {"passed": false, "coverage": 0.52, "missing": ["heading:3.2 Expert Routing", "equation:5"]},
    "H8": {"passed": false, "untraced_ratio": 0.42, "suspect_tables": ["Table_3"]}
  },
  "failed": ["H2", "H8"]
}
```

## 7. SoftGates / Critic（LLM 语义审查，7 项）

HardGates 全部通过后才执行。

| ID | 规则 | 为什么需要 LLM |
|----|------|--------------|
| S1 | 痛点引用 ≥ 2 个 baseline 及数字 | 需理解"痛点"语义 |
| S2 | 因果链 ≥ 3 步逻辑递进 | 需理解逻辑关系 |
| S3 | 消融排序按贡献度排列 | 需理解 delta 的含义方向 |
| S4 | 可信度：无明显过拟合迹象 | 需要领域判断 |
| S5 | 隐藏成本 ≥ 3 个且量化 | "隐藏"需要推理 |
| S6 | 可迁移技术的跨领域分析 | 需要创造性判断 |
| S7 | 家族谱系完整性（≥ 4 祖先、≥ 3 兄弟） | 分类需语义 |

**Critic 输出格式**（强制 JSON，Conductor 可解析）：

```json
{
  "verdict": "fail",
  "passed": ["S1", "S3", "S4", "S6"],
  "failed": [
    {"id": "S2", "reason": "因果链只有2步，缺少从XX到YY的推导"},
    {"id": "S5", "reason": "隐藏成本只列了2个，且第2个未量化"}
  ]
}
```

## 8. Writer 分组与资源分配

### 动态分组

按资源依赖分组，不固定 A/B/C：

| Writer | Section | 输入 | PDF 读取 |
|--------|---------|------|---------|
| Writer-Visual | 方法详解 + 实验与归因 | notes + figure_contexts + Table PDF 页（按需） | 是（仅 Table 页） |
| Writer-Text-1 | YAML + 核心速览 + 动机与第一性原理 + 专家批判 | notes + figure_contexts | 否 |
| Writer-Text-2 | 机制迁移分析 + 背景知识补充 | notes + figure_contexts | 否 |

`figure_contexts`（灵魂图文本描述）作为全局上下文广播给三个 Writer。

### 分组逻辑

```python
def assign_writer_groups(visual_registry):
    visual_sections = ["方法详解"]
    if any(v for v in visual_registry.values() if v["type"].startswith("Table")):
        visual_sections.append("实验与归因")
    
    text_sections_1 = ["YAML frontmatter", "核心速览", "动机与第一性原理", "专家批判"]
    text_sections_2 = ["机制迁移分析", "背景知识补充"]
    
    return {
        "writer_visual": visual_sections,
        "writer_text_1": text_sections_1,
        "writer_text_2": text_sections_2,
    }
```

极端情况：无 Table 的纯理论论文，"实验与归因" 归入文本组，Writer-Visual 只写方法详解。

### 合并顺序

```
Writer-Text-1 → Writer-Visual → Writer-Text-2
```

最终 section 顺序：YAML → 核心速览 → 动机与第一性原理 → 方法详解 → 实验与归因 → 专家批判 → 机制迁移分析 → 背景知识补充

## 9. Fixer 循环与降级保存

### 重试纪律

- 最大轮数：2
- 每轮只修复失败项，Fixer 收到精确的 gate ID + 原因 + 量化差距
- 修复后重跑全量 HardGates + SoftGates（防止修了 A 破坏 B）
- 2 轮后仍失败 → 降级保存

### 降级保存策略

选择 2 轮中通过门控最多的版本（最佳版本，非最后版本），注入质量标记后保存。

### Fixer prompt 结构

```
## 修复任务
以下质量门控未通过，请仅修复这些问题，不要改动已通过的部分。

### 失败清单
{gates_json}

### 当前全文
{merged_md}

### 规则
- 只修改与失败门控相关的 section
- 不要删除或缩减已有内容
- 所有新增数字必须来自 Extractor 笔记
- 输出完整的修改后全文
```

## 10. Pipeline Report 与 Frontmatter 质量标记

### Frontmatter 新增字段

```yaml
quality: full              # full | partial
failed_gates: []           # partial 时列出未通过的 gate ID
pipeline_version: 2        # 区分新旧管线产出
```

Obsidian 中可用 Dataview 筛选 `quality: partial` 的笔记集中复查。

### Pipeline Report

保存在 `.deepaper/runs/{ARXIV_ID}/report.json`，包含：

- `paper_profile`：论文物理特征
- `thresholds`：动态推导的阈值
- `extractor`：StructCheck + Auditor 结果和重试次数
- `writers`：各 Writer 的 section 分配、字符数、PDF 页读取
- `hard_gates`：8 项结果（含 skipped 标记）
- `soft_gates`：7 项结果
- `fixer`：轮数、每轮结果、最佳轮次
- `quality`：最终质量标记
- `total_pdf_pages_read`：图片 token 消耗追踪

### Report 用途

| 场景 | 用法 |
|------|------|
| 调试单篇 | 查看哪个 gate 失败、Fixer 改了几轮 |
| 批量分析 | 聚合多篇 report，统计哪些 gate 最常失败 → 优化 prompt |
| Token 审计 | total_pdf_pages_read 追踪图片 token 消耗 |
| 管线迭代 | 对比 pipeline_version 1 vs 2 的质量分布 |

## 11. JSON 容错处理

核心原则：JSON 是辅助产物，不能因为 JSON 读写失败而丢失主产出（markdown 笔记）。

### 统一的安全读写层

```python
def safe_write_json(path, data) -> bool:
    """原子写入：先写 .tmp 再 rename，失败不抛异常"""

def safe_read_json(path, default=None):
    """读取 JSON，损坏或缺失时返回 default"""
```

### 降级策略

| JSON 不可用 | 影响 | 处理 |
|------------|------|------|
| visual_registry | 跳过 H4/H7/H8，标记 skipped | 管线继续 |
| figure_contexts | Writer 少了灵魂图上下文 | 管线继续 |
| text_by_page | 跳过 Auditor + H8 | 管线继续 |
| report.json | 失去可观测性 | 输出摘要到 stdout 兜底 |
| 磁盘满/权限错误 | 所有写入失败 | 回退到 /tmp/{ARXIV_ID}/ |

```
JSON 可用 → 完整管线，全部门控
JSON 不可用 → 跳过依赖该 JSON 的门控，其余正常
所有 JSON 不可用 → 仍能完成 Extractor → Writer → Critic → Save
最终笔记永远不因 JSON 问题而丢失
```

## 12. Token 消耗估算

以典型 40 页论文、13 个视觉页为例：

| 阶段 | 当前 (v1) | 优化后 (v2) | 说明 |
|------|----------|------------|------|
| Extractor | ~120K | ~25K | 纯文本替代全量 PDF 图片 |
| StructCheck + Auditor | — | 0 | 程序化 |
| Writer × 3 | ~36K | ~38K | +figure_contexts 广播（~2K） |
| HardGates | — | 0 | 程序化 |
| Critic | ~17K | ~17K | 不变 |
| Fixer (50% 概率) | ~10K | ~10K | 不变 |
| **合计** | **~183K** | **~90K** | **↓ ~50%** |

额外 PDF 读取（H8 失败触发、Writer-Visual 按需读 Table 页）：~3-15K tokens，按需发生。

## 13. 关键设计决策汇总

| 决策 | 选择 | 原因 |
|------|------|------|
| Critic 模式 | 混合（程序化 + LLM） | 可量化规则不应依赖 LLM 自觉性 |
| 重试策略 | 最多 2 轮 + 降级保存 | 不阻塞管线，标记质量状态便于追溯 |
| Extractor 校验 | StructCheck + Auditor 两者结合 | section 检查成本低，覆盖率审计更彻底 |
| 灵魂图处理 | 提取文本描述，不读 PDF 图片 | LLM 处理文本信息密度高于图片 |
| 灵魂图识别 | 竞争上岗，硬顶 3 张，比例 20% | 防通胀 |
| 图片读取 | 仅 Table 页按需 + H8 失败触发 | 文本提取表格结构会乱，图片确实有优势 |
| Writer 分组 | 按资源依赖动态分组 | PDF 读取集中到一个 Writer |
| 阈值来源 | 论文原文物理特征（paper_profile） | 独立于 LLM 输出，无循环依赖 |
| 内容完整性 | 论文显式结构元素覆盖率 | 不猜测哪些概念重要，用论文自身声明 |
| 字符数检查 | 极低下限，仅防白卷 | 字符数是差的质量代理 |
| 中间产物存储 | 项目内 .deepaper/runs/ | 可追溯、不被 OS 清理、方便对比 |
| JSON 容错 | 原子写入 + 降级跳过 | 辅助产物不能阻塞主产出 |
| Fixer 选版 | 选最佳版本而非最后版本 | 防止后轮修复破坏前轮成果 |
