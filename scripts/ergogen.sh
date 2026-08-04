#!/usr/bin/env bash
# Generate outlines/boards from the active version's ergogen config, then
# post-process each PCB (update footprints via kb_ergogen_helper, recenter on
# the sheet) and ensure custom project settings (net class + DRC floors) in the
# KiCad project files. The GND pour is added later, at copy:unrouted-to-routed,
# so routing happens on a clean board. Run via: npm run ergogen
#
# The footprint and kb_ergogen_helper submodules are used at their pinned
# (checked-out) revision; this script ensures they are present (so a non-recursive
# clone still works) but does not advance them. See README "Updating footprint submodules".
set -euo pipefail
shopt -s nullglob
source "$(dirname "${BASH_SOURCE[0]}")/lib.sh"

VERSION="${npm_package_config_VERSION:?set via npm (npm run ergogen)}"
helper="${VERSION}/ergogen/kb_ergogen_helper/ergogen_helper.py"
out_dir="dist/${VERSION}/ergogen"

git submodule update --init ergogen/footprints/ceoloide ergogen/footprints/infused-kim ergogen/kb_ergogen_helper

# Ergogen narrates its twelve phases on the way to "Done."; none of it says
# anything the step banner does not. Hold the output and print it only if the run
# fails, where it is the whole diagnosis, or under PIPELINE_VERBOSE.
if [ -n "${PIPELINE_VERBOSE:-}" ]; then
  npx ergogen "./${VERSION}/ergogen/" --output "${out_dir}/"
else
  ergogen_log="$(npx ergogen "./${VERSION}/ergogen/" --output "${out_dir}/" 2>&1)" \
    || { echo "$ergogen_log" >&2; exit 1; }
fi
require_pcbs "${out_dir}/pcbs" "No boards generated in ${out_dir}/pcbs/ -- check the config"
for f in "${files[@]}"; do
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
# add-keepout-zones.py.
mute_pcbnew_noise python3 ./scripts/add-keepout-zones.py "${files[@]}"

# Apply project settings to the generated dist/ projects (ergogen owns this tier;
# unrouted/ and routed/ are owned by the copy steps). See apply_project_settings
# in lib.sh.
apply_project_settings "${out_dir}/pcbs"

ok "ergogen: ${#files[@]} board(s) generated and post-processed in ${out_dir}/pcbs/"
