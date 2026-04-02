# V3 Quality Enhancement Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Absorb 4 content advantages and 3 formatting improvements from `olmo3_slash_v3.md` into the pipeline via template changes, new gates, and prompt builder enhancements.

**Architecture:** Modify DEFAULT_TEMPLATE for prompt guidance (simple examples, metaphors, separators, bullet format, incremental annotations). Add flowchart marker to H9 ContentMarkers. Add new H10 gate for Figure reference density. Enhance `gates_to_constraints()` to inject writer-type-specific contract clauses.

**Tech Stack:** Python, pytest, regex

---

### Task 1: Add flowchart marker to H9 ContentMarkers

**Files:**
- Modify: `src/deepaper/content_checklist.py:15-19`
- Test: `tests/test_gates.py` (new class at end of file)

- [ ] **Step 1: Write the failing test**

Add to `tests/test_gates.py`:

```python
class TestH9FlowchartMarker:
    """H9 should detect flowchart (chain of ≥3 arrows) in 方法详解."""

    def test_flowchart_present(self):
        from deepaper.content_checklist import check_content_markers

        md = (
            "#### 核心速览\n"
            "TL;DR: 达到96.2%准确率\n一图流 mental model\n"
            "[动作]+[对象]+[方式]+[效果]\n"
            "#### 动机与第一性原理\nBecause A → Therefore B\n"
            "#### 方法详解\n"
            "##### 数值推演\nsome derivation\n"
            "```python\nprint('hello')\n```\n"
            "❌ wrong ✅ right\n"
            "Input (B,T) → Encoder → Attention → FFN → Output (B,T,V)\n"
            "#### 实验与归因\n归因分析\n"
            "#### 专家批判\n隐性成本 100天 200GPU 3倍开销\n"
            "#### 机制迁移分析\n"
            "| 原语名称 | 本文用途 | 抽象描述 | 信息论直觉 |\n"
            "| --- | --- | --- | --- |\n| A | B | C | D |\n"
            "前身 Ancestors: X, Y, Z\n"
        )
        result = check_content_markers(md)
        assert result["details"]["方法详解:流程图"] is True

    def test_flowchart_missing(self):
        from deepaper.content_checklist import check_content_markers

        md = (
            "#### 方法详解\n"
            "##### 数值推演\nsome derivation\n"
            "```python\nprint('hello')\n```\n"
            "❌ wrong ✅ right\n"
            "No flowchart here, just text.\n"
        )
        result = check_content_markers(md)
        assert result["details"]["方法详解:流程图"] is False

    def test_single_arrow_not_enough(self):
        from deepaper.content_checklist import check_content_markers

        md = (
            "#### 方法详解\n"
            "##### 数值推演\nsome derivation\n"
            "```python\nprint('hello')\n```\n"
            "❌ wrong ✅ right\n"
            "A → B only one arrow\n"
        )
        result = check_content_markers(md)
        assert result["details"]["方法详解:流程图"] is False
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd /Users/bytedance/github/deepaper && python -m pytest tests/test_gates.py::TestH9FlowchartMarker -v`
Expected: FAIL — `KeyError: '方法详解:流程图'`

- [ ] **Step 3: Add flowchart marker to content_checklist.py**

In `src/deepaper/content_checklist.py`, add to the `方法详解` list (after line 18):

```python
    "方法详解": [
        {"marker": "数值推演", "check": "section_exists", "pattern": r"数值推演"},
        {"marker": "伪代码", "check": "contains_pattern", "pattern": r"```(?:python|pseudo|py)"},
        {"marker": "易混淆点", "check": "contains_pattern", "pattern": r"❌.*✅|✅.*❌"},
        {"marker": "流程图", "check": "contains_pattern", "pattern": r"(?:→.*){2,}"},
    ],
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd /Users/bytedance/github/deepaper && python -m pytest tests/test_gates.py::TestH9FlowchartMarker -v`
Expected: 3 passed

- [ ] **Step 5: Run full gate tests for regression**

Run: `cd /Users/bytedance/github/deepaper && python -m pytest tests/test_gates.py -v`
Expected: All existing tests pass (slash_v3 H9 fixture test already skips due to ## heading mismatch)

- [ ] **Step 6: Commit**

```bash
cd /Users/bytedance/github/deepaper
git add src/deepaper/content_checklist.py tests/test_gates.py
git commit -m "feat: add flowchart marker to H9 ContentMarkers

Detects chain of ≥3 arrows (A → B → C → D) in 方法详解 section.
Pattern: r'(?:→.*){2,}' requires at least 3 → in a single block.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>"
```

---

### Task 2: Add H10 Figure reference density gate

**Files:**
- Modify: `src/deepaper/gates.py:270-291` (after H7), `src/deepaper/gates.py:433-495` (run_hard_gates)
- Test: `tests/test_gates.py` (new class)

- [ ] **Step 1: Write the failing tests**

Add to `tests/test_gates.py`:

```python
class TestH10FigureRefDensity:
    """H10: Each core figure referenced >= 2 times in body."""

    def test_sufficient_density(self):
        from deepaper.gates import check_figure_ref_density

        md = (
            "---\ntitle: Test\n---\n"
            "#### 方法详解\n"
            "As shown in Figure 1, the method works. We extend Figure 1's approach.\n"
            "Figure 3 shows results. We revisit Figure 3 in the appendix.\n"
        )
        core_figures = [
            {"id": "1", "key": "Figure_1"},
            {"id": "3", "key": "Figure_3"},
        ]
        result = check_figure_ref_density(md, core_figures)
        assert result["passed"] is True
        assert result["failures"] == []

    def test_insufficient_density(self):
        from deepaper.gates import check_figure_ref_density

        md = (
            "---\ntitle: Test\n---\n"
            "#### 方法详解\n"
            "As shown in Figure 1, the method works.\n"
            "Figure 3 shows results. We also see Figure 3 again.\n"
        )
        core_figures = [
            {"id": "1", "key": "Figure_1"},
            {"id": "3", "key": "Figure_3"},
        ]
        result = check_figure_ref_density(md, core_figures)
        assert result["passed"] is False
        assert len(result["failures"]) == 1
        assert result["failures"][0]["figure"] == "Figure 1"
        assert result["failures"][0]["count"] == 1

    def test_no_core_figures_skipped(self):
        from deepaper.gates import check_figure_ref_density

        md = "---\ntitle: Test\n---\n#### Content\nSome text.\n"
        result = check_figure_ref_density(md, None)
        assert result["passed"] is True
        assert result.get("skipped") is True

    def test_empty_core_figures_skipped(self):
        from deepaper.gates import check_figure_ref_density

        md = "---\ntitle: Test\n---\n#### Content\nSome text.\n"
        result = check_figure_ref_density(md, [])
        assert result["passed"] is True
        assert result.get("skipped") is True

    def test_h10_in_run_hard_gates(self):
        from deepaper.gates import run_hard_gates

        md = (
            "---\nbaselines:\n  - A\n  - B\ntldr: test 96.2% on 3 benchmarks\n---\n"
            "#### 核心速览\n" + ("核" * 600) + "\n"
            "#### 方法详解\nFigure 1 here and Figure 1 again.\n" + ("方" * 2100) + "\n"
            "#### 实验与归因\n" + ("实" * 1600) + "\n"
            "#### 动机与第一性原理\n" + ("动" * 900) + "\n"
            "#### 专家批判\n" + ("专" * 900) + "\n"
            "#### 机制迁移分析\n" + ("机" * 900) + "\n"
            "#### 背景知识补充\n" + ("背" * 400) + "\n"
        )
        core_figures = [{"id": "1", "key": "Figure_1"}]
        result = run_hard_gates(md, {}, core_figures, {1: "page text"}, None)
        assert "H10" in result["results"]
        assert result["results"]["H10"]["passed"] is True
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd /Users/bytedance/github/deepaper && python -m pytest tests/test_gates.py::TestH10FigureRefDensity -v`
Expected: FAIL — `ImportError: cannot import name 'check_figure_ref_density'`

- [ ] **Step 3: Implement check_figure_ref_density in gates.py**

Add after the H7 section (after line 291) in `src/deepaper/gates.py`:

```python
# ===========================================================================
# H10: Figure Reference Density
# ===========================================================================

def check_figure_ref_density(md: str, core_figures: list[dict] | None) -> dict:
    """Check each core figure is referenced >= 2 times in the body.

    Returns ``{passed, failures, total_figures}``.
    Skipped when *core_figures* is None or empty.
    """
    if not core_figures:
        return {"passed": True, "skipped": True, "reason": "no core_figures"}

    body = _extract_body(md)
    failures: list[dict] = []

    for fig in core_figures:
        fig_id = fig.get("id", "")
        label = f"Figure {fig_id}"
        count = len(re.findall(re.escape(label), body, re.IGNORECASE))
        if count < 2:
            failures.append({"figure": label, "count": count, "required": 2})

    return {
        "passed": len(failures) == 0,
        "failures": failures,
        "total_figures": len(core_figures),
    }
```

- [ ] **Step 4: Wire H10 into run_hard_gates**

In `src/deepaper/gates.py`, update `run_hard_gates`:

1. Update docstring from "Run all 8 gates" to "Run all hard gates (H1-H10)".
2. Add H10 after H9 (after line 488):

```python
    # H10: Figure Reference Density — requires core_figures
    if core_figures:
        results["H10"] = check_figure_ref_density(merged_md, core_figures)
    else:
        results["H10"] = dict(_SKIPPED)
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `cd /Users/bytedance/github/deepaper && python -m pytest tests/test_gates.py::TestH10FigureRefDensity -v`
Expected: 5 passed

- [ ] **Step 6: Run full gate tests for regression**

Run: `cd /Users/bytedance/github/deepaper && python -m pytest tests/test_gates.py -v`
Expected: All tests pass

- [ ] **Step 7: Commit**

```bash
cd /Users/bytedance/github/deepaper
git add src/deepaper/gates.py tests/test_gates.py
git commit -m "feat: add H10 Figure reference density gate

Each core figure must appear ≥2 times in the body (vs H7's ≥1).
Skipped when no core_figures available, consistent with H7.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>"
```

---

### Task 3: Enhance DEFAULT_TEMPLATE with content and formatting guidance

**Files:**
- Modify: `src/deepaper/defaults.py:28-173`
- Test: `tests/test_prompt_builder.py` (new assertions)

- [ ] **Step 1: Write failing tests for new template content**

Add to `tests/test_prompt_builder.py`:

```python
class TestTemplateEnhancements:
    """Verify DEFAULT_TEMPLATE contains new content and formatting guidance."""

    def test_simple_example_guidance(self):
        from deepaper.defaults import DEFAULT_TEMPLATE
        assert "1000篇文档" in DEFAULT_TEMPLATE
        assert "手指头跟着算" in DEFAULT_TEMPLATE

    def test_metaphor_guidance(self):
        from deepaper.defaults import DEFAULT_TEMPLATE
        assert "鸡尾酒调配" in DEFAULT_TEMPLATE
        assert "精准映射到技术机制" in DEFAULT_TEMPLATE

    def test_section_separator_guidance(self):
        from deepaper.defaults import DEFAULT_TEMPLATE
        assert "水平线分隔" in DEFAULT_TEMPLATE or "---" in DEFAULT_TEMPLATE

    def test_bullet_format_guidance(self):
        from deepaper.defaults import DEFAULT_TEMPLATE
        assert "**粗体标题:**" in DEFAULT_TEMPLATE

    def test_incremental_annotation_guidance(self):
        from deepaper.defaults import DEFAULT_TEMPLATE
        assert "(+0.3)" in DEFAULT_TEMPLATE or "增量变化" in DEFAULT_TEMPLATE
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd /Users/bytedance/github/deepaper && python -m pytest tests/test_prompt_builder.py::TestTemplateEnhancements -v`
Expected: FAIL on most assertions (current template lacks these strings)

- [ ] **Step 3: Update DEFAULT_TEMPLATE in defaults.py**

**3a.** Replace line 97 (simple example in 方法详解 直觉版):

Old:
```
用最简单的例子（如3层网络、3个item），不写公式，纯文字走一遍"旧方法做一步 → 新方法做一步 → 差异在哪"。
```

New:
```
用最简单的例子（如3层网络、3个item、1000篇文档），不写公式，纯文字走一遍"旧方法做一步 → 新方法做一步 → 差异在哪"。要求：例子必须包含具体数字（如"假设有1000篇文档，旧方法保留200篇，新方法先按质量分4档再分别以1x/1.2x/3.5x/7x采样，最终保留350篇"），让读者能用手指头跟着算一遍。
```

**3b.** Replace line 83 (metaphor in 动机与第一性原理):

Old:
```
- **物理/直觉解释:** 不要堆砌术语，用大白话解释为什么这个机制必须生效？
```

New:
```
- **物理/直觉解释:** 不要堆砌术语，用大白话或生活化比喻解释为什么这个机制必须生效。好的比喻示例：「品质80%取决于原料配比（数据工程），而非最后的装饰（post-training）——就像鸡尾酒调配」「如果旧方法是拿着固定菜单点菜，新方法就是根据你的口味现场调配」。比喻应当精准映射到技术机制，避免泛泛的修辞。
```

**3c.** In the 注意事项 section (line 167), add three new bullet points:

```
- 每个一级章节之间必须用 `---` 水平线分隔，营造清晰的视觉节拍
- 列举要点时使用 `- **粗体标题:** 内容` 的 bullet 格式，避免大段落叙述
- 归因/ablation 对比表格中，在数值后标注增量变化，格式：`95.9(+0.3)`，让读者一眼看出每步贡献
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd /Users/bytedance/github/deepaper && python -m pytest tests/test_prompt_builder.py::TestTemplateEnhancements -v`
Expected: 5 passed

- [ ] **Step 5: Run full prompt_builder tests for regression**

Run: `cd /Users/bytedance/github/deepaper && python -m pytest tests/test_prompt_builder.py -v`
Expected: All existing tests pass (template still contains all original markers)

- [ ] **Step 6: Commit**

```bash
cd /Users/bytedance/github/deepaper
git add src/deepaper/defaults.py tests/test_prompt_builder.py
git commit -m "feat: enhance DEFAULT_TEMPLATE with content and formatting guidance

- Simple example with concrete numbers in 方法详解 直觉版
- Metaphor few-shot examples in 动机与第一性原理
- Section separator (---), bullet format, incremental annotation rules

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>"
```

---

### Task 4: Enhance prompt builder with writer-type-specific constraints

**Files:**
- Modify: `src/deepaper/prompt_builder.py:108-177`
- Test: `tests/test_prompt_builder.py` (new assertions)

- [ ] **Step 1: Write failing tests for writer-type constraints**

Add to `tests/test_prompt_builder.py`:

```python
class TestWriterTypeConstraints:
    """gates_to_constraints should inject different clauses for visual vs text writers."""

    def test_visual_writer_gets_flowchart_constraint(self):
        from deepaper.prompt_builder import gates_to_constraints
        constraints = gates_to_constraints(
            sections=["方法详解", "实验与归因"],
            profile={"total_pages": 10, "num_tables": 5, "num_equations": 3},
            registry={"Table_1": {"type": "Table"}, "Table_2": {"type": "Table"}},
            core_figures=[{"id": 1, "key": "Figure_1"}],
        )
        assert "数据流图" in constraints or "流程图" in constraints
        assert "≥3" in constraints or "3 个" in constraints

    def test_visual_writer_gets_figure_density_constraint(self):
        from deepaper.prompt_builder import gates_to_constraints
        constraints = gates_to_constraints(
            sections=["方法详解", "实验与归因"],
            profile={"total_pages": 10},
            registry={},
            core_figures=[{"id": 1, "key": "Figure_1"}, {"id": 3, "key": "Figure_3"}],
        )
        assert "至少出现 2 次" in constraints or "至少出现2次" in constraints

    def test_text_writer_gets_metaphor_constraint(self):
        from deepaper.prompt_builder import gates_to_constraints
        constraints = gates_to_constraints(
            sections=["核心速览", "动机与第一性原理"],
            profile={"total_pages": 10},
            registry={},
            core_figures=[],
        )
        assert "比喻" in constraints

    def test_text_writer_gets_simple_example_constraint(self):
        from deepaper.prompt_builder import gates_to_constraints
        constraints = gates_to_constraints(
            sections=["核心速览", "动机与第一性原理", "方法详解"],
            profile={"total_pages": 10},
            registry={},
            core_figures=[],
        )
        assert "简化示例" in constraints or "简单例子" in constraints

    def test_incremental_annotation_for_experiments(self):
        from deepaper.prompt_builder import gates_to_constraints
        constraints = gates_to_constraints(
            sections=["方法详解", "实验与归因"],
            profile={"total_pages": 10, "num_tables": 3},
            registry={"Table_1": {"type": "Table"}},
            core_figures=[],
        )
        assert "(+0.3)" in constraints or "增量" in constraints
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd /Users/bytedance/github/deepaper && python -m pytest tests/test_prompt_builder.py::TestWriterTypeConstraints -v`
Expected: FAIL — assertions not found in current constraints output

- [ ] **Step 3: Enhance gates_to_constraints in prompt_builder.py**

In `src/deepaper/prompt_builder.py`, add after the H9 content markers block (after line 177, before the "Suggested targets" block):

```python
    # --- Writer-type-specific guidance (non-gate, contract only) ---
    lines.append("\n**写作指引（非 gate，但强烈建议遵循）：**")

    # Visual writer: flowchart + figure density
    if "方法详解" in sections:
        lines.append(
            "- 「方法详解 → 精确版」必须包含 ≥1 个完整数据流图，"
            "格式：Input → Step A → Step B → ... → Output，≥3 个箭头步骤（H9）"
        )
    if core_figures and ("方法详解" in sections or "实验与归因" in sections):
        fig_ids = [f"Figure {cf['id']}" for cf in core_figures]
        lines.append(
            f"- 每个灵魂图（{', '.join(fig_ids)}）在正文中至少出现 2 次，"
            "分布在不同段落（H10）"
        )

    # Text writer: metaphor + simple example
    if "动机与第一性原理" in sections:
        lines.append(
            "- 「动机 → 物理/直觉解释」须包含一个生活化比喻，精准映射到技术机制"
        )
    if "方法详解" in sections:
        lines.append(
            "- 「方法详解 → 直觉版」须包含一个带具体数字的简化示例（≤200字），"
            "让读者能手动跟算一遍"
        )

    # Formatting: incremental annotations in experiment tables
    if "实验与归因" in sections:
        lines.append(
            "- 归因/ablation 表格数值后标注增量变化，格式：`95.9(+0.3)`"
        )
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd /Users/bytedance/github/deepaper && python -m pytest tests/test_prompt_builder.py::TestWriterTypeConstraints -v`
Expected: 5 passed

- [ ] **Step 5: Run full test suite for regression**

Run: `cd /Users/bytedance/github/deepaper && python -m pytest tests/test_prompt_builder.py tests/test_gates.py -v`
Expected: All tests pass

- [ ] **Step 6: Commit**

```bash
cd /Users/bytedance/github/deepaper
git add src/deepaper/prompt_builder.py tests/test_prompt_builder.py
git commit -m "feat: inject writer-type-specific constraints in prompt builder

Visual writers get flowchart + figure density contracts.
Text writers get metaphor + simple example guidance.
Experiment sections get incremental annotation format.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>"
```

---

### Task 5: Full regression test

**Files:**
- No new files — verification only

- [ ] **Step 1: Run entire test suite**

Run: `cd /Users/bytedance/github/deepaper && python -m pytest tests/ -v`
Expected: All tests pass

- [ ] **Step 2: Verify H9 marker count is now 12**

Run in Python:
```bash
cd /Users/bytedance/github/deepaper && python -c "
from deepaper.content_checklist import CONTENT_MARKERS
total = sum(len(v) for v in CONTENT_MARKERS.values())
print(f'Total H9 markers: {total}')
assert total == 12, f'Expected 12 markers, got {total}'
print('OK')
"
```
Expected: `Total H9 markers: 12` + `OK`

- [ ] **Step 3: Verify H10 is in run_hard_gates output**

Run in Python:
```bash
cd /Users/bytedance/github/deepaper && python -c "
from deepaper.gates import run_hard_gates
md = '---\nbaselines:\n  - A\n  - B\ntldr: test 96.2% on 3x\n---\n#### Content\ntext\n'
result = run_hard_gates(md, {}, [], None, None)
assert 'H10' in result['results'], 'H10 missing from results'
print(f'Gates: {list(result[\"results\"].keys())}')
print('OK')
"
```
Expected: `Gates: ['H1', 'H2', ..., 'H9', 'H10']` + `OK`

- [ ] **Step 4: Verify template contains all new guidance strings**

Run in Python:
```bash
cd /Users/bytedance/github/deepaper && python -c "
from deepaper.defaults import DEFAULT_TEMPLATE
checks = ['1000篇文档', '鸡尾酒调配', '水平线分隔', '**粗体标题:**', '增量变化']
for c in checks:
    assert c in DEFAULT_TEMPLATE, f'Missing: {c}'
    print(f'  OK: {c}')
print('All template checks passed')
"
```
Expected: All 5 checks OK
