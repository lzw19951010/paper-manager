"""H9 ContentMarkers — verify DEFAULT_TEMPLATE's content requirements are met."""
from __future__ import annotations

import re

CONTENT_MARKERS: dict[str, list[dict]] = {
    "核心速览": [
        # TL;DR must contain at least one number
        {"marker": "tldr_with_numbers", "check": "contains_pattern",
         "pattern": r"TL;DR.*?\d+(?:\.\d+)?"},
        # Mechanism one-liner with [动作] + [对象] format
        {"marker": "mechanism_one_line", "check": "contains_pattern",
         "pattern": r"\[.+?\].*?\+.*?\[.+?\]"},
        # Key numbers table header (standardized columns)
        {"marker": "key_numbers_table", "check": "contains_pattern",
         "pattern": r"\|\s*指标\s*\|\s*数值\s*\|\s*基线\s*\|\s*基线值\s*\|\s*增益\s*\|"},
    ],
    "第一性原理分析": [
        # Numbered causal chain with [C1] prefix + Because/Therefore
        {"marker": "numbered_causal_chain", "check": "contains_pattern",
         "pattern": r"\[C\d+\].*?(?:Because|因为).*?(?:→|Therefore|所以|因此)"},
    ],
    "技术精要": [
        # Flowchart: at least 3 arrow steps
        {"marker": "method_flowchart", "check": "contains_pattern",
         "pattern": r"(?:→.*?){3,}"},
        # Design decisions table header
        {"marker": "design_decisions_table", "check": "contains_pattern",
         "pattern": r"\|\s*决策\s*\|\s*备选方案\s*\|\s*选择理由\s*\|\s*证据来源\s*\|"},
        # Ablation ranking table header
        {"marker": "ablation_ranking_table", "check": "contains_pattern",
         "pattern": r"\|\s*排名\s*\|\s*组件\s*\|\s*增益\s*\|\s*数据来源\s*\|"},
        # Confusion pairs: ❌ and ✅
        {"marker": "confusion_pairs", "check": "contains_pattern",
         "pattern": r"❌.*?✅|✅.*?❌"},
        # Hidden costs table header
        {"marker": "hidden_costs_table", "check": "contains_pattern",
         "pattern": r"\|\s*成本项\s*\|\s*量化数据\s*\|\s*对决策的影响\s*\|"},
    ],
    "机制迁移": [
        # Mechanism decomposition table header
        {"marker": "mechanism_table", "check": "contains_pattern",
         "pattern": r"\|\s*原语名称\s*\|\s*本文用途\s*\|\s*抽象描述\s*\|"},
        # Ancestors list
        {"marker": "ancestors", "check": "contains_pattern",
         "pattern": r"(?:前身|Ancestors)"},
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
