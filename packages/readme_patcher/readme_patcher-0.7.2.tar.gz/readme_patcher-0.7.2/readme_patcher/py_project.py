from __future__ import annotations

import re
from functools import cached_property
from typing import Any, Dict

from pyproject_parser import PyProject


class SimplePyProject:
    """Contains the attributes of a pyproject.toml file that we are interested in."""

    py_project: PyProject

    def __init__(self, py_project: PyProject) -> None:
        self.py_project = py_project

    @cached_property
    def _project(self) -> Dict[str, Any] | None:
        if (
            self.py_project.tool
            and "poetry" in self.py_project.tool
            and self.py_project.tool["poetry"]
        ):
            return self.py_project.tool["poetry"]
        if self.py_project.project:
            return self.py_project.project  # type: ignore
        return None

    @cached_property
    def name(self) -> str | None:
        if self._project and self._project["name"]:
            return self._project["name"]
        return None

    @cached_property
    def name_normalized(self) -> str | None:
        if self.name:
            return re.sub(r"[-_.]+", "-", self.name).lower()
        return None

    @cached_property
    def repository(self) -> str | None:
        if self._project is None:
            return None
        if "repository" in self._project:
            return self._project["repository"]
        if self._project["urls"] and self._project["urls"]["Repository"]:
            return self._project["urls"]["Repository"]
        return None
