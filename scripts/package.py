"""Create a source-only plugin ZIP after release validation."""
from __future__ import annotations

import argparse
import hashlib
import json
import zipfile
from pathlib import Path

from validate import ROOT, package_files, validate


def build(output: Path):
    errors = validate()
    if errors:
        raise ValueError('\n'.join(errors))
    plugin = ROOT / 'plugins/pstack-codex'
    skill_count = len(json.loads((ROOT / 'adapter/skills.json').read_text(encoding='utf-8')))
    files = sorted(package_files(plugin), key=lambda path: path.relative_to(plugin).as_posix())
    output = output.resolve()
    if output.is_relative_to(plugin.resolve()):
        raise ValueError('Archive must be outside the plugin source directory')
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, 'w', zipfile.ZIP_DEFLATED) as archive:
        for path in files:
            entry = zipfile.ZipInfo(path.relative_to(plugin).as_posix(), (2026, 1, 1, 0, 0, 0))
            entry.create_system = 3  # Stable Unix file metadata on every build host.
            entry.compress_type = zipfile.ZIP_DEFLATED
            entry.external_attr = 0o100644 << 16
            archive.writestr(entry, path.read_bytes())
    with zipfile.ZipFile(output) as archive:
        if archive.testzip() is not None:
            raise ValueError('Archive integrity check failed')
        names = archive.namelist()
        if 'plugin.json' not in names or sum(name.endswith('/SKILL.md') for name in names) != skill_count:
            raise ValueError('Archive manifest or skill inventory mismatch')
        if any(set(Path(name).parts) & {'node_modules', '.git', '.venv', '__pycache__'} for name in names):
            raise ValueError('Generated files leaked into archive')
    return {'archive': str(output), 'files': len(files), 'skills': skill_count,
            'version': json.loads((plugin / 'plugin.json').read_text(encoding='utf-8'))['version'],
            'sha256': hashlib.sha256(output.read_bytes()).hexdigest()}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    manifest = json.loads((ROOT / 'plugins/pstack-codex/plugin.json').read_text(encoding='utf-8'))
    parser.add_argument('--output', type=Path, default=ROOT / 'dist' / f"pstack-codex-{manifest['version']}.zip")
    args = parser.parse_args()
    print(json.dumps(build(args.output), indent=2))
