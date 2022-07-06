import shutil
import tempfile
import unittest

from cdda_tools import cli


class TestPlayer(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        shutil.unpack_archive("tests/test_data/save.tar.gz", self.test_dir)

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_path(self):
        args = cli.parse_args(
            [
                f"-d={self.test_dir}",
                "player",
                "-w=WorldA",
                "-p=PlayerA",
                "path",
                "body",
                "torso",
                "hp_max",
            ]
        )
        lines = [line for line in cli.run_cli(args)]
        self.assertEqual(len(lines), 1)
        self.assertEqual(lines[0], "90")

    def test_path_keys(self):
        args = cli.parse_args(
            [
                f"-d={self.test_dir}",
                "player",
                "-w=WorldA",
                "-p=PlayerA",
                "path",
                "body",
                "--key",
            ]
        )
        lines = [line for line in cli.run_cli(args)]
        self.assertEqual(len(lines), 1)

    def test_stats(self):
        args = cli.parse_args(
            [
                f"-d={self.test_dir}",
                "player",
                "-w=WorldA",
                "-p=PlayerA",
                "stats",
            ]
        )
        lines = [line for line in cli.run_cli(args)]
        self.assertEqual(len(lines), 4)
        self.assertTrue(lines[0].startswith("Str "))
        self.assertTrue(lines[1].startswith("Dex "))
        self.assertTrue(lines[2].startswith("Int "))
        self.assertTrue(lines[3].startswith("Per "))

    def test_skills(self):
        args = cli.parse_args(
            [
                f"-d={self.test_dir}",
                "player",
                "-w=WorldA",
                "-p=PlayerA",
                "skills",
            ]
        )
        lines = [line for line in cli.run_cli(args)]
        self.assertEqual(len(lines), 27)

    def test_profs(self):
        args = cli.parse_args(
            [
                f"-d={self.test_dir}",
                "player",
                "-w=WorldA",
                "-p=PlayerA",
                "profs",
                "--raw",
            ]
        )
        _lines = [line for line in cli.run_cli(args)]

    def test_body(self):
        args = cli.parse_args(
            [
                f"-d={self.test_dir}",
                "player",
                "-w=WorldA",
                "-p=PlayerA",
                "body",
            ]
        )
        lines = [line for line in cli.run_cli(args)]
        self.assertEqual(len(lines), 13)
