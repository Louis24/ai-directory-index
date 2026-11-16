#!/usr/bin/env python3
"""Read-only directory auditor.

Loads a directory page in a real browser and reports whether it has a form that
could be filled programmatically. It never submits, never registers and never
writes to any site: the only output is a CSV row describing what the page
exposes.

Why a browser instead of requests
--------------------------------
Half of these directories render their submission form after JavaScript runs,
and a handful refuse non-browser user agents outright. A plain GET on a
single-page directory returns a shell containing a search box, which is why
static probes report "62% of directories have one field" and mean nothing.

Usage
-----
    pip install playwright
    playwright install chromium
    python probe.py --input domains.txt --out probed.csv

domains.txt holds one hostname per line (comments with # are ignored).
"""
from __future__ import annotations

import argparse
import csv
import re
import sys
from pathlib import Path

# Where a submit form usually lives. Ordered by how often they hit.
CANDIDATES = ("/submit", "/submit/", "/submit-a-tool", "/add", "/listing/submit",
              "/submit-your-tool", "/pricing", "/")

ACCOUNT_RE = re.compile(r"/(login|signin|sign-in|signup|sign-up|register|auth)", re.I)

# Only visible, named, non-button inputs count. Hidden inputs are how a form
# carries state, not how a human fills it.
FIELDS_JS = r"""
() => {
  const vis = el => !!(el.offsetWidth || el.offsetHeight || el.getClientRects().length);
  const skip = new Set(['hidden','submit','button','reset','image','file']);
  return Array.from(document.querySelectorAll('input,textarea,select'))
    .filter(el => vis(el) && !skip.has((el.type || '').toLowerCase()))
    .map(el => ({
      name: el.name || el.id || '',
      type: (el.type || el.tagName).toLowerCase(),
      ph: el.placeholder || '',
      label: (el.id && document.querySelector(`label[for="${el.id}"]`)?.textContent || '').trim(),
      required: !!el.required
    }));
}
"""

CAPTCHA_SEL = ("iframe[src*='recaptcha'], iframe[src*='hcaptcha'], "
               "div[class*='cf-turnstile'], div[class*='g-recaptcha'], "
               "script[src*='challenges.cloudflare.com']")

FIELD_HINTS = {
    "url": ("url", "website", "link", "homepage", "domain", "site"),
    "name": ("name", "title", "product"),
    "email": ("email", "mail"),
    "description": ("description", "desc", "about", "tagline", "summary", "pitch"),
}


def classify(fields: list[dict], captcha: bool, url: str) -> str:
    """Return the verdict string used in data/ai-directories.csv."""
    if captcha:
        return "captcha"
    if ACCOUNT_RE.search(url):
        return "login wall"
    if len(fields) <= 1:
        return "too few fields"
    hay = " ".join((f["name"] + " " + f["ph"] + " " + f["label"]).lower() for f in fields)
    matched = sum(1 for k, hints in FIELD_HINTS.items() if any(h in hay for h in hints))
    if matched < 2:
        return "no recognisable submission fields"
    return "automatable"


def probe_one(pw, domain: str, timeout: int = 20000) -> dict:
    browser = pw.chromium.launch(headless=True)
    ctx = browser.new_context(viewport={"width": 1400, "height": 900},
                              user_agent=("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                                          "AppleWebKit/537.36 (KHTML, like Gecko) "
                                          "Chrome/131.0 Safari/537.36"))
    page = ctx.new_page()
    best = {"domain": domain, "entry": "", "fillable_fields": 0,
            "matched_fields": 0, "captcha": False, "verdict": "unreachable"}
    try:
        for path in CANDIDATES:
            url = f"https://{domain}{path}"
            try:
                resp = page.goto(url, timeout=timeout, wait_until="domcontentloaded")
            except Exception:
                continue
            if resp is None:
                continue
            page.wait_for_timeout(1200)
            fields = page.evaluate(FIELDS_JS) or []
            captcha = page.locator(CAPTCHA_SEL).count() > 0
            if len(fields) > best["fillable_fields"]:
                best.update({
                    "entry": page.url,
                    "fillable_fields": len(fields),
                    "captcha": captcha,
                    "verdict": classify(fields, captcha, page.url),
                })
            if best["verdict"] == "automatable":
                break
    finally:
        browser.close()
    return best


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True, help="file with one domain per line")
    ap.add_argument("--out", default="probed.csv")
    ap.add_argument("--timeout", type=int, default=20000)
    args = ap.parse_args()

    domains = [ln.strip() for ln in Path(args.input).read_text(encoding="utf-8").splitlines()
               if ln.strip() and not ln.startswith("#")]
    if not domains:
        sys.exit("no domains in input file")

    from playwright.sync_api import sync_playwright

    rows = []
    with sync_playwright() as pw:
        for i, d in enumerate(domains, 1):
            row = probe_one(pw, d, timeout=args.timeout)
            rows.append(row)
            print(f"{i:>3}/{len(domains)} {d:<34} {row['verdict']:<34} "
                  f"fields={row['fillable_fields']}", flush=True)

    with open(args.out, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print(f"\n{len(rows)} rows -> {args.out}")


if __name__ == "__main__":
    main()
