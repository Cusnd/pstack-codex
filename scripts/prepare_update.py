"""Prepare a pinned upstream snapshot for review without advancing accepted state."""
from __future__ import annotations

import io
import json
import os
import subprocess
import tarfile
import tempfile
from pathlib import Path, PurePosixPath

from probe_upstream import ROOT, probe, sha


def git(repo: Path, *args: str) -> bytes:
    result = subprocess.run(['git', '-C', str(repo), *args], capture_output=True, check=False)
    if result.returncode:
        raise RuntimeError(result.stderr.decode('utf-8', errors='replace').strip())
    return result.stdout


def extract_snapshot(data: bytes, destination: Path):
    """Only regular files and directories from the pstack subtree are accepted."""
    with tarfile.open(fileobj=io.BytesIO(data)) as archive:
        members = archive.getmembers()
        for member in members:
            path = PurePosixPath(member.name)
            if path.is_absolute() or '..' in path.parts or not path.parts or path.parts[0] != 'pstack':
                raise ValueError(f'Unexpected archive path: {member.name}')
            if '\\' in member.name or ':' in member.name or not (member.isdir() or member.isfile()):
                raise ValueError(f'Unsupported archive entry: {member.name}')
        destination.mkdir(parents=True, exist_ok=False)
        for member in members:
            target = destination.joinpath(*PurePosixPath(member.name).parts)
            if member.isdir():
                target.mkdir(parents=True, exist_ok=True)
            else:
                target.parent.mkdir(parents=True, exist_ok=True)
                with archive.extractfile(member) as source:
                    target.write_bytes(source.read())
                target.chmod(member.mode & 0o777)


def verify_candidate(candidate: Path, receipt: dict, expected: dict, data: bytes, delta: bytes):
    """Reuse only a complete receipt, patch, and exact pinned source snapshot."""
    for key, value in expected.items():
        if key != 'candidate_directory' and receipt.get(key) != value:
            raise ValueError(f'Existing candidate receipt mismatch: {key}')
    if candidate.is_symlink():
        raise ValueError('Candidate directory must not be a symlink')
    with tarfile.open(fileobj=io.BytesIO(data)) as archive:
        members = {member.name.rstrip('/'): member for member in archive.getmembers()}
        actual = {path.relative_to(candidate).as_posix(): path for path in candidate.rglob('*')}
        if set(actual) != set(members) | {'receipt.json', 'upstream.patch'}:
            raise ValueError('Existing candidate is incomplete or contains unexpected files')
        if any(path.is_symlink() for path in actual.values()):
            raise ValueError('Existing candidate contains a symlink')
        for name, member in members.items():
            path = actual[name]
            if member.isdir():
                matches = path.is_dir()
            elif member.isfile():
                matches = path.is_file() and path.read_bytes() == archive.extractfile(member).read()
                if os.name != 'nt':
                    matches = matches and (path.stat().st_mode & 0o111) == (member.mode & 0o111)
            else:
                matches = False
            if not matches:
                raise ValueError(f'Existing candidate source mismatch: {name}')
    if (candidate / 'upstream.patch').read_bytes() != delta:
        raise ValueError('Existing candidate patch differs from the pinned source diff')


def prepare(root: Path = ROOT) -> dict:
    lock = json.loads((root / 'upstream.lock.json').read_text(encoding='utf-8'))
    result = probe(lock)
    if not result['changed']:
        return {'ok': True, **result, 'prepared': False}
    candidate = root / 'work/candidates' / result['candidate_tree']
    existing = None
    if candidate.is_symlink():
        raise ValueError('Candidate directory must not be a symlink')
    if candidate.exists():
        receipt_path = candidate / 'receipt.json'
        if not receipt_path.is_file() or receipt_path.is_symlink():
            raise ValueError('Existing candidate is incomplete; preserve it for inspection')
        existing = json.loads(receipt_path.read_text(encoding='utf-8'))
        if not isinstance(existing, dict) or existing.get('candidate_tree') != result['candidate_tree']:
            raise ValueError('Existing candidate receipt does not identify this source tree')
        # Unrelated upstream commits can move main without changing pstack.
        result['candidate_commit'] = sha(existing.get('candidate_commit'))
    cache = root / 'work/upstream-git'
    cache.mkdir(parents=True, exist_ok=True)
    if not (cache / '.git').exists():
        git(cache, 'init')
        git(cache, 'remote', 'add', 'origin', lock['repository'])
    if git(cache, 'remote', 'get-url', 'origin').decode().strip() != lock['repository']:
        raise ValueError('Upstream cache remote does not match the scoped source')
    git(cache, 'fetch', '--no-tags', 'origin', result['candidate_commit'], result['accepted_commit'])
    observed = git(cache, 'rev-parse', result['candidate_commit'] + ':pstack').decode().strip()
    if observed != result['candidate_tree']:
        raise ValueError('Fetched subtree does not match the pinned detection result')
    data = git(cache, 'archive', '--format=tar', result['candidate_commit'], 'pstack')
    delta = git(cache, 'diff', '--no-ext-diff', '--binary', result['accepted_commit'], result['candidate_commit'], '--', 'pstack')
    with tarfile.open(fileobj=io.BytesIO(data)) as archive:
        version = json.load(archive.extractfile('pstack/.cursor-plugin/plugin.json'))['version']
    receipt = {'ok': True, **result, 'prepared': True, 'candidate_directory': str(candidate),
               'proposed_lock': {**lock, 'commit': result['candidate_commit'], 'tree': observed, 'version': version},
               'accepted_lock_modified': False}
    if existing is not None:
        verify_candidate(candidate, existing, receipt, data, delta)
        return {**receipt, 'reused': True}
    candidate.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='.prepare-', dir=candidate.parent) as scratch:
        staged = Path(scratch) / 'candidate'
        extract_snapshot(data, staged)
        (staged / 'upstream.patch').write_bytes(delta)
        (staged / 'receipt.json').write_text(json.dumps(receipt, indent=2) + '\n', encoding='utf-8')
        try:
            staged.rename(candidate)
        except OSError:
            if not candidate.is_dir() or candidate.is_symlink():
                raise
            existing = json.loads((candidate / 'receipt.json').read_text(encoding='utf-8'))
            verify_candidate(candidate, existing, receipt, data, delta)
            return {**receipt, 'reused': True}
    return {**receipt, 'reused': False}


if __name__ == '__main__':
    try:
        print(json.dumps(prepare(), indent=2))
    except Exception as exc:
        print(json.dumps({'ok': False, 'error': str(exc), 'accepted_lock_modified': False}))
        raise SystemExit(2)
