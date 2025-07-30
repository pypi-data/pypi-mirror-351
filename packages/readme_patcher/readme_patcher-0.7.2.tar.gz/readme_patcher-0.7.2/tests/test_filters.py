from tests.helper import activate_requests_mock, patch


@activate_requests_mock
def test_filter_code() -> None:
    assert (
        patch("filters/code/without-language.rst", {"output": "code"})
        == "#\n.. code-block:: \n\n    code\n\n#\n"
    )


@activate_requests_mock
def test_filter_code_language() -> None:
    assert (
        patch("filters/code/with-language.rst", {"output": "code"})
        == "#\n.. code-block:: python\n\n    code\n\n#\n"
    )


@activate_requests_mock
def test_literal() -> None:
    assert (
        patch("filters/literal.rst", {"output": "code"}) == "#\n:: \n\n    code\n\n#\n"
    )


@activate_requests_mock
def test_heading() -> None:
    assert patch("filters/heading.rst") == "#\nheading\n=======\n#\n"
