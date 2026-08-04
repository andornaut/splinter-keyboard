#!/usr/bin/env python3
"""Assert kicad/unrouted and kicad/routed were built from the current config.yaml.

Reads the provenance stamp (title_block comment 1) from every working board and
runs two checks over it. Either failing exits nonzero, and fab runs this as a gate.

CURRENT. Each board's config= hash must equal a fresh hash of the active version's
config.yaml. A mismatch means the board was generated from a different config than
is on disk now (edit config, forgot to rebuild + re-route); a missing stamp means
the board predates stamping or was never built through ergogen.sh.

ONE RUN. Every board within a stage must carry the same stamp, not merely a
matching hash. stamp-provenance.py builds one stamp per run and writes it to every
board it is given, so equality here means the boards were built together. A half
restored or rebuilt on its own passes the hash check, since identical config bytes
hash identically across builds, and shows up only here. Compared within a stage and
never across one: unrouted/ legitimately carries a newer stamp than routed/ between
an ergogen run and the save back to the masters.

Active version comes from npm_package_config_VERSION, so run via npm:
  npm run validate:provenance

By default both stages are checked; pass stage names to narrow it (the fab gate
passes `routed`, since fab only consumes routed/ -- validating unrouted/
there would block a legitimate fab of a current routed master on unrelated
unrouted/ drift):
  validate-provenance.py routed
"""
import argparse
import collections
import glob
import os
import re
import sys

from provenance import config_hash, parse_config_field

STAGES = ("unrouted", "routed")
COMMENT1_RE = re.compile(r'\(comment\s+1\s+"([^"]*)"\)')


def stamped_text(pcb_path):
    """Return a board's whole stamp string, or "" if it carries none. Read from the
    file text rather than through pcbnew: this runs as a gate on every fab, and
    loading a board costs seconds where a regex costs milliseconds."""
    with open(pcb_path, encoding="utf-8") as f:
        text = f.read()
    m = COMMENT1_RE.search(text)
    return m.group(1) if m else ""


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    # default=None (not list(STAGES)): argparse runs `choices` over the default
    # too when nargs="*", and would reject the list as a single invalid choice.
    ap.add_argument("stages", nargs="*", choices=STAGES, default=None,
                    help="stage(s) to validate (default: both)")
    stages = ap.parse_args().stages or list(STAGES)

    version = os.environ.get("npm_package_config_VERSION")
    if not version:
        sys.exit("npm_package_config_VERSION not set -- run via npm (npm run validate:provenance)")

    config = f"{version}/ergogen/config.yaml"
    if not os.path.isfile(config):
        sys.exit(f"{config}: not found")
    expected = config_hash(config)

    staged = {stage: sorted(glob.glob(f"{version}/kicad/{stage}/[!_]*.kicad_pcb"))
              for stage in stages}
    boards = [pcb for stage in stages for pcb in staged[stage]]
    if not boards:
        sys.exit(f"No boards under {version}/kicad/{{{','.join(stages)}}}/ to validate.")

    stamps = {pcb: stamped_text(pcb) for pcb in boards}
    failures = 0
    for pcb in boards:
        stored = parse_config_field(stamps[pcb])
        if stored == expected:
            print(f"  ok       {pcb} (config={stored})")
        elif stored is None:
            print(f"  MISSING  {pcb}: no provenance stamp -- rebuild to stamp")
            failures += 1
        else:
            print(f"  MISMATCH {pcb}: stamped config={stored}, current config={expected}")
            failures += 1

    if failures:
        sys.stdout.flush()  # keep the per-board lines above this summary under a pipe
        print(f"validate:provenance: {failures}/{len(boards)} board(s) stale or unstamped "
              f"for {version} (config={expected}). Rebuild, re-copy, and re-route to clear.",
              file=sys.stderr)
        sys.exit(1)

    # Every board above hashes to the current config, so anything left here is a
    # stage whose boards were built in different runs (see ONE RUN in the docstring).
    split = [stage for stage in stages if len(set(map(stamps.get, staged[stage]))) > 1]
    if split:
        # The per-board lines above go to stdout, which is block-buffered under a
        # pipe; flush so the report below lands after them and not among them.
        sys.stdout.flush()
    for stage in split:
        by_stamp = collections.defaultdict(list)
        for pcb in staged[stage]:
            by_stamp[stamps[pcb]].append(os.path.basename(pcb))
        print(f"  SPLIT    {version}/kicad/{stage}/: boards were not built in one run",
              file=sys.stderr)
        for text, names in sorted(by_stamp.items()):
            print(f"             {', '.join(names)}: {text}", file=sys.stderr)
    if split:
        print(f"validate:provenance: {len(split)} stage(s) mix boards from different builds. "
              "The config hash cannot see this, since identical config bytes hash the same "
              "across builds. Re-run the pipeline so every board is built in one run.",
              file=sys.stderr)
        sys.exit(1)

    print(f"OK: validate:provenance: {len(boards)} board(s) match {config} (config={expected})")


if __name__ == "__main__":
    main()
