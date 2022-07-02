import unittest

import cdda_tools


class TestNotes(unittest.TestCase):
    def test_notes_tuple(self):
        tup = cdda_tools.commands.notes.note_tuple("!:R;Test text")
        self.assertEqual(tup, ["!", "R", 4])

        tup = cdda_tools.commands.notes.note_tuple("!:lg;Test text")
        self.assertEqual(tup, ["!", "lg", 5])

        tup = cdda_tools.commands.notes.note_tuple("!:lg;Test text")
        self.assertEqual(tup, ["!", "lg", 5])

        tup = cdda_tools.commands.notes.note_tuple("lg;Test text")
        self.assertEqual(tup, ["N", "lg", 3])

        tup = cdda_tools.commands.notes.note_tuple("!:Test text")
        self.assertEqual(tup, ["!", None, 2])

        tup = cdda_tools.commands.notes.note_tuple("R;Test text")
        self.assertEqual(tup, ["N", "R", 2])

        tup = cdda_tools.commands.notes.note_tuple("!")
        self.assertEqual(tup, ["N", None, 0])

    def test_notes_tuple(self):
        note = "!:R;Test text"
        self.assertEqual(_split_merge_note(note), note)

        note = "!:Test text"
        self.assertEqual(_split_merge_note(note), note)


def _split_merge_note(note):
    return cdda_tools.commands.notes.format_note_tuple(
        cdda_tools.commands.notes.note_tuple(note), note
    )


if __name__ == "__main__":
    unittest.main
