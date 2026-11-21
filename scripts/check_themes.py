"""Check README theme selection locally: python scripts/check_themes.py."""
import re
from pathlib import Path
from tempfile import TemporaryDirectory
from playwright.sync_api import sync_playwright
ROOT = Path(__file__).resolve().parents[1]
pictures = re.findall(r'<picture>.*?</picture>', (ROOT / 'README.md').read_text(encoding='utf-8'), re.S)
assert len(pictures) == 6
with TemporaryDirectory() as temp, sync_playwright() as p:
    preview = Path(temp) / 'themes.html'
    preview.write_text('<!doctype html><meta charset="utf-8"><base href="'+ROOT.as_uri()+'/"><style>img{max-width:100%;height:auto}</style>'+''.join(pictures),encoding='utf-8')
    browser = p.chromium.launch()
    page = browser.new_page(viewport={'width':390,'height':844})
    page.goto(preview.as_uri(),wait_until='networkidle')
    for theme in ['light', 'dark', 'light']:
        page.emulate_media(color_scheme=theme)
        page.wait_for_function('(theme)=>[...document.querySelectorAll("picture img")].every(i=>i.complete&&i.naturalWidth>0&&i.currentSrc.includes("-"+theme+"."))',arg=theme)
        assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
        print('PASS theme:',theme)
    browser.close()
