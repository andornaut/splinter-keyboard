#!/usr/bin/env python3
"""Build the v4 case as solid geometry from BUILD.md's numbers and the un-filleted hull.

BUILD.md is the specification; this is its executable form. Every dimension here appears
there, and a change belongs in both.

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

Frame matches the build sheet: outline centre at the origin, z=0 at the shell's top face,
+z up, +x toward the inner (thick) edge. The right half is the exact mirror.
"""

import collections
import math
import os
import sys

for _p in ("/usr/lib/freecad-python3/lib", "/usr/lib/freecad/lib"):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import FreeCAD as App
import Part
from FreeCAD import Placement, Rotation, Vector

DEFAULT_DXF = "dist/v4/ergogen/outlines/full_unfilleted.dxf"
DEFAULT_OUTDIR = "dist/v4/onshape"

# ---- BUILD.md parameters -------------------------------------------------
WALL = 3.00
# Per side, on the hull. 0.50 rather than a machining fit: an FDM part loses 0.2-0.3% to
# XY shrink across 160mm and another 0.1-0.2 per wall to perimeter over-extrusion, which
# closes a tenth-millimetre pocket outright. It costs nothing on the milled variant, since
# the board is located by its screws either way (see USB_W).
POCKET_CLR = 0.50
TOP_THICK = 3.00
RECESS_Z = -1.50
PCB_TOP = -6.00
PCB_BOT = -7.60
H_INNER = 16.00
H_OUTER = 12.00
PLATE = 1.50
CAVITY_FILLET = 2.00  # tool radius; 3.20 is the maximum before it fouls the board
TOP_BEZEL = 1.00  # chamfer where the top face meets the outer wall
BOSS_R = 2.75
BORE_R = 1.80  # 3.60 dia heat-set insert
BORE_DEEP = 5.00  # outer pinky
BORE_SHALLOW = 4.00  # the two a switch recess overlaps
STANDOFF_R = 2.75
SCREW_R = 1.45  # 2.90 dia clearance
CBORE_R = 2.50  # 5.00 dia, flat-bottomed, for a flat-underside head
LID_CLR = 0.15
# The board is clamped around its whole perimeter, not only at the three bosses: a shelf
# hangs from the case's top and the plate carries a matching wall up to meet it. Both are
# measured in from the CAVITY, so what laps the board is the width less the clearance:
# SHELF_W - POCKET_CLR, and PLATE_WALL_W - (POCKET_CLR - LID_CLR). The lap is what has to
# stay inside the board's own perimeter keepout (add-keepout-zones.py PERIMETER_INSET) so
# neither lands on a ground plane, and it shrinks 1:1 with any loosening of POCKET_CLR.
# Tracks are a different matter: the ROUTE ring is carved open over the TRRS, so copper
# under soldermask is legal there and the shelf can cross it.
SHELF_W = 2.00
PLATE_WALL_W = 2.00
# The plate's wall clamps the board, so it has to stop wherever something hangs below the
# board or a plug comes in. All of that is in the top-inner corner: the MCU, the jack, the
# TVS and resistor, and both ports.
WALL_RELIEF_X = 50.00
WALL_RELIEF_Y = 45.00
# Flared standoff base. Without it the counterbore runs the plate's full thickness inside a
# 5.50 standoff, leaving the two joined by a 0.25mm annulus: the screw head would bear on
# the standoff and the plate would hang off 4.12 mm2 per boss. 8.00 matches the built v4
# lid. HEIGHT is what constrains a flare, not diameter: it stops below the hotswap sockets
# hanging under the board, and the pads it would otherwise have to dodge are all above it.
FLARE_R = 4.00
SOCKET_H = 1.85
SOCKET_CLR = 0.30

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
# through it. The USB clears an 8.34mm plug shell by 0.58 per side.

# One rectangular relief over everything tall on side B: the Liatris and the TRRS jack.
# Rectangular and continuous so a strip of tape can line it, rather than two pockets with
# an island between them.
#
# The margin around the parts is one-sided, and has to be. Inward it runs over bare board
# and carries enough that board registration play cannot leave a part standing over
# full-thickness plate. Outward there is nowhere to go: both parts run out to the board's
# own top edge and the plate ends barely past it. The outward limits are therefore set by
# the plate, not by the parts: +x stands off the perimeter wall, which still runs below
# WALL_RELIEF_Y and would be undercut by a pocket reaching its foot, and +y keeps a rim at
# the plate edge.
RELIEF_X0, RELIEF_X1 = 50.25, 77.60
RELIEF_Y0, RELIEF_Y1 = 23.35, 58.60
RELIEF_DEPTH = 0.75

# Bumper recesses cut the plate's OUTER face, so they never change the clearance above it.
# What they must not do is land inside the relief pocket, which cuts the inner face: the
# two together leave a membrane where the plate is thinnest, directly under the parts the
# relief exists for. Nothing fits between the relief and the plate edge in the top-inner
# corner, so the top-edge bumper sits inboard of the relief instead.
BUMPERS = [(-70.0, 50.0), (45.0, 50.0), (-70.0, -32.0), (65.0, -50.0)]
BUMPER_R, BUMPER_D = 4.00, 0.50

BIG = 500.0
EPS = 1e-6

# What reading the export back must find, keyed by cylinder radius. Catches a feature that
# silently stopped being cut as well as one that came out the wrong size. The 1.00 count is
# not listed because it is derived from the key field: 4 corner fillets on each cutout and
# 4 on each recess, and the halves carry different numbers of keys.
EXPECT_CYL = {
    # 1.80 x3: the insert bores. 2.00 x10: the cavity's five tool-radius corners and the
    # shelf's five. 2.75 x4: three bosses and the TRRS bore. 3.50 x5: the outer profile's
    # corners, the hull offset out by clearance plus wall. The lone 1.50 is where the
    # shelf's inset rounds the one concave hull corner, before the opening reaches it, so
    # it measures SHELF_W less the clearance.
    "shell": {1.50: 1, 1.80: 3, 2.00: 10, 2.75: 4, 3.50: 5},
    # 1.45 x3: the screw clearance holes. 1.85 x5: the plate outline, the cavity's 2.00
    # corners less the fit clearance, which is the point of deriving it from the cavity.
    # 2.00 x4 rather than x5: the plate wall's fifth inner corner falls inside the
    # top-inner relief. 2.50 x3: the flat counterbores. 2.75 x3: the standoffs, above
    # their flares. 4.00 x7: three flared bases and four bumper recesses, the same radius
    # by coincidence. The lone 1.65 is the plate wall's twin of the shell's 1.50, and the
    # 0.15 is the same concave corner on the plate outline, rounded by the fit clearance.
    "plate": {0.15: 1, 1.45: 3, 1.65: 1, 1.85: 5, 2.00: 4, 2.50: 3, 2.75: 3, 4.00: 7},
}
CNC_FILLET_R = 1.00
# Face area splitting a switch cutout from the recess above it. Only has to land between
# two widely separated clusters; what actually holds the split is the nesting check in
# classify(), which does not depend on where the threshold sits.
CUTOUT_RECESS_SPLIT = 230.0


# ---- DXF, as real edges --------------------------------------------------
def dxf_entities(path):
    """Group codes we care about, per LINE/ARC/CIRCLE entity."""
    with open(path) as fh:
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
            try:
                g[int(code)] = float(val)
            except ValueError:
                pass
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
    return moved(max(tops, key=lambda f: f.Area).OuterWire, Vector(0, 0, -1.0))


def check_bores(recess, bosses, depths):
    """Refuse an insert bore that reaches the recess band without clearing the recess wall.

    A bore whose top passes RECESS_Z runs alongside the recesses, and one passing within
    BORE_R of a recess wall opens through it. This is why two of the three bosses take the
    shallow bore, and it cannot be left to readback: a breakout trims the bore's
    cylindrical face without splitting it or changing its height, so both the face census
    and the depth check pass a shell that has one.
    """
    for (bx, by), depth in zip(bosses, depths):
        if PCB_TOP + depth <= RECESS_Z:
            continue
        v = Part.Vertex(bx, by, 0.0)
        d = min(w.distToShape(v)[0] for w in recess)
        if d < BORE_R:
            raise SystemExit(
                f"FAIL gen-case: the bore at ({bx:.3f}, {by:.3f}) reaches z {PCB_TOP + depth:.2f}, above the {RECESS_Z:.2f} "
                f"recess floor, and a recess wall is {d:.3f} from its axis against a {BORE_R:.2f} "
                "bore radius: it breaks out. This boss needs BORE_SHALLOW"
            )


def check_bumpers(sign):
    """Refuse a bumper recess that lands inside the relief pocket.

    The two cut opposite faces of the plate, so an overlap leaves a membrane, and leaves
    it directly under the parts the relief exists to clear. Readback cannot see it: both
    features are present, the right size and at the right depth, and the plate is still
    one closed solid.
    """
    rx0 = min(sign * RELIEF_X0, sign * RELIEF_X1)
    rx1 = max(sign * RELIEF_X0, sign * RELIEF_X1)
    for bx, by in BUMPERS:
        x = sign * bx
        d = math.hypot(max(rx0 - x, 0.0, x - rx1), max(RELIEF_Y0 - by, 0.0, by - RELIEF_Y1))
        if d < BUMPER_R:
            raise SystemExit(
                f"FAIL gen-case: the bumper recess at ({x:.3f}, {by:.3f}) reaches {BUMPER_R - d:.3f} into the "
                f"relief pocket, which cuts the other face: that leaves {PLATE - RELIEF_DEPTH - BUMPER_D:.2f}mm of plate "
                "under the parts the relief is there for. Move it clear of the pocket"
            )


def bezel_top(body, size):
    """Chamfer where the top face meets the outer wall.

    Only the top face's OUTER wire: its inner wires are the switch recesses, which are
    meant to stay square.
    """
    tops = [
        f
        for f in body.Faces
        if isinstance(f.Surface, Part.Plane) and abs(f.Surface.Axis.z) > 0.999 and abs(f.CenterOfMass.z) < 1e-6
    ]
    if not tops:
        raise SystemExit("FAIL gen-case: no top face to bezel")
    return body.makeChamfer(size, max(tops, key=lambda f: f.Area).OuterWire.Edges)


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
    outer_w = offset(hull, POCKET_CLR + WALL)
    cavity_w = opened(offset(hull, POCKET_CLR), CAVITY_FILLET)
    # The plate follows the cavity, so its corners match the pocket it drops into rather
    # than carrying the hull's own tight radii. LID_CLR is well under CAVITY_FILLET, so the
    # corners survive as arcs.
    plate_w = offset(cavity_w, -LID_CLR)
    # The shelf and the plate wall are insets of the HULL, each opened in its own right.
    # Chaining them off cavity_w would offset inward by exactly CAVITY_FILLET, collapsing
    # its corner arcs to zero radius, which OCC rejects outright.
    shelf_w = opened(offset(hull, POCKET_CLR - SHELF_W), CAVITY_FILLET)
    plate_wall_w = opened(offset(hull, POCKET_CLR - LID_CLR - PLATE_WALL_W), CAVITY_FILLET)

    # Only the outer pinky boss takes the deep bore: a 16.00 switch recess overlaps the
    # other two, leaving 4.50 of material there instead of 6.00.
    outer_i = min(range(len(bosses)), key=lambda i: sign * bosses[i][0])
    depths = [BORE_DEEP if i == outer_i else BORE_SHALLOW for i in range(len(bosses))]
    check_bores(recess, bosses, depths)
    check_bumpers(sign)

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
    ux = sign * (USB_X0 + USB_X1) / 2.0
    body = body.cut(Part.makeBox(USB_W, 40.0, USB_H, Vector(ux - USB_W / 2, TRRS_Y - 20.0, USB_Z - USB_H / 2)))

    # Perimeter shelf: the board is pressed up against its underside. This narrows the
    # opening going up, which is the legal direction; a lip the board RESTS on would widen
    # going up and no setup could reach it.
    body = body.fuse(prism(cavity_w, PCB_TOP, -TOP_THICK).cut(prism(shelf_w, PCB_TOP - 1.0, -TOP_THICK + 1.0)))

    for bx, by in bosses:
        body = body.fuse(cyl(BOSS_R, PCB_TOP, -TOP_THICK, bx, by))
    body = body.removeSplitter()

    for (bx, by), depth in zip(bosses, depths):
        body = body.cut(cyl(BORE_R, PCB_TOP, PCB_TOP + depth, bx, by))
    shell = bezel_top(body.removeSplitter(), TOP_BEZEL)

    # --- plate
    slab = half_space(sign, ang, PLATE).cut(half_space(sign, ang, 0.0))
    plate = prism(plate_w, -BIG, BIG).common(slab)
    # Perimeter wall, rising to the board's underside so the board is sandwiched between it
    # and the shelf above. Built from the plate's top face up, so relieving it cannot bite
    # into the plate itself, and stopped short of the top-inner corner where the tall parts
    # and both ports are.
    ring = (
        prism(plate_w, -BIG, PCB_BOT)
        .cut(prism(plate_wall_w, -BIG - 1.0, PCB_BOT + 1.0))
        .cut(half_space(sign, ang, PLATE))
    )
    rx0 = min(sign * WALL_RELIEF_X, sign * BIG)
    rx1 = max(sign * WALL_RELIEF_X, sign * BIG)
    ring = ring.cut(Part.makeBox(rx1 - rx0, BIG, 2 * BIG, Vector(rx0, WALL_RELIEF_Y, -BIG)))
    plate = plate.fuse(ring)
    for bx, by in bosses:
        plate = plate.fuse(cyl(STANDOFF_R, -BIG, PCB_BOT, bx, by).cut(half_space(sign, ang, 0.0)))
        plate = plate.fuse(cyl(FLARE_R, -BIG, PCB_BOT - SOCKET_H - SOCKET_CLR, bx, by).cut(half_space(sign, ang, 0.0)))
    plate = plate.removeSplitter()

    # Relief over the Liatris and the jack. Without it an aluminium plate sits 0.77mm from
    # the module's pin tails, or 0.03mm if it bottoms out in its sockets.
    x0 = sign * RELIEF_X0 if sign > 0 else sign * RELIEF_X1
    # Spans the full z range: the plate sits well below z=0, so a box starting there
    # intersects the relief slab in nothing and the cut silently does nothing.
    relief = Part.makeBox(
        RELIEF_X1 - RELIEF_X0,
        RELIEF_Y1 - RELIEF_Y0,
        2 * BIG,
        Vector(x0, RELIEF_Y0, -BIG),
    ).common(half_space(sign, ang, PLATE).cut(half_space(sign, ang, PLATE - RELIEF_DEPTH)))
    if relief.Volume < 1.0:
        raise SystemExit("FAIL gen-case: MCU relief tool is empty, it would cut nothing")
    # The pocket must not reach under the perimeter wall. The wall is half the board's
    # clamp and it stands on the plate's full thickness, so a pocket at its foot thins the
    # root. Tested as a footprint overlap, not a solid one: the wall rises FROM the plate's
    # top face and the pocket cuts down from it, so the two touch without ever sharing
    # volume, and an intersection test would read clean while the undercut is real.
    column = Part.makeBox(
        RELIEF_X1 - RELIEF_X0,
        RELIEF_Y1 - RELIEF_Y0,
        2 * BIG,
        Vector(x0, RELIEF_Y0, -BIG),
    )
    undercut = ring.common(column).Volume
    if undercut > EPS:
        raise SystemExit(
            "FAIL gen-case: the relief pocket reaches under the plate's perimeter wall, "
            f"undercutting {undercut:.3f} mm3 of it. Pull the pocket back inside the wall relief"
        )
    plate = plate.cut(relief)

    # Flat-bottomed counterbore, not a countersink: the screw has a flat head underside. It
    # runs the plate's full thickness and bears on the flare's base, so the standoff keeps
    # its full height and the flare still joins the plate over a 1.00mm annulus.
    #
    # Its floor is HORIZONTAL, alone among the features cut into this plate. The screw axis
    # is vertical and a flat head seats square to its own axis, so the seat has to be
    # perpendicular to the screw rather than parallel to the tilted plate. The price is a
    # counterbore whose depth below the outer face varies across its width, which is the
    # right trade here and the wrong one for the bumpers below.
    for bx, by in bosses:
        plate = plate.cut(cyl(SCREW_R, -BIG, BIG, bx, by))
        z = rim_z(sign, bx)
        plate = plate.cut(cyl(CBORE_R, z - 0.5, z + PLATE, bx, by))
    # A bumper recess is a fixed removal, so its floor is PARALLEL to the plate faces and
    # every foot leaves the same material behind. A horizontal floor would be a constant z
    # in a plate that is not, making the recess shallower at one edge than the other and
    # leaving a different thickness at each. A stuck-on foot has no axis wanting a
    # horizontal seat, so the plate wins: bounded by two slope-parallel planes, exactly as
    # the relief pocket is.
    skin = half_space(sign, ang, BUMPER_D).cut(half_space(sign, ang, 0.0))
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
    import Import

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

    bb = shell.BoundBox
    for lbl, got, want in (
        ("width", bb.XLength, 160.0 + 2 * (POCKET_CLR + WALL)),
        ("depth", bb.YLength, 119.0 + 2 * (POCKET_CLR + WALL)),
        ("height", bb.ZLength, H_INNER),
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
        if abs((bb.XLength - tb.XLength) - 2 * TOP_BEZEL) > 0.01:
            fails.append(
                f"top face is {bb.XLength - tb.XLength:.3f} narrower than the widest section, expected "
                f"{2 * TOP_BEZEL:.3f}: bezel wrong or missing"
            )

    # Prismatic features are invisible to a cylinder census, so test them by volume. Both
    # of these have failed silently: a relief box that missed the plate entirely, and a
    # perimeter wall built across both port openings.
    sign = 1 if half == "left" else -1
    dz = -explode
    relief_zone = Part.makeBox(
        RELIEF_X1 - RELIEF_X0,
        RELIEF_Y1 - RELIEF_Y0,
        RELIEF_DEPTH,
        Vector(
            sign * RELIEF_X0 if sign > 0 else sign * RELIEF_X1,
            RELIEF_Y0,
            plate.BoundBox.ZMin,
        ),
    )
    swept = 0.0
    for i in range(60):
        probe = relief_zone.copy()
        probe.translate(Vector(0, 0, i * 0.15))
        swept += plate.common(probe).Volume
    if swept > 0.999 * relief_zone.Volume * 60:
        fails.append("relief pocket absent: plate is solid through its footprint")

    ux = sign * (USB_X0 + USB_X1) / 2.0
    for name, tool in (
        (
            "USB opening",
            Part.makeBox(
                USB_W,
                40.0,
                USB_H,
                Vector(ux - USB_W / 2, TRRS_Y - 20.0, USB_Z - USB_H / 2 + dz),
            ),
        ),
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
    if bores != [BORE_SHALLOW, BORE_SHALLOW, BORE_DEEP]:
        fails.append(f"insert bore depths {bores}, expected {[BORE_SHALLOW, BORE_SHALLOW, BORE_DEEP]}")
    return fails


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
    halves = ["left", "right"] if halves == "both" else [halves]

    if not os.path.exists(dxf):
        raise SystemExit(f"FAIL gen-case: {dxf}: no such file, run 'npm run ergogen' first")
    os.makedirs(outdir, exist_ok=True)

    bad = 0
    for half in halves:
        suffix = "-exploded" if explode else ""
        out = os.path.join(outdir, f"splinter-v4-{half}-case{suffix}.step")
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
                f"{os.path.getsize(out) / 1024.0:.0f} KB"
            )
    sys.stdout.flush()
    if bad:
        raise SystemExit(f"FAIL gen-case: {bad} of {len(halves)} file(s) failed readback")
    print(f"OK: gen-case: {len(halves)} case(s) written to {outdir} and verified on readback")


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
