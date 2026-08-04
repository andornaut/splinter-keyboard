#!/usr/bin/env bash
# Shared helpers for the per-stage pipeline wrappers in scripts/. Source near the
# top of a wrapper, after `set -euo pipefail` and `shopt -s nullglob`:
#   source "$(dirname "${BASH_SOURCE[0]}")/lib.sh"
# Each wrapper still owns its source dir and per-file command (mapping 1:1 to an
# npm script); this only factors out the require-inputs-or-fail pattern they share.
#
# Output convention, followed by every step in this directory, wrapper and python
# helper alike. A pipeline run is one log, so the steps have to read as one voice:
#
#   OK: <step>: <summary>       final success line, one per step, stdout (see ok)
#   ..<tag> <subject>: <detail> per-item line, indented 2. The subject is a
#                               repo-relative board path, or the thing acted on
#                               (a net, a stage) where the line is not about a board
#   ....<detail>                continuation of the line above, indented 4
#
# Tags are lowercase for the routine (ok, skip, wrote) and UPPERCASE for anything
# asking to be read (ADDED, CLEANED, TIDIED, LEFT ALONE, WARN, FAIL, ERROR). Every
# failure and warning goes to stderr, everything else to stdout, and a script that
# mixes the two flushes stdout before writing the summary so a pipe keeps the order.
# A board is a "board", never a "PCB"; paths carry no leading ./; no line ends in a
# full stop.

# Populate the caller's `files` array with the non-underscore .kicad_pcb files in
# $1, or print $2 (default message) to stderr and exit 1. Named "require" because
# every wrapper is a deliberate transform step: a missing input is a mistake to
# surface, not a benign skip. Requires `shopt -s nullglob` in the caller.
require_pcbs() {
  local dir="$1"
  local msg="${2:-No boards found in ${dir}/}"
  files=("$dir"/[!_]*.kicad_pcb)
  if [ ${#files[@]} -eq 0 ]; then
    echo "$msg" >&2
    exit 1
  fi
}

# Print a uniform success line. Call as a wrapper's final statement: under
# `set -e` it is reached only when every prior step succeeded, so it doubles as
# the script's success signal. Goes to stdout (errors already go to stderr).
ok() { echo "OK: $*"; }

# Fail early with a clear message if any named runtime dependency is missing from
# PATH. Shared by the wrappers that shell out to external tools (fab,
# panelize). Call as `require_cmds kicad-cli zip python3`.
require_cmds() {
  local cmd
  for cmd in "$@"; do
    command -v "$cmd" >/dev/null || { echo "Missing required command: $cmd" >&2; exit 1; }
  done
}

# The two harmless wx lines KiCad's pcbnew module prints to stderr on import: the
# PROPERTY_ENUM wxASSERT, and the image-handler debug line. Every tool that loads
# pcbnew emits them (kicad-cli, KiKit, kb_ergogen_helper, our own scripts), so one
# filter covers them all; a per-tool filter only means one caller keeps the noise.
# Matched as fixed strings (not the bare "No enum choices defined") so a real error
# happening to contain the phrase is not swallowed.
PCBNEW_NOISE=(
  'PROPERTY_ENUM(): No enum choices defined'
  'Debug: Adding duplicate image handler'
)

# Drop just that noise from a command's stderr, preserving all other output and its
# exit code (the grep runs in a process substitution, so the wrapped command's
# status is what propagates). Prefix any env-var assignment with `env` so it stays
# a command word (e.g. `mute_pcbnew_noise env PYTHONNOUSERSITE=1 "$py" ...`).
mute_pcbnew_noise() {
  local patterns=() line
  for line in "${PCBNEW_NOISE[@]}"; do patterns+=(-e "$line"); done
  "$@" 2> >(grep -vF "${patterns[@]}" >&2)
}

# Provenance gate shared by fab.sh and panelize.sh: refuse to proceed if any
# routed board drifted from the current config.yaml (or is unstamped). Scoped to
# routed/ (the fab source) so unrouted/ drift never blocks a legitimate fab/panel
# of a current routed master. Under `set -e` a nonzero exit aborts the caller.
provenance_gate_routed() { python3 ./scripts/validate-provenance.py routed; }

# Apply the custom KiCad project settings (VCC net class + DRC floors) to the
# [!_]*.kicad_pro files under $1. Called by each step that writes a board tier so
# that tier owns its project file: ergogen -> dist/, copy:dist-to-unrouted ->
# unrouted/, copy:unrouted-to-routed -> routed/. apply-project-settings.py is
# idempotent and skips non-matching paths, so a no-op call (or empty glob under
# nullglob) is safe. No mute_pcbnew_noise: it edits .kicad_pro JSON and never
# imports pcbnew, so it emits no PROPERTY_ENUM noise.
apply_project_settings() { python3 ./scripts/apply-project-settings.py "$1"/[!_]*.kicad_pro; }

# Resolve the KiKit interpreter: the KIKIT_PYTHON override, else the dedicated
# venv panelize.py needs (KiCad 10 KiKit is git-master only, so it lives in its
# own venv). Echoes the path; callers test it with kikit_importable. Shared by
# pipeline.sh (probe-and-skip) and panelize.sh (hard-fail) so both resolve the
# same interpreter.
kikit_python() { echo "${KIKIT_PYTHON:-/opt/kikit/bin/python}"; }

# True if $1 is an executable interpreter that can import kikit.panelize.
# PYTHONNOUSERSITE=1 so a stale ~/.local pcbnewTransition cannot shadow the venv.
# The one place the import probe lives, so pipeline.sh and panelize.sh agree.
kikit_importable() {
  [ -x "$1" ] && PYTHONNOUSERSITE=1 "$1" -c 'import kikit.panelize' 2>/dev/null
}

# Standard JLCPCB 2-layer set (paste included for the assembly stencil).
JLCPCB_LAYERS="F.Cu,B.Cu,F.Paste,B.Paste,F.Silkscreen,B.Silkscreen,F.Mask,B.Mask,Edge.Cuts"

# Export one board's JLCPCB fab set: gerbers + drill (zipped to <name>-gerber.zip)
# always, plus pos + assembly BOM/CPL when a parts file exists. Shared by
# fab.sh (per routed half) and panelize.sh (the combined panel) so the
# kicad-cli flags and the BOM/CPL join stay in one place.
# Args: <board.kicad_pcb> <out_dir> <name> <parts_json>
export_jlcpcb_fab() {
  local board="$1" out="$2" name="$3" parts="$4"
  local gerber_dir="${out}/gerber"

  # Rebuild gerbers from scratch (clear the stale set and any old zip, so the
  # fresh zip is not appended to a previous one).
  rm -rf "$gerber_dir"
  mkdir -p "$gerber_dir"
  rm -f "${out}/${name}-gerber.zip"

  kicad-cli pcb export gerbers --no-protel-ext --layers "$JLCPCB_LAYERS" \
    --output "${gerber_dir}/" "$board" >/dev/null
  kicad-cli pcb export drill --format excellon --drill-origin absolute \
    --output "${gerber_dir}/" "$board" >/dev/null
  ( cd "$gerber_dir" && zip -qr "../${name}-gerber.zip" . )

  # Assembly files are optional: emit them only where a parts file exists.
  if [ -f "$parts" ]; then
    local pos="${out}/${name}-pos.csv"
    kicad-cli pcb export pos --format csv --units mm --output "$pos" "$board" >/dev/null
    python3 ./scripts/gen-jlcpcb-bom-cpl.py \
      --pos "$pos" --parts "$parts" \
      --bom "${out}/${name}-BOM.csv" --cpl "${out}/${name}-CPL.csv"
  else
    echo "  skip ${parts}: not found, exporting gerbers only (no assembly BOM/CPL)"
  fi
}
