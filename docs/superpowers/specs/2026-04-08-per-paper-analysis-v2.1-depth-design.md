# Per-Paper Analysis v2.1 — Depth, Figure Assets, and Coverage

## 背景

v2 refactor（`2026-04-07-per-paper-analysis-v2-design.md`）成功把 OLMo 3 的分析从 33K → 8.4K 字符，4 章节 3 writer，199 测试全绿。真实使用后暴露出 4 个新痛点：

1. **ROI 质疑**：10+ 分钟 / 6 agent / 624K token 的 pipeline，产出的 `final.md` 看起来"和我自己写一个 prompt 输出的差不多" — agent workflow 的增量价值没沉淀到 artifact 里
2. **混淆点读不懂**：v2 把每条易混淆点压到 2 行，剥离了上下文和后果，对不熟悉先验的读者变成黑话
3. **图缺失**：Obsidian 打开 `papers/**/*.md` 时，每次读到 `Figure 2 展示了...` 都要 alt-tab 去翻 PDF。视觉信息完全没进入 artifact
4. **H2 gate 与 v2 冲突**：H2 用字符串匹配论文 subsection 名，v2 压缩刻意不复述章节名，导致 H2 永远 fail；去掉 H2 又没有替代机制保障"writer 真的读完了论文"

v2.1 的目标是在**不破坏 v2 4 章节结构 + 不膨胀文件数** 的前提下解决这 4 个痛点，并为未来 LLM Wiki 式演进留接口。

## 非目标

- **不做**跨论文 concept 页面 / mechanism 族谱 / wiki index — 那是 v3 的范畴
- **不做** RAG / embedding 检索 / `deepaper ask` 查询接口 — 那是 v3 的范畴
- **不做** Mermaid 重绘图 — 错绘风险大于收益，β 像素裁剪已经够用
- **不做**双文件分层（`deepdive.md` sidecar）— 用户明确要求"不要过度设计"
- **不做** LLM-Judge 覆盖评分或 notes.md 锚点追踪 — 引入新 agent 成本高，留到 v3
- **不迁移**旧的 v2 输出 — 现存 `papers/llm/pretraining/olmo-3.md` 会被 v2.1 pipeline 重新产出（用户手动 `/deepaper <url>` 触发）

## 设计决策总览

| 维度 | 决策 | 取代 |
|------|------|------|
| **深度交付形态** | 形态 1 — 单文件加厚（`olmo-3.md` 从 ~8K → 12-15K），深度内嵌现有 4 章节 | 不拆 `deepdive.md` sidecar |
| **文件布局** | P2 — `papers/<category>/<slug>/<slug>.md` 子目录包裹 | 当前 `papers/<category>/<slug>.md` 扁平结构 |
| **图像处理** | β — PDF 像素裁剪，存 `./assets/figure-N.png`，writer 用图片语法嵌入 | 现有"Figure N"纯文本引用 |
| **混淆点格式** | 方案 Y 紧凑式 — 3 行 `❌/✅/🚨` + 可选嵌图 | 现有 2 行 `❌/✅` |
| **H2 gate** | 移除 H2 实现逻辑（key 保留为 SKIPPED 避免破坏现有快照），H12 接替"结构覆盖"语义 | 字符串匹配 subsection 名 |
| **新增 H11** | Core figure 图片语法嵌入率必须 100% | 无 |
| **Baseline freeze** | 当前 OLMo 3 v2 输出冻结为 `tests/golden/olmo-3.md` | 无 |
| **arxiv_id 保留** | 继续存在 YAML frontmatter（已有），未来扩展 `papers/INDEX.md`（v3 做） | 无需改动 |

## 架构变更

### 1. 文件布局变更（P2 子目录包裹）

**v2（现状）：**
```
papers/llm/pretraining/
└── olmo-3.md              # 单文件
```

**v2.1（目标）：**
```
papers/llm/pretraining/olmo-3/
├── olmo-3.md              # 主分析（v2.1 加厚版，~12-15K 字符）
└── assets/
    ├── figure-1.png       # PDF 像素裁剪
    ├── figure-2.png
    └── figure-13a.png
```

**关键点：**
- 目录名 = 主文件名 = 论文短名（`olmo-3`），保持 Obsidian 文件列表里目录和主文件并排显示的人体工程学
- `assets/` 固定子目录名（Obsidian / Dataview / wiki 社区约定）
- 每篇论文是自包含单元：`rm -rf papers/llm/pretraining/olmo-3/` 删除所有痕迹
- 未来如要新增 `deepdive.md` / `critique.md` / `source.pdf` 归档，不需要重构结构

**迁移：** v2 的现存 `papers/**/*.md` 文件**不自动迁移**。用户下次 `/deepaper <url>` 触发时 pipeline 自动产出 P2 结构；或者未来提供 `deepaper migrate-layout` 一次性脚本（非本 spec 范围）。

### 2. Extractor 新增：core figure 像素裁剪

**新函数：** `extract_core_figure_images()` in `src/deepaper/extractor.py`

**输入：**
- `core_figures.json`（现有）：每个 core figure 的 `id`, `definition_page`, 可选 `bbox`
- PDF 路径

**流程：**
1. 对每个 core figure，调用 `pdftoppm -f <page> -l <page> -r 150 -png` 将该页渲染为 PNG
2. 如果 `bbox` 存在且可信（坐标在页面范围内），用 PIL/Pillow 裁剪到 bbox
3. 如果 bbox 缺失或不可信，**fallback 到整页截图**（保真优先）
4. 输出到 `.deepaper/runs/<run_id>/figures/figure-<id>.png`
5. 裁剪后的 PNG 若超过 500KB，用 Pillow 按 85% 质量转为 JPEG 降体积

**失败处理：**
- `pdftoppm` 不存在 → extractor 打印 warning，跳过图像提取，继续 pipeline（不阻塞）
- 单个 figure 裁剪失败 → 记录到 `figure_extraction.log`，其它 figure 继续
- H11 gate 会在下游捕获缺图问题

**依赖：** `pdftoppm`（poppler-utils，多数系统已预装）+ `Pillow`（已在 deepaper 依赖中）

### 3. Writer prompt 变更：A 级深度 + 图片嵌入 + 紧凑混淆点

**改动位置：** `src/deepaper/prompt_builder.py` 的 `gates_to_constraints()` 和 `generate_writer_prompt()`

#### 3a. 深度内嵌（A 级洞察）

**适用范围：** 深度要求**只施加于** `第一性原理分析` 和 `技术精要` 两个章节，即 `writer-principle` 和 `writer-technical` 的 prompt。`核心速览`（30 秒 TL;DR）和 `机制迁移`（抽象原语表）本质是快速索引，强加深度会破坏各自的职责。

在这两个 writer 的 prompt 里追加：

```
## 深度要求（v2.1 新增，硬性约束，仅适用于本章节）

在保持 v2 压缩格式的前提下，本章节必须包含至少以下 3 种深度信号中的 2 种：

**D1. 反事实推理** — 对至少 1 个核心设计决策，说明"如果不这么做会怎样"
  示例：`如果保留 KL 项 → 策略会被拉回 Delta Learning 的 DPO reference，
       锁住探索空间；Dr.GRPO 在 7B 无此问题，但 32B + Delta 必须去掉`

**D2. 怀疑性批判** — 对至少 1 个数字/结论，指出它的 fine print 或度量偏差
  示例：`2949 tok/s 是 20 推理节点 : 8 训练节点的不对称分配，
       换算 per-GPU 实际提升约 1.8×，论文抽象数字里未披露`

**D3. 实现层细节** — 对至少 1 个核心机制，写出论文正文外的具体实现参数
  示例：`inflight 更新频率 N=64 rollout batch，通过 RDMA 广播权重（~2s），
       IS 截断 ρ=5；实现在 open-instruct/grpo_fast.py _broadcast_weights`

**禁止写伪代码**（v2 已有约束，这里重申）
**禁止写教科书式背景知识**（例如解释什么是 DPO / GRPO 的基本概念）
```

这些深度要求的意图：让 writer **花 10 分钟真正啃论文** 而不是表面概括 — 要产出 D1/D2/D3 级别的内容，必须阅读 appendix、对照 table footnote、交叉 cross-reference section。

#### 3b. 图片嵌入强制约束

**责任分配：** H11 gate 检查的是 `merged.md`（最终合并输出），不是单个 writer 的 part 文件。所有 core figure 的嵌入责任**集中到 `writer-technical`**（它是当前唯一 `needs_pdf_pages=True` 的 writer，本来就要读 PDF 页面，最适合承担图片嵌入职责）。其它 writer 可以嵌入和自己章节相关的 figure，但 **hard requirement 只对 writer-technical 生效**。

**writer-technical 的 prompt 追加：**

```
## 图片嵌入约束（v2.1 新增，H11 gate 验证，仅对本 writer 生效）

你负责把 **所有 core_figures.json 里标记为 core 的 figure** 都嵌入到你的章节。
每个 core figure 至少嵌入 1 次，使用以下语法：

`![Figure N — {简短 caption}](./assets/figure-N.png)`

- 路径固定为 `./assets/figure-N.png`（相对于 final.md 的位置）
- `{简短 caption}` 是你自己写的一句话总结（≤15 个汉字），不是论文原 caption
- 裸文本引用 `Figure N 展示了...` **不算** 嵌入；必须用上面的图片语法
- 即使某张图在你看来意义不大，只要它在 core_figures.json 里就必须嵌入
- 嵌入位置建议：在对应因果链、设计决策或消融排序的附近
```

**其它 writer 的 prompt 追加（宽松版）：**

```
## 图片嵌入建议（可选）

如果你需要引用 core_figures.json 里的某张图作为证据（例如在混淆点里），
可以用图片语法 `![Figure N — ...](./assets/figure-N.png)` 嵌入。
注意路径前缀固定为 `./assets/`。
```

**图片文件名约定：** `figure-<id>.png`，其中 `<id>` 是 `core_figures.json` 里的 id 字段（保持和原 paper 编号一致，含 "13a" 这种子编号）。

#### 3c. 紧凑混淆点格式（方案 Y）

旧格式（v2）：
```
- ❌ 错误理解：OlmoRL与GRPO相同，只是套用了DAPO的zero-gradient过滤
- ✅ 正确理解：OlmoRL在DAPO基础上额外去除KL项和std归一化，
     并引入inflight权重更新...
```

新格式（v2.1 方案 Y）：
```
**混淆点 1：OlmoRL ≠ GRPO + DAPO 的工程优化版**

- ❌ 在 DAPO 基础上只加了 zero-gradient 过滤
- ✅ 多做两件事：(a) 去掉 std 归一化消除难题偏置，(b) inflight 权重更新
     使训练/推理节点异步并行。前者决定"学什么"，后者决定"学多快"
- 🚨 如果搞错：把 inflight 当加速 trick → 忽略 IS 修正 → 策略漂移
  ![Figure 5 — inflight weight update flow](./assets/figure-5.png)
```

**结构约束：**
- 粗体小标题 = 一句话 label，帮助读者快速 scan
- `❌` = 常见错误（或 prior knowledge 容易混淆的版本）
- `✅` = 正确理解（必须解释差异的**动因**，不只是陈述事实）
- `🚨` = 如果搞错会有什么后果（落地影响）
- 可选嵌入 figure 作证据（从 `core_figures.json` 里选）
- 每条混淆点 ≤100 个汉字（不含嵌图；粗体小标题单独算，不计入 100 字上限）

### 4. Gates 变更

#### 4a. H2 删除 → H12 新增（section-bucket 覆盖）

**删除：** `check_structural_coverage()` 在 `gates.py` 的字符串匹配实现。`run_hard_gates()` 里 `results["H2"]` 改为 `_SKIPPED`（保留 key 避免破坏现有测试快照），然后新增 H12。

**新增 H12：** `check_section_bucket_coverage()` in `src/deepaper/gates.py`

**逻辑：**
```python
def check_section_bucket_coverage(merged: str, paper_profile: dict) -> dict:
    """
    从 paper_profile 提取顶层 section 名（通常 5-12 个）。
    对每个 section，检查 merged.md 是否有**任一**引用形式：
      - "Section X.Y" 或 "§X.Y"（X 是该 section 的 index）
      - "p.NN"（NN 落在该 section 的 page range 内）
      - Figure/Table 引用到属于该 section 的对象
    至少 80% 的 top-level section 必须有引用。
    """
```

**输入数据源：** `paper_profile.json`（由 `src/deepaper/registry.py::compute_paper_profile()` 产出）需新增字段 `top_level_sections: [{index, title, page_start, page_end}]`。如果该字段缺失，H12 skip pass。

**Figure/Table → section 映射：** H12 的"Figure/Table 引用到属于该 section 的对象"判定依赖于 `visual_registry.json` 里每个 figure/table 的 `definition_page` 字段和 `top_level_sections` 的 page range 做 range lookup。如果 registry 没有 page 信息，该判定降级为"仅检查 Section X.Y / p.NN 引用"。

**失败模式捕获：**
- Writer 跳过 Evaluation section → Evaluation bucket 空 → fail
- Writer 跳过 Appendix → Appendix bucket 空 → fail
- Writer 只引用前 30 页 → 后半 section 的 bucket 全空 → fail

**80% 阈值选择依据：**
- 对 10 bucket 的论文，允许 2 个 bucket 无引用（例如 Related Work 和 Limitations 这种）
- 对 5 bucket 的短论文，允许 1 个 bucket 无引用
- 比"所有 bucket 必须覆盖"宽松，给 writer 一点合理取舍空间

#### 4b. H11 新增（core figure 图片嵌入率）

**新增 H11：** `check_core_figures_embedded()` in `src/deepaper/gates.py`

**逻辑：**
```python
def check_core_figures_embedded(merged: str, core_figures: list[dict]) -> dict:
    """
    对每个 core figure，检查 merged.md 是否包含图片语法嵌入：
      ![.*](./assets/figure-<id>.png)
    必须 100% 覆盖。缺一即 fail。
    """
```

**和 H7 的区别：** H7 是"引用了 Figure N 字符串"（宽松），H11 是"用了图片语法嵌入"（严格）。v2.1 两者都运行，H7 是最低底线，H11 是新门槛。

#### 4c. Gates 结果布局变更

```
H1  baselines ≥ 2              (不变)
H2  SKIPPED                    (删除逻辑，保留 key)
H3  section existence          (不变)
H4  SKIPPED                    (不变)
H5  tldr numbers               (不变)
H6  heading levels             (不变)
H7  core figure string ref     (不变，宽松版)
H8  number fingerprint         (不变)
H9  content markers            (不变)
H10 figure ref density         (不变)
H11 core figure embed          (新增，严格版)
H12 section bucket coverage    (新增，取代 H2)
```

### 5. Save 命令变更

**改动位置：** `src/deepaper/cli.py` 的 `save` 命令

**旧流程（v2）：**
1. Classify 结果决定目标目录 `papers/llm/pretraining/`
2. 读取 `merged.md`
3. 写到 `papers/llm/pretraining/<slug>.md`

**新流程（v2.1）：**
1. Classify 结果决定目标目录 `papers/llm/pretraining/`
2. 创建子目录 `papers/llm/pretraining/<slug>/`
3. 创建 `papers/llm/pretraining/<slug>/assets/`
4. 读取 `merged.md`，重写图片引用路径（从 `.deepaper/runs/<run>/figures/` 改为 `./assets/`），写到 `papers/llm/pretraining/<slug>/<slug>.md`
5. 复制 `.deepaper/runs/<run_id>/figures/*.png` 到 `papers/llm/pretraining/<slug>/assets/`
6. 保持 writer.py 的 v2 frontmatter 预留字段逻辑不变（commit 89daaa0 的 fix）

**冲突处理：**
- 目标目录已存在 → prompt 用户 overwrite / backup / abort（现有 CLI 交互模式延续）

### 6. Baseline freeze（C5）

**位置：** `tests/golden/olmo-3.md`

**内容：** 当前（2026-04-08）OLMo 3 v2 pipeline 产出的 `papers/llm/pretraining/olmo-3.md` **原封不动**存一份到测试目录。

**用途：**
- **不是 gate** — 不阻塞 pipeline 运行
- **是 regression 防线** — 新增测试 `tests/test_golden_regression.py::test_olmo3_coverage_not_worse`，对比 v2.1 重新产出的 olmo-3.md 和 golden：
  - 关键数字表的每个数字是否都在（允许顺序变化）
  - 因果链条数不减少（≥3 条）
  - 混淆点条数不减少（≥3 条）
  - 设计决策表行数不减少（≥5 行）
  - page references 数量不减少
- 新增指标（深度、图片嵌入）只要增加不要减少

**不测试：** 具体文字措辞（允许 rewrite）。只测结构化指标。

**更新机制：** 当 pipeline 改动导致 golden 需要更新时，人工运行 `python -m tests.update_golden olmo-3`（新增脚本，复制当前 output 到 golden）并在 PR 里写理由。

### 7. arxiv_id 保留

**现状：** YAML frontmatter 已有 `arxiv_id: '2512.13961'` 字段，由 writer 在 `核心速览` 章节写入（v2 output_schema 已定义）。

**v2.1 需要做的：**
- **不做改动** — frontmatter 已保留，Dataview `FROM "papers" WHERE arxiv_id = "2512.13961"` 已经可用
- 新增一个测试断言 `tests/test_frontmatter.py::test_arxiv_id_preserved`，确保所有 v2.1 输出都含 `arxiv_id`

**未来（v3）：**
- `papers/INDEX.md` 由 agent 维护，每次 save 时 append 一行
- `deepaper lookup <arxiv_id>` CLI 命令直接查 INDEX

## 实现 surface（文件清单）

| 文件 | 改动类型 | 预估行数 |
|------|---------|---------|
| `src/deepaper/extractor.py` | +`extract_core_figure_images()` 函数 | +50 |
| `src/deepaper/prompt_builder.py` | 追加 A 级深度 + 图片嵌入 + 紧凑混淆点约束 | +40 / -10 |
| `src/deepaper/gates.py` | +H11 +H12，H2 标记 skipped | +80 / -5 |
| `src/deepaper/output_schema.py` | 新增 H12 配置（min_coverage, bucket_field_name） | +10 |
| `src/deepaper/cli.py`（save 命令） | P2 目录创建 + figure 复制 + 路径重写 | +30 / -15 |
| `src/deepaper/registry.py`（`compute_paper_profile()`） | 新增 `top_level_sections` 字段到 paper_profile.json 返回值 | +20 |
| `src/deepaper/defaults.py` + `src/deepaper/templates.py` | 更新 DEFAULT_TEMPLATE 的混淆点示例为方案 Y | +15 / -5 |
| `src/deepaper/content_checklist.py` | CONTENT_MARKERS 添加 "深度信号" 检查（D1/D2/D3 中至少 2 个） | +10 |
| `tests/test_h11_figure_embed.py` | 新文件 — H11 单元测试 | +60 |
| `tests/test_h12_section_bucket.py` | 新文件 — H12 单元测试 | +80 |
| `tests/test_golden_regression.py` | 新文件 — baseline freeze 对比测试 | +50 |
| `tests/test_frontmatter.py` | 新增 `test_arxiv_id_preserved` | +15 |
| `tests/golden/olmo-3.md` | 新文件 — 冻结当前 OLMo 3 v2 输出 | ~400 行 |
| `tests/update_golden.py` | 新文件 — 手动更新 golden 的脚本 | +30 |

**总计：** ~11 个文件改动 + 5 个新测试文件 + 1 个新 golden 文件
**代码净增：** ~400 行 production + ~200 行 test

## 测试策略

### 单元测试
- **H11 gate**：构造 merged.md 带 / 不带 / 部分嵌入 figure，断言 passed 和 missing
- **H12 gate**：构造 paper_profile 含 5 / 10 bucket，构造 merged.md 覆盖 / 跳过不同 bucket，验证 80% 阈值
- **Extractor figure cropping**：用 fixture PDF（现有 `.deepaper/runs/2512.13961/`），断言输出 PNG 存在且 < 500KB
- **Save command P2 layout**：断言 save 后 `papers/.../slug/slug.md` 和 `papers/.../slug/assets/figure-*.png` 都存在
- **Frontmatter arxiv_id 保留**：parse 输出 frontmatter 断言 arxiv_id 字段存在

### 集成测试
- **End-to-end mini pipeline**：用 2-3 页的 fixture PDF（不是 OLMo 3 的 117 页），跑全 pipeline，断言所有 gates 通过且生成 P2 结构
- **Golden regression**：对比重新跑 OLMo 3 pipeline 的输出和 `tests/golden/olmo-3.md` 的结构化指标（数字覆盖、因果链数、page refs 数）

### 不自动化的验证
- 实际 OLMo 3 pipeline 的人工阅读评估（10 分钟读完感觉如何、深度是否到位）
- Obsidian 打开 `papers/llm/pretraining/olmo-3/olmo-3.md` 图片是否内联渲染
- 混淆点新格式是否真的比旧格式更易懂（主观判断）

## Rollout

1. **Merge v2.1 到 feat/pipeline-perf-optimization 分支**（当前工作分支）
2. **冻结 baseline**：在 v2.1 代码改动开始**之前**，先把当前 `papers/llm/pretraining/olmo-3.md` 复制到 `tests/golden/olmo-3.md` 并 commit
3. **实现 v2.1 改动**：按实现 surface 清单分 task 完成
4. **重新跑 OLMo 3**：用 v2.1 pipeline 产出新的 `papers/llm/pretraining/olmo-3/olmo-3.md`
5. **人工对比**：golden vs v2.1 新输出，确认所有结构化指标不退化且新增深度信号
6. **合并到 main**：v2.1 验证通过 + golden regression test 通过 → PR / merge
7. **可选**：重新跑其它之前删除的 v1 论文（deepseek-v3, minicpm, etc.），用 v2.1 pipeline 生成新版本

## 为 v3（LLM Wiki）留的接口

v2.1 的设计已经为 v3 演进铺好三块地：

1. **P2 目录结构** — 未来的 `concepts/grpo.md` 要 transclude OLMo 3 的 Figure 5 时，路径 `../papers/llm/pretraining/olmo-3/assets/figure-5.png` 稳定
2. **frontmatter arxiv_id + tags + mechanisms** — v3 的 `papers/INDEX.md` 和 `deepaper reindex` 命令可以直接扫 frontmatter 构建索引
3. **深度信号 D1/D2/D3** — 深度段落在未来 wiki 化时可以直接拆出来成为 concept 页面（反事实段落 → `concepts/<mechanism>-counterfactual.md`）

v3 不在本 spec 范围内，但 v2.1 不会对任何 v3 方向造成阻塞。

## Open questions

1. **`top_level_sections` 的提取策略**：H12 需要 paper_profile 提供顶层 section 结构。当前 extractor 可能没有明确区分"顶层 section"和"subsection"。实现时需要先确认 extractor 产出的 section 树结构；如果粒度不对，需要在 extractor 里加过滤逻辑。这个是 H12 实现时最大的不确定性。

2. **bbox 可信度判断**：像素裁剪 fallback 到整页的条件需要实测确定 —— 什么样的 bbox 算"不可信"（越界？面积过小？aspect ratio 异常？）。初版先保守：只要 bbox 存在且在页面范围内就用 bbox，否则整页。

3. **深度信号自动检测**：content_checklist.py 里要检测"D1/D2/D3 至少 2 种"其实很难用正则做 —— 反事实推理 / 怀疑性批判都是语义判断。初版可能只能做 keyword 启发式（"如果不"、"反事实"、"fine print"、"换算"、"实际"），容错率低。这个如果做不好可以退化成"只在 prompt 里要求，不做 gate 检查"。

4. **JPEG vs PNG 阈值**：500KB 是拍脑袋的数字。实际跑 OLMo 3 之后需要调整。
