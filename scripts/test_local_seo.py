"""Validate local SEO metadata, canonical consolidation, and truthful JSON-LD."""
import json
from html.parser import HTMLParser
from pathlib import Path
import unittest
import xml.etree.ElementTree as ET
from build_site import ROOT, SOURCE
from clean_urls import output_path, public_path

class Head(HTMLParser):
    def __init__(self):
        super().__init__();self.meta={};self.canonical=[];self.title='';self.data='';self.in_title=False;self.in_schema=False
    def handle_starttag(self,t,a):
        d=dict(a)
        if t=='title': self.in_title=True
        if t=='meta': self.meta[d.get('name',d.get('property'))]=d.get('content')
        if t=='link' and d.get('rel')=='canonical': self.canonical.append(d['href'])
        if t=='script' and d.get('id')=='kuantum-structured-data': self.in_schema=True
    def handle_endtag(self,t):
        if t=='title':self.in_title=False
        if t=='script':self.in_schema=False
    def handle_data(self,d):
        if self.in_title:self.title+=d
        if self.in_schema:self.data+=d

class LocalSEO(unittest.TestCase):
    def test_metadata_and_structured_data_on_every_page(self):
        conf=json.loads((SOURCE/'seo.json').read_text());pages=json.loads((SOURCE/'pages.json').read_text());business=json.loads((SOURCE/'site.json').read_text())
        titles=set();descriptions=set()
        for path in pages:
            with self.subTest(path=path):
                primary=conf['aliases'].get(path,path);settings=conf['pages'][primary]
                parsed=Head();parsed.feed((ROOT/output_path(path)).read_text())
                self.assertEqual(parsed.canonical,[conf['domain']+'/'+public_path(primary)])
                self.assertEqual(parsed.title,settings['title'])
                self.assertEqual(parsed.meta['description'],settings['description'])
                self.assertEqual(parsed.meta['og:url'],parsed.canonical[0])
                self.assertEqual('noindex' in parsed.meta['robots'],not settings['index'])
                graph=json.loads(parsed.data)['@graph'];org=graph[0]
                self.assertEqual(org['telephone'],business['contact_tel'].removeprefix('tel:'))
                self.assertEqual(org['address']['addressRegion'],'Eskişehir')
                for unknown in ('aggregateRating','review','openingHours','openingHoursSpecification','geo'):
                    self.assertNotIn(unknown,org)
                if primary==path and settings['index']:
                    self.assertNotIn(parsed.title,titles);titles.add(parsed.title)
                    self.assertNotIn(parsed.meta['description'],descriptions);descriptions.add(parsed.meta['description'])
    def test_sitemap_only_contains_primary_indexable_pages(self):
        conf=json.loads((SOURCE/'seo.json').read_text())
        expected={conf['domain']+'/'+public_path(p) for p,m in conf['pages'].items() if m['index']}
        tree=ET.parse(ROOT/'sitemap.xml');found={e.text for e in tree.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}loc')}
        self.assertEqual(found,expected)
        self.assertEqual(len(tree.getroot()),len(found))

if __name__=='__main__':unittest.main()
