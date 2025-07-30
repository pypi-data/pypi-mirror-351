from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

from readme_patcher.project import Project

from . import config
from .config import setup_argument_parser


def search_for_pyproject_toml() -> Optional[Path]:
    """
    https://stackoverflow.com/a/68994012
    """
    directory = Path.cwd()
    # /
    root = Path(directory.root)
    while directory != root:
        attempt = directory / "pyproject.toml"
        if attempt.exists():
            return attempt
        directory = directory.parent
    return None


def main() -> None:
    config.args = setup_argument_parser()
    pyproject_toml = search_for_pyproject_toml()
    base_dir: str | Path
    if pyproject_toml:
        base_dir = pyproject_toml.parent
    else:
        base_dir = os.getcwd()

    if config.args.verbosity > 0:
        print("Found project in {}".format(base_dir))

    Project(base_dir).patch()
