# Example application material (fictional)

Input material for demoing **`/jobscan-setup`**. Everything here is invented —
Sandy Cheeks is a cartoon character.

Point the skill at this folder to see the full setup workflow without using
your own documents:

    /jobscan-setup

then give it `examples/material` when it asks where your material is.

## Who this is

A mechanical engineer and marine biologist who spent twelve years running a
one-person pressurized research station on the sea floor, now moving back to
Texas and looking for aerospace, robotics or extreme-environment engineering
work. `examples/profile.md` is roughly what a good run should produce from
these documents.

## What is in here, and why

| file | what it is |
|---|---|
| `resume-2026-engineering.md` | current résumé, aimed at hardware engineering roles |
| `resume-2019-research-scientist.txt` | older résumé, aimed at research positions — same career, framed as science rather than engineering |
| `cover-letter-aerospace.md` | for a structures role |
| `cover-letter-robotics.txt` | for a manipulator/dexterity role |
| `ats-question-answers.md` | saved answers to recurring application questions |

This folder is deliberately **not** a clean input. It carries the friction real
material has, and each piece is there to make the skill work for its answer:

- **The two résumés frame the same career differently** — one as an engineer,
  one as a scientist. Which is she? Both, and reconciling them is how the
  capability strands get found. Neither document alone gives you the profile.
- **The dates disagree.** The 2019 résumé says "seven-year dataset", the 2026
  one says twelve. Consistent, but only if you notice the older document is
  older; publication counts differ for the same reason.
- **Achievements arrive without scale or context.** "Supervised field
  volunteers" — how many, and did anyone report to her? "Built a powered
  exoskeleton" — to what standard, over how long?
- **One cover letter oversells badly.** The aerospace letter claims "extensive
  experience qualifying flight hardware to demanding standards", which nothing
  else in the folder supports and which `examples/profile.md` lists as an
  outright gap. Whether the skill copies that claim or walks it back is the
  single best test of whether the gap interrogation is working.
- **The other cover letter and the ATS answers are unusually candid**, because
  that is where a direct question gets a direct answer. They give the
  interrogation something to confirm — but only about three of the seven gaps
  in `examples/profile.md`. The rest still have to be asked for.

## This has actually been run

`examples/profile.md` is **not hand-written** — it is the output of running
`/jobscan-setup` against this folder on 2026-08-24.
So the claim that a good run lands close to them is verified rather than
assumed. Run it yourself and you should get something similar.

Four details in that profile could not have come from reading these files
alone, and exist only because the skill asked:

- **"twelve years" throughout.** The 2019 résumé's own arithmetic contradicts
  its stated 2014 start date — it claims seven years. The number had to be
  confirmed rather than picked.
- **The rocket is recorded as crewed only on the third flight**, after two
  uncrewed test failures. The résumé says "crewed" flatly; the ATS answers
  describe three attempts without saying who was aboard.
- **Volunteer supervision is marked "numbers not recorded"** rather than
  quietly given a number.
- **The unsupported flight-qualification claim is named inside a gap**, so a
  future run cannot be talked into scoring it.

The last one matters most: that claim sits in `cover-letter-aerospace.md` and
will be read again on every future run. Naming it in the profile is what stops
it being believed.
