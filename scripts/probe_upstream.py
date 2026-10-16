"""Read-only pinned subtree comparison. Never changes the accepted source lock."""
from __future__ import annotations

import argparse
import json
import re
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
API = 'https://api.github.com/repos/cursor/plugins'


def sha(value: object) -> str:
    if not isinstance(value, str) or not re.fullmatch(r'[0-9a-f]{40}', value):
        raise ValueError('expected a full Git object SHA')
    return value


def request_json(url: str) -> dict:
    request = urllib.request.Request(url, headers={
        'Accept': 'application/vnd.github+json',
        'User-Agent': 'pstack-codex-upstream-probe',
        'X-GitHub-Api-Version': '2022-11-28',
    })
    with urllib.request.urlopen(request, timeout=30) as response:
        payload = json.load(response)
    if not isinstance(payload, dict):
        raise ValueError('expected a JSON object from GitHub')
    return payload


def probe(lock: dict, fetch=request_json) -> dict:
    if lock['repository'] != 'https://github.com/cursor/plugins' or lock['path'] != 'pstack':
        raise ValueError('this probe is scoped to cursor/plugins:pstack')
    accepted_tree = sha(lock['tree'])
    accepted_commit = sha(lock['commit'])
    commit = fetch(API + '/commits/main')
    candidate_commit = sha(commit['sha'])
    root_tree = sha(commit['commit']['tree']['sha'])
    listing = fetch(API + '/git/trees/' + root_tree)
    if listing.get('truncated') is not False or sha(listing['sha']) != root_tree:
        raise ValueError('root tree response is incomplete or does not match the pinned commit')
    entries = [entry for entry in listing['tree'] if entry['path'] == 'pstack']
    if len(entries) != 1 or entries[0]['type'] != 'tree':
        raise ValueError('pstack is missing or is no longer a directory; manual review required')
    candidate_tree = sha(entries[0]['sha'])
    return {
        'changed': candidate_tree != accepted_tree,
        'accepted_commit': accepted_commit,
        'accepted_tree': accepted_tree,
        'candidate_commit': candidate_commit,
        'candidate_tree': candidate_tree,
        'idempotency_key': 'pstack:' + candidate_tree,
    }


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--lock', type=Path, default=ROOT / 'upstream.lock.json')
    args = parser.parse_args()
    try:
        result = probe(json.loads(args.lock.read_text(encoding='utf-8')))
    except Exception as exc:
        print(json.dumps({'ok': False, 'error': str(exc)}))
        raise SystemExit(2)
    print(json.dumps({'ok': True, **result}, indent=2))
