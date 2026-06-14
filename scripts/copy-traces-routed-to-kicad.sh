#!/usr/bin/env bash
# Copy manual traces from the routed/ masters back onto the working kicad/ PCBs.
# Run via: npm run copy-traces-routed-to-kicad
set -euo pipefail

VERSION="${npm_package_config_VERSION:?set via npm (npm run copy-traces-routed-to-kicad)}"
helper="${VERSION}/ergogen/kb_ergogen_helper/ergogen_helper.py"
for f in "./${VERSION}/kicad/routed"/[!_]*.kicad_pcb; do
  echo "$f"
  python3 "$helper" --no-backup copy-traces "$f" "./${VERSION}/kicad/$(basename "$f")"
done
