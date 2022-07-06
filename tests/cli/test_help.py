import shutil
import tempfile
import unittest

from cdda_tools import cli


class TestHelp(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        shutil.unpack_archive("tests/test_data/save.tar.gz", self.test_dir)

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_help(self):
        with self.assertRaises(SystemExit):
            _args = cli.parse_args(
                [
                    f"-d={self.test_dir}",
                    "-h",
                ]
            )

    def test_missing_command(self):
        with self.assertRaises(SystemExit):
            _args = cli.parse_args(
                [
                    f"-d={self.test_dir}",
                ]
            )
