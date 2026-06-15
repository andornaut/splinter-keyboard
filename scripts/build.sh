#!/usr/bin/env bash
# Generate outlines/PCBs from the active version's ergogen config, then
# post-process each PCB (update footprints via kb_ergogen_helper, recenter on
# the sheet) and ensure custom project settings (net class + DRC floors) in the
# KiCad project files. The GND pour is added later, at copy-pcbs-kicad-to-routed,
# so routing happens on a clean board. Run via: npm run build
#
# Footprint submodules are used at their pinned (checked-out) revision; this
# script does not advance them. See README "Updating footprint submodules".
set -euo pipefail
shopt -s nullglob
source "$(dirname "${BASH_SOURCE[0]}")/lib.sh"

VERSION="${npm_package_config_VERSION:?set via npm (npm run build)}"
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

# Idempotently apply the VCC net class and DRC floors to the generated and routed
# KiCad projects (these live in .kicad_pro, which ergogen does not maintain).
# Missing globs are tolerated by the helper, so this is safe before a version is
# routed. (No mute_pcbnew_noise: this script edits .kicad_pro JSON and never
# imports pcbnew, so it emits no PROPERTY_ENUM noise.)
python3 ./scripts/apply-project-settings.py \
  "${out_dir}"/pcbs/[!_]*.kicad_pro \
  "${VERSION}"/kicad/[!_]*.kicad_pro
