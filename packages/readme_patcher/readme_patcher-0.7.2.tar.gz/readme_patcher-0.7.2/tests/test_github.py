from readme_patcher.github import GithubRepository, request_github_api
from tests.helper import activate_requests_mock, project

github: GithubRepository = request_github_api(
    "https://github.com/Josef-Friedrich/readme_patcher/"
)


@activate_requests_mock
def test_name() -> None:
    assert github["name"] == "readme_patcher"


@activate_requests_mock
def test_full_name() -> None:
    assert github["full_name"] == "Josef-Friedrich/readme_patcher"


@activate_requests_mock
def test_description() -> None:
    assert (
        github["description"] == "Generate README files from templates. "
        "Allow input from functions calls and cli output."
    )


@activate_requests_mock
def test_integration() -> None:
    assert (
        project.patch_file(
            src="objects/github/owner/login_template.rst",
            dest="objects/github/owner/login.rst",
        )
        == "#Josef-Friedrich#\n"
    )
