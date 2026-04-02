"""H9 ContentMarkers — verify DEFAULT_TEMPLATE's content requirements are met."""
from __future__ import annotations

import re

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
        {"marker": "流程图", "check": "contains_pattern", "pattern": r"(?:→.*){2,}"},
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
