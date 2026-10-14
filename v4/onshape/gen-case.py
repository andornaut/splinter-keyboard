#!/usr/bin/env python3
"""Build the v4 case as solid geometry from BUILD.md's numbers and the un-filleted hull, and
validate a hand-modelled case against it.

BUILD.md is the specification; this is its executable form. Every dimension here appears
there, and a change belongs in both. The master is the Onshape document, modelled by hand
from BUILD.md; FC_COMPARE checks an export of it against this reference.

Output is real B-rep, not a mesh: cylinders are cylinders, the cavity's tool-radius
corners are arcs, and the outer profile measures its nominal size rather than a polygon
inscribed in it. Each exported file is read back and checked before the script exits, so a
file that cannot be imported never reaches a CAD tool.

Runs under `freecadcmd` or plain `python3`; the sys.path shim below finds the FreeCAD
modules, which Debian keeps off the default path. `freecadcmd` is the portable choice,
since the shim hardcodes that layout. Arguments come from the environment either way,
because freecadcmd treats trailing arguments as documents to open rather than passing them
to the script.

  freecadcmd v4/onshape/gen-case.py

  FC_HALF     left | right | both      (default both)
  FC_EXPLODE  mm to drop the plate by  (default 0; 25 separates it for viewing)
  FC_DXF      hull to build from       (default dist/v4/ergogen/outlines/...)
  FC_OUTDIR   where to write           (default dist/v4/onshape)
  FC_COMPARE  comma-separated STEP file(s) of one hand-modelled half, shell and plate
              assembled; needs FC_HALF left or right
  FC_DIFFS    recorded intentional differences (default v4/onshape/differences.json)

Frame matches the build sheet: outline centre at the origin, z=0 at the shell's top face,
+z up, +x toward the inner (thick) edge. The right half is the exact mirror.
"""

import collections
import json
import math
import os
import sys

for _p in ("/usr/lib/freecad-python3/lib", "/usr/lib/freecad/lib"):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import contextlib
from pathlib import Path

import FreeCAD as App
import Part
from FreeCAD import Placement, Rotation, Vector

DEFAULT_DXF = "dist/v4/ergogen/outlines/full_unfilleted.dxf"
DEFAULT_OUTDIR = "dist/v4/onshape"
DEFAULT_DIFFS = "v4/onshape/differences.json"

# ---- comparison ----------------------------------------------------------
# Fuzzy tolerances for the comparison Booleans, tried in order until one computes sanely
# (see residuals()). Two kernels place the same face nanometres apart, and an exact Boolean
# turns that into sliver solids along every coincident face, so a fuzzy one comes first;
# the exact one is last, its slivers filtered out by COMPARE_MIN_THICK.
COMPARE_FUZZES = (1e-3, 5e-3, 1e-5, 0.0)
# A residual thinner than this (twice volume over area) or smaller than COMPARE_MIN_VOL is
# kernel noise, not geometry, and needs no decision.
COMPARE_MIN_THICK = 0.01
COMPARE_MIN_VOL = 1e-3
# A part whose bounding-box centre is this far from the reference's is in another frame,
# and every face would report as a difference. Caught first so the report names the cause.
FRAME_TOL = 1.0
# Slack when testing a difference region against a recorded box.
MATCH_TOL = 0.05

# ---- BUILD.md parameters -------------------------------------------------
WALL = 2.00
# Per side, on the hull. 0.50 rather than a machining fit: an FDM part loses 0.2-0.3% to
# XY shrink across 160mm and another 0.1-0.2 per wall to perimeter over-extrusion, which
# closes a tenth-millimetre pocket outright. It costs nothing on the milled variant, since
# the board is located by its screws either way (see USB_W).
POCKET_CLR = 0.50
TOP_THICK = 3.00
RECESS_Z = -1.50
PCB_TOP = -6.00
PCB_BOT = -7.60
H_INNER = 17.00
H_OUTER = 13.00
PLATE = 1.50
CAVITY_FILLET = 2.00  # tool radius
EDGE_FILLET = 1.00  # where the outer wall meets the top face, and where it meets the bottom rim
# Hull vertices closer than this are one vertex the DXF happened to write twice.
HULL_WELD = 1e-3
# Hull vertices snap to this grid. The DXF writes the board's straight edges a few tenths of
# a micron off true, so a vertical edge leans and a cut squared to it leaves a step.
HULL_GRID = 1e-3
BOSS_R = 2.75
BORE_R = 1.80  # 3.60 dia heat-set insert
# Every boss. It stops the bore below RECESS_Z, so no switch recess reaches it on either half.
BORE_DEPTH = 4.00
STANDOFF_R = 2.75
SCREW_R = 1.45  # 2.90 dia clearance
CBORE_R = 2.50  # 5.00 dia, flat-bottomed, for a flat-underside head
LID_CLR = 0.20  # plate outline in from the cavity, per side; a print fit
# The board is clamped around its whole perimeter, not only at the three bosses: a shelf
# hangs from the case's top and the plate carries a matching wall up to meet it. The two
# share one inner loop, so they lap the board by the same SHELF_W - POCKET_CLR; the plate
# wall is LID_CLR narrower because the plate edge sits that far in from the cavity. The lap
# is what has to stay inside the board's own perimeter keepout (add-keepout-zones.py
# PERIMETER_INSET) so neither lands on a ground plane, and it shrinks 1:1 with any
# loosening of POCKET_CLR.
# Tracks are a different matter: the ROUTE ring is carved open over the TRRS, so copper
# under soldermask is legal there and the shelf can cross it.
SHELF_W = 1.75
# Flared standoff base. Without it the counterbore runs the plate's full thickness inside a
# 5.50 standoff, leaving the two joined by a 0.25mm annulus: the screw head would bear on
# the standoff and the plate would hang off 4.12 mm2 per boss. 8.00 matches the built v4
# lid. HEIGHT is what constrains a flare, not diameter: it stops below the hotswap sockets
# hanging under the board, and the pads it would otherwise have to dodge are all above it.
FLARE_R = 4.00
# The flare's top, below the board underside. Clears SOCKET_H with room for that figure,
# which is unmeasured, to be wrong.
FLARE_GAP = 2.75
SOCKET_H = 1.85

# Port heights are MEASURED, never derived from the part stack. The TRRS comes off the
# built v4 case, which shares this z stack exactly (top face 0, top underside -3.00, PCB
# -6.00 to -7.60), so its port centres transfer directly. The USB is 0.50 higher than that
# case carries, set on a printed part of THIS design where the inherited height sat low.
# Re-measure on hardware before changing either.
TRRS_X, TRRS_Y = 74.650, 59.500
TRRS_Z, TRRS_R = -10.50, 2.75
USB_X0, USB_X1 = 56.663, 66.663
USB_Z, USB_H = -10.25, 4.00
# Stated, NOT derived from POCKET_CLR. The opening has to stay inside the board's own 10.00
# notch so the plug clears the board edge, and how far inside is set by how far the board
# can move, which is the screws and not the pocket: a 2.5mm screw in a 3.00mm hole is 0.25
# per side whatever the pocket fit is. Deriving it would shrink the port every time the
# pocket is loosened, which is the wrong direction.
USB_W = 9.50
# Both ports are plain cutouts straight through the wall. No counterbore and no recess: a
# pocket on the outer face reads as the port being sunk into the case rather than opened
# through it. The USB clears an 8.34mm plug shell by 0.58 per side. It is a slot with
# USB_H/2 ends rather than a rectangle: a USB-C shell is rounded the same way, and an end
# mill cutting from the side cannot make a rectangle's internal corners.

# The plate wall's top band ends here, short of the USB plug's path and the jack. The
# inner wall runs the full height: it clears the jack. The cut that ends the band starts
# below it at WALL_RELIEF_Y and stops at the inner wall's inner face.
WALL_RELIEF_X = 51.75
WALL_RELIEF_Y = 45.00

# Bumper recesses on the plate's outer face, each tangent to the plate wall's inner loop in
# its corner, so the feet sit as far out as the plate allows.
BUMPERS = [(-72.75, 52.25), (72.75, 52.25), (-72.75, -34.50), (69.36, -50.27)]
BUMPER_R, BUMPER_D = 6.00, 0.50

BIG = 500.0
EPS = 1e-6

# What reading the export back must find, keyed by cylinder radius. Catches a feature that
# silently stopped being cut as well as one that came out the wrong size. The 1.00 count is
# not listed because it is derived from the key field: 4 corner fillets on each cutout and
# 4 on each recess, and the halves carry different numbers of keys.


def _census(*pairs):
    """Sum (radius, count) pairs by rounded radius, since two features may share a radius."""
    out = collections.Counter()
    for r, n in pairs:
        out[round(r, 2)] += n
    return dict(out)


EXPECT_CYL = {
    "shell": _census(
        (BORE_R, 3),  # the insert bores
        (CAVITY_FILLET, 6),  # the cavity's tool-radius corners and its kink
        (CAVITY_FILLET, 6),  # the shelf's inner corners, its kink closed at the same radius
        (BOSS_R, 3),
        (TRRS_R, 1),
        (POCKET_CLR + WALL, 6),  # the outer profile's corners and its kink
    ),
    "plate": _census(
        (SCREW_R, 3),
        (CAVITY_FILLET, 5),  # the outline's corners, opened back to the cavity's radius
        (CAVITY_FILLET, 1),  # the outline's kink
        # The plate wall's inner corners and its kink. Five, not six: one corner falls
        # inside the top-inner relief.
        (CAVITY_FILLET, 5),
        (CBORE_R, 3),
        (STANDOFF_R, 3),  # above their flares
        (FLARE_R, 3),
        (BUMPER_R, 4),
    ),
}
CNC_FILLET_R = 1.00
# Face area splitting a switch cutout from the recess above it. Only has to land between
# two widely separated clusters; what actually holds the split is the nesting check in
# classify(), which does not depend on where the threshold sits.
CUTOUT_RECESS_SPLIT = 230.0


# ---- DXF, as real edges --------------------------------------------------
def dxf_entities(path):
    """Group codes we care about, per LINE/ARC/CIRCLE entity."""
    with Path(path).open() as fh:
        lines = fh.read().splitlines()
    out, kind, g = [], None, {}
    for i in range(0, len(lines) - 1, 2):
        code, val = lines[i].strip(), lines[i + 1].strip()
        if code == "0":
            if kind:
                out.append((kind, g.copy()))
            kind = val if val in ("LINE", "ARC", "CIRCLE") else None
            g = {}
        elif kind and code.isdigit() and int(code) in (10, 11, 20, 21, 40, 50, 51):
            with contextlib.suppress(ValueError):
                g[int(code)] = float(val)
    if kind:
        out.append((kind, g.copy()))
    return out


def dxf_shapes(path):
    """Edges as lines and TRUE arcs, plus full circles as (centre, radius).

    The arcs matter: discretising them here would put the switch cutouts' corner fillets
    into the model as polygons, which is the whole thing this script exists to avoid.
    """
    edges, circles = [], []
    for kind, g in dxf_entities(path):
        if kind == "LINE":
            a, b = Vector(g[10], g[20], 0), Vector(g[11], g[21], 0)
            if a.distanceToPoint(b) > EPS:
                edges.append(Part.LineSegment(a, b).toShape())
        elif kind == "ARC":
            circ = Part.Circle(Vector(g[10], g[20], 0), Vector(0, 0, 1), g[40])
            a0, a1 = math.radians(g.get(50, 0.0)), math.radians(g.get(51, 360.0))
            edges.append(Part.ArcOfCircle(circ, a0, a1).toShape())
        elif kind == "CIRCLE":
            circles.append(((g[10], g[20]), g[40]))
    return edges, circles


def centre_xy(shape):
    bb = shape.BoundBox
    return (bb.XMin + bb.XMax) / 2.0, (bb.YMin + bb.YMax) / 2.0


def face_area(wire):
    try:
        return Part.Face(wire).Area
    # Broad on purpose: a wire that does not bound a face is the ordinary case
    # here, and FreeCAD raises whatever its OCC binding raises for it.
    except Exception:  # noqa: BLE001
        return 0.0


def classify(path, half):
    """Split the DXF into the wall, the switch cutouts, the recesses and the boss circles.

    Ergogen puts everything on layer 0, so these are told apart by connectivity and extent
    rather than by layer: each is its own closed loop, and a 14.5 cutout and a 16.0 recess
    are separated by area rather than bounding box, since the thumb keys are splayed.
    """
    edges, circles = dxf_shapes(path)
    ws = [Part.Wire(c) for c in Part.sortEdges(edges)]
    xs = [v.X for w in ws for v in w.Vertexes]
    mid = (min(xs) + max(xs)) / 2.0
    keep = (lambda x: x < mid) if half == "left" else (lambda x: x > mid)
    ws = [w for w in ws if keep(centre_xy(w)[0])]
    circles = [c for c in circles if keep(c[0][0])]

    wall = max(ws, key=lambda w: w.BoundBox.XLength * w.BoundBox.YLength)
    rest = [w for w in ws if w is not wall]
    bosses = [c for c, r in circles if abs(r - BOSS_R) < 0.01]
    if len(bosses) != 3:
        raise SystemExit(
            f"FAIL gen-case: found {len(bosses)} boss circle(s) of radius "
            f"{BOSS_R:.2f}, expected 3. If screw_boss_radius changed in "
            "config.yaml, BOSS_R must follow"
        )
    holes = [w for w in rest if face_area(w) < CUTOUT_RECESS_SPLIT]
    recess = [w for w in rest if face_area(w) >= CUTOUT_RECESS_SPLIT]
    # Every cutout nests inside its own recess, so pairing is the invariant to assert, not
    # the threshold. Nothing downstream would catch a bad split: `keys` and the corner-arc
    # census both count holes PLUS recesses, so a shell cut with no recesses at all reads
    # back as correct.
    if len(holes) != len(recess):
        raise SystemExit(
            f"FAIL gen-case: {half} half split into {len(holes)} cutout(s) and "
            f"{len(recess)} recess(es), which must be equal. Each switch is one "
            "cutout nested in one recess, so a change to either size in "
            "config.yaml means CUTOUT_RECESS_SPLIT must follow"
        )
    faces = [Part.Face(w) for w in recess]
    for w in holes:
        hx, hy = centre_xy(w)
        n = sum(1 for f in faces if f.isInside(Vector(hx, hy, 0.0), 1e-6, True))
        if n != 1:
            raise SystemExit(
                f"FAIL gen-case: the cutout at ({hx:.3f}, {hy:.3f}) sits inside "
                f"{n} recess(es), expected exactly 1: the area split has "
                "misread the key field"
            )
    return wall, holes, recess, bosses


# ---- helpers -------------------------------------------------------------
def offset(wire, dist):
    """makeOffset2D, with the sign resolved by whether the result actually grew.

    Which way a positive distance goes depends on the wire's orientation, which comes from
    however the DXF happened to be chained.
    """
    if abs(dist) < EPS:
        return wire
    for d in (dist, -dist):
        try:
            a = wire.makeOffset2D(d, 0, False, False, False)
        # Broad on purpose, and nothing to log: trying the other sign is the
        # whole point of the loop, and only the failure of both is an error.
        except Exception:  # noqa: BLE001, S112
            continue  # the wrong sign can throw outright, not just come back wrong
        if (a.BoundBox.XLength > wire.BoundBox.XLength) == (dist > 0):
            return a
    raise SystemExit(f"FAIL gen-case: no offset of {dist:+.3f} produced an outline")


def opened(wire, r):
    """Morphological opening: the region a tool of radius r can actually reach.

    Rounds the pocket's internal corners at r and leaves external ones sharp, which is
    what an end mill does. Filleting the solid afterwards would need edge selection and
    would not model the constraint.
    """
    return offset(offset(wire, -r), r)


def closed(wire, r):
    """Morphological closing: rounds the re-entrant corners at r and leaves the rest."""
    return offset(offset(wire, r), -r)


def prism(wire, z0, z1):
    return Part.Face(wire).extrude(Vector(0, 0, z1 - z0)).translated(Vector(0, 0, z0))


def moved(shape, vec):
    s = shape.copy()
    s.translate(vec)
    return s


def half_space(sign, ang, up):
    """Everything below the sloped bottom plane, raised by `up`."""
    box = Part.makeBox(BIG * 2, BIG * 2, BIG, Vector(-BIG, -BIG, -BIG))
    box.Placement = Placement(Vector(0, 0, rim_z(sign, 0.0) + up), Rotation(Vector(0, 1, 0), sign * ang))
    return box


def cyl(r, z0, z1, x=0.0, y=0.0):
    return Part.makeCylinder(r, z1 - z0, Vector(x, y, z0), Vector(0, 0, 1))


def usb_slot(sign, dz=0.0):
    """The USB opening, run 20mm either side of the top edge so it overshoots both wall faces."""
    ux = sign * (USB_X0 + USB_X1) / 2.0
    r = USB_H / 2.0
    half = USB_W / 2.0 - r
    y0, z = TRRS_Y - 20.0, USB_Z + dz
    slot = Part.makeBox(2 * half, 40.0, USB_H, Vector(ux - half, y0, z - r))
    for x in (ux - half, ux + half):
        slot = slot.fuse(Part.makeCylinder(r, 40.0, Vector(x, y0, z), Vector(0, 1, 0)))
    return slot.removeSplitter()


def shell_width():
    return 160.0 + 2 * (POCKET_CLR + WALL)


def rim_z(sign, x):
    """Bottom-rim z at a given x. The two edge heights are specified; the angle is not."""
    return -(H_INNER + H_OUTER) / 2.0 - sign * (H_INNER - H_OUTER) / shell_width() * x


def unnotched_hull(wall, sign):
    """The hull with the board's USB notch filled in.

    NOTHING in the case follows that notch: not the outer profile, not the cavity, not the
    plate. It exists to clear the plug's overmold, which sits below the board entirely, so
    to the case it is only a bite out of an edge that should run straight. Inheriting it
    puts a jog in all three outlines and leaves a pointless tongue of material in the
    pocket. Filling it leaves a void where the board is absent, which gives the plug more
    room rather than less.
    """
    ux0 = min(sign * USB_X0, sign * USB_X1) - 0.5
    ux1 = max(sign * USB_X0, sign * USB_X1) + 0.5
    ty = wall.BoundBox.YMax
    fill = Part.Face(
        Part.makePolygon(
            [
                Vector(ux0, ty - 12.0, 0),
                Vector(ux1, ty - 12.0, 0),
                Vector(ux1, ty, 0),
                Vector(ux0, ty, 0),
                Vector(ux0, ty - 12.0, 0),
            ]
        )
    )
    # Fuse as solids and read the top face back: fusing two coplanar FACES leaves the union
    # split into pieces that removeSplitter will not merge, and picking one of them yields
    # a fragment rather than the hull.
    merged = Part.Face(wall).extrude(Vector(0, 0, 1.0)).fuse(fill.extrude(Vector(0, 0, 1.0))).removeSplitter()
    tops = [
        f
        for f in merged.Faces
        if isinstance(f.Surface, Part.Plane) and abs(f.Surface.Axis.z) > 0.999 and abs(f.CenterOfMass.z - 1.0) < 1e-6
    ]
    outline = moved(max(tops, key=lambda f: f.Area).OuterWire, Vector(0, 0, -1.0))
    # The DXF splits one corner with a sub-micron segment. The kink's closing rounds any
    # re-entrant corner, so that segment would come back as a stray arc: weld it shut.
    if any(not isinstance(e.Curve, Part.Line) for e in outline.Edges):
        raise SystemExit("FAIL gen-case: the hull has a curved edge; it is expected to be straight lines only")
    pts = []
    for v in outline.OrderedVertexes:
        p = Vector(round(v.Point.x / HULL_GRID) * HULL_GRID, round(v.Point.y / HULL_GRID) * HULL_GRID, 0)
        if not pts or (p - pts[-1]).Length > HULL_WELD:
            pts.append(p)
    if (pts[0] - pts[-1]).Length <= HULL_WELD:
        pts.pop()
    return Part.makePolygon([*pts, pts[0]])


def check_bores(recess, bosses):
    """Refuse an insert bore that reaches the recess band without clearing the recess wall.

    A bore whose top passes RECESS_Z runs alongside the recesses, and one passing within
    BORE_R of a recess wall opens through it. This is what bounds BORE_DEPTH, and it cannot
    be left to readback: a breakout trims the bore's
    cylindrical face without splitting it or changing its height, so both the face census
    and the depth check pass a shell that has one.
    """
    for bx, by in bosses:
        if PCB_TOP + BORE_DEPTH <= RECESS_Z:
            continue
        v = Part.Vertex(bx, by, 0.0)
        d = min(w.distToShape(v)[0] for w in recess)
        if d < BORE_R:
            raise SystemExit(
                f"FAIL gen-case: the bore at ({bx:.3f}, {by:.3f}) reaches z "
                f"{PCB_TOP + BORE_DEPTH:.2f}, above the {RECESS_Z:.2f} "
                f"recess floor, and a recess wall is {d:.3f} from its axis against a {BORE_R:.2f} "
                "bore radius: it breaks out. Reduce BORE_DEPTH"
            )


def top_face(shell):
    """The top face, at z=0."""
    tops = [
        f
        for f in shell.Faces
        if isinstance(f.Surface, Part.Plane) and abs(f.Surface.Axis.z) > 0.999 and abs(f.CenterOfMass.z) < 1e-6
    ]
    return max(tops, key=lambda f: f.Area, default=None)


def rim_face(shell):
    """The sloped bottom rim: the lowest flat ring, its inner wire the cavity's mouth."""
    rims = [
        f
        for f in shell.Faces
        if isinstance(f.Surface, Part.Plane) and abs(f.Surface.Axis.z) > 0.99 and len(f.Wires) > 1
    ]
    return min(rims, key=lambda f: f.CenterOfMass.z, default=None)


def fillet_edges(body, r):
    """Fillet the outer wall's top and bottom edges.

    Only each face's OUTER wire: the top face's inner wires are the switch recesses, which
    stay square, and the rim's inner wire is the cavity's mouth.
    """
    top, rim = top_face(body), rim_face(body)
    if top is None or rim is None:
        raise SystemExit("FAIL gen-case: no top face or bottom rim to fillet")
    return body.makeFillet(r, top.OuterWire.Edges + rim.OuterWire.Edges)


# ---- build ---------------------------------------------------------------
def build(dxf, half, explode):
    wall, holes, recess, bosses = classify(dxf, half)
    cx, cy = centre_xy(wall)
    shift = Vector(-cx, -cy, 0)
    wall = moved(wall, shift)
    holes = [moved(w, shift) for w in holes]
    recess = [moved(w, shift) for w in recess]
    bosses = [(bx - cx, by - cy) for bx, by in bosses]

    sign = 1 if half == "left" else -1
    ang = math.degrees(math.atan((H_INNER - H_OUTER) / shell_width()))

    hull = unnotched_hull(wall, sign)
    # The hull's one re-entrant corner, the kink where the thumb cluster meets the main
    # field, is rounded on both faces of the wall for looks, at each loop's own corner
    # radius. Neither arc reaches the board: outside it adds wall, inside it only trims
    # what would be a sharp point of wall.
    outer_w = closed(offset(hull, POCKET_CLR + WALL), POCKET_CLR + WALL)
    cavity_w = closed(opened(offset(hull, POCKET_CLR), CAVITY_FILLET), CAVITY_FILLET)
    # The plate follows the cavity, LID_CLR inside it, so it drops into the pocket. Every
    # corner is then rounded at CAVITY_FILLET, the design's minimum, the kink included:
    # concentric with the cavity it would be CAVITY_FILLET + LID_CLR, which narrows the fit
    # gap there by only 0.003.
    plate_w = closed(opened(offset(hull, POCKET_CLR - LID_CLR), CAVITY_FILLET), CAVITY_FILLET)
    # The shelf's inner loop, shared by the plate wall, is an inset of the HULL opened in
    # its own right.
    # Chaining them off cavity_w would shrink its corner arcs by the inset, leaving 0.25
    # where CAVITY_FILLET is meant, and collapsing them outright at an inset of 2.00.
    shelf_w = closed(opened(offset(hull, POCKET_CLR - SHELF_W), CAVITY_FILLET), CAVITY_FILLET)
    plate_wall_w = shelf_w

    check_bores(recess, bosses)

    # --- shell
    body = prism(outer_w, -BIG, 0.0).cut(half_space(sign, ang, 0.0))
    body = body.cut(prism(cavity_w, -BIG, -TOP_THICK))
    for w in recess:
        body = body.cut(prism(w, RECESS_Z, 1.0))
    for w in holes:
        body = body.cut(prism(w, -BIG, 1.0))

    # Ports overshoot the outer face on both sides, so no cut face lands coplanar with a
    # shell face, which would leave the solid non-manifold.
    body = body.cut(Part.makeCylinder(TRRS_R, 40.0, Vector(sign * TRRS_X, TRRS_Y - 20.0, TRRS_Z), Vector(0, 1, 0)))
    body = body.cut(usb_slot(sign))

    # Perimeter shelf: the board is pressed up against its underside. This narrows the
    # opening going up, which is the legal direction; a lip the board RESTS on would widen
    # going up and no setup could reach it.
    body = body.fuse(prism(cavity_w, PCB_TOP, -TOP_THICK).cut(prism(shelf_w, PCB_TOP - 1.0, -TOP_THICK + 1.0)))

    for bx, by in bosses:
        body = body.fuse(cyl(BOSS_R, PCB_TOP, -TOP_THICK, bx, by))
    body = body.removeSplitter()

    for bx, by in bosses:
        body = body.cut(cyl(BORE_R, PCB_TOP, PCB_TOP + BORE_DEPTH, bx, by))
    shell = fillet_edges(body.removeSplitter(), EDGE_FILLET)

    # --- plate
    # Thicknesses on the sloped plate are square to its faces, as an offset plane measures
    # them, so each rises 1/cos(ang) times as far vertically.
    plate_rise = PLATE / math.cos(math.radians(ang))
    slab = half_space(sign, ang, plate_rise).cut(half_space(sign, ang, 0.0))
    plate = prism(plate_w, -BIG, BIG).common(slab)
    # Perimeter wall, rising to the board's underside so the board is sandwiched between it
    # and the shelf above. Built from the plate's top face up, so relieving it cannot bite
    # into the plate itself. Its top band stops short of the top-inner corner, where the
    # tall parts and both ports are; the inner wall runs on to the corner.
    ring = (
        prism(plate_w, -BIG, PCB_BOT)
        .cut(prism(plate_wall_w, -BIG - 1.0, PCB_BOT + 1.0))
        .cut(half_space(sign, ang, plate_rise))
    )
    inner_face = sign * (abs(hull.BoundBox.XMax if sign > 0 else hull.BoundBox.XMin) - (SHELF_W - POCKET_CLR))
    rx0 = min(sign * WALL_RELIEF_X, inner_face)
    rx1 = max(sign * WALL_RELIEF_X, inner_face)
    ring = ring.cut(Part.makeBox(rx1 - rx0, BIG, 2 * BIG, Vector(rx0, WALL_RELIEF_Y, -BIG)))
    plate = plate.fuse(ring)
    for bx, by in bosses:
        plate = plate.fuse(cyl(STANDOFF_R, -BIG, PCB_BOT, bx, by).cut(half_space(sign, ang, 0.0)))
        plate = plate.fuse(cyl(FLARE_R, -BIG, PCB_BOT - FLARE_GAP, bx, by).cut(half_space(sign, ang, 0.0)))
    plate = plate.removeSplitter()

    # Flat-bottomed counterbore, not a countersink: the screw has a flat head underside. It
    # runs the plate's full thickness and bears on the flare's base, so the standoff keeps
    # its full height and the flare still joins the plate over a 1.50mm annulus.
    #
    # Its floor is the plate's top face, so it lies PARALLEL to the plate, as a hole tool
    # started from the plate's underside cuts it. Across the 5.00 counterbore that is 0.06
    # off level each side of the vertical screw axis, which a printed plate takes up under
    # the head.
    for bx, by in bosses:
        plate = plate.cut(cyl(SCREW_R, -BIG, BIG, bx, by))
        plate = plate.cut(cyl(CBORE_R, -BIG, BIG, bx, by).common(half_space(sign, ang, plate_rise)))
    # A bumper recess is a fixed removal, so its floor is PARALLEL to the plate faces and
    # every foot leaves the same material behind. A horizontal floor would be a constant z
    # in a plate that is not, making the recess shallower at one edge than the other and
    # leaving a different thickness at each. A stuck-on foot has no axis wanting a
    # horizontal seat, so the plate wins: bounded by two slope-parallel planes.
    skin = half_space(sign, ang, BUMPER_D / math.cos(math.radians(ang))).cut(half_space(sign, ang, 0.0))
    for bx, by in BUMPERS:
        plate = plate.cut(cyl(BUMPER_R, -BIG, BIG, sign * bx, by).common(skin))
    plate = plate.removeSplitter()

    if explode:
        plate = moved(plate, Vector(0, 0, -explode))
    return shell, plate, len(holes) + len(recess)


# ---- export and check ----------------------------------------------------
def export(shell, plate, half, out):
    doc = App.newDocument("case")
    for name, shp in (("shell", shell), ("plate", plate)):
        o = doc.addObject("Part::Feature", name)
        o.Shape = shp
        o.Label = f"splinter_v4_{half}_{name}"
    doc.recompute()
    # FreeCAD's STEP module, imported at the point of use, the one place it is needed.
    import Import  # noqa: PLC0415

    Import.export(doc.Objects, out)
    App.closeDocument(doc.Name)


def check(out, half, explode, keys):
    """Read the export back and prove it is what a strict importer will see.

    Reading the FILE rather than the in-memory shape is the point: a STEP can hold valid
    geometry and still import as nothing if its product structure is missing.
    """
    shp = Part.Shape()
    shp.read(out)
    fails = []
    if len(shp.Solids) != 2:
        fails.append(f"expected 2 solids, found {len(shp.Solids)}")
        return fails
    shell, plate = sorted(shp.Solids, key=lambda s: -s.Volume)

    for name, s in (("shell", shell), ("plate", plate)):
        if not s.isValid():
            fails.append(f"{name} is not a valid solid")
        if not s.isClosed():
            fails.append(f"{name} is not closed")

    # BoundBox pads the top fillet's tori by up to 0.4mm, and optimalBoundingBox crashes
    # FreeCAD 0.21. Planes and cylinders bound exactly and carry every extreme of the shell.
    bb = App.BoundBox()
    for f in shell.Faces:
        if isinstance(f.Surface, (Part.Plane, Part.Cylinder)):
            bb.add(f.BoundBox)
    for lbl, got, want in (
        ("width", bb.XLength, 160.0 + 2 * (POCKET_CLR + WALL)),
        ("depth", bb.YLength, 119.0 + 2 * (POCKET_CLR + WALL)),
        # The bottom edge fillet rounds off the lowest corner, so the lowest point is where
        # it meets the sloped rim, EDGE_FILLET inboard and that much of the slope higher.
        ("height", bb.ZLength, H_INNER - EDGE_FILLET * (H_INNER - H_OUTER) / shell_width()),
    ):
        if abs(got - want) > 0.01:
            fails.append(f"shell {lbl} {got:.3f}, expected {want:.3f}")

    if not explode and abs(plate.BoundBox.ZMax - PCB_BOT) > 0.01:
        fails.append(f"plate wall top {plate.BoundBox.ZMax:.3f}, expected the board underside {PCB_BOT:.3f}")
    # The shelf's underside is what the board is clamped against, so it must be a real
    # horizontal face at the board's top, not merely somewhere in the right region.
    shelf = [
        f
        for f in shell.Faces
        if isinstance(f.Surface, Part.Plane)
        and abs(f.Surface.Axis.z) > 0.999
        and abs(f.CenterOfMass.z - PCB_TOP) < 0.01
    ]
    if not shelf:
        fails.append(f"no horizontal face at the board top {PCB_TOP:.2f}: shelf missing")
    elif sum(f.Area for f in shelf) < 800.0:
        fails.append(f"shelf plus boss ends only {sum(f.Area for f in shelf):.0f} mm2, expected a perimeter shelf")

    for name, s in (("shell", shell), ("plate", plate)):
        got = collections.Counter(round(f.Surface.Radius, 2) for f in s.Faces if isinstance(f.Surface, Part.Cylinder))
        want = dict(EXPECT_CYL[name])
        if name == "shell":
            want[CNC_FILLET_R] = 4 * keys  # each cutout and each recess
            want[round(USB_H / 2, 2)] = want.get(round(USB_H / 2, 2), 0) + 2  # the USB slot's ends
            # Each edge fillet is a cylinder along every straight run of its face's outer
            # wire, and a torus round each arc.
            runs = sum(
                isinstance(e.Curve, Part.Line) for f in (top_face(s), rim_face(s)) if f for e in f.OuterWire.Edges
            )
            want[round(EDGE_FILLET, 2)] = want.get(round(EDGE_FILLET, 2), 0) + runs
        for r, n in sorted(want.items()):
            if got.get(r, 0) != n:
                fails.append(f"{name} r={r:.2f} cylinders: {got.get(r, 0)}, expected {n}")
        if os.environ.get("FC_SHOW_CYL"):
            print(f"  note {name}: cylinders {dict(sorted(got.items()))}")

    tops = [
        f
        for f in shell.Faces
        if isinstance(f.Surface, Part.Plane) and abs(f.Surface.Axis.z) > 0.999 and abs(f.CenterOfMass.z) < 1e-6
    ]
    if not tops:
        fails.append("no top face at z=0")
    else:
        tb = max(tops, key=lambda f: f.Area).BoundBox
        if abs((bb.XLength - tb.XLength) - 2 * EDGE_FILLET) > 0.01:
            fails.append(
                f"top face is {bb.XLength - tb.XLength:.3f} narrower than the widest section, expected "
                f"{2 * EDGE_FILLET:.3f}: top edge fillet wrong or missing"
            )

    # Prismatic features are invisible to a cylinder census, so test them by volume: a
    # perimeter wall built across a port opening leaves every count above unchanged.
    sign = 1 if half == "left" else -1
    dz = -explode

    for name, tool in (
        ("USB opening", usb_slot(sign, dz)),
        (
            "TRRS bore",
            Part.makeCylinder(
                TRRS_R,
                40.0,
                Vector(sign * TRRS_X, TRRS_Y - 20.0, TRRS_Z + dz),
                Vector(0, 1, 0),
            ),
        ),
    ):
        v = plate.common(tool).Volume
        if v > 1e-6:
            fails.append(f"plate obstructs the {name} by {v:.3f} mm3")

    # Every bumper must leave the SAME material behind. A floor at constant z in a plate
    # that is not leaves a different thickness at each edge of every foot, and the solid is
    # closed, correctly sized and correctly counted either way.
    for bx, by in BUMPERS:
        x = sign * bx
        got = []
        for dx, dy in (
            (-0.7 * BUMPER_R, 0.0),
            (0.7 * BUMPER_R, 0.0),
            (0.0, -0.7 * BUMPER_R),
            (0.0, 0.7 * BUMPER_R),
        ):
            probe = Part.makeCylinder(0.04, 4 * BIG, Vector(x + dx, by + dy, -2 * BIG), Vector(0, 0, 1))
            got.append(plate.common(probe).Volume / (math.pi * 0.04**2))
        if max(got) - min(got) > 0.005:
            fails.append(
                f"bumper recess at ({x:.2f}, {by:.2f}) leaves {min(got):.3f} to {max(got):.3f} mm of plate "
                "across its width: the floor is not parallel to the plate"
            )
        elif abs(got[0] - (PLATE - BUMPER_D)) > 0.01:
            fails.append(
                f"bumper recess at ({x:.2f}, {by:.2f}) leaves {got[0]:.3f} mm of plate, expected {PLATE - BUMPER_D:.3f}"
            )

    bores = sorted(
        round(f.BoundBox.ZLength, 2)
        for f in shell.Faces
        if isinstance(f.Surface, Part.Cylinder) and abs(f.Surface.Radius - BORE_R) < 1e-3
    )
    if bores != [BORE_DEPTH] * 3:
        fails.append(f"insert bore depths {bores}, expected {[BORE_DEPTH] * 3}")
    return fails


# ---- comparison against a hand-modelled case ------------------------------
def load_diffs(path, half):
    """The recorded intentional differences for one half.

    Only intentional differences are recorded. A difference resolved by moving the model to
    the reference, or fixed as an error, leaves nothing to record.
    """
    if not Path(path).exists():
        raise SystemExit(f"FAIL gen-case: {path}: no such file")
    entries = json.loads(Path(path).read_text()).get("differences")
    if not isinstance(entries, list):
        raise SystemExit(f'FAIL gen-case: {path}: expected {{"differences": [...]}}')
    for i, e in enumerate(entries):
        box = e.get("box")
        ok = (
            e.get("half") in ("left", "right")
            and e.get("part") in ("shell", "plate")
            and e.get("kind") in ("extra", "missing")
            and isinstance(box, list)
            and len(box) == 6
            and all(isinstance(v, (int, float)) for v in box)
            and all(box[k] < box[k + 3] for k in range(3))
            and isinstance(e.get("reason"), str)
            and e["reason"].strip()
        )
        if not ok:
            raise SystemExit(
                f"FAIL gen-case: {path}: entry {i} needs half (left|right), part "
                "(shell|plate), kind (extra|missing), box [xmin, ymin, zmin, xmax, ymax, zmax] "
                "and a non-empty reason"
            )
    return [e for e in entries if e["half"] == half]


def read_parts(paths, centre_x=0.0):
    """Shell and plate from one or more STEP files, told apart by volume as check() does.

    Two solids are one half. Four are both halves side by side, as one Part Studio built
    from the whole DXF holds them; the pair whose centre is nearest centre_x is returned.
    """
    solids = []
    for p in paths:
        if not Path(p).exists():
            raise SystemExit(f"FAIL gen-case: {p}: no such file")
        shp = Part.Shape()
        shp.read(p)
        solids += shp.Solids
    if len(solids) == 4:
        by_x = sorted(solids, key=lambda s: s.BoundBox.Center.x)
        pairs = [by_x[:2], by_x[2:]]
        solids = min(pairs, key=lambda pair: abs(pair[0].BoundBox.Center.x - centre_x))
    elif len(solids) != 2:
        raise SystemExit(
            f"FAIL gen-case: {', '.join(paths)} hold {len(solids)} solid(s), expected 2 (one "
            "half's shell and plate, assembled) or 4 (both halves)"
        )
    shell, plate = sorted(solids, key=lambda s: -s.Volume)
    return {"shell": shell, "plate": plate}


def half_spacing(dxf):
    """How far the right half's outline centre sits from the left's in the DXF."""
    (lx, ly), (rx, ry) = (centre_xy(classify(dxf, h)[0]) for h in ("left", "right"))
    return rx - lx, ry - ly


def regions(shape):
    """The solids of a Boolean residual that are geometry rather than kernel noise."""
    return [
        s
        for s in shape.Solids
        if s.Volume >= COMPARE_MIN_VOL and s.Area > 0 and 2 * s.Volume / s.Area >= COMPARE_MIN_THICK
    ]


def inside(bb, box):
    lo = (bb.XMin, bb.YMin, bb.ZMin)
    hi = (bb.XMax, bb.YMax, bb.ZMax)
    return all(lo[k] >= box[k] - MATCH_TOL and hi[k] <= box[k + 3] + MATCH_TOL for k in range(3))


def residuals(model, ref):
    """model - ref and ref - model, at the first fuzz OCC computes them sanely with.

    A fuzzy Boolean between two nearly coincident solids can fail without raising: it
    hands back the whole operand, a negative volume, an invalid shape, or plausible-looking
    debris; which fuzz it fails at depends on the geometry. A sound pair is valid, neither
    residual is negative or most of a part whose frame already matches, and the two account
    for the volume difference: extra - missing = model - ref, give or take what the fuzz
    absorbs, at most its width over the part's whole surface. Anything else is a failed
    Boolean, and the next fuzz is tried.
    """
    for fuzz in COMPARE_FUZZES:
        try:
            extra = model.cut(ref, fuzz) if fuzz else model.cut(ref)
            missing = ref.cut(model, fuzz) if fuzz else ref.cut(model)
            sound = (
                extra.isValid()
                and missing.isValid()
                and all(0 <= r.Volume <= 0.5 * whole.Volume for r, whole in ((extra, model), (missing, ref)))
            )
            balance = abs((extra.Volume - missing.Volume) - (model.Volume - ref.Volume))
        except Part.OCCError:
            continue
        if sound and balance <= max(COMPARE_MIN_VOL * 100, fuzz * max(model.Area, ref.Area)):
            return extra, missing
    raise SystemExit(f"FAIL gen-case: the comparison Boolean failed at every fuzz in {COMPARE_FUZZES}")


def compare(ref_path, model_paths, half, diffs_path, spacing):
    """Report every region where the hand model and the reference differ.

    "extra" is material in the model that the reference lacks, "missing" the reverse. Each
    region is matched against the recorded intentional differences; an unrecorded region is
    a decision still to make, and a record matching nothing is stale. Both fail.

    A right half may sit at its own outline centre or where the DXF places it beside the
    left half, `spacing` away; the second is moved back onto the first before comparing.
    """
    entries = load_diffs(diffs_path, half)
    ref = read_parts([ref_path])
    model = read_parts(model_paths, spacing[0] if half == "right" else 0.0)
    subject = ", ".join(model_paths)
    if half == "right":
        c = model["shell"].BoundBox.Center
        if abs(c.x - spacing[0]) < FRAME_TOL and abs(c.y - spacing[1]) < FRAME_TOL:
            for name in ("shell", "plate"):
                model[name] = model[name].copy()
                model[name].translate(Vector(-spacing[0], -spacing[1], 0))
            print(f"  note {subject}: right half at the DXF's placement, moved ({-spacing[0]:.4f}, {-spacing[1]:.4f})")

    for name in ("shell", "plate"):
        rc, mc = ref[name].BoundBox.Center, model[name].BoundBox.Center
        if max(abs(rc.x - mc.x), abs(rc.y - mc.y), abs(rc.z - mc.z)) > FRAME_TOL:
            raise SystemExit(
                f"FAIL gen-case: {subject}: {name} centred at ({mc.x:.2f}, {mc.y:.2f}, {mc.z:.2f}), "
                f"the reference at ({rc.x:.2f}, {rc.y:.2f}, {rc.z:.2f}). Export in millimetres, "
                "outline centre at the origin, z=0 at the top face, plate assembled"
            )

    used = set()
    mismatches, intentional = 0, 0
    for name in ("shell", "plate"):
        extra, missing = residuals(model[name], ref[name])
        for kind, residual in (("extra", extra), ("missing", missing)):
            for r in regions(residual):
                bb = r.BoundBox
                c = bb.Center
                where = (
                    f"{name}, {kind}: {r.Volume:.3f} mm3 at ({c.x:.2f}, {c.y:.2f}, {c.z:.2f}), "
                    f"{bb.XLength:.2f} x {bb.YLength:.2f} x {bb.ZLength:.2f}"
                )
                hit = [
                    i for i, e in enumerate(entries) if e["part"] == name and e["kind"] == kind and inside(bb, e["box"])
                ]
                if hit:
                    used.update(hit)
                    intentional += 1
                    print(f"  intentional {subject}: {where}: {entries[hit[0]]['reason']}")
                    continue
                mismatches += 1
                box = [
                    math.floor(bb.XMin * 10) / 10,
                    math.floor(bb.YMin * 10) / 10,
                    math.floor(bb.ZMin * 10) / 10,
                    math.ceil(bb.XMax * 10) / 10,
                    math.ceil(bb.YMax * 10) / 10,
                    math.ceil(bb.ZMax * 10) / 10,
                ]
                entry = {"half": half, "part": name, "kind": kind, "box": box, "reason": ""}
                sys.stdout.flush()
                print(f"  MISMATCH {subject}: {where}", file=sys.stderr)
                print(f"    to accept as intentional: {json.dumps(entry)}", file=sys.stderr)

    stale = [e for i, e in enumerate(entries) if i not in used]
    for e in stale:
        sys.stdout.flush()
        print(
            f"  FAIL {diffs_path}: {e['half']} {e['part']} {e['kind']} {e['box']} matches no difference: delete it",
            file=sys.stderr,
        )
    return mismatches, len(stale), intentional


def main():
    # USB_W is a stated width, so the invariant it has to satisfy is asserted rather than
    # guaranteed by construction. Nothing downstream would catch a violation: check() tests
    # the opening against the PLATE, never against the notch it has to sit inside.
    if USB_W > USB_X1 - USB_X0:
        raise SystemExit(
            f"FAIL gen-case: the {USB_W:.2f} USB opening is wider than the board's {USB_X1 - USB_X0:.2f} notch, so "
            "a plug would foul the board edge. Narrow USB_W, or widen the notch in "
            "config.yaml and move USB_X0/USB_X1 with it"
        )

    dxf = os.environ.get("FC_DXF", DEFAULT_DXF)
    outdir = os.environ.get("FC_OUTDIR", DEFAULT_OUTDIR)
    explode = float(os.environ.get("FC_EXPLODE", "0"))
    halves = os.environ.get("FC_HALF", "both")
    if halves not in ("left", "right", "both"):
        raise SystemExit(
            f"FAIL gen-case: FC_HALF={halves!r}, expected left, right or both. A typo "
            "would otherwise write the wrong half under the given name and "
            "still pass readback, the checks being mirror-symmetric"
        )
    compare_to = [p.strip() for p in os.environ.get("FC_COMPARE", "").split(",") if p.strip()]
    if compare_to and (halves == "both" or explode):
        raise SystemExit(
            "FAIL gen-case: FC_COMPARE takes one half's model, so it needs FC_HALF left or right and FC_EXPLODE unset"
        )
    halves = ["left", "right"] if halves == "both" else [halves]
    diffs = os.environ.get("FC_DIFFS", DEFAULT_DIFFS)
    # Checked before the build, which takes a minute.
    if compare_to:
        for p in compare_to:
            if not Path(p).exists():
                raise SystemExit(f"FAIL gen-case: {p}: no such file")
        load_diffs(diffs, halves[0])

    if not Path(dxf).exists():
        raise SystemExit(f"FAIL gen-case: {dxf}: no such file, run 'npm run ergogen' first")
    Path(outdir).mkdir(parents=True, exist_ok=True)

    bad = 0
    for half in halves:
        suffix = "-exploded" if explode else ""
        # str(): FreeCAD's Import.export takes a file name, not a Path.
        out = str(Path(outdir) / f"splinter-v4-{half}-case{suffix}.step")
        shell, plate, keys = build(dxf, half, explode)
        export(shell, plate, half, out)
        fails = check(out, half, explode, keys)
        if fails:
            bad += 1
            for f in fails:
                print(f"  FAIL {out}: {f}", file=sys.stderr)
        else:
            print(
                f"  wrote {out}: shell {len(shell.Faces)} faces, "
                f"plate {len(plate.Faces)} faces, "
                f"{Path(out).stat().st_size / 1024.0:.0f} KB"
            )
    sys.stdout.flush()
    if bad:
        raise SystemExit(f"FAIL gen-case: {bad} of {len(halves)} file(s) failed readback")
    if not compare_to:
        print(f"OK: gen-case: {len(halves)} case(s) written to {outdir} and verified on readback")
        return

    mismatches, stale, intentional = compare(out, compare_to, halves[0], diffs, half_spacing(dxf))
    sys.stdout.flush()
    if mismatches or stale:
        raise SystemExit(
            f"FAIL gen-case: {halves[0]} half: {mismatches} undecided difference(s), {stale} stale record(s) in {diffs}"
        )
    print(f"OK: gen-case: {halves[0]} half matches the reference, {intentional} intentional difference(s)")


# freecadcmd swallows an uncaught exception and still exits 0, so report and exit here.
try:
    main()
except SystemExit as e:
    if e.code:
        print(e.code, file=sys.stderr)
    sys.stdout.flush()
    sys.stderr.flush()
    os._exit(1 if e.code else 0)
except BaseException:  # noqa: BLE001  # the point: nothing may reach freecadcmd
    import traceback

    traceback.print_exc(file=sys.stderr)
    sys.stdout.flush()
    sys.stderr.flush()
    os._exit(1)
