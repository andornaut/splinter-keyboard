#!/usr/bin/env bash
# Copy manual traces from the routed/ masters back onto the working kicad/ PCBs.
# Run via: npm run copy-traces-routed-to-kicad
set -euo pipefail
shopt -s nullglob

VERSION="${npm_package_config_VERSION:?set via npm (npm run copy-traces-routed-to-kicad)}"
helper="${VERSION}/ergogen/kb_ergogen_helper/ergogen_helper.py"
files=("./${VERSION}/kicad/routed"/[!_]*.kicad_pcb)
if [ ${#files[@]} -eq 0 ]; then
  echo "No routed PCBs in ${VERSION}/kicad/routed/ -- nothing to do."
  exit 0
fi
for f in "${files[@]}"; do
  echo "$f"
  python3 "$helper" --no-backup copy-traces "$f" "./${VERSION}/kicad/$(basename "$f")"
done
