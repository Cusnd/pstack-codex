import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def module(name, relative):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative)
    result = importlib.util.module_from_spec(spec)
    sys.modules[name] = result
    spec.loader.exec_module(result)
    return result


audit = module('worktree_audit', 'plugins/pstack-codex/skills/poteto-mode/scripts/worktree-audit.py')
log = module('decision_log', 'plugins/pstack-codex/skills/show-me-your-work/scripts/log.py')


class PortableToolTests(unittest.TestCase):
    def setUp(self):
        scratch = ROOT / 'work'
        scratch.mkdir(exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(prefix='portable tools ', dir=scratch)
        self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name).resolve()
        self.assertTrue(self.directory.is_relative_to(scratch.resolve()))

    def git(self, repo, *args):
        return subprocess.check_output(['git', '-C', str(repo), '-c', 'user.name=Fixture', '-c', 'user.email=fixture@example.invalid', *args], text=True, stderr=subprocess.STDOUT).strip()

    def test_real_worktree_with_spaces_preserves_untracked_work_and_requires_usage_evidence(self):
        repo = self.directory / 'repo with spaces'
        repo.mkdir()
        self.git(repo, 'init', '-b', 'main')
        (repo / 'file.txt').write_text('base', encoding='utf-8')
        self.git(repo, 'add', 'file.txt')
        self.git(repo, 'commit', '-m', 'fixture')
        wt = self.directory / 'branch with spaces'
        self.git(repo, 'worktree', 'add', '-b', 'feature', str(wt))
        self.git(repo, 'update-ref', 'refs/remotes/origin/feature', 'HEAD')
        rows = audit.audit(repo, 'main', [], {})
        self.assertEqual(len(rows), 1)
        self.assertEqual(Path(rows[0]['worktree']), wt)
        self.assertEqual(rows[0]['bucket'], 'verify-usage')
        activity = {str(wt.resolve()): {'active': False, 'pinned': False, 'source': 'fixture'}}
        rows = audit.audit(repo, 'main', [], activity)
        self.assertEqual(rows[0]['bucket'], 'candidate-for-review')
        (wt / 'important untracked.txt').write_text('retain', encoding='utf-8')
        rows = audit.audit(repo, 'main', [], activity)
        self.assertEqual(rows[0]['bucket'], 'hold-uncommitted')
        self.assertTrue((wt / 'important untracked.txt').exists())

    def test_closed_pr_is_not_merge_proof(self):
        bucket = audit.classify(dirty=False, merged=False,
                                prs=[{'state': 'closed'}], remote='pushed', locked=False,
                                activity={'active': False, 'pinned': False})
        self.assertEqual(bucket, 'review-unmerged')

    def test_append_log_preserves_rows_and_sanitizes_spreadsheet_formulas(self):
        path = self.directory / 'logs with spaces' / 'decisions.tsv'
        log.append_row(path, ['start', '=command()', '+reason\nline', '@evidence\tcell', '-result'])
        log.append_row(path, ['check', 'ok', 'reason', 'proof', 'pass'])
        lines = path.read_text(encoding='utf-8').splitlines()
        self.assertEqual(len(lines), 3)
        self.assertEqual(lines[1].split('\t')[2:], ["'=command()", "'+reason line", "'@evidence cell", "'-result"])
        self.assertEqual(len(lines[2].split('\t')), 6)
        self.assertEqual(sum(line.startswith('ts\t') for line in lines), 1)


if __name__ == '__main__':
    unittest.main()
