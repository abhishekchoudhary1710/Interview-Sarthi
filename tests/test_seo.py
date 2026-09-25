import json
from html.parser import HTMLParser
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from seo_audit import Page, ROOT, audit, canonical_for, local_target, nodes, robots_allows, srcset_urls
from generate_sitemap import render


class SeoTests(unittest.TestCase):
    def fixture_site(self, root, pages, robots=None):
        """Small crawlable site for testing regressions without live network access."""
        (root/'robots.txt').write_text(
            (robots if robots is not None else 'User-agent: *\nAllow: /\n')
            + '\nSitemap: https://interviewsarthi.com/sitemap.xml\n', encoding='utf-8')
        locations = []
        for path, body in pages.items():
            target = root/path
            target.parent.mkdir(parents=True, exist_ok=True)
            if 'http-equiv="refresh"' in body:
                target.write_text(body, encoding='utf-8')
                continue
            canonical = canonical_for(path)
            target.write_text(f'<html lang="en"><head><title>{path}</title>'
                             f'<meta name="description" content="About {path}">'
                             '<meta name="viewport" content="width=device-width, initial-scale=1">'
                             f'<link rel="canonical" href="{canonical}">'
                             f'<meta property="og:url" content="{canonical}"></head>'
                             f'<body><h1>{path}</h1>{body}</body></html>', encoding='utf-8')
            locations.append(f'<url><loc>{canonical}</loc></url>')
        (root/'sitemap.xml').write_text('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
                                      + ''.join(locations) + '</urlset>', encoding='utf-8')

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

    def test_redirect_migration_is_checked_without_requiring_page_metadata(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.fixture_site(root, {
                'index.html': '<a href="prep/">Prep</a>',
                'prep/index.html': '<p>Practice</p>',
                'mock/index.html': '<meta http-equiv="refresh" content="0; url=/prep/">'
                                   '<link rel="canonical" href="https://interviewsarthi.com/prep/">',
            })
            result = audit(root)
            self.assertEqual(result['errors'], [])
            self.assertEqual(result['pages'], 2)
            self.assertEqual(result['redirects'], 1)
            self.assertEqual(len(result['inventory']), 2)
            (root/'prep/index.html').unlink()
            self.assertIn('redirect destination is not a local HTML page', '\n'.join(audit(root)['errors']))

    def test_redirect_loops_invalid_refresh_and_wrong_canonicals_fail(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.fixture_site(root, {
                'index.html': '<p>Home</p>',
                'a.html': '<meta http-equiv="refresh" content="0; url=/b.html">'
                          '<link rel="canonical" href="https://interviewsarthi.com/">',
                'b.html': '<meta http-equiv="refresh" content="0; url=/a.html">'
                          '<link rel="canonical" href="https://interviewsarthi.com/a.html">',
                'bad.html': '<meta http-equiv="refresh" content="0">',
                'bad-url.html': '<meta http-equiv="refresh" content="0; url=javascript:alert(1)">',
                'wrong-canonical.html': '<meta http-equiv="refresh" content="0; url=/">'
                                        '<link rel="canonical" href="https://interviewsarthi.com/wrong-canonical.html">',
            })
            errors = '\n'.join(audit(root)['errors'])
            self.assertIn('redirect loop', errors)
            self.assertIn('redirect canonical must match', errors)
            self.assertIn('invalid redirect refresh', errors)
            self.assertIn('invalid redirect URL', errors)

    def test_responsive_and_video_asset_failures_are_reported(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.fixture_site(root, {'index.html':
                '<picture><source srcset="/small.webp 640w, /large.webp 1280w"></picture>'
                '<video data-src="/lazy.mp4" poster="/poster.jpg"><source src="/movie.mp4"></video>'})
            errors = '\n'.join(audit(root)['errors'])
            for asset in ('/small.webp', '/large.webp', '/lazy.mp4', '/poster.jpg', '/movie.mp4'):
                self.assertIn('broken local URL ' + asset, errors)
            self.assertEqual(list(srcset_urls('data:image/png;base64,AAAA 1x, /image.png 2x')),
                             ['data:image/png;base64,AAAA', '/image.png'])
            self.assertEqual(list(srcset_urls('/one.png, /two.png 2x')), ['/one.png', '/two.png'])

    def test_language_and_mobile_viewport_are_recommendations(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.fixture_site(root, {'index.html': '<p>Home</p>'})
            page = root/'index.html'
            page.write_text(page.read_text(encoding='utf-8').replace('lang="en"', '')
                            .replace('name="viewport"', 'name="unused"'), encoding='utf-8')
            result = audit(root)
            self.assertEqual(result['errors'], [])
            self.assertIn('missing HTML language declaration', '\n'.join(result['warnings']))
            self.assertIn('missing responsive viewport', '\n'.join(result['warnings']))

    def test_robots_uses_specific_groups_and_longest_matching_rule(self):
        robots = ('User-agent: *\nDisallow: /\n'
                  'User-agent: Googlebot\nDisallow: /private/*\nAllow: /private/public$\n'
                  'User-agent: Googlebot\nDisallow: /assets/\nAllow: /assets/logo.png\n')
        self.assertTrue(robots_allows(robots, 'Googlebot', 'https://interviewsarthi.com/prep/'))
        self.assertFalse(robots_allows(robots, 'Bingbot', 'https://interviewsarthi.com/prep/'))
        self.assertFalse(robots_allows(robots, 'Googlebot', 'https://interviewsarthi.com/private/key'))
        self.assertTrue(robots_allows(robots, 'Googlebot', 'https://interviewsarthi.com/private/public'))
        self.assertFalse(robots_allows(robots, 'Googlebot', 'https://interviewsarthi.com/private/public/other'))
        self.assertTrue(robots_allows(robots, 'Googlebot', 'https://interviewsarthi.com/assets/logo.png'))
        self.assertFalse(robots_allows(robots, 'Googlebot', 'https://interviewsarthi.com/assets/style.css'))
        self.assertTrue(robots_allows('User-agent: *\nDisallow: /\nAllow: /', 'Googlebot', '/'))

    def test_robots_cannot_hide_indexable_pages_or_rendering_assets(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.fixture_site(root, {'index.html': '<img src="/photo.png" alt="Product">'},
                              robots='User-agent: *\nDisallow: /\n')
            (root/'photo.png').write_bytes(b'image')
            errors = '\n'.join(audit(root)['errors'])
            self.assertIn('blocks Googlebot from an indexable page', errors)
            self.assertIn('blocks Bingbot from an indexable page', errors)
            self.assertIn('blocks Googlebot from local asset /photo.png', errors)

    def test_breadcrumb_allows_missing_final_url_but_rejects_invalid_urls(self):
        schema = {'@type': 'BreadcrumbList', 'itemListElement': [
            {'@type': 'ListItem', 'position': 1, 'name': 'Home', 'item': 'https://interviewsarthi.com/'},
            {'@type': 'ListItem', 'position': 2, 'name': 'Page'},
        ]}
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.fixture_site(root, {'index.html': '<script type="application/ld+json">'
                                                    + json.dumps(schema) + '</script>'})
            self.assertEqual(audit(root)['errors'], [])
            schema['itemListElement'][0]['item'] = 'https://interviewsarthi.com/missing.html'
            schema['itemListElement'][1].update(position=4, item='/relative.html')
            self.fixture_site(root, {'index.html': '<script type="application/ld+json">'
                                                    + json.dumps(schema) + '</script>'})
            errors = '\n'.join(audit(root)['errors'])
            self.assertIn('broken breadcrumb URL', errors)
            self.assertIn('positions must be consecutive', errors)
            self.assertIn('must be an absolute web URL', errors)

    def test_structured_dates_and_article_image_recommendation(self):
        schemas = [{'@type': 'Article', 'datePublished': '2002-01-01', 'dateModified': '2001-01-01'},
                   {'@type': 'Article', 'datePublished': 'not a date', 'dateModified': '9999-01-01'},
                   {'@type': 'Article', 'dateModified': '2003-01-01T12:00:00Z'}]
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.fixture_site(root, {'index.html': '<script type="application/ld+json">'
                                                    + json.dumps(schemas) + '</script>'})
            result = audit(root)
            errors = '\n'.join(result['errors'])
            self.assertIn('dateModified precedes datePublished', errors)
            self.assertIn('invalid structured datePublished', errors)
            self.assertIn('future structured dateModified', errors)
            self.assertNotIn('invalid structured dateModified', errors)
            self.assertNotIn('Article has no representative image', errors)
            self.assertIn('Article has no representative image', '\n'.join(result['warnings']))

    def test_current_site_passes(self):
        self.assertEqual(audit()['errors'], [])

    def test_sitemap_is_reproducible(self):
        self.assertEqual(render(), (ROOT/'sitemap.xml').read_text(encoding='utf-8'))

    def test_software_offer_prices_and_entity_links(self):
        page = Page((ROOT/'live/index.html').read_text(encoding='utf-8'))
        app = next(n for s in page.schemas for n in nodes(s) if n.get('@type')=='SoftwareApplication')
        self.assertEqual([str(o['price']) for o in app['offers']], ['0','99','299'])
        self.assertEqual(app['publisher']['@id'], 'https://interviewsarthi.com/#organization')
        self.assertEqual(app['@id'], 'https://interviewsarthi.com/#software')
        self.assertEqual(app['url'], 'https://interviewsarthi.com/live/')

    def test_monthly_checkout_labels_match_monthly_product(self):
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
                    if 'Buy 1-Month Pass' in ' '.join(self.label.split()):
                        self.found.append(self.href)
                    self.href = ''
        html = (ROOT/'live/index.html').read_text(encoding='utf-8')
        links = Links()
        links.feed(html)
        self.assertEqual(len(links.found), 2)
        # The licence server picks Dodo or Cashfree; the plan code is what must match the label.
        self.assertTrue(all('license.interviewsarthi.com/buy?plan=30d' in href for href in links.found))
        # The 7-Day and 3-Month passes were withdrawn on 25 Sep 2026.
        self.assertNotIn('plan=7d', html)
        self.assertNotIn('plan=90d', html)


if __name__ == '__main__':
    unittest.main()
