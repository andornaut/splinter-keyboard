#!/usr/bin/env python3
"""Add a filled bottom-layer (B.Cu) GND pour to a KiCad PCB.

Ergogen emits no copper zones, so the generated boards have no ground plane. A
bottom pour gives the TVS data-line clamp a low-impedance return, a clean
reference for the split serial link, and auto-connects every GND pad so the
ground net barely needs hand routing. Front copper is left clear for the switch
footprints and silk; add an F.Cu pour by hand later if a board ever needs it.

The zone outline is just the board bounding box (inflated slightly); KiCad clips
the actual fill to the Edge.Cuts outline minus the copper-to-edge clearance, so a
rectangle is enough and follows any board shape.

Idempotent: if a GND zone already exists on B.Cu the board is left untouched, so
re-running (e.g. on every build) is safe.

Usage: add-gnd-zone.py <board.kicad_pcb> [more.kicad_pcb ...]
"""
import sys
import pcbnew

CLEARANCE = pcbnew.FromMM(0.25)
MIN_THICKNESS = pcbnew.FromMM(0.25)
THERMAL_GAP = pcbnew.FromMM(0.30)
THERMAL_SPOKE = pcbnew.FromMM(0.30)
MARGIN = pcbnew.FromMM(1)  # inflate the outline past the edge; fill clips to Edge.Cuts


def _try_set(obj, name, *args):
    """Call obj.<name>(*args) if it exists (API varies across KiCad versions)."""
    fn = getattr(obj, name, None)
    if fn is not None:
        fn(*args)


def add_gnd_zone(path):
    board = pcbnew.LoadBoard(path)

    gnd = board.FindNet("GND")
    if gnd is None:
        raise SystemExit(f"{path}: no GND net found")

    if any(z.GetNetname() == "GND" and z.IsOnLayer(pcbnew.B_Cu)
           for z in board.Zones()):
        print(f"  ok (B.Cu GND zone already present): {path}")
        return

    bb = board.GetBoardEdgesBoundingBox()
    x0, y0 = bb.GetX() - MARGIN, bb.GetY() - MARGIN
    x1, y1 = bb.GetRight() + MARGIN, bb.GetBottom() + MARGIN

    zone = pcbnew.ZONE(board)
    zone.SetLayer(pcbnew.B_Cu)
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
    print(f"  added B.Cu GND pour ({pcbnew.ToMM(x1 - x0):.1f} x {pcbnew.ToMM(y1 - y0):.1f}mm "
          f"outline): {path}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    for p in sys.argv[1:]:
        add_gnd_zone(p)
