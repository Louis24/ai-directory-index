# ai-directory-index

A browser-verified audit of **235 AI and startup directories**, plus the outcome of
**2,700 real submission attempts** from 18 different sites.

Most "submit your product to 200 directories" lists are written by copying each
other. This one is a measurement: every directory was loaded in headless Chrome,
its form was inspected, and an attempt was counted as *accepted* only when the
response contained a receipt. HTTP 200 on its own counted as unknown, never as
success — which is the single most common way directory statistics get inflated.

## What the data says

| Measure | Value |
| --- | --- |
| Directories probed | 235 |
| Accept a fully automated submission | 46 (19.6%) |
| Single-input or field-less pages | 146 (62.1%) |
| Require an account before the form | 34 |
| Behind a CAPTCHA or challenge | 4 |
| Submission attempts | 2,700 |
| Attempts a directory accepted | 81 (3.0%) |
| Directories that ever accepted anything | **8 (3.4%)** |

The last row is the one that matters. 3.4% of the pool absorbed 100% of the
acceptances. The other 227 directories took the form, returned HTTP 200, and
produced nothing.

Breakdown by category:

| Category | Directories | Automatable | Rate |
| --- | --- | --- | --- |
| AI tool directories | 159 | 29 | 18% |
| Software / SaaS directories | 44 | 12 | 27% |
| General web directories | 26 | 5 | 19% |
| Local / business listings | 5 | 0 | 0% |
| Launch communities | 1 | 0 | 0% |

## Files

| File | Rows | What it is |
| --- | --- | --- |
| `data/ai-directories.csv` | 235 | one row per directory: category, entry URL, fillable field count, CAPTCHA flag, login wall, whether a fill was possible, rejection reason, attempts, acceptances |
| `data/ai-directories.json` | 235 | the same, plus summary block and metadata |
| `data/attempts.csv` | 2,700 | one row per submission attempt: timestamp, site, directory, verdict |
| `probe.py` | — | the read-only auditor that produced the field counts |

Column notes:

- `fillable_fields` counts visible inputs that are not hidden/submit/button. A
  value of `1` usually means a newsletter box or a site search, not a form.
- `auto_submit` is `true` only when at least two visible fields exist, at least
  one matches a known submission field (URL, name, email, description), and no
  login redirect or CAPTCHA appeared.
- `accepted` counts attempts whose response contained a thank-you message,
  pending-review notice, or email-verification prompt.

## Reproduce the probe

`probe.py` needs Playwright and only reads pages — it never submits anything.

```bash
pip install playwright && playwright install chromium
python probe.py --input domains.txt --out probed.csv
```

`domains.txt` is one hostname per line. The script loads each one, counts visible
fillable fields, follows a few candidate submission paths, and writes the same
columns used in `data/`. Expect roughly 15–25 seconds per domain; the slow part
is single-page sites that render their form after a client-side round trip.

## Caveats, stated plainly

- **One operator, one night.** 18 sites, one person, one batch of submissions.
  The acceptance column is a sample, not a census.
- **Acceptance is not a live link.** At the time of collection every submission
  was still in review and no listing had appeared. Some of those 81 will never
  be published.
- **The pool is not the whole web.** 159 of 235 are AI-tool directories because
  that is what the products were. A different product gets a different pool.
- **Judgement calls.** Some pages are ambiguous: a form that posts via `fetch()`
  and swaps the DOM has no receipt and no status code, so it lands in "unknown".
  That bucket is 8% of attempts and is the main source of error.

## Citation

Data: CC BY 4.0. Code: MIT. If you use this, link to the methodology page:

> Isaksson, L. *I submitted 18 sites to 235 AI directories: the data.*
> https://neonstack.net/reviews/ai-directory-submission-study/

Adding your own results to `data/attempts.csv` is welcome — PRs that add rows
with timestamps and verdicts are the whole point of publishing this.

## License

- Data (`data/*`, `*.json`): [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)
- Code (`probe.py`, `index.js`): MIT
