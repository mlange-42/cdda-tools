import unittest

import cdda_tools


class TestJson(unittest.TestCase):
    def test_read_game_data(self):
        data = cdda_tools.game.read_game_data("./tests/test_data")
        self.assertTrue(isinstance(data, dict))
        self.assertTrue(len(data) > 0)

    def test_read_game_data_partial(self):
        data = cdda_tools.game.read_game_data("./tests/test_data", ["skill"])
        self.assertTrue(isinstance(data, dict))
        self.assertEqual(len(data), 1)
