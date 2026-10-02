"""Write assets/ats-skills.json: the skill dictionary and role figures the ATS checker reads in the browser.

The dictionary is ApplySarthi's own (Job-Hunt jobhunt/skillvocab.py), so a skill counts in the checker exactly
when it counts on ApplySarthi's job pages. Job-Hunt is a separate, private repository checked out beside this
one; CI does not have it, so this script is run by hand when the vocabulary changes, and the result is
committed. tests/test_ats_pages.py checks the role half against scripts/apply_pages/ats.py.

    python scripts/export_ats_skills.py                      # ../Job-Hunt/jobhunt/skillvocab.py
    python scripts/export_ats_skills.py --vocab path/to/skillvocab.py
    python scripts/export_ats_skills.py --check              # fail if the JSON is stale
"""
import argparse
import importlib.util
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'assets/ats-skills.json'
DEFAULT_VOCAB = ROOT.parent / 'Job-Hunt/jobhunt/skillvocab.py'

sys.path.insert(0, str(Path(__file__).resolve().parent))


def load_vocab(path):
    spec = importlib.util.spec_from_file_location('skillvocab', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def render(vocab_module):
    from apply_pages.ats import ROLES, SNAPSHOT, roles_json
    ambiguous = {}
    for canon, rx in vocab_module.AMBIGUOUS.items():
        unsupported = rx.flags & ~(re.I | re.U)
        if unsupported:
            raise ValueError(f'{canon}: regex flags {unsupported} have no JavaScript equivalent')
        ambiguous[canon] = [rx.pattern, 'i' if rx.flags & re.I else '']
    data = {
        'about': 'Skill dictionary from ApplySarthi (jobhunt/skillvocab.py) and the role figures printed on '
                 'interviewsarthi.com/apply/ats-resume-checker/. Written by scripts/export_ats_skills.py.',
        'roles_read': SNAPSHOT,
        'max_scan': vocab_module.MAX_SCAN,
        'vocab': vocab_module.VOCAB,
        'ambiguous': ambiguous,
        'roles': roles_json(),
    }
    assert [r['slug'] for r in ROLES] == list(data['roles'])
    return json.dumps(data, ensure_ascii=False, indent=1) + '\n'


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--vocab', type=Path, default=DEFAULT_VOCAB)
    ap.add_argument('--check', action='store_true')
    args = ap.parse_args()
    if not args.vocab.is_file():
        sys.exit(f'No skill dictionary at {args.vocab}; pass --vocab')
    wanted = render(load_vocab(args.vocab))
    if args.check:
        if not OUT.is_file() or OUT.read_text(encoding='utf-8') != wanted:
            sys.exit('assets/ats-skills.json is stale: run python scripts/export_ats_skills.py')
        print('assets/ats-skills.json matches the skill dictionary and the role pages.')
        return
    OUT.write_text(wanted, encoding='utf-8')
    print(f'Wrote {OUT.relative_to(ROOT)}: {len(json.loads(wanted)["vocab"])} skills, '
          f'{len(json.loads(wanted)["roles"])} roles.')


if __name__ == '__main__':
    main()
