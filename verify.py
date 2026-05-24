#!/usr/bin/env python3
"""Growth-Copy Harness — structural verifier (computational sensor).
Opens a generated landing page in Chromium and runs the 8 structural assertions
from feature_list.json. Writes evidence (screenshot + results JSON) to evidence/<variant>/.
Usage: python3 verify.py <variant>   e.g. python3 verify.py variant-a
"""
import sys, json, os
from pathlib import Path
from playwright.sync_api import sync_playwright

def run(variant):
    page_path = Path(f"output/{variant}/index.html").resolve()
    if not page_path.exists():
        print(f"FAIL: {page_path} does not exist. Build the page first.")
        sys.exit(1)

    ev_dir = Path(f"evidence/{variant}")
    ev_dir.mkdir(parents=True, exist_ok=True)
    results = {}

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1280, "height": 800})
        page.goto(page_path.as_uri())

        # S1: viewport meta tag
        results["S1"] = page.locator("meta[name=viewport]").count() > 0

        # S2: a primary CTA above the fold (within first 700px)
        cta = page.locator(".cta-primary, #cta-primary").first
        if cta.count() > 0:
            box = cta.bounding_box()
            results["S2"] = bool(box and box["y"] < 700)
        else:
            results["S2"] = False

        # S3: exactly one <h1>
        results["S3"] = page.locator("h1").count() == 1

        # S4: every information-bearing visual (img AND inline svg) has an accessible label.
        # img -> non-empty alt. inline svg -> aria-label, OR role=img + a <title>,
        # OR explicitly decorative (aria-hidden=true). Anything else is a violation.
        imgs = page.locator("img")
        n = imgs.count()
        imgs_ok = all((imgs.nth(i).get_attribute("alt") or "").strip() != "" for i in range(n))

        svgs = page.locator("svg")
        m = svgs.count()
        def svg_ok(el):
            if (el.get_attribute("aria-hidden") or "").lower() == "true":
                return True  # explicitly decorative -> fine
            if (el.get_attribute("aria-label") or "").strip() != "":
                return True  # has an accessible name
            if (el.get_attribute("role") or "").lower() == "img" and el.locator("title").count() > 0:
                return True  # role=img + a <title> element
            return False
        svgs_ok = all(svg_ok(svgs.nth(i)) for i in range(m))

        results["S4"] = imgs_ok and svgs_ok

        # S5: schema.org JSON-LD block present
        results["S5"] = page.locator("script[type='application/ld+json']").count() > 0

        # S6: exactly one primary CTA
        results["S6"] = page.locator(".cta-primary, #cta-primary").count() == 1

        # S7: no horizontal scroll at 375px width
        page.set_viewport_size({"width": 375, "height": 800})
        overflow = page.evaluate("() => document.documentElement.scrollWidth > document.documentElement.clientWidth")
        results["S7"] = not overflow
        page.set_viewport_size({"width": 1280, "height": 800})

        # S8: no remote <script src>
        srcs = page.eval_on_selector_all("script[src]", "els => els.map(e => e.getAttribute('src'))")
        results["S8"] = all(not (s.startswith("http://") or s.startswith("https://") or s.startswith("//")) for s in srcs)

        page.screenshot(path=str(ev_dir / "screenshot.png"), full_page=True)
        browser.close()

    (ev_dir / "structural_results.json").write_text(json.dumps(results, indent=2))
    passed = sum(1 for v in results.values() if v)
    print(f"=== Structural verification: {variant} ===")
    for k in sorted(results): print(f"  {k}: {'PASS' if results[k] else 'FAIL'}")
    print(f"  -> {passed}/{len(results)} structural criteria pass")
    print(f"  Evidence written to {ev_dir}/ (screenshot.png, structural_results.json)")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 verify.py <variant>"); sys.exit(1)
    run(sys.argv[1])
