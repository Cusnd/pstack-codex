"""Audit Git worktrees without deleting files or scanning personal transcripts."""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import subprocess
from pathlib import Path


def command(args, cwd):
    return subprocess.run(args, cwd=cwd, capture_output=True, encoding='utf-8', errors='replace', check=False)


def git(repo, *args, required=True):
    result = command(['git', '-C', str(repo), *args], repo)
    if required and result.returncode:
        raise RuntimeError(result.stderr.strip() or f'Git command failed: {args[0]}')
    return result


def worktrees(repo):
    records = []
    current = {}
    for field in git(repo, 'worktree', 'list', '--porcelain', '-z').stdout.split('\0'):
        if not field:
            if current:
                records.append(current)
                current = {}
            continue
        key, _, value = field.partition(' ')
        current[key] = value
    if current:
        records.append(current)
    return records


def directory_size(path):
    total = 0
    failures = []
    def onerror(exc):
        failures.append(str(exc))
    for base, dirs, files in os.walk(path, followlinks=False, onerror=onerror):
        dirs[:] = [name for name in dirs if not (Path(base) / name).is_symlink()]
        for name in files:
            entry = Path(base) / name
            try:
                if not entry.is_symlink():
                    total += entry.stat().st_size
            except OSError as exc:
                failures.append(str(exc))
    return total, failures


def classify(*, dirty, merged, prs, remote, locked, activity):
    if locked:
        return 'hold-locked'
    if dirty:
        return 'hold-uncommitted'
    if any(pr['state'] in {'open', 'draft'} for pr in prs):
        return 'hold-open-pr'
    if activity is None or activity.get('active') is not False or activity.get('pinned') is not False:
        return 'verify-usage'
    if remote not in {'pushed', 'detached'}:
        return 'review-unpushed'
    if merged:
        return 'candidate-for-review'
    return 'review-unmerged'


def audit(repo, base, prs, activity):
    records = worktrees(repo)
    result = []
    for entry in records[1:]:
        path = Path(entry['worktree'])
        row = {'worktree': str(path), 'head': entry.get('HEAD'), 'branch': entry.get('branch', '').removeprefix('refs/heads/')}
        if not path.is_dir() or 'prunable' in entry:
            result.append({**row, 'bucket': 'review-missing', 'reason': entry.get('prunable', 'path unavailable')})
            continue
        head = git(path, 'rev-parse', 'HEAD').stdout.strip()
        dirty = bool(git(path, 'status', '--porcelain', '-z', '--untracked-files=all').stdout)
        branch = row['branch']
        matches = [pr for pr in prs if pr['head'] == branch and branch]
        ancestor = git(repo, 'merge-base', '--is-ancestor', head, base, required=False)
        if ancestor.returncode not in {0, 1}:
            raise RuntimeError(ancestor.stderr.strip())
        merged = ancestor.returncode == 0 or any(pr['state'] == 'merged' and pr.get('sha') == head for pr in matches)
        if not branch:
            remote = 'detached'
        else:
            tracking = git(repo, 'rev-parse', '--verify', f'refs/remotes/origin/{branch}', required=False)
            remote = 'no-remote' if tracking.returncode else ('pushed' if tracking.stdout.strip() == head else 'diverged')
        size, failures = directory_size(path)
        last_commit = int(git(path, 'log', '-1', '--format=%ct').stdout.strip())
        activity_record = activity.get(str(path.resolve()))
        bucket = classify(dirty=dirty, merged=merged, prs=matches, remote=remote,
                          locked='locked' in entry, activity=activity_record)
        if failures and bucket == 'candidate-for-review':
            bucket = 'review-incomplete'
        result.append({**row, 'size_bytes': size, 'size_errors': failures, 'last_commit_utc': dt.datetime.fromtimestamp(last_commit, dt.timezone.utc).isoformat(),
                       'merged': merged, 'dirty': dirty, 'remote': remote, 'prs': matches,
                       'last_chat': activity_record, 'bucket': bucket})
    return sorted(result, key=lambda row: row.get('size_bytes', 0), reverse=True)


def forge_prs(repo, forge):
    if forge == 'none':
        return [], 'PR state not requested'
    args = ['gh', 'pr', 'list', '--state', 'all', '--limit', '1000', '--json', 'number,state,headRefName,headRefOid']
    if forge == 'origin':
        args = ['origin', 'pr', 'list', '--author', '@me', '--state', 'all', '--limit', '1000', '--json', 'number,status,headRef']
    try:
        result = command(args, repo)
        if result.returncode:
            return [], f'{forge} PR lookup failed: {result.stderr.strip()}'
        records = json.loads(result.stdout)
        if forge == 'origin':
            return [{'number': pr['number'], 'state': pr['status'].lower(), 'head': pr['headRef']} for pr in records], 'Origin PR head SHA unavailable; squash-merge proof needs separate verification'
        warning = 'PR lookup hit its limit; verify relevant branch PRs separately' if len(records) >= 1000 else None
        return [{'number': pr['number'], 'state': pr['state'].lower(), 'head': pr['headRefName'], 'sha': pr['headRefOid']} for pr in records], warning
    except (OSError, ValueError, KeyError, TypeError) as exc:
        return [], f'{forge} PR lookup unavailable: {exc}'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('repo', nargs='?', type=Path, default=Path.cwd())
    parser.add_argument('-b', '--base')
    parser.add_argument('--forge', choices=['gh', 'origin', 'none'], default='gh')
    parser.add_argument('--activity-index', type=Path, help='Explicit scoped JSON map of absolute worktree paths to active/pinned/last-chat evidence')
    args = parser.parse_args()
    repo = args.repo.resolve()
    base = args.base
    if not base:
        default = git(repo, 'symbolic-ref', '--short', 'refs/remotes/origin/HEAD', required=False).stdout.strip()
        for candidate in [default, 'origin/main', 'origin/master']:
            if candidate and git(repo, 'rev-parse', '--verify', candidate + '^{commit}', required=False).returncode == 0:
                base = candidate
                break
    if not base:
        raise ValueError('No default base is available; pass --base explicitly')
    git(repo, 'rev-parse', '--verify', base + '^{commit}')
    prs, warning = forge_prs(repo, args.forge)
    activity = json.loads(args.activity_index.read_text(encoding='utf-8')) if args.activity_index else {}
    if not isinstance(activity, dict):
        raise ValueError('Activity index must be an object keyed by absolute worktree path')
    if any(not isinstance(value, dict) or not Path(key).is_absolute() for key, value in activity.items()):
        raise ValueError('Every activity entry must map an absolute path to an evidence object')
    rows = audit(repo, base, prs, activity)
    if warning:
        for row in rows:
            if row['bucket'] == 'candidate-for-review':
                row['bucket'] = 'verify-pr-state'
    print(json.dumps({'base': base, 'remote_refs': 'cached; fetch explicitly before relying on merge state',
                      'warning': warning, 'worktrees': rows,
                      'deletion_authorized': False}, indent=2))


if __name__ == '__main__':
    try:
        main()
    except (OSError, RuntimeError, ValueError, KeyError) as exc:
        print(json.dumps({'error': str(exc)}))
        raise SystemExit(1)
