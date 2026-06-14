#!/usr/bin/env bash
# Copy freshly generated PCBs from dist/ over the working kicad/ copies, first
# backing up each existing kicad/ PCB into kicad/backups/ (timestamped) so routed
# work is recoverable. Run via: npm run copy-pcbs-to-kicad
set -euo pipefail

VERSION="${npm_package_config_VERSION:?set via npm (npm run copy-pcbs-to-kicad)}"
src_dir="dist/${VERSION}/ergogen/pcbs"
dst_dir="${VERSION}/kicad"
backup_dir="${dst_dir}/backups"

mkdir -p "$backup_dir"
stamp="$(date +%Y%m%d-%H%M%S)"
for f in "$src_dir"/[!_]*.kicad_pcb; do
  name="$(basename "$f")"
  existing="${dst_dir}/${name}"
  if [ -f "$existing" ]; then
    cp "$existing" "${backup_dir}/${name%.kicad_pcb}-${stamp}.kicad_pcb"
  fi
  cp "$f" "$existing"
done
