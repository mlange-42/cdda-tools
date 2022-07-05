import gzip
import shutil
import tempfile
import unittest

from cdda_tools import cli


class TestCopyPlayer(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        shutil.unpack_archive("tests/test_data/save.tar.gz", self.test_dir)

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_copy_player(self):
        args = cli.parse_args([f"-d={self.test_dir}", "copy-player", "-w=WorldA", "-p=PlayerA",
                               "-w2=WorldB", "-p2=PlayerB"])
        cli.run_cli(args)
