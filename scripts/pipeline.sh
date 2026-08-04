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
#   6 validate:symmetry     the halves mirror: outline, parts, pads, zones, silk
#   7 validate:firmware     halves agree on MCU pins; boards match QMK matrix_pins
#   8 fab                   per-half gerbers/drill (+ assembly BOM/CPL)
#   9 validate:fab          audit the fab outputs (GND plane, gerber set, BOM/CPL)
#  10 panelize              combined left+right PCBA panel (optional)
#
# validate:firmware runs before fab so a board whose matrix nets disagree with the
# firmware aborts before any gerber is written; that error passes DRC and is
# invisible until an MCU is plugged in. It lives here rather than inside fab.sh
# because it needs an external firmware source, and a fetch failure should not
# block a legitimate gerber export. All of its checks are required: a board
# is not fab-ready until firmware is proven to match it, so an unset or unreachable
# firmware source stops the pipeline rather than silently dropping a check. Set the
# source in package.json config.FIRMWARE (a URL or path).
#
# panelize needs the KiKit venv (see panelize.sh). When it is absent the pipeline
# skips that step with a note instead of failing -- the per-half fab output from
# steps 8-9 is complete on its own. Every other step is a hard gate.
#
# A step reports what it changed and what wants reading; the lines that only
# confirm nothing needed doing are held back, since each step's OK: summary
# already carries the count they would have added up to. `npm run pipeline -- -v`
# shows them all, plus Ergogen's own narration and the full artifact listing. It
# is one env var (PIPELINE_VERBOSE) because a run is a dozen processes deep and
# every one of them has to agree on how loud it is; see scripts/pipeline_log.py.
set -Eeuo pipefail
shopt -s nullglob
source "$(dirname "${BASH_SOURCE[0]}")/lib.sh"

# Every argument is checked, not just the first: this run rewrites the masters and
# writes gerbers, so an unrecognised argument has to stop it rather than be dropped
# on the floor behind a flag that did parse.
while [ $# -gt 0 ]; do
  case "$1" in
    -v|--verbose) export PIPELINE_VERBOSE=1 ;;
    *) echo "usage: npm run pipeline [-- -v]" >&2; exit 2 ;;
  esac
  shift
done

VERSION="${npm_package_config_VERSION:?set via npm (npm run pipeline)}"
total_steps=10

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
run_step 6 "validate:symmetry"       python3 ./scripts/validate-symmetry.py
run_step 7 "validate:firmware"       python3 ./scripts/validate-firmware.py
run_step 8 "fab"                     ./scripts/fab.sh
run_step 9 "validate:fab"            python3 ./scripts/validate-fab.py

# Step 10 (panelize) is optional: run it only when the KiKit venv is present and
# importable (the same probe panelize.sh does), otherwise skip with a note so a
# machine without KiKit still gets a complete per-half fab from steps 8-9.
current_step="panelize"
printf '\n%s==> [%d/%d] %s%s\n' "$B" "$total_steps" "$total_steps" "panelize (optional)" "$R"
kikit_py="$(kikit_python)"
if kikit_importable "$kikit_py"; then
  t0=$SECONDS
  ./scripts/panelize.sh
  summary+=("ok|panelize|$(( SECONDS - t0 ))s")
else
  echo "  skip panelize: KiKit not importable at ${kikit_py}"
  echo "    The per-half fab from steps 8-9 is complete on its own. Install KiKit"
  echo "    (ansible-ctrl hobbies role, kicad tag) or set KIKIT_PYTHON to enable it"
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
    # A count and a size per output directory; the file-by-file listing is what
    # PIPELINE_VERBOSE is for. The names are derivable from the directory name.
    files=("$d"*)                # the gerber/ subdir is skipped: the zip is the artifact
    n=0
    for f in "${files[@]}"; do [ -f "$f" ] && n=$((n + 1)); done
    printf '  %-8s %d files, %s\n' "${d#"${base}/"}" "$n" \
      "$(du -sh --exclude=gerber "$d" | cut -f1)"
    for f in "${files[@]}"; do
      [ -f "$f" ] || continue
      note "$(printf '    %-22s %s' "$(basename "$f")" "$(du -h "$f" | cut -f1)")"
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
