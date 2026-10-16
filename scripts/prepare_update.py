"""Prepare a pinned upstream snapshot for review without advancing accepted state."""
from __future__ import annotations

import io
import json
import subprocess
import tarfile
from pathlib import Path, PurePosixPath

from probe_upstream import ROOT, probe


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


def prepare() -> dict:
    lock = json.loads((ROOT / 'upstream.lock.json').read_text(encoding='utf-8'))
    result = probe(lock)
    if not result['changed']:
        return {'ok': True, **result, 'prepared': False}
    candidate = ROOT / 'work/candidates' / result['candidate_tree']
    if candidate.exists():
        raise ValueError(f'Candidate directory already exists; inspect and reuse its receipt: {candidate}')
    cache = ROOT / 'work/upstream-git'
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
    extract_snapshot(data, candidate)
    delta = git(cache, 'diff', '--no-ext-diff', '--binary', result['accepted_commit'], result['candidate_commit'], '--', 'pstack')
    (candidate / 'upstream.patch').write_bytes(delta)
    version = json.loads((candidate / 'pstack/.cursor-plugin/plugin.json').read_text(encoding='utf-8'))['version']
    receipt = {'ok': True, **result, 'prepared': True, 'candidate_directory': str(candidate),
               'proposed_lock': {**lock, 'commit': result['candidate_commit'], 'tree': observed, 'version': version},
               'accepted_lock_modified': False}
    (candidate / 'receipt.json').write_text(json.dumps(receipt, indent=2) + '\n', encoding='utf-8')
    return receipt


if __name__ == '__main__':
    try:
        print(json.dumps(prepare(), indent=2))
    except Exception as exc:
        print(json.dumps({'ok': False, 'error': str(exc), 'accepted_lock_modified': False}))
        raise SystemExit(2)
