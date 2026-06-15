#!/usr/bin/env bash
# Copy the working kicad/unrouted/ PCBs onto the routed/ masters (the fab source), then
# add a filled B.Cu GND pour to each master. The pour is applied here, after
# manual routing, rather than at build time so routing happens on a clean board;
# the cp overwrites each master with the pour-free working copy first, so the
# pour is always freshly flowed around the current traces. Run via:
# npm run copy-pcbs-unrouted-to-routed
set -euo pipefail
shopt -s nullglob
source "$(dirname "${BASH_SOURCE[0]}")/lib.sh"

VERSION="${npm_package_config_VERSION:?set via npm (npm run copy-pcbs-unrouted-to-routed)}"
kicad_dir="${VERSION}/kicad"
src_dir="${kicad_dir}/unrouted"
dst_dir="${kicad_dir}/routed"

require_pcbs "$src_dir"
mkdir -p "$dst_dir"
for f in "${files[@]}"; do
  dst="${dst_dir}/$(basename "$f")"
  cp "$f" "$dst"
  mute_pcbnew_noise python3 ./scripts/add-gnd-zone.py "$dst"
done

ok "copy-pcbs-unrouted-to-routed: ${#files[@]} PCB(s) copied to ${dst_dir}/ with GND pour"
