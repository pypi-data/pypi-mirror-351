import os

from tests.helper import activate_requests_mock, get_path, project, read_file_content


def assert_patch_file(basename: str) -> None:
    rendered = project.patch_file(
        src="badge/{}_template.rst".format(basename),
        dest="badge/{}_tmp.rst".format(basename),
    )
    expected = read_file_content("project/badge/{}.rst".format(basename))
    os.remove(get_path("project/badge/{}_tmp.rst".format(basename)))
    assert rendered == expected


@activate_requests_mock
def test_pypi() -> None:
    assert_patch_file("pypi")


@activate_requests_mock
def test_github_workflow() -> None:
    assert_patch_file("github_workflow")


@activate_requests_mock
def test_readthedocs() -> None:
    assert_patch_file("readthedocs")
