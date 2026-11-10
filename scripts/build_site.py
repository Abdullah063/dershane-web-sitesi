#!/usr/bin/env python3
"""Build the existing static pages from shared partials; no third-party packages."""
import argparse
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'site-src'
TOKEN = re.compile(r'\{\{([\w:-]+)\}\}')


def render(path, metadata):
    page = (SOURCE / 'pages' / (path + '.template')).read_text()
    def include(match):
        key = match[1]
        if key.startswith('include:'):
            name = key.split(':', 1)[1]
            return (SOURCE / 'partials' / (name + '.html.template')).read_text()
        return match[0]
    page = TOKEN.sub(include, page)
    values = metadata.get('values', {})
    page = TOKEN.sub(lambda m: values.get(m[1], m[0]), page)
    page = page.replace('{{root}}', '../' * (len(Path(path).parts) - 1))
    unresolved = TOKEN.findall(page)
    if unresolved:
        raise ValueError(f'{path}: unresolved template fields: {unresolved}')
    return page


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='Check output without writing files')
    args = parser.parse_args()
    pages = json.loads((SOURCE / 'pages.json').read_text())
    # Render everything before writing, so a template error cannot leave half a build.
    outputs = {path: render(path, data) for path, data in pages.items()}
    stale = []
    for path, html in outputs.items():
        target = ROOT / path
        if target.exists() and target.read_text() == html:
            continue
        stale.append(path)
        if not args.check:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(html)
    if args.check and stale:
        print('Rebuild required:\n' + '\n'.join(stale), file=sys.stderr)
        return 1
    print(f'{len(outputs)} pages checked; {len(stale)} ' + ('outdated.' if args.check else 'updated.'))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
