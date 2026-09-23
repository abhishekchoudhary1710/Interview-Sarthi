"""Dependency-free static-site checks. Run from any directory; --json saves inventory."""
import argparse
from collections import defaultdict
from datetime import date
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import sys
from urllib.parse import unquote, urljoin, urlsplit
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
ORIGIN = 'https://interviewsarthi.com'
NS = {'s': 'http://www.sitemaps.org/schemas/sitemap/0.9'}


def nodes(value):
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from nodes(child)
    elif isinstance(value, list):
        for child in value:
            yield from nodes(child)


class Page(HTMLParser):
    def __init__(self, source):
        super().__init__(convert_charrefs=True)
        self.titles, self.descriptions, self.canonicals = [], [], []
        self.robots, self.links, self.images, self.schemas, self.json_errors = [], [], [], [], []
        self.ids, self.h1, self.meta, self.visible = set(), 0, {}, []
        self.refresh = None
        self._title, self._script, self._hidden = None, None, 0
        self.feed(source)

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if a.get('id'):
            self.ids.add(a['id'])
        if tag == 'title':
            self._title = ''
        if tag in ('style', 'script'):
            self._hidden += 1
        if tag == 'script' and a.get('type', '').lower() == 'application/ld+json':
            self._script = ''
        if tag == 'meta' and a.get('http-equiv', '').lower() == 'refresh':
            self.refresh = a.get('content', '')
        if tag == 'meta':
            key = a.get('name', a.get('property', '')).lower()
            self.meta[key] = a.get('content', '')
            if key == 'description':
                self.descriptions.append(a.get('content', ''))
            if key in ('robots', 'googlebot'):
                self.robots.append(a.get('content', '').lower())
        if tag == 'link' and 'canonical' in a.get('rel', '').lower().split():
            self.canonicals.append(a.get('href', ''))
        if tag == 'h1':
            self.h1 += 1
        if tag == 'a' and 'href' in a:
            self.links.append(a['href'])
        if tag in ('img', 'script') and a.get('src'):
            self.images.append(a['src'])
        if tag == 'link' and a.get('rel') in ('stylesheet', 'icon', 'apple-touch-icon'):
            self.images.append(a.get('href', ''))

    def handle_endtag(self, tag):
        if tag == 'title' and self._title is not None:
            self.titles.append(self._title.strip())
            self._title = None
        if tag == 'script' and self._script is not None:
            try:
                self.schemas.append(json.loads(self._script))
            except ValueError as exc:
                self.json_errors.append(str(exc))
            self._script = None
        if tag in ('style', 'script'):
            self._hidden = max(0, self._hidden - 1)

    def handle_data(self, data):
        if self._title is not None:
            self._title += data
        if self._script is not None:
            self._script += data
        if not self._hidden:
            self.visible.append(data)

    @property
    def indexable(self):
        return not any(re.search(r'\b(noindex|none)\b', x) for x in self.robots)

    @property
    def is_redirect(self):
        """A stub left at a moved URL. GitHub Pages cannot serve a 301, so a renamed page leaves
        behind a meta-refresh that points at its new home. It is routing, not a page: it has no H1
        and no description on purpose, and its canonical belongs to the destination."""
        return bool(self.refresh)


def public_pages(root=ROOT):
    """Every real page. Redirect stubs are left out -- auditing them reports the absence of things
    a redirect is not supposed to have, and their canonical always names another URL."""
    pages = {p.relative_to(root).as_posix(): Page(p.read_text(encoding='utf-8'))
             for p in sorted(root.rglob('*.html'))
             if not any(part.startswith('.') for part in p.relative_to(root).parts)}
    return {path: page for path, page in pages.items() if not page.is_redirect}


def canonical_for(path):
    return ORIGIN + '/' + (path[:-10] if path.endswith('index.html') else path)


def local_target(href, base):
    url = urlsplit(urljoin(base, href))
    if url.scheme not in ('http', 'https') or url.netloc != urlsplit(ORIGIN).netloc:
        return None
    path = unquote(url.path).lstrip('/')
    if not path or path.endswith('/'):
        path += 'index.html'
    return path, unquote(url.fragment)


def audit(root=ROOT):
    pages = public_pages(root)
    errors, warnings, inventory = [], [], []
    sitemap = []
    try:
        tree = ET.parse(root / 'sitemap.xml')
        for entry in tree.findall('s:url', NS):
            loc = entry.findtext('s:loc', namespaces=NS)
            if not loc:
                errors.append('sitemap: missing loc')
                continue
            sitemap.append(loc)
            modified = entry.findtext('s:lastmod', namespaces=NS)
            if modified:
                try:
                    if date.fromisoformat(modified) > date.today():
                        errors.append(f'sitemap: future lastmod for {loc}')
                except ValueError:
                    errors.append(f'sitemap: invalid lastmod for {loc}')
    except (OSError, ET.ParseError) as exc:
        errors.append(f'sitemap: {exc}')
    if len(sitemap) != len(set(sitemap)):
        errors.append('sitemap: duplicate URLs')
    duplicates = {key: defaultdict(list) for key in ('title', 'description', 'canonical')}
    incoming = defaultdict(set)
    for path, page in pages.items():
        base = canonical_for(path)
        if page.indexable:
            for label, values in [('title', page.titles), ('description', page.descriptions), ('canonical', page.canonicals)]:
                if len(values) != 1 or not values[0].strip():
                    errors.append(f'{path}: expected one nonempty {label}')
                elif values:
                    duplicates[label][values[0]].append(path)
            if page.canonicals != [base]:
                errors.append(f'{path}: canonical must be {base}')
            if page.h1 == 0:
                errors.append(f'{path}: missing H1')
            elif page.h1 > 1:
                warnings.append(f'{path}: {page.h1} H1 elements')
            if base not in sitemap:
                errors.append(f'{path}: missing from sitemap')
            if page.meta.get('og:url') != base:
                errors.append(f'{path}: og:url does not match canonical')
            for key in ('og:title', 'og:description', 'og:image', 'twitter:card'):
                if not page.meta.get(key):
                    warnings.append(f'{path}: missing {key}')
        elif base in sitemap:
            errors.append(f'{path}: noindex page in sitemap')
        for err in page.json_errors:
            errors.append(f'{path}: invalid JSON-LD: {err}')
        for schema in page.schemas:
            for node in nodes(schema):
                if node.get('@type') == 'Organization' and node.get('name') == 'Interview Sarthi':
                    if node.get('@id') != ORIGIN + '/#organization':
                        warnings.append(f'{path}: Organization missing stable ID')
                for profile in node.get('sameAs', []):
                    if not isinstance(profile, str) or not profile.startswith('https://') or re.search(r'OFFICIAL_|PLACEHOLDER|example\.com', profile):
                        errors.append(f'{path}: invalid sameAs')
        text = ' '.join(page.visible)
        if re.search(r'\b(TODO|CHANGEME|PLACEHOLDER)\b', text):
            warnings.append(f'{path}: possible visible placeholder')
        if re.search(r'(?:three|3)\s+(?:full\s+|15.minute\s+)sessions\s+(?:(?:are\s+)?free|with every feature|,?\s*no card)', text, re.I):
            errors.append(f'{path}: stale trial copy')
        for href in page.links + page.images + [page.meta.get('og:image', '')]:
            if not href:
                continue
            target = local_target(href, base)
            if target is None:
                continue
            dest, fragment = target
            if not (root / dest).is_file():
                errors.append(f'{path}: broken local URL {href}')
            elif dest in pages:
                if dest != path:
                    incoming[dest].add(path)
                if fragment and fragment not in pages[dest].ids:
                    errors.append(f'{path}: missing fragment {href}')
        inventory.append({'file': path, 'title': page.titles, 'description': page.descriptions,
                          'canonical': page.canonicals, 'robots': page.robots, 'h1_count': page.h1,
                          'schema_types': sorted({str(n['@type']) for s in page.schemas for n in nodes(s) if '@type' in n}),
                          'in_sitemap': base in sitemap})
    for loc in sitemap:
        target = local_target(loc, ORIGIN + '/')
        if not target or target[0] not in pages or loc != canonical_for(target[0]):
            errors.append(f'sitemap: not a local canonical HTML page: {loc}')
    for label, values in duplicates.items():
        for value, paths in values.items():
            if len(paths) > 1:
                errors.append(f'duplicate {label}: {", ".join(paths)}')
    for path, page in pages.items():
        if page.indexable and path != 'index.html' and not incoming[path]:
            warnings.append(f'{path}: no incoming internal links')
    robots = (root / 'robots.txt').read_text(encoding='utf-8')
    if f'Sitemap: {ORIGIN}/sitemap.xml' not in robots:
        errors.append('robots.txt: canonical sitemap declaration missing')
    return {'pages': len(pages), 'indexable': sum(p.indexable for p in pages.values()),
            'errors': sorted(set(errors)), 'warnings': sorted(set(warnings)), 'inventory': inventory}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--json', type=Path, help='Write full inventory and findings')
    args = parser.parse_args()
    result = audit()
    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(json.dumps(result, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    for severity in ('errors', 'warnings'):
        for message in result[severity]:
            print(f'{severity.upper()}: {message}')
    print(f"SEO audit: {result['pages']} pages, {result['indexable']} indexable, "
          f"{len(result['errors'])} errors, {len(result['warnings'])} warnings")
    sys.exit(bool(result['errors']))
