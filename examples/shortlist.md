# Shortlist — 2026-08-24 (Texas / US-remote)

> **Illustrative example.** What `/jobscan-score` produces from
> `examples/candidates.md` scored against `examples/profile.md` using
> `examples/SCORING.md`. The candidate is fictional; the postings are real,
> fetched 2026-08-24.
>
> The eight rows are chosen to exercise the rubric, not to sample the run, so
> the Apply density is higher than a full pass over 124 would give.
>
> Short quotations from the postings appear below because the reasoning is not
> checkable without them. The full descriptions are redacted in
> `examples/candidates.md` rather than republished — see the note there.
>
> The *"The Applies, in full"* section below is what a real run ends with:
> every Apply's `candidates.md` entry — location, URL, prescreen hits and the
> employer's description — reproduced so the file can be applied from on its
> own. Here the description text is the redaction placeholder rather than the
> employer's copy; everything else is as a real run writes it.

14 sources · 2,066 open roles · 1,666 in target locations · 124 scored
(8 shown here).
Score = fraction of *the role's* requirements this profile covers.

| # | Company | Role | Loc | Score | Matched via | Key gap |
|---|---------|------|-----|-------|-------------|---------|
| 1 | Firefly Aerospace | **Environmental Test Engineer III** | Cedar Park, TX | **8** | prototype vehicles & manipulators | qualification to NASA/Space Force standards |
| 2 | Apptronik | **Hardware Test Engineer – Dexterity** | Austin, TX | **8** | prototype vehicles & manipulators | PLM and released-drawing practice |
| 3 | Leidos | **Space Radiation Research Engineer (NASA HHPC)** *(discovery)* | Houston, TX | **7** | field science & instrumentation | radiation detection physics; **hybrid — see below** |
| 4 | Firefly Aerospace | **Fluids GSE Design Engineer II** | Briggs, TX | **7** | life-critical pressure & life-support systems | cryogenics; P&ID formalism; ASME |
| 5 | Sierra Space | ME III – Thermal Systems | 2 Locations | 6 | life-critical pressure & life-support systems | spacecraft TCS specialty; **location unconfirmed** |
| 6 | Firefly Aerospace | Spacecraft Thermal Engineer II | Cedar Park, TX | 4 | — | thermal *simulation* is the job; a listed gap |
| 7 | Pindrop | Research Scientist II *(discovery)* | Remote, US | 3 | — | audio/ML security research — title says nothing |
| 8 | Howard Hughes Medical Institute | Postdoctoral Scientist, Mendell Lab *(discovery)* | Remote, US | 2 | — | RNA biology; wrong kind of biologist |

**Apply: 1, 2, 3, 4. Maybe: 5. Skip: 6, 7, 8.**

---

**Firefly — Environmental Test Engineer III (8). Do this one first.** The
responsibilities are *"developing test plans, designing test fixtures,
managing the performance/execution of tests for product development,
acceptance, and qualification"*, plus authoring procedures and keeping records.

The decisive evidence is not on either résumé — it is in the ATS answers. The
sounding rocket failed twice because the deployment charge and the flight
computer were each bench-tested and never tested *together* under vibration;
building a shake table felt like a detour. The discipline adopted afterwards —
writing the test plan before the design so verification cannot be negotiated
away — is precisely what this job exists to enforce. Lead with the failure, not
the third flight that worked.

The gap is qualification *to an external standard*, which is a nice-to-have
here rather than the work, hence 8. Note the feed says Cedar Park while the
description says the lab is in Leander; both are Austin-metro.

**Apptronik — Hardware Test Engineer, Dexterity (8).** Hands-on mechanical,
electrical and system-level testing that *"sits inside the development team,
not downstream of it"*, with an explicit ask to consult on testability early.
Individual contributor, so "no team engineering" costs less here than in a
lead role. Two 8s is not indecision — it is one strength pointed at two kinds
of hardware, and the applications reuse most of the same material.

**Leidos — Space Radiation Research Engineer (7), and the reason the rubric
has a conditional rule.** This role is *genuinely both directions at once*: a
research engineer, at a contractor, supporting NASA's Space Radiation Analysis
Group. Per `SCORING.md`, a hybrid gets the **stricter** of the two allowances —
so it is scored without forgiving either the organisational-process gap or the
research-infrastructure gap, and it still reaches 7.

It earns that on instrumentation. The posting wants *"development, testing,
calibration, and troubleshooting of radiation detector systems for human
spaceflight"* — building sensing hardware, then trusting it with people's
lives. Twelve years of self-built instrumentation (water-chemistry loggers,
non-destructive samplers) plus a habitat rated for continuous human occupancy
is a direct answer to both halves. The gap is radiation-detection physics
specifically, which is learnable domain knowledge rather than a missing
capability. Houston, so in region, and found by the open sweep rather than any
tracked board.

**Firefly — Fluids GSE Design Engineer II (7).** Ground fluid systems:
*"P&IDs, tube & pipe sizing calculations for cryogenic, multiphase,
compressible & incompressible fluids, valve/fitting/component specification and
selection, design for critical safety equipment"*, then owning fabrication,
installation and checkout.

A habitat life-support loop **is** a safety-critical fluid system — oxygen
generation, CO₂ scrubbing, humidity, the valves and seals holding it together,
and a scrubber loop rebuilt twice after unanticipated degradation. Installing
and maintaining it alone for twelve years covers the second half outright.
Gaps: cryogenics, P&ID formalism, and design-to-code, which has never applied.

Located in **Briggs, TX** — worth noting because before the region tokens were
fixed, every Briggs role was silently dropped as out-of-region.

---

## The Applies, in full

Each block below is copied verbatim from `examples/candidates.md`, in table order. **`jobscan.py` truncates every description at 1,800 characters**, so a posting that stops mid-sentence below is not the whole of it — follow the URL for the rest. In this example the description text is the same redaction placeholder that stands in for the employer's copy in `examples/candidates.md`; a real run reproduces the posting itself here.

### 1. Firefly Aerospace — Environmental Test Engineer III (8)

**Matched via:** prototype vehicles & manipulators  
**Key gap:** qualification to NASA/Space Force standards  
**From `candidates.md` entry 1.**

- Location: Cedar Park TX
- URL: https://firefly.clearcompany.com/careers/jobs/b668da3f-5f5c-97b8-257f-f76e71a68ef8
- Prescreen hits: test engineer, environmental test

_**Description redacted.** jobscan writes the full posting text here — about 1,800 characters of it. Removed from this checked-in example so the repository does not republish Firefly Aerospace's copy; the real text is at the URL above. Placeholder below stands in for the length._

lorem ipsum dolor sit amet consectetur adipiscing elit sed do eiusmod tempor
incididunt ut labore et dolore magna aliqua ut enim ad minim veniam quis
nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat
duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore
eu fugiat nulla pariatur excepteur sint occaecat cupidatat non proident sunt
in culpa qui officia deserunt mollit anim id est laborum lorem ipsum dolor sit
amet consectetur adipiscing elit sed do eiusmod tempor incididunt ut labore et
dolore magna aliqua ut enim ad minim veniam quis nostrud exercitation ullamco
laboris nisi ut aliquip ex ea commodo consequat duis aute irure dolor in
reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur
excepteur sint occaecat cupidatat non proident sunt in culpa qui officia
deserunt mollit anim id est laborum lorem ipsum dolor sit amet consectetur
adipiscing elit sed do eiusmod tempor incididunt ut labore et dolore magna
aliqua ut enim ad minim veniam quis nostrud exercitation ullamco laboris nisi
ut aliquip ex ea commodo consequat duis aute irure dolor in reprehenderit in
voluptate velit esse cillum dolore eu fugiat nulla pariatur excepteur sint
occaecat cupidatat non proident sunt in culpa qui officia deserunt mollit anim
id est laborum lorem ipsum dolor sit amet consectetur adipiscing elit sed do
eiusmod tempor incididunt ut labore et dolore magna aliqua ut enim ad minim
veniam quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo
consequat duis aute irure dolor in reprehenderit in voluptate velit esse
cillum dolore eu fugiat nulla pariatur excepteur sint occaecat cupidatat non
proident sunt in culpa qui officia deserunt mollit anim id est laborum lorem
ipsum dolor sit amet consectetur adipiscing

### 2. Apptronik — Hardware Test Engineer – Dexterity (8)

**Matched via:** prototype vehicles & manipulators  
**Key gap:** PLM and released-drawing practice  
**From `candidates.md` entry 2.**

- Location: Austin, TX
- URL: https://boards.greenhouse.io/apptronik/jobs/5997414004?gh_jid=5997414004
- Prescreen hits: test engineer

_**Description redacted.** jobscan writes the full posting text here — about 1,800 characters of it. Removed from this checked-in example so the repository does not republish Apptronik's copy; the real text is at the URL above. Placeholder below stands in for the length._

lorem ipsum dolor sit amet consectetur adipiscing elit sed do eiusmod tempor
incididunt ut labore et dolore magna aliqua ut enim ad minim veniam quis
nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat
duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore
eu fugiat nulla pariatur excepteur sint occaecat cupidatat non proident sunt
in culpa qui officia deserunt mollit anim id est laborum lorem ipsum dolor sit
amet consectetur adipiscing elit sed do eiusmod tempor incididunt ut labore et
dolore magna aliqua ut enim ad minim veniam quis nostrud exercitation ullamco
laboris nisi ut aliquip ex ea commodo consequat duis aute irure dolor in
reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur
excepteur sint occaecat cupidatat non proident sunt in culpa qui officia
deserunt mollit anim id est laborum lorem ipsum dolor sit amet consectetur
adipiscing elit sed do eiusmod tempor incididunt ut labore et dolore magna
aliqua ut enim ad minim veniam quis nostrud exercitation ullamco laboris nisi
ut aliquip ex ea commodo consequat duis aute irure dolor in reprehenderit in
voluptate velit esse cillum dolore eu fugiat nulla pariatur excepteur sint
occaecat cupidatat non proident sunt in culpa qui officia deserunt mollit anim
id est laborum lorem ipsum dolor sit amet consectetur adipiscing elit sed do
eiusmod tempor incididunt ut labore et dolore magna aliqua ut enim ad minim
veniam quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo
consequat duis aute irure dolor in reprehenderit in voluptate velit esse
cillum dolore eu fugiat nulla pariatur excepteur sint occaecat cupidatat non
proident sunt in culpa qui officia deserunt mollit anim id est laborum lorem
ipsum dolor sit amet consectetur adipiscing

### 3. Leidos — Space Radiation Research Engineer (NASA HHPC) *(discovery)* (7)

**Matched via:** field science & instrumentation  
**Key gap:** radiation detection physics; the role is a hybrid, scored under the stricter allowance  
**From `candidates.md` entry 3.**

- Location: Houston, TX
- URL: https://www.themuse.com/jobs/leidos/space-radiation-research-engineer-nasa-hhpc
- Prescreen hits: research engineer

_**Description redacted.** jobscan writes the full posting text here — about 1,800 characters of it. Removed from this checked-in example so the repository does not republish Leidos's copy; the real text is at the URL above. Placeholder below stands in for the length._

lorem ipsum dolor sit amet consectetur adipiscing elit sed do eiusmod tempor
incididunt ut labore et dolore magna aliqua ut enim ad minim veniam quis
nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat
duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore
eu fugiat nulla pariatur excepteur sint occaecat cupidatat non proident sunt
in culpa qui officia deserunt mollit anim id est laborum lorem ipsum dolor sit
amet consectetur adipiscing elit sed do eiusmod tempor incididunt ut labore et
dolore magna aliqua ut enim ad minim veniam quis nostrud exercitation ullamco
laboris nisi ut aliquip ex ea commodo consequat duis aute irure dolor in
reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur
excepteur sint occaecat cupidatat non proident sunt in culpa qui officia
deserunt mollit anim id est laborum lorem ipsum dolor sit amet consectetur
adipiscing elit sed do eiusmod tempor incididunt ut labore et dolore magna
aliqua ut enim ad minim veniam quis nostrud exercitation ullamco laboris nisi
ut aliquip ex ea commodo consequat duis aute irure dolor in reprehenderit in
voluptate velit esse cillum dolore eu fugiat nulla pariatur excepteur sint
occaecat cupidatat non proident sunt in culpa qui officia deserunt mollit anim
id est laborum lorem ipsum dolor sit amet consectetur adipiscing elit sed do
eiusmod tempor incididunt ut labore et dolore magna aliqua ut enim ad minim
veniam quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo
consequat duis aute irure dolor in reprehenderit in voluptate velit esse
cillum dolore eu fugiat nulla pariatur excepteur sint occaecat cupidatat non
proident sunt in culpa qui officia deserunt mollit anim id est laborum lorem
ipsum dolor sit amet consectetur adipiscing

### 4. Firefly Aerospace — Fluids GSE Design Engineer II (7)

**Matched via:** life-critical pressure & life-support systems  
**Key gap:** cryogenics; P&ID formalism; ASME  
**From `candidates.md` entry 4.**

- Location: Briggs TX
- URL: https://firefly.clearcompany.com/careers/jobs/0a3f606e-7445-aef6-362f-fcad87116c84
- Prescreen hits: design engineer, fluid

_**Description redacted.** jobscan writes the full posting text here — about 1,800 characters of it. Removed from this checked-in example so the repository does not republish Firefly Aerospace's copy; the real text is at the URL above. Placeholder below stands in for the length._

lorem ipsum dolor sit amet consectetur adipiscing elit sed do eiusmod tempor
incididunt ut labore et dolore magna aliqua ut enim ad minim veniam quis
nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat
duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore
eu fugiat nulla pariatur excepteur sint occaecat cupidatat non proident sunt
in culpa qui officia deserunt mollit anim id est laborum lorem ipsum dolor sit
amet consectetur adipiscing elit sed do eiusmod tempor incididunt ut labore et
dolore magna aliqua ut enim ad minim veniam quis nostrud exercitation ullamco
laboris nisi ut aliquip ex ea commodo consequat duis aute irure dolor in
reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur
excepteur sint occaecat cupidatat non proident sunt in culpa qui officia
deserunt mollit anim id est laborum lorem ipsum dolor sit amet consectetur
adipiscing elit sed do eiusmod tempor incididunt ut labore et dolore magna
aliqua ut enim ad minim veniam quis nostrud exercitation ullamco laboris nisi
ut aliquip ex ea commodo consequat duis aute irure dolor in reprehenderit in
voluptate velit esse cillum dolore eu fugiat nulla pariatur excepteur sint
occaecat cupidatat non proident sunt in culpa qui officia deserunt mollit anim
id est laborum lorem ipsum dolor sit amet consectetur adipiscing elit sed do
eiusmod tempor incididunt ut labore et dolore magna aliqua ut enim ad minim
veniam quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo
consequat duis aute irure dolor in reprehenderit in voluptate velit esse
cillum dolore eu fugiat nulla pariatur excepteur sint occaecat cupidatat non
proident sunt in culpa qui officia deserunt mollit anim id est laborum lorem
ipsum dolor sit amet consectetur adipiscing

## Skip list, grouped by reason

- **The specialty IS the job** — *Spacecraft Thermal Engineer II* (4). Read it
  against row 5: both are "thermal", and they are not the same job. Sierra
  Space's is Responsible-Engineer ownership of hardware packages; Firefly's is
  *"advanced simulation and heat transfer expertise… develop validated thermal
  models"*, with MLI and radiator sizing. Modelling is the deliverable, and
  FEA/CFD is a listed gap. **Same title family, four points apart.**
- **Wrong kind of biologist** — *HHMI Postdoctoral Scientist, Mendell Lab* (2).
  The lab studies RNA biology, microRNAs and post-transcriptional regulation.
  Having a marine-ecology strand does not make molecular genetics adjacent.
  This is the research direction working correctly: it surfaced a real research
  posting, and the rubric rejected it on domain rather than on level.
- **Title reveals nothing** — *Pindrop, Research Scientist II* (3). Audio and
  ML security research, discoverable only by reading the description. See the
  flag below; this row is in the shortlist on purpose.

## Flags

- **Five domain-ambiguous "Research Scientist" rows are being left in the
  prescreen deliberately.** Adding a research direction to the profile means
  `research scientist` and `research engineer` are now signal terms, and those
  titles carry no domain information — Pindrop, FutureSearch, abridge and two
  mercor rows all arrived that way. Blocking harder would cost real research
  roles, and row 3 is proof: *Space Radiation Research Engineer* needed exactly
  that signal term to appear. **This is the prescreen working at its limit, not
  failing.** Reading requirements is the scorer's job.
- **The two-direction profile did not inflate scores**, which was the risk when
  `SCORING.md` was written. The conditional Expected-gaps rule held: rows 7 and
  8 are both research-direction postings and both scored ≤3, because the rule
  forgives research-infrastructure gaps but not domain mismatch.
- **Firefly dominates the tracked half** — 46 of 89. Proportionate to a
  169-role board in the right field, but one employer now sets the shape of
  this shortlist.
- **`2 Locations` is still the largest uncertainty**, at 15 of 89 tracked
  candidates, every one of them Sierra Space. A hydrate-on-shortlist pass remains the fix.
- **Next block-term candidates if they recur:** `Subject Matter Expert` (online
  universities) and `Commissioning` (plant startup roles that match
  `instrumentation`).

---

## Sources

The roles scored above were written by the employers that posted them and remain their property. They were read through:

- **Ashby** (https://www.ashbyhq.com) — Menlo
- **ClearCompany** (https://www.clearcompany.com) — Firefly Aerospace
- **Greenhouse** (https://www.greenhouse.io) — Apptronik, Colossal Biosciences, Diligent Robotics, Gather AI, ICON, IonQ, Ursa Major
- **Himalayas** (https://himalayas.app)
  - Job data sourced from Himalayas (https://himalayas.app).
- **Lever** (https://www.lever.co) — Everly Health
- **The Muse** (https://www.themuse.com) — USAA
- **Workday** (https://www.workday.com) — Sierra Space

Every row links to the original posting. Apply there, not here.
