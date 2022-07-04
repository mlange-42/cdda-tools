import shutil
import tempfile
import unittest
from os import path

import cdda_tools


class TestJson(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_read_json(self):
        temp_path = path.join(self.test_dir, "test.json")
        f = open(temp_path, "w")
        f.write('{"a": 1, "b": "Hallo"}')
        f.close()

        data = cdda_tools.json_utils.read_json(temp_path)
        self.assertEqual(data, {"a": 1, "b": "Hallo"})

    def test_write_json(self):
        temp_path = path.join(self.test_dir, "test.json")
        data = {"a": 1, "b": "Hallo"}
        cdda_tools.json_utils.write_json(data, temp_path)

        data2 = cdda_tools.json_utils.read_json(temp_path)
        self.assertEqual(data, data2)
        self.assertEqual(data, {"a": 1, "b": "Hallo"})
        self.assertEqual(data2, {"a": 1, "b": "Hallo"})


if __name__ == "__main__":
    unittest.main
