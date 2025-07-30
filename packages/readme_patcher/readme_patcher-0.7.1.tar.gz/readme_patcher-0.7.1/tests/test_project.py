from pathlib import Path

from readme_patcher.project import Project
from tests.helper import TEST_FILES_FOLDER, project

project_uv = Project(Path(TEST_FILES_FOLDER) / "project_uv")


def test_poetry() -> None:
    assert project.py_project
    assert project.py_project.name_normalized == "readme-patcher"
    assert (
        project.py_project.repository
        == "https://github.com/Josef-Friedrich/readme_patcher"
    )


def test_uv() -> None:
    assert project_uv.py_project
    assert project_uv.py_project.name_normalized == "readme-patcher"
    assert (
        project_uv.py_project.repository
        == "https://github.com/Josef-Friedrich/readme_patcher"
    )
