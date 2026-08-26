# Scoring rubric

Read `profile.md`, then score every role in `candidates.md`.

<!--
  TEMPLATE. Most of this file is profile-independent and should be left alone.
  Exactly TWO sections must be adapted to your profile, both marked FILL:
  below, plus a handful of domain illustrations marked "example, replace":

    1. "Expected gaps"  — LOAD-BEARING. This is the section that most changes
                          scores. Get it wrong and the scorer forgives the
                          wrong weakness.
    2. "Matched via"    — must list the strand names you used as the bold
                          headings in profile.md.

  A worked, filled-in version of this exact file is in examples/SCORING.md.
  `./check-setup.sh` reports what is still unfilled.
-->

## What to score, and what not to

- **`candidates.md` only**, and every row there should carry a full
  description. If one is obviously truncated — a few hundred characters, or
  text ending in an ellipsis — **do not score it.** Say so instead: a short
  sample is enough to notice a role, never enough to judge one. `jobscan.py`
  warns when a source looks capped, but check what you are reading.
- Rows tagged **`*(discovery)*`** come from an open sweep rather than a company
  you chose. Score them identically — but they are unfamiliar employers, so say
  what the company actually does in the write-up.

Why the full text matters, from a real run: the most promising *title* in one
batch of capped listings turned out, in full, to describe different work under a
familiar name — it scored 4. Titles systematically overstate fit.

## Direction of scoring (this is the whole trick)

Score **what fraction of the JOB's requirements the candidate's experience
covers** — never "how much of the candidate's background does this job use".

The second direction punishes breadth: a role that is an excellent fit for one
of the candidate's strands scores badly merely because it does not touch the
others. Only the first direction answers the actual question, which is *is
applying worth the effort*.

So for each role: list its real requirements, then ask which of them some part
of the candidate's experience covers.

**Do not reverse this.** It is the single decision the whole tool rests on,
and reversing it is an easy, quiet mistake: the wrong direction still produces
a confident-looking ranked table, just one that buries the roles worth
applying to.

## Weighting

- Separate **must-haves** (stated as required, or clearly load-bearing for the
  day-to-day) from **nice-to-haves**. A missing nice-to-have barely matters.
- An **adjacent** match counts as partial credit. Judge adjacency by what the
  work actually demands, not by shared vocabulary.
  <!-- FILL: two or three adjacency pairs from your own field, in the form
       "what the candidate did" vs. "what the posting calls it". Examples from
       the worked profile in examples/, replace these:
         habitat life-support design   vs. "ECLSS" / "thermal-fluids systems"
         live-specimen manipulator     vs. "compliant grasping"
         no-maintenance-visit hardware vs. "design for reliability" -->
- Years-of-industry-experience requirements are soft. Count sustained,
  substantive work as real experience even when it was not an industry job —
  a PhD, a trade, self-directed projects at scale. Do not drop a role on a
  years-of-experience line alone.
- Seniority mismatch **downward** (a role well below the candidate's level) is
  a bigger negative than mismatch upward.

## Expected gaps

<!-- FILL: THE LOAD-BEARING SECTION. Rewrite the paragraph below for your own
     profile. It must answer three questions:
       1. What direction is the candidate moving in? (from what, to what)
       2. Which gap is therefore EXPECTED, and should not sink a role on its
          own?
       3. When does that same gap become disqualifying — i.e. what does a
          posting look like when the gap IS the job? Give one or two concrete
          phrasings you would actually see in a description.
     Without (3) the rule has no teeth and everything scores as a fit. -->

FILL: `<candidate>` is moving from `<current field>` toward `<target field>`.
**Some `<expected gap>` is expected and fine** — do not treat "wants
`<expected gap>` experience they lack" as disqualifying on its own. It only
sinks a role when that depth *is* the job (e.g. a posting whose core
responsibilities read "FILL: concrete phrasing", "FILL: concrete phrasing").
A role wanting `<the candidate's real strengths>`, with `<expected gap>` as
context rather than as the work, is a good fit even if they have never done it.

### A learnable gap must never become a prescreen filter

This is the rule most easily got wrong, because it cuts against the tuning
advice everywhere else in this project ("when noise gets through, tighten
`block`"). **Scoring and blocking are different mechanisms.** A gap weighed at
scoring time is set against everything else the posting offers. A term in
`block` deletes the role before anyone reads a word of it.

So separate two kinds of missing thing:

- **Hard gates** make the role unobtainable however good the fit — an active
  security clearance, a professional licence, work authorization, a degree that
  is stated as mandatory. Blocking these is correct: they are unreachable by
  definition, and every one that reaches scoring wastes effort.
- **Learnable gaps** are a tool, language or technique the candidate would
  pick up if the rest of the role fitted. **Never put the name of one in
  `block`.** Weigh the *surrounding domain* instead — the same technology turns
  up in jobs that are otherwise nothing alike.

A real case: a candidate open to learning GPU programming. Adding `gpu` to
`block` looked reasonable and would have been a serious mistake — GPU compute
and numerical-kernel work scored among the highest roles that search produced,
while 3D rendering pipelines and mobile silicon bring-up are entirely different
jobs that merely run on a GPU. The domain around the technology is what to
judge, never the technology's name.

Before adding any term to `block`, ask: *is this unobtainable, or merely
unfamiliar?* Only the first belongs there.

**Never credit anything under "Honest gaps" in profile.md as present.** That
list is the hard floor of this rubric; it overrides any inference the posting
tempts you into.

## Output

A markdown table, best first, then one short paragraph per role scoring ≥6:

| # | Company | Role | Loc | Score | Matched via | Key gap |

- **Score 0–10** = the fraction of the role's requirements the candidate
  plausibly covers.
- **Matched via** = which strand carried it. A label only — it is not a second
  score.
  <!-- FILL: list your strands here, matching the bold headings under
       "Demonstrated capability" in profile.md, separated by " / ". The example
       profile uses: product development / production & operations /
       food safety & quality / formal training -->
- **Key gap** = the one thing most likely to get this application screened out.

Then: **Apply / Maybe / Skip**.

- **Apply (≥7)** — covers the must-haves; what is missing is nice-to-haves or
  the expected gap named above.
- **Maybe (5–6)** — one real must-have missing, but the rest is strong.
- **Skip (<5)** — multiple must-haves uncovered, or the job *is* the gap.

### Every Apply gets its `candidates.md` entry reproduced in full

After the Apply / Maybe / Skip split, add a section — **"The Applies, in
full"** — carrying one subsection per Apply role, in the same order as the
table. Each one holds:

- a heading with the role's rank, company, role title and score;
- its **Matched via** and **Key gap**, repeated from the table;
- `Location`, `URL` and `Prescreen hits`, copied verbatim from
  `candidates.md`;
- the `candidates.md` entry number it came from, so any claim can be traced
  back to its source row;
- the employer's description text, as fetched.

**Copy the description, do not re-summarise it.** The point of the section is
that a decision and the evidence behind it can be read in one file — without
`candidates.md` open alongside, and without trusting a paraphrase written by
the same pass that did the scoring. `jobscan.py` truncates descriptions at
1,800 characters; say so in the section, so a posting that stops mid-sentence
is not read as the whole of it.

**Applies only.** Maybes and Skips stay as table rows and paragraphs. A
shortlist that reproduces every row is just `candidates.md` with extra steps.

Reproducing the descriptions means `shortlist.md` now carries employer text
verbatim, exactly as `candidates.md` does. Carry the **Sources** block across
(see below): locally this is a file on a disk, but shared or published it is
the employers' own words on someone else's page.


Be blunt. A shortlist that says "apply" to everything is useless — the entire
value here is preventing applications that were never going to land.

Group the Skip list by *reason* rather than listing every role.
<!-- FILL: reason buckets for your field. The example uses "regulatory affairs
     is the job", "plant maintenance", "wrong level". Generic ones that apply
     to almost any search: "the specialty IS the job", "wrong level",
     "adjacent industry, non-transferable". -->
The reasons are what tell you whether a whole company is worth tracking, and
they feed straight back into tuning `block` / `discovery_block` in
`config.json`. Treat that as part of the output, not an afterthought.

## Flag rather than silently absorb

Say so explicitly when:

- **A role there is already archived application material for reappears.** The
  marginal cost of applying is near zero, and that changes the recommendation
  independently of the score.
- **A posting is mostly boilerplate**, so the score is low-confidence. Mark it
  `6?` rather than guessing a clean number.
- **A location looks wrong for the filter** (a foreign office or plant that
  slipped through). That is a bug report against `config.json` or
  `location_ok()`, not just a note.
- **A whole source contributed nothing usable.** Worth knowing before the next
  run — a source can answer `ok`, return a healthy count, and still be
  contributing only noise. See the silent-zero note in PLATFORMS.md.
