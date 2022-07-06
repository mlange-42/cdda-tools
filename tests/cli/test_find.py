import shutil
import tempfile
import unittest

from cdda_tools import cli


class TestFind(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        shutil.unpack_archive("tests/test_data/save.tar.gz", self.test_dir)

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_find(self):
        args = cli.parse_args(
            [
                f"-d={self.test_dir}",
                "find",
                "-w=WorldA",
                "-p=PlayerA",
                "terrain",
                "*forest*",
            ]
        )
        lines = [line for line in cli.run_cli(args)]
        self.assertTrue(len(lines) > 0)

    def test_find_nothing(self):
        args = cli.parse_args(
            [
                f"-d={self.test_dir}",
                "find",
                "-w=WorldA",
                "-p=PlayerA",
                "terrain",
                "abcdefg",
            ]
        )
        lines = [line for line in cli.run_cli(args)]
        self.assertEqual(len(lines), 0)
