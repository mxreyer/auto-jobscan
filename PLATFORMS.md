# Platforms

Everything about talking to job boards: which platform a careers page is built
on, what each one's API does that its documentation does not mention, and which
portals resist scripting altogether.

**You do not need this to use jobscan.** Read it when you are adding a company,
when a source starts behaving oddly, or when you want to know why a particular
adapter is written the way it is. The setup guide is in
[README.md](README.md); `/jobscan-connector` automates most of what follows.

Almost every finding here came from a real run rather than from documentation.
Where a platform's own docs contradict what it actually does, that is called
out — it happened more than once.

**Contents:** [Sources and kinds](#sources-and-kinds) ·
[`themuse`](#themuse) · [`himalayas`](#himalayas) ·
[`eightfold`](#eightfold) · [`paradox`](#paradox) ·
[Portals that resist scripting](#sources-that-dont-work-this-way) ·
[Finding the real board](#finding-the-real-board-behind-an-aggregator) ·
[Why no Adzuna](#why-there-is-no-adzuna-source)

---

## Sources and kinds

**`kind`** is which platform to talk to. Every adapter returns the same job
dict, so everything downstream — dedupe, prescreen, location filter, output —
is platform-agnostic.

### Only add sources that return full descriptions

This is the one hard rule about adding a source, and it was expensive to
learn. A truncated description is worse than none: the single most promising
*title* in one batch of capped listings described, in full, entirely different
work under a familiar name. It scored well on the excerpt and was worthless.

A few hundred characters is enough to notice a role and never enough to judge
one, so a feed that caps its text cannot feed the scorer. `jobscan.py` checks
for this after every run — if a source's median description is implausibly
short, or its text ends in ellipses, it says so — but the check is a safety
net, not a licence to add capped feeds and score them anyway.

The aggregator that forced this rule is written up at the end of this file.

### Kinds

First-party boards — the company's own ATS, always full descriptions:

| URL looks like | kind | config |
|---|---|---|
| `boards.greenhouse.io/X` | `greenhouse` | `token: X` |
| `jobs.lever.co/X` | `lever` | `token: X` |
| `jobs.ashbyhq.com/X` | `ashby` | `token: X` |
| `jobs.smartrecruiters.com/X` | `smartrecruiters` | `token: X` |
| `X.wdN.myworkdayjobs.com/SITE` | `workday` | `tenant: X, wd: wdN, site: SITE` |
| a `/api/jobs` feed | `phenom` | `base: https://careers.X.com` |
| a `/search-jobs` page | `radancy` | `base: https://jobs.X.com` |
| `careers.X.edu/cw/en-us/listing` | `pageup` | `base: https://careers.X.edu` |
| an Eightfold site | `eightfold` | `base: https://careers.X.com, domain: X.com` |
| a Paradox.ai careersite | `paradox` | `base: https://employment.X.edu` |
| a `careers-api.clearcompany.com` board | `clearcompany` | `site_id: <UUID>` |

(That table is first-party boards. The two aggregator kinds — `themuse` and
`himalayas` — are below.)

Aggregators — for employers whose own portal resists scripting, and for
reaching employers you would never have thought to track:

| kind | descriptions | tier | coverage | notes |
|---|---|---|---|---|
| `themuse` | **full** (~4k chars) | `scored` | metro + remote, all employers | no key required |
| `himalayas` | **full** (~4.9k chars) | `scored` | **remote-only**, ~104k roles | no key required |

The two do not overlap the way you would expect. The Muse indexes employers
against offices; Himalayas is remote-only, so it reaches remote-first companies
that have no office to be indexed against and therefore never appear on a metro
aggregator at all. Running both is not redundancy.

**Token names are not guessable.** One company's Greenhouse board turned out to
be `<name>-careers`, not `<name>` — three obvious guesses all 404'd before a web
search found it. If a probe fails, search for the real board before concluding
the company has none.

Unsure which platform? Fingerprint the careers page:

    curl -sL <careers-url> | grep -ioE 'myworkdayjobs|greenhouse|lever|ashby|icims|eightfold|avature|talentbrew|pageuppeople|brassring|paradox|smartrecruiters|successfactors|phenom|clearcompany|jobvite|workable|breezy|bamboohr|recruitee|teamtailor|jazzhr|dayforce|ultipro|taleo|applytojob'

Then `python3 jobscan.py --check` to confirm it answers.

**This list is the single most repeated cause of a wrong "no route" verdict**,
so treat a miss as inconclusive rather than as an answer. Twice now a board was
written off as a custom JS portal purely because its platform was absent from
the pattern — once for Paradox, once for ClearCompany, and the second one was
hiding 169 roles. Both names are in the list above *now*, which is exactly the
problem: the list is only ever complete for platforms already encountered.

A second, subtler way to miss one: **grep the raw HTML, not attribute
patterns.** One real ClearCompany board is injected by a script tag whose `src`
is *unquoted*, so a search for `src="..."` could not match it, while a plain
search for `clearcompany` would have.

Also read `<careers-url>/robots.txt` before concluding a portal is closed.
It enumerates the paths a site expects robots to use, and on at least one
Eightfold site it named the working API after the frontend's own endpoint had
returned 403.

`/jobscan-connector` does all of this for you, and checks the results.

### `themuse`

`location` and `category` accept **repeated values with OR semantics**, so one
query covers the whole target region. Iterating them separately means dozens of
requests per company and earns 504s. `levels` filters out internships and
entry-level.

Omit `company_query` and it becomes a **discovery** sweep across every employer
The Muse indexes. Mark such a source `"group": "discovery"`: it then draws on
`max_discovery` rather than `max_to_score`, so a sweep spanning 100 employers
cannot starve the boards you deliberately track, and it faces the stricter
`discovery_signal` / `discovery_block` prescreen. That asymmetry is deliberate —
you chose the tracked companies, so a weak title there still deserves a look;
open search is mostly roles with nothing to do with your profile.

There is **no free-text search parameter** — unknown params are silently
ignored rather than erroring — so titles are the only lever.

**Watch for the silent zero.** `category` filters against a field that some
employers simply do not populate. One tracked employer's postings carried *no
categories at all*, so a three-category filter excluded 100% of them and the
source returned `0` for months while still reporting `ok`. If a Muse source's
count drops to zero, test it in this order before assuming the employer stopped
hiring:

    company only            -> is it still indexed?
    company + categories    -> do its postings have categories?
    company + locations     -> is it just not in your regions?

A source returning `0` is not a failure the `--check` report can catch — it
prints `ok` either way.

### `himalayas`

Remote-only, ~108,000 roles, no key, descriptions inline (median ~4,900
characters). Multi-employer, so it must be marked `"group": "discovery"`.

**There are two endpoints, and picking the wrong one decides whether this
source is worth having.**

| endpoint | what it is | filtering |
|---|---|---|
| `/jobs/api` | newest-first firehose | none |
| `/jobs/api/search` | filtered search | `q`, `country`, `seniority`, `employment_type`, `company`, `timezone`, `sort` |

Set `queries` in config and the adapter uses **search**, one sweep per phrase,
deduped by `guid`. Omit it and you get browse. Measured on the same budget:

| | fetched | past locations | past prescreen |
|---|---|---|---|
| browse (no `queries`) | 400 | 265 | **1** |
| search (8 `queries`) | 283 | 283 | **60** |

The raw feed is overwhelmingly remote sales, support and marketing. **Always
set `queries`.**

Quirks, all verified by probing rather than taken from the docs:

- **`limit` is capped at 20** on both endpoints, so cost is one request per
  twenty roles. Budget with `pages` × number of queries.
- **`q` is fuzzy, and more words *broaden* the result set rather than
  narrowing it.** `q=engineer` returns 31 hits; `q=mechanical engineer`
  returns 147. It ranks across the terms instead of requiring all of them —
  the opposite of the Adzuna AND-matching trap, and the opposite of what you
  will assume. Write specific role phrases and let the dedupe absorb the
  overlap.
- **Browse paginates by cursor, search by 1-based `page`.** `nextCursor` is a
  keyset cursor (base64 `timestamp|id`) with zero overlap between pages.
  Browse `offset` is documented as deprecated and behaves like it — `offset=0`
  and `offset=20` returned four of the same jobs, because the feed shifts
  while you read it.
- **The two endpoints validate differently, which is a trap.** On browse,
  unknown params are silently ignored — pass `q` or `seniority` there and the
  returned ids all change, which *looks* like filtering, while
  `q=mechanical engineer` happily returns religion tutors. On search, a bad
  `seniority` or `sort` returns HTTP 400, but a bad `employment_type` is
  accepted quietly. **Never conclude a filter works because the ids changed;
  read the rows.**
- **`seniority` is `Senior`, not `Senior-level`** — the latter is a 400.
  Valid: `Entry-level`, `Mid-level`, `Senior`, `Manager`, `Director`,
  `Executive`.
- **`country`** accepts `US` / `USA` / `us` / `United States` interchangeably,
  and **includes** worldwide-eligible roles unless you also pass
  `exclude_worldwide`.
- **Upstream data refreshes every 24 hours**, so running more than daily
  fetches nothing new.

**Locations still need translating.** Himalayas reports *eligibility* as a
country list (`locationRestrictions`) rather than an office, so the adapter
maps it:

| `locationRestrictions` | emitted location |
|---|---|
| `[]` | `Remote` (worldwide) |
| `["United States", "Canada"]` | `Remote, United States` |
| `["Germany", "France"]` | `Remote, Germany, France` |

Two deliberate choices. Passing the raw field through would drop
**everything** — a bare `United States` matches no `WANTED` token and falls
through to the final reject rule, silently, looking exactly like an empty
source. And co-listed countries are dropped when the US is present, because a
role open to both the US and Canada would otherwise match `canada` in
`FOREIGN` and be rejected despite a US applicant being eligible. The
foreign-only case keeps every country so the filter can reject it for the
right reason.

### `eightfold`

The endpoint an Eightfold site's **own frontend** calls,
`/api/apply/v2/jobs`, returns `{"message": "Not authorized for PCSX"}` in its
list form without a session. That looks final, and it is not — `robots.txt`
commonly **allows** `/api/pcsx`, and

    /api/pcsx/search?domain=<company>.com&start=0&num=10

answers unauthenticated. Descriptions come from
`/api/pcsx/position_details?position_id=…`, one request per job, hydrated
lazily like Workday.

The lesson generalises: **a 403 on the obvious endpoint is not proof the data
is closed.** Read `robots.txt` — it enumerates the paths the site expects
robots to use.

Two constraints shape the config:

- **`num` is capped at 10** server-side no matter what you ask for, so a sweep
  costs one request per ten roles. Filter; do not enumerate a whole board.
- **`location` is radius-based and not repeatable.** Passing it twice keeps one
  value. Santa Clara, San Jose, Sunnyvale and San Francisco all return the same
  Bay Area bucket, so list **one city per region**, not one per office.

`query=` works as a keyword filter if you ever need to narrow further; `sort_by`
does not — it echoes back `distance` whatever you pass.

**It rate-limits.** Because of the `num=10` cap a full sweep is ~80 requests,
which is enough to earn a `429` — reliably so if anything else is hitting the
same host at the same time. Both the search and the hydrate call go through
`_get_retry()`, which backs off on 429/5xx and does *not* retry other 4xx.
Don't run two sweeps concurrently.

Job pages themselves may stay unreadable: a site setting `publishToGoogle:
false` has no JSON-LD to fall back on. The API is then the only route.

### `paradox`

A **Paradox.ai careersite** is not a bespoke JS portal, whatever it looks like:
every `/jobs` page is server-rendered with the entire result set in a
`window.__PRELOAD_STATE__` blob. Plain `urllib` with a normal User-Agent is
enough; there is no bot detection to be graceful about, because there is no
JavaScript in the path.

Parse the blob with `raw_decode` from the opening brace — it is not terminated
predictably enough to regex the closing one.

List rows carry no description; the detail page does, in a
`.job-description-content` container. Its JSON-LD block is **not** usable —
unescaped control characters inside the description make it fail `json.loads`
even with `strict=False`. Use the container.

Pages hold ten roles each, so a full sweep of a few hundred is cheap.
`?keyword=` works if you want to narrow it.

## Sources that don't work this way

Some first-party portals are genuinely unscriptable, and the honest move is to
record *what was tried* rather than "doesn't work". Keep that table in
`config.json` under `_manual`. Failure modes seen so far:

| Platform | How it fails |
|---|---|
| Akamai-fronted, CSRF-tokened sites | job pages are JS shells with no JSON-LD |
| Avature | `/search-jobs/results` 404s; `/careers/api/jobs` serves the SPA shell, not JSON |
| BrassRing | `ProcessSortAndShowMoreJobs` answers but returns a fixed handful of featured jobs with `Total=0`; the documented `MatchedJobs` endpoint 500s even with a session cookie |
| SuccessFactors | no public feed found |

For those, an aggregator (`themuse`) or a saved-search email alert on the
company's own portal are the realistic options.

**But re-test before you believe it.** Two portals sat in this table as
"nothing works" for an entire session and neither upstream site had changed —
the earlier verdicts were simply wrong. One was solved by reading `robots.txt`;
the other was never a custom portal at all, just a server-rendered Paradox site.
A negative result about a portal is only as good as the specific thing that was
tried. `robots.txt` plus a platform fingerprint are the two cheapest first
moves.

## Finding the real board behind an aggregator

**An aggregator's posting often contains a link to the employer's real ATS.**
Phenom careers sites embed their data in a `phApp.ddo` blob, and each job there
carries an `applyUrl`. In one case that field revealed an employer already
covered as an aggregator source was a **Workday** shop — swapping `kind` gave
**502 roles with full descriptions instead of 28 filtered to zero**, using an
adapter that already existed.

Before adding an aggregator source for an employer, look at one of its postings
for an `applyUrl`, `apply_url` or outbound apply link — it names the ATS for
free.

Note the limit: **The Muse does not expose this.** Its `landing_page` always
points back to themuse.com, so the trick works from Phenom-style feeds, not
from Muse.

(A warning if you try to automate this: grepping descriptions for ATS names
gives false positives — `lever` matches inside "leverage".)

## Why there is no Adzuna source

Adzuna was dropped, after checking
whether its 500-character cap could be worked around at all. It cannot:

- `description` is capped at **exactly 500 characters** with a trailing
  ellipsis, and it is the **only** text field on the result object.
- There is **no per-job detail endpoint** — every URL variant 404s.
- `redirect_url` does not lead to the employer. It lands on an Adzuna
  interstitial that JavaScript-redirects through `air-api.jobiqo.com` to
  **`career.io`**, another aggregator, which answers scripted requests with
  `202` and "we need to verify that you're not a robot".
- `adzuna.com` itself returns 403 to scripted requests.

So the cap is structural, not a parameter. Since capped text cannot be scored,
Adzuna's entire contribution was a title-level list — and its last run produced
exactly one row. The cost of keeping it was credentials, a gitignored file, and
a whole tier of machinery; the benefit did not justify it. Removing it also
left the project needing **no credentials at all**.
