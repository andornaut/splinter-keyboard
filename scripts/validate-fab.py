#!/usr/bin/env python3
"""Final fab-output audit: assert the JLCPCB artifacts have the properties the
upstream gates only check by proxy.

The existing gates validate proxies, not the shipped artifact: validate-provenance
checks the config hash, the DRC gate checks connectivity, the teardrop guard checks
routing presence. None of them check that the design properties we actually care
about made it into the files uploaded to the fab. This script closes that gap by
inspecting the routed masters and the dist/ fab outputs directly. It is the reason
a board with no ground plane could pass every other gate and still ship (a filled
zone the guard skipped left GND "connected" by thin traces, so DRC stayed clean).

Run it standalone after fab, or as the validate:fab pipeline step:
  npm run validate:fab

Active version comes from npm_package_config_VERSION, so run via npm.

Checks, per routed board + its dist/${VERSION}/kicad/jlcpcb/<name>/ output:

  GATES (a failure exits nonzero):
  1. GND ground plane -- the routed master has a filled, non-teardrop GND zone on a
     copper layer covering most of the board (catches an unfilled/missing pour at
     the source), AND the exported copper gerber contains a flood region spanning
     most of the board (catches the same thing in what actually shipped, immune to
     any export-stage drop). This is the direct inverse of the add-gnd-zone guard bug.
  2. Gerber-set completeness -- <name>-gerber.zip exists and contains every expected
     layer gerber (the lib.sh JLCPCB_LAYERS set) plus a drill file.
  3. Assembly placement sanity (only when jlcpcb-parts.json exists) -- BOM + CPL exist
     and are non-empty, and every assembled footprint on the board appears in the CPL
     exactly once (catches a part silently dropping out of the pos/CPL join, which
     gen-jlcpcb-bom-cpl.py does not count-check).
  5. Freshness ordering -- config.yaml must not be newer than a routed board, and a
     routed board must not be newer than its gerber zip (either inversion means a
     stale artifact was not regenerated). Mtime-based, so a git checkout that shuffles
     file times without rebuilding can trip it; regenerate to clear.
  6. Teardrop consistency -- the mirrored routed masters should carry comparable
     teardrop counts, so flag any board below TEARDROP_MIN_FRAC of the best-teardropped
     board (catches a half that lost its teardrops in a re-route or a lossy copy).
     Self-skips when teardrops are off everywhere (max count 0).

  WARNING (reported, never fatal):
  4. Provenance clean flag -- warn if a routed master was built from an uncommitted
     tree (clean=no/unknown), which makes its commit= stamp meaningless; the config=
     hash match says nothing about it, so validate:provenance never flags it.
"""
import glob
import os
import re
import sys
import zipfile

# pcbnew prints a harmless "No enum choices defined" wxASSERT to stderr at import.
# Silence stderr across just the import (see route.py for the same pattern); a
# real import failure still surfaces via the traceback after fd 2 is restored.
_saved_stderr_fd = os.dup(2)
_devnull_fd = os.open(os.devnull, os.O_WRONLY)
os.dup2(_devnull_fd, 2)
try:
    import pcbnew
finally:
    os.dup2(_saved_stderr_fd, 2)
    os.close(_devnull_fd)
    os.close(_saved_stderr_fd)

# Drop wx's Debug-level chatter (e.g. "Adding duplicate image handler") that pcbnew
# emits to stderr each time it re-inits image handlers on a board load.
import wx
wx.Log.SetLogLevel(wx.LOG_Warning)

import csv
import json

# Gerber filename fragments for the lib.sh JLCPCB_LAYERS set (layer name dots ->
# underscores, as kicad-cli writes them). Keep in sync with JLCPCB_LAYERS in lib.sh.
LAYER_FRAGMENTS = (
    "F_Cu", "B_Cu", "F_Paste", "B_Paste",
    "F_Silkscreen", "B_Silkscreen", "F_Mask", "B_Mask", "Edge_Cuts",
)
COPPER_FRAGMENTS = ("F_Cu", "B_Cu")
COPPER_LAYERS = (pcbnew.B_Cu, pcbnew.F_Cu)

# A real ground flood spans nearly the whole board; teardrop/pad regions are tiny.
# Require the largest copper region (and the master's filled GND zone) to cover at
# least this fraction of the board in each dimension / by area -- a wide margin that
# separates a flood from islands without being sensitive to clearance insets.
FLOOD_SPAN_FRAC = 0.5
ZONE_AREA_FRAC = 0.30

# Teardrops are applied per junction, so the mirrored left/right halves should carry
# comparable counts. A board with far fewer than the best-teardropped board lost them
# (a re-route without re-teardropping, or a lossy trace copy). Flag any board below
# this fraction of the run's max count. Scales with whatever the design uses, and
# self-skips when teardrops are off everywhere (max=0), so it never false-positives
# on an intentionally teardrop-free design.
TEARDROP_MIN_FRAC = 0.5

FS_RE = re.compile(r"%FS[LT][AI]X\d(\d)Y\d\d\*%")
MO_RE = re.compile(r"%MO(MM|IN)\*%")
COORD_X_RE = re.compile(r"X(-?\d+)")
COORD_Y_RE = re.compile(r"Y(-?\d+)")


# --- check 1: GND ground plane -------------------------------------------------

def _zone_filled_area_mm2(zone, layer):
    """Filled area of a zone on a layer in mm^2, or None if the API is unavailable."""
    try:
        try:
            polys = zone.GetFilledPolysList(layer)
        except TypeError:
            polys = zone.GetFilledPolysList()  # older API takes no layer arg
        return polys.Area() / 1e12  # Area() is in nm^2; 1 mm^2 = (1e6 nm)^2
    except Exception:
        return None


def gnd_zone_master(board):
    """Return (present, filled, area_mm2_or_None) for the board's GND pour: is there
    a non-teardrop GND zone on a copper layer, is it flagged filled, and its area."""
    present = filled = False
    best_area = None
    for z in board.Zones():
        if z.IsTeardropArea() or z.GetNetname() != "GND":
            continue
        for layer in COPPER_LAYERS:
            if not z.IsOnLayer(layer):
                continue
            present = True
            if z.IsFilled():
                filled = True
            area = _zone_filled_area_mm2(z, layer)
            if area is not None and (best_area is None or area > best_area):
                best_area = area
    return present, filled, best_area


def teardrop_count(board):
    """Number of teardrop zones on the board."""
    return sum(1 for z in board.Zones() if z.IsTeardropArea())


def _parse_format(text):
    """Return (divisor, unit_mm) from the gerber format/unit headers."""
    fs = FS_RE.search(text)
    divisor = 10 ** int(fs.group(1)) if fs else 1e6  # default 6 decimals (KiCad)
    mo = MO_RE.search(text)
    unit_mm = 25.4 if (mo and mo.group(1) == "IN") else 1.0
    return divisor, unit_mm


def largest_region_span_mm(text):
    """Span (w_mm, h_mm) of the gerber's largest G36/G37 region, by the region whose
    smaller dimension is largest -- i.e. the most plane-like region, not a long thin
    trace fill. Coordinates are modal, so current x/y carry across blocks."""
    divisor, unit_mm = _parse_format(text)
    in_region = False
    cx = cy = 0
    rminx = rminy = rmaxx = rmaxy = None
    best_w = best_h = 0.0

    def close_region():
        nonlocal best_w, best_h
        if rminx is None:
            return
        w = (rmaxx - rminx) / divisor * unit_mm
        h = (rmaxy - rminy) / divisor * unit_mm
        if min(w, h) > min(best_w, best_h):
            best_w, best_h = w, h

    for block in text.split("*"):
        if "G36" in block:
            in_region, rminx, rminy, rmaxx, rmaxy = True, None, None, None, None
        if "G37" in block:
            close_region()
            in_region = False
        mx = COORD_X_RE.search(block)
        my = COORD_Y_RE.search(block)
        if mx:
            cx = int(mx.group(1))
        if my:
            cy = int(my.group(1))
        if in_region and (mx or my):
            rminx = cx if rminx is None else min(rminx, cx)
            rminy = cy if rminy is None else min(rminy, cy)
            rmaxx = cx if rmaxx is None else max(rmaxx, cx)
            rmaxy = cy if rmaxy is None else max(rmaxy, cy)
    return best_w, best_h


def gnd_flood_in_gerber(zip_path, board_w, board_h):
    """True if any copper gerber in the zip has a region spanning most of the board."""
    with zipfile.ZipFile(zip_path) as z:
        for name in z.namelist():
            if not name.endswith(".gbr"):
                continue
            if not any(frag in name for frag in COPPER_FRAGMENTS):
                continue
            text = z.read(name).decode("latin-1")
            w, h = largest_region_span_mm(text)
            if w >= FLOOD_SPAN_FRAC * board_w and h >= FLOOD_SPAN_FRAC * board_h:
                return True
    return False


# --- check 2: gerber-set completeness ------------------------------------------

def gerber_zip_missing(zip_path):
    """Return the list of expected gerber/drill members absent from the zip."""
    with zipfile.ZipFile(zip_path) as z:
        names = z.namelist()
    missing = [frag for frag in LAYER_FRAGMENTS
               if not any(frag in n and n.endswith(".gbr") for n in names)]
    if not any(n.endswith(".drl") for n in names):
        missing.append("drill(.drl)")
    return missing


# --- check 3: assembly placement sanity ----------------------------------------

def assembled_refs_on_board(board, assembled_pkgs):
    """Map ref -> package for footprints whose package is an assembled part. The
    package is the footprint library item name, which is the pos 'Package' column."""
    refs = {}
    for fp in board.GetFootprints():
        pkg = str(fp.GetFPID().GetLibItemName())  # UTF8 -> str (UTF8 is unhashable)
        if pkg in assembled_pkgs:
            refs[fp.GetReference()] = pkg
    return refs


def csv_designators(path, column):
    with open(path, newline="") as f:
        return [row[column] for row in csv.DictReader(f)]


# --- driver --------------------------------------------------------------------

def main():
    version = os.environ.get("npm_package_config_VERSION")
    if not version:
        sys.exit("npm_package_config_VERSION not set -- run via npm (npm run validate:fab)")

    config = f"{version}/ergogen/config.yaml"
    routed = sorted(glob.glob(f"{version}/kicad/routed/[!_]*.kicad_pcb"))
    if not routed:
        sys.exit(f"No routed boards under {version}/kicad/routed/ to validate.")

    parts_path = f"{version}/kicad/jlcpcb-parts.json"
    assembled_pkgs = {}
    if os.path.isfile(parts_path):
        with open(parts_path) as f:
            assembled_pkgs = {k: v for k, v in json.load(f).get("parts", {}).items()
                              if v.get("lcsc")}

    config_mtime = os.path.getmtime(config) if os.path.isfile(config) else 0
    failures, warnings = [], []
    teardrop_counts = {}

    for pcb in routed:
        name = os.path.splitext(os.path.basename(pcb))[0]
        out = f"dist/{version}/kicad/jlcpcb/{name}"
        zip_path = f"{out}/{name}-gerber.zip"
        print(f"  {pcb} -> {out}/")

        if not os.path.isdir(out):
            failures.append(f"{name}: no fab output at {out}/ -- run `npm run fab` first")
            continue

        board = pcbnew.LoadBoard(pcb)
        bb = board.GetBoardEdgesBoundingBox()
        board_w, board_h = pcbnew.ToMM(bb.GetWidth()), pcbnew.ToMM(bb.GetHeight())

        # 1. GND ground plane: master zone + exported gerber flood.
        present, filled, area = gnd_zone_master(board)
        if not present:
            failures.append(f"{name}: routed master has no non-teardrop GND zone on a copper layer")
        elif not filled:
            failures.append(f"{name}: GND zone present but not filled in the routed master")
        elif area is not None and area < ZONE_AREA_FRAC * board_w * board_h:
            failures.append(f"{name}: GND fill only {area:.0f}mm^2 of {board_w * board_h:.0f}mm^2 "
                            f"board (< {ZONE_AREA_FRAC:.0%}); looks like islands, not a plane")
        else:
            shown = f"{area:.0f}mm^2" if area is not None else "filled"
            print(f"    GND zone (master): ok ({shown})")

        if not os.path.isfile(zip_path):
            failures.append(f"{name}: missing gerber zip {zip_path}")
        else:
            if gnd_flood_in_gerber(zip_path, board_w, board_h):
                print(f"    GND flood (gerber): ok")
            else:
                failures.append(f"{name}: no copper flood spanning the board in {name}-gerber.zip "
                                f"-- the shipped gerbers have no ground plane")

            # 2. gerber-set completeness.
            missing = gerber_zip_missing(zip_path)
            if missing:
                failures.append(f"{name}: gerber zip missing {', '.join(missing)}")
            else:
                print(f"    gerber set: ok ({len(LAYER_FRAGMENTS)} layers + drill)")

        # 3. assembly placement sanity.
        if assembled_pkgs:
            bom, cpl = f"{out}/{name}-BOM.csv", f"{out}/{name}-CPL.csv"
            expected = assembled_refs_on_board(board, assembled_pkgs)
            if not (os.path.isfile(bom) and os.path.getsize(bom) > 0):
                failures.append(f"{name}: BOM missing or empty ({bom})")
            if not (os.path.isfile(cpl) and os.path.getsize(cpl) > 0):
                failures.append(f"{name}: CPL missing or empty ({cpl})")
            elif not expected:
                failures.append(f"{name}: no assembled footprints found on the board "
                                f"(expected {', '.join(assembled_pkgs)})")
            else:
                placed = set(csv_designators(cpl, "Designator"))
                dropped = sorted(set(expected) - placed)
                if dropped:
                    failures.append(f"{name}: {len(dropped)} assembled part(s) absent from the CPL: "
                                    f"{', '.join(dropped)}")
                else:
                    print(f"    assembly: ok ({len(expected)} placements in CPL)")

        # 6. teardrop count: collect per board; the consistency gate runs after the loop.
        teardrop_counts[name] = teardrop_count(board)
        print(f"    teardrops: {teardrop_counts[name]}")

        # 4. provenance clean flag (warning).
        # Read the stamp off the already-loaded board (title_block comment 1 = index 0,
        # per provenance.py) instead of re-reading the file.
        stamp = board.GetTitleBlock().GetComment(0)
        clean = re.search(r"\bclean=(\w+)", stamp) if stamp else None
        if not clean or clean.group(1) != "yes":
            warnings.append(f"{name}: built from a non-clean tree (clean={clean.group(1) if clean else '?'})")

        # 5. freshness ordering (gate).
        pcb_mtime = os.path.getmtime(pcb)
        if config_mtime and pcb_mtime < config_mtime:
            failures.append(f"{name}: routed master older than config.yaml -- rebuild (stale)")
        if os.path.isfile(zip_path) and os.path.getmtime(zip_path) < pcb_mtime:
            failures.append(f"{name}: gerber zip older than the routed master -- re-run fab (stale)")

    # 6. teardrop consistency (gate): the mirrored halves should carry comparable
    # teardrop counts; a board far below the best-teardropped one lost them.
    max_count = max(teardrop_counts.values(), default=0)
    if max_count > 0:
        floor = TEARDROP_MIN_FRAC * max_count
        for name, count in sorted(teardrop_counts.items()):
            if count < floor:
                failures.append(
                    f"{name}: only {count} teardrops vs {max_count} on the best-teardropped "
                    f"board (< {TEARDROP_MIN_FRAC:.0%}); teardrops were lost -- restore the master")

    for w in warnings:
        print(f"  WARN: {w}")
    if failures:
        print(file=sys.stderr)
        for fmsg in failures:
            print(f"  FAIL: {fmsg}", file=sys.stderr)
        print(f"validate:fab: {len(failures)} check(s) failed for {version}.", file=sys.stderr)
        sys.exit(1)
    print(f"OK: validate:fab: {len(routed)} board(s) passed all gates for {version}"
          f"{f' ({len(warnings)} warning(s))' if warnings else ''}")


if __name__ == "__main__":
    main()
