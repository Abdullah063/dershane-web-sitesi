"""Regression checks for clean URLs and unchanged layout/asset destinations."""
import json
import posixpath
import unittest
from html.parser import HTMLParser
from urllib.parse import urlsplit, unquote
from build_site import ROOT, SOURCE, render, render_source, generated_files
from clean_urls import output_path, rewrite_page

class Document(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tags = []
        self.assets = []
        self.links = []
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'meta' and attrs.get('property') in ('og:url',): attrs.pop('content', None)
        self.tags.append((tag, {k: v for k, v in attrs.items() if k not in ('href','src','action','srcset','data-sticky','defer','async')}))
        for key in ('src', 'data-sticky'):
            if key in attrs and tag != 'script': self.assets.append(attrs[key])
        if 'srcset' in attrs:
            self.assets.extend(item.strip().split()[0] for item in attrs['srcset'].split(','))
        if tag == 'a' and 'href' in attrs: self.links.append(attrs['href'])

def destination(url, page):
    p = urlsplit(url)
    if p.scheme or p.netloc or not p.path: return url
    resolved = posixpath.normpath(posixpath.join(posixpath.dirname(page), unquote(p.path)))
    pages = json.loads((SOURCE / 'pages.json').read_text())
    if resolved in pages:
        resolved = posixpath.dirname(output_path(resolved)) or '.'
    return resolved + ('?' + p.query if p.query else '')

class CleanURLs(unittest.TestCase):
    def test_all_pages_preserve_layout_assets_and_use_clean_links(self):
        pages = json.loads((SOURCE / 'pages.json').read_text())
        for source, data in pages.items():
            with self.subTest(source=source):
                before, after = Document(), Document()
                before.feed(render_source(source, data)); after.feed(render(source, data))
                self.assertEqual(before.tags, after.tags)
                self.assertEqual([destination(u,source) for u in before.assets],
                                 [destination(u,output_path(source)) for u in after.assets])
                self.assertFalse(any(urlsplit(u).path.endswith('.html') for u in after.links))
                self.assertEqual((ROOT/output_path(source)).read_text(),render(source,data))
    def test_query_fragment_and_external_urls(self):
        pages = {'index.html': {}, 'kurs.html': {}, 'iletisim/index.html': {}}
        text = '<a href="kurs.html?x=1&amp;y=2#bilgi">Kurs</a><a href="https://example.com/a.html">Dış</a><img src="assets/a.png">'
        result = rewrite_page(text, 'kurs.html', pages)
        self.assertIn('href="./?x=1&amp;y=2#bilgi"',result)
        self.assertIn('href="https://example.com/a.html"',result)
        self.assertIn('src="../assets/a.png"',result)
    def test_redirect_outputs_preserve_query_and_fragment(self):
        pages = json.loads((SOURCE/'pages.json').read_text())
        outputs = generated_files(pages)
        for source in pages:
            if source != output_path(source):
                self.assertIn('location.search + location.hash',outputs[source])
                self.assertIn('http-equiv="refresh"',outputs[source])
        self.assertIn('THE_REQUEST',outputs['.htaccess'])

if __name__ == '__main__': unittest.main()
