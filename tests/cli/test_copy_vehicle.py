import shutil
import tempfile
import unittest

from cdda_tools import cli


class TestCopyVehicle(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        shutil.unpack_archive("tests/test_data/save.tar.gz", self.test_dir)

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_copy_vehicle_dry(self):
        args = cli.parse_args(
            [
                f"-d={self.test_dir}",
                "copy-vehicle",
                "-w=WorldA",
                "-v=SourceCar",
                "-w2=WorldB",
                "-v2=TargetCar",
                "--dry",
            ]
        )
        lines = [line for line in cli.run_cli(args)]
        self.assertTrue(lines[-1].startswith("Successfully"))

    def test_copy_vehicle(self):
        args = cli.parse_args(
            [
                f"-d={self.test_dir}",
                "copy-vehicle",
                "-w=WorldA",
                "-v=SourceCar",
                "-w2=WorldB",
                "-v2=TargetCar",
            ]
        )
        lines = [line for line in cli.run_cli(args)]
        self.assertTrue(lines[-1].startswith("Successfully"))

    def test_copy_vehicle_fail_source(self):
        args = cli.parse_args(
            [
                f"-d={self.test_dir}",
                "copy-vehicle",
                "-w=WorldA",
                "-v=abcdefg",
                "-w2=WorldB",
                "-v2=TargetCar",
            ]
        )
        with self.assertRaises(ValueError):
            _lines = [line for line in cli.run_cli(args)]

    def test_copy_vehicle_fail_target(self):
        args = cli.parse_args(
            [
                f"-d={self.test_dir}",
                "copy-vehicle",
                "-w=WorldA",
                "-v=SourceCar",
                "-w2=WorldB",
                "-v2=abcdefg",
            ]
        )
        with self.assertRaises(ValueError):
            _lines = [line for line in cli.run_cli(args)]
