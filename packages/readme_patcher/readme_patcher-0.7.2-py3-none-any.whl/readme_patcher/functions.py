"""https://jinja.palletsprojects.com/en/3.1.x/api/#custom-filters"""

from __future__ import annotations

import importlib
import os
import re
import subprocess
from typing import Any, Callable

from jinja2 import pass_context
from jinja2.runtime import Context


def read_cli_output(command: str, strip_whitespaces: bool = True) -> str:
    result = subprocess.run(command, capture_output=True, text=True, shell=True)
    output = result.stdout + result.stderr
    # clean ansi codes
    output = re.sub(r"\x1b.*?m", "", output)
    if strip_whitespaces:
        output = output.strip()
    return output


def read_func_output(function_spec: str) -> str:
    module, func_name = function_spec.rsplit(".", 1)
    func = getattr(importlib.import_module(module), func_name)
    return func()


@pass_context
def read_file_content(context: Context, path: str) -> str:
    project = context.get("project")
    file = open(os.path.join(project.base_dir, path), "r")
    return file.read()


collection: dict[str, Callable[..., Any]] = {
    "cli": read_cli_output,
    "func": read_func_output,
    "read": read_file_content,
}
