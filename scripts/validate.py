from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

import yaml

SCHEMA = 'https://agent-plugins.org/schemas/1.0.0/plugin.schema.json'
ROOT = Path(__file__).resolve().parents[1]
LEGACY = re.compile(r'~[/\\]\.cursor|subagent_type\s*:|run_in_background\s*:|cloud_base_branch\s*:|api2\.cursor\.sh/automations|claude-opus-[\w.-]+|grok-4\.[\w.-]+|cursor-team-kit')


def read_skill(path: Path) -> tuple[dict, str]:
    text = path.read_text(encoding='utf-8')
    if not text.startswith('---\n'):
        raise ValueError('missing YAML frontmatter')
    _, front, body = text.split('---', 2)
    metadata = yaml.safe_load(front)
    if not isinstance(metadata, dict):
        raise ValueError('frontmatter must be a mapping')
    return metadata, body


def validate(root: Path = ROOT, metadata_only: bool = False) -> list[str]:
    errors = []
    plugin = root / 'plugins/pstack-codex'
    manifest = json.loads((plugin / 'plugin.json').read_text(encoding='utf-8'))
    statuses = json.loads((root / 'adapter/skills.json').read_text(encoding='utf-8'))
    if manifest.get('$schema') != SCHEMA or manifest.get('name') != plugin.name:
        errors.append('plugin manifest schema or identity mismatch')
    if not re.fullmatch(r'\d+\.\d+\.\d+(?:-[0-9A-Za-z.-]+)?(?:\+[0-9A-Za-z.-]+)?', manifest.get('version', '')):
        errors.append('plugin version must be SemVer')
    forbidden = {'skills', 'mcpServers', 'apps', 'interface'} & manifest.keys()
    if forbidden:
        errors.append(f'non-portable root manifest fields: {sorted(forbidden)}')
    interface = manifest.get('extensions', {}).get('com.openai', {}).get('interface', {})
    if len(interface.get('shortDescription', '')) > 30:
        errors.append('plugin shortDescription exceeds 30 characters')
    expected = {p.parent.name for p in (root / 'upstream/pstack/skills').glob('*/SKILL.md')}
    actual = {p.parent.name for p in (plugin / 'skills').glob('*/SKILL.md')}
    if expected != actual or actual != set(statuses):
        errors.append(f'skill inventory mismatch: missing={sorted(expected - actual)}, extra={sorted(actual - expected)}')
    for path in sorted((plugin / 'skills').glob('*/SKILL.md')):
        name = path.parent.name
        try:
            meta, _ = read_skill(path)
            if meta.get('name') != name or not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', name):
                errors.append(f'{name}: invalid or mismatched skill name')
            if not isinstance(meta.get('description'), str) or not meta['description'].strip():
                errors.append(f'{name}: missing description')
            if 'disable-model-invocation' in meta:
                errors.append(f'{name}: invocation policy still uses Cursor metadata')
            original, _ = read_skill(root / 'upstream/pstack/skills' / name / 'SKILL.md')
            expected_implicit = not original.get('disable-model-invocation', False)
            policy = yaml.safe_load((path.parent / 'agents/openai.yaml').read_text(encoding='utf-8'))
            implicit = policy['policy']['allow_implicit_invocation']
            if type(implicit) is not bool or implicit != expected_implicit:
                errors.append(f'{name}: invocation policy differs from upstream')
            status = statuses.get(name, {}).get('status')
            if status not in {'pending', 'adapted', 'deferred'}:
                errors.append(f'{name}: invalid capability status')
            if not metadata_only and status == 'pending':
                errors.append(f'{name}: adaptation pending')
            if status == 'deferred' and not statuses[name].get('reason'):
                errors.append(f'{name}: deferred capability needs a reason')
        except (ValueError, KeyError, TypeError, OSError, yaml.YAMLError) as exc:
            errors.append(f'{name}: {exc}')
    if not metadata_only:
        for path in sorted(plugin.rglob('*')):
            if path.is_symlink():
                errors.append(f'package symlink: {path.relative_to(plugin)}')
            if path.is_file() and path.suffix in {'.md', '.ts', '.js', '.mjs', '.sh'}:
                for number, line in enumerate(path.read_text(encoding='utf-8').splitlines(), 1):
                    if LEGACY.search(line):
                        errors.append(f'{path.relative_to(plugin)}:{number}: unhandled Cursor runtime reference')
        license_text = (plugin / 'LICENSE').read_text(encoding='utf-8')
        if 'Lauren Tan' not in license_text or 'MIT License' not in license_text:
            errors.append('upstream license attribution missing')
    return errors


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--metadata-only', action='store_true')
    args = parser.parse_args()
    problems = validate(metadata_only=args.metadata_only)
    print(json.dumps({'ok': not problems, 'scope': 'metadata' if args.metadata_only else 'release', 'errors': problems}, indent=2))
    raise SystemExit(bool(problems))
