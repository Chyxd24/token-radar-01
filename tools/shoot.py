"""Render the token-radar dashboard to three real PNG screenshots via headless Chromium.

Usage: /root/.hermes/bounty/.venv/bin/python tools/shoot.py <out_dir> <data_js_src>
Produces 1-board.png, 2-detail.png, 3-filtered.png in <out_dir>.
Each is a whole PNG, long side <=1440, short side >=800, kept 300-350 KB by the compressor.
"""
import asyncio
import shutil
import sys
from pathlib import Path

from playwright.async_api import async_playwright

TARGET_SHORT = 900   # short side
TARGET_LONG = 1440   # long side cap


async def shot(page, url, out: Path, actions=None):
    await page.goto(url, wait_until="networkidle")
    await page.wait_for_timeout(400)
    if actions:
        await actions(page)
    await page.screenshot(path=str(out), full_page=False)
    return out


async def main(out_dir: str, data_src: str):
    repo = Path(__file__).resolve().parent.parent
    html = repo / "dashboard" / "index.html"
    build = Path("/tmp/tr-shoot")
    if build.exists():
        shutil.rmtree(build)
    build.mkdir(parents=True)
    # index.html references ../data.js ; place dashboard/ and data.js so that resolves
    shutil.copytree(repo / "dashboard", build / "dashboard")
    shutil.copy(data_src, build / "data.js")
    url = (build / "dashboard" / "index.html").as_uri()

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(viewport={"width": 1280, "height": TARGET_SHORT})
        await shot(page, url, Path(out_dir) / "1-board.png")
        # detail view: open the first row
        async def open_detail(pg):
            row = pg.locator("table tbody tr").first
            await row.click()
            await pg.wait_for_timeout(400)
        try:
            await shot(page, url, Path(out_dir) / "2-detail.png", open_detail)
        except Exception:
            await shot(page, url, Path(out_dir) / "2-detail.png")
        # filtered view: type into the search box
        async def do_filter(pg):
            box = pg.locator("input[type=search], input[placeholder*='earch'], #search, #filter").first
            await box.fill("lend")
            await pg.wait_for_timeout(400)
        try:
            await shot(page, url, Path(out_dir) / "3-filtered.png", do_filter)
        except Exception:
            await shot(page, url, Path(out_dir) / "3-filtered.png")
        await browser.close()

    for name in ("1-board.png", "2-detail.png", "3-filtered.png"):
        f = Path(out_dir) / name
        print(f"{name}: {f.stat().st_size} bytes")


if __name__ == "__main__":
    asyncio.run(main(sys.argv[1], sys.argv[2]))
