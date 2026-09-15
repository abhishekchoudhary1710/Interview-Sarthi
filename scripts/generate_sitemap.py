"""Generate canonical sitemap from the reviewed page manifest, never from build time.

After a meaningful page edit: --record path/to/page.html --date YYYY-MM-DD.
Then run without arguments to write, or --check to detect drift in CI.
"""
import argparse
from datetime import date
import json
from pathlib import Path
import sys
import xml.etree.ElementTree as ET
from seo_audit import ROOT, Page, canonical_for

CONFIG = ROOT / 'scripts/seo_pages.json'
NAMESPACE = 'http://www.sitemaps.org/schemas/sitemap/0.9'


def render(root=ROOT, config=None):
    records = config if config is not None else json.loads(CONFIG.read_text(encoding='utf-8'))
    ET.register_namespace('', NAMESPACE)
    tree = ET.Element('{' + NAMESPACE + '}urlset')
    for path, modified in sorted(records.items(), key=lambda pair: canonical_for(pair[0])):
        target = (root / path).resolve()
        if not target.is_relative_to(root.resolve()) or not target.is_file():
            raise ValueError(f'Not a public file: {path}')
        page = Page(target.read_text(encoding='utf-8'))
        canonical = canonical_for(path)
        if not page.indexable or page.canonicals != [canonical] or path in ('404.html', 'thanks.html'):
            raise ValueError(f'Not an indexable canonical page: {path}')
        if modified and date.fromisoformat(modified) > date.today():
            raise ValueError(f'Future lastmod: {path}')
        url = ET.SubElement(tree, 'url')
        ET.SubElement(url, 'loc').text = canonical
        if modified:
            ET.SubElement(url, 'lastmod').text = modified
    ET.indent(tree, space='  ')
    return '<?xml version="1.0" encoding="UTF-8"?>\n' + ET.tostring(tree, encoding='unicode') + '\n'


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    parser.add_argument('--record', help='Review/add one page in the allow-list')
    parser.add_argument('--date', help='Actual meaningful content-change date')
    args = parser.parse_args()
    try:
        if args.record:
            if args.check or not args.date:
                parser.error('--record requires --date and cannot be used with --check')
            config = json.loads(CONFIG.read_text(encoding='utf-8'))
            config[args.record] = args.date
            render(config=config)  # Validate before modifying config.
            CONFIG.write_text(json.dumps(config, indent=2, sort_keys=True)+'\n', encoding='utf-8')
        output = render()
        dest = ROOT / 'sitemap.xml'
        if args.check:
            if dest.read_text(encoding='utf-8') != output:
                sys.exit('Sitemap differs: run python scripts/generate_sitemap.py')
            print('Sitemap matches the reviewed page manifest.')
        else:
            dest.write_text(output, encoding='utf-8')
            print('Wrote sitemap.xml from reviewed page dates.')
    except (ValueError, OSError) as exc:
        sys.exit(str(exc))
