# auto-jobscan

Pulls open roles from company career portals and job aggregators, drops the
obvious noise, and hands the survivors to an LLM for scoring against your
profile — so you read twenty roles worth considering instead of two thousand
that are not.

It is **read-only** — it finds roles and ranks them; you apply to them
yourself.

**[`examples/shortlist.md`](examples/shortlist.md) is what it produces.** Read
that first; it will tell you in a minute whether this is for you. Then
[Caveats](#caveats) at the bottom, for what it does badly.

## How it works

    config.json ──▶ fetch every source          ~2,000 open roles
                    drop anything already seen
                    drop anything out of region ~1,600
                    title prescreen             ~120  → candidates.md
                                                            │
    profile.md ─┐                                           ▼
    SCORING.md ─┴──▶ an LLM reads each description   →  shortlist.md
                                                    ranked, with reasons

The first half is plain Python and deterministic. The second half is judgement,
and needs a model. The two files you write (or have Claude Code generate for
you via the `/jobscan-setup` skill) — `profile.md` (what you have done,
*and what you have not*) and `SCORING.md` (how to weigh a posting against that)
— are what make the ranking yours rather than generic.

Three Claude Code skills ship in `.claude/skills/` and cover the three jobs
above — writing those files, adding employers, and doing the ranking:

| skill | what it does |
|---|---|
| **`/jobscan-setup`** | Point it at a folder of your résumés, cover letters and ATS answers. It reads them, asks about what those documents *cannot* tell it — chiefly your gaps — and writes all three files with you reviewing each one. No folder? It interviews you instead. |
| **`/jobscan-connector <company>`** | Works out which ATS an employer uses, verifies it with a real request, and adds it to `config.json`. |
| **`/jobscan-score`** | Ranks `candidates.md` into `shortlist.md` with reasons, then turns the skip reasons back into filter fixes. The one you will use weekly. |

Run them from Claude Code with this repo as the working directory. **Skills are
discovered when a session starts**, so a freshly cloned repo needs one restart
before the slash-commands appear. They are convenience, not a dependency —
each is a plain Markdown file, and every rule they follow is also written into
the files they edit.

**Get going:** [Requirements](#requirements) → [Setup](#setup) →
[Run it](#run-it)
**Reference:** [Files](#files) · [config.json](#configjson-reference) ·
[Attribution](#sources-and-attribution) · [Conduct](#conduct) ·
[Caveats](#caveats) · [PLATFORMS.md](PLATFORMS.md) for job-board quirks

## Requirements

- **Python 3.8+ and nothing else.** Stdlib only — no venv, no pip, no lockfile.
- **No accounts or API keys** for any source that ships with it — though The
  Muse asks that you register for more than casual use; see
  [attribution](#sources-and-attribution).
- **An LLM for the scoring step.** The fetching half is plain Python; ranking
  needs a model that can read a job description against your profile. Three
  [Claude Code](https://claude.com/claude-code) skills ship with the repo (see
  [Setup](#setup)), but you can paste `SCORING.md` and `candidates.md` into
  whatever you use instead.

## Setup

Two files describe you, and everything else is machinery:

| file | what it holds |
|---|---|
| `profile.md` | what you have done, **what you have not**, which directions you are aiming at, and what counts as adjacent |
| `config.json` | where to look: sources, keyword filters, regions |

`SCORING.md` is **not** one of them. It carries the scoring machinery and
nothing personal, so it is the same file for everyone and upstream can keep
improving it under you. Everything profile-specific it needs, it reads out of
`profile.md`.

They ship as templates marked `FILL:`, and **`jobscan.py` refuses to scan while
any marker remains.** An unfilled config is valid JSON where every source
answers `ok` and the run returns nothing — which reads as "no good jobs this
week" rather than "you have not set this up yet". `./check-setup.sh` lists what is
outstanding.

### Let `/jobscan-setup` write them

Point it at a folder of your résumés, cover letters and ATS answers and it
writes all three, asking you about whatever those documents cannot settle.
Expect a conversation rather than a form, and expect it to push on your gaps —
the part a résumé is built to hide, and the part that does most to keep a
shortlist honest.

### Or edit them by hand

Nothing here is generated or opaque. All three are plain text, each carrying
its own rules in its own comments: replace the `FILL:` markers, then
`./check-setup.sh` to check and `python3 jobscan.py --check` to confirm the sources
answer.

### Run with the shipped example persona

`examples/` holds a worked version of every file for a fictional persona, plus
the material she was built from — and **her `profile.md` was generated by
`/jobscan-setup` from that material, not written by hand.** Run
the skill against `examples/material` and compare. Or just watch the scan run:

    cp examples/config.json config.json
    cp examples/profile.md   profile.md
    python3 jobscan.py --all

Remember to put your own files back.

### After setup

- **Retune the keyword filters for a few runs.** Your shortlist's skip reasons
  are the feedback loop; `/jobscan-score` proposes the edits.
- **`profile.md` is tracked, not gitignored.** Filled in, it holds a distilled
  CV. Decide whether you want that committed.

## Run it

    python3 jobscan.py           # new roles since last run
    python3 jobscan.py --all     # ignore seen.json, consider everything open
    python3 jobscan.py --check   # just verify every source still answers

Then, in Claude Code:

    /jobscan-score

which scores every candidate against `profile.md` using the `SCORING.md`
rubric, writes `shortlist.md`, and turns the Skip reasons back into concrete
prescreen fixes. (The equivalent by hand: *read SCORING.md and score
candidates.md -> shortlist.md*.)

On `--check`, **read the counts, not just the ok/FAIL flags.** A source that
returns zero still prints `ok`, and that is the one failure mode this report
cannot catch for you.

## Files

| file | what it is |
|---|---|
| `LICENSE` | MIT |
| `check-setup.sh` | read-only check: what is still unfilled, and what to do next |
| `.claude/skills/` | `/jobscan-setup`, `/jobscan-connector`, `/jobscan-score` |
| `config.json` | sources + prescreen rules. The shipped template. |
| `config.local.json` | optional per-user overlay merged onto `config.json` at load — the thing you tune, kept out of git |
| `adapters.py` | one function per platform, all returning the same job dict |
| `jobscan.py` | fetch → delta vs `seen.json` → locations → prescreen (incl. dedupe) → tier/budget split → hydrate → re-check locations → write → defer the capped |
| `profile.md` | your capabilities *and honest gaps*, distilled from your CV |
| `SCORING.md` | the rubric — profile-independent machinery; read before changing how scoring works, but nothing in it is yours to fill |
| `PLATFORMS.md` | adapters, per-platform quirks, and portals that resist scripting |
| `candidates.md` | scored-tier survivors with full descriptions — the scoring input |
| `candidates.json` | same, machine-readable |
| `shortlist.md` | the scored output — ranked, with each Apply's full posting reproduced |
| `seen.json` | job ids already reported, so each run is a delta |
| `deferred.json` | job ids that passed the prescreen but lost to a cap, with the date they first did |
| `examples/` | a worked version of every file you have to fill in, plus sample output |
| `examples/material/` | the fictional persona's résumés, cover letters and ATS answers — input for a `/jobscan-setup` dry run |

`candidates.*`, `shortlist.md`, `seen.json` and `deferred.json` are gitignored —
they are generated, they churn daily, and a shortlist is personal.
`config.local.json` is gitignored too, for a different reason: it is not
generated, it is yours — real employers, your regions, your keywords.

## `config.local.json` — keeping your tuning out of the template

`config.json` is the shipped template. You can edit it directly and everything
works — but then every `git pull` that improves the template collides with your
tuning, and a term added upstream to the universal `block` list never reaches
you.

The alternative is to leave `config.json` alone and put your values in
`config.local.json`, which `jobscan.py` merges over it at load:

```jsonc
{
  "prescreen": {
    "block+":  ["your noise terms"],     // ADDS to the 29 shipped ones
    "signal+": ["your title terms"],     // template ships only placeholders
    "max_to_score": 600                  // no "+" -- replaces outright
  },
  "regions": { "wanted+": ["remote", "boston"] },
  "companies+": [
    { "id": "muse-discovery", "locations": ["Boston, MA"] },  // fills in a shipped source
    { "kind": "greenhouse", "company": "acme", "group": "tracked" }  // adds one
  ]
}
```

| in the overlay | means |
|---|---|
| a dict | merged key-wise, recursively |
| `"key+"` | merged into the list at `key`: an entry whose `id` matches a shipped one merges onto it, the rest append, and `FILL:` placeholders in the template are dropped |
| `"key"` | replaces outright |
| `null` | deletes the key inherited from the template |

**Prefer `block+` to `block`.** Replacing the list silently drops the universal
noise terms, and nothing tells you — the run just quietly reports roles you did
not want.

`check-setup.sh` and the unfilled-`FILL:` check both run against the *merged*
config, so an overlay that fills a placeholder counts as filled.

## config.json reference

**The file documents itself.** Every key has a `_README` or `_comment` sibling
inside `config.json` carrying the rules, the reasoning and the measurements
behind it — read them there rather than trusting a summary here to stay
current.

| top-level key | what it is |
|---|---|
| `companies` | the sources to fetch — see [PLATFORMS.md](PLATFORMS.md) |
| `regions` | where you will work — `wanted` place tokens, plus optional `foreign` and `ambiguous` |
| `prescreen` | the title gate: `block`, `signal`, `min_signal`, the `discovery_*` pair, and the caps |
| `filter_locations` | `false` disables region filtering entirely |
| `_manual` | employers with no automated route, and exactly what was tried |
| `_companies_examples` | ignored by the tool: a skeleton entry per platform, to copy from |

**On `regions`:** getting the tokens right is fiddlier than it looks — feeds
write the same city half a dozen ways, and bare city names collide across
states. The `_README` beside it covers that. One behaviour is worth knowing up
front because it shows up in your shortlist: **vague postings are kept.**
Workday hides multi-site listings behind "4 Locations", so those pass the
filter at step 1 — dropping them there would lose genuine in-region roles.
For Workday they do not stay vague: hydration fetches the detail page anyway,
which carries the concrete site list, so the region filter runs a second time
afterwards and the ones that are entirely foreign are dropped before they
reach `candidates.md`. Vague postings from other platforms still get through,
and the rubric asks the scorer to flag those. `location_ok()` in `jobscan.py`
documents the full order of tests.

Two things worth knowing before you edit the prescreen:

- **Caps are filled round-robin across companies**, so one large board cannot
  crowd out a small one. Tracked sources and discovery sources draw on separate
  budgets (`max_to_score` / `max_discovery`) so an open sweep can never starve
  the boards you chose deliberately.
- **Nothing is lost to a cap.** A role that passed the prescreen but did not
  fit the budget is *deferred*, not marked seen: it is recorded in
  `deferred.json` and gets first claim on the next run. A run that ends with a
  backlog says so on stderr, with the age of the oldest entry — a growing one
  means the caps are too low or the prescreen too loose for the sources you
  track.
- **`block` entries are regexes; `signal` entries are plain lowercase
  substrings.** Anchoring bugs are the most common way a block list quietly
  underperforms — `intern$` misses "Robotics Intern - Real-Time Controls".

## Sources and attribution

**The job descriptions are not this project's to give away.** Each is written
by the employer that posted it and remains theirs; what follows credits the
platforms the data is read *through*. Every row in `candidates.md` links to the
original posting, and each generated file ends with a **Sources** block naming
the platforms that run used — generated from the config, so it stays accurate
as you add sources.

**First-party applicant tracking systems.** The employer publishes here and the
platform is the pipe: [Greenhouse](https://www.greenhouse.io),
[Lever](https://www.lever.co), [Ashby](https://www.ashbyhq.com),
[SmartRecruiters](https://www.smartrecruiters.com),
[Workday](https://www.workday.com), [Phenom](https://www.phenom.com),
[Radancy/TalentBrew](https://www.radancy.com),
[PageUp](https://www.pageuppeople.com), [Eightfold](https://eightfold.ai),
[Paradox](https://www.paradox.ai), [ClearCompany](https://www.clearcompany.com).

**Aggregators**, which index many employers at once:

- **[The Muse](https://www.themuse.com)** — public API, no key needed to call
  it. Their docs state **500 requests/hour unauthenticated**, 3,600 with a free
  key, and that *"registration is required for any use beyond testing."* A
  daily run of the shipped config is well inside the unauthenticated limit, but
  if you run this regularly you should
  [register](https://www.themuse.com/developers/api/v2) — it is free and it is
  what they ask for. Their documentation states no explicit attribution
  requirement; do not assume one either way without checking.
- **[Himalayas](https://himalayas.app)** — public API, no key. Their docs
  **do** ask for attribution: a visible link back and a statement that the data
  came from Himalayas, if you republish it. The generated Sources block carries
  that line automatically. Their data refreshes every 24 hours, so more than a
  daily run gains nothing and only costs them requests.

**If you publish your `shortlist.md` anywhere**, carry the Sources block with
it. Locally it is a file on your disk; published, it is someone else's data
displayed on your page. Note that a shortlist reproduces the full posting for
every role it says Apply to, so it carries the employers' own words and not
just your summary of them — the same care `candidates.md` needs.

**Adding a source?** Put it in `ATTRIBUTION` in `adapters.py`, and if the
platform documents a required credit line, in `REQUIRED_CREDIT` alongside it.
Check the terms before adding — and record what you actually read, rather than
assuming the permissive case.

## Conduct

**Read-only, by design.** It fetches the same public JSON a site's own frontend
fetches, roughly once a day, one request at a time with a delay. It does not
log in, does not submit applications, keeps no credentials, and holds no
personal data beyond your `profile.md`. Where a site publishes a `robots.txt`,
the paths used are ones it explicitly allows.

Keep it that way. The automation is for *finding* roles — you apply to them
yourself.

**Attribution and rate limits** are covered in *Sources and attribution*
above. The short version: credit the platforms if you publish the output, keep
to about one run a day, and check a new source's terms before adding it rather
than assuming.

## Caveats

**This was built for one person's job search and generalised afterwards.** The
fetching and filtering half has done a lot of real work. The parts that depend
on judgement — the setup interview, the scoring — have been exercised against
very few profiles, and none of them a stranger's.

So expect to hit things:

- **A careers site it cannot read.** Most portals are one of a handful of
  platforms, and those are covered. Yours may not be.
- **A profile it handles clumsily.** Career changers, non-linear histories,
  academic tracks and anything outside a US job search are all thinly tested.
- **Filters that are wrong for you at first.** The keyword rules and the region
  matching need a few runs of tuning before they fit; that is normal, and the
  tuning loop is documented.

None of this is fatal, because **nothing here is a black box.** The rules live
in files you can read and edit, and where something was ruled out — a portal
judged unreachable, a source judged useless — the reason is written down with
it. That matters more than it sounds: several such verdicts have already turned
out to be wrong when someone bothered to re-test them. Treat a "doesn't work"
here as provisional.

