#!/usr/bin/env bash
# Checks a generated shortlist against the section skeleton in SCORING.md,
# and reports whether the candidates.md it was scored from has been scored
# before. Read-only: it checks, it never writes.
#
# Usage:  ./check-shortlist.sh                     before scoring
#         ./check-shortlist.sh --after [file]      after writing [file]
#
# /jobscan-score runs this twice. Before scoring, the duplicate check reads
# EVERY shortlist, shortlist.md included -- the file most likely to already
# hold this candidates.md's stamp is the one a previous pass just wrote.
# After writing, the file on disk necessarily carries the current stamp, so
# --after skips the duplicate question (it was answered before scoring) and
# checks only the skeleton of what was written.
set -u
cd "$(dirname "$0")"

after=0
if [ "${1-}" = "--after" ]; then
  after=1
  shift
fi
target=${1:-shortlist.md}

bold=$'\033[1m'; red=$'\033[31m'; grn=$'\033[32m'; yel=$'\033[33m'; off=$'\033[0m'
[ -t 1 ] || { bold=""; red=""; grn=""; yel=""; off=""; }

fail=0

# The canonical section skeleton. Every shortlist carries all of these, as
# level-2 headings, in this order, with nothing else at level 2 -- an empty
# section says "None this run." rather than disappearing. Kept in step with
# the "Section skeleton" section of SCORING.md; change them together.
skeleton=(
  "Do this one first"
  "Table"
  "The roles scoring ≥6"
  "Apply / Maybe / Skip"
  "The Applies, in full"
  "Skip list, grouped by reason"
  "Flags"
  "Config feedback"
  "Sources"
)

# --- the fingerprint of the current candidates.md -------------------------
# Twelve hex characters of sha256. Long enough that a collision is not a
# thing that happens, short enough to sit in a header line a human reads.
fingerprint() {
  shasum -a 256 "$1" 2>/dev/null | cut -c1-12
}

echo "${bold}jobscan — shortlist check${off}"
echo

# --- has this candidates.md already been scored? --------------------------
echo "${bold}Duplicate scoring${off}"
if [ "$after" = 1 ]; then
  echo "  skip --after: this was checked before scoring"
elif [ ! -f candidates.md ]; then
  echo "  ${yel}TODO${off} candidates.md is missing -- run python3 jobscan.py first"
else
  fp=$(fingerprint candidates.md)
  prior=""
  for f in shortlist.md shortlist-*.md; do
    [ -f "$f" ] || continue
    if grep -q "sha256 $fp" "$f" 2>/dev/null; then
      prior="$prior $f"
    fi
  done
  if [ -n "$prior" ]; then
    echo "  ${red}FAIL${off} candidates.md (sha256 $fp) was already scored:"
    for f in $prior; do echo "         $f"; done
    echo "         Re-read that shortlist instead of scoring again, or re-run"
    echo "         jobscan.py for fresh candidates."
    fail=1
  else
    echo "  ${grn}ok${off}   candidates.md (sha256 $fp) has not been scored yet"
  fi
fi

# --- the section skeleton -------------------------------------------------
echo
echo "${bold}Section skeleton — $target${off}"
if [ ! -f "$target" ]; then
  echo "  ${yel}TODO${off} $target does not exist yet -- nothing to check"
  echo
  exit $fail
fi

head -n 1 "$target" | grep -q '^# Shortlist — ' \
  && echo "  ${grn}ok${off}   title line" \
  || { echo "  ${red}FAIL${off} first line is not '# Shortlist — <date>'"; fail=1; }

stamp=$(grep -m1 '^Scored from: candidates.md' "$target" || true)
if [ -z "$stamp" ]; then
  echo "  ${red}FAIL${off} no 'Scored from: candidates.md ... sha256 <hex>' stamp line"
  echo "         Without it the duplicate check above cannot see this run."
  fail=1
elif ! printf '%s' "$stamp" | grep -q 'sha256 [0-9a-f]\{12\}'; then
  echo "  ${red}FAIL${off} stamp line carries no 12-hex sha256: $stamp"
  fail=1
else
  echo "  ${grn}ok${off}   ${stamp}"
fi

# Compare the level-2 headings present against the skeleton, in order.
# Done in the shell rather than with diff <(...): this script must not write,
# and process substitution is not available everywhere it runs.
oldifs=$IFS; IFS=$'\n'; set -f
got=($(grep '^## ' "$target" | sed 's/^## //'))
set +f; IFS=$oldifs
if [ "${got[*]-}" = "${skeleton[*]}" ]; then
  echo "  ${grn}ok${off}   all ${#skeleton[@]} sections, in order, nothing extra at ## level"
else
  echo "  ${red}FAIL${off} sections do not match the skeleton:"
  for want in "${skeleton[@]}"; do
    case " ${got[*]-} " in
      *" $want "*) ;;
      *) echo "         missing: ## $want" ;;
    esac
  done
  for have in ${got[@]+"${got[@]}"}; do
    case " ${skeleton[*]} " in
      *" $have "*) ;;
      *) echo "         unexpected: ## $have" ;;
    esac
  done
  i=0
  for have in ${got[@]+"${got[@]}"}; do
    [ "$have" = "${skeleton[$i]-}" ] || { echo "         out of order at: ## $have"; break; }
    i=$((i + 1))
  done
  echo "         Order matters, and an empty section stays in with 'None this run.'"
  fail=1
fi

echo
[ "$fail" = 0 ] && echo "${grn}All good.${off}" || echo "${red}Fix the FAILs above.${off}"
exit $fail
