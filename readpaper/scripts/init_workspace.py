#!/usr/bin/env python3
"""Create a ReadPaper workspace without replacing user files (stdlib only)."""
import argparse
import json
import re
from pathlib import Path

HEADER = '| slug | 标题 | 会议/年份 | 状态 | 一句话贡献 | 与主线的关系 |'
SEPARATOR = '|---|---|---|---|---|---|'
DEFAULT_FOCUS = '长程任务的世界模型、记忆与移动操纵'
SLUG = re.compile(r'[a-z0-9][a-z0-9._-]*-\d{4}\.\d{4,5}')
CUSTOM_SLUG = re.compile(r'[a-z0-9][a-z0-9._-]*')


def cell(value):
    return ' '.join(value.split()).replace('|', '&#124;')


def scaffold(root, slug=None, title='待核对', venue_year='待核对',
             focus=DEFAULT_FOCUS, allow_custom_slug=False):
    if slug and not (CUSTOM_SLUG if allow_custom_slug else SLUG).fullmatch(slug):
        raise ValueError('slug 应为全小写短名-arXiv编号；自定义稳定 slug 需 --allow-custom-slug')
    root = Path(root).expanduser().resolve()
    if root.exists() and not root.is_dir():
        raise ValueError('root 必须是目录')
    skill = Path(__file__).resolve().parents[1]
    directories = ['paper', 'analyse', 'ideas', 'archive']
    files = {
        'AGENTS.md': (skill / 'assets/AGENTS.template.md').read_text(encoding='utf-8').replace('{{FOCUS}}', ' '.join(focus.split())),
        'README.md': HEADER + '\n' + SEPARATOR + '\n',
        'paper/README.md': '# 论文原料\n\n这里存放用户提供的论文 PDF 及其原始资料。\n\n每篇使用全小写 `<短名>-<arXiv编号>` 目录，与 analyse 共用 slug。\n无 arXiv 编号时使用用户指定的稳定 slug，不伪造编号。\n初始化只补建说明和空目录，不写入或修改论文文件。\n笔记、图、提示词和编译文件全部放 analyse。\n',
    }
    if slug:
        directories += [f'paper/{slug}', f'analyse/{slug}', *[f'analyse/{slug}/{s}' for s in ('notes', 'figures', 'tmp')]]
        files[f'analyse/{slug}/README.md'] = '\n'.join([
            '# ' + cell(title), '',
            '## 1. 一句话贡献', '', '待读原文后填写。', '',
            '## 2. 开卷地图', '', '阅读全文后将 notes/map.md 原样存档于此。', '',
            '## 3. 验收问题 + 我的答案 + 你的判词', '', '开卷后记录题目；提交答案后记录原答案与判词。', '',
            '## 4. 错题本', '', '尚未验收。', '',
            '## 5. 我的疑问与批判', '', '<!-- 留给读者本人。 -->', '',
            '## 6. 文件索引', '', '| 路径 | 这是什么 | 日期 |', '|---|---|---|', '',
        ])
    # Preflight every target before writing; refuse child symlinks and type conflicts.
    for rel in directories + list(files):
        target = root / rel
        for part in [target, *target.parents]:
            if part == root:
                break
            if part.is_symlink():
                raise ValueError(f'初始化目标不能经过符号链接: {part}')
        if target.exists() and target.is_dir() != (rel in directories):
            raise ValueError(f'目标类型冲突: {target}')
    result = {'root': str(root), 'created': [], 'preserved': [], 'warnings': [], 'ledger_added': False}
    root.mkdir(parents=True, exist_ok=True)
    for rel in directories:
        p = root / rel
        if not p.exists():
            p.mkdir(parents=True, exist_ok=True)
            result['created'].append(rel + '/')
    for rel, content in files.items():
        try:
            with (root / rel).open('x', encoding='utf-8') as out:
                out.write(content)
            result['created'].append(rel)
        except FileExistsError:
            result['preserved'].append(rel)
    if slug:
        ledger = root / 'README.md'
        old = ledger.read_text(encoding='utf-8')
        lines = old.splitlines(keepends=True)
        expected = [x.strip() for x in HEADER.strip('|').split('|')]
        def fields(line):
            return [x.strip().strip('`') for x in line.strip().strip('|').split('|')]
        start = next((i for i, line in enumerate(lines) if fields(line) == expected), None)
        if start is None or start + 1 >= len(lines) or not re.fullmatch(r'[\s|:\-]+', lines[start + 1]):
            result['warnings'].append('现有根 README 不是六列论文台账；已保留，请按项目规则处理索引。')
        else:
            end = start + 2
            while end < len(lines) and lines[end].lstrip().startswith('|'):
                end += 1
            if not any(fields(line)[0] == slug for line in lines[start + 2:end]):
                row = '| ' + ' | '.join(map(cell, (slug, title, venue_year, '待读', '待读原文后填写', '待读原文后判断'))) + ' |\n'
                if end and not lines[end - 1].endswith('\n'):
                    lines[end - 1] += '\n'
                lines.insert(end, row)
                ledger.write_text(''.join(lines), encoding='utf-8')
                result['ledger_added'] = True
    return result


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root', required=True)
    p.add_argument('--slug')
    p.add_argument('--title', default='待核对')
    p.add_argument('--venue-year', default='待核对')
    p.add_argument('--focus', default=DEFAULT_FOCUS)
    p.add_argument('--allow-custom-slug', action='store_true')
    try:
        result = scaffold(**vars(p.parse_args()))
    except (ValueError, OSError) as error:
        p.exit(2, f'初始化失败: {error}\n')
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
