"""Paper analysis using Claude Code CLI (uses Max subscription, not API billing)."""
from __future__ import annotations

import json
import logging
import re
import subprocess
from pathlib import Path

import pdfplumber
import pypdfium2 as pdfium

logger = logging.getLogger(__name__)


def get_page_count(pdf_path: Path) -> int:
    """Return the number of pages in a PDF file."""
    with pdfplumber.open(pdf_path) as pdf:
        return len(pdf.pages)


def get_file_size_mb(pdf_path: Path) -> float:
    """Return file size in megabytes."""
    return pdf_path.stat().st_size / (1024 * 1024)


def extract_text(pdf_path: Path) -> str:
    """Extract all text from a PDF using pdfplumber."""
    with pdfplumber.open(pdf_path) as pdf:
        pages_text = [page.extract_text() or "" for page in pdf.pages]
    return "\n\n".join(pages_text)


def extract_page_images(pdf_path: Path, pages: list[int], output_dir: Path) -> list[Path]:
    """Render specific PDF pages as PNG images.

    Args:
        pdf_path: Path to the PDF file.
        pages: 0-indexed page numbers to render.
        output_dir: Directory to save the PNG files.

    Returns:
        List of paths to saved PNG files.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    pdf = pdfium.PdfDocument(str(pdf_path))
    total = len(pdf)
    paths = []
    for page_idx in pages:
        if page_idx >= total:
            continue
        page = pdf[page_idx]
        bitmap = page.render(scale=1.5)
        img = bitmap.to_pil()
        dest = output_dir / f"page_{page_idx + 1}.jpg"
        img.save(str(dest), "JPEG", quality=75)
        paths.append(dest)
    return paths


def _detect_figure_pages(pdf_path: Path, max_pages: int = 20) -> list[int]:
    """Detect pages containing figures/tables and rank by importance.

    Uses three signals:
    1. Bitmap images: pages where embedded image objects cover >= 10% of page area.
    2. Vector figures: pages with graphic objects + figure/table caption.
    3. Position weight: earlier pages (main body) scored higher than later pages
       (appendix), since core figures tend to appear in the first ~60% of the paper.

    Returns 0-indexed page numbers, capped at max_pages.
    """
    scored: dict[int, float] = {}
    with pdfplumber.open(pdf_path) as pdf:
        total_pages = len(pdf.pages)
        for i, page in enumerate(pdf.pages):
            text = page.extract_text() or ""
            page_area = float(page.width) * float(page.height)
            score = 0.0

            # Signal 1: embedded bitmap images
            imgs = page.images
            if imgs:
                img_area = sum(
                    abs((im["x1"] - im["x0"]) * (im["y1"] - im["y0"]))
                    for im in imgs
                )
                ratio = img_area / page_area if page_area > 0 else 0
                if ratio >= 0.10:
                    score += ratio

            # Signal 2: vector graphics + caption
            n_gfx = len(page.rects) + len(page.lines) + len(page.curves)
            has_caption = bool(
                re.search(r"(?:Figure|Fig\.|Table)\s*\d+", text)
            )
            if n_gfx >= 20 and has_caption:
                score += 0.3
            elif n_gfx >= 100:
                score += 0.2

            if score > 0:
                # Signal 3: position weight — front 60% of paper gets bonus
                position = i / total_pages if total_pages > 0 else 0
                if position <= 0.6:
                    score += 0.15  # main body bonus
                scored[i] = score

    # Sort by score descending, return top pages
    top = sorted(scored, key=lambda p: scored[p], reverse=True)[:max_pages]
    return sorted(top)


def _call_claude(prompt: str, show_progress: bool = True) -> str:
    """Call Claude Code CLI with real-time streaming progress display.

    Uses stream-json format to show token count and elapsed time while
    Claude is generating, then returns the full text result.
    """
    import sys
    import time as _time

    proc = subprocess.Popen(
        ["claude", "-p", "-", "--output-format", "stream-json", "--verbose"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
    )

    # Send prompt and close stdin
    proc.stdin.write(prompt)
    proc.stdin.close()

    result_text = ""
    output_tokens = 0
    start = _time.monotonic()

    for line in proc.stdout:
        line = line.strip()
        if not line:
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue

        etype = event.get("type", "")

        if etype == "assistant":
            # Extract text content and token count from assistant message
            msg = event.get("message", {})
            usage = msg.get("usage", {})
            output_tokens = usage.get("output_tokens", output_tokens)
            content = msg.get("content", [])
            for block in content:
                if isinstance(block, dict) and block.get("type") == "text":
                    result_text = block.get("text", "")
            if show_progress:
                elapsed = _time.monotonic() - start
                sys.stderr.write(f"\r    Generating... {output_tokens} tokens, {elapsed:.0f}s")
                sys.stderr.flush()

        elif etype == "result":
            # Final result — extract text
            final_text = event.get("result", "")
            if final_text:
                result_text = final_text
            usage = event.get("usage", {})
            output_tokens = usage.get("output_tokens", output_tokens)
            if show_progress:
                elapsed = _time.monotonic() - start
                sys.stderr.write(f"\r    Done: {output_tokens} tokens in {elapsed:.0f}s          \n")
                sys.stderr.flush()

    proc.wait(timeout=30)
    if proc.returncode != 0:
        stderr_text = proc.stderr.read() if proc.stderr else ""
        raise RuntimeError(f"Claude CLI error (rc={proc.returncode}): {stderr_text.strip()}")

    return result_text.strip()


def _fix_json_string_escapes(s: str) -> str:
    """Escape control characters that appear inside JSON string values only.

    Walks the JSON character-by-character tracking whether we're inside a
    string, so structural whitespace (newlines between keys) is preserved
    while unescaped newlines/tabs *within* values are fixed.
    """
    result = []
    in_string = False
    i = 0
    while i < len(s):
        c = s[i]
        if c == "\\" and in_string:
            # Pass through existing escape sequence verbatim
            result.append(c)
            i += 1
            if i < len(s):
                result.append(s[i])
                i += 1
            continue
        if c == '"':
            in_string = not in_string
        if in_string and c == "\n":
            result.append("\\n")
        elif in_string and c == "\r":
            result.append("\\r")
        elif in_string and c == "\t":
            result.append("\\t")
        else:
            result.append(c)
        i += 1
    return "".join(result)


def _extract_json(text: str) -> dict:
    """Extract a JSON object from Claude's response text, with robust fallback."""
    # Try to find JSON in a code block first (handles optional language tag and
    # varying amounts of surrounding whitespace)
    match = re.search(r"```(?:json)?\s*\n?(\{.*?\})\s*\n?```", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1))
        except json.JSONDecodeError:
            try:
                return json.loads(_fix_json_string_escapes(match.group(1)))
            except json.JSONDecodeError:
                pass

    # Try to find the outermost JSON object by matching braces
    start = text.find("{")
    if start == -1:
        raise ValueError("No JSON object found in response")

    depth = 0
    end = start
    for i in range(start, len(text)):
        if text[i] == "{":
            depth += 1
        elif text[i] == "}":
            depth -= 1
            if depth == 0:
                end = i + 1
                break

    candidate = text[start:end]
    try:
        return json.loads(candidate)
    except json.JSONDecodeError:
        pass

    # Last resort: fix unescaped control chars inside string values only
    fixed = _fix_json_string_escapes(candidate)
    try:
        return json.loads(fixed)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Could not parse JSON from response: {exc}") from exc


ANALYSIS_JSON_SCHEMA = """\
请输出一个 JSON 对象（不要 markdown 代码块，不要多余解释），包含以下字段。
结构化元数据字段为简短值，分析字段为完整的 Markdown 文本（可包含子标题、表格、代码块等富格式）。

{
  "venue": "发表场所 (如 NeurIPS 2023)，未找到则为 null",
  "publication_type": "论文类型: conference/journal/preprint/workshop/thesis 之一",
  "doi": "DOI 标识符（如 10.xxxx/yyyy），从论文中提取，未找到则为 null",
  "keywords": ["关键词1", "关键词2", "...5-10个技术关键词"],
  "tldr": "一句话总结论文核心贡献（≤100字，纯文本）",
  "core_contribution": "核心贡献类型: new-method/new-dataset/new-benchmark/new-framework/survey/empirical-study/theoretical 之一或组合",
  "baselines": ["对比的主要baseline方法名称列表"],
  "datasets": ["使用的数据集名称列表"],
  "metrics": ["使用的评估指标列表，如 BLEU, Recall@20, NDCG@10"],
  "code_url": "官方代码仓库 URL，从论文中提取，未找到则为 null",
  "executive_summary": "核心速览的完整 Markdown 文本（含 TL;DR、一图流、核心机制一句话）",
  "motivation": "动机与第一性原理的完整 Markdown 文本（含痛点、核心洞察、直觉解释）",
  "methodology": "方法详解的完整 Markdown 文本（含直觉版、精确版、设计决策、易混淆点）",
  "experiments": "实验与归因的完整 Markdown 文本（含核心收益、归因分析、可信度检查）",
  "critical_review": "专家批判的完整 Markdown 文本（含隐性成本、工程落地建议、关联思考）",
  "mechanism_transfer": "机制迁移分析的完整 Markdown 文本（含机制解耦、迁移处方、机制家族图谱）",
  "background_context": "背景知识补充的 Markdown 文本，如不需要则为 null"
}"""


def analyze_paper(pdf_path: Path, prompt: str, config) -> dict:
    """Analyze a paper using Claude Code CLI with text + figure images.

    1. Extracts full text from the PDF.
    2. Detects and renders key figure pages as images.
    3. Sends text + image file paths to Claude Code for analysis.

    Args:
        pdf_path: Path to the PDF file.
        prompt: Rendered prompt string (template + metadata header).
        config: Config object (kept for interface compatibility).

    Returns:
        Dict with extracted paper analysis fields.
    """
    text = extract_text(pdf_path)
    if not text.strip():
        raise RuntimeError(f"Could not extract text from {pdf_path.name}")

    # Truncate very long papers to avoid CLI limits
    max_chars = 80000
    if len(text) > max_chars:
        text = text[:max_chars] + "\n\n[...truncated...]"

    # Extract key figure pages as images
    figure_dir = pdf_path.parent / f"{pdf_path.stem}_figures"
    try:
        figure_pages = _detect_figure_pages(pdf_path)
        image_paths = extract_page_images(pdf_path, figure_pages, figure_dir)
    except Exception as exc:
        logger.warning("Could not extract figure images: %s", exc)
        image_paths = []

    # Build prompt with image references
    image_section = ""
    if image_paths:
        image_refs = "\n".join(
            f"- Page {p.stem.replace('page_', '')}: {p.resolve()}"
            for p in image_paths
        )
        image_section = (
            f"\n\n---\n以下是论文关键页面的图片文件路径，请使用 Read 工具查看这些图片以分析 Figure 和 Table 的内容：\n{image_refs}\n"
        )

    full_prompt = f"{prompt}\n\n{ANALYSIS_JSON_SCHEMA}{image_section}\n\n---\nPaper text:\n{text}"
    response = _call_claude(full_prompt)

    # Clean up figure images after analysis
    if figure_dir.exists():
        import shutil
        shutil.rmtree(figure_dir, ignore_errors=True)

    return _extract_json(response)


def classify_paper(analysis: dict, config) -> str:
    """Classify a paper into a category using Claude Code CLI.

    Reads the categories definition from templates/categories.md, then asks
    Claude to classify the paper based on its executive_summary and keywords.

    Args:
        analysis: Analysis result dict (must contain executive_summary, keywords).
        config: Config object (used to locate templates_path).

    Returns:
        Category string like "llm/pretraining" or "recsys/llm-as-rec".
        Falls back to "misc" if classification fails.
    """
    try:
        categories_path = config.templates_path / "categories.md"
        categories_text = categories_path.read_text(encoding="utf-8")
    except OSError as exc:
        logger.warning("Could not read categories.md: %s", exc)
        return "misc"

    keywords = analysis.get("keywords", [])
    keywords_str = ", ".join(keywords) if isinstance(keywords, list) else str(keywords)

    summary_text = analysis.get("executive_summary", "")
    if not summary_text:
        summary_text = f"{analysis.get('research_question', '')} {analysis.get('method', '')}"

    summary = f"{summary_text} {keywords_str}".strip()

    prompt = (
        f"Based on the paper summary and the category definitions below, classify this paper.\n\n"
        f"Paper summary and keywords:\n{summary}\n\n"
        f"Category definitions:\n{categories_text}\n\n"
        f'Respond with ONLY a JSON object: {{"category": "llm/pretraining"}} '
        f"where the value is the category path relative to papers/. "
        f"Valid top-level categories: llm, recsys, multimodal, misc. "
        f"Use misc if unsure."
    )

    try:
        response = _call_claude(prompt)
        result = _extract_json(response)
        category = result.get("category", "misc")
        if not isinstance(category, str) or not category.strip():
            return "misc"
        return category.strip()
    except Exception as exc:
        logger.warning("Paper classification failed: %s", exc)
        return "misc"


def generate_tags(analysis: dict, config) -> list[str]:
    """Generate classification tags for a paper using Claude Code CLI."""
    keywords = analysis.get("keywords", [])
    keywords_str = ", ".join(keywords) if isinstance(keywords, list) else str(keywords)

    # Use executive_summary if available, fall back to old fields
    summary_text = analysis.get("executive_summary", "")
    if not summary_text:
        summary_text = f"{analysis.get('research_question', '')} {analysis.get('method', '')}"

    summary = f"{summary_text} {keywords_str}".strip()

    prompt = (
        f"Generate 3-8 classification tags for this academic paper.\n\n"
        f"Paper summary: {summary}\n\n"
        f"Respond with ONLY a JSON object: {{\"tags\": [\"tag1\", \"tag2\", ...]}}"
    )

    response = _call_claude(prompt)
    result = _extract_json(response)
    return result.get("tags", [])
