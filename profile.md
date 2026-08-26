# FILL: Your Name — candidate profile (for job matching)

<!--
  TEMPLATE. Every FILL: marker below must be replaced before your first run.
  A worked, filled-in version of this exact structure is in examples/profile.md.
  Run `./check-setup.sh` to see what is still unfilled, or use `/jobscan-setup`
  (see README.md) to have Claude write this file from your material.

  Two rules that matter more than the wording:

  1. NOTHING HERE MAY BE INVENTED. Every line must trace back to your CV or to
     an application you actually sent. This file is the sole evidence the
     scorer has; a flattering line here produces a confidently wrong shortlist.

  2. THE "HONEST GAPS" SECTION IS LOAD-BEARING. Without it the scorer
     hallucinates competence and recommends applications that were never going
     to land. It is the single highest-value part of this file.
-->

FILL: where this was distilled from — e.g. "Distilled from `~/cv/experience.txt`
and the application archive in `~/cv/past_applications/`." Regenerate whenever
the CV changes materially; every score depends on this file, so drift here
quietly degrades everything.

## One-line

FILL: one or two sentences. What kind of problem you take on end to end, and
with what. Written for a stranger deciding whether to keep reading.

## Status

FILL: work authorization, where you are based, and the regions you will take.
Then state whether role *type* is a filter. The recommended framing, because it
is what makes the scoring direction work:

> Open to a wide range of roles — role type is NOT a filter, capability fit is.

## Demonstrated capability

<!--
  These bold strand names are load-bearing: they become the "Matched via"
  labels in SCORING.md. Use three to five. Order them by depth, deepest first,
  and say so on the first one. Under each, give concrete, verifiable bullets —
  numbers, scale, artifacts — not adjectives.

  Keep every strand you have real evidence for, even ones that feel off-target.
  Breadth is an asset under this rubric (see SCORING.md, "Direction of
  scoring"); it is only a liability under the wrong one.
-->

**FILL: strand one — your deepest strength (say so)**
- FILL: a concrete accomplishment with scale or a measurable outcome.
- FILL: another.

**FILL: strand two**
- FILL: concrete bullets.

**FILL: strand three**
- FILL: concrete bullets.

<!--
  Optional: a strand that is recent, real, but thinner than the others. Label
  the caveat inline rather than hiding it — e.g. "(recent, contract-scale)".
-->

## Languages & tools

FILL: a flat list of what you actually use. Add a short "Learning:" tail for
things you are mid-way through, so the scorer neither credits nor ignores them.

## Honest gaps — do NOT score as if present

<!--
  The most important section. Write it in the negative and be specific: name
  the thing, then the boundary. "No production ML engineering: no training at
  scale, no deployment, no MLOps" is useful. "Limited ML experience" is not.

  Rules of thumb:
   - Anything a recruiter in your target field would ask about and you cannot
     answer with evidence belongs here.
   - Distinguish adjacent-but-not-the-same from absent. Say which.
   - Include the boring ones: no people management, no budget ownership, no
     industry role, no degree in the field.
   - 5-8 entries is typical. Fewer usually means you are flattering yourself.
-->

- FILL: gap, stated specifically, with its boundary.
- FILL: gap.
- FILL: gap.
- FILL: gap.
- FILL: gap.

## Target directions and their expected gaps

<!--
  THE LOAD-BEARING SECTION for scoring. SCORING.md carries the machinery for
  applying this -- "forgive at most one HARD gap" -- but the directions and
  the allowances are facts about you, so they live here.

  For each direction you are actually targeting, answer three questions:
    1. What is the direction? (from what, to what)
    2. Which gap is therefore EXPECTED, and must not sink a role on its own?
    3. When does that same gap become disqualifying -- what does a posting
       look like when the gap IS the job? Give one or two concrete phrasings
       you would really see in a description.

  Without (3) the rule has no teeth and everything scores as a fit.

  Two to four directions is typical. Say whether you weight them equally: the
  scorer picks ONE per posting, and if a direction is a long shot, saying so
  here is what stops it being forgiven as generously as the others.
-->

FILL: `<candidate>` is moving from `<current field>` toward `<N>` destinations,
weighted `<equally / in this order>`: **FILL: direction one**, **FILL:
direction two**.

FILL: one gap expected across ALL directions, if there is one — commonly "has
never held an industry role". State why it is not disqualifying.

### If it is a FILL: direction-one role

**Some FILL: `<expected gap>` is expected and fine.** Do not treat "wants
FILL: `<the thing they lack>`" as disqualifying on its own.

It becomes disqualifying when that depth *is* the job — a posting whose core
responsibilities read "FILL: concrete phrasing", "FILL: concrete phrasing".

### If it is a FILL: direction-two role

**FILL: the expected gap for this direction, and its limit.** Repeat the shape
above. Delete or add directions to match what you are really targeting.

## Adjacency

<!--
  What counts as PARTIAL CREDIT at scoring time. SCORING.md reads this list
  rather than inferring adjacency from shared words, which is the failure this
  section exists to prevent.

  Write each pair as "what you actually did" vs. "what a posting would call
  it". Two to five pairs.

  Then the harder half: name what LOOKS adjacent and is not. Shared vocabulary
  between a thing you did and a thing you did not is a trap, and it is worth
  spelling out for anything you also listed under "Honest gaps".
-->

- FILL: what you did, with scale or specifics, vs. "FILL: what the posting
  calls it", "FILL: another phrasing"
- FILL: another pair.
- **Not adjacent, despite the vocabulary:** FILL: the thing you did is *not*
  the thing it shares words with. Do not grant partial credit on the overlap.

## Skip buckets

<!--
  The reason categories the Skip list is grouped by. These are the output that
  feeds back into tuning `block` / `discovery_block` in config.json, so they
  are worth keeping current: a bucket that keeps filling up is telling you the
  prescreen is letting a whole category through.

  Start with whatever you can guess and add to it after the first scored run.
  Ones that apply to almost any search: "the specialty IS the job", "wrong
  level", "adjacent industry, non-transferable".
-->

- **FILL: the specialty IS the job** — FILL: the tell, in a few words
- **FILL: another bucket** — FILL: the tell
- **wrong level** — roles resting on a track record the candidate does not
  have, or roles well below their level
- **adjacent industry, non-transferable**
