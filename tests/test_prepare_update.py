import io
import json
import sys
import tarfile
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import prepare_update
from prepare_update import extract_snapshot, git, prepare


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


class PreparationTests(unittest.TestCase):
    def setUp(self):
        scratch = ROOT / 'work'
        scratch.mkdir(exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(dir=scratch, prefix='prepare test ')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.cache = self.root / 'work/upstream-git'
        self.cache.mkdir(parents=True)
        git(self.cache, 'init')
        git(self.cache, 'config', 'user.name', 'Test')
        git(self.cache, 'config', 'user.email', 'test@example.invalid')
        git(self.cache, 'remote', 'add', 'origin', 'https://github.com/cursor/plugins')
        source = self.cache / 'pstack/.cursor-plugin/plugin.json'
        source.parent.mkdir(parents=True)
        source.write_text('{"version":"0.15.25"}\n')
        self.old = self.commit('baseline')
        self.old_tree = git(self.cache, 'rev-parse', 'HEAD:pstack').decode().strip()
        source.write_text('{"version":"0.15.27"}\n')
        self.new = self.commit('update')
        self.new_tree = git(self.cache, 'rev-parse', 'HEAD:pstack').decode().strip()
        self.lock = {'repository': 'https://github.com/cursor/plugins', 'path': 'pstack',
                     'commit': self.old, 'tree': self.old_tree, 'version': '0.15.25',
                     'adaptation_status': 'alpha'}
        self.lock_path = self.root / 'upstream.lock.json'
        self.lock_path.write_text(json.dumps(self.lock))
        self.result = {'changed': True, 'accepted_commit': self.old, 'accepted_tree': self.old_tree,
                       'candidate_commit': self.new, 'candidate_tree': self.new_tree,
                       'idempotency_key': 'pstack:' + self.new_tree}
        # All repository operations are real; only network detection/fetch are replaced.
        self.addCleanup(patch.stopall)
        patch('prepare_update.probe', side_effect=lambda lock: dict(self.result)).start()
        patch('prepare_update.git', side_effect=lambda repo, *args:
              b'' if args[0] == 'fetch' else git(repo, *args)).start()
        self.candidate = self.root / 'work/candidates' / self.new_tree

    def commit(self, message):
        git(self.cache, 'add', '.')
        git(self.cache, '-c', 'commit.gpgsign=false', 'commit', '-m', message)
        return git(self.cache, 'rev-parse', 'HEAD').decode().strip()

    def test_repeated_preparation_preserves_candidate_and_accepted_lock(self):
        before = self.lock_path.read_bytes()
        first = prepare(self.root)
        receipt = (self.candidate / 'receipt.json').read_bytes()
        second = prepare(self.root)
        self.assertFalse(first['reused'])
        self.assertTrue(second['reused'])
        self.assertEqual(first['proposed_lock'], second['proposed_lock'])
        self.assertEqual(before, self.lock_path.read_bytes())
        self.assertEqual(receipt, (self.candidate / 'receipt.json').read_bytes())

    def test_unrelated_upstream_commit_reuses_original_pinned_candidate(self):
        first = prepare(self.root)
        (self.cache / 'other.txt').write_text('unrelated')
        self.result['candidate_commit'] = self.commit('outside pstack')
        second = prepare(self.root)
        self.assertTrue(second['reused'])
        self.assertEqual(first['candidate_commit'], second['candidate_commit'])

    def test_corrupted_source_patch_and_receipt_are_rejected_without_overwrite(self):
        prepare(self.root)
        for relative in ('pstack/.cursor-plugin/plugin.json', 'upstream.patch', 'receipt.json'):
            path = self.candidate / relative
            original = path.read_bytes()
            path.write_text('{}' if relative == 'receipt.json' else 'corrupt')
            with self.subTest(relative=relative), self.assertRaises(ValueError):
                prepare(self.root)
            self.assertEqual(path.read_text(), '{}' if relative == 'receipt.json' else 'corrupt')
            path.write_bytes(original)

    def test_incomplete_candidate_is_preserved(self):
        self.candidate.mkdir(parents=True)
        (self.candidate / 'interrupted').write_text('keep')
        with self.assertRaisesRegex(ValueError, 'incomplete'):
            prepare(self.root)
        self.assertEqual((self.candidate / 'interrupted').read_text(), 'keep')

    def test_failed_preparation_does_not_publish_a_partial_candidate(self):
        with patch.object(prepare_update, 'extract_snapshot', side_effect=RuntimeError('interrupted')):
            with self.assertRaisesRegex(RuntimeError, 'interrupted'):
                prepare(self.root)
        self.assertFalse(self.candidate.exists())
        self.assertEqual(json.loads(self.lock_path.read_text()), self.lock)

    def test_unchanged_source_creates_no_candidate(self):
        self.result['changed'] = False
        result = prepare(self.root)
        self.assertFalse(result['prepared'])
        self.assertFalse(self.candidate.exists())
