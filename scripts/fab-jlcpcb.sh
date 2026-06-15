#!/usr/bin/env bash
# Generate JLCPCB fabrication files from the routed/ masters: gerbers + drill
# always, plus assembly BOM + CPL when a parts file exists for the active version.
#
# Everything comes from kicad-cli, so the gerbers and the position file share one
# coordinate origin (required for the CPL to line up). LCSC part assignments live
# in ${VERSION}/kicad/jlcpcb-parts.json (keyed by footprint name) and are joined
# against the position file by gen-jlcpcb-bom-cpl.py -- outside the .kicad_pcb, so
# they survive Ergogen regeneration. Run via: npm run fab-jlcpcb
set -euo pipefail
shopt -s nullglob
here="$(dirname "${BASH_SOURCE[0]}")"
source "${here}/lib.sh"

VERSION="${npm_package_config_VERSION:?set via npm (npm run fab-jlcpcb)}"
parts="./${VERSION}/kicad/jlcpcb-parts.json"

# Fail early with a clear message if a runtime dependency is missing.
for cmd in kicad-cli zip python3; do
  command -v "$cmd" >/dev/null || { echo "Missing required command: $cmd" >&2; exit 1; }
done

# Standard JLCPCB 2-layer set (paste included for the assembly stencil).
layers="F.Cu,B.Cu,F.Paste,B.Paste,F.Silkscreen,B.Silkscreen,F.Mask,B.Mask,Edge.Cuts"

require_pcbs "./${VERSION}/kicad/routed"
for f in "${files[@]}"; do
  name="$(basename "${f%.kicad_pcb}")"
  out="dist/${VERSION}/kicad/jlcpcb/${name}"
  gerber_dir="${out}/gerber"
  rm -rf "$out"
  mkdir -p "$gerber_dir"
  echo "$f -> $out"

  kicad-cli pcb export gerbers --no-protel-ext --layers "$layers" \
    --output "${gerber_dir}/" "$f" >/dev/null
  kicad-cli pcb export drill --format excellon --drill-origin absolute \
    --output "${gerber_dir}/" "$f" >/dev/null
  ( cd "$gerber_dir" && zip -qr "../${name}-gerber.zip" . )

  # Assembly files are optional per version: emit them only where a parts file exists.
  if [ -f "$parts" ]; then
    pos="${out}/${name}-pos.csv"
    kicad-cli pcb export pos --format csv --units mm --output "$pos" "$f" >/dev/null
    python3 "${here}/gen-jlcpcb-bom-cpl.py" \
      --pos "$pos" --parts "$parts" \
      --bom "${out}/${name}-BOM.csv" --cpl "${out}/${name}-CPL.csv"
  else
    echo "  no ${parts} -- gerbers only (no assembly BOM/CPL)"
  fi
done
