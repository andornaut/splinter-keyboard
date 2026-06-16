#!/usr/bin/env bash
# Generate JLCPCB fabrication files from the routed/ masters: gerbers + drill
# always, plus assembly BOM + CPL when a parts file exists for the active version.
#
# Everything comes from kicad-cli, so the gerbers and the position file share one
# coordinate origin (required for the CPL to line up). LCSC part assignments live
# in ${VERSION}/kicad/jlcpcb-parts.json (keyed by footprint name) and are joined
# against the position file by gen-jlcpcb-bom-cpl.py -- outside the .kicad_pcb, so
# they survive Ergogen regeneration. Run via: npm run fab
set -euo pipefail
shopt -s nullglob
source "$(dirname "${BASH_SOURCE[0]}")/lib.sh"

VERSION="${npm_package_config_VERSION:?set via npm (npm run fab)}"
parts="./${VERSION}/kicad/jlcpcb-parts.json"

require_cmds kicad-cli zip python3

# Provenance gate: refuse to fab if any routed board drifted from the current
# config.yaml (or is unstamped). Only routed/ is checked -- it is the fab source;
# unrouted/ drift is irrelevant to fab (the full sync check is the bare
# `npm run validate:provenance`). Under set -e a nonzero exit aborts the whole
# fab before any gerber is written. See provenance_gate_routed in lib.sh.
provenance_gate_routed

require_pcbs "./${VERSION}/kicad/routed"
for f in "${files[@]}"; do
  name="$(basename "${f%.kicad_pcb}")"
  out="dist/${VERSION}/kicad/jlcpcb/${name}"
  mkdir -p "$out"
  echo "$f -> $out"

  # DRC gate: refill the GND pour, then fail the fab on any error-level violation
  # or unrouted net BEFORE export_jlcpcb_fab clears this board's prior output, so a
  # failing run never destroys its last-good gerbers. On failure print where to
  # look; the || keeps the abort hard despite the redirect.
  # No --schematic-parity: the Ergogen-generated boards have no .kicad_sch.
  # --refill-zones is in-memory only (no --save-board), so the master is untouched.
  mute_pcbnew_noise kicad-cli pcb drc --refill-zones --severity-error \
    --exit-code-violations --format json \
    --output "${out}/${name}-drc.json" "$f" >/dev/null \
    || { echo "DRC failed for ${name}: see ${out}/${name}-drc.json" >&2; exit 1; }

  export_jlcpcb_fab "$f" "$out" "$name" "$parts"
done

ok "fab: ${#files[@]} board(s) exported to dist/${VERSION}/kicad/jlcpcb/"
