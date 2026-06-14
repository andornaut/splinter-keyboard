#!/usr/bin/env bash
# Generate JLCPCB fabrication files (gerbers/drill) from the routed/ masters.
# Run via: npm run fab-jlcpcb
set -euo pipefail

VERSION="${npm_package_config_VERSION:?set via npm (npm run fab-jlcpcb)}"
for f in "./${VERSION}/kicad/routed"/[!_]*.kicad_pcb; do
  echo "$f"
  kikit fab jlcpcb --nametemplate 'splinter_{boardTitle}_{date}' "$f" "dist/${VERSION}/kicad/jlcpcb/"
done
