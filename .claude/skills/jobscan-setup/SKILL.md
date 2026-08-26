---
name: jobscan-setup
description: Set up this jobscan repository for a specific person — reads their existing application material (resumes, cover letters, ATS question answers), interviews them to fill the gaps, then writes profile.md and config.local.json (sources, prescreen and regions). Use when the user wants to configure jobscan for themselves, is starting from the shipped templates, mentions unfilled FILL markers or check-setup.sh, or asks to point Claude at their CV or application folder.
---

# jobscan setup

Turn the shipped templates into one person's working configuration.

Three files end up changed: `profile.md`, `config.local.json`, and three
region lists inside `jobscan.py`. `examples/` holds a fully worked version of
the first two — read them before writing anything, they show the target shape.

**The output that matters is `profile.md`.** Every score depends on it. The
other three are tuning; this one is the evidence base. Spend the time there.

## Ground rules

1. **Nothing invented, ever.** Every line in `profile.md` must trace to a
   document the user gave you or an answer they typed. If you cannot point to
   the source, ask — do not write it. A flattering line here produces a
   confidently wrong shortlist for months.
2. **Stop at each phase.** Show what you produced, get a reaction, then
   continue. Do not run phases 1–6 and present a finished repo.
3. **Batch questions.** Three to five at a time, not one per message. Use
   `AskUserQuestion` for closed choices (regions, seniority, which strands to
   keep); ask in prose for anything open-ended.
4. **Their material is private.** Read it locally. Never paste CV contents into
   a web search, a commit message, or any outbound call. Quote from it only
   into `profile.md`, and only what earns its place.

---

## Phase 1 — Inventory their material

Ask for **a directory** holding whatever they have: resumes (often several,
tailored differently), cover letters, ATS question answers, past job
descriptions they applied to, performance reviews, a LinkedIn export.

    Point me at a folder with your application material — resumes, cover
    letters, ATS answers, anything you have. Several versions is better than
    one; the differences between tailored resumes tell me what you emphasise
    for which kind of role.

If they have no such folder, say so plainly and switch to interview mode: the
rest of this skill works, it just takes longer and you ask more in phase 2.

If they are just trying the tool out, `examples/material/` holds fictional
material for the example persona and exercises this whole workflow.

Then:

- `ls -R` the directory. **Read every relevant file** — PDFs and text both.
  If it is very large (>40 documents), read the resumes and cover letters in
  full, sample the rest, and say what you sampled.
- **Report the inventory before analysing it.** Group by type, note dates,
  and flag anything ambiguous ("three resumes, one dated 2019 — still
  accurate?").

Tailored variants are the richest source in the folder. Where two resumes
describe the same work differently, that difference *is* the strand structure —
name it and check it in phase 2.

## Phase 2 — Draft the picture, then interrogate the gaps

Produce a first pass, on screen, not in a file:

- **Three to five capability strands**, each with the concrete evidence you
  found. Deepest first.
- **Tools and languages**, split into "uses" and "learning".
- **Status**: work authorization, base location, target regions.
- **Anything contradictory or undated** you need resolved.

Then ask your follow-ups. Cover, at minimum:

- Evidence with no scale attached ("led a migration" — of what size?).
- Claims that appear in one document and not others.
- Whether a thin-but-real strand should stay (recent contract work, coursework,
  volunteer projects). Label the caveat inline rather than dropping it.
- Where they are trying to *move to*, not just what they have done. Phase 4
  depends on this answer.

### The gap interrogation — do not skip this

`profile.md`'s "Honest gaps" section is the single highest-value part of the
file, and it is the part people write too kindly about themselves. Their
material will not contain it: resumes and cover letters are built to hide
exactly this.

So derive gaps yourself and put them to the user:

- Take the roles they are targeting. What would a recruiter in that field ask
  about that their material cannot answer with evidence?
- Name the standard omissions explicitly and make them respond: no people
  management, no budget ownership, no industry role in the target field, no
  formal credential, no production/at-scale version of the thing they have done
  at small scale.
- Distinguish **absent** from **adjacent-but-not-the-same**, and say which.

**Push back at least once.** If the first list they accept has fewer than five
entries, or every gap is hedged, tell them it is too kind and name what you
think is missing. Then write each gap with its boundary:

    good:  No production ML: no training at scale, no deployment, no MLOps.
    bad:   Limited ML experience.

The boundary is what makes the rubric able to use it.

## Phase 3 — Write `profile.md`

Follow the template's structure exactly; `examples/profile.md` shows it filled
in. The bold strand names under "Demonstrated capability" are load-bearing —
`SCORING.md` reads them straight out of this file as the "Matched via" labels,
so there is no second copy to keep in sync.

Show the finished file and ask for corrections before continuing. Expect a
round or two here; this is the file worth iterating on.

## Phase 4 — The three scoring sections, still in `profile.md`

**Never edit `SCORING.md`.** It is profile-independent machinery and stays
byte-identical for every user; writing someone's field into it is the one
mistake this phase exists to prevent. Everything below goes in `profile.md`,
in the sections the template already marks out.

- **"Target directions and their expected gaps"** — the load-bearing one. For
  each direction they are actually targeting, it must answer three things:
  which direction it is, which gap is therefore *expected and forgivable*, and
  **when that same gap becomes disqualifying**. The third is the one that gets
  skipped, and without it the rule has no teeth and everything scores as a
  fit. Give one or two concrete phrasings they would really read in a job
  description.
  Two to four directions is normal. Say whether they are weighted equally —
  the scorer grants exactly one allowance per posting, so a long-shot
  direction that is not flagged as one gets forgiven as generously as their
  strongest.
- **"Adjacency"** — two to five pairs, in the form *what they actually did* vs.
  *what a posting in their target field calls it*. Then the harder half: what
  **looks** adjacent and is not. Anything they listed under "Honest gaps" that
  shares vocabulary with a real strength belongs here, named explicitly.
- **"Skip buckets"** — reason categories for their field. A first guess is
  fine; they get corrected after the first scored run.

## Write to `config.local.json`, not `config.json`

**Leave `config.json` alone.** It is the shipped template; everything you
configure in Phases 5 and 6 goes into `config.local.json`, which `jobscan.py`
merges over it at load. That is what keeps their tuning from colliding with the
next `git pull`. Read the `_local_README` key in `config.json` for the merge
rules, and note the two that matter most here:

- **`"block+"` and `"discovery_block+"`, never `"block"`.** The `+` adds to the
  29 universal noise terms the template ships. Replacing the list drops them
  silently — the run just starts reporting roles they did not want, with
  nothing to say why.
- **`"signal+"` / `"discovery_signal+"` / `"wanted+"`** — the template ships
  only `FILL:` placeholders for these, which the merge strips, so `+` gives a
  clean list of exactly what you wrote.
- To configure a **shipped** source (the Muse and Himalayas discovery sources),
  add an entry to `"companies+"` carrying that source's `id` — `muse-discovery`
  or `himalayas-remote` — and only the keys you are setting. It merges onto the
  shipped entry, so its `_README` and defaults stay current. Tracked companies
  you add have no `id` and simply append.

## Phase 5 — Regions

Two keys, and they are not the same thing:

1. `regions.wanted` — the place tokens the **location filter** matches against.
2. the Muse source's `locations` — the cities that **search** is restricted to.

Ask which metro areas they would actually take, and whether remote-only
postings should count. Then, for `regions.wanted`: include the state name, its
abbreviation in several punctuation forms (`, tx` / `tx,` / ` tx `) because
feeds disagree, and every city. **Check for city-name collisions** — write
`pasadena, tx` rather than `pasadena`, or every Pasadena CA role passes;
Portland, Springfield, Columbus and Charleston have the same problem.

Read `location_ok()` before you finish, so you preserve its five-step logic —
in particular that a bare "remote" is not evidence of a domestic role.

## Phase 6 — The prescreen

Fill `signal+`, `discovery_signal+`, and the field-specific additions to
`block+` and `discovery_block+` in `config.local.json`. Read the `_README` keys
in `config.json` first; they carry the tuning rules.

Set the Muse `categories` from names you have **verified return results** —
a wrong category name silently returns zero while `--check` still prints `ok`.
Say which ones you checked and what each returned.

Tell the user plainly that these lists will be wrong on the first pass and that
phase 7 is where they get fixed.

## Phase 7 — Verify, then actually look at the output

    ./check-setup.sh
    python3 jobscan.py --check
    python3 jobscan.py --all

- On `--check`, **read the counts, not the flags.** A source returning 0 still
  prints `ok`. Flag any zero and diagnose it before moving on.
- Then read `candidates.md` yourself and give an honest verdict: is the
  prescreen too loose (noise got through) or too tight (suspiciously few rows)?
  Propose concrete list edits. When noise gets through, **tighten `block`
  rather than narrowing `signal`** — narrowing `signal` drops real roles
  silently. But **never block a learnable gap**: block only hard gates
  (clearance, licence, work authorization), never the name of a tool the
  candidate would pick up. See the "learnable gap" section of `SCORING.md`.
- Offer to run `/jobscan-score` on the result so they see the full pipeline
  before deciding anything.

## Phase 8 — Close out

Two things to raise, both easy to forget:

- **`profile.md` is tracked, not gitignored.** Once filled in it holds a
  distilled CV. Ask whether they want it committed or added to `.gitignore`,
  and act on the answer.
- **Adding companies** is `/jobscan-connector`, deliberately not part of setup
  — the two shipped sweeps alone prove the pipeline works. Mention it as the
  obvious next step once they have seen a run.

Then summarise what changed, what is still guesswork, and what to watch on the
next two or three runs.
