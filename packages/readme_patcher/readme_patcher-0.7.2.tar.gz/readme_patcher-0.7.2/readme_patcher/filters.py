"""Custom jinja filters

https://jinja.palletsprojects.com/en/3.1.x/api/#custom-filters
"""

from __future__ import annotations

from typing import Any, Callable

from jinja2.filters import do_indent


def _indent_block(content: str, strip_whitespace: bool = True) -> str:
    if strip_whitespace:
        content = content.strip()
    return "\n\n" + do_indent(content, width=4, first=True) + "\n\n"


def wrap_in_code_block(
    content: str, language: str = "", strip_whitespace: bool = True
) -> str:
    """https://www.sphinx-doc.org/en/master/usage/restructuredtext/directives.html#directive-code-block

    https://pygments.org/docs/lexers/
    """
    return "\n.. code-block:: " + language + _indent_block(content, strip_whitespace)


def wrap_in_literal_block(content: str, strip_whitespace: bool = True) -> str:
    """
    https://www.sphinx-doc.org/en/master/usage/restructuredtext/basics.html#literal-blocks
    """
    return "\n:: " + _indent_block(content, strip_whitespace)


def heading(content: str, level: int = 1) -> str:
    """
    https://www.sphinx-doc.org/en/master/usage/restructuredtext/basics.html#sections
    """
    length = len(content)
    # markdown:
    # print('\n' + ('#' * level) + ' ' + content + '\n')
    if level == 1:
        underline = "="
    elif level == 2:
        underline = "-"
    elif level == 3:
        underline = "^"
    elif level == 4:
        underline = '"'
    else:
        underline = "-"
    return "\n" + content + "\n" + (underline * length) + "\n"


collection: dict[str, Callable[..., Any]] = {
    "code": wrap_in_code_block,
    "literal": wrap_in_literal_block,
    "heading": heading,
}
