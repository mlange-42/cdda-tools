import shutil
import tempfile
import unittest

from cdda_tools import cli


class TestNote(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        shutil.unpack_archive("tests/test_data/save.tar.gz", self.test_dir)

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_note(self):
        args = cli.parse_args(
            [
                f"-d={self.test_dir}",
                "note",
                "-w=WorldA",
                "-p=PlayerA",
                "0'00",
                "0'00",
                "0",
                "!",
                "R",
                "Note text",
            ]
        )
        lines = [line for line in cli.run_cli(args)]
        self.assertTrue(len(lines) == 1)
        self.assertEqual(lines[0].split("|")[-1].strip(), "!:R;Note text")
