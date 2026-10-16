import io
import sys
import tarfile
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from prepare_update import extract_snapshot


def archive(name, kind=tarfile.REGTYPE):
    buffer = io.BytesIO()
    with tarfile.open(fileobj=buffer, mode='w') as output:
        item = tarfile.TarInfo(name)
        item.type = kind
        item.size = 4 if kind == tarfile.REGTYPE else 0
        output.addfile(item, io.BytesIO(b'test') if item.size else None)
    return buffer.getvalue()


class SnapshotTests(unittest.TestCase):
    def setUp(self):
        scratch = ROOT / 'work'
        scratch.mkdir(exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(dir=scratch)
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name)
        self.assertTrue(self.path.resolve().is_relative_to(scratch.resolve()))

    def test_preserves_regular_snapshot_without_touching_existing_destination(self):
        dest = self.path / 'candidate'
        extract_snapshot(archive('pstack/skills/example/SKILL.md'), dest)
        self.assertEqual((dest / 'pstack/skills/example/SKILL.md').read_bytes(), b'test')
        with self.assertRaises(FileExistsError):
            extract_snapshot(archive('pstack/other'), dest)

    def test_rejects_traversal_links_and_windows_drive_paths_before_writing(self):
        cases = [('pstack/../../escape', tarfile.REGTYPE), ('C:/escape', tarfile.REGTYPE),
                 ('pstack/link', tarfile.SYMTYPE), ('pstack/hardlink', tarfile.LNKTYPE),
                 ('/pstack/absolute', tarfile.REGTYPE), ('pstack/..\\escape', tarfile.REGTYPE)]
        for index, (name, kind) in enumerate(cases):
            with self.subTest(name=name):
                destination = self.path / str(index)
                with self.assertRaises(ValueError):
                    extract_snapshot(archive(name, kind), destination)
                self.assertFalse(destination.exists())
