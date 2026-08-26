---
name: jobscan-score
description: Score jobscan's candidates.md against the user's profile and write shortlist.md, then feed the Skip reasons back into the prescreen. Use after a jobscan run, or when the user asks to score candidates, rank roles, produce a shortlist, decide what is worth applying to, or asks what came through this week.
---

# jobscan scoring

Turn `candidates.md` into a blunt, ranked `shortlist.md`, then use what you
learned to improve the next run.

**`SCORING.md` is the rubric and this skill is not.** Read it and follow it
exactly. Do not restate its rules here, do not substitute your own judgment for
them, and if something in it seems wrong, say so to the user rather than
quietly deviating — the rubric encodes decisions that were expensive to reach.

## Before scoring

1. **`candidates.md` must exist.** If it does not, the user needs a run first:
   `python3 jobscan.py` (new since last run) or `--all` (everything open).
2. **Check the header date.** If it is more than a few days old, say so and
   offer to re-run before you spend effort scoring stale postings.
3. **`profile.md` must be filled in.** If it still has `FILL:` markers, stop
   and point at `/jobscan-setup` — scoring against a template produces
   confident nonsense. (`SCORING.md` has no markers to fill; it is the same
   file for everyone.)
4. **Read `profile.md` and `SCORING.md` in full, every time.** They drift. Do
   not score from memory of a previous session. Three sections of `profile.md`
   are the ones `SCORING.md` defers to: **Target directions and their expected
   gaps**, **Adjacency**, and **Skip buckets**. Scoring without them is
   scoring without a rubric.

## Scoring

Score **every** row in `candidates.md`. Follow the rubric's direction of
scoring, its weighting, its "Expected gaps" section, and its output format
exactly.

Three failure modes to guard against in yourself:

- **Grade inflation.** A shortlist that says Apply to everything is useless.
  The value here is preventing applications that were never going to land. If
  most rows land at 7+, you have reversed the scoring direction — re-read that
  section of the rubric.
- **Scoring the title.** Read the whole description. Titles systematically
  overstate fit, which is why truncated sources are never scored at all.
- **Crediting a listed gap.** Nothing under "Honest gaps" in `profile.md` may
  be treated as present, however much the posting invites it.

For `*(discovery)*` rows the employer is unfamiliar, so say what the company
actually does — the user has no context for the name.

## Output

Write `shortlist.md` in the format `SCORING.md` specifies: the table, a
paragraph for each role scoring ≥6, the Apply/Maybe/Skip split, **the Applies
reproduced in full**, the Skip list grouped by reason, and the flags.

Three things that make a shortlist useful rather than decorative:

- **Lead with the one to do first**, and say why it is first. Ranking alone
  does not answer "what do I do this afternoon".
- **Be concrete about the gap.** "Key gap" should name the thing likely to get
  them screened out, not a genre of concern.
- **Reproduce each Apply's `candidates.md` entry** — location, URL, prescreen
  hits, entry number and the employer's description text — in the "in full"
  section the rubric asks for. The user applies from this file; making them
  open `candidates.md` to find the link is the difference between a shortlist
  and a set of notes about one. Copy the text; do not summarise it, and do not
  quietly drop it when the run is large.

  Extract those blocks **mechanically**, by entry number, rather than
  retyping them — a copied description with an invented sentence in it is
  worse than no description. Two things to check: that each block stops where
  the next `## N.` heading starts, and that the last entry does not absorb the
  **Sources** block at the end of `candidates.md`.

Header line: the date, the region filter, source and role counts from the
`candidates.md` header, and a one-line reminder of what the score means.

## Then close the loop — this is the part that gets skipped

`SCORING.md` asks for the Skip list to be grouped by *reason* because those
reasons are prescreen feedback. Actually act on it:

1. **Propose concrete `config.json` edits.** If a reason bucket has several
   roles in it, name the `block` / `discovery_block` term that would have
   caught them. Show the exact strings.
2. **Prefer tightening `block` over narrowing `signal`.** Narrowing `signal`
   drops real roles silently; a bad `block` term announces itself the moment a
   title you expected goes missing.
3. **Never propose blocking a learnable gap.** Before suggesting any term, ask
   whether it names something *unobtainable* or merely *unfamiliar*. Hard gates
   — an active clearance, a licence, work authorization — are correct to block.
   A tool or technology the candidate would learn is not: the same technology
   appears in jobs that are otherwise nothing alike, so the surrounding domain
   decides, not the name. Adding `gpu` to one block list would have discarded
   the highest-scoring role that search ever produced. See the "learnable gap"
   section of `SCORING.md`.
4. **Warn about over-broad terms.** Say what else a proposed pattern would
   catch. One term that kills a whole category of roles the user wants is worse
   than the noise it removes.
5. **Flag dead weight.** If a source contributed nothing usable again, say so —
   judge a source by its Apply count, not its role count.
6. Apply the edits only if the user agrees, then note that the next run will
   show whether they helped.

## Also flag, per the rubric

- A role reappearing that they already have tailored material for — the
  marginal cost of applying is near zero, which changes the recommendation
  independently of the score.
- Boilerplate-heavy postings: mark `6?` rather than guessing a clean number.
- A location that should not have passed the filter. That is a bug report
  against `config.json` or `location_ok()`, not a footnote.

## Attribution

`candidates.md` ends with a **Sources** block naming the platforms that run
read from, generated from the config. **Carry it into `shortlist.md`.** This
matters more now that the Applies are reproduced in full: `shortlist.md` holds
the employers' own description text, not just your summary of it. The
descriptions belong to the employers who wrote them, and one shipped source
(Himalayas) documents an explicit request for a visible link back. Locally it
is a file on a disk; the moment a shortlist is shared or published, it is
someone else's data on someone else's page. See *Sources and attribution* in
README.md.

## After

`shortlist.md` is gitignored and overwritten each run. If the user wants to
keep one, suggest a dated copy before the next run.
