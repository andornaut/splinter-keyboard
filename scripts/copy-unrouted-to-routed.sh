#!/usr/bin/env bash
# Copy the working kicad/unrouted/ boards onto the routed/ masters (the fab source), then
# add a filled GND pour to each master, clean up the copper no route uses, and
# tidy away the strays and the segments an edit left shorter than they are wide.
# The pour is applied here, after manual routing, rather than at build time so
# routing happens on a clean board; the cp overwrites each master with the
# pour-free working copy first, so the pour is always freshly flowed around the
# current traces. The cleanup runs after the pour, never before: it treats a
# filled pour as copper, which is what keeps a GND stitching via. The three steps
# after it are a cycle, not a sequence, and repeat until they settle. Run via:
# npm run copy:unrouted-to-routed
set -euo pipefail
shopt -s nullglob
source "$(dirname "${BASH_SOURCE[0]}")/lib/common.sh"

VERSION="${npm_package_config_VERSION:?set via npm (npm run copy:unrouted-to-routed)}"
kicad_dir="${VERSION}/kicad"
src_dir="${kicad_dir}/unrouted"
dst_dir="${kicad_dir}/routed"

# How many times the cleanup/tidy cycle below may run on one board. The three steps
# feed each other: tidy-slivers.py deletes segments, which changes the shape
# tidy-patterns.py reads a run as, so a run left alone on one pass can be snappable
# on the next; a snap in turn leaves collinear fragments for cleanup-tracks.py to
# merge and can leave a sliver of its own. Running them once each therefore emits a
# master that is one pass behind its own tooling, and the next build ships different
# copper from the same inputs. Same contract as cleanup-tracks.py's own loop: a pass
# still changing the board on the last one is a hard error, since the board is then
# not settling and every further pass is another candidate master.
TIDY_PASSES=3

require_pcbs "$src_dir"
mkdir -p "$dst_dir"

# Apply project settings to the routed/ projects (this copy step owns the routed
# tier, the fab source whose DRC floors fab's DRC gate reads). See
# apply_project_settings in lib/common.sh. Before the boards, not after: the two steps that
# move copper read this project's net classes to test what they lay down against
# the clearance every other net asks for, so a settings change has to land first or
# the run that introduces it measures against the clearances it replaced. It reads
# the .kicad_pro files, which the copy never touches, so it does not need the boards.
apply_project_settings "$dst_dir"

for f in "${files[@]}"; do
  dst="${dst_dir}/$(basename "$f")"
  # One master at a time, copy included: every step below can hard-fail (a sliver
  # over its cap, a snap into a keepout), and a master this run has not reached yet
  # must still be the routed board it was, not an un-poured working copy. Nothing
  # downstream would catch that: a board with no ground plane passes fab's DRC gate.
  cp "$f" "$dst"
  mute_pcbnew_noise python3 ./scripts/add-gnd-zone.py "$dst"

  for ((pass = 1; pass <= TIDY_PASSES; pass++)); do
    before="$(sha256sum <"$dst")"
    mute_pcbnew_noise python3 ./scripts/cleanup-tracks.py "$dst"
    # After the cleanup, which merges the collinear fragments an edit leaves behind:
    # a fragmented run does not read as the shape it is, so a stray would be missed.
    mute_pcbnew_noise python3 ./scripts/tidy-patterns.py "$dst"
    # Last, so every sliver it sees sits in copper the route uses and has already
    # been snapped to the pattern.
    mute_pcbnew_noise python3 ./scripts/tidy-slivers.py "$dst"
    # Each step leaves the board untouched when it has nothing to do, so an
    # unchanged file is the fixpoint. Close every pass with its outcome: the last
    # pass repeats the lines of the one before it, and this is what tells a reader
    # that a re-reported LEFT ALONE is a second look rather than a second finding.
    if [ "$(sha256sum <"$dst")" = "$before" ]; then
      echo "  tidy ${dst}: settled, pass ${pass}/${TIDY_PASSES} changed nothing"
      break
    fi
    echo "  tidy ${dst}: pass ${pass}/${TIDY_PASSES} changed it, going again"
    if [ "$pass" -eq "$TIDY_PASSES" ]; then
      echo "ERROR ${dst}: still changing after ${TIDY_PASSES} tidy passes" >&2
      echo "    The cleanup and tidy steps are trading changes rather than settling, so" >&2
      echo "    this build and the next would ship different copper from the same routing." >&2
      echo "    Read the pass output above for what kept moving, settle it in KiCad, re-run" >&2
      exit 1
    fi
  done
done

ok "copy:unrouted-to-routed: ${#files[@]} board(s) copied to ${dst_dir}/ with GND pour, then cleaned, snapped to the pattern and tidied of slivers until settled (max ${TIDY_PASSES} passes)"
