#!/usr/bin/env python3
"""Vendor the standalone DrawPaper workflow into ReadPaper, or check parity."""
import argparse
import json
from hashlib import sha256
from pathlib import Path


def expected_files(root):
    source = root / 'drawpaper'
    skill = (source / 'SKILL.md').read_text(encoding='utf-8')
    if not skill.startswith('---\n'):
        raise ValueError('DrawPaper SKILL.md lacks frontmatter')
    body = skill.split('---\n', 2)[2].lstrip()
    files = {'WORKFLOW.md': body.encode()}
    for folder in ('references', 'scripts', 'assets'):
        for path in sorted((source / folder).rglob('*')):
            if path.is_file() and path.name != '.DS_Store' and '__pycache__' not in path.parts and path.suffix != '.pyc':
                files[path.relative_to(source).as_posix()] = path.read_bytes()
    manifest = {'source': 'drawpaper', 'files': {key: sha256(value).hexdigest() for key, value in files.items()}}
    files['manifest.json'] = (json.dumps(manifest, ensure_ascii=False, indent=2) + '\n').encode()
    return files


def sync(root, check=False):
    target = root / 'readpaper/bundled/drawpaper'
    expected = expected_files(root)
    actual = {p.relative_to(target).as_posix() for p in target.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.name != '.DS_Store'}
    changed = [rel for rel, data in expected.items() if not (target / rel).is_file() or (target / rel).read_bytes() != data]
    extra = sorted(actual - expected.keys())
    if check:
        if changed or extra:
            raise ValueError(f'Embedded DrawPaper differs: changed={changed}, extra={extra}')
    else:
        if extra:
            raise ValueError(f'Unexpected embedded files; inspect instead of deleting: {extra}')
        for rel, data in expected.items():
            path = target / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            if rel in changed:
                path.write_bytes(data)
    return len(expected)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    try:
        count = sync(Path(__file__).resolve().parents[1], args.check)
    except (ValueError, OSError) as error:
        parser.exit(1, f'{error}\n')
    print(f'DrawPaper {"verified" if args.check else "synced"}: {count} files')


if __name__ == '__main__':
    main()
