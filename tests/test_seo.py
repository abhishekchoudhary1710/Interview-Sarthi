import json
from html.parser import HTMLParser
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from seo_audit import Page, ROOT, audit, canonical_for, local_target, nodes
from generate_sitemap import render


class SeoTests(unittest.TestCase):
    def test_parser_detects_invalid_json_and_noindex(self):
        page = Page('<META NAME="ROBOTS" CONTENT="noindex, follow"><script type="application/ld+json">{bad}</script>')
        self.assertFalse(page.indexable)
        self.assertEqual(len(page.json_errors), 1)

    def test_canonical_directory_and_relative_fragment(self):
        self.assertEqual(canonical_for('guides/index.html'), 'https://interviewsarthi.com/guides/')
        self.assertEqual(local_target('../#pricing', canonical_for('guides/test.html')), ('index.html', 'pricing'))
        self.assertIsNone(local_target('https://example.com/a.html', canonical_for('index.html')))

    def test_sitemap_refuses_noindex_and_paths_outside_root(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root/'thanks.html').write_text('<meta name="robots" content="noindex">', encoding='utf-8')
            for config in ({'thanks.html':'2026-09-01'}, {'../escape.html':'2026-09-01'}):
                with self.assertRaises(ValueError):
                    render(root, config)

    def test_audit_detects_broken_fragments_and_duplicate_metadata(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root/'robots.txt').write_text('Sitemap: https://interviewsarthi.com/sitemap.xml', encoding='utf-8')
            (root/'sitemap.xml').write_text('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"/>', encoding='utf-8')
            for name in ('index.html','a.html'):
                (root/name).write_text('<title>Duplicate</title><meta name="description" content="Duplicate"><h1>Title</h1><a href="a.html#missing">link</a>', encoding='utf-8')
            errors = '\n'.join(audit(root)['errors'])
            self.assertIn('duplicate title', errors)
            self.assertIn('missing fragment', errors)
            self.assertIn('missing from sitemap', errors)

    def test_current_site_passes(self):
        self.assertEqual(audit()['errors'], [])

    def test_sitemap_is_reproducible(self):
        self.assertEqual(render(), (ROOT/'sitemap.xml').read_text(encoding='utf-8'))

    def test_software_offer_prices_and_entity_links(self):
        page = Page((ROOT/'index.html').read_text(encoding='utf-8'))
        app = next(n for s in page.schemas for n in nodes(s) if n.get('@type')=='SoftwareApplication')
        self.assertEqual([str(o['price']) for o in app['offers']], ['0','99','399','999','1999'])
        self.assertEqual(app['publisher']['@id'], 'https://interviewsarthi.com/#organization')

    def test_weekly_checkout_labels_match_weekly_product(self):
        class Links(HTMLParser):
            def __init__(self):
                super().__init__()
                self.href, self.label, self.found = '', '', []
            def handle_starttag(self, tag, attrs):
                if tag == 'a':
                    self.href, self.label = dict(attrs).get('href', ''), ''
            def handle_data(self, text):
                if self.href:
                    self.label += text
            def handle_endtag(self, tag):
                if tag == 'a':
                    if 'Buy 7-Day Pass' in ' '.join(self.label.split()):
                        self.found.append(self.href)
                    self.href = ''
        links = Links()
        links.feed((ROOT/'index.html').read_text(encoding='utf-8'))
        self.assertEqual(len(links.found), 2)
        # The licence server picks Dodo or Cashfree; the plan code is what must match the label.
        self.assertTrue(all('license.interviewsarthi.com/buy?plan=7d' in href for href in links.found))


if __name__ == '__main__':
    unittest.main()
