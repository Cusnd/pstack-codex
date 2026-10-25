import hashlib
import json
import sys
import tempfile
import unittest
import urllib.error
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import release

SHA = '1' * 40
OTHER = '2' * 40
VERSION = '0.1.0-alpha.2'
EXPECTED = {'pstack-codex-0.1.0-alpha.2.zip': b'package', 'SHA256SUMS': b'checksum\n'}


class MemoryGitHub:
    def __init__(self):
        self.main = SHA
        self.tag = None
        self.releases = []
        self.assets = []
        self.writes = []
        self.fail_upload = False
        self.move_main_on_upload = False

    def all(self, path):
        return list(self.releases if path == '/releases' else self.assets)

    def request(self, method, path, data=None, content_type=None):
        if method == 'GET':
            if path == '/git/ref/heads/main':
                return {'object': {'type': 'commit', 'sha': self.main}}
            if path.startswith('/git/ref/tags/'):
                return {'object': {'type': 'commit', 'sha': self.tag}} if self.tag else None
        self.writes.append((method, path, data))
        if method == 'POST' and path == '/releases':
            item = {**data, 'id': 1, 'html_url': 'https://github.com/Cusnd/pstack-codex/releases/tag/v' + VERSION,
                    'upload_url': release.UPLOAD_ROOT + '1/assets{?name,label}'}
            self.releases.append(item)
            return item
        if method == 'POST' and path.startswith(release.UPLOAD_ROOT):
            if self.fail_upload:
                self.fail_upload = False
                raise RuntimeError('interrupted upload')
            name = release.urllib.parse.parse_qs(release.urllib.parse.urlsplit(path).query)['name'][0]
            asset = {'name': name, 'size': len(data), 'state': 'uploaded',
                     'digest': 'sha256:' + hashlib.sha256(data).hexdigest()}
            self.assets.append(asset)
            if self.move_main_on_upload:
                self.main = OTHER
            return asset
        if method == 'POST' and path == '/git/refs':
            if self.tag:
                raise RuntimeError('tag already exists')
            self.tag = data['sha']
            return {'object': {'sha': self.tag}}
        if method == 'PATCH' and path == '/releases/1':
            self.releases[0].update(data)
            return self.releases[0]
        raise AssertionError((method, path))


class ReleaseTests(unittest.TestCase):
    def setUp(self):
        self.api = MemoryGitHub()

    def publish(self, version=VERSION, commit=SHA):
        return release.publish(self.api, commit, version, EXPECTED, 'notes', lambda old, new: True)

    def test_draft_upload_verify_tag_then_publish_prerelease(self):
        result = self.publish()
        self.assertEqual(result['outcome'], 'published')
        self.assertEqual(self.api.tag, SHA)
        self.assertFalse(self.api.releases[0]['draft'])
        self.assertTrue(self.api.releases[0]['prerelease'])
        self.assertEqual(self.api.releases[0]['make_latest'], 'false')
        self.assertEqual([entry[0] for entry in self.api.writes], ['POST'] * 4 + ['PATCH'])
        self.assertTrue(self.api.writes[0][2]['draft'])

    def test_stable_version_is_not_prerelease(self):
        self.publish(version='1.0.0')
        self.assertFalse(self.api.releases[0]['prerelease'])
        self.assertEqual(self.api.releases[0]['make_latest'], 'true')

    def test_published_rerun_does_not_write(self):
        self.publish()
        self.api.writes.clear()
        self.assertEqual(self.publish()['outcome'], 'already_published')
        self.assertEqual(self.api.writes, [])

    def test_documentation_only_new_commit_is_noop(self):
        self.publish()
        self.api.main = OTHER
        self.api.writes.clear()
        self.assertEqual(self.publish(commit=OTHER)['outcome'], 'already_published')
        self.assertEqual(self.api.writes, [])

    def test_published_nonancestor_tag_rejected(self):
        self.publish()
        self.api.writes.clear()
        with self.assertRaisesRegex(ValueError, 'conflicts'):
            release.publish(self.api, SHA, VERSION, EXPECTED, '', lambda a, b: False)
        self.assertEqual(self.api.writes, [])

    def test_interrupted_draft_resumes_without_duplicate_release(self):
        self.api.fail_upload = True
        with self.assertRaisesRegex(RuntimeError, 'interrupted'):
            self.publish()
        self.assertTrue(self.api.releases[0]['draft'])
        self.assertIsNone(self.api.tag)
        self.assertEqual(self.publish()['outcome'], 'published')
        self.assertEqual(len(self.api.releases), 1)
        self.assertEqual(len(self.api.assets), 2)

    def test_existing_draft_assets_reused(self):
        self.publish()
        self.api.releases[0]['draft'] = True
        self.api.writes.clear()
        self.publish()
        self.assertEqual([write[0] for write in self.api.writes], ['PATCH'])

    def test_tag_collision_never_overwritten(self):
        self.api.tag = OTHER
        with self.assertRaisesRegex(ValueError, 'refusing to move'):
            self.publish()
        self.assertEqual(self.api.writes, [])

    def test_different_draft_target_rejected(self):
        self.publish()
        self.api.tag = None
        self.api.releases[0].update(draft=True, target_commitish=OTHER)
        self.api.writes.clear()
        with self.assertRaisesRegex(ValueError, 'different target'):
            self.publish()
        self.assertEqual(self.api.writes, [])

    def test_duplicate_release_rejected(self):
        self.publish()
        self.api.releases *= 2
        self.api.writes.clear()
        with self.assertRaisesRegex(ValueError, 'Multiple releases'):
            self.publish()
        self.assertEqual(self.api.writes, [])

    def test_missing_changed_duplicate_and_extra_assets_fail_closed(self):
        for kind in ('missing', 'changed', 'digest', 'extra', 'duplicate'):
            with self.subTest(kind=kind):
                self.api = MemoryGitHub()
                self.publish()
                if kind == 'missing':
                    self.api.assets.pop()
                elif kind == 'changed':
                    self.api.assets[0]['size'] += 1
                elif kind == 'digest':
                    self.api.assets[0]['digest'] = None
                elif kind == 'extra':
                    self.api.assets.append({'name': 'unexpected'})
                else:
                    self.api.assets.append(self.api.assets[0])
                self.api.writes.clear()
                with self.assertRaises(ValueError):
                    self.publish()
                self.assertEqual(self.api.writes, [])

    def test_new_main_before_start_skips_all_writes(self):
        self.api.main = OTHER
        self.assertEqual(self.publish()['outcome'], 'superseded')
        self.assertEqual(self.api.writes, [])

    def test_new_main_during_upload_keeps_draft(self):
        self.api.move_main_on_upload = True
        self.assertEqual(self.publish()['outcome'], 'superseded_draft')
        self.assertTrue(self.api.releases[0]['draft'])
        self.assertIsNone(self.api.tag)

    def test_invalid_versions_rejected_before_network(self):
        for version in ('../main', '1.0', 'v1.0.0', '1.0.0-custom', '1.0.0+unsafe'):
            with self.assertRaises(ValueError):
                self.publish(version=version)
        self.assertEqual(self.api.writes, [])

    def test_context_rejects_forks_prs_tags_dirty_or_wrong_checkout(self):
        env = dict(GITHUB_ACTIONS='true', GITHUB_REPOSITORY=release.REPOSITORY,
                   GITHUB_EVENT_NAME='push', GITHUB_REF='refs/heads/main', GITHUB_SHA=SHA)
        for key, value in [('GITHUB_ACTIONS', 'false'), ('GITHUB_REPOSITORY', 'other/fork'),
                           ('GITHUB_EVENT_NAME', 'pull_request'), ('GITHUB_REF', 'refs/tags/v1.0.0'),
                           ('GITHUB_SHA', 'bad')]:
            with self.subTest(key=key), self.assertRaises(ValueError):
                release.context(ROOT, {**env, key: value})
        with patch('release.git', side_effect=[SHA, 'dirty']), self.assertRaises(ValueError):
            release.context(ROOT, env)
        with patch('release.git', return_value=OTHER), self.assertRaises(ValueError):
            release.context(ROOT, env)
        with patch('release.git', side_effect=[SHA, '']):
            self.assertEqual(release.context(ROOT, env), SHA)

    def test_both_platform_packages_must_match(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            archive = root / 'package.zip'
            archive.write_bytes(b'bytes')
            info = {'archive': str(archive), 'sha256': hashlib.sha256(b'bytes').hexdigest()}
            for platform in ('ubuntu-latest', 'windows-latest'):
                path = root / 'work/verified-packages' / ('package-' + platform)
                path.mkdir(parents=True)
                (path / archive.name).write_bytes(b'bytes')
            self.assertEqual(release.artifacts(root, info)[archive.name], b'bytes')
            (path / archive.name).write_bytes(b'corrupt')
            with self.assertRaisesRegex(ValueError, 'differs'):
                release.artifacts(root, info)

    def test_http_permission_error_is_not_absence(self):
        api = release.GitHub('test-token-not-a-real-credential')
        for status in (401, 403, 429, 500):
            error = urllib.error.HTTPError(release.API_ROOT, status, 'failure', {}, None)
            with patch.object(api.opener, 'open', side_effect=error), self.assertRaises(RuntimeError):
                api.request('GET', '/releases')
        error = urllib.error.HTTPError(release.API_ROOT, 404, 'missing', {}, None)
        with patch.object(api.opener, 'open', side_effect=error):
            self.assertIsNone(api.request('GET', '/git/ref/tags/v1.0.0'))
        with self.assertRaises(ValueError):
            api.request('POST', 'https://example.invalid/upload', b'bytes')

    def test_all_pages_are_inspected(self):
        api = release.GitHub('test-token-not-a-real-credential')
        with patch.object(api, 'request', side_effect=[[{}] * 100, [{'id': 101}]]) as request:
            self.assertEqual(len(api.all('/releases')), 101)
            self.assertIn('page=2', request.call_args.args[1])


if __name__ == '__main__':
    unittest.main()
