from __future__ import annotations

import re
import typing
from typing import Dict, Optional, TypedDict

from jinja2 import Template

from . import config, functions

if typing.TYPE_CHECKING:
    from .project import Project


class Replacement:
    """A variable and its replacement text."""

    raw: str

    def __init__(self, raw: str) -> None:
        self.raw = raw.strip()

    def get(self) -> str:
        output: str
        if self.raw.startswith("cli:"):
            output = functions.read_cli_output(self.raw[4:].strip())
        elif self.raw.startswith("func:"):
            output = functions.read_func_output(self.raw[5:].strip())
        else:
            output = self.raw
        return str(output)


class FileConfig(TypedDict):
    src: str
    dest: str
    variables: Optional[Dict[str, str]]


Variables = Dict[str, str]


class File:
    """A file to patch."""

    project: "Project"
    src: str
    dest: str
    variables: Optional[Variables] = None

    def __init__(
        self,
        project: "Project",
        src: Optional[str] = None,
        dest: Optional[str] = None,
        variables: Optional[Variables] = None,
        config: Optional[FileConfig] = None,
    ) -> None:
        self.project = project
        if config:
            self.src = config["src"]
            self.dest = config["dest"]
            if "variables" in config:
                self.variables = config["variables"]
        if src:
            self.src = src
        if dest:
            self.dest = dest
        if variables:
            self.variables = variables

    def _setup_template(self) -> Template:
        variables: Dict[str, str] = {}
        if self.variables:
            for k, v in self.variables.items():
                variables[k] = Replacement(v).get()

        template = self.project.template_env.get_template(self.src)
        template.globals.update(variables)
        return template  #

    def patch(self) -> str:
        if config.args.verbosity > 0:
            print("Patch file dest: {} src: {}".format(self.src, self.dest))
        template = self._setup_template()

        rendered = template.render()
        # Remove multiple newlines
        rendered = re.sub(r"\n\s*\n", "\n\n", rendered)
        if config.args.verbosity > 1:
            print(rendered)
        dest = self.project.base_dir / self.dest
        dest.write_text(rendered)
        return rendered
