#!/usr/bin/env bash
# Copy manual traces (and teardrops) from the routed/ masters back onto the working
# kicad/unrouted/ boards. kb_ergogen_helper copy-traces handles the tracks (segments,
# arcs, vias); copy-teardrops.py handles the teardrop zones it leaves behind.
# Run via: npm run copy:traces-to-unrouted
set -euo pipefail
shopt -s nullglob
source "$(dirname "${BASH_SOURCE[0]}")/lib.sh"

VERSION="${npm_package_config_VERSION:?set via npm (npm run copy:traces-to-unrouted)}"
helper="${VERSION}/ergogen/kb_ergogen_helper/ergogen_helper.py"

# A board carries human routing only if it has tracks at a width other than the
# include_traces_vias stub width (0.25mm = VCC net class). Every fresh ergogen
# emits the footprint stubs at 0.25mm; the human matrix routing uses the Default
# net class (0.20mm). A board with only 0.25mm tracks is stub-only: freshly
# generated, or a master whose routing was clobbered.
#
# Asked of the source, this says the master is worth copying, and asking the
# board directly avoids the false alarm where the helper legitimately copies 0
# because the routes already exist in unrouted/. Asked of the destination, it
# says the board is fresh enough to be copied onto (see the merge note below).
has_human_routes() {
  # Count track-width lines that are not the 0.25mm stub width; >0 means routed.
  # Use grep -v | wc -l (not grep -vq): the system grep may be ugrep, whose -vq
  # reports "pattern absent" rather than "a non-matching line exists".
  local n
  n=$(grep -A4 '(segment' "$1" | grep '(width ' | grep -v '(width 0.25)' | wc -l)
  [ "$n" -gt 0 ]
}

require_pcbs "${VERSION}/kicad/routed"
for f in "${files[@]}"; do
  if ! has_human_routes "$f"; then
    echo "ERROR $f: no human routing on it (only footprint stubs), refusing to copy" >&2
    echo "    Restore the routed master: git checkout HEAD -- $f" >&2
    exit 1
  fi
  dst="${VERSION}/kicad/unrouted/$(basename "$f")"
  # The copy MERGES: copy-traces adds every routed track the destination does not
  # already hold verbatim. That is only safe onto a freshly generated board. Since
  # routed/ now differs from unrouted/ by MOVED copper (tidy-patterns.py and
  # tidy-slivers.py), not deletions alone, a snapped run is not verbatim-equal to
  # the copy it replaced, so onto a board that still carries the previous routing
  # it lands ALONGSIDE it: two runs of one net a fraction of a millimetre apart.
  # DRC cannot see that (same net) and cleanup-tracks.py does not remove it (each
  # is fully connected and neither is an exact duplicate of the other), so the
  # stale copy rides into the fab source and another accumulates every run.
  if has_human_routes "$dst"; then
    echo "ERROR $dst: already carries routing, refusing to copy onto it" >&2
    echo "    This step merges rather than replaces, so it needs a freshly generated" >&2
    echo "    board: npm run ergogen && npm run copy:dist-to-unrouted, or npm run pipeline" >&2
    exit 1
  fi
  mute_pcbnew_noise python3 "$helper" --no-backup copy-traces "$f" "$dst"
  mute_pcbnew_noise python3 ./scripts/copy-teardrops.py "$f" "$dst"
done

ok "copy:traces-to-unrouted: traces + teardrops copied for ${#files[@]} board(s) into ${VERSION}/kicad/unrouted/"
