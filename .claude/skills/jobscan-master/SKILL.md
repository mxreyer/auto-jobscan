---
name: jobscan-master
description: Merge every archived shortlist into one master list of the postings that are still open, verifying each link against its own platform. Use when the user asks which roles are still available, wants the shortlists combined or deduplicated, asks what has closed since a run, or wants a single list to apply from.
---

# Building the master shortlist

Every run overwrites `shortlist.md`, so the dated copies in the repo are a
pile of overlapping, partly stale judgments. This turns them into one list of
**what is still open**, ranked, deduplicated, and safe to apply from.

Two files come out of it:

- `master-shortlist.md` — everything still open, by score band.
- `closed-postings.md` — the complement, when the user wants it. It is worth
  offering: a count of Apply-tier roles that closed unapplied is the sentence
  that changes behaviour, and it only exists if you keep the dead rows.

Both are generated output. They belong in the repo root next to
`shortlist.md`, and they are overwritten, not appended to.

## Write the scripts to files

This job is several hundred HTTP requests and a lot of parsing. Do it in
scripts under `.claude/scratch/`, not in inline `python3 -c` or heredocs —
the user's `CLAUDE.md` requires it, and it also means the liveness sweep can
be resumed and re-run instead of retyped. Keep the intermediate JSON
(`rows.json`, `liveness.json`, `entries.json`) so a failed pass costs one
retry and not the whole job.

## Step 1 — collect the rows

Parse the table out of every `shortlist*.md`. Do not trust the `#` column:
in most runs it is the `candidates.md` entry number, but in at least one it
is a **rank**, and joining on it silently returns a different employer's
posting. Check one row per file by hand before trusting the whole file.

## Step 2 — resolve each row to a URL, from its own run only

The shortlists carry URLs only for their Applies. Everything else is joined
back to the `candidates-<date>.md` that the run was scored from.

**Never borrow a URL from a different run.** A same-title match elsewhere is a
different requisition. University boards routinely repost the same job under a
fresh requisition number every few weeks, and large employers reuse one title
across many req numbers — so the same title can appear three times, scored
differently each time, and only one of them is live. A borrowed link sends the
user to the wrong posting, or resurrects a dead one's score against a live
one's link.

When a run's `candidates.md` was overwritten, try, in order:

1. **git.** `git show HEAD:candidates.md` and earlier revisions — one archived
   run's source survives only there.
2. **The shortlist's own "Applies, in full" section**, which reproduces the
   entry including its `- URL:` line.
3. **The source platform.** For any row scoring ≥5, look the posting up again
   through the repo's own adapters (`adapters.himalayas`, `adapters.paradox`,
   …). This doubles as the liveness check. Accept the match only on an exact
   title or requisition number; a near-title from the same employer is not
   the same posting and must stay unresolved.

Never retype a URL from a transcript or from memory. Rows that stay
unresolved go in the output as unresolved, with the reason.

## Step 3 — calibrate before you sweep

**An HTTP status is not enough, and the exceptions are not guessable.** For
each platform, fetch one posting you know is live and one bogus id, and
compare, before checking anything in bulk. The rules below were calibrated
that way once; re-derive them rather than trusting them, because a board only
has to change its template once.

| Platform | Live test | The trap |
|---|---|---|
| Workday | `GET /wday/cxs/{tenant}/{site}/job/...` → 200; 404 = gone | the HTML page is a JS shell and answers 200 forever |
| Workday, at volume | `POST /wday/cxs/{tenant}/{site}/jobs` with `searchText=<JR id>`, match `externalPath` | the per-job endpoint starts 403-ing after a few hundred reads, whatever the pacing |
| Himalayas | job present in `/jobs/api/search` under its own `guid`, `expiryDate` in the future | the HTML is behind a Cloudflare challenge that 403s every client |
| The Muse | HTTP status | none — a removed slug is a clean 404 |
| Eightfold | `<title>` is the role | a dead requisition answers **200** with "Careers at X" |
| Greenhouse | `<title>` starts "Job Application for" | a closed job answers **200 with the board index**, "Jobs at X" |
| Ashby | `<title>` contains "@" | same generic-index trap, titled "Jobs" |
| Paradox | HTTP status | none — expired postings 404 |
| Radancy | HTTP status | none |
| iCIMS | HTTP status | a closed requisition answers **410**, not 404 |
| PageUp | the `#job-details` container is present and populated | the `<title>` is the generic board title on live postings too, so the Greenhouse rule inverts the answer |

The Greenhouse and Ashby traps alone produced five false "closed — no, open"
verdicts in a single run. Note which direction is expensive: a false "closed"
silently retires a posting the user could still have applied to, and nothing
downstream will ever question it. Assume every platform you have not
calibrated is lying to you.

## Step 4 — rate limiting, and the rule that matters

Boards throttle. Himalayas returns 429s, a Workday tenant starts returning
403s, a PageUp board answers empty `HTTP 202`s to everything including
known-good URLs. **None of that is evidence about the posting.**

- **A rate-limited, blocked or throttled URL is never recorded as closed.**
  Mark it `unverified`, keep it in the master list, and say in the row why it
  could not be settled and what was seen (`"board began answering empty 202s
  to every request, including known-good URLs"`). The user can then open it
  themselves. Dropping it, or calling it gone, throws away a job that is
  probably still there.
- **Pace for the whole sweep, not the first request.** At most 2–3 concurrent
  per host, a short sleep between requests, and one lock per host. Eight
  workers against a single host earns 429s for a hundred URLs and poisons every
  other request to that host for the next few minutes, including unrelated
  lookups.
- **Retry unsettled URLs serially, with backoff**, in a second pass that only
  touches them. If a whole host is failing the same way, stop and find the
  other endpoint — that is how the Workday `POST /jobs` route was found —
  rather than grinding through an hour of backoff.
- **Throw away a poisoned sweep.** If the sandbox or a proxy blocked
  everything, the run produced no information: delete the results file and
  start again once the hosts are declared. Never let "unknown because I was
  blocked" reach the output as a verdict.
- **Declare the hosts.** Outbound requests are refused unless the command
  names them in `allowed_domains`; the denial message names the host to add.

## Step 5 — deduplicate on the requisition

Key on the **URL**, not on company+title. The same job under two requisition
numbers is two rows with two fates, and the same posting under two title
variants — the bare role name on one board, the same name carrying a
location-and-rate suffix on another — is one.

**The headline score is the most recent run's, not the highest.** `SCORING.md`
and `profile.md` have been loosened more than once, so the latest reading is
the current judgment rather than the kindest one. Where runs disagreed, show
the earlier scores with their dates — an undated "(was 6)" hides which way
the role moved. Expect disagreement in roughly 5% of rows, and expect one or
two to be violent (6 → 2). Do not re-score anything here; that is
`/jobscan-score`'s job against the current `profile.md`, and a merge that
quietly re-scores is no longer a merge.

## Step 6 — write the file

Header: the date, how many shortlist rows collapsed into how many
requisitions, how many are still open, what the score means, and the
per-platform liveness table — the reader needs to know what "still open" was
allowed to mean.

Then:

- **Do these first** — the two or three actions, with reasons that ranking
  alone does not give. Roles with archived application material already
  written outrank their score. Filing deadlines outrank almost everything.
- **Apply / Maybe / Skip tables** of what is still open, each with a link.
  Put the Skip tier behind a `<details>` block; the user asked for
  completeness, not for a wall.
- **Unverified rows**, with the evidence and a plain `[the posting]` link —
  never an `[apply]` link, which reads as a verdict you did not earn.
- **Unresolved rows**, with why the URL is gone and what was tried.
- **The Applies, in full** — same rule as `/jobscan-score`: reproduce each
  still-open Apply's `candidates.md` entry verbatim. Extract the blocks
  **keyed on the URL**, never on an entry number, and cut each block at the
  next heading **of any level**: inside a shortlist's own "Applies, in full"
  the next thing is an `###` heading, and cutting only on `## ` swallows it.
- **Caveats**: scores written on different days, "still open" ≠ "still
  actively hiring", nothing re-fetched for content.
- **The Sources block**, carried across from `candidates.md`. This file
  reproduces employers' description text, so the attribution travels with it —
  Himalayas asks for a visible link back. See *Sources and attribution* in
  README.md.

## Step 7 — verify, in a script

Assert, and print pass/fail rather than eyeballing:

- every `[apply]` link is one the sweep marked live;
- every reproduced block sits under the heading whose URL it carries;
- no block swallowed the next entry or the Sources list;
- the counts in the prose match the data;
- the named claims in the prose are true — check each employer you named as
  closed is actually closed. Two such claims were wrong on the first pass of
  one run: "both of this employer's postings", when two of the four were still
  open; and a claim about which sources were most durable, when the platform
  named had the *highest* closure rate and the durability was really in the
  reposting.

Any statistic in the prose is a claim. Compute it; do not estimate it from
the shape of a table.

## Worth flagging in the write-up

- **A still-open role with archived application material.** Near-zero
  marginal cost, and it outranks its score.
- **A filing deadline inside the next fortnight.** University postings carry
  them and then vanish; they close fastest of any source.
- **A truncated posting whose earlier requisition was scored in full.** The
  archive can settle what a `6?` really is: a role whose description was cut
  short this time may have scored cleanly under its previous requisition
  number, and that earlier reading is the answer to what the repost is worth.
- **Attrition by platform and by run**, if a closed list is produced. Judge a
  source by what survives into the Apply tier, not by how much of it expires.
