import copy
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from probe_upstream import probe


class ProbeTests(unittest.TestCase):
    def setUp(self):
        self.lock = {'repository': 'https://github.com/cursor/plugins', 'path': 'pstack',
                     'commit': 'a' * 40, 'tree': 'b' * 40}
        self.commit = {'sha': 'c' * 40, 'commit': {'tree': {'sha': 'd' * 40}}}
        self.tree = {'sha': 'd' * 40, 'truncated': False,
                     'tree': [{'path': 'pstack', 'type': 'tree', 'sha': 'b' * 40}]}
        self.urls = []

    def fetch(self, url):
        self.urls.append(url)
        return copy.deepcopy(self.commit if url.endswith('/commits/main') else self.tree)

    def test_unrelated_commit_does_not_trigger(self):
        original = copy.deepcopy(self.lock)
        result = probe(self.lock, self.fetch)
        self.assertFalse(result['changed'])
        self.assertNotEqual(result['accepted_commit'], result['candidate_commit'])
        self.assertEqual(self.lock, original)
        self.assertTrue(self.urls[1].endswith('/git/trees/' + 'd' * 40))

    def test_changed_subtree_has_stable_deduplication_key(self):
        self.tree['tree'][0]['sha'] = 'e' * 40
        result = probe(self.lock, self.fetch)
        self.assertTrue(result['changed'])
        self.assertEqual(result['idempotency_key'], 'pstack:' + 'e' * 40)
        self.assertEqual(self.lock['tree'], 'b' * 40)

    def test_truncated_missing_replaced_and_mismatched_trees_fail_closed(self):
        variants = [dict(self.tree, truncated=True), dict(self.tree, tree=[]),
                    dict(self.tree, sha='f' * 40),
                    dict(self.tree, tree=[{'path': 'pstack', 'type': 'commit', 'sha': 'b' * 40}])]
        for variant in variants:
            with self.subTest(tree=variant):
                self.tree = variant
                with self.assertRaises(ValueError):
                    probe(self.lock, self.fetch)

    def test_network_failure_is_not_no_change(self):
        def fail(_):
            raise OSError('offline')
        with self.assertRaises(OSError):
            probe(self.lock, fail)


if __name__ == '__main__':
    unittest.main()
