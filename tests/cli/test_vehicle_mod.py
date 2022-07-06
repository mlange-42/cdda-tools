import json
import shutil
import tempfile
import unittest

from cdda_tools import cli


class TestVehicleMod(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        shutil.unpack_archive("tests/test_data/save.tar.gz", self.test_dir)

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_vehicle_mod(self):
        args = cli.parse_args(
            [
                f"-d={self.test_dir}",
                "vehicle-mod",
                "-w=WorldA",
                "-v=SourceCar",
                "--id=my_test_vehicle",
            ]
        )
        lines = [line for line in cli.run_cli(args)]
        self.assertEqual(len(lines), 1)

        obj = json.loads(lines[0])
        self.assertEqual(obj["id"], "my_test_vehicle")
        self.assertEqual(obj["type"], "vehicle")
        self.assertEqual(obj["name"], "SourceCar")
        self.assertTrue(len(obj["parts"]) > 0)
