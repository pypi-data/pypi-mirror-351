import os

from tests.helper import activate_requests_mock, get_tmp_file_path, patch, project


class TestFunctions:
    @activate_requests_mock
    def test_cli(self) -> None:
        assert patch("functions/cli.rst") == "#output#\n"

    @activate_requests_mock
    def test_func(self) -> None:
        assert patch("functions/func.rst") == "#{}#\n".format(os.getcwd())

    @activate_requests_mock
    def test_read(self) -> None:
        assert (
            project.patch_file("read.rst", get_tmp_file_path())
            == "#\n:: \n\n    Example text\n\n#\n"
        )
