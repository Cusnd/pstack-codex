"""Publish verified main packages without moving tags or replacing release assets.

Run only in the release job after both platform validators succeed. Unit tests
inject an in-memory API; importing this module never reads a token or publishes.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

from package import build
from validate import ROOT

REPOSITORY = 'Cusnd/pstack-codex'
API_ROOT = f'https://api.github.com/repos/{REPOSITORY}'
UPLOAD_ROOT = f'https://uploads.github.com/repos/{REPOSITORY}/releases/'


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise RuntimeError('Unexpected API redirect; refusing to forward authorization')


class GitHub:
    def __init__(self, token):
        if not token:
            raise ValueError('Missing job-scoped GITHUB_TOKEN')
        self.token = token
        # Retain the runner's inherited proxy and TLS configuration.
        self.opener = urllib.request.build_opener(NoRedirect())

    def request(self, method, path, data=None, content_type=None):
        url = API_ROOT + path if path.startswith('/') else path
        if not (url.startswith(API_ROOT + '/') or url.startswith(UPLOAD_ROOT)):
            raise ValueError('Unexpected GitHub API destination')
        payload = data if isinstance(data, bytes) else (json.dumps(data).encode() if data is not None else None)
        request = urllib.request.Request(url, data=payload, method=method, headers={
            'Authorization': f'Bearer {self.token}', 'Accept': 'application/vnd.github+json',
            'X-GitHub-Api-Version': '2022-11-28', 'User-Agent': 'pstack-codex-release',
            'Content-Type': content_type or 'application/json',
        })
        try:
            with self.opener.open(request, timeout=90) as response:
                return json.load(response)
        except urllib.error.HTTPError as exc:
            if method == 'GET' and exc.code == 404:
                return None
            # Do not echo request headers, tokens, or arbitrary response bodies.
            raise RuntimeError(f'GitHub {method} {urllib.parse.urlsplit(url).path}: HTTP {exc.code}') from None

    def all(self, path):
        records = []
        for page in range(1, 101):
            batch = self.request('GET', f'{path}?per_page=100&page={page}')
            if not isinstance(batch, list):
                raise ValueError(f'Cannot list {path}')
            records.extend(batch)
            if len(batch) < 100:
                return records
        raise ValueError('Pagination limit exceeded; refusing an incomplete release inventory')


def git(root, *args):
    return subprocess.check_output(['git', '-C', str(root), *args], text=True).strip()


def context(root, env):
    if (env.get('GITHUB_ACTIONS') != 'true' or env.get('GITHUB_REPOSITORY') != REPOSITORY
            or env.get('GITHUB_EVENT_NAME') != 'push' or env.get('GITHUB_REF') != 'refs/heads/main'):
        raise ValueError('Publication is restricted to this repository main push workflow')
    commit = env.get('GITHUB_SHA', '')
    if not re.fullmatch(r'[0-9a-f]{40}', commit) or git(root, 'rev-parse', 'HEAD') != commit:
        raise ValueError('Checkout does not match the validated workflow commit')
    if git(root, 'status', '--porcelain', '--untracked-files=normal'):
        raise ValueError('Publication requires a clean checkout')
    return commit


def tag_commit(api, tag):
    ref = api.request('GET', '/git/ref/tags/' + tag)
    if ref is None:
        return None
    obj = ref['object']
    for _ in range(8):
        if obj['type'] == 'commit':
            return obj['sha']
        if obj['type'] != 'tag':
            break
        obj = api.request('GET', '/git/tags/' + obj['sha'])['object']
    raise ValueError('Release tag does not resolve to a commit')


def verify_asset(asset, data):
    if (asset.get('state') != 'uploaded' or asset.get('size') != len(data)
            or asset.get('digest') != 'sha256:' + hashlib.sha256(data).hexdigest()):
        raise ValueError(f"Release asset conflict or missing digest: {asset.get('name')}")


def release_assets(api, release_id, expected, complete=False):
    assets = api.all(f'/releases/{release_id}/assets')
    names = [asset['name'] for asset in assets]
    if len(names) != len(set(names)) or set(names) - set(expected):
        raise ValueError('Duplicate or unexpected release assets; nothing will be overwritten')
    for asset in assets:
        verify_asset(asset, expected[asset['name']])
    if complete and set(names) != set(expected):
        raise ValueError('Published release is missing assets; manual reconciliation required')
    return set(names)


def publish(api, commit, version, expected, body, is_ancestor):
    if not re.fullmatch(r'\d+\.\d+\.\d+(?:-(?:alpha|beta|rc)\.\d+)?', version):
        raise ValueError('Unsupported release version')
    tag = 'v' + version
    prerelease = '-' in version
    main = api.request('GET', '/git/ref/heads/main')['object']['sha']
    if main != commit:
        return {'outcome': 'superseded', 'commit': commit, 'main': main}
    releases = [item for item in api.all('/releases') if item['tag_name'] == tag]
    if len(releases) > 1:
        raise ValueError('Multiple releases share the version tag')
    release = releases[0] if releases else None
    target = tag_commit(api, tag)
    if release and not release['draft']:
        if not target or not is_ancestor(target, commit) or release['prerelease'] != prerelease:
            raise ValueError('Existing release tag or prerelease classification conflicts')
        release_assets(api, release['id'], expected, complete=True)
        return {'outcome': 'already_published', 'url': release['html_url'], 'tag': tag, 'commit': target}
    if target is not None and target != commit:
        raise ValueError('Existing tag points elsewhere; refusing to move it')
    if release and (release['target_commitish'] != commit or release['prerelease'] != prerelease):
        raise ValueError('Existing draft has a different target or prerelease classification')
    if release is None:
        release = api.request('POST', '/releases', {
            'tag_name': tag, 'target_commitish': commit, 'name': tag, 'body': body,
            'draft': True, 'prerelease': prerelease, 'make_latest': 'false',
        })
    present = release_assets(api, release['id'], expected)
    upload_url = release['upload_url'].split('{', 1)[0]
    if upload_url != f"{UPLOAD_ROOT}{release['id']}/assets":
        raise ValueError('Unexpected asset upload URL')
    for name, data in expected.items():
        if name not in present:
            asset = api.request('POST', upload_url + '?' + urllib.parse.urlencode({'name': name}),
                                data, 'application/zip' if name.endswith('.zip') else 'text/plain')
            verify_asset(asset, data)
    release_assets(api, release['id'], expected, complete=True)
    # A newer main push must publish its own validated source, not this stale job.
    if api.request('GET', '/git/ref/heads/main')['object']['sha'] != commit:
        return {'outcome': 'superseded_draft', 'url': release['html_url'], 'commit': commit}
    target = tag_commit(api, tag)
    if target is None:
        api.request('POST', '/git/refs', {'ref': 'refs/tags/' + tag, 'sha': commit})
    if tag_commit(api, tag) != commit:
        raise ValueError('Tag changed before publication; refusing to publish')
    result = api.request('PATCH', f"/releases/{release['id']}", {
        'draft': False, 'prerelease': prerelease, 'make_latest': 'false' if prerelease else 'true',
    })
    if result['draft'] or result['prerelease'] != prerelease or tag_commit(api, tag) != commit:
        raise ValueError('Published release verification failed')
    release_assets(api, release['id'], expected, complete=True)
    return {'outcome': 'published', 'url': result['html_url'], 'tag': tag, 'commit': commit}


def artifacts(root, info):
    archive = Path(info['archive'])
    data = archive.read_bytes()
    for platform in ('ubuntu-latest', 'windows-latest'):
        directory = root / 'work/verified-packages' / ('package-' + platform)
        if sorted(path.name for path in directory.iterdir()) != [archive.name]:
            raise ValueError(f'Unexpected {platform} package artifacts')
        if (directory / archive.name).read_bytes() != data:
            raise ValueError(f'{platform} package differs from the validated release build')
    return {archive.name: data, 'SHA256SUMS': f"{info['sha256']}  {archive.name}\n".encode()}


def main():
    commit = context(ROOT, os.environ)
    manifest = json.loads((ROOT / 'plugins/pstack-codex/plugin.json').read_text(encoding='utf-8'))
    version = manifest['version']
    info = build(ROOT / 'dist' / f'pstack-codex-{version}.zip')
    expected = artifacts(ROOT, info)
    lock = json.loads((ROOT / 'upstream.lock.json').read_text(encoding='utf-8'))
    changelog = (ROOT / 'CHANGELOG.md').read_text(encoding='utf-8')
    heading = '## ' + version + ' '
    if heading not in changelog:
        raise ValueError('Missing version-specific changelog entry')
    notes = changelog.split(heading, 1)[1].split('\n## ', 1)[0].split('\n', 1)[1].strip()
    body = (f"{notes}\n\nValidated source: `{commit}`.\n"
            f"Upstream pstack {lock['version']}: commit `{lock['commit']}`, tree `{lock['tree']}`.\n\n"
            f"Source key: `pstack:{lock['tree']}`.\n"
            'Linux and Windows validators, Python/Bun tests, typecheck, and deterministic ZIP checks passed. '
            'The two platform packages match byte for byte. Live macOS/desktop workflows and personal installation '
            'are not certified by these checks.\n\n'
            'MIT; original pstack copyright Lauren Tan. No installed plugin caches are changed.\n\n'
            f"SHA-256: `{info['sha256']}`. See `SHA256SUMS`.\n"
            f"CI: https://github.com/{REPOSITORY}/actions/runs/{os.environ['GITHUB_RUN_ID']}\n")
    api = GitHub(os.environ.get('GITHUB_TOKEN'))
    def is_ancestor(old, new):
        return subprocess.run(['git', '-C', str(ROOT), 'merge-base', '--is-ancestor', old, new],
                              check=False).returncode == 0
    result = publish(api, commit, version, expected, body, is_ancestor)
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
