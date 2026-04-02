# Pipeline Redesign Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rebuild the deepaper pipeline so that DEFAULT_TEMPLATE is the single source of truth, gates serve as both guidance and validation, and the slash command is a thin dispatcher (~60 lines) with all logic in testable Python CLI commands.

**Architecture:** New CLI commands (`extract`, `prompt`, `check`, `merge`, `fix`, `classify`) encapsulate all pipeline logic. `deepaper prompt --split` parses DEFAULT_TEMPLATE into sections, auto-bins them across Writers by workload, injects gate constraints as "contracts" into each Writer prompt, and broadcasts figure contexts. The slash command only calls CLI commands and spawns agents.

**Tech Stack:** Python 3.10+, typer, pymupdf, pyyaml. Existing test infra: pytest.

**Spec:** `docs/superpowers/specs/2026-04-01-pipeline-redesign.md`
**Prompt templates:** `docs/superpowers/specs/prompts/*.md`

---

## File Map

```
src/deepaper/
  ├── cli.py                 # MODIFY: add extract, prompt, check, merge, fix, classify commands; fix _auto_install version detection
  ├── defaults.py            # MODIFY: add SLASH_CMD_VERSION, update get_default_slash_command
  ├── prompt_builder.py      # CREATE: template parsing, auto-split, gate contract injection, prompt generation
  ├── content_checklist.py   # CREATE: H9 ContentMarkers — extract checkable items from DEFAULT_TEMPLATE
  ├── gates.py               # MODIFY: update CHAR_FLOORS, add H9 gate, integrate content_checklist
  ├── extractor.py           # KEEP: struct_check + audit_coverage (already exists)
  ├── registry.py            # KEEP: build_visual_registry, core figures, paper profile (already exists)
  ├── pipeline_io.py         # KEEP: safe_read_json, safe_write_json, ensure_run_dir (already exists)
  ├── writer.py              # KEEP: write_paper_note, find_existing (already exists)
  ├── analyzer.py            # KEEP: parse_analysis_response (already exists)
  ├── templates.py           # KEEP: load_template (already exists)
  └── (others unchanged)

tests/
  ├── test_prompt_builder.py # CREATE: template parsing, auto-split, gate constraints, prompt gen
  ├── test_content_checklist.py # CREATE: H9 marker detection
  ├── test_gates.py          # MODIFY: add H9 tests
  ├── test_cli.py            # MODIFY: add tests for new commands
  └── (others unchanged)

.claude/commands/
  └── deepaper.md            # REWRITE: thin dispatcher (~60 lines)
```

---

### Task 1: Update CHAR_FLOORS and fix version detection in defaults.py

**Files:**
- Modify: `src/deepaper/gates.py:20-28`
- Modify: `src/deepaper/defaults.py`
- Modify: `src/deepaper/cli.py:23-36` (auto-install) and `cli.py:43-58` (install command)
- Test: `tests/test_gates.py`
- Test: `tests/test_cli.py`

- [ ] **Step 1: Write test for updated CHAR_FLOORS**

```python
# tests/test_gates.py — add to existing TestH3CharFloors class

def test_updated_char_floors_values(self):
    """CHAR_FLOORS are reasonable minimums for short ML papers."""
    from deepaper.gates import CHAR_FLOORS

    assert CHAR_FLOORS["核心速览"] == 300
    assert CHAR_FLOORS["动机与第一性原理"] == 400
    assert CHAR_FLOORS["方法详解"] == 1500
    assert CHAR_FLOORS["实验与归因"] == 800
    assert CHAR_FLOORS["专家批判"] == 500
    assert CHAR_FLOORS["机制迁移分析"] == 600
    assert CHAR_FLOORS["背景知识补充"] == 200
    # Total floor ~4,300 — any ML paper should meet this
    assert sum(CHAR_FLOORS.values()) < 5000
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_gates.py::TestH3CharFloors::test_updated_char_floors_values -v`
Expected: FAIL (current floors are different values)

- [ ] **Step 3: Update CHAR_FLOORS in gates.py**

```python
# src/deepaper/gates.py lines 20-28, replace entire CHAR_FLOORS dict

CHAR_FLOORS: dict[str, int] = {
    "核心速览": 300,
    "动机与第一性原理": 400,
    "方法详解": 1500,
    "实验与归因": 800,
    "专家批判": 500,
    "机制迁移分析": 600,
    "背景知识补充": 200,
}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_gates.py::TestH3CharFloors::test_updated_char_floors_values -v`
Expected: PASS

- [ ] **Step 5: Write test for version-aware auto-install**

```python
# tests/test_cli.py — add new class

class TestAutoInstallVersion:
    def test_old_version_gets_overwritten(self, tmp_path: Path) -> None:
        """Stale global slash command should be overwritten by new version."""
        cmd_path = tmp_path / ".claude" / "commands" / "deepaper.md"
        cmd_path.parent.mkdir(parents=True, exist_ok=True)
        cmd_path.write_text("<!-- deepaper-version: 1 -->\nold content\n")

        with patch.object(Path, "home", return_value=tmp_path):
            from deepaper.cli import _auto_install_slash_command
            _auto_install_slash_command()

        content = cmd_path.read_text()
        assert "<!-- deepaper-version: 1 -->" not in content
        # Should contain current version marker
        from deepaper.defaults import SLASH_CMD_VERSION
        assert f"<!-- deepaper-version: {SLASH_CMD_VERSION} -->" in content

    def test_current_version_not_overwritten(self, tmp_path: Path) -> None:
        """Current version should not be touched."""
        from deepaper.defaults import SLASH_CMD_VERSION
        cmd_path = tmp_path / ".claude" / "commands" / "deepaper.md"
        cmd_path.parent.mkdir(parents=True, exist_ok=True)
        original = f"<!-- deepaper-version: {SLASH_CMD_VERSION} -->\ncurrent content\n"
        cmd_path.write_text(original)

        with patch.object(Path, "home", return_value=tmp_path):
            from deepaper.cli import _auto_install_slash_command
            _auto_install_slash_command()

        assert cmd_path.read_text() == original
```

- [ ] **Step 6: Run test to verify it fails**

Run: `pytest tests/test_cli.py::TestAutoInstallVersion -v`
Expected: FAIL (SLASH_CMD_VERSION not defined, version check not implemented)

- [ ] **Step 7: Implement version-aware auto-install**

```python
# src/deepaper/defaults.py — add at module level after imports

SLASH_CMD_VERSION = 2
```

```python
# src/deepaper/cli.py — replace _auto_install_slash_command (lines 23-36)

def _auto_install_slash_command() -> None:
    """Auto-install slash command to ~/.claude/commands/ if not present or outdated."""
    cmd_path = Path.home() / ".claude" / "commands" / "deepaper.md"
    from deepaper.defaults import get_default_slash_command, SLASH_CMD_VERSION

    version_marker = f"<!-- deepaper-version: {SLASH_CMD_VERSION} -->"

    if cmd_path.exists():
        existing = cmd_path.read_text(encoding="utf-8")
        if version_marker in existing:
            return  # already current version

    cmd_path.parent.mkdir(parents=True, exist_ok=True)
    cmd_path.write_text(get_default_slash_command(), encoding="utf-8")
```

- [ ] **Step 8: Run all tests**

Run: `pytest tests/test_gates.py tests/test_cli.py -v`
Expected: ALL PASS

- [ ] **Step 9: Commit**

```bash
git add src/deepaper/gates.py src/deepaper/defaults.py src/deepaper/cli.py tests/test_gates.py tests/test_cli.py
git commit -m "fix: update CHAR_FLOORS to short-paper minimums and add version-aware slash command install"
```

---

### Task 2: Create prompt_builder.py — template parsing and auto-split

**Files:**
- Create: `src/deepaper/prompt_builder.py`
- Test: `tests/test_prompt_builder.py`

- [ ] **Step 1: Write tests for template section parsing**

```python
# tests/test_prompt_builder.py

import pytest


class TestParseTemplateSections:
    def test_extracts_all_seven_sections(self):
        from deepaper.prompt_builder import parse_template_sections
        from deepaper.defaults import DEFAULT_TEMPLATE

        sections = parse_template_sections(DEFAULT_TEMPLATE)
        expected_keys = [
            "核心速览",
            "动机与第一性原理",
            "方法详解",
            "实验与归因",
            "专家批判",
            "机制迁移分析",
            "背景知识补充",
        ]
        for key in expected_keys:
            assert key in sections, f"Missing section: {key}"
            assert len(sections[key]) > 50, f"Section {key} too short: {len(sections[key])}"

    def test_sections_contain_key_markers(self):
        from deepaper.prompt_builder import parse_template_sections
        from deepaper.defaults import DEFAULT_TEMPLATE

        sections = parse_template_sections(DEFAULT_TEMPLATE)
        assert "TL;DR" in sections["核心速览"]
        assert "一图流" in sections["核心速览"]
        assert "Because" in sections["动机与第一性原理"]
        assert "数值推演" in sections["方法详解"]
        assert "伪代码" in sections["方法详解"]
        assert "易混淆点" in sections["方法详解"]
        assert "归因分析" in sections["实验与归因"]
        assert "隐性成本" in sections["专家批判"]
        assert "机制解耦" in sections["机制迁移分析"]
        assert "迁移处方" in sections["机制迁移分析"]

    def test_extract_system_role(self):
        from deepaper.prompt_builder import extract_system_role
        from deepaper.defaults import DEFAULT_TEMPLATE

        role = extract_system_role(DEFAULT_TEMPLATE)
        assert "费曼技巧" in role
        assert "算法专家" in role


class TestExtractFrontmatterSpec:
    def test_extracts_frontmatter_section(self):
        from deepaper.prompt_builder import extract_frontmatter_spec
        from deepaper.defaults import DEFAULT_TEMPLATE

        spec = extract_frontmatter_spec(DEFAULT_TEMPLATE)
        assert "venue" in spec
        assert "baselines" in spec
        assert "datasets" in spec
        assert "metrics" in spec
        assert "tldr" in spec
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_prompt_builder.py::TestParseTemplateSections -v`
Expected: FAIL (module not found)

- [ ] **Step 3: Implement template parsing**

```python
# src/deepaper/prompt_builder.py

"""Prompt generation: template parsing, auto-split, gate contract injection."""
from __future__ import annotations

import json
import re
from pathlib import Path

from deepaper.defaults import DEFAULT_TEMPLATE

# Canonical section names and their order (matches DEFAULT_TEMPLATE)
SECTION_ORDER = [
    "核心速览",
    "动机与第一性原理",
    "方法详解",
    "实验与归因",
    "专家批判",
    "机制迁移分析",
    "背景知识补充",
]

# Sections that require PDF table pages and visual verification
VISUAL_SECTIONS = ["方法详解", "实验与归因"]

# Section heading pattern in DEFAULT_TEMPLATE: **## 中文名 (English Name)**
_TEMPLATE_SECTION_RE = re.compile(
    r"^\*\*##\s+(.+?)\s*\((.+?)\)\*\*\s*$", re.MULTILINE
)


def extract_system_role(template: str) -> str:
    """Extract the Role: line from the template header."""
    for line in template.split("\n"):
        if line.startswith("Role:"):
            return line
    return ""


def extract_frontmatter_spec(template: str) -> str:
    """Extract the YAML frontmatter specification block from the template."""
    match = re.search(r"### YAML Frontmatter\s*\n(.*?)```\s*\n", template, re.DOTALL)
    if match:
        return match.group(1).strip()
    # Fallback: extract between first ``` and closing ```
    blocks = re.findall(r"```\s*\n(.*?)\n```", template, re.DOTALL)
    for block in blocks:
        if "venue:" in block and "baselines:" in block:
            return block
    return ""


def parse_template_sections(template: str) -> dict[str, str]:
    """Split DEFAULT_TEMPLATE into {short_chinese_name: section_text}.

    Parses the **## 中文名 (English)** headings and extracts content
    between consecutive headings (up to the next --- or next heading).
    """
    sections: dict[str, str] = {}

    matches = list(_TEMPLATE_SECTION_RE.finditer(template))
    if not matches:
        return sections

    for i, m in enumerate(matches):
        chinese_name = m.group(1).strip()
        # Extract short name (before any space/parenthesis detail)
        short_name = chinese_name
        for canonical in SECTION_ORDER:
            if canonical in chinese_name:
                short_name = canonical
                break

        start = m.end()
        if i + 1 < len(matches):
            end = matches[i + 1].start()
        else:
            # Last section: go until "## 注意事项" or end
            end_marker = template.find("## 注意事项", start)
            end = end_marker if end_marker > 0 else len(template)

        content = template[start:end].strip()
        # Remove leading/trailing ---
        content = re.sub(r"^---\s*", "", content)
        content = re.sub(r"\s*---\s*$", "", content)
        sections[short_name] = content

    return sections
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_prompt_builder.py::TestParseTemplateSections tests/test_prompt_builder.py::TestExtractFrontmatterSpec -v`
Expected: PASS

- [ ] **Step 5: Write tests for auto-split**

```python
# tests/test_prompt_builder.py — add

class TestAutoSplit:
    def _profile(self, pages=10, tables=3, figures=4, equations=2):
        return {
            "total_pages": pages,
            "num_tables": tables,
            "num_figures": figures,
            "num_equations": equations,
        }

    def test_short_paper_two_writers(self):
        from deepaper.prompt_builder import auto_split
        tasks = auto_split(self._profile(pages=8, tables=3, figures=2, equations=1))
        # Short paper: 1 visual + 1 text
        assert len(tasks) == 2
        assert tasks[0].name == "writer-visual"
        assert set(tasks[0].sections) == {"方法详解", "实验与归因"}
        # All text sections in one writer
        text_sections = set()
        for t in tasks[1:]:
            text_sections.update(t.sections)
        assert "核心速览" in text_sections
        assert "机制迁移分析" in text_sections

    def test_long_paper_three_writers(self):
        from deepaper.prompt_builder import auto_split
        tasks = auto_split(self._profile(pages=120, tables=20, figures=22, equations=10))
        # Long paper: 1 visual + 2 text
        assert len(tasks) == 3
        assert tasks[0].name == "writer-visual"

    def test_visual_sections_always_together(self):
        from deepaper.prompt_builder import auto_split
        for pages in [8, 30, 120]:
            tasks = auto_split(self._profile(pages=pages))
            visual = tasks[0]
            assert visual.name == "writer-visual"
            assert "方法详解" in visual.sections
            assert "实验与归因" in visual.sections

    def test_all_sections_covered(self):
        from deepaper.prompt_builder import auto_split, SECTION_ORDER
        tasks = auto_split(self._profile(pages=50))
        all_sections = set()
        for t in tasks:
            all_sections.update(t.sections)
        assert all_sections == set(SECTION_ORDER)
```

- [ ] **Step 6: Run tests to verify they fail**

Run: `pytest tests/test_prompt_builder.py::TestAutoSplit -v`
Expected: FAIL (auto_split not implemented)

- [ ] **Step 7: Implement auto-split**

```python
# src/deepaper/prompt_builder.py — add after parse_template_sections

from dataclasses import dataclass, field
from deepaper.gates import CHAR_FLOORS


@dataclass
class WriterTask:
    name: str
    sections: list[str]
    needs_pdf_pages: bool = False


def compute_scaling_factor(section: str, profile: dict) -> float:
    """Estimate workload scaling for a section based on paper characteristics."""
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


def auto_split(profile: dict) -> list[WriterTask]:
    """Split sections across Writers: visual fixed, text by workload."""
    text_sections = [s for s in SECTION_ORDER if s not in VISUAL_SECTIONS]

    # Estimate workload per text section
    workloads = {
        s: CHAR_FLOORS.get(s, 500) * compute_scaling_factor(s, profile)
        for s in text_sections
    }

    # Visual workload (for reference when deciding text writer count)
    visual_workload = sum(
        CHAR_FLOORS.get(s, 1000) * compute_scaling_factor(s, profile)
        for s in VISUAL_SECTIONS
    )

    # Decide number of text writers
    total_text = sum(workloads.values())
    if total_text < visual_workload * 0.8:
        n_text = 1  # Text is light enough for one writer
    else:
        n_text = 2
    n_text = min(n_text, len(text_sections))  # Can't have more writers than sections

    # Greedy bin-pack: sort by workload descending, assign to lightest bin
    sorted_sections = sorted(text_sections, key=lambda s: workloads[s], reverse=True)
    bins: list[list[str]] = [[] for _ in range(n_text)]
    bin_loads = [0.0] * n_text

    for sec in sorted_sections:
        lightest = min(range(n_text), key=lambda i: bin_loads[i])
        bins[lightest].append(sec)
        bin_loads[lightest] += workloads[sec]

    # Restore original order within each bin
    for b in bins:
        b.sort(key=lambda s: SECTION_ORDER.index(s))

    # Build writer tasks
    tasks: list[WriterTask] = []
    tasks.append(WriterTask(
        name="writer-visual",
        sections=list(VISUAL_SECTIONS),
        needs_pdf_pages=True,
    ))
    for i, bin_sections in enumerate(bins):
        tasks.append(WriterTask(
            name=f"writer-text-{i}",
            sections=bin_sections,
            needs_pdf_pages=False,
        ))

    return tasks
```

- [ ] **Step 8: Run tests to verify they pass**

Run: `pytest tests/test_prompt_builder.py -v`
Expected: ALL PASS

- [ ] **Step 9: Commit**

```bash
git add src/deepaper/prompt_builder.py tests/test_prompt_builder.py
git commit -m "feat: add prompt_builder with template parsing and auto-split"
```

---

### Task 3: Gate contract injection and prompt generation

**Files:**
- Modify: `src/deepaper/prompt_builder.py`
- Test: `tests/test_prompt_builder.py`

- [ ] **Step 1: Write tests for gate contract generation**

```python
# tests/test_prompt_builder.py — add

class TestGatesToConstraints:
    def test_char_floor_in_constraints(self):
        from deepaper.prompt_builder import gates_to_constraints
        constraints = gates_to_constraints(
            sections=["方法详解", "实验与归因"],
            profile={"total_pages": 10, "num_tables": 5, "num_equations": 3},
            registry={"Table_1": {"type": "Table"}, "Table_2": {"type": "Table"}},
            core_figures=[{"id": 1, "key": "Figure_1"}],
        )
        assert "方法详解" in constraints
        assert "1,500" in constraints or "1500" in constraints  # floor
        assert "Figure 1" in constraints  # H7
        assert "h1/h2/h3" in constraints  # H6

    def test_tldr_constraint_for_executive_summary(self):
        from deepaper.prompt_builder import gates_to_constraints
        constraints = gates_to_constraints(
            sections=["核心速览", "动机与第一性原理"],
            profile={"total_pages": 10},
            registry={},
            core_figures=[],
        )
        assert "TL;DR" in constraints
        assert "≥2" in constraints  # H5

    def test_table_count_for_experiments(self):
        from deepaper.prompt_builder import gates_to_constraints
        registry = {f"Table_{i}": {"type": "Table"} for i in range(1, 8)}
        constraints = gates_to_constraints(
            sections=["方法详解", "实验与归因"],
            profile={"total_pages": 30, "num_tables": 7},
            registry=registry,
            core_figures=[],
        )
        assert "markdown" in constraints.lower()
        assert "表格" in constraints or "table" in constraints.lower()


class TestGenerateWriterPrompt:
    def test_prompt_contains_system_role(self):
        from deepaper.prompt_builder import (
            generate_writer_prompt, WriterTask, parse_template_sections,
            extract_system_role,
        )
        from deepaper.defaults import DEFAULT_TEMPLATE

        task = WriterTask(name="writer-text-0", sections=["核心速览"])
        prompt = generate_writer_prompt(
            task=task,
            run_dir="/tmp/test",
            template_sections=parse_template_sections(DEFAULT_TEMPLATE),
            system_role=extract_system_role(DEFAULT_TEMPLATE),
            figure_contexts={},
            constraints="- test constraint",
            pdf_path="",
            table_def_pages=[],
        )
        assert "费曼技巧" in prompt
        assert "算法专家" in prompt

    def test_prompt_contains_template_text_verbatim(self):
        from deepaper.prompt_builder import (
            generate_writer_prompt, WriterTask, parse_template_sections,
            extract_system_role,
        )
        from deepaper.defaults import DEFAULT_TEMPLATE

        sections = parse_template_sections(DEFAULT_TEMPLATE)
        task = WriterTask(name="writer-visual", sections=["方法详解"], needs_pdf_pages=True)
        prompt = generate_writer_prompt(
            task=task,
            run_dir="/tmp/test",
            template_sections=sections,
            system_role=extract_system_role(DEFAULT_TEMPLATE),
            figure_contexts={},
            constraints="",
            pdf_path="/tmp/test.pdf",
            table_def_pages=[7, 9],
        )
        # Template content should appear verbatim
        assert "数值推演" in prompt
        assert "【必做】" in prompt
        assert "伪代码" in prompt
        assert "易混淆点" in prompt

    def test_prompt_contains_figure_contexts(self):
        from deepaper.prompt_builder import (
            generate_writer_prompt, WriterTask, parse_template_sections,
            extract_system_role,
        )
        from deepaper.defaults import DEFAULT_TEMPLATE

        fig_ctx = {"Figure_1": {"caption": "Test caption", "references": ["ref1"]}}
        task = WriterTask(name="writer-text-0", sections=["核心速览"])
        prompt = generate_writer_prompt(
            task=task,
            run_dir="/tmp/test",
            template_sections=parse_template_sections(DEFAULT_TEMPLATE),
            system_role=extract_system_role(DEFAULT_TEMPLATE),
            figure_contexts=fig_ctx,
            constraints="",
            pdf_path="",
            table_def_pages=[],
        )
        assert "Test caption" in prompt
        assert "灵魂图" in prompt
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_prompt_builder.py::TestGatesToConstraints tests/test_prompt_builder.py::TestGenerateWriterPrompt -v`
Expected: FAIL

- [ ] **Step 3: Implement gates_to_constraints and generate_writer_prompt**

```python
# src/deepaper/prompt_builder.py — add after auto_split

def gates_to_constraints(
    sections: list[str],
    profile: dict,
    registry: dict,
    core_figures: list[dict],
) -> str:
    """Translate gate requirements into Writer prompt constraints."""
    lines = ["## ⚠️ 质量合同（写完后会被 programmatic 验证，不达标需返工）\n"]
    lines.append("**硬约束（gate 验证）：**")

    # H3: char floors
    for sec in sections:
        floor = CHAR_FLOORS.get(sec, 300)
        lines.append(f"- 「{sec}」≥ {floor:,} 字符（H3）")

    # H4: table count
    if "实验与归因" in sections:
        n_tables = sum(1 for v in registry.values() if v.get("type") == "Table")
        gate = min(n_tables, 6)
        if gate > 0:
            lines.append(f"- 输出 ≥ {gate} 张完整 markdown 对比表格（H4）")
        lines.append("- 表格数字必须从 notes MAIN_RESULTS 段逐项复制，禁止编造（H8）")

    # H5: TL;DR numbers
    if "核心速览" in sections:
        lines.append("- TL;DR 必须包含 ≥2 个具体量化数字，如 \"MATH 96.2%\"（H5）")

    # H6: heading levels
    lines.append("- 主标题 ####（h4），子标题 #####（h5），禁止 h1/h2/h3（H6）")

    # H7: core figure references
    if core_figures:
        fig_ids = [f"Figure {cf['id']}" for cf in core_figures]
        lines.append(f"- 必须引用灵魂图: {', '.join(fig_ids)}（H7）")

    # H1: baselines
    if "核心速览" in sections:
        lines.append("- YAML frontmatter baselines ≥ 2 个模型（H1）")

    # H9: content markers
    markers = _section_content_markers(sections)
    for m in markers:
        lines.append(f"- {m}（H9）")

    # Suggested targets
    lines.append("\n**建议目标：**")
    for sec in sections:
        floor = CHAR_FLOORS.get(sec, 300)
        suggested = int(floor * compute_scaling_factor(sec, profile))
        if suggested > floor * 1.5:
            lines.append(f"- 「{sec}」建议 ~{suggested:,} 字符")

    return "\n".join(lines)


def _section_content_markers(sections: list[str]) -> list[str]:
    """Return H9 content marker constraints relevant to the given sections."""
    markers = []
    if "方法详解" in sections:
        markers.append("数值推演【必做】必须存在")
        markers.append("伪代码（Python/PyTorch 代码块）必须存在")
        markers.append("易混淆点 ≥2 个 ❌/✅ 对")
    if "动机与第一性原理" in sections:
        markers.append("因果链 Because→Therefore 格式必须存在")
    if "专家批判" in sections:
        markers.append("隐性成本必须包含 ≥3 个具体数字")
    if "机制迁移分析" in sections:
        markers.append("机制解耦表格（4列: 原语名称|本文用途|抽象描述|信息论直觉）必须存在")
        markers.append("前身 (Ancestors) ≥ 3 个")
    return markers


def generate_writer_prompt(
    task: WriterTask,
    run_dir: str,
    template_sections: dict[str, str],
    system_role: str,
    figure_contexts: dict,
    constraints: str,
    pdf_path: str,
    table_def_pages: list[int],
) -> str:
    """Generate a complete prompt for one Writer agent."""
    parts = []

    # 1. System role (every writer gets this)
    parts.append(system_role)
    parts.append("")

    # 2. Gate contract (before section instructions)
    if constraints:
        parts.append(constraints)
        parts.append("")

    # 3. Figure contexts (broadcast to all writers)
    parts.append("## 灵魂图上下文（所有 Writer 共享）\n")
    if figure_contexts:
        parts.append(f"```json\n{json.dumps(figure_contexts, ensure_ascii=False, indent=2)}\n```\n")
        parts.append("在描述方法和实验时引用这些核心图，用 Figure N 格式。\n")
    else:
        parts.append("（本论文未检测到核心图）\n")

    # 4. Section instructions (verbatim from DEFAULT_TEMPLATE)
    parts.append("## 你的章节\n")
    parts.append("以下指令直接来自分析模板，请严格遵循。\n")
    for sec_name in task.sections:
        sec_text = template_sections.get(sec_name, "")
        parts.append(f"**#### {sec_name}**\n")
        parts.append(sec_text)
        parts.append("")

    # 5. Format rules
    parts.append("## 格式规则")
    parts.append("- 主标题: #### (h4)")
    parts.append("- 子标题: ##### (h5)")
    parts.append("- 禁止添加 '深度分析'、'Part' 等总标题")
    parts.append("- 禁止在章节间添加 `---` 分隔线")
    first_section = task.sections[0]
    if first_section == "核心速览":
        parts.append("- 文件开头必须是 `---`（YAML frontmatter 开始）")
    else:
        parts.append(f"- 文件开头直接是 `#### {first_section}`")
    parts.append("")

    # 6. Inputs
    parts.append("## 输入")
    parts.append(f"- 结构化笔记: {run_dir}/notes.md（先读这个）")
    parts.append(f"- 全文检索: {run_dir}/text.txt")
    if task.needs_pdf_pages and table_def_pages:
        parts.append(f"- PDF 表格验证页: {pdf_path}（仅读这些页: {table_def_pages}）")
    parts.append("")

    # 7. Output
    output_file = f"{run_dir}/part_{task.name.replace('writer-', '')}.md"
    parts.append("## 输出")
    parts.append(f"写入文件: `{output_file}`")
    parts.append("写完后对照上方「质量合同」逐项自检，不达标立即补充。")

    return "\n".join(parts)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_prompt_builder.py -v`
Expected: ALL PASS

- [ ] **Step 5: Commit**

```bash
git add src/deepaper/prompt_builder.py tests/test_prompt_builder.py
git commit -m "feat: add gate contract injection and writer prompt generation"
```

---

### Task 4: Create content_checklist.py (H9 ContentMarkers gate)

**Files:**
- Create: `src/deepaper/content_checklist.py`
- Modify: `src/deepaper/gates.py`
- Test: `tests/test_content_checklist.py`
- Modify: `tests/test_gates.py`

- [ ] **Step 1: Write tests for content marker detection**

```python
# tests/test_content_checklist.py

import pytest


class TestCheckContentMarkers:
    def test_pass_on_complete_output(self):
        from deepaper.content_checklist import check_content_markers

        md = (
            "---\ntldr: test\n---\n"
            "#### 核心速览\n"
            "- **TL;DR:** 在 MATH 达 96.2%\n"
            "- **一图流:** 如果旧方法是X\n"
            "- **核心机制一句话:** [压缩] + [表示] + [渐进式] + [提升效率]\n\n"
            "#### 动机与第一性原理\n"
            "Because A导致B → Therefore C解决了D → 最终E\n\n"
            "#### 方法详解\n"
            "##### 数值推演\n假设 x=3, 代入公式...\n"
            "```python\ndef train(): pass\n```\n"
            "##### 易混淆点\n"
            "- ❌ 错误: blah\n- ✅ 正确: blah\n"
            "- ❌ 错误: blah2\n- ✅ 正确: blah2\n\n"
            "#### 实验与归因\n归因分析排序\n\n"
            "#### 专家批判\n隐性成本: 训练花了47天, 1024个GPU, 2.75M美元\n\n"
            "#### 机制迁移分析\n"
            "| 原语名称 | 本文用途 | 抽象描述 | 信息论/几何直觉 |\n"
            "|---|---|---|---|\n"
            "| A | B | C | D |\n"
            "前身 (Ancestors):\n- Method1\n- Method2\n- Method3\n"
        )
        result = check_content_markers(md)
        assert result["passed"] is True
        assert result["score"] >= 0.7

    def test_fail_on_missing_pseudocode(self):
        from deepaper.content_checklist import check_content_markers

        md = (
            "---\ntldr: test\n---\n"
            "#### 方法详解\n"
            "##### 数值推演\n假设 x=3\n"
            "##### 易混淆点\n- ❌ A\n- ✅ B\n- ❌ C\n- ✅ D\n"
        )
        result = check_content_markers(md)
        assert "方法详解:伪代码" in result["missing"]

    def test_fail_on_missing_causal_chain(self):
        from deepaper.content_checklist import check_content_markers

        md = (
            "---\ntldr: test\n---\n"
            "#### 动机与第一性原理\n"
            "这个方法很好因为它解决了问题。\n"
        )
        result = check_content_markers(md)
        assert "动机与第一性原理:因果链" in result["missing"]
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_content_checklist.py -v`
Expected: FAIL (module not found)

- [ ] **Step 3: Implement content_checklist.py**

```python
# src/deepaper/content_checklist.py

"""H9 ContentMarkers — verify DEFAULT_TEMPLATE's content requirements are met."""
from __future__ import annotations

import re

# Section-level content markers extracted from DEFAULT_TEMPLATE
CONTENT_MARKERS: dict[str, list[dict]] = {
    "核心速览": [
        {"marker": "TL;DR", "check": "contains_pattern", "pattern": r"TL;DR.*\d+"},
        {"marker": "一图流", "check": "section_exists", "pattern": r"一图流"},
        {"marker": "核心机制一句话", "check": "contains_pattern", "pattern": r"\[.+?\].*\+.*\[.+?\]"},
    ],
    "动机与第一性原理": [
        {"marker": "因果链", "check": "contains_pattern", "pattern": r"(?:Because|因为|由于).*(?:→|Therefore|所以|因此)"},
    ],
    "方法详解": [
        {"marker": "数值推演", "check": "section_exists", "pattern": r"数值推演"},
        {"marker": "伪代码", "check": "contains_pattern", "pattern": r"```(?:python|pseudo|py)"},
        {"marker": "易混淆点", "check": "contains_pattern", "pattern": r"❌.*✅|✅.*❌"},
    ],
    "实验与归因": [
        {"marker": "归因分析", "check": "section_exists", "pattern": r"(?:归因|ablation|贡献排序)"},
    ],
    "专家批判": [
        {"marker": "隐性成本含数字", "check": "contains_numbers_in_section", "min_count": 3},
    ],
    "机制迁移分析": [
        {"marker": "机制解耦表格", "check": "contains_pattern",
         "pattern": r"\|.*(?:原语|名称).*\|.*(?:用途|本文).*\|"},
        {"marker": "前身Ancestors", "check": "contains_pattern", "pattern": r"(?:前身|Ancestor)"},
    ],
}

_NUMBER_RE = re.compile(r"\b\d+(?:\.\d+)?(?:\s*(?:%|天|day|hour|小时|GPU|M|B|K|T|倍|x))")


def _extract_section_text(md: str, section_name: str) -> str:
    """Extract text under a #### section heading."""
    pattern = re.compile(
        rf"####\s*{re.escape(section_name)}.*?\n(.*?)(?=\n####\s|\Z)",
        re.DOTALL,
    )
    m = pattern.search(md)
    return m.group(1).strip() if m else ""


def check_content_markers(md: str) -> dict:
    """H9: Verify DEFAULT_TEMPLATE content requirements are present in output."""
    results: dict[str, bool] = {}

    for section, markers in CONTENT_MARKERS.items():
        section_text = _extract_section_text(md, section)
        if not section_text:
            # Section missing entirely — mark all markers as failed
            for m in markers:
                results[f"{section}:{m['marker']}"] = False
            continue

        for m in markers:
            key = f"{section}:{m['marker']}"
            check_type = m["check"]

            if check_type == "section_exists":
                results[key] = bool(re.search(m["pattern"], section_text, re.IGNORECASE))
            elif check_type == "contains_pattern":
                results[key] = bool(re.search(m["pattern"], section_text, re.DOTALL))
            elif check_type == "contains_numbers_in_section":
                numbers = _NUMBER_RE.findall(section_text)
                results[key] = len(numbers) >= m.get("min_count", 1)
            else:
                results[key] = False

    total = len(results)
    passed_count = sum(1 for v in results.values() if v)
    score = passed_count / total if total > 0 else 1.0

    return {
        "passed": score >= 0.7,
        "score": round(score, 4),
        "total": total,
        "passed_count": passed_count,
        "missing": [k for k, v in results.items() if not v],
        "details": results,
    }
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_content_checklist.py -v`
Expected: ALL PASS

- [ ] **Step 5: Integrate H9 into gates.py**

```python
# src/deepaper/gates.py — add import at top
from deepaper.content_checklist import check_content_markers

# In run_hard_gates function, add after H8 block:

    # H9: Content Markers
    results["H9"] = check_content_markers(merged_md)
```

- [ ] **Step 6: Write integration test for H9 in gates**

```python
# tests/test_gates.py — add new class

class TestH9ContentMarkers:
    def test_h9_included_in_run_hard_gates(self):
        from deepaper.gates import run_hard_gates

        md = (
            "---\nbaselines:\n  - A\n  - B\ntldr: MATH 96.2% on benchmark\n---\n"
            "#### 核心速览\n- **TL;DR:** MATH达96.2%\n- **一图流:** 类比\n"
            "- **核心机制一句话:** [A]+[B]+[C]+[D]\n"
        )
        result = run_hard_gates(md, {}, [], None, None)
        assert "H9" in result["results"]
```

- [ ] **Step 7: Run all gate tests**

Run: `pytest tests/test_gates.py tests/test_content_checklist.py -v`
Expected: ALL PASS

- [ ] **Step 8: Commit**

```bash
git add src/deepaper/content_checklist.py src/deepaper/gates.py tests/test_content_checklist.py tests/test_gates.py
git commit -m "feat: add H9 ContentMarkers gate for template compliance checking"
```

---

### Task 5: New CLI commands — extract, check, prompt, merge, fix, classify

**Files:**
- Modify: `src/deepaper/cli.py`
- Test: `tests/test_cli.py`

- [ ] **Step 1: Write test for `deepaper extract`**

```python
# tests/test_cli.py — add

class TestExtract:
    def test_extract_creates_all_artifacts(self, tmp_path: Path) -> None:
        """Extract should create text_by_page.json, text.txt, registry, profile, core_figures, figure_contexts."""
        # Create a minimal PDF
        import fitz
        doc = fitz.open()
        page = doc.new_page()
        page.insert_text((50, 50), "Introduction\nWe propose a method. See Table 1.\n"
                         "Table 1: Results of our method compared to baselines.\n"
                         "Figure 1: Overview of our architecture with detailed components.\n")
        pdf_path = tmp_path / "tmp" / "2301.00001.pdf"
        pdf_path.parent.mkdir()
        doc.save(str(pdf_path))
        doc.close()

        old_cwd = os.getcwd()
        os.chdir(tmp_path)
        try:
            result = runner.invoke(app, ["extract", "2301.00001"])
            assert result.exit_code == 0
            output = json.loads(result.stdout)
            assert output["total_pages"] == 1

            run_dir = tmp_path / ".deepaper" / "runs" / "2301.00001"
            assert (run_dir / "text_by_page.json").exists()
            assert (run_dir / "text.txt").exists()
            assert (run_dir / "visual_registry.json").exists()
            assert (run_dir / "paper_profile.json").exists()
            assert (run_dir / "core_figures.json").exists()
            assert (run_dir / "figure_contexts.json").exists()
        finally:
            os.chdir(old_cwd)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_cli.py::TestExtract -v`
Expected: FAIL (no extract command)

- [ ] **Step 3: Implement `extract` command**

```python
# src/deepaper/cli.py — add after existing commands

@app.command()
def extract(
    arxiv_id: str = typer.Argument(..., help="arxiv ID to extract."),
) -> None:
    """Extract text from PDF and build registry, profile, core figures, and figure contexts."""
    import fitz
    from deepaper.pipeline_io import safe_write_json, ensure_run_dir
    from deepaper.registry import (
        build_visual_registry, compute_paper_profile,
        identify_core_figures, extract_figure_contexts,
    )

    root = Path.cwd()
    pdf_path = root / "tmp" / f"{arxiv_id}.pdf"
    if not pdf_path.exists():
        typer.echo(json.dumps({"error": f"PDF not found: {pdf_path}"}))
        raise typer.Exit(1)

    run_dir = ensure_run_dir(root, arxiv_id)

    # 1. Extract text
    doc = fitz.open(str(pdf_path))
    text_by_page: dict[str, str] = {}
    full_lines: list[str] = []
    for i, page in enumerate(doc):
        text = page.get_text()
        text_by_page[str(i + 1)] = text
        full_lines.append(f"--- PAGE {i + 1} ---\n{text}")
    doc.close()

    safe_write_json(str(run_dir / "text_by_page.json"), text_by_page)
    (run_dir / "text.txt").write_text("\n".join(full_lines), encoding="utf-8")

    # 2. Build registry and profile
    int_text = {int(k): v for k, v in text_by_page.items()}
    registry = build_visual_registry(int_text)
    safe_write_json(str(run_dir / "visual_registry.json"), registry)

    profile = compute_paper_profile(int_text, registry)
    safe_write_json(str(run_dir / "paper_profile.json"), profile)

    # 3. Core figures + contexts
    core_figs = identify_core_figures(registry, int_text, profile["total_pages"])
    safe_write_json(str(run_dir / "core_figures.json"), core_figs)

    fig_contexts = extract_figure_contexts(int_text, core_figs)
    safe_write_json(str(run_dir / "figure_contexts.json"), fig_contexts)

    # 4. Table definition pages
    table_def_pages = sorted(set(
        v["definition_page"] for v in registry.values()
        if v.get("type") == "Table" and v.get("definition_page")
    ))

    typer.echo(json.dumps({
        "run_dir": str(run_dir),
        "total_pages": profile["total_pages"],
        "num_tables": profile["num_tables"],
        "num_figures": profile["num_figures"],
        "num_equations": profile["num_equations"],
        "core_figures": [cf["key"] for cf in core_figs],
        "table_def_pages": table_def_pages,
    }, ensure_ascii=False, indent=2))
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_cli.py::TestExtract -v`
Expected: PASS

- [ ] **Step 5: Implement `check` command**

```python
# src/deepaper/cli.py — add

@app.command()
def check(
    arxiv_id: str = typer.Argument(..., help="arxiv ID to check."),
) -> None:
    """Run StructCheck + Auditor on Extractor notes."""
    from deepaper.pipeline_io import safe_read_json, ensure_run_dir
    from deepaper.extractor import struct_check, audit_coverage

    root = Path.cwd()
    run_dir = ensure_run_dir(root, arxiv_id)
    notes_path = run_dir / "notes.md"

    if not notes_path.exists():
        typer.echo(json.dumps({"error": "notes.md not found"}))
        raise typer.Exit(1)

    notes = notes_path.read_text(encoding="utf-8")
    text_by_page_raw = safe_read_json(str(run_dir / "text_by_page.json"), {})
    text_by_page = {int(k): v for k, v in text_by_page_raw.items()}
    profile = safe_read_json(str(run_dir / "paper_profile.json"), {})
    total_pages = profile.get("total_pages", len(text_by_page))

    sc = struct_check(notes, total_pages, profile)
    ac = audit_coverage(text_by_page, notes, total_pages)

    result = {
        "passed": sc["passed"] and ac["coverage_ratio"] >= 0.7,
        "struct_check": sc,
        "audit": {
            "coverage_ratio": ac["coverage_ratio"],
            "uncovered_segments": ac["uncovered_segments"],
        },
    }
    safe_read_json  # ensure import
    from deepaper.pipeline_io import safe_write_json
    safe_write_json(str(run_dir / "check.json"), result)
    typer.echo(json.dumps(result, indent=2))
```

- [ ] **Step 6: Implement `prompt` command**

```python
# src/deepaper/cli.py — add

@app.command()
def prompt(
    arxiv_id: str = typer.Argument(..., help="arxiv ID."),
    role: Optional[str] = typer.Option(None, "--role", help="Agent role: extractor"),
    split: bool = typer.Option(False, "--split", help="Auto-split into Writer prompts."),
) -> None:
    """Generate agent prompts. Use --role extractor or --split for writers."""
    from deepaper.pipeline_io import safe_read_json, safe_write_json, ensure_run_dir
    from deepaper.prompt_builder import (
        parse_template_sections, extract_system_role,
        auto_split, gates_to_constraints, generate_writer_prompt,
    )
    from deepaper.defaults import DEFAULT_TEMPLATE

    root = Path.cwd()
    run_dir = ensure_run_dir(root, arxiv_id)
    pdf_path = root / "tmp" / f"{arxiv_id}.pdf"

    if role == "extractor":
        # Load extractor prompt template and fill variables
        tmpl_path = Path(__file__).parent.parent.parent / "docs" / "superpowers" / "specs" / "prompts" / "extractor.md"
        if not tmpl_path.exists():
            # Fallback: use built-in template
            tmpl_path = Path(__file__).parent / "prompt_templates" / "extractor.md"
        if tmpl_path.exists():
            tmpl = tmpl_path.read_text(encoding="utf-8")
        else:
            typer.echo(json.dumps({"error": "extractor prompt template not found"}))
            raise typer.Exit(1)

        profile = safe_read_json(str(run_dir / "paper_profile.json"), {})
        prompt_text = (tmpl
            .replace("{RUN_DIR}", str(run_dir))
            .replace("{TOTAL_PAGES}", str(profile.get("total_pages", "?")))
            .replace("{ARXIV_ID}", arxiv_id))

        out_path = run_dir / "prompt_extractor.md"
        out_path.write_text(prompt_text, encoding="utf-8")
        typer.echo(json.dumps({"prompt_file": str(out_path)}))
        return

    if split:
        profile = safe_read_json(str(run_dir / "paper_profile.json"), {})
        registry = safe_read_json(str(run_dir / "visual_registry.json"), {})
        core_figures = safe_read_json(str(run_dir / "core_figures.json"), [])
        figure_contexts = safe_read_json(str(run_dir / "figure_contexts.json"), {})

        table_def_pages = sorted(set(
            v["definition_page"] for v in (registry or {}).values()
            if v.get("type") == "Table" and v.get("definition_page")
        ))

        template_sections = parse_template_sections(DEFAULT_TEMPLATE)
        system_role = extract_system_role(DEFAULT_TEMPLATE)
        tasks = auto_split(profile or {})

        writers_config = {"writers": [], "merge_order": [], "figure_contexts": figure_contexts}

        for task in tasks:
            constraints = gates_to_constraints(
                sections=task.sections,
                profile=profile or {},
                registry=registry or {},
                core_figures=core_figures or [],
            )
            prompt_text = generate_writer_prompt(
                task=task,
                run_dir=str(run_dir),
                template_sections=template_sections,
                system_role=system_role,
                figure_contexts=figure_contexts or {},
                constraints=constraints,
                pdf_path=str(pdf_path),
                table_def_pages=table_def_pages,
            )
            prompt_file = run_dir / f"prompt_{task.name}.md"
            prompt_file.write_text(prompt_text, encoding="utf-8")

            output_file = f"part_{task.name.replace('writer-', '')}.md"
            writers_config["writers"].append({
                "name": task.name,
                "sections": task.sections,
                "prompt_file": str(prompt_file),
                "output_file": output_file,
            })

        # merge_order: text writers in section order, visual in the middle
        text_writers = [w for w in writers_config["writers"] if not w["name"].endswith("visual")]
        visual_writers = [w for w in writers_config["writers"] if w["name"].endswith("visual")]
        # Order: first text writer(s) that have early sections, then visual, then remaining text
        if len(text_writers) >= 2:
            writers_config["merge_order"] = [text_writers[0]["name"], visual_writers[0]["name"], text_writers[1]["name"]]
        elif text_writers:
            writers_config["merge_order"] = [text_writers[0]["name"], visual_writers[0]["name"]]
        else:
            writers_config["merge_order"] = [visual_writers[0]["name"]]

        safe_write_json(str(run_dir / "writers.json"), writers_config)
        typer.echo(json.dumps(writers_config, ensure_ascii=False, indent=2))
        return

    typer.echo("Use --role extractor or --split")
    raise typer.Exit(1)
```

- [ ] **Step 7: Implement `merge` command**

```python
# src/deepaper/cli.py — add

@app.command()
def merge(
    arxiv_id: str = typer.Argument(..., help="arxiv ID to merge."),
) -> None:
    """Merge Writer outputs in canonical order and normalize formatting."""
    import re as _re
    from deepaper.pipeline_io import safe_read_json, ensure_run_dir

    root = Path.cwd()
    run_dir = ensure_run_dir(root, arxiv_id)
    config = safe_read_json(str(run_dir / "writers.json"))

    if not config:
        typer.echo(json.dumps({"error": "writers.json not found"}))
        raise typer.Exit(1)

    parts = []
    for writer_name in config["merge_order"]:
        writer = next((w for w in config["writers"] if w["name"] == writer_name), None)
        if not writer:
            continue
        part_path = run_dir / writer["output_file"]
        if part_path.exists():
            parts.append(part_path.read_text(encoding="utf-8"))

    merged = "\n\n".join(parts)

    # Normalize: remove stray --- outside YAML frontmatter
    if merged.startswith("---"):
        fm_end = merged.find("---", 3)
        if fm_end > 0:
            yaml_block = merged[:fm_end + 3]
            body = merged[fm_end + 3:]
            body = _re.sub(r"\n---\s*\n", "\n\n", body)
            merged = yaml_block + body

    # Remove stray title lines
    merged = _re.sub(r"^#{1,3}\s+.*(?:Part [ABC]|深度分析|部分).*\n+", "", merged, flags=_re.MULTILINE)

    merged_path = run_dir / "merged.md"
    merged_path.write_text(merged, encoding="utf-8")

    # Also copy as final.md initially
    (run_dir / "final.md").write_text(merged, encoding="utf-8")

    typer.echo(json.dumps({"merged": str(merged_path), "chars": len(merged)}))
```

- [ ] **Step 8: Implement `fix` command**

```python
# src/deepaper/cli.py — add

@app.command()
def fix(
    arxiv_id: str = typer.Argument(..., help="arxiv ID to generate fix prompt for."),
) -> None:
    """Generate Fixer agent prompt from gate failures."""
    from deepaper.pipeline_io import safe_read_json, ensure_run_dir

    root = Path.cwd()
    run_dir = ensure_run_dir(root, arxiv_id)
    gates_result = safe_read_json(str(run_dir / "gates.json"))

    if not gates_result:
        typer.echo(json.dumps({"error": "gates.json not found"}))
        raise typer.Exit(1)

    if gates_result.get("passed", False):
        typer.echo(json.dumps({"needs_fix": False}))
        return

    figure_contexts = safe_read_json(str(run_dir / "figure_contexts.json"), {})
    lines = ["你是论文分析修复专员。以下问题来自 programmatic 质量检查，请逐一修复。\n"]
    lines.append("## 需要修复的问题\n")

    for gate_name in gates_result.get("failed", []):
        gate = gates_result["results"].get(gate_name, {})
        lines.append(f"### {gate_name}")

        if gate_name == "H3":
            for f in gate.get("failures", []):
                lines.append(f"- 「{f['section']}」当前 {f['actual']:,} 字符 < {f['floor']:,} 门控")
                lines.append(f"  → 从 notes.md 的相关段落补充内容")
        elif gate_name == "H7":
            for fig_key in gate.get("missing", []):
                ctx = figure_contexts.get(fig_key, {})
                lines.append(f"- {fig_key} 未被引用。Caption: {ctx.get('caption', 'N/A')}")
        elif gate_name == "H9":
            for marker in gate.get("missing", []):
                lines.append(f"- {marker} 未找到")
        else:
            lines.append(f"- {json.dumps(gate, ensure_ascii=False)}")
        lines.append("")

    lines.append("## 输入")
    lines.append(f"- 当前分析: {run_dir}/merged.md（直接修改此文件）")
    lines.append(f"- 补充来源: {run_dir}/notes.md\n")
    lines.append("## 规则")
    lines.append("- 只修改有问题的部分，不要重写正常内容")
    lines.append("- 修复后的文件保存为 merged_fixed.md（保留原 merged.md 不覆盖）")

    prompt_text = "\n".join(lines)
    prompt_path = run_dir / "prompt_fix.md"
    prompt_path.write_text(prompt_text, encoding="utf-8")

    typer.echo(json.dumps({
        "needs_fix": True,
        "prompt_file": str(prompt_path),
        "failed": gates_result["failed"],
    }))
```

- [ ] **Step 9: Implement `classify` command**

```python
# src/deepaper/cli.py — add

@app.command()
def classify(
    arxiv_id: str = typer.Argument(..., help="arxiv ID to classify."),
) -> None:
    """Generate classification prompt from categories.md rules."""
    from deepaper.pipeline_io import safe_read_json, ensure_run_dir
    from deepaper.config import load_config
    from deepaper.templates import load_template

    root = Path.cwd()
    run_dir = ensure_run_dir(root, arxiv_id)
    config = load_config(root)

    notes_path = run_dir / "notes.md"
    if not notes_path.exists():
        typer.echo(json.dumps({"error": "notes.md not found"}))
        raise typer.Exit(1)

    notes = notes_path.read_text(encoding="utf-8")
    # Extract META section as summary
    meta_match = re.search(r"## META\n(.*?)(?=\n## |\Z)", notes, re.DOTALL)
    summary = meta_match.group(1).strip() if meta_match else notes[:500]

    categories = load_template("categories", config.templates_path)
    classify_tmpl = load_template("classify", config.templates_path)

    prompt_text = classify_tmpl.format(summary=summary, categories=categories)
    prompt_path = run_dir / "prompt_classify.md"
    prompt_path.write_text(prompt_text, encoding="utf-8")

    typer.echo(json.dumps({"prompt_file": str(prompt_path)}))
```

- [ ] **Step 10: Run all tests**

Run: `pytest tests/test_cli.py -v`
Expected: ALL PASS

- [ ] **Step 11: Commit**

```bash
git add src/deepaper/cli.py tests/test_cli.py
git commit -m "feat: add extract, check, prompt, merge, fix, classify CLI commands"
```

---

### Task 6: Rewrite slash command as thin dispatcher

**Files:**
- Rewrite: `.claude/commands/deepaper.md`

- [ ] **Step 1: Write the new slash command**

```markdown
<!-- deepaper-version: 2 -->
Analyze an arxiv paper and save to the deepaper knowledge base using a multi-agent pipeline.

## Step 0: Setup

Run `which deepaper` to check. If not found: `pip install deepaper && deepaper init`.
If papers/ directory exists, skip init.

## Step 1: Download & Extract

```bash
deepaper download $ARGUMENTS
```
Parse JSON output → ARXID, PDF_PATH.

```bash
deepaper extract ARXID
```
Parse JSON output → RUN_DIR, TOTAL_PAGES, CORE_FIGURES, TABLE_DEF_PAGES.

## Step 2: Extractor Agent

```bash
deepaper prompt ARXID --role extractor
```
Parse JSON output → prompt_file. Read the prompt file content.
Spawn one Agent (subagent_type: executor, name: extractor) with that prompt content.
Wait for it to finish writing notes.md.

```bash
deepaper check ARXID
```
If passed=false → read check.json failures, spawn one retry Agent (subagent_type: executor, name: extractor-retry) with the failure details and instructions to supplement notes.md. Max 1 retry.

## Step 3: Writers (parallel)

```bash
deepaper prompt ARXID --split
```
Parse JSON output → writers array with prompt_file for each.

For EACH writer in the array, spawn an Agent (subagent_type: executor) in parallel:
- Read the writer's prompt_file content
- Give it as the agent prompt
- Name it the writer's name from the config

Wait for all writers to complete.

## Step 4: Merge + Gates

```bash
deepaper merge ARXID
deepaper gates ARXID
```

If gates passed=false:
```bash
deepaper fix ARXID
```
Read prompt_file from output, spawn Fixer Agent (subagent_type: executor, name: fixer).
Fixer writes merged_fixed.md. Copy it as final.md.
Re-run `deepaper gates ARXID` on the fixed version (max 2 rounds total).

If gates passed=true: final.md is already set.

## Step 5: Classify + Save

```bash
deepaper classify ARXID
```
Read prompt_classify.md content and determine the category (the classify prompt contains the full category rules — read it and output the JSON classification yourself).

```bash
deepaper save ARXID --category CATEGORY --input .deepaper/runs/ARXID/final.md
```

Report the saved path and category to the user.
```

- [ ] **Step 2: Verify version marker is present**

Check that the file starts with `<!-- deepaper-version: 2 -->`.

- [ ] **Step 3: Run install test to verify version detection works with new content**

Run: `pytest tests/test_cli.py::TestAutoInstallVersion -v`
Expected: PASS

- [ ] **Step 4: Commit**

```bash
git add .claude/commands/deepaper.md
git commit -m "feat: rewrite slash command as thin dispatcher (~60 lines)"
```

---

### Task 7: Copy prompt templates into package for distribution

**Files:**
- Create: `src/deepaper/prompt_templates/extractor.md` (copy from specs/prompts)
- Create: `src/deepaper/prompt_templates/extractor_retry.md`
- Create: `src/deepaper/prompt_templates/fixer.md`
- Create: `src/deepaper/prompt_templates/critic.md`
- Create: `src/deepaper/prompt_templates/classify.md`

- [ ] **Step 1: Create prompt_templates directory and copy templates**

Copy from `docs/superpowers/specs/prompts/` to `src/deepaper/prompt_templates/`, keeping only the runtime templates (writer prompts are generated dynamically by prompt_builder, so they don't need static files).

```bash
mkdir -p src/deepaper/prompt_templates
cp docs/superpowers/specs/prompts/extractor.md src/deepaper/prompt_templates/
cp docs/superpowers/specs/prompts/extractor-retry.md src/deepaper/prompt_templates/extractor_retry.md
cp docs/superpowers/specs/prompts/fixer.md src/deepaper/prompt_templates/
cp docs/superpowers/specs/prompts/critic.md src/deepaper/prompt_templates/
cp docs/superpowers/specs/prompts/classify.md src/deepaper/prompt_templates/
```

Note: Writer prompts (writer-visual.md, writer-text-0.md, writer-text-1.md) are NOT copied because they are generated dynamically by `prompt_builder.py` from DEFAULT_TEMPLATE. The specs/prompts versions are reference documentation only.

- [ ] **Step 2: Update `deepaper prompt --role extractor` to find the template in package**

The implementation in Task 5 Step 6 already has fallback logic. Verify the path resolves correctly:

```python
# Verify in cli.py prompt command, the extractor template path:
tmpl_path = Path(__file__).parent / "prompt_templates" / "extractor.md"
```

- [ ] **Step 3: Commit**

```bash
git add src/deepaper/prompt_templates/
git commit -m "feat: add runtime prompt templates to package"
```

---

### Task 8: Integration test — gates pass on slash_v3 reference output

**Files:**
- Modify: `tests/test_gates.py`

- [ ] **Step 1: Write integration test**

```python
# tests/test_gates.py — add

class TestGatesOnSlashV3:
    """The slash_v3 reference output should pass all gates including H9."""

    def test_slash_v3_passes_all_hard_gates(self):
        from deepaper.gates import run_hard_gates

        fixture = Path(__file__).parent / "fixtures" / "olmo3_slash_v3.md"
        if not fixture.exists():
            pytest.skip("slash_v3 fixture not found")

        md = fixture.read_text(encoding="utf-8")
        result = run_hard_gates(md, {}, [], None, None)

        # H1: baselines
        assert result["results"]["H1"]["passed"], f"H1 failed: {result['results']['H1']}"
        # H3: char floors
        assert result["results"]["H3"]["passed"], f"H3 failed: {result['results']['H3']}"
        # H5: TL;DR numbers
        assert result["results"]["H5"]["passed"], f"H5 failed: {result['results']['H5']}"
        # H6: heading levels
        assert result["results"]["H6"]["passed"], f"H6 failed: {result['results']['H6']}"
        # H9: content markers
        assert result["results"]["H9"]["passed"], f"H9 failed: {result['results']['H9']}"

    def test_current_bad_output_fails_gates(self):
        """The freestyle output should fail at least H6 and H9."""
        from deepaper.gates import run_hard_gates

        # Simulate the bad output structure (h2 headings, no template sections)
        md = (
            "---\nbaselines:\n  - A\n  - B\ntldr: test 96.2 percent\n---\n"
            "## 1. 论文概述\nSome content\n"
            "## 2. 核心技术贡献\nMore content\n"
        )
        result = run_hard_gates(md, {}, [], None, None)
        # H6 should fail (uses h2 instead of h4)
        assert result["results"]["H6"]["passed"] is False
```

- [ ] **Step 2: Run integration test**

Run: `pytest tests/test_gates.py::TestGatesOnSlashV3 -v`
Expected: PASS (slash_v3 passes, bad output fails)

- [ ] **Step 3: Commit**

```bash
git add tests/test_gates.py
git commit -m "test: add integration tests verifying slash_v3 passes all gates"
```

---

### Task 9: Run full test suite and verify

- [ ] **Step 1: Run entire test suite**

Run: `pytest tests/ -v --tb=short`
Expected: ALL PASS, no regressions

- [ ] **Step 2: Verify prompt generation end-to-end**

Run manually in the deepaper project directory:
```bash
# Requires OLMo 3 PDF in tmp/
deepaper extract 2512.13961
deepaper prompt 2512.13961 --split
# Check generated prompts contain template text
grep "费曼技巧" .deepaper/runs/2512.13961/prompt_writer_*.md
grep "数值推演" .deepaper/runs/2512.13961/prompt_writer_visual.md
grep "质量合同" .deepaper/runs/2512.13961/prompt_writer_*.md
```
Expected: All greps find matches.

- [ ] **Step 3: Commit any final fixes**

```bash
git add -A
git commit -m "chore: final verification pass"
```
