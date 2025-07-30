"""Test some jinja features"""

from tests.helper import activate_requests_mock, patch


@activate_requests_mock
def test_include() -> None:
    assert (
        patch("include/python-snippet.rst")
        == 'def example():\n    print("Example")\n\n'
    )
