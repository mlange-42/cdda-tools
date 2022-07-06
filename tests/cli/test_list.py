import shutil
import tempfile
import unittest

from cdda_tools import cli


class TestList(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        shutil.unpack_archive("tests/test_data/save.tar.gz", self.test_dir)

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_list(self):
        args = cli.parse_args(
            [
                f"-d={self.test_dir}",
                "list",
                "-w=WorldA",
                "0'00",
                "0'00",
                "--z-level",
                "0",
            ]
        )
        _lines = [line for line in cli.run_cli(args)]

    def test_list_fail(self):
        with self.assertRaises(SystemExit):
            _args = cli.parse_args(
                [
                    f"-d={self.test_dir}",
                    "list",
                    "-w=WorldA",
                    "0'00",
                    "--z-level",
                    "0",
                ]
            )
