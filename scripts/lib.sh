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
