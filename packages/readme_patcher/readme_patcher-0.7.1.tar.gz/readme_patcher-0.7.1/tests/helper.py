import json
import os
import tempfile
from pathlib import Path
from typing import Optional

import responses

from readme_patcher import Project
from readme_patcher.file import Variables

TEST_FILES_FOLDER = os.path.join(os.path.dirname(__file__), "files")


def get_tmp_file_path() -> str:
    return os.path.join(tempfile.mkdtemp(), "README.rst")


def get_path(rel_path: str) -> str:
    return os.path.join(TEST_FILES_FOLDER, rel_path)


def read_file_content(rel_path: str) -> str:
    file = open(get_path(rel_path), "r")
    return file.read()


responses.get(
    "https://api.github.com/repos/Josef-Friedrich/readme_patcher",
    json=json.loads(read_file_content("github.json")),
)

activate_requests_mock = responses.activate

project_test_files_folder = Project(TEST_FILES_FOLDER)


def patch(src: str, variables: Optional[Variables] = None) -> str:
    tmp = get_tmp_file_path()
    project_test_files_folder.patch_file(src=src, dest=tmp, variables=variables)
    return read_file_content(tmp)


# To avoid Github API limits: Client Error: rate limit exceeded for url
# rate limit exceeded for url
project = Project(Path(TEST_FILES_FOLDER) / "project")
