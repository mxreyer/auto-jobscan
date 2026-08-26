#!/usr/bin/env bash
# Reports how far through setup you are, and what to do next.
# Read-only: it checks, it never writes. Setup itself is /jobscan-setup.
# Read-only: it never edits your files. See README.md for the guided version.
set -u
cd "$(dirname "$0")"

bold=$'\033[1m'; red=$'\033[31m'; grn=$'\033[32m'; yel=$'\033[33m'; off=$'\033[0m'
[ -t 1 ] || { bold=""; red=""; grn=""; yel=""; off=""; }

echo "${bold}jobscan — setup check${off}"
echo

fail=0

# --- python ---------------------------------------------------------------
if command -v python3 >/dev/null 2>&1; then
  echo "  ${grn}ok${off}   $(python3 --version 2>&1) -- stdlib only, nothing to install"
else
  echo "  ${red}FAIL${off} python3 not found"; fail=1
fi

# --- the three files you must make yours ----------------------------------
echo
echo "${bold}Files to make yours${off}"
for f in profile.md SCORING.md config.json; do
  if [ ! -f "$f" ]; then
    echo "  ${red}FAIL${off} $f is missing -- copy examples/$f as a starting point"; fail=1
    continue
  fi
  if [ "$f" = config.json ]; then
    # Reuse jobscan's own marker scan so the two can never disagree.
    n=$(python3 -c '
import json, sys
sys.path.insert(0, ".")
import jobscan
cfg, _ = jobscan.load_config()
found = [f for f in jobscan.find_fill_markers(cfg)
         if not f[0].startswith("config._companies_examples")]
print(len(found))
for p, _ in found[:20]:
    print(p, file=sys.stderr)
' 2>/tmp/jobscan_fill.$$ ) || n=error
    marks=$(cat /tmp/jobscan_fill.$$ 2>/dev/null); rm -f /tmp/jobscan_fill.$$
  else
    # grep -c prints 0 and exits 1 when there are no matches; keep the 0.
    n=$(grep -c 'FILL:' "$f" 2>/dev/null || true)
    n=${n:-0}
    marks=""
  fi
  if [ "$n" = "0" ]; then
    if [ "$f" = config.json ] && [ -f config.local.json ]; then
      echo "  ${grn}ok${off}   $f + config.local.json -- no FILL: markers left after merge"
    else
      echo "  ${grn}ok${off}   $f -- no FILL: markers left"
    fi
  else
    echo "  ${yel}TODO${off} $f -- ${n} FILL: marker(s) remaining"; fail=1
    if [ -n "$marks" ]; then
      echo "$marks" | sed 's/^/         /'
    fi
  fi
done

# --- generated state ------------------------------------------------------
echo
echo "${bold}State${off}"
if [ -f seen.json ]; then
  c=$(python3 -c 'import json;print(len(json.load(open("seen.json"))))' 2>/dev/null || echo "?")
  echo "  ${grn}ok${off}   seen.json -- ${c} job ids already reported (runs are deltas)"
else
  echo "  ${grn}ok${off}   no seen.json yet -- the first run will see everything as new"
fi

# --- what next ------------------------------------------------------------
echo
if [ "$fail" -eq 0 ]; then
  echo "${grn}${bold}Setup looks complete.${off} Next:"
  echo "    python3 jobscan.py --check   # verify every source answers"
  echo "    python3 jobscan.py --all     # first full run"
  echo
  echo "  On --check, read the COUNTS, not just the ok/FAIL flags. A source can"
  echo "  return 0 and still print ok -- that is the one failure this cannot catch."
  echo
  echo "  Then score what came through:  /jobscan-score  (in Claude Code)"
else
  echo "${bold}Not ready yet.${off} Two ways to finish:"
  echo "    - In Claude Code, run:  /jobscan-setup   (point it at a folder of"
  echo "      your resumes, cover letters and ATS answers; it does the rest)"
  echo "    - Or edit the files above by hand; examples/ has a worked version of each"
  echo "      See the Setup section of README.md."
  echo
  echo "  To watch it run before setting up your own:"
  echo "    cp examples/config.json config.json && cp examples/profile.md profile.md \\"
  echo "      && cp examples/SCORING.md SCORING.md && python3 jobscan.py --all"
fi
exit 0
