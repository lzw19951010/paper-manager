"""Command-line interface for paper-manager."""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Optional

import typer

app = typer.Typer(
    name="paper-manager",
    help="Personal academic paper manager with Claude AI analysis.",
    add_completion=False,
)


# ---------------------------------------------------------------------------
# init
# ---------------------------------------------------------------------------

@app.command()
def init(
    git_remote: str = typer.Option("", "--git-remote", help="Git remote URL for syncing."),
) -> None:
    """Initialize the paper-manager project in the current directory."""
    root = Path.cwd()

    # 1. Create config.yaml from example (idempotent)
    config_path = root / "config.yaml"
    example_path = root / "config.yaml.example"

    if config_path.exists():
        typer.echo("config.yaml already exists — skipping.")
    elif example_path.exists():
        import shutil
        shutil.copy(example_path, config_path)
        typer.echo("Created config.yaml from example. Edit it to add your API key.")
    else:
        typer.echo(
            "Warning: config.yaml.example not found. Create config.yaml manually.",
            err=True,
        )

    # 2. Create papers/ directory
    papers_dir = root / "papers"
    papers_dir.mkdir(exist_ok=True)
    typer.echo("papers/ directory ready.")

    # 3. Create .obsidian/app.json to exclude non-vault dirs (idempotent)
    obsidian_dir = root / ".obsidian"
    obsidian_dir.mkdir(exist_ok=True)
    app_json_path = obsidian_dir / "app.json"

    if not app_json_path.exists():
        obsidian_config = {
            "userIgnoreFilters": ["src/", "tests/", "tmp/", ".chromadb/"]
        }
        app_json_path.write_text(
            json.dumps(obsidian_config, indent=2), encoding="utf-8"
        )
        typer.echo("Created .obsidian/app.json with exclusion filters.")
    else:
        typer.echo(".obsidian/app.json already exists — skipping.")

    # 4. Init git repo
    if git_remote:
        from paper_manager.sync import init_repo
        init_repo(root, git_remote)
        typer.echo(f"Git repo initialized with remote: {git_remote}")
    elif not (root / ".git").exists():
        typer.echo(
            "Tip: run `paper-manager init --git-remote <url>` to enable git sync."
        )

    typer.echo("\nDone. Run `paper-manager add <arxiv-url>` to add your first paper.")


# ---------------------------------------------------------------------------
# add
# ---------------------------------------------------------------------------

@app.command()
def add(
    urls: list[str] = typer.Argument(..., help="One or more arxiv URLs or IDs to process."),
    force: bool = typer.Option(False, "--force", "-f", help="Re-process existing papers."),
) -> None:
    """Download and analyze one or more arxiv papers."""
    from paper_manager.config import load_config
    from paper_manager.downloader import parse_arxiv_id, fetch_metadata, download_pdf
    from paper_manager.templates import load_template, render_prompt
    from paper_manager.analyzer import analyze_paper, generate_tags, classify_paper
    from paper_manager.writer import find_existing, write_paper_note
    from paper_manager.search import get_collection, index_paper

    root = Path.cwd()
    config = load_config(root)

    for url in urls:
        typer.echo(f"\nProcessing: {url}")

        # Parse arxiv ID
        try:
            arxiv_id = parse_arxiv_id(url)
        except ValueError as exc:
            typer.echo(f"  Error: {exc}", err=True)
            continue

        typer.echo(f"  arxiv ID: {arxiv_id}")

        # Skip if already exists (unless --force)
        existing = find_existing(arxiv_id, config.papers_path)
        if existing is not None and not force:
            typer.echo(f"  Skipping — note already exists: {existing.name}")
            typer.echo("  Use --force to re-process.")
            continue

        # Fetch metadata
        typer.echo("  Fetching metadata...")
        try:
            metadata = fetch_metadata(arxiv_id)
        except Exception as exc:
            typer.echo(f"  Error fetching metadata: {exc}", err=True)
            continue

        title_display = metadata["title"]
        if len(title_display) > 60:
            title_display = title_display[:57] + "..."
        typer.echo(f"  Title: {title_display}")

        # Download PDF (skip if already cached locally)
        pdf_path = config.tmp_path / f"{arxiv_id}.pdf"
        if pdf_path.exists() and pdf_path.stat().st_size > 0:
            typer.echo(f"  PDF cached: {pdf_path.name}")
        else:
            typer.echo("  Downloading PDF...")
            try:
                pdf_path = download_pdf(arxiv_id, config.tmp_path)
            except Exception as exc:
                typer.echo(f"  Error downloading PDF: {exc}", err=True)
                continue

        # Analyze with Claude
        typer.echo(f"  Analyzing with {config.model}...")
        try:
            template = load_template(config.template, config.templates_path)
            prompt = render_prompt(template, metadata)
            analysis = analyze_paper(pdf_path, prompt, config)
        except Exception as exc:
            typer.echo(f"  Error during analysis: {exc}", err=True)
            continue

        # Generate tags
        typer.echo("  Generating tags...")
        try:
            tags = generate_tags(analysis, config)
        except Exception as exc:
            typer.echo(f"  Warning: tag generation failed: {exc}", err=True)
            tags = []

        # Classify paper into category
        typer.echo("  Classifying paper...")
        try:
            category = classify_paper(analysis, config)
        except Exception as exc:
            typer.echo(f"  Warning: classification failed: {exc}", err=True)
            category = "misc"
        typer.echo(f"  Category: {category}")

        # Write markdown note
        typer.echo("  Writing note...")
        try:
            note_path = write_paper_note(
                analysis, metadata, tags, config.papers_path, force=force, category=category
            )
        except Exception as exc:
            typer.echo(f"  Error writing note: {exc}", err=True)
            continue

        # Index in ChromaDB
        typer.echo("  Indexing in search database...")
        try:
            collection = get_collection(config.chromadb_path)
            index_paper(note_path, collection)
        except Exception as exc:
            typer.echo(f"  Warning: indexing failed: {exc}", err=True)


        try:
            rel_path = note_path.relative_to(root)
        except ValueError:
            rel_path = note_path
        typer.echo(f"  Done: {rel_path}")

    typer.echo("\nAll papers processed.")


def _cleanup_pdf(pdf_path: Path) -> None:
    """Remove a temporary PDF file, silently ignoring errors."""
    try:
        pdf_path.unlink(missing_ok=True)
    except OSError:
        pass


# ---------------------------------------------------------------------------
# sync
# ---------------------------------------------------------------------------

@app.command()
def sync(
    message: Optional[str] = typer.Option(
        None, "--message", "-m", help="Custom commit message."
    ),
) -> None:
    """Sync papers to git: pull --rebase, commit, and push."""
    import git as gitlib

    from paper_manager.config import load_config
    from paper_manager.sync import sync_to_git, get_new_files_from_pull
    from paper_manager.search import get_collection, index_paper

    root = Path.cwd()

    if not (root / ".git").exists():
        typer.echo(
            "No git repo found. Run: paper-manager init --git-remote <url>",
            err=True,
        )
        raise typer.Exit(1)

    config = load_config(root)

    # Capture HEAD SHA before pull so we can detect newly pulled files
    before_sha: Optional[str] = None
    try:
        repo = gitlib.Repo(root)
        try:
            before_sha = repo.head.commit.hexsha
        except (ValueError, TypeError):
            before_sha = None
    except gitlib.InvalidGitRepositoryError:
        typer.echo("Invalid git repository.", err=True)
        raise typer.Exit(1)

    typer.echo("Syncing to git...")
    sync_to_git(root, message=message, papers_dir=config.papers_dir)
    typer.echo("Sync complete.")

    # Reindex any new .md files that arrived via pull
    if before_sha:
        try:
            new_files = get_new_files_from_pull(repo, before_sha)
            if new_files:
                typer.echo(f"Indexing {len(new_files)} new paper(s) from pull...")
                collection = get_collection(config.chromadb_path)
                for md_path in new_files:
                    try:
                        index_paper(md_path, collection)
                        typer.echo(f"  Indexed: {md_path.name}")
                    except Exception as exc:
                        typer.echo(
                            f"  Warning: failed to index {md_path.name}: {exc}",
                            err=True,
                        )
        except Exception as exc:
            typer.echo(f"Warning: could not check for new files: {exc}", err=True)


# ---------------------------------------------------------------------------
# search
# ---------------------------------------------------------------------------

@app.command()
def search(
    query: str = typer.Argument(..., help="Natural language search query."),
    n: int = typer.Option(5, "--n", "-n", help="Number of results to return."),
) -> None:
    """Semantic search over your paper collection."""
    from paper_manager.config import load_config
    from paper_manager.search import get_collection, search_papers

    root = Path.cwd()
    config = load_config(root)

    if not config.chromadb_path.exists():
        typer.echo(
            "No search index found. Run: paper-manager reindex",
            err=True,
        )
        raise typer.Exit(1)

    collection = get_collection(config.chromadb_path)
    results = search_papers(query, collection, n_results=n)

    if not results:
        typer.echo("No matching papers found. The paper may not be indexed yet.")
        return

    typer.echo(f"\nSearch results for: {query!r}\n")
    typer.echo(f"{'#':<3}  {'Score':<7}  {'Title':<50}  Tags")
    typer.echo("-" * 90)

    for i, result in enumerate(results, 1):
        title = result["title"]
        if len(title) > 50:
            title = title[:48] + ".."
        score_str = f"{result['score']:.3f}"
        tags = (result.get("tags") or "")[:30]
        typer.echo(f"{i:<3}  {score_str:<7}  {title:<50}  {tags}")

        snippet = result.get("matched_section", "")
        if snippet:
            snippet_display = snippet[:100].replace("\n", " ")
            typer.echo(f"     → {snippet_display}")

        typer.echo(f"     arxiv: {result['arxiv_id']}")

    typer.echo()


# ---------------------------------------------------------------------------
# tag
# ---------------------------------------------------------------------------

@app.command()
def tag(
    limit: Optional[int] = typer.Option(
        None, "--limit", "-l", help="Maximum number of papers to re-tag."
    ),
    since: Optional[str] = typer.Option(
        None, "--since", "-s", help="Only re-tag papers on or after this date (YYYY-MM-DD)."
    ),
) -> None:
    """Re-generate tags for papers using Claude."""
    from paper_manager.config import load_config
    from paper_manager.analyzer import generate_tags
    from paper_manager.writer import update_frontmatter
    from paper_manager.search import parse_frontmatter

    root = Path.cwd()
    config = load_config(root)

    if not config.papers_path.exists():
        typer.echo("No papers directory found.", err=True)
        raise typer.Exit(1)

    md_files = sorted(config.papers_path.rglob("*.md"))

    # Filter by --since
    if since:
        filtered: list[Path] = []
        for md in md_files:
            try:
                content = md.read_text(encoding="utf-8")
                fm, _ = parse_frontmatter(content)
                date_val = fm.get("date", "")
                if date_val and str(date_val) >= since:
                    filtered.append(md)
            except OSError:
                continue
        md_files = filtered

    # Apply --limit
    if limit is not None:
        md_files = md_files[:limit]

    if not md_files:
        typer.echo("No papers to re-tag.")
        return

    typer.echo(f"Re-tagging {len(md_files)} paper(s)...")

    for md_path in md_files:
        try:
            content = md_path.read_text(encoding="utf-8")
        except OSError as exc:
            typer.echo(f"  Warning: cannot read {md_path.name}: {exc}", err=True)
            continue

        fm, body = parse_frontmatter(content)
        title_display = str(fm.get("title", md_path.stem))
        if len(title_display) > 50:
            title_display = title_display[:47] + "..."
        typer.echo(f"  Tagging: {title_display}")

        # Build analysis dict for tag generation from frontmatter + body sections
        analysis: dict = {
            "research_question": "",
            "method": "",
            "keywords": fm.get("keywords", []),
        }

        # Extract from new-format sections
        es_match = re.search(r"## 核心速览.*?\n(.+?)(?=\n---|\n## |\Z)", body, re.DOTALL)
        if es_match:
            analysis["research_question"] = es_match.group(1).strip()
        method_match = re.search(r"## 方法详解.*?\n(.+?)(?=\n---|\n## |\Z)", body, re.DOTALL)
        if method_match:
            analysis["method"] = method_match.group(1).strip()[:500]

        try:
            new_tags = generate_tags(analysis, config)
            fm["tags"] = new_tags
            update_frontmatter(md_path, fm)
            typer.echo(f"    Tags: {', '.join(new_tags)}")
        except Exception as exc:
            typer.echo(f"    Warning: failed to tag {md_path.name}: {exc}", err=True)

    typer.echo("Done.")


# ---------------------------------------------------------------------------
# reindex
# ---------------------------------------------------------------------------

@app.command()
def reindex() -> None:
    """Rebuild the semantic search index from all paper notes."""
    from paper_manager.config import load_config
    from paper_manager.search import get_collection, reindex_all

    root = Path.cwd()
    config = load_config(root)

    if not config.papers_path.exists():
        typer.echo("No papers directory found.", err=True)
        raise typer.Exit(1)

    typer.echo("Rebuilding search index...")
    collection = get_collection(config.chromadb_path)
    count = reindex_all(config.papers_path, collection)
    typer.echo(f"Indexed {count} paper(s).")


# ---------------------------------------------------------------------------
# config
# ---------------------------------------------------------------------------

@app.command(name="config")
def config_cmd() -> None:
    """Show current configuration and validate the API key."""
    from paper_manager.config import load_config

    root = Path.cwd()
    config = load_config(root)

    typer.echo("paper-manager configuration\n")
    typer.echo(f"  root_dir:      {config.root_dir}")
    typer.echo(f"  model:         {config.model}")
    typer.echo(f"  tag_model:     {config.tag_model}")
    typer.echo(f"  papers_dir:    {config.papers_dir}")
    typer.echo(f"  template:      {config.template}")
    typer.echo(f"  chromadb_dir:  {config.chromadb_dir}")
    typer.echo(f"  git_remote:    {config.git_remote or '(not set)'}")

    typer.echo(f"  backend:       Claude Code CLI (Max subscription)")

    # Validate Claude Code CLI is available
    typer.echo("\nValidating Claude Code CLI...")
    try:
        import subprocess
        result = subprocess.run(
            ["claude", "-p", "respond with exactly: OK", "--output-format", "text"],
            capture_output=True, text=True, timeout=30,
        )
        if result.returncode == 0 and "OK" in result.stdout:
            typer.echo("  Claude Code CLI: available")
        else:
            typer.echo("  Claude Code CLI: error — check your installation", err=True)
    except FileNotFoundError:
        typer.echo("  Claude Code CLI: not found — install Claude Code first", err=True)
    except Exception as exc:
        typer.echo(f"  Claude Code CLI: could not validate — {exc}", err=True)
