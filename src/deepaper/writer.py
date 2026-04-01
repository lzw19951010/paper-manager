"""Markdown note writer with Obsidian-compatible YAML frontmatter."""
from __future__ import annotations

import re
from pathlib import Path

import yaml


def sanitize_filename(title: str, arxiv_id: str = "") -> str:
    """Convert a paper title into a safe, readable filename stem.

    Args:
        title: Paper title to sanitize.
        arxiv_id: Fallback ID if sanitization yields an empty string.

    Returns:
        A lowercase, hyphen-separated filename stem (no extension).
    """
    result = title.lower()

    # Replace spaces with hyphens
    result = result.replace(" ", "-")

    # Remove only filesystem-unsafe chars: / \ : * ? " < > |
    result = re.sub(r'[/\\:*?"<>|]', "", result)

    # Remove leading/trailing hyphens and whitespace
    result = result.strip("-").strip()

    # Truncate to 80 characters at a word boundary
    if len(result) > 80:
        truncated = result[:80]
        # Find last hyphen to avoid cutting mid-word
        last_hyphen = truncated.rfind("-")
        if last_hyphen > 0:
            truncated = truncated[:last_hyphen]
        result = truncated.strip("-")

    if not result:
        return arxiv_id

    return result


def find_existing(arxiv_id: str, papers_dir: Path) -> Path | None:
    """Find an existing note file with a matching arxiv_id in its frontmatter.

    Args:
        arxiv_id: The arxiv ID to search for.
        papers_dir: Root directory to search recursively.

    Returns:
        Path to the matching file, or None if not found.
    """
    for md_file in papers_dir.rglob("*.md"):
        try:
            content = md_file.read_text(encoding="utf-8")
        except OSError:
            continue

        # Extract YAML frontmatter between first --- and second ---
        if not content.startswith("---"):
            continue

        end_idx = content.find("---", 3)
        if end_idx == -1:
            continue

        frontmatter_text = content[3:end_idx]
        try:
            fm = yaml.safe_load(frontmatter_text)
        except yaml.YAMLError:
            continue

        if isinstance(fm, dict) and str(fm.get("arxiv_id", "")) == arxiv_id:
            return md_file

    return None


def update_frontmatter(md_path: Path, new_frontmatter: dict) -> None:
    """Replace the YAML frontmatter of a markdown file, preserving the body.

    Args:
        md_path: Path to the markdown file to update.
        new_frontmatter: New frontmatter dict to serialize and write.
    """
    content = md_path.read_text(encoding="utf-8")

    new_yaml = yaml.dump(
        new_frontmatter, default_flow_style=False, allow_unicode=True
    )
    new_block = f"---\n{new_yaml}---"

    if content.startswith("---"):
        end_idx = content.find("---", 3)
        if end_idx != -1:
            # Preserve everything after the closing ---
            body = content[end_idx + 3:]
            result = new_block + body
        else:
            # Malformed: no closing ---, prepend new block
            result = new_block + "\n\n" + content
    else:
        # No frontmatter: prepend
        result = new_block + "\n\n" + content

    md_path.write_text(result, encoding="utf-8")


def write_paper_note(
    analysis_fm: dict,
    analysis_body: str,
    metadata: dict,
    tags: list[str],
    output_dir: Path,
    force: bool = False,
    category: str = "misc",
    quality: str = "full",
    failed_gates: list[str] | None = None,
    pipeline_version: int = 1,
) -> Path:
    """Write a paper analysis as an Obsidian-compatible markdown note.

    Args:
        analysis_fm: Frontmatter dict extracted from Claude's analysis
                     (venue, keywords, etc.). May be empty if parsing failed.
        analysis_body: Markdown body from Claude's analysis (the actual content).
        metadata: Paper metadata dict (title, authors, date, arxiv_id, url).
        tags: List of tag strings for the frontmatter.
        output_dir: Root directory for paper notes (category subdirs are created here).
        force: If True, overwrite an existing note for the same arxiv_id.
        category: Category path like "llm/pretraining" or "misc".

    Returns:
        Path to the written markdown file.

    Raises:
        FileExistsError: If a note for this arxiv_id already exists and force=False.
    """
    sanitized = sanitize_filename(metadata["title"], metadata["arxiv_id"])
    dest = output_dir / category / f"{sanitized}.md"

    existing = find_existing(metadata["arxiv_id"], output_dir)

    if existing is not None:
        if not force:
            raise FileExistsError(
                f"A note for arxiv_id {metadata['arxiv_id']!r} already exists: {existing}"
            )

    frontmatter: dict = {
        # --- Bibliographic metadata (from arxiv API) ---
        "title": metadata["title"],
        "authors": metadata["authors"],
        "date": metadata["date"],
        "arxiv_id": metadata["arxiv_id"],
        "url": metadata["url"],
        "abstract": metadata.get("abstract", ""),
        "arxiv_categories": metadata.get("categories", []),
        # --- Extracted by Claude analysis (from YAML frontmatter) ---
        "venue": analysis_fm.get("venue"),
        "publication_type": analysis_fm.get("publication_type", "preprint"),
        "doi": analysis_fm.get("doi"),
        "keywords": analysis_fm.get("keywords", []),
        "tldr": analysis_fm.get("tldr", ""),
        "core_contribution": analysis_fm.get("core_contribution", ""),
        "baselines": analysis_fm.get("baselines", []),
        "datasets": analysis_fm.get("datasets", []),
        "metrics": analysis_fm.get("metrics", []),
        "code_url": analysis_fm.get("code_url"),
        # --- Generated by pipeline ---
        "tags": tags,
        "category": category,
        # --- Pipeline quality metadata ---
        "quality": quality,
        "failed_gates": failed_gates or [],
        "pipeline_version": pipeline_version,
    }

    yaml_content = yaml.dump(
        frontmatter, default_flow_style=False, allow_unicode=True
    )
    full_content = f"---\n{yaml_content}---\n\n{analysis_body}\n"

    if existing is not None and force:
        # Remove old file (may be in a different directory/category)
        existing.unlink(missing_ok=True)

    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(full_content, encoding="utf-8")
    return dest
