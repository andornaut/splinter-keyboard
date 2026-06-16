#!/usr/bin/env bash
# Full hardware pipeline for the active version: the one-command path from the
# ergogen config to fab-ready JLCPCB artifacts. Runs each standalone step in the
# required order, prints a per-step banner, and closes with a summary of what ran
# plus the output files produced. Run via: npm run pipeline
#
# Order (each step is also its own npm script):
#   1 ergogen               regenerate boards from config.yaml
#   2 copy:dist-to-unrouted dist/ -> kicad/unrouted/ (backs up first)
#   3 copy:traces-to-unrouted routed/ traces+teardrops -> unrouted/
#   4 copy:unrouted-to-routed unrouted/ -> routed/ (adds GND pour)
#   5 validate:provenance   unrouted/ + routed/ match current config
#   6 fab                   per-half gerbers/drill (+ assembly BOM/CPL)
#   7 validate:fab          audit the fab outputs (GND plane, gerber set, BOM/CPL)
#   8 panelize              combined left+right PCBA panel (optional)
#
# panelize needs the KiKit venv (see panelize.sh). When it is absent the pipeline
# skips that step with a note instead of failing -- the per-half fab output from
# steps 6-7 is complete on its own. Every other step is a hard gate.
set -Eeuo pipefail
shopt -s nullglob
source "$(dirname "${BASH_SOURCE[0]}")/lib.sh"

VERSION="${npm_package_config_VERSION:?set via npm (npm run pipeline)}"
total_steps=8

# Bold the banners only when stdout is a terminal (plain text when piped/logged).
if [ -t 1 ]; then B=$'\033[1m'; R=$'\033[0m'; else B=''; R=''; fi

# Collected per-step result lines for the closing summary: "tag|name|detail".
summary=()
current_step=""

# Print which step was in flight when the pipeline aborts (set -E propagates the
# ERR trap into the called scripts' failure return). The step's own stderr
# already explains the cause; this just pins the blame to a named step.
on_err() { printf '\n%sPIPELINE FAILED at: %s%s\n' "$B" "$current_step" "$R" >&2; }
trap on_err ERR

# Run a mandatory step: $1 index, $2 label, rest = command. A nonzero exit
# propagates under set -e (aborting the pipeline via the ERR trap above).
run_step() {
  local n="$1"; current_step="$2"; shift 2
  printf '\n%s==> [%d/%d] %s%s\n' "$B" "$n" "$total_steps" "$current_step" "$R"
  local t0=$SECONDS
  "$@"
  summary+=("ok|${current_step}|$(( SECONDS - t0 ))s")
}

SECONDS=0
run_step 1 "ergogen"                 ./scripts/ergogen.sh
run_step 2 "copy:dist-to-unrouted"   ./scripts/copy-dist-to-unrouted.sh
run_step 3 "copy:traces-to-unrouted" ./scripts/copy-traces-to-unrouted.sh
run_step 4 "copy:unrouted-to-routed" ./scripts/copy-unrouted-to-routed.sh
run_step 5 "validate:provenance"     python3 ./scripts/validate-provenance.py
run_step 6 "fab"                     ./scripts/fab.sh
run_step 7 "validate:fab"            python3 ./scripts/validate-fab.py

# Step 8 (panelize) is optional: run it only when the KiKit venv is present and
# importable (the same probe panelize.sh does), otherwise skip with a note so a
# machine without KiKit still gets a complete per-half fab from steps 6-7.
current_step="panelize"
printf '\n%s==> [%d/%d] %s%s\n' "$B" "$total_steps" "$total_steps" "panelize (optional)" "$R"
kikit_py="$(kikit_python)"
if kikit_importable "$kikit_py"; then
  t0=$SECONDS
  ./scripts/panelize.sh
  summary+=("ok|panelize|$(( SECONDS - t0 ))s")
else
  echo "  KiKit not available at ${kikit_py}; skipping the panel."
  echo "  Per-half fab from step 6 is complete. Install KiKit (ansible-ctrl hobbies"
  echo "  role, kicad tag) or set KIKIT_PYTHON to enable panelization."
  summary+=("skip|panelize|KiKit unavailable")
fi

# Closing summary: a divider off the step logs, then step ledger and artifacts.
printf '\n%s\n' '------------------------------------------------------------'
printf '%s== pipeline complete (%s) in %ds ==%s\n' "$B" "$VERSION" "$SECONDS" "$R"
echo
echo "Steps:"
for s in "${summary[@]}"; do
  IFS='|' read -r tag name detail <<<"$s"
  printf '  %-6s %-32s %s\n' "[${tag}]" "$name" "$detail"
done

base="dist/${VERSION}/kicad/jlcpcb"
if [ -d "$base" ]; then
  echo
  echo "Fab outputs (${base}/):"
  for d in "$base"/*/; do
    [ -d "$d" ] || continue
    echo "  ${d#"${base}/"}"
    for f in "$d"*; do
      [ -f "$f" ] || continue   # skip the gerber/ subdir; the zipped set is the artifact
      printf '    %-22s %s\n' "$(basename "$f")" "$(du -h "$f" | cut -f1)"
    done
  done
fi
panel="dist/${VERSION}/kicad/panelize/panel.kicad_pcb"
[ -f "$panel" ] && { echo; echo "Panel board:"; printf '  %s\n' "$panel"; }

# Provenance stamp of what was just fabbed: the title-block comment 1 of a routed
# board (the fab source). All halves share one stamp, so any routed board serves.
# Read by regex, no pcbnew load -- same field validate:provenance compares.
stamp_board=("${VERSION}/kicad/routed"/[!_]*.kicad_pcb)
if [ ${#stamp_board[@]} -gt 0 ]; then
  stamp=$(grep -oE '\(comment 1 "[^"]*"\)' "${stamp_board[0]}" | head -1 \
    | sed -E 's/^\(comment 1 "(.*)"\)$/\1/')
  [ -n "$stamp" ] && { echo; echo "Provenance:"; printf '  %s\n' "$stamp"; }
fi

echo
ok "pipeline: ${VERSION} fab-ready outputs in dist/${VERSION}/kicad/"
