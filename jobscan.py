#!/usr/bin/env python3
"""Pull open roles from configured career portals, drop the obvious noise,
and emit a candidate set for Claude to score against profile.md.

    python3 jobscan.py            # fetch, diff against seen.json, write candidates.md
    python3 jobscan.py --all      # ignore seen.json (re-score everything currently open)
    python3 jobscan.py --check    # just verify every configured portal still answers

Deliberately read-only: it reads public job feeds and writes local files.
It never logs in and never submits anything.
"""
import argparse
import json
import os
import re
import sys
import time
from datetime import datetime, timezone

import adapters

HERE = os.path.dirname(os.path.abspath(__file__))
CONFIG = os.path.join(HERE, "config.json")
SEEN = os.path.join(HERE, "seen.json")
# Jobs that PASSED the prescreen but lost to a cap. Held back from
# seen.json so they return next run, and given first claim when they do.
DEFERRED = os.path.join(HERE, "deferred.json")
OUT_MD = os.path.join(HERE, "candidates.md")
OUT_JSON = os.path.join(HERE, "candidates.json")
DELAY = 1.0  # be a polite client; these are public endpoints but not free to serve


def load_json(path, default):
    if not os.path.exists(path):
        return default
    with open(path) as f:
        return json.load(f)


def find_fill_markers(node, path="config"):
    """Locate every unfilled template placeholder, so a fresh clone fails loudly.

    An unfilled `signal` list is the dangerous case: it is valid JSON, every
    source answers, --check prints ok, and the run quietly yields zero
    candidates because no title can score a signal hit. That looks like "no
    good jobs this week" rather than "you have not set this up".
    """
    found = []
    if isinstance(node, dict):
        for k, v in node.items():
            # Documentation keys explain the FILL: convention, so they contain
            # the marker without being placeholders themselves.
            if k.endswith("_README") or k in ("_warning", "_comment"):
                continue
            found += find_fill_markers(v, f"{path}.{k}")
    elif isinstance(node, list):
        for i, v in enumerate(node):
            found += find_fill_markers(v, f"{path}[{i}]")
    elif isinstance(node, str) and "FILL:" in node:
        found.append((path, node))
    return found


# --- location filter -----------------------------------------------------
# Feeds disagree wildly on format: "US, CA, Santa Clara", "San Francisco, CA",
# "Sunnyvale, California", "Remote - United States", "UK-Remote", "4 Locations".
# So: split into parts, keep the job if ANY part is somewhere you want.
#
# The region lists live in config.json under "regions", NOT here -- `wanted` is
# the one you must set, and it is personal. DEFAULT_FOREIGN below is a generic
# list of non-US place names that applies to any US-based search; override it
# in config.json ("regions": {"foreign": [...]}) if you are searching elsewhere.

DEFAULT_FOREIGN = [
    "united kingdom", "uk-", "uk,", "london", "ireland", "dublin", "germany",
    "munich", "berlin", "netherlands", "eindhoven", "veldhoven", "france",
    "paris", "switzerland", "zurich", "zürich", "finland", "helsinki", "oulu",
    "sweden", "poland", "warsaw", "krakow", "romania", "hungary", "israel",
    "tel aviv", "india", "bangalore", "bengaluru", "hyderabad", "noida",
    "china", "shanghai", "beijing", "shenzhen", "taiwan", "taipei", "hsinchu",
    "japan", "tokyo", "korea", "seoul", "singapore", "malaysia", "penang",
    "vietnam", "da nang", "ho chi minh", "philippines", "australia", "sydney",
    "canada", "toronto", "vancouver", "ontario", "mexico", "guadalajara",
    "brazil", "uae", "dubai", "abu dhabi", "egypt", "cairo", "spain", "italy",
    "portugal", "lisbon", "czech", "prague", "austria", "belgium", "denmark",
    "norway", "scotland", "wales", "new zealand", "thailand", "indonesia",
]

DEFAULT_AMBIGUOUS = ["locations", "multiple", "various"]


def location_ok(loc, wanted, foreign=None, ambiguous=None):
    """Is this posting somewhere you would work? True = keep.

    `wanted`, and optionally `foreign` / `ambiguous`, come from the `regions`
    block in config.json -- read its `_README` for how to write them, which is
    fiddlier than it looks.

    Feeds disagree wildly on format ("US, CA, Santa Clara", "Boston MA",
    "Remote - United States", "UK-Remote", "4 Locations"), so this is substring
    matching over the whole string, in this order:

        1. empty, or vague ("4 Locations")     -> keep
        2. a `wanted` token appears anywhere   -> keep
        3. otherwise a `foreign` token appears -> drop
        4. otherwise bare "remote"             -> keep
        5. otherwise                           -> drop, out-of-region domestic

    Two deliberate choices in there:

    * Step 1 keeps vague postings because Workday hides multi-site listings
      behind a count, and dropping them would lose real roles. THIS IS THE
      KNOWN SOFT SPOT: a vague posting whose hidden list is entirely foreign
      passes, and one board alone once contributed 24 candidates that every
      one read "2 Locations". Those have to be opened by hand.

    * Step 2 does not let a bare "remote" count as an in-region token, because
      "UK-Remote" and "Flexible / Remote; Katowice, Poland" both contain it.
      Remote-only postings pass later, at step 4, once no foreign token has
      turned up.
    """
    foreign = DEFAULT_FOREIGN if foreign is None else foreign
    ambiguous = DEFAULT_AMBIGUOUS if ambiguous is None else ambiguous
    if not loc or not loc.strip():
        return True
    low = loc.lower()
    if any(a in low for a in ambiguous):
        return True
    # "remote" alone is not evidence of a domestic role: "Flexible / Remote;
    # Katowice, Poland" and "UK-Remote" both contain it. Require a concrete
    # in-region token before letting a bare remote listing through.
    concrete = [w for w in wanted if w != "remote"]
    has_home = any(w in low for w in concrete)
    has_foreign = any(f in low for f in foreign)
    if has_home:
        return True          # a wanted location is named somewhere
    if has_foreign:
        return False         # foreign named, no wanted location to offset it
    if "remote" in low:
        return True          # remote with no foreign office attached
    return False             # some other out-of-region domestic city


def prescreen(jobs, rules):
    """Title-level gate. Cheap, and keeps the scoring payload small.

    Discovery rows face a stricter bar. The tracked companies were chosen
    deliberately, so a weak title on one of their boards still deserves a
    look. An open sweep of every employer is mostly roles with nothing to do
    with the profile, and the permissive list let those through.
    """
    block = [re.compile(p, re.I) for p in rules["block"]]
    signal = [s.lower() for s in rules["signal"]]
    d_block = [re.compile(p, re.I) for p in rules.get("discovery_block", [])]
    d_signal = [s.lower() for s in rules.get("discovery_signal", [])]
    kept = []
    for j in jobs:
        t = j["title"].lower()
        if any(p.search(t) for p in block):
            continue
        if j.get("group") == "discovery":
            if any(p.search(t) for p in d_block):
                continue
            if d_signal and not any(s in t for s in d_signal):
                continue
        hits = [s for s in signal if s in t]
        if len(hits) < rules.get("min_signal", 1):
            continue
        j = dict(j, signal_hits=hits, signal_score=len(hits))
        kept.append(j)
    # Same role posted in several locations shows up as separate rows.
    merged = {}
    for j in kept:
        key = (j["company"], re.sub(r"\s+", " ", j["title"]).strip().lower())
        if key in merged:
            prev = merged[key]
            if j["location"] and j["location"] not in prev["location"]:
                prev["location"] += f"; {j['location']}"
            prev.setdefault("also", []).append(j["url"])
            # A role can arrive from both a tracked board and the discovery
            # sweep; keep it attributed to the tracked source.
            if prev.get("group") == "discovery" and j.get("group") != "discovery":
                prev["group"] = j.get("group", "tracked")
        else:
            merged[key] = j
    kept = list(merged.values())
    kept.sort(key=lambda x: (-x["signal_score"], x["company"], x["title"]))
    return kept


def allocate(kept, cap, priority=frozenset()):
    """Round-robin across companies so one large portal cannot crowd out the
    others -- a global sort let one board's 600 roles bury a small board's 8.

    `priority` holds job ids deferred by a previous run's cap. Selection below
    is q.pop(0) in FEED ORDER (the sort at the end is presentation only), and
    feed order is broadly stable -- so without this, the same jobs would win
    every run and the deferred ones would starve forever instead of being
    lost outright. Sorting within each company keeps the round-robin fair
    ACROSS companies while letting the backlog drain.
    """
    by_co = {}
    for j in kept:
        by_co.setdefault(j["company"], []).append(j)
    if priority:
        for q in by_co.values():
            q.sort(key=lambda j: j["job_id"] not in priority)
    out, queues = [], list(by_co.values())
    while len(out) < cap and any(queues):
        for q in queues:
            if q and len(out) < cap:
                out.append(q.pop(0))
        queues = [q for q in queues if q]
    out.sort(key=lambda x: (-x["signal_score"], x["company"], x["title"]))
    return out


def fetch_all(cfg):
    jobs, report = [], []
    for c in cfg["companies"]:
        kind = c["kind"]
        fn = adapters.ADAPTERS.get(kind)
        if fn is None:
            report.append((c["company"], kind, "no such adapter", 0))
            continue
        try:
            got = fn(c)
            for g in got:
                g["group"] = c.get("group", "tracked")
            jobs.extend(got)
            report.append((c["company"], kind, "ok", len(got)))
        except Exception as e:
            report.append((c["company"], kind, f"{type(e).__name__}: {str(e)[:60]}", 0))
        time.sleep(DELAY)
    for company, kind, status, n in report:
        flag = "ok  " if status == "ok" else "FAIL"
        print(f"  {flag} {company:<12} {kind:<10} {n:>4}  {'' if status=='ok' else status}",
              file=sys.stderr)
    return jobs


TRUNCATION_FLOOR = 600  # chars; below this a feed is probably capping text


def warn_if_truncated(jobs):
    """Shout if a source's descriptions look capped rather than complete.

    Truncated text must never be scored. A 500-character sample is enough to
    notice a role and never enough to judge one: one posting that read like an
    HPC engineering job turned out, in full, to be rack cabling and OS
    provisioning, and it had scored well on the excerpt.

    This inspects the descriptions themselves rather than trusting a per-source
    flag. A flag has to be set by whoever adds the source -- who is exactly the
    person who does not yet know the feed is capped.
    """
    by_co = {}
    for j in jobs:
        by_co.setdefault(j["company"], []).append((j["description"] or "").rstrip())
    for co, texts in sorted(by_co.items()):
        lens = sorted(len(t) for t in texts)
        median = lens[len(lens) // 2]
        clipped = sum(1 for t in texts if t.endswith(("…", "...")))
        if median < TRUNCATION_FLOOR or clipped > len(texts) / 3:
            print(f"[jobscan] WARNING: {co} descriptions look TRUNCATED "
                  f"(median {median} chars; {clipped}/{len(texts)} end in an "
                  f"ellipsis). Do not score these -- find a source that "
                  f"returns full text, or drop it.", file=sys.stderr)


def attribution_block(cfg):
    """Credit the platforms a run read from.

    The job descriptions are written by the employers and remain theirs; this
    names the platform each was read through, which is what those platforms
    ask for. Himalayas documents an explicit request for a visible link back,
    so its line is reproduced verbatim from REQUIRED_CREDIT.
    """
    by_kind = {}
    for c in cfg["companies"]:
        by_kind.setdefault(c["kind"], []).append(c.get("company", ""))
    lines = ["## Sources", "",
             "Descriptions above were written by the employers that posted them and "
             "remain their property. They were read through:", ""]
    for kind in sorted(by_kind):
        name, url = adapters.ATTRIBUTION.get(kind, (kind, ""))
        who = ", ".join(sorted(x for x in by_kind[kind] if x and not x.startswith("(")))
        via = f" — {who}" if who else ""
        lines.append(f"- **{name}** ({url}){via}")
        if kind in adapters.REQUIRED_CREDIT:
            lines.append(f"  - {adapters.REQUIRED_CREDIT[kind]}")
    lines += ["", "Every row links to the original posting. Apply there, not here."]
    return "\n".join(lines) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--all", action="store_true", help="ignore seen.json")
    ap.add_argument("--check", action="store_true", help="verify portals only")
    args = ap.parse_args()

    cfg = load_json(CONFIG, None)
    if cfg is None:
        sys.exit(f"[jobscan] no {CONFIG}. Copy examples/config.json, or see README.md.")

    # `_companies_examples` is reference material in the template, not sources.
    unfilled = [f for f in find_fill_markers(cfg)
                if not f[0].startswith("config._companies_examples")]
    if unfilled:
        where = "\n".join(f"    {p}" for p, _ in unfilled[:12])
        more = f"\n    ... and {len(unfilled) - 12} more" if len(unfilled) > 12 else ""
        msg = (f"[jobscan] config.json still has {len(unfilled)} unfilled "
               f"FILL: placeholder(s):\n{where}{more}\n"
               "    Run ./check-setup.sh, or /jobscan-setup to fill them in with Claude.\n"
               "    A worked example is in examples/config.json.")
        if not args.check:
            sys.exit(msg + "\n[jobscan] refusing to scan -- it would silently "
                           "return zero candidates.")
        print(msg + "\n[jobscan] --check continues anyway (connectivity only).",
              file=sys.stderr)

    print(f"[jobscan] {datetime.now(timezone.utc):%Y-%m-%d %H:%M} UTC — "
          f"{len(cfg['companies'])} portals", file=sys.stderr)
    jobs = fetch_all(cfg)
    print(f"[jobscan] {len(jobs)} open roles total", file=sys.stderr)
    if args.check:
        return

    seen = set(load_json(SEEN, []))
    fresh = jobs if args.all else [j for j in jobs if j["job_id"] not in seen]
    print(f"[jobscan] {len(fresh)} new since last run", file=sys.stderr)

    rules = cfg["prescreen"]
    if cfg.get("filter_locations", True):
        reg = cfg.get("regions") or {}
        wanted = reg.get("wanted") or []
        if not wanted:
            sys.exit("[jobscan] config.json has no regions.wanted -- every job "
                     "would be dropped. Set it, or set filter_locations:false.")
        before = len(fresh)
        fresh = [j for j in fresh
                 if location_ok(j["location"], wanted,
                                reg.get("foreign"), reg.get("ambiguous"))]
        print(f"[jobscan] {len(fresh)} in target locations "
              f"(dropped {before - len(fresh)})", file=sys.stderr)
    screened = prescreen(fresh, rules)
    # Discovery gets its own budget. Sharing one budget would let a broad
    # search spanning 50 employers starve the boards we deliberately track,
    # because allocate() gives every company an equal round-robin share.
    deferred = load_json(DEFERRED, {})
    prio = set(deferred)
    known = allocate([j for j in screened if j.get("group") != "discovery"],
                     rules.get("max_to_score", 60), prio)
    disco = allocate([j for j in screened if j.get("group") == "discovery"],
                     rules.get("max_discovery", 40), prio)
    kept = known + disco
    print(f"[jobscan] {len(known)} tracked + {len(disco)} discovery "
          f"= {len(kept)} to score", file=sys.stderr)

    need = [j for j in kept if not j["description"]]
    if need:
        print(f"[jobscan] fetching {len(need)} missing descriptions", file=sys.stderr)
        for j in need:
            adapters.hydrate(j)
            time.sleep(0.4)

    # Re-check the region filter now that hydration has replaced Workday's
    # vague "N Locations" with the concrete site list. This is the ONLY way
    # to catch a multi-site posting whose hidden list is entirely foreign
    # without also discarding the multi-site postings that are genuinely in
    # region -- and the request it depends on has already been made above.
    #
    # These are dropped from the OUTPUT only. They stay in `kept_ids` below,
    # so they are marked seen rather than deferred: a wrong location is a
    # verdict, not a capacity limit.
    scored_ids = {j["job_id"] for j in kept}
    if cfg.get("filter_locations", True):
        reg = cfg.get("regions") or {}
        wanted = reg.get("wanted") or []
        stale = [j for j in kept
                 if not location_ok(j["location"], wanted,
                                    reg.get("foreign"), reg.get("ambiguous"))]
        if stale:
            kept = [j for j in kept if j not in stale]
            print(f"[jobscan] {len(stale)} dropped after hydration revealed "
                  f"their real locations (e.g. {stale[0]['location'][:48]!r})",
                  file=sys.stderr)

    warn_if_truncated(kept)

    with open(OUT_JSON, "w") as f:
        json.dump(kept, f, indent=1)

    with open(OUT_MD, "w") as f:
        f.write(f"# Candidates — {datetime.now(timezone.utc):%Y-%m-%d}\n\n")
        f.write(f"{len(kept)} roles past prescreen, out of {len(fresh)} new "
                f"({len(jobs)} open overall).\n\n")
        for i, j in enumerate(kept, 1):
            desc = re.sub(r"\s+", " ", j["description"])[:1800]
            tag = " *(discovery)*" if j.get("group") == "discovery" else ""
            f.write(f"## {i}. {j['company']} — {j['title']}{tag}\n")
            f.write(f"- Location: {j['location'] or 'n/a'}\n- URL: {j['url']}\n")
            f.write(f"- Prescreen hits: {', '.join(j['signal_hits'])}\n\n")
            f.write((desc or "_(no description in feed — open the URL)_") + "\n\n")
        f.write("---\n\n" + attribution_block(cfg))

    # only mark seen once we've successfully written the outputs.
    #
    # A job cut by max_to_score / max_discovery was never JUDGED -- it lost to
    # a capacity limit, not to a verdict. Marking it seen would delete it
    # silently and permanently, since it can never appear in a later delta.
    # Location- and prescreen-rejects ARE marked: those are deterministic
    # verdicts. (Retune the prescreen and re-run with --all to revisit them.)
    deferred_ids = {j["job_id"] for j in screened} - scored_ids

    with open(SEEN, "w") as f:
        json.dump(sorted((seen | {j["job_id"] for j in jobs}) - deferred_ids), f)

    # Rebuilt from what is deferred NOW, not accumulated: an entry disappears
    # by itself once the posting comes down. Keep the original date so the
    # backlog's age is visible.
    today = f"{datetime.now(timezone.utc):%Y-%m-%d}"
    still = {i: deferred.get(i, today) for i in sorted(deferred_ids)}
    with open(DEFERRED, "w") as f:
        json.dump(still, f, indent=1)

    if still:
        print(f"[jobscan] {len(still)} passed prescreen but were deferred by a "
              f"cap (oldest {min(still.values())}) -- they will get first claim "
              f"next run; raise max_to_score/max_discovery or tighten the "
              f"prescreen to clear the backlog", file=sys.stderr)

    print(f"[jobscan] wrote {OUT_MD}", file=sys.stderr)


if __name__ == "__main__":
    main()
