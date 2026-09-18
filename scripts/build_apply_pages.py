"""Render the ApplySarthi content pages from one template.

The ApplySarthi pages share their chrome with the rest of the site (assets/article.css), so the only
thing worth writing by hand is each page's own argument. Content lives in apply_pages/*.py; this
module wraps it, writes the files and leaves them in the tree as ordinary static HTML.

    python scripts/build_apply_pages.py            # write every page
    python scripts/build_apply_pages.py --check    # fail if a written page is stale (CI)
"""
import argparse
import html
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
ORIGIN = 'https://interviewsarthi.com'
# ApplySarthi's own share card. og.jpg pictures the Interview Sarthi overlay and belongs to that
# product's pages; rendered from assets/og-apply.source.html.
OG_IMAGE = ORIGIN + '/assets/og-apply.jpg'

sys.path.insert(0, str(Path(__file__).resolve().parent))


def canonical_for(path):
    return ORIGIN + '/' + (path[:-10] if path.endswith('index.html') else path)


def up(path):
    """Relative prefix back to the site root, e.g. apply/guides/x.html -> ../../"""
    return '../' * path.count('/')


def breadcrumbs(path, trail):
    items = [{'@type': 'ListItem', 'position': 1, 'name': 'Home', 'item': ORIGIN + '/'}]
    for i, (name, href) in enumerate(trail, start=2):
        items.append({'@type': 'ListItem', 'position': i, 'name': name, 'item': ORIGIN + href})
    return {'@type': 'BreadcrumbList', 'itemListElement': items}


def faq_schema(faq):
    return {
        '@type': 'FAQPage',
        'mainEntity': [
            {'@type': 'Question', 'name': q,
             'acceptedAnswer': {'@type': 'Answer', 'text': a}}
            for q, a in faq
        ],
    }


def article_schema(page, canonical):
    return {
        '@type': 'Article',
        '@id': canonical + '#article',
        'headline': page['h1'],
        'description': page['description'],
        'inLanguage': 'en-IN',
        'datePublished': page['published'],
        'dateModified': page['modified'],
        'author': {'@id': ORIGIN + '/#organization'},
        'publisher': {'@id': ORIGIN + '/#organization'},
        'isPartOf': {'@type': 'WebSite', '@id': ORIGIN + '/#website'},
        'about': {'@id': ORIGIN + '/apply/#software'},
        'mainEntityOfPage': canonical,
    }


def crumb_html(trail, prefix):
    parts = [f'<a href="{prefix or "/"}">Home</a>']
    for name, href in trail[:-1]:
        parts.append(f'<a href="{ORIGIN + href}">{html.escape(name)}</a>')
    parts.append(html.escape(trail[-1][0]))
    return ' › '.join(parts)


def render(page):
    path = page['path']
    canonical = canonical_for(path)
    prefix = up(path)
    graph = [breadcrumbs(path, page['trail']), article_schema(page, canonical)]
    if page.get('faq'):
        graph.append(faq_schema(page['faq']))
    graph.extend(page.get('schema', []))
    ld = json.dumps({'@context': 'https://schema.org', '@graph': graph}, indent=2, ensure_ascii=False)

    faq_html = ''
    if page.get('faq'):
        blocks = '\n'.join(
            f'<div class="qa"><p class="q">{html.escape(q)}</p><p class="a">{a}</p></div>'
            for q, a in page['faq'])
        faq_html = f'\n<h2 id="faq">Questions people ask</h2>\n{blocks}\n'

    more = '\n'.join(f'<a href="{href}">{html.escape(text)}</a>' for text, href in page['more'])
    t, d = html.escape(page['title']), html.escape(page['description'])
    return f"""<!doctype html>
<html lang="en">
<head>
<script>if(location.protocol==="http:"&&/interviewsarthi\\.com$/.test(location.hostname)){{location.replace("https://"+location.host+location.pathname+location.search+location.hash);}}</script>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{t}</title>
<meta name="description" content="{d}">
<meta name="robots" content="index, follow">
<link rel="canonical" href="{canonical}">
<meta property="og:title" content="{t}">
<meta property="og:description" content="{d}">
<meta property="og:url" content="{canonical}">
<meta property="og:type" content="article">
<meta property="og:site_name" content="Interview Sarthi">
<meta property="og:image" content="{OG_IMAGE}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{t}">
<meta name="twitter:description" content="{d}">
<meta name="twitter:image" content="{OG_IMAGE}">
<script type="application/ld+json">
{ld}
</script>
<link rel="icon" href="/favicon.ico" sizes="any"><link rel="icon" type="image/svg+xml" href="{prefix}assets/mark.svg"><link rel="icon" type="image/png" sizes="96x96" href="{prefix}assets/favicon-96.png"><link rel="icon" type="image/png" sizes="192x192" href="{prefix}assets/favicon-192.png"><link rel="apple-touch-icon" href="{prefix}assets/icon-512.png">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{prefix}assets/article.css">
<script defer src="{prefix}assets/analytics.js"></script>
<script defer src="{prefix}assets/wa.js"></script>
</head>
<body>
<div class="wrap">
<header class="top">
  <a class="logo" href="{prefix or '/'}"><img src="{prefix}assets/mark.svg" width="26" height="26" alt=""><span class="wm">Interview <i>Sarthi</i></span></a>
  <nav><a href="{prefix}apply/">ApplySarthi</a><a href="{prefix}apply/guides/">Applying guides</a><a href="{prefix}#pricing">Pricing</a><a href="{prefix}help.html">Help</a></nav>
</header>

<p class="crumb" aria-label="Breadcrumb">{crumb_html(page['trail'], prefix)}</p>
<h1>{html.escape(page['h1'])}</h1>
<p class="lead">{page['lead']}</p>
<p class="meta">{page['meta']}</p>

{page['body']}
{faq_html}
<div class="promo">
  <h3>{html.escape(page['cta_title'])}</h3>
  <p>{page['cta_text']}</p>
  <p><a class="cta" href="https://apply.interviewsarthi.com/">Open ApplySarthi</a> <a class="cta ghost" href="{prefix}apply/">What it does</a></p>
</div>

<div class="more">
  <h2>Keep reading</h2>
  {more}
</div>
</div>
<footer>
  <p><a href="{prefix}apply/">ApplySarthi</a> · <a href="{prefix}apply/guides/">Applying guides</a> · <a href="{prefix}apply/best-auto-apply-tools-india.html">Auto-apply tools compared</a> · <a href="{prefix}facts.html">Product facts</a> · <a href="{prefix}help.html">Help</a></p>
  © 2026 Interview Sarthi · <a href="{prefix or '/'}">Home</a> · <a href="{prefix}privacy.html">Privacy</a> · <a href="{prefix}terms.html">Terms</a> · <a href="{prefix}refunds.html">Refunds</a>
</footer>
</body>
</html>
"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--check', action='store_true', help='fail if any page on disk is stale')
    args = ap.parse_args()
    from apply_pages import PAGES
    stale = []
    for page in PAGES:
        target = ROOT / page['path']
        wanted = render(page)
        if args.check:
            if not target.exists() or target.read_text(encoding='utf-8') != wanted:
                stale.append(page['path'])
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(wanted, encoding='utf-8')
    if args.check:
        if stale:
            print('Stale generated pages: ' + ', '.join(stale), file=sys.stderr)
            return 1
        print(f'{len(PAGES)} ApplySarthi pages match their source.')
        return 0
    print(f'Wrote {len(PAGES)} ApplySarthi pages.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
