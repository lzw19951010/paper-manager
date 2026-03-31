"""Command-line interface for deepaper.

Lightweight paper knowledge base for Claude Code.
Analysis is done via /deepaper slash command in Claude Code.
CLI provides I/O utilities: download, save, cite, sync.
"""
from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Optional

import typer

app = typer.Typer(
    name="deepaper",
    help="Paper knowledge base for Claude Code. Use /deepaper in Claude Code to analyze papers.",
    add_completion=False,
)


def _auto_install_slash_command() -> None:
    """Auto-install slash command to ~/.claude/commands/ if not present."""
    cmd_path = Path.home() / ".claude" / "commands" / "deepaper.md"
    if not cmd_path.exists():
        cmd_path.parent.mkdir(parents=True, exist_ok=True)
        from deepaper.defaults import get_default_slash_command
        cmd_path.write_text(get_default_slash_command(), encoding="utf-8")


# Auto-install on first import (i.e., first `deepaper` command)
try:
    _auto_install_slash_command()
except Exception:
    pass  # silently skip if home dir is read-only etc.


# ---------------------------------------------------------------------------
# install
# ---------------------------------------------------------------------------

@app.command()
def install() -> None:
    """Install /deepaper slash command to Claude Code (global).

    Copies the slash command to ~/.claude/commands/ so /deepaper works
    in any project.
    """
    home_claude = Path.home() / ".claude" / "commands"
    home_claude.mkdir(parents=True, exist_ok=True)

    cmd_dest = home_claude / "deepaper.md"
    from deepaper.defaults import get_default_slash_command
    cmd_dest.write_text(get_default_slash_command(), encoding="utf-8")

    typer.echo(f"Installed /deepaper to {cmd_dest}")
    typer.echo("Now use /deepaper <arxiv-url> in Claude Code from any directory.")


# ---------------------------------------------------------------------------
# init
# ---------------------------------------------------------------------------

@app.command()
def init(
    git_remote: str = typer.Option("", "--git-remote", help="Git remote URL for syncing."),
) -> None:
    """Initialize a deepaper project in the current directory."""
    root = Path.cwd()

    # config.yaml
    config_path = root / "config.yaml"
    if config_path.exists():
        typer.echo("config.yaml already exists — skipping.")
    else:
        from deepaper.defaults import DEFAULT_CONFIG_YAML
        config_path.write_text(DEFAULT_CONFIG_YAML, encoding="utf-8")
        typer.echo("Created config.yaml.")

    # papers/
    (root / "papers").mkdir(exist_ok=True)
    typer.echo("papers/ directory ready.")

    # .obsidian/app.json
    obsidian_dir = root / ".obsidian"
    obsidian_dir.mkdir(exist_ok=True)
    app_json = obsidian_dir / "app.json"
    if not app_json.exists():
        app_json.write_text(
            json.dumps({"userIgnoreFilters": ["tmp/", ".chromadb/"]}, indent=2),
            encoding="utf-8",
        )

    # .claude/commands/deepaper.md (project-level)
    claude_dir = root / ".claude" / "commands"
    claude_dir.mkdir(parents=True, exist_ok=True)
    cmd_path = claude_dir / "deepaper.md"
    if not cmd_path.exists():
        from deepaper.defaults import get_default_slash_command
        cmd_path.write_text(get_default_slash_command(), encoding="utf-8")
        typer.echo("Created .claude/commands/deepaper.md")
    else:
        typer.echo(".claude/commands/deepaper.md already exists — skipping.")

    # Git
    if git_remote:
        from deepaper.sync import init_repo
        init_repo(root, git_remote)
        typer.echo(f"Git initialized with remote: {git_remote}")
    elif not (root / ".git").exists():
        typer.echo("Tip: deepaper init --git-remote <url> to enable sync.")

    typer.echo("\nDone. Use /deepaper <arxiv-url> in Claude Code.")


# ---------------------------------------------------------------------------
# download
# ---------------------------------------------------------------------------

@app.command()
def download(
    url: str = typer.Argument(..., help="arxiv URL or ID to download."),
) -> None:
    """Download a paper PDF and output metadata + file path as JSON.

    Claude Code reads the PDF directly via its native Read tool.
    """
    from deepaper.downloader import parse_arxiv_id, fetch_metadata, download_pdf

    root = Path.cwd()
    tmp_dir = root / "tmp"
    tmp_dir.mkdir(exist_ok=True)

    try:
        arxiv_id = parse_arxiv_id(url)
    except ValueError as exc:
        typer.echo(json.dumps({"error": str(exc)}))
        raise typer.Exit(1)

    metadata = fetch_metadata(arxiv_id)

    pdf_path = tmp_dir / f"{arxiv_id}.pdf"
    if not (pdf_path.exists() and pdf_path.stat().st_size > 0):
        pdf_path = download_pdf(arxiv_id, tmp_dir)

    size_mb = pdf_path.stat().st_size / (1024 * 1024)

    typer.echo(json.dumps({
        "arxiv_id": arxiv_id,
        "title": metadata["title"],
        "authors": metadata["authors"],
        "date": metadata["date"],
        "abstract": metadata.get("abstract", ""),
        "categories": metadata.get("categories", []),
        "url": metadata["url"],
        "pdf_path": str(pdf_path.resolve()),
        "size_mb": round(size_mb, 1),
    }, ensure_ascii=False, indent=2))


# ---------------------------------------------------------------------------
# save
# ---------------------------------------------------------------------------

@app.command()
def save(
    arxiv_id: str = typer.Argument(..., help="arxiv ID of the paper."),
    category: str = typer.Option("misc", "--category", "-c", help="Category path like llm/pretraining."),
    input_file: Optional[str] = typer.Option(None, "--input", "-i", help="Path to markdown file. Reads stdin if omitted."),
    tags: Optional[str] = typer.Option(None, "--tags", "-t", help="Comma-separated tags."),
) -> None:
    """Save an analyzed paper note to the knowledge base.

    Accepts markdown with YAML frontmatter. Merges arxiv metadata,
    writes to the category directory.
    """
    import sys
    from deepaper.downloader import parse_arxiv_id, fetch_metadata
    from deepaper.analyzer import parse_analysis_response
    from deepaper.writer import write_paper_note

    root = Path.cwd()
    papers_dir = root / "papers"
    papers_dir.mkdir(exist_ok=True)

    content = Path(input_file).read_text(encoding="utf-8") if input_file else sys.stdin.read()
    if not content.strip():
        typer.echo("Error: empty input", err=True)
        raise typer.Exit(1)

    analysis_fm, analysis_body = parse_analysis_response(content)
    real_id = parse_arxiv_id(arxiv_id)
    metadata = fetch_metadata(real_id)

    tag_list = [t.strip() for t in tags.split(",") if t.strip()] if tags else analysis_fm.get("keywords", [])

    note_path = write_paper_note(
        analysis_fm, analysis_body, metadata, tag_list,
        papers_dir, force=True, category=category,
    )

    try:
        rel_path = str(note_path.relative_to(root))
    except ValueError:
        rel_path = str(note_path)

    typer.echo(json.dumps({
        "saved": rel_path,
        "category": category,
        "tags": tag_list,
    }, ensure_ascii=False))


# ---------------------------------------------------------------------------
# sync
# ---------------------------------------------------------------------------

@app.command()
def sync(
    message: Optional[str] = typer.Option(None, "--message", "-m", help="Custom commit message."),
) -> None:
    """Sync papers to git: pull --rebase, commit, and push."""
    root = Path.cwd()
    if not (root / ".git").exists():
        typer.echo("No git repo. Run: deepaper init --git-remote <url>", err=True)
        raise typer.Exit(1)

    from deepaper.sync import sync_to_git
    typer.echo("Syncing to git...")
    sync_to_git(root, message=message, papers_dir="papers")
    typer.echo("Sync complete.")


# ---------------------------------------------------------------------------
# cite
# ---------------------------------------------------------------------------

@app.command()
def cite(
    arxiv_id_or_url: str = typer.Argument(..., help="arxiv URL or ID."),
    update: bool = typer.Option(False, "--update", "-u", help="Update existing note."),
) -> None:
    """Look up citing papers and optionally update an existing note."""
    from deepaper.downloader import parse_arxiv_id
    from deepaper.citations import fetch_citing_papers, format_descendants_section, enrich_mechanism_transfer

    try:
        arxiv_id = parse_arxiv_id(arxiv_id_or_url)
    except ValueError as exc:
        typer.echo(f"Error: {exc}", err=True)
        raise typer.Exit(1)

    typer.echo(f"Fetching citations for: {arxiv_id}")
    citation_data = fetch_citing_papers(arxiv_id)
    total_cites = citation_data.get("total_citations", 0)
    typer.echo(f"Citations: {total_cites:,} total")

    if update:
        from deepaper.writer import find_existing, update_frontmatter
        import re as _re
        import yaml

        root = Path.cwd()
        papers_dir = root / "papers"

        existing = find_existing(arxiv_id, papers_dir)
        if existing is None:
            typer.echo(f"No note found for {arxiv_id}", err=True)
            raise typer.Exit(1)

        content = existing.read_text(encoding="utf-8")
        # Parse frontmatter
        fm_match = _re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)", content, _re.DOTALL)
        if fm_match:
            fm = yaml.safe_load(fm_match.group(1)) or {}
            body = fm_match.group(2)
        else:
            fm, body = {}, content

        # Inject citation data
        mt_pattern = _re.compile(r"(## 机制迁移分析[^\n]*\n\n)(.*?)(?=\n---\n|\n## |\Z)", _re.DOTALL)
        m = mt_pattern.search(body)
        if m:
            body = body[:m.start(2)] + enrich_mechanism_transfer(m.group(2), citation_data) + body[m.end(2):]
        else:
            body = body.rstrip("\n") + "\n\n" + format_descendants_section(citation_data)

        fm["citation_count"] = total_cites
        fm["citation_date"] = citation_data.get("fetch_date", "")

        new_yaml = yaml.dump(fm, default_flow_style=False, allow_unicode=True)
        existing.write_text(f"---\n{new_yaml}---\n{body}", encoding="utf-8")
        typer.echo(f"Updated: {existing}")
    else:
        typer.echo("")
        typer.echo(format_descendants_section(citation_data))
