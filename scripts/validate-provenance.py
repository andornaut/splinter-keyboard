#!/usr/bin/env python3
"""Assert kicad/unrouted and kicad/routed were built from the current config.yaml.

Reads the provenance stamp (title_block comment 1) from every working board and
compares its config= hash against a fresh hash of the active version's config.yaml.
A mismatch means the board was generated from a different config than is on disk
now (edit config, forgot to rebuild + re-route); a missing stamp means the board
predates stamping or was never built through build.sh. Either way the routed
master is not safe to fab, so this exits nonzero. fab-jlcpcb runs it as a gate.

Active version comes from npm_package_config_VERSION, so run via npm:
  npm run validate-provenance

By default both stages are checked; pass stage names to narrow it (the fab gate
passes `routed`, since fab-jlcpcb only consumes routed/ -- validating unrouted/
there would block a legitimate fab of a current routed master on unrelated
unrouted/ drift):
  validate-provenance.py routed
"""
import argparse
import glob
import os
import re
import sys

from provenance import config_hash, parse_config_field

STAGES = ("unrouted", "routed")
COMMENT1_RE = re.compile(r'\(comment\s+1\s+"([^"]*)"\)')


def stamped_config(pcb_path):
    """Return the config= hash stored in a board's stamp, or None if unstamped."""
    with open(pcb_path, encoding="utf-8") as f:
        text = f.read()
    m = COMMENT1_RE.search(text)
    return parse_config_field(m.group(1)) if m else None


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    # default=None (not list(STAGES)): argparse runs `choices` over the default
    # too when nargs="*", and would reject the list as a single invalid choice.
    ap.add_argument("stages", nargs="*", choices=STAGES, default=None,
                    help="stage(s) to validate (default: both)")
    stages = ap.parse_args().stages or list(STAGES)

    version = os.environ.get("npm_package_config_VERSION")
    if not version:
        sys.exit("npm_package_config_VERSION not set -- run via npm (npm run validate-provenance)")

    config = f"{version}/ergogen/config.yaml"
    if not os.path.isfile(config):
        sys.exit(f"{config}: not found")
    expected = config_hash(config)

    boards = []
    for stage in stages:
        boards += sorted(glob.glob(f"{version}/kicad/{stage}/[!_]*.kicad_pcb"))
    if not boards:
        sys.exit(f"No boards under {version}/kicad/{{{','.join(stages)}}}/ to validate.")

    failures = 0
    for pcb in boards:
        stored = stamped_config(pcb)
        if stored == expected:
            print(f"  ok       {pcb} (config={stored})")
        elif stored is None:
            print(f"  MISSING  {pcb}: no provenance stamp -- rebuild to stamp")
            failures += 1
        else:
            print(f"  MISMATCH {pcb}: stamped config={stored}, current config={expected}")
            failures += 1

    if failures:
        print(f"validate-provenance: {failures}/{len(boards)} board(s) stale or unstamped "
              f"for {version} (config={expected}). Rebuild, re-copy, and re-route to clear.",
              file=sys.stderr)
        sys.exit(1)
    print(f"OK: validate-provenance: {len(boards)} board(s) match {config} (config={expected})")


if __name__ == "__main__":
    main()
