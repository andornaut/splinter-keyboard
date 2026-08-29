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

  cost(layer) = non-GND track length on the layer, dangling copper excluded
              + UNREACHABLE_GND_PAD_COST_MM * (GND pads not reachable on it)

Lower is better. The first term measures how much the plane would be fragmented
by signal copper (GND tracks merge into the pour, so they do not count, and so
does copper cleanup-tracks.py is about to strip); the second penalizes each GND
pad that would need a stitching via to reach the plane.
Neither side is inherently preferred: the pour lands on whichever gives the more
continuous plane with fewer stitching vias. On a tie (e.g. an un-routed board
with no signal copper yet) B.Cu wins. The selected layer
and the full per-layer breakdown are printed for every board.

The zone outline is just the board bounding box (inflated slightly); KiCad clips
the actual fill to the Edge.Cuts outline minus the copper-to-edge clearance, so a
rectangle is enough and follows any board shape.

Idempotent: if a GND zone already exists on either candidate layer the board is
left untouched, so re-running (e.g. on every build) is safe.

Usage: add-gnd-zone.py <board.kicad_pcb> [more.kicad_pcb ...]
"""

import sys
from typing import NamedTuple

from lib.pcb_copper import copper_pads, dangling_tracks, ids, is_via, net_class
from lib.pcbnew_quiet import pcbnew
from lib.pipeline_log import note

POUR_NET_CLASS = "Default"  # the pour takes this class's clearance
MIN_THICKNESS = pcbnew.FromMM(0.25)
THERMAL_GAP = pcbnew.FromMM(0.30)
THERMAL_SPOKE = pcbnew.FromMM(0.30)
MARGIN = pcbnew.FromMM(1)  # inflate the outline past the edge; fill clips to Edge.Cuts

# Candidate ground layers, in tie-break preference order (B.Cu wins a tie).
CANDIDATE_LAYERS = (pcbnew.B_Cu, pcbnew.F_Cu)
# Rough cost, in mm of equivalent routing, of the stitching via each GND pad that
# does not reach the pour layer would need. Small: openness dominates the choice.
UNREACHABLE_GND_PAD_COST_MM = 50.0


class LayerScore(NamedTuple):
    """One candidate layer, scored; `cost` drives the choice (lower wins)."""

    layer: int
    name: str
    signal_mm: float
    reach: float
    cost: float


def _signal_track_len_mm(tracks, doomed_ids, layer):
    """Total length of non-GND tracks/arcs on `layer` (GND copper merges into the
    pour, so it does not fragment the plane and is excluded), skipping the copper
    cleanup-tracks.py is about to delete."""
    total = 0.0
    for t in tracks:
        if is_via(t) or id(t) in doomed_ids:
            continue
        if t.GetLayer() != layer:
            continue
        if t.GetNetname() == "GND":
            continue
        total += pcbnew.ToMM(t.GetLength())
    return total


def _gnd_pads(board):
    return [p for fp in board.GetFootprints() for p in fp.Pads() if p.GetNetname() == "GND"]


def choose_gnd_layer(board):
    """Score each candidate layer and return (best, rows, total_gnd_pads), where
    best is the winning LayerScore and rows is every candidate's LayerScore."""
    gnd_pads = _gnd_pads(board)
    total_gnd = len(gnd_pads)
    # Copper that copy-unrouted-to-routed.sh is about to strip must not sway the
    # choice: the unused include_traces_vias stubs are tens of mm of front-side
    # track on v4, all of it gone by the time the plane is poured. The pour this
    # script is about to add does not exist yet, so nothing counts as a filled zone;
    # only a track of the pour's own net could read differently for its absence, and
    # GND tracks are excluded from the score anyway.
    tracks = list(board.GetTracks())
    doomed_ids = ids(dangling_tracks(tracks, copper_pads(board), []))
    rows = []
    for layer in CANDIDATE_LAYERS:
        signal_mm = _signal_track_len_mm(tracks, doomed_ids, layer)
        reach = sum(1 for p in gnd_pads if p.IsOnLayer(layer))
        cost = signal_mm + UNREACHABLE_GND_PAD_COST_MM * (total_gnd - reach)
        rows.append(LayerScore(layer, board.GetLayerName(layer), signal_mm, reach, cost))
    # CANDIDATE_LAYERS is in tie-break order, and min() is stable, so the first
    # (B.Cu) wins an exact cost tie.
    best = min(rows, key=lambda r: r.cost)
    return best, rows, total_gnd


def _print_analysis(path, best, rows, total_gnd):
    note(f"  analysis {path}: GND pour layer")
    for r in rows:
        mark = "  <- selected" if r.layer == best.layer else ""
        note(
            f"    {r.name}: signal={r.signal_mm:7.1f}mm  "
            f"GND-pads-reachable={r.reach}/{total_gnd}  cost={r.cost:7.1f}{mark}"
        )
    note(f"    selected {best.name}")


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
    # entered the pipeline (copy:traces-to-unrouted carries GND teardrops in).
    existing = [
        board.GetLayerName(cand)
        for cand in CANDIDATE_LAYERS
        if any(z.GetNetname() == "GND" and z.IsOnLayer(cand) and not z.IsTeardropArea() for z in board.Zones())
    ]
    if existing:
        msg = f"GND pour already present on {', '.join(existing)}, leaving as-is"
        if layer_name not in existing:
            msg += f"; analysis preferred {layer_name}, not re-pouring an already-poured board"
        note(f"  unchanged {path}: {msg}")
        return

    bb = board.GetBoardEdgesBoundingBox()
    x0, y0 = bb.GetX() - MARGIN, bb.GetY() - MARGIN
    x1, y1 = bb.GetRight() + MARGIN, bb.GetBottom() + MARGIN

    zone = pcbnew.ZONE(board)
    zone.SetLayer(layer)
    zone.SetNet(gnd)
    zone.SetMinThickness(MIN_THICKNESS)
    zone.SetLocalClearance(net_class(board, POUR_NET_CLASS).GetClearance())
    zone.SetPadConnection(pcbnew.ZONE_CONNECTION_THERMAL)
    zone.SetThermalReliefGap(THERMAL_GAP)
    zone.SetThermalReliefSpokeWidth(THERMAL_SPOKE)

    outline = zone.Outline()
    outline.NewOutline()
    for x, y in ((x0, y0), (x1, y0), (x1, y1), (x0, y1)):
        outline.Append(x, y)

    board.Add(zone)
    pcbnew.ZONE_FILLER(board).Fill(board.Zones())  # sets the zone's filled state

    board.Save(path)
    print(
        f"  ADDED {path}: {layer_name} GND pour, {pcbnew.ToMM(x1 - x0):.1f} x "
        f"{pcbnew.ToMM(y1 - y0):.1f}mm pour extent (larger than the board outline)"
    )


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    for p in sys.argv[1:]:
        add_gnd_zone(p)
