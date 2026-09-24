"""Dependency-free static-site checks. Run from any directory; --json saves inventory."""
import argparse
from collections import defaultdict
from datetime import date, datetime
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


def srcset_urls(value):
    """Read candidate URLs without splitting commas inside data URLs."""
    position = 0
    while position < len(value):
        while position < len(value) and (value[position].isspace() or value[position] == ','):
            position += 1
        start = position
        while position < len(value) and not value[position].isspace():
            position += 1
        candidate = value[start:position]
        if candidate:
            yield candidate.rstrip(',')
        if candidate.endswith(','):
            continue
        # Width and density descriptors end at the next comma.
        while position < len(value) and value[position] != ',':
            position += 1


def robots_allows(source, user_agent, url):
    """Check crawler groups and longest matching path, including * and trailing $."""
    groups, agents, rules = [], [], []
    for line in source.splitlines():
        key, separator, value = line.split('#', 1)[0].partition(':')
        if not separator:
            continue
        key, value = key.strip().lower(), value.strip()
        if key == 'user-agent':
            if rules:
                groups.append((agents, rules))
                agents, rules = [], []
            agents.append(value.lower())
        elif key in ('allow', 'disallow') and agents:
            rules.append((key, value))
    if agents:
        groups.append((agents, rules))
    matches = []
    for agents, rules in groups:
        specificity = max((0 if agent == '*' else len(agent)
                           for agent in agents if agent == '*' or agent in user_agent.lower()), default=-1)
        if specificity >= 0:
            matches.append((specificity, rules))
    if not matches:
        return True
    best_group = max(specificity for specificity, _ in matches)
    parsed = urlsplit(url)
    path = parsed.path + (('?' + parsed.query) if parsed.query else '')
    decisions = []
    for specificity, rules in matches:
        if specificity != best_group:
            continue
        for directive, pattern in rules:
            if not pattern:
                continue
            expression = re.escape(pattern).replace(r'\*', '.*')
            if pattern.endswith('$'):
                expression = expression[:-2] + '$'
            if re.match(expression, path):
                decisions.append((len(pattern.replace('*', '').rstrip('$')), directive == 'allow'))
    return max(decisions, default=(0, True))[1]


class Page(HTMLParser):
    def __init__(self, source):
        super().__init__(convert_charrefs=True)
        self.titles, self.descriptions, self.canonicals = [], [], []
        self.robots, self.links, self.images, self.schemas, self.json_errors = [], [], [], [], []
        self.ids, self.h1, self.meta, self.visible = set(), 0, {}, []
        self.refresh, self.lang = None, ''
        self._title, self._script, self._hidden = None, None, 0
        self.feed(source)

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == 'html':
            self.lang = a.get('lang', '')
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
        if tag in ('img', 'script', 'video', 'audio', 'source', 'track') and a.get('src'):
            self.images.append(a['src'])
        if tag in ('img', 'video', 'audio', 'source') and a.get('data-src'):
            self.images.append(a['data-src'])
        if tag == 'video' and a.get('poster'):
            self.images.append(a['poster'])
        if tag in ('img', 'source'):
            for attribute in ('srcset', 'data-srcset'):
                self.images.extend(srcset_urls(a.get(attribute, '')))
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
        return self.refresh is not None


def all_pages(root=ROOT):
    return {p.relative_to(root).as_posix(): Page(p.read_text(encoding='utf-8'))
             for p in sorted(root.rglob('*.html'))
             if not any(part.startswith('.') for part in p.relative_to(root).parts)}


def public_pages(root=ROOT):
    """Content pages; redirects have separate routing checks in audit()."""
    pages = all_pages(root)
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


def absolute_web_url(value):
    if not isinstance(value, str):
        return False
    try:
        parsed = urlsplit(value)
        return parsed.scheme in ('https', 'http') and bool(parsed.netloc)
    except ValueError:
        return False


def redirect_destinations(pages, errors, warnings):
    """Validate migration stubs even though they are excluded from the sitemap."""
    targets = {}
    for path, page in pages.items():
        if not page.is_redirect:
            continue
        match = re.fullmatch(r'\s*(\d+(?:\.\d+)?)\s*;\s*url\s*=\s*(.+?)\s*', page.refresh, re.I)
        if not match:
            errors.append(f'{path}: invalid redirect refresh')
            continue
        delay, href = match.groups()
        href = href.strip('\'"')
        try:
            target = local_target(href, canonical_for(path))
        except ValueError:
            errors.append(f'{path}: invalid redirect URL {href}')
            continue
        if target is None:
            if absolute_web_url(urljoin(canonical_for(path), href)):
                warnings.append(f'{path}: external redirect destination requires manual review: {href}')
            else:
                errors.append(f'{path}: invalid redirect URL {href}')
            continue
        dest, fragment = target
        if dest not in pages:
            errors.append(f'{path}: redirect destination is not a local HTML page: {href}')
            continue
        targets[path] = dest
        if fragment and fragment not in pages[dest].ids:
            errors.append(f'{path}: redirect destination missing fragment {href}')
        if float(delay) != 0:
            warnings.append(f'{path}: delayed redirect; use an immediate migration redirect')
    for path in targets:
        visited, dest = {path}, targets[path]
        while dest in targets and dest not in visited:
            visited.add(dest)
            dest = targets[dest]
        if dest in visited:
            errors.append(f'{path}: redirect loop')
        elif pages[dest].is_redirect and dest not in targets:
            errors.append(f'{path}: redirect reaches an invalid migration stub')
        else:
            if pages[path].canonicals != [canonical_for(dest)]:
                errors.append(f'{path}: redirect canonical must match destination {canonical_for(dest)}')
            if len(visited) > 1:
                warnings.append(f'{path}: redirect chain; link directly to {canonical_for(dest)}')
    return targets


def schema_findings(node, path, root, pages, errors, warnings):
    types = node.get('@type', [])
    types = [types] if isinstance(types, str) else types
    if not isinstance(types, list):
        errors.append(f'{path}: JSON-LD @type must be a string or list')
        return
    if any(kind in types for kind in ('Article', 'BlogPosting', 'NewsArticle')) and not node.get('image'):
        warnings.append(f'{path}: Article has no representative image (recommended, not required)')
    dates = {}
    for field in ('datePublished', 'dateModified'):
        if field not in node:
            continue
        value = node[field]
        try:
            if not isinstance(value, str):
                raise ValueError('not a string')
            parsed = date.fromisoformat(value) if len(value) == 10 else datetime.fromisoformat(value.replace('Z', '+00:00')).date()
            dates[field] = parsed
            if parsed > date.today():
                errors.append(f'{path}: future structured {field}')
        except ValueError:
            errors.append(f'{path}: invalid structured {field}')
    if 'datePublished' in dates and 'dateModified' in dates and dates['dateModified'] < dates['datePublished']:
        errors.append(f'{path}: structured dateModified precedes datePublished')
    if 'BreadcrumbList' not in types:
        return
    crumbs = node.get('itemListElement', [])
    if not isinstance(crumbs, list) or len(crumbs) < 2:
        errors.append(f'{path}: BreadcrumbList requires at least two items')
        return
    for position, crumb in enumerate(crumbs, start=1):
        if not isinstance(crumb, dict):
            errors.append(f'{path}: invalid breadcrumb item')
            continue
        if crumb.get('position') != position or isinstance(crumb.get('position'), bool):
            errors.append(f'{path}: breadcrumb positions must be consecutive from 1')
        if not isinstance(crumb.get('name'), str) or not crumb['name'].strip():
            errors.append(f'{path}: breadcrumb name missing')
        item = crumb.get('item')
        if item is None and position == len(crumbs):
            continue  # Google allows the current (last) crumb to omit its URL.
        if isinstance(item, dict):
            item = item.get('@id', item.get('url'))
        if not absolute_web_url(item):
            errors.append(f'{path}: breadcrumb item must be an absolute web URL')
            continue
        target = local_target(item, canonical_for(path))
        if target:
            dest, fragment = target
            if not (root / dest).is_file():
                errors.append(f'{path}: broken breadcrumb URL {item}')
            elif dest in pages and fragment and fragment not in pages[dest].ids:
                errors.append(f'{path}: breadcrumb missing fragment {item}')


def audit(root=ROOT):
    parsed_pages = all_pages(root)
    pages = {path: page for path, page in parsed_pages.items() if not page.is_redirect}
    errors, warnings, inventory = [], [], []
    redirects = redirect_destinations(parsed_pages, errors, warnings)
    try:
        robots = (root / 'robots.txt').read_text(encoding='utf-8')
    except OSError as exc:
        errors.append(f'robots.txt: {exc}')
        robots = ''
    for path, page in parsed_pages.items():
        if page.is_redirect:
            for crawler in ('Googlebot', 'Bingbot'):
                if not robots_allows(robots, crawler, canonical_for(path)):
                    errors.append(f'{path}: robots.txt blocks {crawler} from a migration redirect')
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
            if not page.lang.strip():
                warnings.append(f'{path}: missing HTML language declaration')
            if not re.search(r'\bwidth\s*=\s*device-width\b', page.meta.get('viewport', ''), re.I):
                warnings.append(f'{path}: missing responsive viewport')
            for crawler in ('Googlebot', 'Bingbot'):
                if not robots_allows(robots, crawler, base):
                    errors.append(f'{path}: robots.txt blocks {crawler} from an indexable page')
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
                schema_findings(node, path, root, parsed_pages, errors, warnings)
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
        assets = page.images + [page.meta.get('og:image', ''), page.meta.get('twitter:image', '')]
        for href in page.links + assets:
            if not href:
                continue
            try:
                target = local_target(href, base)
            except ValueError:
                errors.append(f'{path}: invalid URL {href}')
                continue
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
            elif dest in redirects and href in page.links:
                warnings.append(f'{path}: internal link uses redirect {href}; use {canonical_for(redirects[dest])}')
                incoming[redirects[dest]].add(path)
            if page.indexable and href in assets and not robots_allows(robots, 'Googlebot', urljoin(base, href)):
                errors.append(f'{path}: robots.txt blocks Googlebot from local asset {href}')
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
    if not re.search(r'^\s*Sitemap:\s*' + re.escape(ORIGIN + '/sitemap.xml') + r'\s*$', robots, re.I | re.M):
        errors.append('robots.txt: canonical sitemap declaration missing')
    return {'pages': len(pages), 'redirects': sum(p.is_redirect for p in parsed_pages.values()),
            'indexable': sum(p.indexable for p in pages.values()),
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
