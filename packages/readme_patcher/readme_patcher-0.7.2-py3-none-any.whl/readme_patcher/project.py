from __future__ import annotations

from functools import cached_property
from pathlib import Path
from typing import Any, Dict, List, Optional

from jinja2 import Environment
from pyproject_parser import PyProject

from readme_patcher.template import setup_environment

from .file import File, Variables
from .github import GithubRepository, request_github_api
from .py_project import SimplePyProject


class Project:
    """A project corresponds to a code repository. In its root there is a
    README file."""

    base_dir: Path

    def __init__(self, base_dir: str | Path):
        if isinstance(base_dir, str):
            self.base_dir = Path(base_dir)
        else:
            self.base_dir = base_dir

    @cached_property
    def _py_project(self) -> PyProject | None:
        path = self.base_dir / "pyproject.toml"
        if path.exists():
            return PyProject().load(path)  # type: ignore
        return None

    @cached_property
    def py_project(self) -> SimplePyProject | None:
        py_project = self._py_project
        if py_project:
            return SimplePyProject(py_project)
        return None

    @cached_property
    def py_project_config(self) -> Dict[str, Any] | None:
        if self._py_project and "readme_patcher" in self._py_project.tool:
            return self._py_project.tool["readme_patcher"]
        return None

    @cached_property
    def github(self) -> GithubRepository | None:
        if self.py_project and self.py_project.repository:
            return request_github_api(self.py_project.repository)
        return None

    def patch_file(
        self, src: str, dest: str, variables: Optional[Variables] = None
    ) -> str:
        return File(project=self, src=src, dest=dest, variables=variables).patch()

    def _patch_files_specified_in_toml(self, config: Dict[str, Any]) -> List[str]:
        rendered: List[str] = []
        for file_config in config["file"]:
            file = File(project=self, config=file_config)
            rendered.append(file.patch())
        return rendered

    @cached_property
    def template_env(self) -> Environment:
        return setup_environment(self)

    def _patch_default(self) -> str:
        return File(project=self, src="README_template.rst", dest="README.rst").patch()

    def patch(self) -> List[str]:
        config = self.py_project_config
        if config:
            return self._patch_files_specified_in_toml(config)
        else:
            return [self._patch_default()]
