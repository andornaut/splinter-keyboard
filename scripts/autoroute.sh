#!/usr/bin/env bash
# Autoroute each working kicad/ PCB in place via headless Freerouting.
# Run via: npm run autoroute
set -euo pipefail

VERSION="${npm_package_config_VERSION:?set via npm (npm run autoroute)}"
for f in "./${VERSION}/kicad"/[!_]*.kicad_pcb; do
  echo "$f"
  python3 ./scripts/autoroute.py "$f" "dist/${VERSION}/kicad/freerouting/"
done
