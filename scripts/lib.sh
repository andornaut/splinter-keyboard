#!/usr/bin/env bash
# Shared helpers for the per-stage pipeline wrappers in scripts/. Source near the
# top of a wrapper, after `set -euo pipefail` and `shopt -s nullglob`:
#   source "$(dirname "${BASH_SOURCE[0]}")/lib.sh"
# Each wrapper still owns its source dir and per-file command (mapping 1:1 to an
# npm script); this only factors out the require-inputs-or-fail pattern they share.

# Populate the caller's `files` array with the non-underscore .kicad_pcb files in
# $1, or print $2 (default message) to stderr and exit 1. Named "require" because
# every wrapper is a deliberate transform step: a missing input is a mistake to
# surface, not a benign skip. Requires `shopt -s nullglob` in the caller.
require_pcbs() {
  local dir="$1"
  local msg="${2:-No PCBs found in ${dir}/.}"
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

# KiCad's pcbnew module prints a harmless PROPERTY_ENUM wxASSERT to stderr every
# time it is imported (directly, or via kb_ergogen_helper). Drop just those lines
# from a command's stderr, preserving all other output and its exit code. The
# match is the full distinctive assert tail (not the bare "No enum choices
# defined") so a real error happening to contain that phrase is not swallowed.
mute_pcbnew_noise() { "$@" 2> >(grep -vF 'PROPERTY_ENUM(): No enum choices defined' >&2); }

# Standard JLCPCB 2-layer set (paste included for the assembly stencil).
JLCPCB_LAYERS="F.Cu,B.Cu,F.Paste,B.Paste,F.Silkscreen,B.Silkscreen,F.Mask,B.Mask,Edge.Cuts"

# Export one board's JLCPCB fab set: gerbers + drill (zipped to <name>-gerber.zip)
# always, plus pos + assembly BOM/CPL when a parts file exists. Shared by
# fab-jlcpcb.sh (per routed half) and panelize.sh (the combined panel) so the
# kicad-cli flags and the BOM/CPL join stay in one place.
# Args: <board.kicad_pcb> <out_dir> <name> <parts_json> <scripts_dir>
export_jlcpcb_fab() {
  local board="$1" out="$2" name="$3" parts="$4" scripts_dir="$5"
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
    python3 "${scripts_dir}/gen-jlcpcb-bom-cpl.py" \
      --pos "$pos" --parts "$parts" \
      --bom "${out}/${name}-BOM.csv" --cpl "${out}/${name}-CPL.csv"
  else
    echo "  no ${parts} -- gerbers only (no assembly BOM/CPL)"
  fi
}
