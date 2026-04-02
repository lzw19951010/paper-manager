# Deepaper Pipeline Redesign: 模板驱动 + Gates 合同 + 自动分片

## 1. 问题诊断

### 1.1 直接故障

`~/.claude/commands/deepaper.md` 有旧版一行模板，覆盖了项目级 550 行 pipeline。原因：`_auto_install_slash_command()` 只检查文件是否存在，不检查版本。

### 1.2 系统性问题

即使 pipeline 被正确加载，仍有以下设计缺陷：

1. **模板双源**: DEFAULT_TEMPLATE (defaults.py) 定义了完整分析结构，但 Writer prompts 在 slash command 里独立重写了一遍，两者脱钩
2. **Gates 单向**: gates.py 定义了 H1-H8 验证逻辑，但 Writer 不知道这些约束，无法主动满足
3. **分类断线**: `templates/categories.md` 定义了 4 大类 13 子类 + 3 条分类原则，但 pipeline 中从未被调用
4. **无端到端验证**: `tests/fixtures/olmo3_slash_v3.md` 是参考输出，但没有测试验证 pipeline 能生成它

## 2. 设计原则

1. **DEFAULT_TEMPLATE 是唯一真相源** — Writer prompts 从它动态切片生成，不允许重写
2. **Gates = 合同** — 同一套约束用三次：前馈引导 Writer → 事后验证 → 精确修复指令
3. **分片按工作量自动决定** — 只硬编码 visual vs text 分离（因为 visual 需要 PDF 表格页），text 章节按预期工作量自动装箱
4. **灵魂图广播** — figure_contexts 注入每个 Writer 的 prompt
5. **slash command 只做调度** — 所有 prompt 生成、模板切片、gate 约束翻译、合并、分类在 Python CLI 中
6. **核心功能不可砍** — 7 个分析章节、frontmatter schema、分类规则、标签生成、quality gates 全部保留

## 3. 架构

### 3.1 CLI 命令清单

```
deepaper download URL                     # 已有，不改
deepaper extract ARXID                    # 新: pymupdf 提取 + registry + profile + core_figures + figure_contexts
deepaper prompt ARXID --role extractor    # 新: 生成 Extractor prompt (从当前 slash command 的 Extractor 模板迁入)
deepaper prompt ARXID --split             # 新: 自动分片生成 N 个 Writer prompts + merge 配置
deepaper check ARXID                      # 新: StructCheck + Auditor (封装 extractor.py 逻辑)
deepaper merge ARXID                      # 新: 合并 Writer 输出 + 格式规范化
deepaper gates ARXID                      # 已有，不改
deepaper fix ARXID                        # 新: 读 gates 失败结果，生成 Fixer prompt
deepaper classify ARXID                   # 新: 读 categories.md + classify.md，输出分类 prompt 供 Conductor 使用
deepaper save ARXID --category CAT        # 已有，不改
deepaper install                          # 已有，改: 加版本检测，强制覆盖旧版
```

### 3.2 Pipeline 流程

```
Conductor (slash command, ~60行)
  │
  ├─ [1] deepaper download URL → ARXID, PDF_PATH
  ├─ [2] deepaper extract ARXID → text_by_page + registry + profile + core_figures + figure_contexts
  │
  ├─ [3] deepaper prompt ARXID --role extractor → prompt file
  │      spawn Extractor agent → notes.md
  │      deepaper check ARXID → if fail, retry once
  │
  ├─ [4] deepaper prompt ARXID --split → writers.json
  │      for each writer in writers.json: spawn agent (parallel)
  │      灵魂图 figure_contexts 广播给所有 Writer
  │
  ├─ [5] deepaper merge ARXID → merged.md
  ├─ [6] deepaper gates ARXID → gates.json
  │      if fail: deepaper fix ARXID → fixer prompt
  │      spawn Fixer agent → re-run deepaper gates (max 2 rounds)
  │
  ├─ [7] deepaper classify ARXID → classify prompt → Conductor 判断 category
  └─ [8] deepaper save ARXID --category CAT --input merged.md
```

### 3.3 数据流

每个 agent 的输入 prompt 和输出产物都保留在 run 目录下，便于事后审核和调试。

```
.deepaper/runs/{ARXID}/
  │
  │  # ── Step 1: extract 产出 ──
  ├── text_by_page.json          # PyMuPDF 逐页文本
  ├── text.txt                   # 全文（供 Extractor 读）
  ├── visual_registry.json       # Table/Figure 注册表
  ├── paper_profile.json         # 页数/表数/图数/公式数
  ├── core_figures.json          # 灵魂图列表
  ├── figure_contexts.json       # 灵魂图 caption + 引用段落
  │
  │  # ── Step 2: Extractor ──
  ├── prompt_extractor.md        # Extractor 收到的 prompt
  ├── notes.md                   # Extractor 产出的结构化笔记
  ├── check.json                 # StructCheck + Auditor 结果
  ├── prompt_extractor_retry.md  # (可选) 补充提取的 prompt
  │
  │  # ── Step 3: Writers ──
  ├── writers.json               # 分片配置（哪个 writer 写哪些章节 + merge 顺序）
  ├── prompt_writer_visual.md    # Writer-Visual 收到的 prompt
  ├── prompt_writer_text_0.md    # Writer-Text-0 收到的 prompt
  ├── prompt_writer_text_1.md    # Writer-Text-1 收到的 prompt（可能没有，取决于论文大小）
  ├── part_visual.md             # Writer-Visual 产出
  ├── part_text_0.md             # Writer-Text-0 产出
  ├── part_text_1.md             # Writer-Text-1 产出（可能没有）
  │
  │  # ── Step 4: Merge + Gates ──
  ├── merged.md                  # merge 后的完整分析
  ├── gates.json                 # HardGates + ContentMarkers 结果
  ├── prompt_fix.md              # (可选) Fixer 收到的 prompt
  ├── merged_fixed.md            # (可选) Fixer 修复后的版本（保留原 merged.md 不覆盖）
  ├── gates_round2.json          # (可选) 第2轮 gates 结果
  │
  │  # ── Step 5: Critic ──
  ├── prompt_critic.md           # Critic 收到的 prompt
  ├── critic.json                # Critic 语义审核结果（逐章节打分）
  ├── prompt_fix_soft.md         # (可选) Critic 触发的 Fixer prompt
  │
  │  # ── Step 6: Classify + Save ──
  ├── prompt_classify.md         # 分类 prompt
  ├── classify.json              # 分类结果 {"category": "llm/pretraining"}
  └── final.md                   # 最终版本（= merged.md 或 merged_fixed.md 的 copy）
```

**审核原则：**
- 每个 agent 的 prompt 和产出成对保留（prompt_xxx.md → xxx.md / xxx.json）
- Fixer 不覆盖 merged.md，而是写 merged_fixed.md，保留修复前后对比
- gates.json / critic.json 记录了每个 gate 的通过/失败详情
- writers.json 记录了分片决策（哪些章节分给了哪个 writer）
- 任何时候可以回溯：这个章节是哪个 writer 写的？它收到了什么 prompt？gates 怎么评的？

## 4. 核心模块设计

### 4.1 `deepaper extract ARXID`

合并当前 slash command 里散落的步骤为一条命令：

```python
def extract(arxiv_id: str):
    """提取文本 + 构建 registry + profile + core_figures + figure_contexts"""
    run_dir = ensure_run_dir(root, arxiv_id)
    pdf_path = root / "tmp" / f"{arxiv_id}.pdf"

    # 1. PyMuPDF 提取文本
    text_by_page = extract_text_by_page(pdf_path)
    save(run_dir / "text_by_page.json", text_by_page)
    save(run_dir / "text.txt", format_full_text(text_by_page))

    # 2. Visual registry
    registry = build_visual_registry(text_by_page)
    save(run_dir / "visual_registry.json", registry)

    # 3. Paper profile
    profile = compute_paper_profile(text_by_page, registry)
    save(run_dir / "paper_profile.json", profile)

    # 4. Core figures + contexts
    core_figs = identify_core_figures(registry, text_by_page, profile["total_pages"])
    save(run_dir / "core_figures.json", core_figs)
    fig_contexts = extract_figure_contexts(text_by_page, core_figs)
    save(run_dir / "figure_contexts.json", fig_contexts)

    # 5. Table definition pages (for Writer-Visual)
    table_def_pages = sorted(set(
        v["definition_page"] for v in registry.values()
        if v.get("type") == "Table" and v.get("definition_page")
    ))

    # 输出 JSON 摘要供 slash command 使用
    print(json.dumps({
        "run_dir": str(run_dir),
        "total_pages": profile["total_pages"],
        "num_tables": profile["num_tables"],
        "num_figures": profile["num_figures"],
        "num_equations": profile["num_equations"],
        "core_figures": [cf["key"] for cf in core_figs],
        "table_def_pages": table_def_pages,
    }))
```

### 4.2 `deepaper prompt ARXID --split`

核心：从 DEFAULT_TEMPLATE 动态切片 + 注入 gate 合同 + 广播灵魂图。

#### 4.2.1 模板切片

从 DEFAULT_TEMPLATE 中按 `## 章节名` 分段提取：

```python
TEMPLATE_SECTIONS = [
    "核心速览 (Executive Summary)",
    "动机与第一性原理 (Motivation & First Principles)",
    "方法详解 (Methodology)",
    "实验与归因 (Experiments & Attribution)",
    "专家批判 (Critical Review)",
    "机制迁移分析 (Mechanism Transfer Analysis)",
    "背景知识补充 (Background Context)",
]

def parse_template_sections(template: str) -> dict[str, str]:
    """将 DEFAULT_TEMPLATE 按 ## 章节名 分割为 {short_name: section_text}"""
    # 返回 {"核心速览": "- **TL;DR:** ...\n- **一图流:** ...", ...}
```

#### 4.2.2 自动分片算法

```python
def auto_split(paper_profile: dict, char_floors: dict) -> list[WriterTask]:
    """
    1. Visual 组固定: 方法详解 + 实验与归因 (需要 PDF 表格页 + figure contexts)
    2. Text 章节按预期工作量贪心装箱
    3. 短论文可能只有 2 个 Writer，长论文 3 个
    """
    VISUAL_SECTIONS = ["方法详解", "实验与归因"]
    TEXT_SECTIONS = ["核心速览", "动机与第一性原理", "专家批判", "机制迁移分析", "背景知识补充"]

    # 估算每个 text 章节的预期工作量
    workloads = {}
    for sec in TEXT_SECTIONS:
        base = char_floors.get(sec, 500)
        # 动态调整: 论文越长/表格越多，某些章节需要更多内容
        factor = compute_scaling_factor(sec, paper_profile)
        workloads[sec] = base * factor

    # Visual 组工作量估算
    visual_workload = sum(char_floors.get(s, 2000) * compute_scaling_factor(s, paper_profile)
                         for s in VISUAL_SECTIONS)

    # 贪心装箱: 目标是每个 text writer 的工作量 ≈ visual_workload / 2
    # (因为 visual writer 通常最重)
    total_text = sum(workloads.values())
    n_text_writers = max(1, round(total_text / (visual_workload * 0.6)))
    n_text_writers = min(n_text_writers, 3)  # 上限 3 个 text writer

    bins = greedy_bin_pack(TEXT_SECTIONS, workloads, n_bins=n_text_writers)

    # 构建 writer tasks
    tasks = []
    # Visual writer
    tasks.append(WriterTask(
        name="writer-visual",
        sections=VISUAL_SECTIONS,
        needs_pdf_pages=True,
    ))
    # Text writers
    for i, bin_sections in enumerate(bins):
        tasks.append(WriterTask(
            name=f"writer-text-{i}",
            sections=bin_sections,
            needs_pdf_pages=False,
        ))

    return tasks


def compute_scaling_factor(section: str, profile: dict) -> float:
    """根据论文特征动态调整章节预期工作量"""
    pages = profile.get("total_pages", 10)
    tables = profile.get("num_tables", 0)
    figures = profile.get("num_figures", 0)
    equations = profile.get("num_equations", 0)

    if section == "方法详解":
        # 公式多 → 精确版更长; 图多 → 直觉版更长
        return max(2.0, 1.0 + equations * 0.15 + figures * 0.1)
    elif section == "实验与归因":
        # 表多 → 对比表格更多
        return max(1.5, 1.0 + tables * 0.1)
    elif section == "专家批判":
        # 论文长 → 隐性成本更多
        return max(1.0, 0.8 + pages * 0.01)
    elif section == "机制迁移分析":
        # 相对固定
        return max(1.5, 1.0 + equations * 0.05)
    elif section == "背景知识补充":
        return 1.0
    elif section in ("核心速览", "动机与第一性原理"):
        return 1.0
    return 1.0
```

#### 4.2.3 Gate 合同注入

```python
def gates_to_constraints(sections: list[str], profile: dict, registry: dict,
                         core_figures: list, char_floors: dict) -> str:
    """将 gate 要求翻译为 Writer prompt 中的可执行约束"""
    lines = ["## ⚠️ 质量合同（写完后会被 programmatic 验证，不达标需返工）\n"]

    for sec in sections:
        floor = char_floors.get(sec, 500)
        adjusted = int(floor * compute_scaling_factor(sec, profile))
        lines.append(f"- 「{sec}」 ≥ {adjusted:,} 字符")

    # H4: 表格数
    if "实验与归因" in sections:
        n_tables = sum(1 for v in registry.values() if v.get("type") == "Table")
        lines.append(f"- 实验与归因：输出 ≥ {min(n_tables, 6)} 张完整 markdown 对比表格")
        lines.append("- 表格数字必须从 notes MAIN_RESULTS 段逐项复制，禁止编造（H8 数字溯源检查）")

    # H5: TL;DR
    if "核心速览" in sections:
        lines.append("- TL;DR 必须包含 ≥2 个具体量化数字，如 'MATH 96.2%'（H5 检查）")

    # H6: 标题层级
    lines.append("- 主标题 ####（h4），子标题 #####（h5），禁止 h1/h2/h3（H6 检查）")

    # H7: 核心图引用
    if core_figures:
        fig_ids = [f"Figure {cf['id']}" for cf in core_figures]
        lines.append(f"- 必须在正文中引用灵魂图: {', '.join(fig_ids)}（H7 检查）")

    # H1: Baselines
    if "核心速览" in sections or "实验与归因" in sections:
        lines.append("- YAML frontmatter baselines ≥ 2 个模型（H1 检查）")

    lines.append("")
    lines.append("写完后对照上述合同逐项自检，不达标立即补充。")
    return "\n".join(lines)
```

#### 4.2.4 单个 Writer prompt 生成

```python
def generate_writer_prompt(task: WriterTask, run_dir: Path, template_sections: dict,
                           figure_contexts: dict, constraints: str,
                           pdf_path: str, table_def_pages: list) -> str:
    """为一个 Writer 生成完整 prompt"""

    parts = []

    # 1. 角色定义
    parts.append(f"你是论文分析专家，负责撰写以下章节。用中文写作。\n")

    # 2. 质量合同（最前面，确保 Writer 先看到约束）
    parts.append(constraints)

    # 3. 灵魂图上下文（所有 Writer 共享）
    parts.append("\n## 灵魂图上下文（所有 Writer 共享）\n")
    parts.append(f"```json\n{json.dumps(figure_contexts, ensure_ascii=False, indent=2)}\n```\n")
    parts.append("在描述方法和实验时引用这些核心图，用 Figure N 格式。\n")

    # 4. 章节指令（从 DEFAULT_TEMPLATE 原文切出）
    parts.append("\n## 你的章节\n")
    for sec_name in task.sections:
        sec_text = template_sections.get(sec_name, "")
        parts.append(f"### {sec_name}\n\n{sec_text}\n")

    # 5. 格式规则
    parts.append("\n## 格式规则\n")
    parts.append("- 主标题: #### (h4)，如 `#### 核心速览 (Executive Summary)`\n")
    parts.append("- 子标题: ##### (h5)\n")
    parts.append("- 禁止 h1/h2/h3，禁止添加 '深度分析' 等总标题\n")
    parts.append("- 禁止在章节间添加 `---` 分隔线\n")
    if task.sections[0] == "核心速览":
        parts.append("- 文件开头必须是 `---`（YAML frontmatter 开始）\n")
    else:
        parts.append(f"- 文件开头直接是 `#### {task.sections[0]}`\n")

    # 6. 输入
    parts.append("\n## 输入\n")
    parts.append(f"- 结构化笔记: {run_dir}/notes.md（先读这个）\n")
    parts.append(f"- 全文检索: {run_dir}/text.txt\n")
    if task.needs_pdf_pages:
        parts.append(f"- PDF 表格验证页: {pdf_path}（仅读这些页: {table_def_pages}）\n")

    # 7. 输出
    output_file = f"{run_dir}/part_{task.name.replace('writer-', '')}.md"
    parts.append(f"\n## 输出\n")
    parts.append(f"写入文件: `{output_file}`\n")
    parts.append("写完后执行 `wc -c` 检查是否满足质量合同中的字符门控。\n")

    return "\n".join(parts)
```

#### 4.2.5 `--split` 输出

```json
{
  "writers": [
    {
      "name": "writer-visual",
      "sections": ["方法详解", "实验与归因"],
      "prompt_file": ".deepaper/runs/2512.13961/prompt_writer_visual.md",
      "output_file": ".deepaper/runs/2512.13961/part_visual.md"
    },
    {
      "name": "writer-text-0",
      "sections": ["核心速览", "动机与第一性原理", "专家批判"],
      "prompt_file": ".deepaper/runs/2512.13961/prompt_writer_text_0.md",
      "output_file": ".deepaper/runs/2512.13961/part_text_0.md"
    },
    {
      "name": "writer-text-1",
      "sections": ["机制迁移分析", "背景知识补充"],
      "prompt_file": ".deepaper/runs/2512.13961/prompt_writer_text_1.md",
      "output_file": ".deepaper/runs/2512.13961/part_text_1.md"
    }
  ],
  "merge_order": ["writer-text-0", "writer-visual", "writer-text-1"],
  "section_order": ["核心速览", "动机与第一性原理", "方法详解", "实验与归因", "专家批判", "机制迁移分析", "背景知识补充"],
  "figure_contexts": { "Figure_1": {...}, "Figure_2": {...} }
}
```

### 4.3 `deepaper check ARXID`

封装 `extractor.py` 的 `struct_check` + `audit_coverage`：

```python
def check(arxiv_id: str):
    """运行 StructCheck + Auditor，输出 JSON 结果"""
    run_dir = ensure_run_dir(root, arxid)
    notes = (run_dir / "notes.md").read_text()
    text_by_page = load(run_dir / "text_by_page.json")
    profile = load(run_dir / "paper_profile.json")

    sc = struct_check(notes, profile["total_pages"], profile)
    ac = audit_coverage(text_by_page, notes, profile["total_pages"])

    result = {
        "passed": sc["passed"] and ac["coverage_ratio"] >= 0.7,
        "struct_check": sc,
        "audit": {
            "coverage_ratio": ac["coverage_ratio"],
            "uncovered_segments": ac["uncovered_segments"],
        }
    }
    print(json.dumps(result, indent=2))
```

### 4.4 `deepaper merge ARXID`

读 `writers.json` 的 `merge_order`，按顺序拼接 + 格式规范化：

```python
def merge(arxiv_id: str):
    """合并 Writer 输出，规范化格式"""
    run_dir = ensure_run_dir(root, arxiv_id)
    config = load(run_dir / "writers.json")

    parts = []
    for writer_name in config["merge_order"]:
        writer = next(w for w in config["writers"] if w["name"] == writer_name)
        part_path = run_dir / Path(writer["output_file"]).name
        parts.append(part_path.read_text())

    merged = "\n\n".join(parts)

    # 格式规范化
    merged = normalize_headings(merged)   # 确保 h4/h5/h6
    merged = remove_stray_rules(merged)   # 移除 YAML 外的 ---
    merged = remove_title_lines(merged)   # 移除 "Part A" 等多余标题

    (run_dir / "merged.md").write_text(merged)
    print(json.dumps({"merged": str(run_dir / "merged.md"), "chars": len(merged)}))
```

### 4.5 `deepaper fix ARXID`

读 gates 输出的失败结果 + notes.md，生成精确的 Fixer prompt：

```python
def fix(arxiv_id: str):
    """读 gates.json 失败结果，生成 Fixer agent prompt"""
    run_dir = ensure_run_dir(root, arxiv_id)
    gates_result = load(run_dir / "gates.json")
    figure_contexts = load(run_dir / "figure_contexts.json")

    if gates_result["passed"]:
        print(json.dumps({"needs_fix": False}))
        return

    instructions = ["## 需要修复的问题（来自 programmatic 质量检查）\n"]
    for gate_name in gates_result["failed"]:
        gate = gates_result["results"][gate_name]
        instructions.append(format_fix_instruction(gate_name, gate, figure_contexts))

    instructions.append("\n## 输入")
    instructions.append(f"- 当前分析: {run_dir}/merged.md")
    instructions.append(f"- 结构化笔记（补充来源）: {run_dir}/notes.md")
    instructions.append(f"\n## 输出")
    instructions.append(f"直接修改 {run_dir}/merged.md，不要创建新文件。")

    prompt = "\n".join(instructions)
    prompt_path = run_dir / "prompt_fix.md"
    prompt_path.write_text(prompt)
    print(json.dumps({"needs_fix": True, "prompt_file": str(prompt_path), "failed": gates_result["failed"]}))


def format_fix_instruction(gate_name: str, gate: dict, figure_contexts: dict) -> str:
    """将单个 gate 失败翻译为精确修复指令"""
    if gate_name == "H3":
        lines = [f"### {gate_name}: 字符门控未达标"]
        for f in gate.get("failures", []):
            lines.append(f"- 「{f['section']}」当前 {f['actual']:,} 字符 < {f['floor']:,} 门控")
            lines.append(f"  → 从 notes.md 的相关段落补充内容")
        return "\n".join(lines)
    elif gate_name == "H7":
        missing = gate.get("missing", [])
        lines = [f"### {gate_name}: 核心图未引用"]
        for fig_key in missing:
            ctx = figure_contexts.get(fig_key, {})
            lines.append(f"- {fig_key} 未被引用。Caption: {ctx.get('caption', 'N/A')}")
            lines.append(f"  → 在方法详解或实验归因中引用此图")
        return "\n".join(lines)
    # ... 类似处理 H1, H4, H5, H6, H8
    else:
        return f"### {gate_name}: {json.dumps(gate, ensure_ascii=False)}"
```

### 4.6 `deepaper classify ARXID`

读 `templates/categories.md` + `classify.md`，基于 notes 的摘要生成分类 prompt 供 Conductor 使用：

```python
def classify(arxiv_id: str):
    """输出分类 prompt 文件，由 Conductor 转交 LLM 判断分类"""
    run_dir = ensure_run_dir(root, arxiv_id)
    notes = (run_dir / "notes.md").read_text()

    # 提取 META 段作为摘要
    summary = extract_meta_summary(notes)

    # 读分类规则（完整的 4 大类 13 子类 + 3 条分类原则）
    categories = load_template("categories", templates_dir)
    classify_tmpl = load_template("classify", templates_dir)

    # 渲染 prompt
    prompt = classify_tmpl.format(summary=summary, categories=categories)

    # 输出 prompt 文件
    prompt_path = run_dir / "prompt_classify.md"
    prompt_path.write_text(prompt)
    print(json.dumps({"prompt_file": str(prompt_path)}))
```

Conductor 读取 prompt_classify.md 的内容，直接作为自己的 context 判断分类（不需要单独 spawn agent，分类是轻量任务）。

### 4.6 `deepaper install` 修复

```python
SLASH_CMD_VERSION = 2  # 递增此值强制覆盖旧版

def _auto_install_slash_command() -> None:
    cmd_path = Path.home() / ".claude" / "commands" / "deepaper.md"
    content = get_default_slash_command()

    if cmd_path.exists():
        existing = cmd_path.read_text(encoding="utf-8")
        # 检查版本标记
        if f"deepaper-version: {SLASH_CMD_VERSION}" in existing:
            return  # 已是最新版
    # 写入新版（含版本标记）
    cmd_path.parent.mkdir(parents=True, exist_ok=True)
    cmd_path.write_text(content, encoding="utf-8")
```

Slash command 文件头部加版本标记：

```markdown
<!-- deepaper-version: 2 -->
Analyze an arxiv paper using the deepaper pipeline.
...
```

### 4.7 Gates 的三次使用

```
同一套 gate 定义 (gates.py::CHAR_FLOORS, H1-H8)
    │
    ├─[1] gates_to_constraints() → Writer prompt "质量合同"     前馈引导
    │
    ├─[2] deepaper gates ARXID  → pass/fail JSON                事后验证
    │
    └─[3] gates_to_fix_instructions() → Fixer prompt            精确修复
         "H3 失败: 方法详解 8,200 < 12,000。从 notes HYPERPARAMETERS 段补充。"
```

### 4.8 CHAR_FLOORS 更新

当前 `gates.py` 的 CHAR_FLOORS 设计为**短论文（8-15 页、3-5 张表）的合理下限**。长论文靠 `compute_scaling_factor` 动态上调。

```python
CHAR_FLOORS: dict[str, int] = {
    "核心速览": 300,
    "动机与第一性原理": 400,
    "方法详解": 1500,
    "实验与归因": 800,
    "专家批判": 500,
    "机制迁移分析": 600,
    "背景知识补充": 200,
}
# 总计 ~4,300 字符 — 纯兜底，防止章节空白或只写一两句话
# 任何常规 ML 论文（8-15 页）都应轻松达到
```

**CHAR_FLOORS 只是兜底**，不是质量驱动力。真正驱动输出质量的是 DEFAULT_TEMPLATE 中的内容要求（公式推演、伪代码、设计决策、易混淆点等）。字符门控的作用是捕获"章节被完全遗漏或敷衍跳过"的故障，不是精确控制输出长度。

`compute_scaling_factor` 保留但定位为**Writer 参考建议**而非硬约束，在质量合同中表述为"建议字符数"而非"必须达到"：

```python
def compute_scaling_factor(section: str, profile: dict) -> float:
    """为 Writer 提供参考建议的字符数 scaling，不作为 gate 硬约束"""
    pages = profile.get("total_pages", 10)
    tables = profile.get("num_tables", 0)
    equations = profile.get("num_equations", 0)

    page_scale = min(3.0, max(1.0, pages / 15))

    if section == "方法详解":
        return page_scale * max(1.0, 1.0 + equations * 0.1)
    elif section == "实验与归因":
        return page_scale * max(1.0, 1.0 + tables * 0.08)
    else:
        return page_scale
```

Writer prompt 的质量合同区分两级：
- **硬约束**（gate 验证）：`「方法详解」≥ 1,500 字符`（来自 CHAR_FLOORS）
- **建议目标**：`「方法详解」建议 ~{floor × scaling} 字符`（参考值，不做 gate 验证）

## 5. Slash Command 精简版

~60 行，纯调度：

```markdown
<!-- deepaper-version: 2 -->
Analyze an arxiv paper and save to the deepaper knowledge base.

## Step 0: Setup
Run `which deepaper` to check. If not found: `pip install deepaper`.

## Step 1: Download & Extract
\```bash
deepaper download $ARGUMENTS
\```
Parse JSON output → ARXID, PDF_PATH.
\```bash
deepaper extract ARXID
\```
Parse JSON output → RUN_DIR, TOTAL_PAGES, etc.

## Step 2: Extractor Agent
Read the prompt file:
\```bash
deepaper prompt ARXID --role extractor
\```
Spawn one Agent (subagent_type: executor, name: extractor).
Give it the prompt file content. Wait for notes.md.
\```bash
deepaper check ARXID
\```
If failed → spawn extractor-retry agent with the failure details (max 1 retry).

## Step 3: Writers (parallel)
\```bash
deepaper prompt ARXID --split
\```
Parse JSON output → writers array. For EACH writer, spawn an Agent (subagent_type: executor) in parallel.
Each agent reads its prompt file and writes its output file.
All agents receive figure_contexts (灵魂图广播).

## Step 4: Merge + Gates
\```bash
deepaper merge ARXID
deepaper gates ARXID
\```
If gates failed → spawn Fixer agent with the gate failure JSON (max 2 rounds).

## Step 5: Classify + Save
\```bash
deepaper classify ARXID
\```
Read the classify prompt, determine category. Then:
\```bash
deepaper save ARXID --category CATEGORY --input .deepaper/runs/ARXID/merged.md
\```
Report saved path to user.
```

## 6. 测试计划

### 6.1 单元测试

| 测试 | 验证内容 |
|------|----------|
| `test_parse_template_sections` | DEFAULT_TEMPLATE 能被正确切为 7 个章节 |
| `test_auto_split_large_paper` | 120 页论文分为 3 个 Writer (1 visual + 2 text) |
| `test_auto_split_small_paper` | 8 页论文分为 2 个 Writer (1 visual + 1 text) |
| `test_gates_to_constraints` | gate 约束能被翻译为 prompt 文本，包含具体数字 |
| `test_merge_order` | 合并后章节顺序与 DEFAULT_TEMPLATE 一致 |
| `test_normalize_headings` | h2→h4, h3→h5 规范化 |
| `test_classify_prompt` | classify prompt 包含 categories.md 全部规则 |
| `test_install_version_check` | 新版本覆盖旧版本，同版本不覆盖 |

### 6.2 集成测试

| 测试 | 验证内容 |
|------|----------|
| `test_extract_olmo3` | extract 命令在 OLMo 3 PDF 上产出完整 registry/profile |
| `test_prompt_split_olmo3` | prompt --split 对 OLMo 3 产出 3 个 writer configs |
| `test_gates_on_slash_v3` | slash_v3 参考输出通过所有 8 个 gates |
| `test_gates_on_bad_output` | 当前不合格输出未通过 H3 (字符门控) 和 H6 (标题层级) |

### 6.3 端到端验证

完成实现后，在 OLMo 3 论文上跑一次完整 pipeline，对比 `tests/fixtures/olmo3_slash_v3.md`：
- 7 个章节是否全部存在
- 字符门控是否全部通过
- frontmatter 字段是否完整（baselines ≥ 10, datasets ≥ 10, metrics ≥ 10）
- 分类是否为 `llm/pretraining`

## 7. 实现顺序

1. **修复 install 版本检测** — 消除直接故障
2. **`deepaper extract`** — 合并散落步骤
3. **模板切片 + gate 合同注入 (`deepaper prompt --split`)** — 核心改动
4. **`deepaper check`** — 封装 StructCheck + Auditor
5. **`deepaper merge`** — 合并 + 规范化
6. **`deepaper classify`** — 分类接入
7. **更新 CHAR_FLOORS** — 对齐 slash_v3 质量标准
8. **精简 slash command** — 纯调度版
9. **单元测试 + 集成测试**
10. **端到端验证** — 跑一次完整 pipeline
