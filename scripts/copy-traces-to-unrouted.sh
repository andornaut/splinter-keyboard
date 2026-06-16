#!/usr/bin/env bash
# Copy manual traces (and teardrops) from the routed/ masters back onto the working
# kicad/unrouted/ PCBs. kb_ergogen_helper copy-traces handles the tracks (segments,
# arcs, vias); copy-teardrops.py handles the teardrop zones it leaves behind.
# Run via: npm run copy:traces-to-unrouted
set -euo pipefail
shopt -s nullglob
source "$(dirname "${BASH_SOURCE[0]}")/lib.sh"

VERSION="${npm_package_config_VERSION:?set via npm (npm run copy:traces-to-unrouted)}"
helper="${VERSION}/ergogen/kb_ergogen_helper/ergogen_helper.py"

# A routed master has human routing only if it carries tracks at a width other
# than the include_traces_vias stub width (0.25mm = VCC net class). Every fresh
# ergogen emits the footprint stubs at 0.25mm; the human matrix routing uses the
# Default net class (0.20mm). A board with only 0.25mm tracks is stub-only, i.e.
# was never routed (or its routing was clobbered). Checking the source directly
# avoids the false alarm where the helper legitimately copies 0 because the
# routes already exist in unrouted/.
has_human_routes() {
  # Count track-width lines that are not the 0.25mm stub width; >0 means routed.
  # Use grep -v | wc -l (not grep -vq): the system grep may be ugrep, whose -vq
  # reports "pattern absent" rather than "a non-matching line exists".
  local n
  n=$(grep -A4 '(segment' "$1" | grep '(width ' | grep -v '(width 0.25)' | wc -l)
  [ "$n" -gt 0 ]
}

require_pcbs "./${VERSION}/kicad/routed"
for f in "${files[@]}"; do
  echo "$f"
  if ! has_human_routes "$f"; then
    echo "ERROR: $f has no human routing (only footprint stubs); refusing to copy. Restore the routed master (e.g. git checkout HEAD -- $f)." >&2
    exit 1
  fi
  dst="./${VERSION}/kicad/unrouted/$(basename "$f")"
  mute_pcbnew_noise python3 "$helper" --no-backup copy-traces "$f" "$dst"
  mute_pcbnew_noise python3 ./scripts/copy-teardrops.py "$f" "$dst"
done

ok "copy:traces-to-unrouted: traces + teardrops copied for ${#files[@]} PCB(s) into ${VERSION}/kicad/unrouted/"
