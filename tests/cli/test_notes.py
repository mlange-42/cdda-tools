import shutil
import tempfile
import unittest

from cdda_tools import cli


class TestNotes(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        shutil.unpack_archive("tests/test_data/save.tar.gz", self.test_dir)

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def add_note(self, symbol, color, text):
        args = cli.parse_args(
            [
                f"-d={self.test_dir}",
                "note",
                "-w=WorldA",
                "-p=PlayerA",
                "0'00",
                "0'00",
                "0",
                symbol,
                color,
                text,
            ]
        )
        _lines = [line for line in cli.run_cli(args)]

    def list_notes(self, pattern):
        args = cli.parse_args(
            [
                f"-d={self.test_dir}",
                "notes",
                "-w=WorldA",
                "-p=PlayerA",
                "list",
                pattern,
            ]
        )
        yield from cli.run_cli(args)

    def test_notes_list(self):
        self.add_note("!", "R", "Unique note text")

        lines = [line for line in self.list_notes("*Unique*")]
        self.assertEqual(len(lines), 1)
        self.assertEqual(lines[0].split("|")[-1].strip(), "!:R;Unique note text")

    def test_notes_danger(self):
        self.add_note("!", "R", "Unique note text")

        args = cli.parse_args(
            [
                f"-d={self.test_dir}",
                "notes",
                "-w=WorldA",
                "-p=PlayerA",
                "danger",
                "*Unique*",
                "--radius",
                "5",
            ]
        )
        lines = [line for line in cli.run_cli(args)]
        self.assertEqual(len(lines), 1)
        self.assertEqual(lines[0].split("|")[-1].strip(), "!:R;Unique note text")
        self.assertTrue(lines[0].startswith("!"))

        lines = [line for line in self.list_notes("*Unique*")]
        self.assertEqual(len(lines), 1)
        self.assertEqual(lines[0].split("|")[-1].strip(), "!:R;Unique note text")
        self.assertTrue(lines[0].startswith("!"))

    def test_notes_delete(self):
        self.add_note("!", "R", "Unique note text")

        args = cli.parse_args(
            [
                f"-d={self.test_dir}",
                "notes",
                "-w=WorldA",
                "-p=PlayerA",
                "delete",
                "*Unique*",
            ]
        )
        lines = [line for line in cli.run_cli(args)]
        self.assertEqual(len(lines), 1)
        self.assertEqual(lines[0].split("|")[-1].strip(), "!:R;Unique note text")

        lines = [line for line in self.list_notes("*Unique*")]
        self.assertEqual(len(lines), 0)

    def test_notes_edit(self):
        self.add_note("!", "R", "Unique note text")

        args = cli.parse_args(
            [
                f"-d={self.test_dir}",
                "notes",
                "-w=WorldA",
                "-p=PlayerA",
                "edit",
                "*Unique*",
                "-s",
                "?",
                "-c",
                "y",
                "-t",
                "Changed unique note text",
            ]
        )
        lines = [line for line in cli.run_cli(args)]
        self.assertEqual(len(lines), 3)
        self.assertEqual(lines[0].split("|")[-1].strip(), "!:R;Unique note text")
        self.assertEqual(
            lines[1].split("|")[-1].strip(), "?:y;Changed unique note text"
        )

        lines = [line for line in self.list_notes("*Changed unique*")]
        self.assertEqual(len(lines), 1)
        self.assertEqual(
            lines[0].split("|")[-1].strip(), "?:y;Changed unique note text"
        )

    def test_notes_replace(self):
        self.add_note("!", "R", "Unique note text")

        args = cli.parse_args(
            [
                f"-d={self.test_dir}",
                "notes",
                "-w=WorldA",
                "-p=PlayerA",
                "replace",
                "*Unique*",
                "-r",
                "text",
                "TEXT",
            ]
        )
        lines = [line for line in cli.run_cli(args)]
        self.assertEqual(len(lines), 3)
        self.assertEqual(lines[0].split("|")[-1].strip(), "!:R;Unique note text")
        self.assertEqual(lines[1].split("|")[-1].strip(), "!:R;Unique note TEXT")

        lines = [line for line in self.list_notes("*Unique*")]
        self.assertEqual(len(lines), 1)
        self.assertEqual(lines[0].split("|")[-1].strip(), "!:R;Unique note TEXT")
