"""Command-line interface for deepaper.

Lightweight paper knowledge base for Claude Code.
Analysis is done via /deepaper slash command in Claude Code.
CLI provides I/O utilities: download, save, cite, sync.
"""
from __future__ import annotations

import json
import re
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

    # CLI --tags overrides analysis frontmatter tags; otherwise use writer's
    tag_list = [t.strip() for t in tags.split(",") if t.strip()] if tags else analysis_fm.get("tags", [])
    if tags:
        analysis_fm["tags"] = tag_list  # ensure writer.py preserves override

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


# ---------------------------------------------------------------------------
# registry
# ---------------------------------------------------------------------------

@app.command()
def registry(
    arxiv_id: str = typer.Argument(..., help="arxiv ID to build registry for."),
) -> None:
    """Build visual registry from extracted text and output as JSON."""
    root = Path.cwd()
    run_dir = root / ".deepaper" / "runs" / arxiv_id

    from deepaper.pipeline_io import safe_read_json
    text_by_page_raw = safe_read_json(str(run_dir / "text_by_page.json"), default={})
    text_by_page = {int(k): v for k, v in text_by_page_raw.items()}

    if not text_by_page:
        typer.echo(json.dumps({"error": "text_by_page.json not found or empty"}))
        raise typer.Exit(1)

    from deepaper.registry import build_visual_registry
    reg = build_visual_registry(text_by_page)

    from deepaper.pipeline_io import safe_write_json
    safe_write_json(str(run_dir / "visual_registry.json"), reg)

    typer.echo(json.dumps(reg, ensure_ascii=False, indent=2))


# ---------------------------------------------------------------------------
# gates
# ---------------------------------------------------------------------------

@app.command()
def gates(
    arxiv_id: str = typer.Argument(..., help="arxiv ID to run gates on."),
) -> None:
    """Run HardGates on merged analysis and output results as JSON."""
    root = Path.cwd()
    run_dir = root / ".deepaper" / "runs" / arxiv_id

    merged_path = run_dir / "merged.md"
    if not merged_path.exists():
        typer.echo(json.dumps({"error": "merged.md not found"}))
        raise typer.Exit(1)

    merged_md = merged_path.read_text(encoding="utf-8")

    from deepaper.pipeline_io import safe_read_json
    registry_data = safe_read_json(str(run_dir / "visual_registry.json"))
    text_by_page_raw = safe_read_json(str(run_dir / "text_by_page.json"))
    text_by_page = (
        {int(k): v for k, v in text_by_page_raw.items()}
        if text_by_page_raw
        else None
    )

    from deepaper.registry import build_coverage_checklist, identify_core_figures, compute_paper_profile
    checklist = {}
    core_figures = []
    profile = safe_read_json(str(run_dir / "paper_profile.json"), {})
    if text_by_page and registry_data:
        computed_profile = compute_paper_profile(text_by_page, registry_data)
        # Merge: prefer pre-saved profile (has top_level_sections from Task 1),
        # fall back to freshly computed values for any missing keys.
        profile = {**computed_profile, **profile} if profile else computed_profile
        core_figures = identify_core_figures(registry_data, text_by_page, profile["total_pages"])
        checklist = build_coverage_checklist(
            text_by_page, registry_data, profile.get("subsection_headings", [])
        )

    from deepaper.gates import run_hard_gates
    result = run_hard_gates(merged_md, checklist, core_figures, text_by_page, registry_data,
                            paper_profile=profile or None)

    result_json = json.dumps(result, ensure_ascii=False, indent=2)
    (run_dir / "gates.json").write_text(result_json, encoding="utf-8")
    typer.echo(result_json)


# ---------------------------------------------------------------------------
# extract
# ---------------------------------------------------------------------------

@app.command()
def extract(
    arxiv_id: str = typer.Argument(..., help="arxiv ID to extract."),
) -> None:
    """Extract text from PDF and build registry, profile, core figures."""
    import fitz
    from deepaper.pipeline_io import safe_write_json, ensure_run_dir
    from deepaper.registry import (
        build_visual_registry, compute_paper_profile,
        identify_core_figures, extract_figure_contexts,
        identify_core_tables,
    )

    root = Path.cwd()
    pdf_path = root / "tmp" / f"{arxiv_id}.pdf"
    if not pdf_path.exists():
        typer.echo(json.dumps({"error": f"PDF not found: {pdf_path}"}))
        raise typer.Exit(1)

    run_dir = ensure_run_dir(root, arxiv_id)

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

    int_text = {int(k): v for k, v in text_by_page.items()}
    registry_data = build_visual_registry(int_text)
    safe_write_json(str(run_dir / "visual_registry.json"), registry_data)

    profile = compute_paper_profile(int_text, registry_data)
    safe_write_json(str(run_dir / "paper_profile.json"), profile)

    core_figs = identify_core_figures(registry_data, int_text, profile["total_pages"])
    safe_write_json(str(run_dir / "core_figures.json"), core_figs)

    fig_contexts = extract_figure_contexts(int_text, core_figs)
    safe_write_json(str(run_dir / "figure_contexts.json"), fig_contexts)

    core_tables = identify_core_tables(registry_data, int_text, profile["total_pages"])
    safe_write_json(str(run_dir / "core_tables.json"), core_tables)

    # v2.1: extract core figure images
    from deepaper.extractor import extract_core_figure_images
    figures_dir = run_dir / "figures"
    fig_result = extract_core_figure_images(
        pdf_path=str(pdf_path),
        core_figures=core_figs,
        output_dir=str(figures_dir),
    )
    if fig_result.get("warning"):
        typer.echo(f"Warning: {fig_result['warning']}", err=True)

    table_def_pages = sorted(set(
        v["definition_page"] for v in registry_data.values()
        if v.get("type") == "Table" and v.get("definition_page")
    ))

    typer.echo(json.dumps({
        "run_dir": str(run_dir),
        "total_pages": profile["total_pages"],
        "num_tables": profile["num_tables"],
        "num_figures": profile["num_figures"],
        "num_equations": profile["num_equations"],
        "core_figures": [cf["key"] for cf in core_figs],
        "core_tables": [ct["key"] for ct in core_tables],
        "table_def_pages": table_def_pages,
        "figures_extracted": fig_result["extracted"],
    }, ensure_ascii=False, indent=2))


# ---------------------------------------------------------------------------
# check
# ---------------------------------------------------------------------------

@app.command()
def check(
    arxiv_id: str = typer.Argument(..., help="arxiv ID to check."),
) -> None:
    """Run StructCheck + Auditor on Extractor notes."""
    from deepaper.pipeline_io import safe_read_json, safe_write_json, ensure_run_dir
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
        "audit": {"coverage_ratio": ac["coverage_ratio"], "uncovered_segments": ac["uncovered_segments"]},
    }
    safe_write_json(str(run_dir / "check.json"), result)
    typer.echo(json.dumps(result, indent=2))


# ---------------------------------------------------------------------------
# prompt
# ---------------------------------------------------------------------------

@app.command()
def prompt(
    arxiv_id: str = typer.Argument(..., help="arxiv ID."),
    role: Optional[str] = typer.Option(None, "--role", help="Agent role: extractor"),
    split: bool = typer.Option(False, "--split", help="Auto-split into Writer prompts."),
) -> None:
    """Generate agent prompts."""
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
        tmpl_path = Path(__file__).parent / "prompt_templates" / "extractor.md"
        if not tmpl_path.exists():
            typer.echo(json.dumps({"error": f"Template not found: {tmpl_path}"}))
            raise typer.Exit(1)
        tmpl = tmpl_path.read_text(encoding="utf-8")
        profile = safe_read_json(str(run_dir / "paper_profile.json"), {})
        core_tables = safe_read_json(str(run_dir / "core_tables.json"), [])
        core_figures = safe_read_json(str(run_dir / "core_figures.json"), [])

        # Compute read strategy: generate exact Read commands
        text_path = run_dir / "text.txt"
        total_lines = 0
        if text_path.exists():
            total_lines = sum(1 for _ in text_path.open(encoding="utf-8"))

        chunk_size = 2000
        read_commands_lines: list[str] = []
        if total_lines <= chunk_size:
            read_commands_lines.append(
                f'1. `Read(file_path="{run_dir}/text.txt")`'
            )
        else:
            n_reads = max(1, -(-total_lines // chunk_size))
            for i in range(n_reads):
                offset = i * chunk_size
                limit = min(chunk_size, total_lines - offset)
                read_commands_lines.append(
                    f'{i + 1}. `Read(file_path="{run_dir}/text.txt", offset={offset}, limit={limit})`'
                )
        read_commands = "\n".join(read_commands_lines)

        core_tables_json = json.dumps(core_tables, ensure_ascii=False, indent=2) if core_tables else "（本论文未检测到核心表格候选）"
        core_figures_json = json.dumps(core_figures, ensure_ascii=False, indent=2) if core_figures else "（本论文未检测到灵魂图）"

        prompt_text = (tmpl
            .replace("{RUN_DIR}", str(run_dir))
            .replace("{TOTAL_PAGES}", str(profile.get("total_pages", "?")))
            .replace("{ARXIV_ID}", arxiv_id)
            .replace("{TOTAL_LINES}", str(total_lines))
            .replace("{READ_COMMANDS}", read_commands)
            .replace("{CORE_FIGURES_JSON}", core_figures_json)
            .replace("{CORE_TABLES_JSON}", core_tables_json))
        out_path = run_dir / "prompt_extractor.md"
        out_path.write_text(prompt_text, encoding="utf-8")
        typer.echo(json.dumps({"prompt_file": str(out_path)}))
        return

    if split:
        profile = safe_read_json(str(run_dir / "paper_profile.json"), {})
        registry_data = safe_read_json(str(run_dir / "visual_registry.json"), {})
        core_figures = safe_read_json(str(run_dir / "core_figures.json"), [])
        figure_contexts = safe_read_json(str(run_dir / "figure_contexts.json"), {})

        table_def_pages = sorted(set(
            v["definition_page"] for v in (registry_data or {}).values()
            if v.get("type") == "Table" and v.get("definition_page")
        ))

        # Compute file sizes for read strategy
        text_path = run_dir / "text.txt"
        notes_path = run_dir / "notes.md"
        text_lines = sum(1 for _ in text_path.open(encoding="utf-8")) if text_path.exists() else 0
        notes_lines = sum(1 for _ in notes_path.open(encoding="utf-8")) if notes_path.exists() else 0
        file_info = {"notes_lines": notes_lines, "text_lines": text_lines}

        template_sections = parse_template_sections(DEFAULT_TEMPLATE)
        system_role = extract_system_role(DEFAULT_TEMPLATE)
        tasks = auto_split(profile or {})

        writers_config: dict = {"writers": [], "merge_order": [], "figure_contexts": figure_contexts}

        for task in tasks:
            constraints = gates_to_constraints(
                sections=task.sections,
                profile=profile or {},
                registry=registry_data or {},
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
                file_info=file_info,
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

        # merge reorders sections by SECTION_ORDER, so just include all writers
        writers_config["merge_order"] = [w["name"] for w in writers_config["writers"]]

        safe_write_json(str(run_dir / "writers.json"), writers_config)
        typer.echo(json.dumps(writers_config, ensure_ascii=False, indent=2))
        return

    typer.echo("Use --role extractor or --split")
    raise typer.Exit(1)


# ---------------------------------------------------------------------------
# merge
# ---------------------------------------------------------------------------

def _hoist_frontmatter(content: str) -> str:
    """Move YAML frontmatter to the top and collapse double #### markers.

    When writers write parts independently, the part containing frontmatter
    may not be first in merge order, so frontmatter ends up mid-file. This
    helper detects the `---\\n...---\\n` block anywhere in the content and
    moves it to the start. Also collapses accidental `#### #### ` duplicates
    that arise when a writer prepends `####` to a section name that already
    has it.
    """
    import re as _re

    content = content.strip()

    # Collapse double heading markers: "#### #### X" -> "#### X"
    content = _re.sub(r"#### #### ", "#### ", content)

    if content.startswith("---\n"):
        return content  # Already at top

    # Find the first standalone "---\n...\n---\n" YAML block
    match = _re.search(r"(^|\n)---\n(.*?)\n---\n", content, _re.DOTALL)
    if not match:
        return content  # No frontmatter to hoist

    fm_block = "---\n" + match.group(2).strip() + "\n---\n\n"
    body = content[:match.start()] + content[match.end():]
    body = body.lstrip("\n")
    return fm_block + body


@app.command()
def merge(
    arxiv_id: str = typer.Argument(..., help="arxiv ID to merge."),
) -> None:
    """Merge Writer outputs in canonical order."""
    from deepaper.pipeline_io import safe_read_json, ensure_run_dir

    root = Path.cwd()
    run_dir = ensure_run_dir(root, arxiv_id)
    config = safe_read_json(str(run_dir / "writers.json"))

    if not config:
        typer.echo(json.dumps({"error": "writers.json not found"}))
        raise typer.Exit(1)

    # Read all writer parts
    raw_parts = []
    for writer_name in config["merge_order"]:
        writer = next((w for w in config["writers"] if w["name"] == writer_name), None)
        if not writer:
            continue
        part_path = run_dir / writer["output_file"]
        if part_path.exists():
            raw_parts.append(part_path.read_text(encoding="utf-8"))

    merged = "\n\n".join(raw_parts)

    # Reorder sections by SECTION_ORDER
    from deepaper.output_schema import SECTION_ORDER, HEADING_SECTION_LEVEL
    h_prefix = "#" * HEADING_SECTION_LEVEL + " "  # "#### "
    # Split into frontmatter + sections
    frontmatter = ""
    body = merged
    if merged.startswith("---"):
        fm_end = merged.find("---", 3)
        if fm_end > 0:
            frontmatter = merged[:fm_end + 3]
            body = merged[fm_end + 3:]
    # Parse sections by #### headers
    section_pattern = re.compile(r"(?=^" + re.escape(h_prefix) + r")", re.MULTILINE)
    chunks = section_pattern.split(body)
    preamble = chunks[0] if chunks else ""
    sections: dict[str, str] = {}
    unmatched: list[str] = []
    for chunk in chunks[1:]:
        matched = False
        for name in SECTION_ORDER:
            if chunk.lstrip().startswith(h_prefix) and name in chunk[:chunk.find("\n") if "\n" in chunk else len(chunk)]:
                sections[name] = h_prefix + chunk
                matched = True
                break
        if not matched:
            unmatched.append(h_prefix + chunk)
    # Reassemble in canonical order
    ordered = [frontmatter, preamble] if frontmatter else [preamble]
    for name in SECTION_ORDER:
        if name in sections:
            ordered.append(sections[name])
    ordered.extend(unmatched)
    merged = "\n\n".join(part for part in ordered if part.strip())

    # Normalize: remove stray --- outside YAML frontmatter
    if merged.startswith("---"):
        fm_end = merged.find("---", 3)
        if fm_end > 0:
            yaml_block = merged[:fm_end + 3]
            body = merged[fm_end + 3:]
            body = re.sub(r"\n---\s*\n", "\n\n", body)
            merged = yaml_block + body

    # Remove stray title lines
    merged = re.sub(r"^#{1,3}\s+.*(?:Part [ABC]|深度分析|部分).*\n+", "", merged, flags=re.MULTILINE)

    # Hoist frontmatter to top and collapse double #### markers
    merged = _hoist_frontmatter(merged)

    merged_path = run_dir / "merged.md"
    merged_path.write_text(merged, encoding="utf-8")
    (run_dir / "final.md").write_text(merged, encoding="utf-8")

    typer.echo(json.dumps({"merged": str(merged_path), "chars": len(merged)}))


# ---------------------------------------------------------------------------
# fix
# ---------------------------------------------------------------------------

@app.command()
def fix(
    arxiv_id: str = typer.Argument(..., help="arxiv ID to fix."),
) -> None:
    """Generate Fixer prompt from gate failures."""
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
                lines.append("  → 从 notes.md 的相关段落补充内容")
        elif gate_name == "H7":
            for fig_key in gate.get("missing", []):
                ctx = (figure_contexts or {}).get(fig_key, {})
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


# ---------------------------------------------------------------------------
# classify
# ---------------------------------------------------------------------------

@app.command()
def classify(
    arxiv_id: str = typer.Argument(..., help="arxiv ID to classify."),
) -> None:
    """Generate classification prompt from categories.md rules."""
    from deepaper.pipeline_io import ensure_run_dir
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
    meta_match = re.search(r"## META\n(.*?)(?=\n## |\Z)", notes, re.DOTALL)
    summary = meta_match.group(1).strip() if meta_match else notes[:500]

    categories = load_template("categories", config.templates_path)
    classify_tmpl = load_template("classify", config.templates_path)

    prompt_text = classify_tmpl.format(summary=summary, categories=categories)
    prompt_path = run_dir / "prompt_classify.md"
    prompt_path.write_text(prompt_text, encoding="utf-8")

    typer.echo(json.dumps({"prompt_file": str(prompt_path)}))
