"""The ATS resume checker pages and the data file the browser reads must say the same thing."""
import json
from pathlib import Path
import re
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from apply_pages.ats import ROLES, roles_json  # noqa: E402


class AtsPagesTests(unittest.TestCase):
    def setUp(self):
        self.data = json.loads((ROOT / 'assets/ats-skills.json').read_text(encoding='utf-8'))

    def test_browser_roles_match_the_pages(self):
        # The picker in the browser and the tables on the pages are the same snapshot.
        self.assertEqual(self.data['roles'], roles_json())

    def test_skill_dictionary_is_present_and_portable(self):
        self.assertGreater(len(self.data['vocab']), 100)
        for canon, (pattern, flags) in self.data['ambiguous'].items():
            self.assertIn(canon, self.data['vocab'])
            self.assertIn(flags, ('', 'i'))
            self.assertNotIn('(?P', pattern)          # Python-only syntax would break in the browser
        for role in self.data['roles'].values():
            for skill, share in role['skills']:
                self.assertIn(skill, self.data['vocab'], skill)
                self.assertTrue(0 < share <= 100)

    def test_every_role_page_carries_the_tool_preset_to_its_role(self):
        main = (ROOT / 'apply/ats-resume-checker/index.html').read_text(encoding='utf-8')
        self.assertIn('data-role=""', main)
        for asset in ('ats-checker.css', 'ats-engine.js', 'ats-checker.js'):
            self.assertIn(f'../../assets/{asset}', main)
            self.assertTrue((ROOT / 'assets' / asset).is_file(), asset)
        for r in ROLES:
            page = (ROOT / f'apply/ats-resume-checker/{r["slug"]}.html').read_text(encoding='utf-8')
            self.assertIn(f'href="{r["slug"]}.html"', main)
            self.assertIn(f'data-role="{r["slug"]}"', page)
            self.assertIn(f'<option value="{r["slug"]}" selected>', page)
            self.assertEqual(page.count(' selected>'), 1)
            for skill, share in r['skills']:
                self.assertIn(f'<td>{share:.1f}%</td>', page)
            self.assertIn(f'{r["postings"]:,} open', page)

    def test_the_engine_loads_before_the_page_script(self):
        page = (ROOT / 'apply/ats-resume-checker/index.html').read_text(encoding='utf-8')
        scripts = re.findall(r'<script defer src="[^"]*/(ats-[a-z]+\.js)"', page)
        self.assertEqual(scripts, ['ats-engine.js', 'ats-checker.js'])

    def test_no_page_promises_what_an_ats_does_not_do(self):
        # The ATS guide says systems store and search, they do not score or auto-reject.
        for path in (ROOT / 'apply/ats-resume-checker').glob('*.html'):
            text = path.read_text(encoding='utf-8').lower()
            self.assertNotIn('auto-reject', text, path.name)
            self.assertNotIn('beat the ats', text, path.name)
            self.assertNotIn('75%', text, path.name)


if __name__ == '__main__':
    unittest.main()
