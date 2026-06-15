#!/usr/bin/env bash
# Generate JLCPCB fabrication files (gerbers/drill) from the routed/ masters.
# Run via: npm run fab-jlcpcb
set -euo pipefail
shopt -s nullglob
source "$(dirname "${BASH_SOURCE[0]}")/lib.sh"

VERSION="${npm_package_config_VERSION:?set via npm (npm run fab-jlcpcb)}"
require_pcbs "./${VERSION}/kicad/routed"
for f in "${files[@]}"; do
  echo "$f"
  kikit fab jlcpcb --nametemplate 'splinter_{boardTitle}_{date}' "$f" "dist/${VERSION}/kicad/jlcpcb/"
done
