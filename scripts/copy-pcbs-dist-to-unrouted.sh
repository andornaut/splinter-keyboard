#!/usr/bin/env bash
# Copy freshly generated PCBs from dist/ over the working kicad/unrouted/ copies,
# first backing up each existing one into kicad/backups/ (timestamped) so routed
# work is recoverable. Run via: npm run copy-pcbs-dist-to-unrouted
set -euo pipefail
shopt -s nullglob
source "$(dirname "${BASH_SOURCE[0]}")/lib.sh"

VERSION="${npm_package_config_VERSION:?set via npm (npm run copy-pcbs-dist-to-unrouted)}"
src_dir="dist/${VERSION}/ergogen/pcbs"
kicad_dir="${VERSION}/kicad"
dst_dir="${kicad_dir}/unrouted"
backup_dir="${kicad_dir}/backups"

require_pcbs "$src_dir" "No generated PCBs in ${src_dir}/ -- run 'npm run build' first."
mkdir -p "$dst_dir" "$backup_dir"
stamp="$(date +%Y-%m-%d_%H%M%S)"
for f in "${files[@]}"; do
  name="$(basename "$f")"
  existing="${dst_dir}/${name}"
  if [ -f "$existing" ]; then
    cp "$existing" "${backup_dir}/${name%.kicad_pcb}-${stamp}.kicad_pcb"
  fi
  cp "$f" "$existing"
done

# Apply project settings to the unrouted/ projects (this copy step owns the
# unrouted tier). See apply_project_settings in lib.sh.
apply_project_settings "$dst_dir"

ok "copy-pcbs-dist-to-unrouted: ${#files[@]} PCB(s) copied to ${dst_dir}/ (backups in ${backup_dir}/)"
