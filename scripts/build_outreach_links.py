"""Build the fixed, non-personal campaign codes accepted by assets/analytics.js."""
import argparse
import csv
from pathlib import Path
from urllib.parse import urlencode

CHANNELS = {
    'linkedin': ('social', 'post'),
    'reddit': ('referral', 'community'),
    'facebook': ('referral', 'community'),
    'career_creator': ('referral', 'review'),
    'career_newsletter': ('email', 'newsletter'),
}


def campaign_rows(slot=1):
    if slot not in range(1, 6):
        raise ValueError('Use a placement slot from 1 to 5.')
    for market in ('us', 'uk'):
        for product in ('live', 'prep'):
            for role in ('software', 'data', 'cloud'):
                for source, (medium, placement) in CHANNELS.items():
                    campaign = f'international_{market}_{product}'
                    content = f'{role}-{placement}-{slot:02d}'
                    landing = 'live/international.html' if product == 'live' else 'prep/'
                    query = urlencode(dict(utm_source=source, utm_medium=medium,
                                          utm_campaign=campaign, utm_content=content))
                    yield dict(target_market=market, product=product, role=role,
                               source=source, medium=medium, campaign=campaign,
                               content=content, slot=slot, status='draft',
                               assigned_placement='',
                               url=f'https://interviewsarthi.com/{landing}?{query}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir', type=Path, required=True)
    parser.add_argument('--slot', type=int, choices=range(1, 6), default=1)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    rows = list(campaign_rows(args.slot))
    target = args.output_dir / f'campaign-links-{args.slot:02d}.csv'
    with target.open('w', newline='', encoding='utf-8') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    print(f'Wrote {len(rows)} draft campaign links to {target}')
