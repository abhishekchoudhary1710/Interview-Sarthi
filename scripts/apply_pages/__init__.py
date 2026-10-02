"""Content for the ApplySarthi pages, wrapped by scripts/build_apply_pages.py."""
from .ats import PAGES as ATS_PAGES
from .guides import PAGES as GUIDE_PAGES
from .pillars import PAGES as PILLAR_PAGES
from .versus import PAGES as VERSUS_PAGES

PAGES = PILLAR_PAGES + GUIDE_PAGES + VERSUS_PAGES + ATS_PAGES
