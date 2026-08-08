#!/usr/bin/env bash
# Copy freshly generated boards from dist/ over the working kicad/unrouted/ copies,
# first backing up each existing one into kicad/unrouted-backups/ (timestamped).
# That backup is the only copy of routing done in unrouted/ and not yet promoted
# to routed/, which this step would otherwise overwrite; everything older is
# reproducible from config.yaml plus routed/, so only BACKUP_KEEP are kept per
# board. Run via: npm run copy:dist-to-unrouted
set -euo pipefail
shopt -s nullglob
source "$(dirname "${BASH_SOURCE[0]}")/lib/common.sh"

BACKUP_KEEP=5

VERSION="${npm_package_config_VERSION:?set via npm (npm run copy:dist-to-unrouted)}"
src_dir="dist/${VERSION}/ergogen/pcbs"
kicad_dir="${VERSION}/kicad"
dst_dir="${kicad_dir}/unrouted"
backup_dir="${kicad_dir}/unrouted-backups"

require_pcbs "$src_dir" "No generated boards in ${src_dir}/ -- run 'npm run ergogen' first"
mkdir -p "$dst_dir" "$backup_dir"
stamp="$(date +%Y-%m-%d_%H%M%S)"
pruned=0
for f in "${files[@]}"; do
  name="$(basename "$f")"
  stem="${name%.kicad_pcb}"
  existing="${dst_dir}/${name}"
  if [ -f "$existing" ]; then
    cp "$existing" "${backup_dir}/${stem}-${stamp}.kicad_pcb"
  fi
  cp "$f" "$existing"

  # The stamp is fixed-width and leading-zero padded, so the glob sorts oldest
  # first and the surplus is the head of the list.
  kept=("${backup_dir}/${stem}"-[0-9]*.kicad_pcb)
  if [ "${#kept[@]}" -gt "$BACKUP_KEEP" ]; then
    doomed=("${kept[@]:0:${#kept[@]} - BACKUP_KEEP}")
    rm -f "${doomed[@]}"
    pruned=$((pruned + ${#doomed[@]}))
    note "  pruned ${backup_dir}/${stem}: ${#doomed[@]} backup(s) past the last ${BACKUP_KEEP}"
  fi
done

# Apply project settings to the unrouted/ projects (this copy step owns the
# unrouted tier). See apply_project_settings in lib/common.sh.
apply_project_settings "$dst_dir"

ok "copy:dist-to-unrouted: ${#files[@]} board(s) copied to ${dst_dir}/ (backups in ${backup_dir}/, ${pruned} pruned)"
