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

import FreeCAD as App  # noqa: E402
import Part  # noqa: E402
from FreeCAD import Placement, Rotation, Vector  # noqa: E402

DEFAULT_DXF = "dist/v4/ergogen/outlines/full_unfilleted.dxf"
DEFAULT_OUTDIR = "dist/v4/onshape"

# ---- BUILD.md parameters -------------------------------------------------
WALL          = 3.00
POCKET_CLR    = 0.25
TOP_THICK     = 3.00
RECESS_Z      = -1.50
PCB_TOP       = -6.00
PCB_BOT       = -7.60
H_INNER       = 16.00
H_OUTER       = 12.00
PLATE         = 1.50
CAVITY_FILLET = 2.00     # tool radius; 2.35 is the maximum before it fouls the board
BOSS_R        = 2.75
BORE_R        = 1.80     # 3.60 dia heat-set insert
BORE_DEEP     = 5.00     # outer pinky
BORE_SHALLOW  = 4.00     # the two a switch recess overlaps
STANDOFF_R    = 2.75
SCREW_R       = 1.45     # 2.90 dia clearance
CBORE_R       = 2.50     # 5.00 dia, flat-bottomed, for a flat-underside head
LID_CLR       = 0.15
# The board is clamped around its whole perimeter, not only at the three bosses: a shelf
# hangs from the case's top and the plate carries a matching wall up to meet it. 2.00 is
# the board's own perimeter keepout (add-keepout-zones.py PERIMETER_INSET), so neither
# lands on a ground plane. Tracks are a different matter: the ROUTE ring is carved open
# over the TRRS, so copper under soldermask is legal there and the shelf can cross it.
SHELF_W       = 2.00
PLATE_WALL_W  = 2.00
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
FLARE_R       = 4.00
SOCKET_H      = 1.85
SOCKET_CLR    = 0.30

# Port heights are MEASURED off the built v4 case, which shares this z stack exactly (top
# face 0, top underside -3.00, PCB -6.00 to -7.60). They are not derived from the part
# stack; a derivation put both too high, the USB by 0.65.
TRRS_X, TRRS_Y = 74.650, 59.500
TRRS_Z, TRRS_R = -10.50, 2.75
USB_X0, USB_X1 = 56.663, 66.663
USB_Z, USB_H = -10.75, 4.00
# Both ports are plain cutouts straight through the wall. No counterbore and no recess: a
# pocket on the outer face reads as the port being sunk into the case rather than opened
# through it. The USB width sits inside the board's own 10.00 notch so the plug clears the
# board edge, and clears an 8.34mm plug shell by 0.58 per side.

# One rectangular relief over everything tall on side B: the Liatris and the TRRS jack.
# Rectangular and continuous so a strip of tape can line it, rather than two pockets with
# an island between them. Bounded by the plate's perimeter wall at x 78.10 (below y 45,
# where the wall still runs) and held clear of the plate's own edge.
RELIEF_X0, RELIEF_X1 = 51.75, 77.60
RELIEF_Y0, RELIEF_Y1 = 25.35, 58.60
RELIEF_DEPTH = 0.75

BUMPERS = [(-70.0, 50.0), (70.0, 50.0), (-70.0, -32.0), (65.0, -50.0)]
BUMPER_R, BUMPER_D = 4.00, 0.50

BIG = 500.0
EPS = 1e-6

# What reading the export back must find, keyed by cylinder radius. Catches a feature that
# silently stopped being cut as well as one that came out the wrong size. The 1.00 count is
# not listed because it is derived from the key field: 4 corner fillets on each cutout and
# 4 on each recess, and the halves carry different numbers of keys.
EXPECT_CYL = {
    # 2.00 x10: the cavity's five tool-radius corners and the shelf's five. 2.75 x4: three
    # bosses and the TRRS bore. The lone 1.75 is where the shelf's inset rounds a concave
    # hull corner.
    "shell": {1.75: 1, 1.80: 3, 2.00: 10, 2.75: 4, 3.25: 5},
    # 1.85 x5: the plate outline, the cavity's 2.00 corners less the fit clearance, which
    # is the point of deriving it from the cavity. 2.50 x3: the flat counterbores. 3.50 x3:
    # 4.00 x7: four bumper recesses and three flared standoff bases, same radius by
    # coincidence. 2.00 x4 rather than x5: the wall's fifth inner corner falls
    # inside the top-inner relief.
    "plate": {0.15: 1, 1.45: 3, 1.85: 5, 1.90: 1, 2.00: 4, 2.50: 3, 2.75: 3,
              4.00: 7},
}
CNC_FILLET_R = 1.00


# ---- DXF, as real edges --------------------------------------------------
def dxf_entities(path):
    """Group codes we care about, per LINE/ARC/CIRCLE entity."""
    lines = open(path).read().splitlines()
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
    except Exception:
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
            "FAIL gen-case: found %d boss circle(s) of radius %.2f, expected 3. If "
            "screw_boss_radius changed in config.yaml, BOSS_R must follow"
            % (len(bosses), BOSS_R))
    return (wall,
            [w for w in rest if face_area(w) < 230.0],
            [w for w in rest if face_area(w) >= 230.0],
            bosses)


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
        except Exception:
            continue        # the wrong sign can throw outright, not just come back wrong
        if (a.BoundBox.XLength > wire.BoundBox.XLength) == (dist > 0):
            return a
    raise SystemExit("FAIL gen-case: no offset of %+.3f produced an outline" % dist)


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
    box.Placement = Placement(Vector(0, 0, rim_z(sign, 0.0) + up),
                              Rotation(Vector(0, 1, 0), sign * ang))
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
    fill = Part.Face(Part.makePolygon([
        Vector(ux0, ty - 12.0, 0), Vector(ux1, ty - 12.0, 0),
        Vector(ux1, ty, 0), Vector(ux0, ty, 0), Vector(ux0, ty - 12.0, 0)]))
    # Fuse as solids and read the top face back: fusing two coplanar FACES leaves the union
    # split into pieces that removeSplitter will not merge, and picking one of them yields
    # a fragment rather than the hull.
    merged = Part.Face(wall).extrude(Vector(0, 0, 1.0)).fuse(
        fill.extrude(Vector(0, 0, 1.0))).removeSplitter()
    tops = [f for f in merged.Faces
            if isinstance(f.Surface, Part.Plane)
            and abs(f.Surface.Axis.z) > 0.999
            and abs(f.CenterOfMass.z - 1.0) < 1e-6]
    return moved(max(tops, key=lambda f: f.Area).OuterWire, Vector(0, 0, -1.0))


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

    # --- shell
    body = prism(outer_w, -BIG, 0.0).cut(half_space(sign, ang, 0.0))
    body = body.cut(prism(cavity_w, -BIG, -TOP_THICK))
    for w in recess:
        body = body.cut(prism(w, RECESS_Z, 1.0))
    for w in holes:
        body = body.cut(prism(w, -BIG, 1.0))

    # Ports overshoot the outer face on both sides, so no cut face lands coplanar with a
    # shell face, which would leave the solid non-manifold.
    body = body.cut(Part.makeCylinder(
        TRRS_R, 40.0, Vector(sign * TRRS_X, TRRS_Y - 20.0, TRRS_Z), Vector(0, 1, 0)))
    usb_w = (USB_X1 - USB_X0) - 2 * POCKET_CLR
    ux = sign * (USB_X0 + USB_X1) / 2.0
    body = body.cut(Part.makeBox(
        usb_w, 40.0, USB_H, Vector(ux - usb_w / 2, TRRS_Y - 20.0, USB_Z - USB_H / 2)))

    # Perimeter shelf: the board is pressed up against its underside. This narrows the
    # opening going up, which is the legal direction; a lip the board RESTS on would widen
    # going up and no setup could reach it.
    body = body.fuse(prism(cavity_w, PCB_TOP, -TOP_THICK).cut(
        prism(shelf_w, PCB_TOP - 1.0, -TOP_THICK + 1.0)))

    for bx, by in bosses:
        body = body.fuse(cyl(BOSS_R, PCB_TOP, -TOP_THICK, bx, by))
    body = body.removeSplitter()

    for i, (bx, by) in enumerate(bosses):
        body = body.cut(cyl(BORE_R, PCB_TOP, PCB_TOP +
                            (BORE_DEEP if i == outer_i else BORE_SHALLOW), bx, by))
    shell = body.removeSplitter()

    # --- plate
    slab = half_space(sign, ang, PLATE).cut(half_space(sign, ang, 0.0))
    plate = prism(plate_w, -BIG, BIG).common(slab)
    # Perimeter wall, rising to the board's underside so the board is sandwiched between it
    # and the shelf above. Built from the plate's top face up, so relieving it cannot bite
    # into the plate itself, and stopped short of the top-inner corner where the tall parts
    # and both ports are.
    ring = (prism(plate_w, -BIG, PCB_BOT)
            .cut(prism(plate_wall_w, -BIG - 1.0, PCB_BOT + 1.0))
            .cut(half_space(sign, ang, PLATE)))
    rx0 = min(sign * WALL_RELIEF_X, sign * BIG)
    rx1 = max(sign * WALL_RELIEF_X, sign * BIG)
    ring = ring.cut(Part.makeBox(rx1 - rx0, BIG, 2 * BIG,
                                 Vector(rx0, WALL_RELIEF_Y, -BIG)))
    plate = plate.fuse(ring)
    for bx, by in bosses:
        plate = plate.fuse(cyl(STANDOFF_R, -BIG, PCB_BOT, bx, by).cut(
            half_space(sign, ang, 0.0)))
        plate = plate.fuse(cyl(FLARE_R, -BIG, PCB_BOT - SOCKET_H - SOCKET_CLR,
                                bx, by).cut(
            half_space(sign, ang, 0.0)))
    plate = plate.removeSplitter()

    # Relief over the Liatris and the jack. Without it an aluminium plate sits 0.77mm from
    # the module's pin tails, or 0.03mm if it bottoms out in its sockets.
    x0 = sign * RELIEF_X0 if sign > 0 else sign * RELIEF_X1
    # Spans the full z range: the plate sits well below z=0, so a box starting there
    # intersects the relief slab in nothing and the cut silently does nothing.
    relief = Part.makeBox(RELIEF_X1 - RELIEF_X0, RELIEF_Y1 - RELIEF_Y0, 2 * BIG,
                          Vector(x0, RELIEF_Y0, -BIG)).common(
        half_space(sign, ang, PLATE).cut(
            half_space(sign, ang, PLATE - RELIEF_DEPTH)))
    if relief.Volume < 1.0:
        raise SystemExit("FAIL gen-case: MCU relief tool is empty, it would cut nothing")
    plate = plate.cut(relief)

    # Flat-bottomed counterbore, not a countersink: the screw has a flat head underside. It
    # runs the plate's full thickness and bears on the flare's base, so the standoff keeps
    # its full height and the flare still joins the plate over a 1.00mm annulus.
    for bx, by in bosses:
        plate = plate.cut(cyl(SCREW_R, -BIG, BIG, bx, by))
        z = rim_z(sign, bx)
        plate = plate.cut(cyl(CBORE_R, z - 0.5, z + PLATE, bx, by))
    for bx, by in BUMPERS:
        x = sign * bx
        z = rim_z(sign, x)
        plate = plate.cut(cyl(BUMPER_R, z - 0.5, z + BUMPER_D, x, by))
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
        o.Label = "splinter_v4_%s_%s" % (half, name)
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
        fails.append("expected 2 solids, found %d" % len(shp.Solids))
        return fails
    shell, plate = sorted(shp.Solids, key=lambda s: -s.Volume)

    for name, s in (("shell", shell), ("plate", plate)):
        if not s.isValid():
            fails.append("%s is not a valid solid" % name)
        if not s.isClosed():
            fails.append("%s is not closed" % name)

    bb = shell.BoundBox
    for lbl, got, want in (("width", bb.XLength, 160.001 + 2 * (POCKET_CLR + WALL)),
                           ("depth", bb.YLength, 119.0 + 2 * (POCKET_CLR + WALL)),
                           ("height", bb.ZLength, H_INNER)):
        if abs(got - want) > 0.01:
            fails.append("shell %s %.3f, expected %.3f" % (lbl, got, want))

    if not explode and abs(plate.BoundBox.ZMax - PCB_BOT) > 0.01:
        fails.append("plate wall top %.3f, expected the board underside %.3f"
                     % (plate.BoundBox.ZMax, PCB_BOT))
    # The shelf's underside is what the board is clamped against, so it must be a real
    # horizontal face at the board's top, not merely somewhere in the right region.
    shelf = [f for f in shell.Faces
             if isinstance(f.Surface, Part.Plane) and abs(f.Surface.Axis.z) > 0.999
             and abs(f.CenterOfMass.z - PCB_TOP) < 0.01]
    if not shelf:
        fails.append("no horizontal face at the board top %.2f: shelf missing" % PCB_TOP)
    elif sum(f.Area for f in shelf) < 800.0:
        fails.append("shelf plus boss ends only %.0f mm2, expected a perimeter shelf"
                     % sum(f.Area for f in shelf))

    for name, s in (("shell", shell), ("plate", plate)):
        got = collections.Counter(round(f.Surface.Radius, 2) for f in s.Faces
                                  if isinstance(f.Surface, Part.Cylinder))
        want = dict(EXPECT_CYL[name])
        if name == "shell":
            want[CNC_FILLET_R] = 4 * keys      # each cutout and each recess
        for r, n in sorted(want.items()):
            if got.get(r, 0) != n:
                fails.append("%s r=%.2f cylinders: %d, expected %d"
                             % (name, r, got.get(r, 0), n))
        if os.environ.get("FC_SHOW_CYL"):
            print("  note %s: cylinders %s" % (name, dict(sorted(got.items()))))

    # Prismatic features are invisible to a cylinder census, so test them by volume. Both
    # of these have failed silently: a relief box that missed the plate entirely, and a
    # perimeter wall built across both port openings.
    sign = 1 if half == "left" else -1
    dz = -explode
    relief_zone = Part.makeBox(RELIEF_X1 - RELIEF_X0, RELIEF_Y1 - RELIEF_Y0, RELIEF_DEPTH,
                               Vector(sign * RELIEF_X0 if sign > 0 else sign * RELIEF_X1,
                                      RELIEF_Y0, plate.BoundBox.ZMin))
    swept = 0.0
    for i in range(60):
        probe = relief_zone.copy()
        probe.translate(Vector(0, 0, i * 0.15))
        swept += plate.common(probe).Volume
    if swept > 0.999 * relief_zone.Volume * 60:
        fails.append("relief pocket absent: plate is solid through its footprint")

    usb_w = (USB_X1 - USB_X0) - 2 * POCKET_CLR
    ux = sign * (USB_X0 + USB_X1) / 2.0
    for name, tool in (
            ("USB opening", Part.makeBox(usb_w, 40.0, USB_H,
                                         Vector(ux - usb_w / 2, TRRS_Y - 20.0,
                                                USB_Z - USB_H / 2 + dz))),
            ("TRRS bore", Part.makeCylinder(
                TRRS_R, 40.0, Vector(sign * TRRS_X, TRRS_Y - 20.0, TRRS_Z + dz),
                Vector(0, 1, 0)))):
        v = plate.common(tool).Volume
        if v > 1e-6:
            fails.append("plate obstructs the %s by %.3f mm3" % (name, v))

    bores = sorted(round(f.BoundBox.ZLength, 2) for f in shell.Faces
                   if isinstance(f.Surface, Part.Cylinder)
                   and abs(f.Surface.Radius - BORE_R) < 1e-3)
    if bores != [BORE_SHALLOW, BORE_SHALLOW, BORE_DEEP]:
        fails.append("insert bore depths %s, expected %s"
                     % (bores, [BORE_SHALLOW, BORE_SHALLOW, BORE_DEEP]))
    return fails


def main():
    dxf = os.environ.get("FC_DXF", DEFAULT_DXF)
    outdir = os.environ.get("FC_OUTDIR", DEFAULT_OUTDIR)
    explode = float(os.environ.get("FC_EXPLODE", "0"))
    halves = os.environ.get("FC_HALF", "both")
    if halves not in ("left", "right", "both"):
        raise SystemExit("FAIL gen-case: FC_HALF=%r, expected left, right or both. A typo "
                         "would otherwise write the wrong half under the given name and "
                         "still pass readback, the checks being mirror-symmetric" % halves)
    halves = ["left", "right"] if halves == "both" else [halves]

    if not os.path.exists(dxf):
        raise SystemExit("FAIL gen-case: %s: no such file, run 'npm run ergogen' first"
                         % dxf)
    os.makedirs(outdir, exist_ok=True)

    bad = 0
    for half in halves:
        suffix = "-exploded" if explode else ""
        out = os.path.join(outdir, "splinter-v4-%s-case%s.step" % (half, suffix))
        shell, plate, keys = build(dxf, half, explode)
        export(shell, plate, half, out)
        fails = check(out, half, explode, keys)
        if fails:
            bad += 1
            for f in fails:
                print("  FAIL %s: %s" % (out, f), file=sys.stderr)
        else:
            print("  wrote %s: shell %d faces, plate %d faces, %.0f KB"
                  % (out, len(shell.Faces), len(plate.Faces),
                     os.path.getsize(out) / 1024.0))
    sys.stdout.flush()
    if bad:
        raise SystemExit("FAIL gen-case: %d of %d file(s) failed readback"
                         % (bad, len(halves)))
    print("OK: gen-case: %d case(s) written to %s and verified on readback"
          % (len(halves), outdir))


# freecadcmd swallows an uncaught exception and still exits 0, so report and exit here.
try:
    main()
except SystemExit as e:
    if e.code:
        print(e.code, file=sys.stderr)
    sys.stdout.flush()
    sys.stderr.flush()
    os._exit(1 if e.code else 0)
except BaseException:
    import traceback
    traceback.print_exc(file=sys.stderr)
    sys.stdout.flush()
    sys.stderr.flush()
    os._exit(1)
