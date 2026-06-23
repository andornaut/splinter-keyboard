#!/usr/bin/env python3
"""Add copper keepout rule areas to a KiCad PCB: two perimeter rings just inside
the board edge and a disk around each screw boss.

Three kinds of zone, all rule areas (keepouts) on F.Cu + B.Cu. Pads and
footprints stay allowed at the rule-area level (the rule-area pad keepout cannot
tell plated copper from a bare hole; conductive pads are caught by a separate
.kicad_dru rule -- see apply-project-settings.py). The perimeter is split into
two rings with different jobs so the TRRS corner can be freed for routing while
the GND plane is still excluded there:

  - perimeter pour ring (PERIMETER_POUR_NAME): the full PERIMETER_INSET-wide ring
    following the outer Edge.Cuts periphery, disallowing only the copper pour, so
    the GND plane stays inset from the board edge all the way around (including
    the TRRS corner). The later add-gnd-zone fill clips around it.
  - perimeter route ring (PERIMETER_ROUTE_NAME): the same ring with the TRRS
    corner carved out (see _trrs_carve), disallowing tracks and vias, so DRC
    flags any stray routing into the border EXCEPT at the TRRS connector corner,
    which has no case wall above/below it and whose through-holes and protection
    traces legitimately reach the edge.
  - screw bosses (BOSS_NAME): a disk of (boss radius + BOSS_MARGIN) centered on
    each mounting hole, disallowing pour, tracks, and vias, so nothing lands
    within BOSS_MARGIN of a boss. One zone per boss (a single zone with disjoint
    islands collapses to its first island on save), all sharing one zone name.

Edge-open notches (the USB cutout) are bridged so the rings do not dip into them
(see _perimeter_ring).

Geometry is read from the board, not the config: the perimeter from
GetBoardPolygonOutlines(), and each boss from the User.Eco1 circle coincident
with a mounting-hole footprint (so the disk tracks the boss radius and position
if the screw is retuned). Run in the ergogen step on the dist/ boards; the zones
then ride the cp steps into unrouted/ (so routing and DRC see them) and routed/
(where add-gnd-zone pours around them).

Idempotent: if these keepouts already exist the board is left untouched, so
re-running (e.g. every build) is safe. Like add-gnd-zone, ergogen regenerates
the dist/ boards from scratch each run, so a normal build always re-derives them.

Usage: add-keepout-zones.py <board.kicad_pcb> [more.kicad_pcb ...]
"""
import math
import sys

import pcbnew

# Ring width: keep copper clear of the case support-wall lip (which sits on the
# PCB face), with margin for the board's shift in its pocket and case build
# tolerance, so no pad or trace lands under the wall in the worst-case stack-up.
PERIMETER_INSET = pcbnew.FromMM(2.0)
NOTCH_BRIDGE = pcbnew.FromMM(6.0)     # bridge edge-open notches up to 2x this wide (USB cutout)
BOSS_MARGIN = pcbnew.FromMM(1.0)      # keepout extends this far past the boss edge
BOSS_FALLBACK_RADIUS = pcbnew.FromMM(2.75)  # if no Eco1 boss circle is found
BOSS_FPID_KEY = "mounting_hole"       # footprint-id substring marking a screw boss
CENTER_TOL = pcbnew.FromMM(0.05)      # boss-circle/mounting-hole coincidence tolerance
ARC_ERROR = pcbnew.FromMM(0.01)       # inflate max error
CIRCLE_SEGMENTS = 64                  # polygon approximation of each boss disk
DEGENERATE_EDGE_MAX = pcbnew.FromMM(0.001)  # drop Edge.Cuts shapes shorter than this

# The route-ring carve opens the top edge above the TRRS connector (the case's
# top wall has the port opening there; the inner vertical edge ring stays whole).
# CARVE_MARGIN pads the connector width and the carve depth past the top ring;
# CARVE_OVERSHOOT extends the carve above the top edge and past the inner board
# edge (removing the rounded corner fillet). CARVE_FPID_KEY finds the TRRS.
CARVE_FPID_KEY = "trrs"
CARVE_MARGIN = pcbnew.FromMM(2.0)
CARVE_OVERSHOOT = pcbnew.FromMM(2.0)
# The carve runs out to the far edge of the adjacent top-edge cutout (the USB
# notch beside the TRRS) so no thin tab of top ring is left between them. A
# top-edge notch is an Edge.Cuts point this far below the top edge (deeper than
# the corner fillet, shallower than the board).
NOTCH_PROBE_MIN = pcbnew.FromMM(3.0)
NOTCH_PROBE_MAX = pcbnew.FromMM(15.0)

PERIMETER_POUR_NAME = "keepout_perimeter_pour"
PERIMETER_ROUTE_NAME = "keepout_perimeter_route"
BOSS_NAME = "keepout_screw_bosses"
KEEPOUT_LAYERS = (pcbnew.F_Cu, pcbnew.B_Cu)


def _populate(zone, src):
    """Copy every outline and hole of SHAPE_POLY_SET `src` into the zone's own
    (C++-owned) outline, point by point. Building the outline in place via
    NewOutline/Append/AddHole is the pattern add-gnd-zone.py uses; handing a
    Python-owned poly to SetOutline transfers ownership and double-frees at
    interpreter teardown."""
    dst = zone.Outline()
    for i in range(src.OutlineCount()):
        dst.NewOutline()
        chain = src.Outline(i)
        for p in range(chain.PointCount()):
            pt = chain.CPoint(p)
            dst.Append(pt.x, pt.y)
        for h in range(src.HoleCount(i)):
            dst.AddHole(src.Hole(i, h))  # default: attach to the last outline


def _add_keepout(board, name, src, *, pour, tracks_vias):
    """Add a rule-area zone named `name` with outline `src`, on both copper
    layers. `pour` disallows the copper fill; `tracks_vias` disallows tracks and
    vias.

    Pads and footprints stay allowed: the rule-area pad keepout cannot tell a
    copper pad from a bare hole, so disallowing pads flagged the mechanical
    mounting-hole and TRRS locating holes (no copper). Conductive pads are caught
    instead by the .kicad_dru rule (apply-project-settings.py), which keys on the
    pad type (anything but 'NPTH, mechanical') inside the route/boss areas."""
    zone = pcbnew.ZONE(board)
    zone.SetIsRuleArea(True)
    zone.SetZoneName(name)
    ls = pcbnew.LSET()
    for layer in KEEPOUT_LAYERS:
        ls.AddLayer(layer)
    zone.SetLayerSet(ls)
    zone.SetDoNotAllowZoneFills(pour)
    zone.SetDoNotAllowTracks(tracks_vias)
    zone.SetDoNotAllowVias(tracks_vias)
    zone.SetDoNotAllowPads(False)
    zone.SetDoNotAllowFootprints(False)
    _populate(zone, src)
    board.Add(zone)


def _poly(points):
    """A single-outline SHAPE_POLY_SET from (x, y) points (floats truncated)."""
    poly = pcbnew.SHAPE_POLY_SET()
    poly.NewOutline()
    for x, y in points:
        poly.Append(int(x), int(y))
    return poly


def _footprints(board, fpid_key):
    """Footprints whose (lowercased) library id contains `fpid_key`."""
    return [fp for fp in board.GetFootprints()
            if fpid_key in fp.GetFPIDAsString().lower()]


def _top_notch_far_x(board, edges, trrs_cx, toward_right):
    """X of the far edge of the top-edge cutout (USB notch) beyond the TRRS in the
    carve's direction, or None if there is none. 'Far' = the notch edge away from
    the TRRS, so the carve runs out to it and leaves no top-ring tab between the
    connector opening and the notch."""
    top = edges.GetTop()
    out = pcbnew.SHAPE_POLY_SET()
    board.GetBoardPolygonOutlines(out, False)
    ch = out.Outline(0)
    pts = (ch.CPoint(p) for p in range(ch.PointCount()))
    xs = [pt.x for pt in pts
          if top + NOTCH_PROBE_MIN < pt.y < top + NOTCH_PROBE_MAX
          and (pt.x > trrs_cx) == toward_right]
    return (max if toward_right else min)(xs, default=None)


def _trrs_carve(board):
    """Rectangle to subtract from the route ring, opening the top edge above the
    TRRS connector (the case's top wall has the port opening; the inner vertical
    edge ring is left whole). Returns None if there is no TRRS footprint.

    The opening spans the top edge from the inner board edge -- overshot, so the
    rounded corner fillet is removed and the vertical ring gets a clean straight
    top (a straight carve cannot follow the fillet without a step or sliver) --
    out to the far edge of the adjacent USB notch (merging into that cutout with
    no leftover top-ring tab; falls back to the connector width if no notch is
    found). It is only deep enough to clear the top ring (a margin past its inner
    edge, so no sliver is left), not the vertical edge below."""
    trrs = next(iter(_footprints(board, CARVE_FPID_KEY)), None)
    if trrs is None:
        return None
    edges = board.GetBoardEdgesBoundingBox()
    box = trrs.GetBoundingBox()
    cx = box.GetCenter().x
    toward_right = cx < edges.GetCenter().x   # TRRS near the left edge -> carve opens rightward

    if toward_right:
        inner_edge = edges.GetLeft() - CARVE_OVERSHOOT
        fallback = box.GetRight() + CARVE_MARGIN
    else:
        inner_edge = edges.GetRight() + CARVE_OVERSHOOT
        fallback = box.GetLeft() - CARVE_MARGIN
    notch = _top_notch_far_x(board, edges, cx, toward_right)
    left, right = sorted((inner_edge, notch if notch is not None else fallback))

    top = edges.GetTop() - CARVE_OVERSHOOT
    bottom = edges.GetTop() + PERIMETER_INSET + CARVE_MARGIN
    return _poly([(left, top), (right, top), (right, bottom), (left, bottom)])


def _perimeter_ring(board):
    """SHAPE_POLY_SET ring of width PERIMETER_INSET hugging the inside of the
    outer Edge.Cuts periphery only -- edge-open notches (the USB cutout) are
    bridged so the ring runs straight across them instead of dipping in.

    Bridging is a morphological close (inflate then deflate by NOTCH_BRIDGE with
    square ALLOW_ACUTE corners, which fully fills a notch; rounded corners leave
    it partly open). The ring is then clipped back to the real board outline so
    no keepout floats over the open cutout mouth."""
    outline = pcbnew.SHAPE_POLY_SET()
    if not board.GetBoardPolygonOutlines(outline, False):
        raise SystemExit("could not read board outline (Edge.Cuts)")

    closed = pcbnew.SHAPE_POLY_SET(outline)
    closed.Inflate(NOTCH_BRIDGE, pcbnew.CORNER_STRATEGY_ALLOW_ACUTE_CORNERS, ARC_ERROR)
    closed.Inflate(-NOTCH_BRIDGE, pcbnew.CORNER_STRATEGY_ALLOW_ACUTE_CORNERS, ARC_ERROR)

    inner = pcbnew.SHAPE_POLY_SET(closed)
    inner.Inflate(-PERIMETER_INSET, pcbnew.CORNER_STRATEGY_ROUND_ALL_CORNERS, ARC_ERROR)
    ring = pcbnew.SHAPE_POLY_SET(closed)
    ring.BooleanSubtract(inner)
    ring.BooleanIntersection(outline)
    return ring


def _disk(center, radius):
    """A circle approximated by a CIRCLE_SEGMENTS-gon."""
    angles = (2 * math.pi * i / CIRCLE_SEGMENTS for i in range(CIRCLE_SEGMENTS))
    return _poly((center.x + radius * math.cos(a), center.y + radius * math.sin(a))
                 for a in angles)


def _boss_radius(board, center):
    """Radius of the User.Eco1 boss circle coincident with `center`, or the
    fallback if none is found."""
    for d in board.GetDrawings():
        if (d.GetClass() == "PCB_SHAPE" and d.GetLayerName() == "User.Eco1"
                and d.GetShape() == pcbnew.SHAPE_T_CIRCLE):
            c = d.GetCenter()
            if abs(c.x - center.x) <= CENTER_TOL and abs(c.y - center.y) <= CENTER_TOL:
                return d.GetRadius()
    return BOSS_FALLBACK_RADIUS


def _boss_centers(board):
    """Center of every mounting-hole footprint (one per screw boss)."""
    return [fp.GetPosition() for fp in _footprints(board, BOSS_FPID_KEY)]


def _strip_degenerate_edges(board):
    """Take near-zero-length Edge.Cuts shapes off the Edge.Cuts layer. Ergogen
    emits a zero-length shape where two outline vertices coincide (e.g. the thumb
    hull corner closing exactly onto the box corner), which makes
    GetBoardPolygonOutlines() fail to chain the outline ("could not read board
    outline"). The shape is geometric noise. We test GetLength() so a degenerate
    arc (a fillet collapsing at a coincident corner) is caught as well as a
    segment; real edges are mm-scale, far above the threshold. We move it to
    Cmts.User rather than board.Remove() it: Remove() corrupts pcbnew's SWIG type
    table (later zone.Outline() then returns an untyped SwigPyObject with no
    NewOutline); re-layering mutates nothing the outline reader sees and leaves
    SWIG intact. Returns the count moved."""
    moved = 0
    for d in board.GetDrawings():
        if (d.GetClass() == "PCB_SHAPE" and d.GetLayer() == pcbnew.Edge_Cuts
                and d.GetShape() in (pcbnew.SHAPE_T_SEGMENT, pcbnew.SHAPE_T_ARC)
                and d.GetLength() < DEGENERATE_EDGE_MAX):
            d.SetLayer(pcbnew.Cmts_User)
            moved += 1
    return moved


def add_keepout_zones(path):
    board = pcbnew.LoadBoard(path)

    keepout_names = (PERIMETER_POUR_NAME, PERIMETER_ROUTE_NAME, BOSS_NAME)
    existing = {z.GetZoneName() for z in board.Zones()
                if z.GetIsRuleArea() and z.GetZoneName() in keepout_names}
    if existing:
        print(f"  UNCHANGED: keepouts already present ({', '.join(sorted(existing))}): {path}")
        return

    moved = _strip_degenerate_edges(board)
    if moved:
        print(f"  moved {moved} degenerate Edge.Cuts shape(s) to Cmts.User")

    ring = _perimeter_ring(board)
    _add_keepout(board, PERIMETER_POUR_NAME, ring, pour=True, tracks_vias=False)

    route_ring = pcbnew.SHAPE_POLY_SET(ring)
    carve = _trrs_carve(board)
    if carve is not None:
        route_ring.BooleanSubtract(carve)
    _add_keepout(board, PERIMETER_ROUTE_NAME, route_ring, pour=False, tracks_vias=True)

    centers = _boss_centers(board)
    if not centers:
        raise SystemExit(f"{path}: no mounting-hole footprints found for boss keepouts")
    for center in centers:
        _add_keepout(board, BOSS_NAME, _disk(center, _boss_radius(board, center) + BOSS_MARGIN),
                     pour=True, tracks_vias=True)

    board.Save(path)
    print(f"  ADDED keepouts: {pcbnew.ToMM(PERIMETER_INSET):.1f}mm perimeter pour ring + "
          f"route ring (TRRS corner carved) + {len(centers)} screw-boss disks "
          f"(+{pcbnew.ToMM(BOSS_MARGIN):.1f}mm): {path}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    for p in sys.argv[1:]:
        add_keepout_zones(p)
