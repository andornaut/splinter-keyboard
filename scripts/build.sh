#!/usr/bin/env bash
# Update vendored footprint submodules, generate outlines/PCBs from the active
# version's ergogen config, then post-process each PCB (update footprints via
# kb_ergogen_helper, recenter on the sheet). Run via: npm run build
set -euo pipefail

VERSION="${npm_package_config_VERSION:?set via npm (npm run build)}"
helper="${VERSION}/ergogen/kb_ergogen_helper/ergogen_helper.py"
out_dir="dist/${VERSION}/ergogen"

git submodule update --init --remote ergogen/footprints/ceoloide ergogen/footprints/infused-kim
npx ergogen "./${VERSION}/ergogen/" --output "${out_dir}/"
for f in "${out_dir}"/pcbs/[!_]*.kicad_pcb; do
  echo "$f"
  python3 "$helper" --no-backup update-pcb "$f"
  python3 ./scripts/recenter.py "$f"
done
