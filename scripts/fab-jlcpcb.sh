#!/usr/bin/env bash
# Generate JLCPCB fabrication files (gerbers/drill) from the routed/ masters.
# Run via: npm run fab-jlcpcb
set -euo pipefail
shopt -s nullglob

VERSION="${npm_package_config_VERSION:?set via npm (npm run fab-jlcpcb)}"
files=("./${VERSION}/kicad/routed"/[!_]*.kicad_pcb)
if [ ${#files[@]} -eq 0 ]; then
  echo "No routed PCBs in ${VERSION}/kicad/routed/ -- nothing to do."
  exit 0
fi
for f in "${files[@]}"; do
  echo "$f"
  kikit fab jlcpcb --nametemplate 'splinter_{boardTitle}_{date}' "$f" "dist/${VERSION}/kicad/jlcpcb/"
done
