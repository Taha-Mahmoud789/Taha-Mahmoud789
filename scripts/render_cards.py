"""Render README project panels from real screenshots. Requires Python Playwright."""
from pathlib import Path
from tempfile import TemporaryDirectory
from playwright.sync_api import sync_playwright
ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'assets'
PROJECTS = [
    ('over-benefits', 'Over Benefits', 'Bilingual company website', True),
    ('atheer', 'Atheer Digital', 'Digital agency website', False),
    ('portfolio', 'taha.dev', 'Personal portfolio', False),
]
with TemporaryDirectory() as temp, sync_playwright() as p:
    browser = p.chromium.launch()
    for slug, title, description, featured in PROJECTS:
        width, height = (1200, 570) if featured else (590, 530)
        source = (ASSETS / (slug + '.jpg')).as_uri()
        content = f'''<!doctype html><html><meta charset="utf-8"><style>
        *{{box-sizing:border-box}}body{{margin:0;background:#f4efe5;color:#232323;font-family:Arial,sans-serif;padding:32px;}}
        .browser{{border:1px solid #655f56;border-radius:9px;overflow:hidden;background:#e8e1d6;}}
        .bar{{height:28px;display:flex;gap:6px;align-items:center;padding:0 12px;border-bottom:1px solid #bcb4a8;}}
        .dot{{width:7px;height:7px;border-radius:50%;background:#d66732;}}.dot:nth-child(2){{background:#b3a06e}}.dot:nth-child(3){{background:#77826c}}
        .url{{font-size:10px;color:#655f56;margin-left:12px;letter-spacing:.5px}}
        img{{display:block;width:100%;height:auto}}
        h2{{margin:20px 0 8px;font-size:{'40' if featured else '30'}px;letter-spacing:-1px;}}
        p{{margin:0;font-size:19px;line-height:1.5;}}
        .view{{margin-top:14px;font-size:18px;color:#a5431d;font-weight:bold;}}
        </style><div class="browser"><div class="bar"><i class="dot"></i><i class="dot"></i><i class="dot"></i><span class="url">{title}</span></div><img src="{source}"></div><div class="copy"><h2>{title}</h2><p>{description}</p><div class="view">View project ↗</div></div></html>'''
        if featured:
            content = content.replace('img{display:block;width:100%;height:auto}', 'img{display:block;width:100%;height:auto} body{display:grid;grid-template-columns: 2fr 1fr;gap:0 32px;align-content:center} .copy{display:flex;flex-direction:column;justify-content:center} h2{margin-top:0}')
        file = Path(temp) / (slug + '.html')
        file.write_text(content, encoding='utf-8')
        page = browser.new_page(viewport={'width':width,'height':height},device_scale_factor=2)
        page.goto(file.as_uri(),wait_until='networkidle')
        assert page.locator('img').evaluate('(el)=>el.complete && el.naturalWidth>0')
        page.screenshot(path=str(ASSETS/(slug+'-card.jpg')),type='jpeg',quality=90)
        page.close()
    browser.close()
