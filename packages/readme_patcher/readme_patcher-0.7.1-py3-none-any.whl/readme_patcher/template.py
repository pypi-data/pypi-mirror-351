import os
import typing

from jinja2 import Environment, FileSystemLoader, select_autoescape

from . import filters, functions
from .badge import Badge

if typing.TYPE_CHECKING:
    from .project import Project


def setup_environment(project: "Project") -> Environment:
    """
    Setup the search paths for the template engine Jinja2. ``os.path.sep`` is

    required to be able to include absolute paths, quotes around
    ``os.PathLike[str]`` to get py38 compatibility."""
    environment = Environment(
        loader=FileSystemLoader([project.base_dir, os.path.sep]),
        autoescape=select_autoescape(),
        keep_trailing_newline=True,
    )

    environment.filters.update(filters.collection)

    environment.globals.update(functions.collection)
    environment.globals.update(project=project)
    if project.py_project:
        environment.globals.update(py_project=project.py_project)
        if project.py_project.repository:
            try:
                github = project.github
                environment.globals.update(github=github)
            except Exception:
                pass

    environment.globals.update(badge=Badge(project))

    return environment
