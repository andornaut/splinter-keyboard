#!/usr/bin/env bash
# Combine the routed/ masters into one JLCPCB panel, then export its fab files.
#
# Pays JLC's per-order assembly setup + stencil fee once instead of once per half.
# The panel is built with KiKit (scripts/panelize.py), then gerbers/drill/pos +
# assembly BOM/CPL are exported via lib.sh's export_jlcpcb_fab (shared with fab.sh).
#
# KiCad 10 support is only in KiKit git master (no PyPI release yet), so KiKit
# lives in a dedicated venv. panelize.sh runs panelize.py with that venv's python
# and PYTHONNOUSERSITE=1 (so a stale ~/.local pcbnewTransition can't shadow it).
# Set KIKIT_PYTHON to override the interpreter. The per-half fab is the
# strict-DRC gate and source of truth; the panel's DRC here is advisory only,
# because KiKit panels routinely trip board-to-board / tab clearance rules.
# Run via: npm run panelize
set -euo pipefail
shopt -s nullglob
source "$(dirname "${BASH_SOURCE[0]}")/lib.sh"

VERSION="${npm_package_config_VERSION:?set via npm (npm run panelize)}"
parts="./${VERSION}/kicad/jlcpcb-parts.json"
config="./${VERSION}/ergogen/config.yaml"
out="dist/${VERSION}/kicad/jlcpcb/panel"
panel="dist/${VERSION}/kicad/panelize/panel.kicad_pcb"

require_cmds kicad-cli zip python3

# Resolve the KiKit interpreter: KIKIT_PYTHON override, else the dedicated venv,
# else fail with a pointer to the installer (the ansible hobbies role, kicad tag).
kikit_py="${KIKIT_PYTHON:-/opt/kikit/bin/python}"
[ -x "$kikit_py" ] || { echo "KiKit venv python not found at ${kikit_py}. Install it (ansible-ctrl hobbies role, kicad tag) or set KIKIT_PYTHON." >&2; exit 1; }
PYTHONNOUSERSITE=1 "$kikit_py" -c 'import kikit.panelize' 2>/dev/null \
  || { echo "KiKit not importable under ${kikit_py} (needs KiCad 10 git-master KiKit + pcbnewTransition). Reinstall via the ansible hobbies role." >&2; exit 1; }

# Provenance gate: same as fab, refuse to panel if routed/ drifted from
# config. Scoped to routed/ (the only stage the panel consumes), so unrouted/
# drift never blocks a legitimate panel of a current routed master. See
# provenance_gate_routed in lib.sh.
provenance_gate_routed

require_pcbs "./${VERSION}/kicad/routed"

# Build the panel (KiKit prints wx image-handler + pcbnew PROPERTY_ENUM noise to
# stderr; mute_kikit_noise drops just those, keeping real errors and the exit
# code). panelize.py creates the output directory itself.
echo "panel <- ${files[*]}"
mute_kikit_noise env PYTHONNOUSERSITE=1 "$kikit_py" ./scripts/panelize.py "${files[@]}" \
  --output "$panel" --version "$VERSION" --config "$config"

# DRC is advisory on the panel: write the report but do NOT abort on violations
# (board-to-board and tab clearances are expected). The per-half fab run
# is the hard DRC gate. Refill zones in-memory so the report is meaningful.
mkdir -p "$out"
echo "panel -> $out"
if mute_pcbnew_noise kicad-cli pcb drc --refill-zones --severity-error \
    --exit-code-violations --format json \
    --output "${out}/panel-drc.json" "$panel" >/dev/null; then
  echo "  panel DRC: clean"
else
  echo "  panel DRC: violations present (advisory only) -- review ${out}/panel-drc.json" >&2
fi

# Export gerbers/drill/pos + BOM/CPL from the panel. Shared with fab.sh;
# the parts file is joined by footprint Package (panelization preserves it), and
# KiKit's fiducial/tooling footprints fall through to Do-Not-Place.
export_jlcpcb_fab "$panel" "$out" "panel" "$parts"

ok "panelize: panel exported to ${out}/"
