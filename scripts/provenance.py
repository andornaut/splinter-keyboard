#!/usr/bin/env python3
"""Shared helpers for the PCB provenance stamp.

The stamp is one string written into each generated PCB's title_block comment 1
at build time (see stamp-provenance.py) and checked by validate-provenance.py. Its
purpose is to detect when kicad/unrouted or kicad/routed have drifted from the
current ergogen config.yaml. Exactly one field is compared (config=); the rest is
human provenance and is never compared.

Format:
  splinter v=v4 built=2026-06-15T17:30:00Z config=a1b2c3d4e5f6 commit=bf4e6c2 clean=yes

  built=  ISO-8601 UTC build time (provenance)
  config= sha256(config.yaml bytes)[:12] -- the only compared field (the match key)
  commit= short git HEAD, or "unknown" outside a git tree (provenance)
  clean=  yes when the working tree was fully committed at build time, no when it
          had uncommitted changes, unknown outside a git tree (provenance)

This module is stdlib-only and imported by both the writer and the validator, so
the hashing and parsing stay identical on both sides.
"""
import hashlib
import re
import subprocess
from datetime import datetime, timezone

STAMP_PREFIX = "splinter"
STAMP_COMMENT_INDEX = 0  # title_block "comment 1" is index 0


def write_stamp(board, text):
    """Store a stamp string in the board's title_block comment 1. Operates on an
    already-loaded pcbnew board (so this module stays stdlib-only / pcbnew-free),
    keeping the comment index in one place for every writer."""
    board.GetTitleBlock().SetComment(STAMP_COMMENT_INDEX, text)


def config_hash(config_path):
    """Return sha256 of the config file's bytes, truncated to 12 hex chars."""
    with open(config_path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()[:12]


def _git(*args):
    """Run a git command at the repo root (cwd) and return stripped stdout, or
    None if git is unavailable or the command fails (e.g. not a git tree)."""
    try:
        out = subprocess.run(
            ["git", *args],
            capture_output=True, text=True, check=True,
        )
        return out.stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return None


def build_stamp(config_path, version):
    """Assemble the provenance stamp string for a freshly generated board."""
    commit = _git("rev-parse", "--short", "HEAD")
    status = _git("status", "--porcelain")
    if commit is None or status is None:
        commit, clean = "unknown", "unknown"
    else:
        clean = "yes" if status == "" else "no"
    built = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    return (f"{STAMP_PREFIX} v={version} built={built} "
            f"config={config_hash(config_path)} commit={commit} clean={clean}")


def parse_config_field(comment_text):
    """Return the config= hash from a stamp string, or None if absent."""
    if not comment_text:
        return None
    m = re.search(r"\bconfig=([0-9a-f]+)\b", comment_text)
    return m.group(1) if m else None


def silk_from_stamp(stamp):
    """Return the silkscreen form of a stamp: the full stamp minus the leading
    'splinter v=<ver> ' prefix, leaving 'built=... config=... commit=... clean=...'.
    The dropped prefix already rides the credit label on silk, so it is redundant
    there; the leading 'built=' field is what makes the silk text recognizable
    for idempotent re-stamping."""
    parts = stamp.split(" ", 2)
    return parts[2] if len(parts) == 3 else stamp
