#!/usr/bin/env python3
"""Join a KiCad position file against jlcpcb-parts.json to emit JLCPCB BOM + CPL.

LCSC part assignments live in a standalone JSON keyed by footprint name (the
position file's "Package" column) rather than in the .kicad_pcb, so they survive
Ergogen regeneration of the boards. This script reads the position file produced
by `kicad-cli pcb export pos --format csv`, looks each footprint up in the JSON,
and writes the two files JLCPCB's assembly service expects:

  BOM.csv  Comment, Designator, Footprint, LCSC Part #   (one line per LCSC part)
  CPL.csv  Designator, Mid X, Mid Y, Rotation, Layer     (one line per placement)

Placement rules (see jlcpcb-parts.json `_comment`):
  - footprint absent from the JSON  -> Do-Not-Place (skipped silently)
  - footprint present, empty `lcsc` -> skipped with a warning (fill it in)
  - footprint present, `lcsc` set    -> placed; `rotation` is added to KiCad's
                                        angle to correct pick-and-place orientation

Usage:
  gen-jlcpcb-bom-cpl.py --pos POS.csv --parts parts.json --bom BOM.csv --cpl CPL.csv
"""
import argparse
import csv
import json
import re
import sys
from collections import defaultdict


def ref_key(ref):
    """Natural sort key for a reference designator (D2 before D10)."""
    m = re.match(r"([A-Za-z]+)(\d+)", ref)
    return (m.group(1), int(m.group(2))) if m else (ref, 0)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--pos", required=True, help="kicad-cli CSV position file")
    ap.add_argument("--parts", required=True, help="jlcpcb-parts.json")
    ap.add_argument("--bom", required=True, help="output BOM CSV path")
    ap.add_argument("--cpl", required=True, help="output CPL CSV path")
    args = ap.parse_args()

    with open(args.parts) as f:
        parts = json.load(f).get("parts", {})
    with open(args.pos, newline="") as f:
        rows = list(csv.DictReader(f))

    placed = []                          # (pos_row, spec) for footprints we place
    dnp = []                             # refs with no JSON entry
    no_lcsc = defaultdict(list)          # package -> refs listed but unassigned

    for r in rows:
        spec = parts.get(r["Package"])
        if spec is None:
            dnp.append(r["Ref"])
        elif not spec.get("lcsc"):
            no_lcsc[r["Package"]].append(r["Ref"])
        else:
            placed.append((r, spec))

    # CPL: one row per placed footprint, rotation corrected.
    with open(args.cpl, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["Designator", "Mid X", "Mid Y", "Rotation", "Layer"])
        for r, spec in placed:
            rot = (float(r["Rot"]) + float(spec.get("rotation", 0))) % 360
            layer = "Top" if r["Side"] == "top" else "Bottom"
            w.writerow([r["Ref"], r["PosX"], r["PosY"], f"{rot:g}", layer])

    # BOM: group placed footprints by LCSC part number.
    refs_by_lcsc = defaultdict(list)
    spec_by_lcsc = {}
    for r, spec in placed:
        refs_by_lcsc[spec["lcsc"]].append(r["Ref"])
        spec_by_lcsc[spec["lcsc"]] = spec
    with open(args.bom, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["Comment", "Designator", "Footprint", "LCSC Part #"])
        for lcsc, refs in sorted(refs_by_lcsc.items()):
            spec = spec_by_lcsc[lcsc]
            designators = ",".join(sorted(refs, key=ref_key))
            w.writerow([spec.get("comment", ""), designators,
                        spec.get("package", ""), lcsc])

    print(f"  placed {len(placed)} parts in {len(refs_by_lcsc)} BOM lines; "
          f"{len(dnp)} do-not-place")
    for pkg, refs in sorted(no_lcsc.items()):
        print(f"  WARNING: no lcsc for '{pkg}' ({len(refs)} part(s)) -- skipped; "
              f"set it in {args.parts}", file=sys.stderr)


if __name__ == "__main__":
    main()
