from __future__ import annotations

import argparse
import json
import os
import re
from pathlib import Path

import yaml

SCHEMA = 'https://agent-plugins.org/schemas/1.0.0/plugin.schema.json'
ROOT = Path(__file__).resolve().parents[1]
LEGACY = re.compile(r'~[/\\]\.cursor|subagent_type\s*:|run_in_background\s*:|cloud_base_branch\s*:|api2\.cursor\.sh/automations|claude-opus-[\w.-]+|grok-4\.[\w.-]+|cursor-team-kit')
GENERATED_DIRS = {'node_modules', '__pycache__', '.venv', '.git'}


def package_files(plugin: Path):
    """The same source-only file selection is used by validation and packaging."""
    for base, dirs, files in os.walk(plugin, followlinks=False):
        for name in sorted(dirs):
            path = Path(base) / name
            if name not in GENERATED_DIRS and path.is_symlink():
                yield path
        dirs[:] = sorted(name for name in dirs if name not in GENERATED_DIRS and not (Path(base) / name).is_symlink())
        for name in sorted(files):
            if not name.endswith('.pyc'):
                yield Path(base) / name


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
    try:
        marketplace = json.loads((root / '.agents/plugins/marketplace.json').read_text(encoding='utf-8'))
        entries = marketplace.get('plugins', [])
        if marketplace.get('name') != 'pstack-codex' or len(entries) != 1:
            errors.append('public marketplace identity or inventory mismatch')
        else:
            entry = entries[0]
            source = entry.get('source', {})
            source_path = source.get('path')
            if (entry.get('name') != manifest['name'] or source.get('source') != 'local'
                    or not isinstance(source_path, str) or Path(source_path).is_absolute()
                    or (root / source_path).resolve() != plugin.resolve()):
                errors.append('marketplace must resolve to the maintained plugin directory')
            if entry.get('policy', {}).get('installation') != 'AVAILABLE':
                errors.append('marketplace must make the plugin available for installation')
    except (OSError, ValueError, TypeError, AttributeError, KeyError) as exc:
        errors.append(f'invalid marketplace: {exc}')
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
        for path in package_files(plugin):
            if path.is_symlink():
                errors.append(f'package symlink: {path.relative_to(plugin)}')
            if path.is_file() and path.suffix in {'.md', '.ts', '.js', '.mjs', '.sh'}:
                for number, line in enumerate(path.read_text(encoding='utf-8').splitlines(), 1):
                    if LEGACY.search(line):
                        errors.append(f'{path.relative_to(plugin)}:{number}: unhandled Cursor runtime reference')
                    if path.suffix == '.md':
                        for target in re.findall(r'\[[^\]]*\]\(([^\s)]+)\)', line):
                            target = target.split('#', 1)[0]
                            if not target or ':' in target or '<' in target or target.startswith('/'):
                                continue
                            resolved = (path.parent / target).resolve()
                            if not resolved.is_relative_to(plugin.resolve()) or not resolved.exists():
                                errors.append(f'{path.relative_to(plugin)}:{number}: broken or escaping local link {target}')
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
