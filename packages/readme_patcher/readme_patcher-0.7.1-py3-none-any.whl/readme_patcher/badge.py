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

    def __init__(self, project: "Project"):
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
        markup = ".. image:: {}\n".format(image) + "    :target: {}\n".format(link)
        if alt:
            markup += "    :alt: {}\n".format(alt)
        return markup

    @cached_property
    def pypi(self) -> str:
        return self._linked_image(
            "http://img.shields.io/pypi/v/{}.svg".format(
                self._py_project.name_normalized
            ),
            "https://pypi.org/project/{}".format(self._py_project.name_normalized),
            "This package on the Python Package Index",
        )

    def github_workflow(
        self, workflow: str = "tests", alt: Optional[str] = "Tests"
    ) -> str:
        url = "https://github.com/{}/actions/workflows/{}.yml".format(
            self._github["full_name"], workflow
        )
        return self._linked_image(url + "/badge.svg", url, alt)

    @cached_property
    def readthedocs(self) -> str:
        return self._linked_image(
            "https://readthedocs.org/projects/{}/badge/?version=latest".format(
                self._py_project.name_normalized
            ),
            "https://{}.readthedocs.io/en/latest/?badge=latest".format(
                self._py_project.name_normalized
            ),
            "Documentation Status",
        )
