#!/usr/bin/env python3
"""Add a filled GND copper pour to a KiCad PCB, on whichever side is the better
ground layer.

Ergogen emits no copper zones, so the generated boards have no ground plane. A
pour gives the TVS data-line clamp a low-impedance return, a clean reference for
the split serial link, and auto-connects every GND pad so the ground net barely
needs hand routing.

The layer is chosen per board, not hardcoded. The script scores F.Cu and B.Cu
and pours on the lower-cost one (see `choose_gnd_layer`), so it follows whatever
routing strategy a board actually has instead of assuming the back is clear:

  cost(layer) = non-GND track length on the layer
              + UNREACHABLE_GND_PAD_COST_MM * (GND pads not reachable on it)

Lower is better. The first term measures how much the plane would be fragmented
by signal copper (GND tracks merge into the pour, so they do not count); the
second penalizes each GND pad that would need a stitching via to reach the plane.
Neither side is inherently preferred: the pour lands on whichever gives the more
continuous plane with fewer stitching vias. On a tie (e.g. an un-routed board
with no signal copper yet) B.Cu wins, the historical default. The selected layer
and the full per-layer breakdown are printed for every board.

The zone outline is just the board bounding box (inflated slightly); KiCad clips
the actual fill to the Edge.Cuts outline minus the copper-to-edge clearance, so a
rectangle is enough and follows any board shape.

Idempotent: if a GND zone already exists on either candidate layer the board is
left untouched, so re-running (e.g. on every build) is safe.

Usage: add-gnd-zone.py <board.kicad_pcb> [more.kicad_pcb ...]
"""
import sys
from collections import namedtuple

import pcbnew

CLEARANCE = pcbnew.FromMM(0.25)
MIN_THICKNESS = pcbnew.FromMM(0.25)
THERMAL_GAP = pcbnew.FromMM(0.30)
THERMAL_SPOKE = pcbnew.FromMM(0.30)
MARGIN = pcbnew.FromMM(1)  # inflate the outline past the edge; fill clips to Edge.Cuts

# Candidate ground layers, in tie-break preference order (B.Cu wins a tie).
CANDIDATE_LAYERS = (pcbnew.B_Cu, pcbnew.F_Cu)
# Rough cost, in mm of equivalent routing, of the stitching via each GND pad that
# does not reach the pour layer would need. Small: openness dominates the choice.
UNREACHABLE_GND_PAD_COST_MM = 50.0

# One candidate layer's score; `cost` drives the choice (lower wins).
LayerScore = namedtuple("LayerScore", "layer name signal_mm reach cost")


def _try_set(obj, name, *args):
    """Call obj.<name>(*args) if it exists (API varies across KiCad versions)."""
    fn = getattr(obj, name, None)
    if fn is not None:
        fn(*args)


def _signal_track_len_mm(board, layer):
    """Total length of non-GND tracks/arcs on `layer` (GND copper merges into the
    pour, so it does not fragment the plane and is excluded)."""
    total = 0.0
    for t in board.GetTracks():
        if t.GetClass() == "PCB_VIA":
            continue
        if t.GetLayer() != layer:
            continue
        if t.GetNetname() == "GND":
            continue
        total += pcbnew.ToMM(t.GetLength())
    return total


def _gnd_pads(board):
    return [p for fp in board.GetFootprints() for p in fp.Pads()
            if p.GetNetname() == "GND"]


def choose_gnd_layer(board):
    """Score each candidate layer and return (best, rows, total_gnd_pads), where
    best is the winning LayerScore and rows is every candidate's LayerScore."""
    gnd_pads = _gnd_pads(board)
    total_gnd = len(gnd_pads)
    rows = []
    for layer in CANDIDATE_LAYERS:
        signal_mm = _signal_track_len_mm(board, layer)
        reach = sum(1 for p in gnd_pads if p.IsOnLayer(layer))
        cost = signal_mm + UNREACHABLE_GND_PAD_COST_MM * (total_gnd - reach)
        rows.append(LayerScore(layer, board.GetLayerName(layer), signal_mm, reach, cost))
    # CANDIDATE_LAYERS is in tie-break order, and min() is stable, so the first
    # (B.Cu) wins an exact cost tie.
    best = min(rows, key=lambda r: r.cost)
    return best, rows, total_gnd


def _print_analysis(path, best, rows, total_gnd):
    print(f"  GND-layer analysis ({path}):")
    for r in rows:
        mark = "  <- selected" if r.layer == best.layer else ""
        print(f"    {r.name}: signal={r.signal_mm:7.1f}mm  "
              f"GND-pads-reachable={r.reach}/{total_gnd}  cost={r.cost:7.1f}{mark}")
    print(f"  selected GND layer: {best.name}")


def add_gnd_zone(path):
    board = pcbnew.LoadBoard(path)

    gnd = board.FindNet("GND")
    if gnd is None:
        raise SystemExit(f"{path}: no GND net found")

    best, rows, total_gnd = choose_gnd_layer(board)
    _print_analysis(path, best, rows, total_gnd)
    layer, layer_name = best.layer, best.name

    # Guard against pouring twice. Check ALL candidate layers, not just the
    # selected one, so a board that already has a GND pour (on either side) is
    # left untouched and never ends up with a redundant plane on both layers.
    # Exclude teardrops: they are ZONE objects too, and a teardrop on a GND track
    # is a GND zone on its layer. Counting them here made the guard see a "GND
    # pour" that was never flooded and skip the actual fill once teardrop-copying
    # entered the pipeline (copy-traces-routed-to-unrouted carries GND teardrops in).
    existing = [board.GetLayerName(cand) for cand in CANDIDATE_LAYERS
                if any(z.GetNetname() == "GND" and z.IsOnLayer(cand)
                       and not z.IsTeardropArea()
                       for z in board.Zones())]
    if existing:
        msg = f"GND pour already present on {', '.join(existing)}"
        if layer_name not in existing:
            msg += f"; analysis preferred {layer_name}, not re-pouring an already-poured board"
        print(f"  ok ({msg}): {path}")
        return

    bb = board.GetBoardEdgesBoundingBox()
    x0, y0 = bb.GetX() - MARGIN, bb.GetY() - MARGIN
    x1, y1 = bb.GetRight() + MARGIN, bb.GetBottom() + MARGIN

    zone = pcbnew.ZONE(board)
    zone.SetLayer(layer)
    zone.SetNet(gnd)
    zone.SetMinThickness(MIN_THICKNESS)
    _try_set(zone, "SetLocalClearance", CLEARANCE)
    _try_set(zone, "SetPadConnection", pcbnew.ZONE_CONNECTION_THERMAL)
    _try_set(zone, "SetThermalReliefGap", THERMAL_GAP)
    _try_set(zone, "SetThermalReliefSpokeWidth", THERMAL_SPOKE)

    outline = zone.Outline()
    outline.NewOutline()
    for x, y in ((x0, y0), (x1, y0), (x1, y1), (x0, y1)):
        outline.Append(x, y)

    board.Add(zone)
    pcbnew.ZONE_FILLER(board).Fill(board.Zones())  # sets the zone's filled state

    board.Save(path)
    print(f"  added {layer_name} GND pour ({pcbnew.ToMM(x1 - x0):.1f} x "
          f"{pcbnew.ToMM(y1 - y0):.1f}mm outline): {path}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    for p in sys.argv[1:]:
        add_gnd_zone(p)
