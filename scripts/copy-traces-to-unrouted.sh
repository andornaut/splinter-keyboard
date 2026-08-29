#!/usr/bin/env bash
# Copy manual traces (and teardrops) from the routed/ masters back onto the working
# kicad/unrouted/ boards. kb_ergogen_helper copy-traces handles the tracks (segments,
# arcs, vias); copy-teardrops.py handles the teardrop zones it leaves behind.
# Run via: npm run copy:traces-to-unrouted
set -euo pipefail
shopt -s nullglob
source "$(dirname "${BASH_SOURCE[0]}")/lib/common.sh"

VERSION="${npm_package_config_VERSION:?set via npm (npm run copy:traces-to-unrouted)}"
helper="${VERSION}/ergogen/kb_ergogen_helper/ergogen_helper.py"

# The Default net class's track width, read from the board's sibling .kicad_pro,
# where apply-project-settings.py wrote it. Not restated here: a copy that drifted
# would read every master as stub-only and refuse every copy. Printed the way
# KiCad writes it into a (width ...) clause, so it can be matched as text.
default_track_width() {
  python3 - "${1%.kicad_pcb}.kicad_pro" <<'EOF'
import json
import sys

pro = sys.argv[1]
with open(pro) as f:
    classes = json.load(f).get("net_settings", {}).get("classes") or []
for c in classes:
    if c.get("name") == "Default" and c.get("track_width"):
        print(f"{c['track_width']:g}")
        break
else:
    sys.exit(f"ERROR {pro}: no Default net class track_width; apply-project-settings.py writes the project")
EOF
}

# A board carries human routing only if it has tracks at the Default net class's
# track width: the hand-routed matrix is drawn at it, while the include_traces_vias
# stubs every fresh ergogen emits carry the footprints' own trace_width, which is
# wider. A board with no track at the Default width is stub-only: freshly
# generated, or a master whose routing was clobbered. (Retuning the Default width
# onto the footprints' stub width would blind this test.)
#
# Asked of the source, this says the master is worth copying, and asking the
# board directly avoids the false alarm where the helper legitimately copies 0
# because the routes already exist in unrouted/. Asked of the destination, it
# says the board is fresh enough to be copied onto (see the merge note below).
has_human_routes() {
  # Count segments at the Default track width ($2); >0 means routed. grep | wc -l
  # rather than grep -c, which exits 1 on zero matches and would read as a failure
  # under pipefail.
  local n
  # shellcheck disable=SC2126 # see above
  n=$(grep -A4 '(segment' "$1" | grep -F "(width $2)" | wc -l)
  [ "$n" -gt 0 ]
}

require_pcbs "${VERSION}/kicad/routed"
for f in "${files[@]}"; do
  width="$(default_track_width "$f")"
  if ! has_human_routes "$f" "$width"; then
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
  if has_human_routes "$dst" "$width"; then
    echo "ERROR $dst: already carries routing, refusing to copy onto it" >&2
    echo "    This step merges rather than replaces, so it needs a freshly generated" >&2
    echo "    board: npm run ergogen && npm run copy:dist-to-unrouted, or npm run pipeline" >&2
    exit 1
  fi
  mute_pcbnew_noise python3 "$helper" --no-backup copy-traces "$f" "$dst"
  mute_pcbnew_noise python3 ./scripts/copy-teardrops.py "$f" "$dst"
done

ok "copy:traces-to-unrouted: traces + teardrops copied for ${#files[@]} board(s) into ${VERSION}/kicad/unrouted/"
