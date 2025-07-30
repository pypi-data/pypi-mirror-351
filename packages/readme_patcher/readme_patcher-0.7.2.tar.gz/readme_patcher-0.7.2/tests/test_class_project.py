"""Test some jinja features"""

from tests.helper import activate_requests_mock, project


@activate_requests_mock
def test_property_py_project() -> None:
    rendered = project.patch()
    assert (
        rendered[0]
        == "README\n======\n\nhttps://github.com/Josef-Friedrich/readme_patcher\n"
    )
