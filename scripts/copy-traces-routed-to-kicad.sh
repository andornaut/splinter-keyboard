#!/usr/bin/env bash
# Copy manual traces from the routed/ masters back onto the working kicad/ PCBs.
# Run via: npm run copy-traces-routed-to-kicad
set -euo pipefail
shopt -s nullglob
source "$(dirname "${BASH_SOURCE[0]}")/lib.sh"

VERSION="${npm_package_config_VERSION:?set via npm (npm run copy-traces-routed-to-kicad)}"
helper="${VERSION}/ergogen/kb_ergogen_helper/ergogen_helper.py"
require_pcbs "./${VERSION}/kicad/routed"
for f in "${files[@]}"; do
  echo "$f"
  mute_pcbnew_noise python3 "$helper" --no-backup copy-traces "$f" "./${VERSION}/kicad/$(basename "$f")"
done

ok "copy-traces-routed-to-kicad: traces copied for ${#files[@]} PCB(s) into ${VERSION}/kicad/"
