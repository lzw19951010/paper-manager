"""Prompt generation: template parsing, auto-split, gate contract injection."""
from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path

from deepaper.gates import CHAR_FLOORS

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
        if "venue:" in block and "baselines:" in block:
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


def auto_split(profile: dict) -> list[WriterTask]:
    """Split sections across Writers: visual fixed, text by workload."""
    text_sections = [s for s in SECTION_ORDER if s not in VISUAL_SECTIONS]

    workloads = {
        s: CHAR_FLOORS.get(s, 500) * compute_scaling_factor(s, profile)
        for s in text_sections
    }

    visual_workload = sum(
        CHAR_FLOORS.get(s, 1000) * compute_scaling_factor(s, profile)
        for s in VISUAL_SECTIONS
    )

    total_text = sum(workloads.values())
    # Use 2 text writers when text workload is substantial relative to
    # the average section floor, regardless of visual workload size.
    avg_floor = sum(CHAR_FLOORS.get(s, 500) for s in text_sections) / len(text_sections)
    if total_text < avg_floor * len(text_sections) * 1.5:
        n_text = 1
    else:
        n_text = 2
    n_text = min(n_text, len(text_sections))

    sorted_sections = sorted(text_sections, key=lambda s: workloads[s], reverse=True)
    bins: list[list[str]] = [[] for _ in range(n_text)]
    bin_loads = [0.0] * n_text

    for sec in sorted_sections:
        lightest = min(range(n_text), key=lambda i: bin_loads[i])
        bins[lightest].append(sec)
        bin_loads[lightest] += workloads[sec]

    for b in bins:
        b.sort(key=lambda s: SECTION_ORDER.index(s))

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
