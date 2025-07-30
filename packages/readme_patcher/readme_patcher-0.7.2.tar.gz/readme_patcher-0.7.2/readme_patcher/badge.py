from __future__ import annotations

import typing
from functools import cached_property
from typing import Optional

if typing.TYPE_CHECKING:
    from .github import GithubRepository
    from .project import Project
    from .py_project import SimplePyProject


class Badge:
    project: "Project"

    def __init__(self, project: "Project") -> None:
        self.project = project

    @cached_property
    def _github(self) -> "GithubRepository":
        if not self.project.github:
            raise Exception("No github repo found")
        return self.project.github

    @cached_property
    def _py_project(self) -> "SimplePyProject":
        if not self.project.py_project:
            raise Exception("No pyproject.toml")
        return self.project.py_project

    def _linked_image(self, image: str, link: str, alt: Optional[str] = None) -> str:
        markup = f".. image:: {image}\n" + f"    :target: {link}\n"
        if alt:
            markup += f"    :alt: {alt}\n"
        return markup

    @cached_property
    def pypi(self) -> str:
        return self._linked_image(
            f"http://img.shields.io/pypi/v/{self._py_project.name_normalized}.svg",
            f"https://pypi.org/project/{self._py_project.name_normalized}",
            "This package on the Python Package Index",
        )

    def github_workflow(
        self, workflow: str = "tests", alt: Optional[str] = "Tests"
    ) -> str:
        url = f"https://github.com/{self._github['full_name']}/actions/workflows/{workflow}.yml"
        return self._linked_image(url + "/badge.svg", url, alt)

    @cached_property
    def readthedocs(self) -> str:
        return self._linked_image(
            f"https://readthedocs.org/projects/{self._py_project.name_normalized}/badge/?version=latest",
            f"https://{self._py_project.name_normalized}.readthedocs.io/en/latest/?badge=latest",
            "Documentation Status",
        )
