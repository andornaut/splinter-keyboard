#!/usr/bin/env bash
# Generate outlines/PCBs from the active version's ergogen config, then
# post-process each PCB (update footprints via kb_ergogen_helper, recenter on
# the sheet) and ensure custom project settings (net class + DRC floors) in the
# KiCad project files. The GND pour is added later, at copy:unrouted-to-routed,
# so routing happens on a clean board. Run via: npm run ergogen
#
# Footprint submodules are used at their pinned (checked-out) revision; this
# script does not advance them. See README "Updating footprint submodules".
set -euo pipefail
shopt -s nullglob
source "$(dirname "${BASH_SOURCE[0]}")/lib.sh"

VERSION="${npm_package_config_VERSION:?set via npm (npm run ergogen)}"
helper="${VERSION}/ergogen/kb_ergogen_helper/ergogen_helper.py"
out_dir="dist/${VERSION}/ergogen"

git submodule update --init ergogen/footprints/ceoloide ergogen/footprints/infused-kim
npx ergogen "./${VERSION}/ergogen/" --output "${out_dir}/"
require_pcbs "${out_dir}/pcbs" "ergogen produced no PCBs in ${out_dir}/pcbs/ -- check the config."
for f in "${files[@]}"; do
  echo "$f"
  mute_pcbnew_noise python3 "$helper" --no-backup update-pcb "$f"
  mute_pcbnew_noise python3 ./scripts/recenter.py "$f"
done

# Stamp config provenance into the title block of every board in one invocation,
# so all halves share one build stamp (timestamp/commit/hash). It rides the cp
# steps into unrouted/ and routed/ unchanged; validate:provenance checks it before fab.
mute_pcbnew_noise python3 ./scripts/stamp-provenance.py \
  --version "${VERSION}" --config "${VERSION}/ergogen/config.yaml" "${files[@]}"

# Add copper keepout rule areas (2mm perimeter ring + a disk around each screw
# boss). Like the stamp, they ride the cp steps into unrouted/ (so routing and
# DRC see them) and routed/ (where add-gnd-zone pours around them). See
# add-keepout-zones.py and AGENTS.md "v4: Copper keepout zones".
mute_pcbnew_noise python3 ./scripts/add-keepout-zones.py "${files[@]}"

# Apply project settings to the generated dist/ projects (ergogen owns this tier;
# unrouted/ and routed/ are owned by the copy steps). See apply_project_settings
# in lib.sh.
apply_project_settings "${out_dir}/pcbs"

ok "ergogen: ${#files[@]} PCB(s) generated and post-processed in ${out_dir}/pcbs/"
