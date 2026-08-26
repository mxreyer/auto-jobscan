---
name: jobscan-connector
description: Add a company to jobscan's config.json — work out which ATS platform it uses, derive the identifiers, verify with a real request, and wire it in. Use when the user wants to track a specific employer, asks which job board a company uses, says a source is failing or returning zero, or wants to re-test a company previously recorded as unreachable.
---

# Adding a jobscan connector

A **connector** is one entry in the `companies` array of `config.json`. Adding
one means answering two questions: *which ATS does this company use*, and
*what identifiers does that adapter need*.

Both are quick. Both are also easy to get confidently wrong, which is what
most of this file is about.

The company (and careers URL, if given) come from the invocation. If only a
name was given, find the careers page first. Read `PLATFORMS.md` (the "Kinds"
table, and the per-platform quirks) and `adapters.py` before starting.

## Ground rules

1. **Verify by reading rows, never by reading status codes.** Every trap below
   is a request that succeeded and returned the wrong thing.
2. **Never guess a token twice.** If the obvious one fails, web-search for the
   real board URL. Guessing is how you end up with a working connector
   pointed at a different company.
3. **Read-only, public endpoints, no credentials, one request at a time.**
   This tool does not log in and does not apply.

---

## Phase 1 — Identify the platform

Fingerprint the careers page:

    curl -sL <URL> | grep -ioE 'myworkdayjobs|greenhouse|lever|ashby|icims|eightfold|avature|talentbrew|pageuppeople|brassring|paradox|smartrecruiters|successfactors|phenom|clearcompany|jobvite|workable|breezy|bamboohr|recruitee|teamtailor|jazzhr|dayforce|ultipro|taleo|applytojob'

**A miss here is inconclusive, not an answer.** This pattern list is the most
repeated cause of a wrong "no route" verdict in this project — twice a board
was written off as a custom portal purely because its platform was not in it,
and the second time that hid 169 roles. Grep the **raw HTML** for the platform
names rather than matching attribute patterns: one real board is injected by a
script tag with an *unquoted* `src`, which `src="..."` cannot match.

Then, in order of how often they pay off:

- **Follow the redirect chain and any "apply" link.** A marketing careers page
  frequently redirects to the real ATS, and the apply link almost always does.
  A Workday tenant is usually sitting in the page HTML as a
  `tenant.wdN.myworkdayjobs.com/SITE` URL — that is the cheapest way to get
  `tenant` and `site` together.
- **Read `<URL>/robots.txt`.** It enumerates the paths the site expects robots
  to use. On one Eightfold site it named the working API (`/api/pcsx`) after
  the frontend's own endpoint returned 403 — see "a 403 is not proof" below.
- **If the company already appears via an aggregator, look at that posting's
  `applyUrl`.** Aggregators link to the employer's real ATS, naming the
  platform for free. (The Muse is the exception: its `landing_page` always
  points back to themuse.com.)

Report what each step returned before moving on.

## Phase 2 — Derive the identifiers

Map the URL to a `kind` using the table in `PLATFORMS.md`. Then:

**Tokens are not guessable and are case-sensitive.** Real examples: one board
is `thriveMarket`, not `thrivemarket`; another company's Greenhouse token was
`<name>-careers` after three obvious guesses 404'd. If the obvious token
fails, search for the real board URL rather than trying a fourth spelling.

## Phase 3 — Verify with a real request

**Do this before writing anything to config.** Fetch the list endpoint, and
report the role count, one title, and one location.

Then check it against the four ways this step lies to you:

- **A token that resolves to the wrong company.** The failure that actually
  happened here: Ashby `clera` returns 300 marketing and intern roles for an
  unrelated company, and `foundation` is a four-person design shop — neither
  was the employer being added. **Read the titles and confirm they look like
  the company you meant.**
- **SmartRecruiters returns HTTP 200 with `totalFound: 0` for an unknown
  token**, not a 404. Status code can never validate that source; compare the
  count against what the careers page shows.
- **Workday `422` means the tenant resolved but the site slug is wrong.** Take
  the slug from the real careers URL, do not invent it.
- **A healthy board can legitimately be empty.** One tracked source returns 200
  with zero open roles and that is a true state, not a failure. Distinguish
  "empty right now" from "wrong token" by checking the careers page.

**A 403 on the obvious endpoint is not proof the data is closed.** It may be
specific to the *list* form of an endpoint whose detail form works, and
`robots.txt` may advertise a different path entirely.

## Phase 4 — Wire it in and check

Add the entry to `config.json` (copy the shape from `_companies_examples` in
that file), then:

    python3 jobscan.py --check

Show the user the line for this company. **Read the count, not the flag** — a
source returning `0` still prints `ok`, and that is the one failure `--check`
cannot catch. If it is a `themuse` company source returning zero, run the
three-way test before concluding the employer stopped hiring:

    company only            -> is it still indexed?
    company + categories    -> do its postings carry categories at all?
    company + locations     -> is it just not in your regions?

The middle one is the usual culprit: `category` filters a field some employers
do not populate, so a category filter can exclude 100% of their postings
silently.

## Phase 5 — Look at what it actually contributed

Run `python3 jobscan.py --all`, then read `candidates.md`:

- **Did the new board flood the list?** A large board tends to bring roles that
  match a `signal` term by accident. The fix is to **tighten `block`, not to
  narrow `signal`** — narrowing `signal` drops real roles silently, while a bad
  block term announces itself the moment an expected title goes missing. Say
  what else any proposed pattern would catch.
  **Never block a learnable gap**, though: block hard gates (clearance,
  licence, work authorization), never the name of a tool the candidate would
  learn. See the "learnable gap" section of `SCORING.md`.
- **Are the locations real?** Workday hides multi-site postings behind
  `2 Locations`, which the location filter keeps by design. A board
  headquartered outside the user's regions can contribute a stack of
  candidates that are all secretly elsewhere. Flag it if that happens.
- **Judge the source by its Apply count, not its role count.** A 270-role board
  yielding two good roles a month earns its place; a 600-role board that has
  never produced an Apply does not.

## If no existing `kind` fits

Stop and tell the user which platform it is and what the list endpoint looks
like, before writing code. If they want the adapter:

Add a function to `adapters.py` following the shape of the existing ones — it
takes the config dict and returns a list of job dicts with the same keys, and
is registered in `ADAPTERS`. Two rules the existing adapters follow:

- **Every adapter returns the same job dict.** Dedupe, prescreen, the location
  filter and the output all depend on that uniformity.
- **Descriptions are hydrated lazily.** If the list endpoint omits them, add a
  `_hydrate_<kind>` and wire it into `hydrate()` rather than fetching per
  listed job. A 700-role board with 12 survivors should cost 12 description
  fetches, not 700.

For a multi-employer feed, **take the company name from the response row**, not
from `cfg["company"]` — using the config label collapses every employer into
one bucket and breaks both dedupe and the round-robin. Mark such a source
`"group": "discovery"`.

Show the list endpoint URL, one raw response, and the field mapping before
writing the function.

## If the company is genuinely unreachable

Record **what was tried** — the exact endpoints and how they failed — in the
`_manual` block of `config.json`. Not "doesn't work":

```json
"_manual": {
  "Example Co.": "BrassRing (partnerid=NNNNN). ProcessSortAndShowMoreJobs answers but returns a fixed 3 featured jobs with Total=0; the documented MatchedJobs endpoint 500s even with a session cookie. Not on The Muse. NO ROUTE."
}
```

That specificity is the whole value of the note. **A negative verdict is only
as good as the specific thing that was tried** — two portals in this project's
history sat in that table as "nothing works" for an entire session before a
re-test found a route that had been there all along, and neither upstream site
had changed. When a `NO ROUTE` entry starts mattering, re-derive it from
scratch rather than trusting it.

The realistic fallback for a truly closed portal is a saved-search email alert
on the company's own site.
