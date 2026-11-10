#!/usr/bin/env python3
"""Check generated pages, local asset references and dynamic Elementor chunks."""
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import sys
from urllib.parse import unquote, urlsplit

from build_site import ROOT, SOURCE, render

errors = []

class References(HTMLParser):
    def __init__(self, page):
        super().__init__()
        self.page = page

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        urls = [attrs[k] for k in ('src', 'href', 'action', 'data-sticky') if attrs.get(k)]
        if attrs.get('srcset'):
            urls.extend(item.strip().split()[0] for item in attrs['srcset'].split(','))
        for url in urls:
            parts = urlsplit(url)
            if parts.scheme or parts.netloc or not parts.path:
                continue
            path = unquote(parts.path)
            target = ROOT / path.lstrip('/') if path.startswith('/') else self.page.parent / path
            if not target.exists():
                errors.append(f'{self.page.relative_to(ROOT)}: missing {url}')


def main():
    pages = json.loads((SOURCE / 'pages.json').read_text())
    for path, metadata in pages.items():
        page = ROOT / path
        if not page.exists():
            errors.append(f'Missing output: {path}')
            continue
        html = page.read_text()
        if html != render(path, metadata):
            errors.append(f'{path}: rebuild required')
        References(page).feed(html)
        if re.search(r'gaziosman|bakirkoymurat', html, re.I):
            errors.append(f'{path}: legacy institution reference')
    # Fonts and background images are referenced by CSS rather than HTML.
    for css in (ROOT / 'wp-content').rglob('*'):
        if not css.is_file() or '.css' not in css.name:
            continue
        for url in re.findall(r"url\(\s*[\"']?([^\)\"']+)", css.read_text(errors='replace')):
            parts = urlsplit(url)
            if parts.scheme or parts.netloc:
                if parts.hostname == 'kuantumegitim.com.tr':
                    errors.append(f'{css.relative_to(ROOT)}: inaccessible remote font {url}')
                continue
            if parts.path:
                target = ROOT / unquote(parts.path).lstrip('/') if parts.path.startswith('/') else css.parent / unquote(parts.path)
                if not target.exists():
                    errors.append(f'{css.relative_to(ROOT)}: missing CSS asset {url}')
    dialog = ROOT / 'wp-content/plugins/elementor/assets/lib/dialog/dialog.min.js'
    if not dialog.is_file():
        errors.append('Missing Elementor dialog library')
    # Dynamic chunks do not appear in ordinary <script> references.
    widgets = set()
    for path in pages:
        widgets.update(re.findall(r'data-widget_type="([^"]+)"', (ROOT / path).read_text()))
    core_chunks = {
        'text-editor.default': 'text-editor', 'counter.default': 'counter',
        'image-carousel.default': 'image-carousel', 'accordion.default': 'accordion',
        'tabs.default': 'tabs', 'toggle.default': 'toggle', 'video.default': 'video',
    }
    for widget, chunk in core_chunks.items():
        if widget in widgets and not (ROOT / 'wp-content/plugins/elementor/assets/js/chunks' / (chunk + '.min.js')).is_file():
            errors.append(f'Missing dynamic chunk for {widget}')
    if 'gallery.default' in widgets:
        runtime = (ROOT / 'wp-content/plugins/elementor-pro/assets/js/webpack-pro.runtime.min.js?ver=3.35.1').read_text()
        match = re.search(r'"(gallery\.[a-f0-9]+\.bundle\.min\.js)"', runtime)
        if not match or not (ROOT / 'wp-content/plugins/elementor-pro/assets/js' / match[1]).is_file():
            errors.append('Missing gallery dynamic chunk')
    if errors:
        print('\n'.join(errors), file=sys.stderr)
        return 1
    print(f'{len(pages)} pages: generated output, local links, CSS assets, fonts, dialog and required chunks OK.')
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
