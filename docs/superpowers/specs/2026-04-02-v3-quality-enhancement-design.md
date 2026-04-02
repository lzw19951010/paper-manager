# V3 Pipeline Quality Enhancement — 吸收 slash_v3 独有优势

**Date:** 2026-04-02
**Status:** Approved
**Scope:** 将 `olmo3_slash_v3.md` 的四项独有优势固化到管线中，使所有论文分析受益

## Background

对比 `papers/llm/pretraining/olmo-3.md`（主摘要）与 `tests/fixtures/olmo3_slash_v3.md`（v3 管线输出）发现，v3 在以下方面表现更优：

1. **数据管线/训练流程的文本流程图** — 完整的 Stage 0-3 文本流程图
2. **"用简单例子走一遍差异"** — 具体数字的简化示例（如"假设有 1000 篇文档"）
3. **物理/直觉比喻** — "鸡尾酒调配"等比喻精准映射技术机制
4. **Figure 引用密度** — 17 次 vs 5 次，更系统地引用论文图表

这些优势目前是偶发的（取决于 LLM 生成质量），需要通过模板 + Gate + 合同注入固化。

## Design Decisions

- **分层强制策略**：可程序化检测的（流程图、Figure 引用）用 Gate 强制；难以程序化判定的（简单例子、直觉比喻）仅用模板引导 + 合同注入
- **融入现有章节**：不新增独立子章节，将简化示例融入"方法详解 → 直觉版"，比喻融入"动机与第一性原理 → 物理/直觉解释"
- **方案 B（模板 + Gate + Prompt Builder 联动）**：比纯模板引导更可靠，比 Extractor 增强更轻量

## Changes

### 1. DEFAULT_TEMPLATE (`src/deepaper/defaults.py`)

**1a. 方法详解 → 直觉版（强化简单例子）**

现有文字（line ~97）：
```
用最简单的例子（如3层网络、3个item），不写公式，纯文字走一遍
"旧方法做一步 → 新方法做一步 → 差异在哪"。
```

改为：
```
用最简单的例子（如3层网络、3个item、1000篇文档），不写公式，纯文字走一遍
"旧方法做一步 → 新方法做一步 → 差异在哪"。要求：例子必须包含具体数字
（如"假设有1000篇文档，旧方法保留200篇，新方法先按质量分4档再分别以1x/1.2x/3.5x/7x采样，
最终保留350篇"），让读者能用手指头跟着算一遍。
```

**1b. 动机与第一性原理 → 物理/直觉解释（增加 few-shot 示例）**

现有文字（line ~83）：
```
- **物理/直觉解释:** 不要堆砌术语，用大白话解释为什么这个机制必须生效？
```

改为：
```
- **物理/直觉解释:** 不要堆砌术语，用大白话或生活化比喻解释为什么这个机制必须生效。
  好的比喻示例：「品质80%取决于原料配比（数据工程），而非最后的装饰（post-training）——
  就像鸡尾酒调配」「如果旧方法是拿着固定菜单点菜，新方法就是根据你的口味现场调配」。
  比喻应当精准映射到技术机制，避免泛泛的修辞。
```

**1c. 格式规范 — 章节分隔线**

在 DEFAULT_TEMPLATE 的"正文（Markdown）"说明中，现有文字（line ~67）：
```
正文由以下章节组成，每个章节用 `## 标题` 开头，章节之间用 `---` 分隔。
```

这条指令已存在但当前管线输出未严格遵循。在模板末尾"注意事项"中新增一条强调：
```
- 每个一级章节（核心速览、动机与第一性原理、方法详解、实验与归因、专家批判、机制迁移分析、背景知识补充）之间必须用 `---` 水平线分隔，营造清晰的视觉节拍
```

**1d. 格式规范 — bullet 模式**

在模板的各章节指令中，将列出要点的格式统一为 `- **粗体标题:** 内容` 模式。具体改动：

现有"核心速览"格式（line ~73-75）：
```
- **TL;DR (≤100字):** 一句话讲清...
- **一图流 (Mental Model):** 用文字描述...
- **核心机制一句话 (Mechanism in One Line):** 剥离领域上下文...
```

这部分已是正确格式，无需改动。但在以下章节中需要明确要求使用相同模式：

在"专家批判"末尾新增格式指引：
```
每个要点使用 `- **粗体标题:** 内容` 的 bullet 格式，避免大段落叙述。
```

在"实验与归因"末尾新增格式指引：
```
每个分析要点使用 `- **粗体标题:** 内容` 的 bullet 格式组织，便于速览。
```

**1e. 格式规范 — 表格增量标注**

在"实验与归因"章节的"归因分析"指令中新增：
```
- **归因分析 (Ablation Study):** 论文的哪个组件贡献了最大的收益？将ablation结果按贡献大小排序。
  对比表格中，在数值后标注相对上一阶段的增量变化，格式：`95.9(+0.3)`，让读者一眼看出每步贡献。
```

### 2. H9 ContentMarkers (`src/deepaper/content_checklist.py`)

在 `方法详解` markers 中新增流程图检测：

```python
{"marker": "流程图", "check": "contains_pattern", "pattern": r"(?:→.*){2,}"},
```

检测逻辑：匹配至少 3 个 `→` 出现的链式箭头（`A → B → C → D`）。H9 整体通过阈值保持 70% 不变，新增后总共 12 个 marker，允许最多 3 个缺失。

### 3. 新增 H10 Figure 引用密度 Gate (`src/deepaper/gates.py`)

```python
def check_figure_ref_density(md: str, core_figures: list[dict] | None) -> dict:
    """H10: Each core figure must be referenced >= 2 times in the body."""
    if not core_figures:
        return {"passed": True, "skipped": True, "reason": "no core_figures"}

    body = _extract_body(md)
    failures = []
    for fig in core_figures:
        fig_id = fig.get("id", "")
        count = len(re.findall(re.escape(fig_id), body, re.IGNORECASE))
        if count < 2:
            failures.append({"figure": fig_id, "count": count, "required": 2})

    return {
        "passed": len(failures) == 0,
        "failures": failures,
        "total_figures": len(core_figures),
    }
```

- 遍历 `core_figures.json` 中每个图（最多 3 个）
- 要求每个 core figure 在正文中出现 ≥2 次
- 无 `core_figures` 时自动 skip（与 H7 一致）
- 在 `run_hard_gates()` 中接入，与 H7 共享 `core_figures` 参数

**与 H7 的区别**：H7 检查"是否引用了"（≥1），H10 检查"引用密度"（≥2）。

### 4. Prompt Builder 合同注入 (`src/deepaper/prompt_builder.py`)

在 `gates_to_constraints()` 中根据 writer 类型注入不同约束：

**Visual Writer 合同增强：**
```
- 「方法详解 → 精确版」必须包含 ≥1 个完整数据流图，格式：Input (shape) → Step A → Step B → ... → Output，≥3 个箭头步骤（H9）
- 必须引用灵魂图 {fig_ids}，且每个 Figure 在正文中至少出现 2 次（H10）
```

`{fig_ids}` 从 `core_figures.json` 动态生成。

**Text Writer 合同增强：**
```
- 「动机与第一性原理 → 物理/直觉解释」须包含一个生活化比喻，精准映射到技术机制
- 「方法详解 → 直觉版」须包含一个带具体数字的简化示例（≤200字），让读者能手动跟算一遍
```

这两条不对应 gate，仅作合同引导。

## Files Changed

| File | Change | Enforcement |
|------|--------|-------------|
| `src/deepaper/defaults.py` | 模板措辞强化（简单例子 + 直觉比喻 + 分隔线 + bullet 模式 + 增量标注） | 模板引导 |
| `src/deepaper/content_checklist.py` | 新增流程图 marker | H9 Gate 强制 |
| `src/deepaper/gates.py` | 新增 `check_figure_ref_density` + 接入 `run_hard_gates` | H10 Gate 强制 |
| `src/deepaper/prompt_builder.py` | `gates_to_constraints()` 增加 writer 类型条件约束 | 合同引导 |

## Testing

- 现有 `tests/test_gates.py` 新增 H10 测试 case（有/无 core_figures、density 不足、skip 场景）
- 现有 `tests/test_prompt_builder.py` 验证 visual/text writer 合同包含新约束文案
- `content_checklist.py` 的流程图 marker 用 `olmo3_slash_v3.md` fixture 验证通过
- 回归：对 `olmo3_slash_v3.md` 和 `olmo3_cli_baseline.md` 跑全量 gates 确保无意外 break

## Out of Scope

- Extractor 模板增强（方案 C 的内容，本次不做）
- 补齐 v3 缺失的溯源引用（Section/Table refs）— 属于方向 A
- CHAR_FLOORS 调整 — 当前阈值足够
- 标题层级提升（h4→h2）— 需改 H6 gate，风险较大，本次不动
- 降低括号注释密度 — 与溯源精度冲突，暂不处理
- 增加 `→` 因果链密度 — 已通过流程图 gate 间接覆盖
