"""Prompt generation: template parsing, auto-split, gate contract injection."""
from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path

from deepaper.output_schema import (
    CHAR_FLOORS,
    FRONTMATTER_FIELDS,
    HEADING_SECTION_LEVEL,
    HEADING_SUBSECTION_LEVEL,
    SECTION_ORDER as _SCHEMA_SECTION_ORDER,
)

# Canonical section names and their order (matches DEFAULT_TEMPLATE)
SECTION_ORDER = _SCHEMA_SECTION_ORDER

# Sections that may benefit from PDF table pages for verification
VISUAL_SECTIONS = ["技术精要"]

# Writer task definitions for the v2 4-section layout.
# Fixed assignment: paper length does not affect split.
WRITER_ASSIGNMENTS: list[tuple[str, list[str], bool]] = [
    # (writer_name, sections, needs_pdf_pages)
    ("writer-overview", ["核心速览", "机制迁移"], False),
    ("writer-principle", ["第一性原理分析"], False),
    ("writer-technical", ["技术精要"], True),
]

# Section heading pattern in DEFAULT_TEMPLATE: **## 中文名 (English Name)**
_TEMPLATE_SECTION_RE = re.compile(
    r"^\*\*##\s+(.+?)\s*\((.+?)\)\*\*\s*$", re.MULTILINE
)


@dataclass
class WriterTask:
    name: str
    sections: list
    needs_pdf_pages: bool = False


def extract_system_role(template: str) -> str:
    """Extract the Role: line from the template header."""
    for line in template.split("\n"):
        if line.startswith("Role:"):
            return line
    return ""


def extract_frontmatter_spec(template: str) -> str:
    """Extract the YAML frontmatter specification block from the template."""
    # Look for the ``` block that contains venue:/baselines:/datasets:
    blocks = re.findall(r"```\s*\n(.*?)\n```", template, re.DOTALL)
    for block in blocks:
        if "baselines:" in block and ("venue:" in block or "tldr:" in block):
            return block
    return ""


def parse_template_sections(template: str) -> dict[str, str]:
    """Split DEFAULT_TEMPLATE into {short_chinese_name: section_text}.

    Parses the **## 中文名 (English)** headings and extracts content
    between consecutive headings.
    """
    sections: dict[str, str] = {}

    matches = list(_TEMPLATE_SECTION_RE.finditer(template))
    if not matches:
        return sections

    for i, m in enumerate(matches):
        chinese_name = m.group(1).strip()
        # Map to canonical name
        short_name = chinese_name
        for canonical in SECTION_ORDER:
            if canonical in chinese_name:
                short_name = canonical
                break

        start = m.end()
        if i + 1 < len(matches):
            end = matches[i + 1].start()
        else:
            end_marker = template.find("## 注意事项", start)
            end = end_marker if end_marker > 0 else len(template)

        content = template[start:end].strip()
        content = re.sub(r"^---\s*", "", content)
        content = re.sub(r"\s*---\s*$", "", content)
        sections[short_name] = content

    return sections


def compute_scaling_factor(section: str, profile: dict) -> float:
    """Estimate workload scaling based on paper characteristics."""
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

    # Table guidance (H4 removed — tables are selectively extracted)
    if "实验与归因" in sections:
        lines.append("- 围绕核心表格展开归因分析，引用数据必须来自 notes KEY_FINDINGS 段或原文")
        lines.append("- 实验表格只保留核心行（支撑主要结论的对比行），不要求完整复制")
        lines.append("- 表格数字必须可追溯到原文，禁止编造（H8）")

    # H5: TL;DR numbers (from schema: frontmatter.tldr.min_numbers)
    if "核心速览" in sections:
        min_nums = FRONTMATTER_FIELDS["tldr"].min_numbers
        lines.append(f"- TL;DR（YAML frontmatter 的 tldr 字段）必须包含 ≥{min_nums} 个具体量化数字，如 \"MATH 96.2%\"（H5）")

    # H6: heading levels (from schema: body.heading_levels)
    lines.append(f"- 主标题 {'#' * HEADING_SECTION_LEVEL}（h{HEADING_SECTION_LEVEL}），"
                 f"子标题 {'#' * HEADING_SUBSECTION_LEVEL}（h{HEADING_SUBSECTION_LEVEL}），"
                 f"禁止 h1/h2/h3（H6）。代码块内 # 注释不受限制")

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

    # Suggested targets
    lines.append("\n**建议目标：**")
    for sec in sections:
        floor = CHAR_FLOORS.get(sec, 300)
        suggested = int(floor * compute_scaling_factor(sec, profile))
        if suggested > floor * 1.5:
            lines.append(f"- 「{sec}」建议 ~{suggested:,} 字符")

    return "\n".join(lines)


def _section_content_markers(sections: list[str]) -> list[str]:
    """Return H9 content marker constraints relevant to given sections."""
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
    file_info: dict | None = None,
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

    # 6b. Read strategy — generate exact Read commands
    if file_info:
        parts.append("## 读取策略（严格执行，禁止修改）")
        parts.append("")
        chunk = 2000
        for label, fpath_suffix, total in [
            ("notes.md", "notes.md", file_info.get("notes_lines", 0)),
            ("text.txt", "text.txt", file_info.get("text_lines", 0)),
        ]:
            if total <= 0:
                continue
            fpath = f"{run_dir}/{fpath_suffix}"
            if total <= chunk:
                parts.append(f'- `Read(file_path="{fpath}")`')
            else:
                n = max(1, -(-total // chunk))
                for i in range(n):
                    offset = i * chunk
                    limit = min(chunk, total - offset)
                    parts.append(f'- `Read(file_path="{fpath}", offset={offset}, limit={limit})`')
        parts.append("")
        parts.append("按以上顺序逐条执行，禁止拆分、合并或跳过。读完所有内容后再开始写作。")
        parts.append("")

    # 7. Output
    output_file = f"{run_dir}/part_{task.name.replace('writer-', '')}.md"
    parts.append("## 输出")
    parts.append(f"写入文件: `{output_file}`")
    parts.append("写完后对照上方「质量合同」逐项自检，不达标立即补充。")

    return "\n".join(parts)


def auto_split(profile: dict) -> list[WriterTask]:
    """Split sections across 3 Writers with a fixed assignment.

    In v2 we use a fixed 3-writer layout regardless of paper length:
    - writer-overview: 核心速览 + 机制迁移 (both need global view)
    - writer-principle: 第一性原理分析 (independent causal reasoning)
    - writer-technical: 技术精要 (method + experiment + critique merged)

    Long papers grow tables (not prose), so 3 writers is enough for any
    paper length. The ``profile`` arg is retained for interface stability.
    """
    _ = profile  # interface compatibility; length no longer affects split
    tasks: list[WriterTask] = []
    for name, sections, needs_pdf in WRITER_ASSIGNMENTS:
        tasks.append(WriterTask(
            name=name,
            sections=sections,
            needs_pdf_pages=needs_pdf,
        ))
    return tasks
