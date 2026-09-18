"""Content for the ApplySarthi pages, wrapped by scripts/build_apply_pages.py."""
from .guides import PAGES as GUIDE_PAGES
from .pillars import PAGES as PILLAR_PAGES
from .versus import PAGES as VERSUS_PAGES

PAGES = PILLAR_PAGES + GUIDE_PAGES + VERSUS_PAGES
