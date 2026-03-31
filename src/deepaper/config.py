"""Configuration loading for deepaper.

Priority order: environment variables > config.yaml > defaults.
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

import yaml


@dataclass
class Config:
    api_key: str
    model: str = "claude-opus-4-6"
    tag_model: str = "claude-opus-4-6"
    git_remote: str = ""
    papers_dir: str = "papers"
    template: str = "default"
    chromadb_dir: str = ".chromadb"
    semantic_scholar_api_key: str = ""

    # Derived paths (set after init)
    root_dir: Path = field(default_factory=Path.cwd)

    @property
    def papers_path(self) -> Path:
        return self.root_dir / self.papers_dir

    @property
    def chromadb_path(self) -> Path:
        return self.root_dir / self.chromadb_dir

    @property
    def templates_path(self) -> Path:
        return self.root_dir / "templates"

    @property
    def tmp_path(self) -> Path:
        return self.root_dir / "tmp"


def _ensure_config(config_path: Path) -> None:
    """Create a default config.yaml if one does not exist."""
    from deepaper.defaults import DEFAULT_CONFIG_YAML
    config_path.write_text(DEFAULT_CONFIG_YAML, encoding="utf-8")


def _ensure_templates(templates_dir: Path) -> None:
    """Create the templates directory with default templates if missing."""
    from deepaper.defaults import (
        DEFAULT_TEMPLATE, DEFAULT_CATEGORIES,
        DEFAULT_CLASSIFY, DEFAULT_TAGS,
    )

    templates_dir.mkdir(parents=True, exist_ok=True)

    _defaults = {
        "default.md": DEFAULT_TEMPLATE,
        "categories.md": DEFAULT_CATEGORIES,
        "classify.md": DEFAULT_CLASSIFY,
        "tags.md": DEFAULT_TAGS,
    }
    for filename, content in _defaults.items():
        path = templates_dir / filename
        if not path.exists():
            path.write_text(content, encoding="utf-8")


def load_config(root_dir: Path | None = None) -> Config:
    """Load configuration from environment variables and config.yaml.

    If config.yaml does not exist it is created automatically with defaults
    so that commands like ``deepaper add`` work from a fresh directory without
    requiring the user to run ``deepaper init`` first.

    Args:
        root_dir: Project root directory. Defaults to current working directory.

    Returns:
        Config instance with all settings resolved.
    """
    if root_dir is None:
        root_dir = Path.cwd()

    config_path = root_dir / "config.yaml"
    file_config: dict = {}

    if not config_path.exists():
        _ensure_config(config_path)

    with open(config_path, encoding="utf-8") as f:
        file_config = yaml.safe_load(f) or {}

    # Ensure templates directory exists
    _ensure_templates(root_dir / "templates")

    # API key is optional — analysis now uses Claude Code CLI (Max subscription)
    api_key = (
        os.environ.get("ANTHROPIC_API_KEY")
        or file_config.get("anthropic_api_key", "")
    )

    return Config(
        api_key=api_key,
        model=os.environ.get("DEEPAPER_MODEL") or file_config.get("model", "claude-opus-4-6"),
        tag_model=file_config.get("tag_model", "claude-opus-4-6"),
        git_remote=file_config.get("git_remote", ""),
        papers_dir=file_config.get("papers_dir", "papers"),
        template=file_config.get("template", "default"),
        chromadb_dir=file_config.get("chromadb_dir", ".chromadb"),
        semantic_scholar_api_key=(
            os.environ.get("SEMANTIC_SCHOLAR_API_KEY")
            or file_config.get("semantic_scholar_api_key", "")
        ),
        root_dir=root_dir,
    )
