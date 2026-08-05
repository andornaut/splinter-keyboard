#!/usr/bin/env python3
"""Assert the two halves are exact mirror images: outline, parts, pads, zones, silk.

Everything the config generates must mirror. The one licensed exception is the keys
of the outer pinky columns, which differ by design (the left is 1.5u, the right is
1u plus the zones.extra inner column), and UNPAIRED_KEYS pins how many of those
there are so a mirrored key drifting cannot hide among them.

Nothing else sees this. Both halves are generated from one set of mirrored anchors,
and a shape re-anchored to one half's own keys drifts a fraction of a millimetre
while both halves still route, pass DRC, fab and assemble. It shows up as a case
that fits one half and rocks on the other, or a clearance that is comfortable on one
half and marginal on the other.

Two checks, and they measure different things:

OUTLINE. The two-sided Hausdorff distance between the Edge.Cuts outlines, i.e. the
worst gap in either direction, so a bulge on either half is caught. TOLERANCE is not
slack to spend: it covers KiCad's nanometre quantization and the sub-micron edge weld
in add-keepout-zones.py, both noise on a shape that is otherwise mirror-exact.

COMPONENTS. Every footprint pairs with one at the mirrored position, and its pads
land mirrored, pad name included. Pad NAMES, not just positions, because a two-pin
part rotated 180 leaves its pad positions unchanged and swaps which net sits at each
one, which is precisely the regression worth catching. Parts in
PINFIELD_NOT_MIRRORABLE are held to a weaker rule for a physical reason; see there.
Routing is not compared: it is drawn by hand per half, so the GND pour (whose layer
is scored per board) and the teardrops are skipped, and only rule areas are read.

Each half is compared in its own frame, translated to its own Edge.Cuts bounding-box
center before one is mirrored in x, so the per-board recentering recenter.py applies
is not mistaken for asymmetry. That frame is shared between the two checks and ties
them together: an outline difference moves a board's bbox center by about half of it
and so offsets every component on that half. The component check therefore runs only
once the outline mirrors within FP_TOLERANCE, because below that precision it would
report every part on the board as unpaired when the fault is one edge.

Active version comes from npm_package_config_VERSION, so run via npm:
  npm run validate:symmetry

By default both stages are checked; pass stage names to narrow it:
  validate-symmetry.py routed
"""
import argparse
import collections
import glob
import math
import os
import re
import sys

from lib.pcbnew_quiet import pcbnew
from lib.pipeline_log import note
from lib.stages import add_stage_argument, selected


MM = 1e6  # pcbnew internal units (nm) per mm

# Position agreement required of anything but the outline, in mm. Mirrored geometry
# comes out of Ergogen agreeing to nanometres, so this is quantization headroom and
# not a budget: it is both the pairing radius and the match test.
FP_TOLERANCE = 0.001

# Rotation agreement, in degrees, for the parts held to a mirrored orientation.
ROT_TOLERANCE = 0.01

# The per-key footprints. These are the only ones allowed to lack a counterpart on
# the other half, because the outer pinky columns differ by design (the left is 1.5u,
# the right is 1u plus the zones.extra inner column).
KEY_FOOTPRINTS = ("switch_mx", "diode_sod123")

# Parts placed in the same orientation on both halves rather than mirrored, so their
# pads land at mirrored POSITIONS but carry the opposite pin at each one. Held to the
# three things that can hold instead: mirrored placement, mirrored orientation, and
# the same set of pads.
#
# An MX switch's pins and the Kailh socket that receives them are physically
# asymmetric, so the mirror image of that pad pattern is not a part that exists. The
# matrix diode wires straight to a switch pin, so it follows the switch: mirroring the
# diode alone would leave it reaching across a pin field that did not move with it.
# The MCU is a module that plugs in one way up, so its pin 1 stays in its physical
# corner and the NETS swap columns instead (validate:firmware is what checks that).
#
# The common thread is a physical part, not a preference. Everything else on the board
# is held to landing its copper on the mirror line, and a two-pin part that needs a
# compensating rotation to do so carries one (see the TVS in config.yaml).
PINFIELD_NOT_MIRRORABLE = ("switch_mx", "diode_sod123", "mcu_liatris")

# How many footprints on each half have no mirrored counterpart: the keys of the
# outer pinky columns, switch plus diode each. Pinned rather than derived so that a
# mirrored key drifting out of alignment shows up here as a count that moved, which
# is the failure this number exists to catch. Update it only alongside a deliberate
# change to those columns.
UNPAIRED_KEYS = {"left": 12, "right": 16}

# Where the per-key case-reference curves live (switch cutouts and keycap recesses,
# case geometry that is never fabricated). The differing keys leave unpaired shapes
# here by design; a graphic on any other layer is silk or copper and must mirror.
KEY_REFERENCE_LAYER = "User.Eco1"

# Worst mirrored gap accepted, in mm. See TOLERANCE in the docstring.
TOLERANCE = 0.02

# Point spacing used to flatten arcs and to sample the outline, in mm. Well below
# the tolerance, so a deviation cannot hide between two samples.
STEP = 0.05

# Edge.Cuts graphics this board family uses. Any other graphic on the layer is a
# hard error rather than a skip: silently ignoring an outline element would let
# the very asymmetry this gate exists to catch pass unmeasured.
LINE_RE = re.compile(
    r'\(gr_line\s+\(start\s+(\S+)\s+(\S+)\)\s+\(end\s+(\S+)\s+(\S+)\)(.*?)\(layer\s+"([^"]+)"',
    re.S)
ARC_RE = re.compile(
    r'\(gr_arc\s+\(start\s+(\S+)\s+(\S+)\)\s+\(mid\s+(\S+)\s+(\S+)\)\s+\(end\s+(\S+)\s+(\S+)\)'
    r'(.*?)\(layer\s+"([^"]+)"',
    re.S)
OTHER_RE = re.compile(r'\(gr_(rect|circle|poly|curve|bbox)\b(.*?)\(layer\s+"([^"]+)"', re.S)


def arc_points(start, mid, end):
    """Flatten a KiCad three-point arc to a polyline, STEP apart along the curve."""
    (x1, y1), (x2, y2), (x3, y3) = start, mid, end
    d = 2 * (x1 * (y2 - y3) + x2 * (y3 - y1) + x3 * (y1 - y2))
    if abs(d) < 1e-12:  # collinear: a straight run, not an arc
        return [start, end]
    cx = ((x1**2 + y1**2) * (y2 - y3) + (x2**2 + y2**2) * (y3 - y1)
          + (x3**2 + y3**2) * (y1 - y2)) / d
    cy = ((x1**2 + y1**2) * (x3 - x2) + (x2**2 + y2**2) * (x1 - x3)
          + (x3**2 + y3**2) * (x2 - x1)) / d
    r = math.hypot(x1 - cx, y1 - cy)

    def ang(p):
        return math.atan2(p[1] - cy, p[0] - cx) % (2 * math.pi)

    a1, am, a3 = ang(start), ang(mid), ang(end)
    ccw = ((am - a1) % (2 * math.pi)) < ((a3 - a1) % (2 * math.pi))
    sweep = (a3 - a1) % (2 * math.pi) if ccw else -((a1 - a3) % (2 * math.pi))
    n = max(2, int(abs(sweep) * r / STEP) + 1)
    return [(cx + r * math.cos(a1 + sweep * i / n), cy + r * math.sin(a1 + sweep * i / n))
            for i in range(n + 1)]


def edge_segments(pcb_path):
    """Return the board's Edge.Cuts outline as a list of (p0, p1) segments.

    Read from the file text rather than through pcbnew: this is a pipeline gate,
    and loading a board costs seconds where a regex costs milliseconds (the same
    trade validate-provenance.py makes)."""
    with open(pcb_path, encoding="utf-8") as f:
        text = f.read()

    segs = []
    for m in LINE_RE.finditer(text):
        if m.group(6) == "Edge.Cuts":
            segs.append(((float(m.group(1)), float(m.group(2))),
                         (float(m.group(3)), float(m.group(4)))))
    for m in ARC_RE.finditer(text):
        if m.group(8) == "Edge.Cuts":
            g = [float(m.group(i)) for i in range(1, 7)]
            pts = arc_points((g[0], g[1]), (g[2], g[3]), (g[4], g[5]))
            segs += list(zip(pts, pts[1:]))

    unhandled = sorted({m.group(1) for m in OTHER_RE.finditer(text)
                        if m.group(3) == "Edge.Cuts"})
    if unhandled:
        sys.exit(f"ERROR {pcb_path}: unhandled Edge.Cuts graphic(s): "
                 f"{', '.join('gr_' + u for u in unhandled)}. "
                 "Teach validate-symmetry.py to flatten them; skipping one would "
                 "leave part of the outline unchecked")
    if not segs:
        sys.exit(f"ERROR {pcb_path}: no Edge.Cuts outline found")
    return segs


def bbox(segs):
    xs = [p[0] for s in segs for p in s]
    ys = [p[1] for s in segs for p in s]
    return min(xs), min(ys), max(xs), max(ys)


def normalize(segs, mirror_x):
    """Translate to the outline's own bbox center, optionally mirroring in x."""
    x0, y0, x1, y1 = bbox(segs)
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    sx = -1 if mirror_x else 1
    return [(((a[0] - cx) * sx, a[1] - cy), ((b[0] - cx) * sx, b[1] - cy))
            for a, b in segs]


class SegmentIndex:
    """Uniform grid over segments, for nearest-segment queries.

    A dense sample of one outline against every segment of the other is ~10^7
    point-segment tests, which is seconds of pure Python per board pair. Bucketing
    by cell and searching outward ring by ring keeps each query to a handful."""

    CELL = 2.0

    def __init__(self, segs):
        self.segs = segs
        self.cells = {}
        for i, (a, b) in enumerate(segs):
            n = max(1, int(math.dist(a, b) / self.CELL) + 1)
            for k in range(n + 1):
                t = k / n
                p = (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)
                self.cells.setdefault(self._key(p), set()).add(i)

    def _key(self, p):
        return (int(math.floor(p[0] / self.CELL)), int(math.floor(p[1] / self.CELL)))

    def distance(self, p):
        cx, cy = self._key(p)
        best = math.inf
        for ring in range(0, 64):
            found = False
            for gx in range(cx - ring, cx + ring + 1):
                for gy in range(cy - ring, cy + ring + 1):
                    # Only the newly added outer ring; inner cells are already done.
                    if ring and abs(gx - cx) != ring and abs(gy - cy) != ring:
                        continue
                    for i in self.cells.get((gx, gy), ()):
                        found = True
                        best = min(best, point_segment_distance(p, *self.segs[i]))
            # A segment can sit up to one cell outside the ring searched so far, so
            # only stop once the ring's guaranteed reach exceeds the best distance.
            if found and best <= (ring * self.CELL):
                break
        return best


def point_segment_distance(p, a, b):
    dx, dy = b[0] - a[0], b[1] - a[1]
    L = dx * dx + dy * dy
    if L == 0:
        return math.dist(p, a)
    t = max(0.0, min(1.0, ((p[0] - a[0]) * dx + (p[1] - a[1]) * dy) / L))
    return math.dist(p, (a[0] + t * dx, a[1] + t * dy))


def sample(segs):
    pts = []
    for a, b in segs:
        n = max(1, int(math.dist(a, b) / STEP))
        for i in range(n + 1):
            pts.append((a[0] + (b[0] - a[0]) * i / n, a[1] + (b[1] - a[1]) * i / n))
    return pts


def hausdorff(a_segs, b_segs):
    """Two-sided Hausdorff distance, with the point at which it is attained."""
    worst = (0.0, None)
    for src, dst in ((a_segs, b_segs), (b_segs, a_segs)):
        index = SegmentIndex(dst)
        for p in sample(src):
            d = index.distance(p)
            if d > worst[0]:
                worst = (d, p)
    return worst


def _normalized(pcb_path, mirror):
    """Load a board and return (board, cx, cy, sign) for normalizing its geometry.

    The center comes from Edge.Cuts, the same reference the outline check uses, so
    both checks measure against one frame."""
    board = pcbnew.LoadBoard(pcb_path)
    if board is None:
        sys.exit(f"ERROR {pcb_path}: pcbnew could not load the board")
    x0, y0, x1, y1 = bbox(edge_segments(pcb_path))
    return board, (x0 + x1) / 2, (y0 + y1) / 2, (-1 if mirror else 1)


def _q(value):
    """Quantize a mm length to FP_TOLERANCE, so exact-mirror geometry compares equal."""
    return round(value / FP_TOLERANCE)


def zone_segments(zone, cx, cy, s):
    """A rule area's outline and holes as closed polylines in the comparison frame."""
    poly = zone.Outline()
    segs = []
    for i in range(poly.OutlineCount()):
        for chain in [poly.Outline(i)] + [poly.Hole(i, h) for h in range(poly.HoleCount(i))]:
            ring = [(((chain.CPoint(v).x / MM) - cx) * s, (chain.CPoint(v).y / MM) - cy)
                    for v in range(chain.PointCount())]
            segs += [(ring[v], ring[(v + 1) % len(ring)]) for v in range(len(ring))]
    return segs


def components(pcb_path, mirror):
    """Footprints, zones and graphics of one half, in the mirrored comparison frame."""
    board, cx, cy, s = _normalized(pcb_path, mirror)
    fps, areas, gfx = [], [], []

    for fp in board.GetFootprints():
        origin = fp.GetPosition()
        rot = fp.GetOrientationDegrees()
        absolute, sizes = collections.Counter(), collections.Counter()
        for pad in fp.Pads():
            # The pad's name is part of the key: without it a 180 rotation that swaps
            # two pads symmetric about the origin leaves the position set unchanged and
            # reads as mirrored, which is exactly the TVS regression this must catch.
            absolute[(pad.GetNumber(), _q((pad.GetPosition().x / MM - cx) * s),
                      _q(pad.GetPosition().y / MM - cy),
                      pad.GetSizeX(), pad.GetSizeY())] += 1
            sizes[(pad.GetSizeX(), pad.GetSizeY(), pad.GetShape())] += 1
        fps.append(dict(lib=str(fp.GetFPIDAsString()).split(":")[-1], ref=fp.GetReference(),
                        layer=fp.GetLayerName(), x=(origin.x / MM - cx) * s, y=origin.y / MM - cy,
                        rot=(-rot if mirror else rot) % 360, absolute=absolute, sizes=sizes))

    for i in range(board.GetAreaCount()):
        z = board.GetArea(i)
        if not z.GetIsRuleArea():
            continue  # a filled copper zone is routing, not generated geometry
        bb = z.GetBoundingBox()
        areas.append(dict(name=z.GetZoneName() or z.GetNetname(), layer=z.GetLayerName(),
                          x=((bb.GetLeft() + bb.GetRight()) / 2 / MM - cx) * s,
                          y=(bb.GetTop() + bb.GetBottom()) / 2 / MM - cy,
                          w=_q(bb.GetWidth() / MM), h=_q(bb.GetHeight() / MM),
                          shape=zone_segments(z, cx, cy, s)))

    for d in board.GetDrawings():
        if d.GetLayerName() == "Edge.Cuts":
            continue  # the outline has its own, finer check
        bb = d.GetBoundingBox()
        gfx.append(dict(kind=d.GetClass(), layer=d.GetLayerName(),
                        text=d.GetShownText(True) if hasattr(d, "GetShownText") else "",
                        # Same string, same box, reversed on the board: a text carrying the
                        # wrong mirror flag is invisible to every other field here.
                        mirrored=bool(d.IsMirrored()) if hasattr(d, "IsMirrored") else False,
                        x=((bb.GetLeft() + bb.GetRight()) / 2 / MM - cx) * s,
                        y=(bb.GetTop() + bb.GetBottom()) / 2 / MM - cy,
                        w=_q(bb.GetWidth() / MM), h=_q(bb.GetHeight() / MM)))
    return fps, areas, gfx


def _pair(left, right, same_kind):
    """Pair items across halves by identical kind and mirrored position.

    Mirrored geometry agrees to nanometres, so a hit is unambiguous and a miss is a
    real difference rather than a matching artifact."""
    pairs, unmatched_r = [], list(range(len(right)))
    unmatched_l = []
    for a in left:
        hit = None
        for i in unmatched_r:
            b = right[i]
            if not same_kind(a, b):
                continue
            d = math.hypot(a["x"] - b["x"], a["y"] - b["y"])
            if hit is None or d < hit[0]:
                hit = (d, i)
        if hit is not None and hit[0] <= FP_TOLERANCE:
            unmatched_r.remove(hit[1])
            pairs.append((a, right[hit[1]]))
        else:
            unmatched_l.append(a)
    return pairs, unmatched_l, [right[i] for i in unmatched_r]


def check_components(a_path, b_path):
    """Return a list of failure lines: every way the two halves are not mirrors.

    What must hold, and why each rule is shaped the way it is:

    - Every footprint has a partner at the mirrored position. Unpaired ones may only
      be keys, and only as many as the outer pinky columns account for.
    - A pair's pad geometry must land mirrored. This, not the footprint's rotation
      angle, is the real test: a part whose pin field is not mirror-symmetric needs a
      compensating rotation to put its copper on the mirror line (the TVS carries
      rotate: 180 for exactly this), so comparing angles would flag the placement
      that is right and pass the one that is wrong.
    - Parts in PINFIELD_NOT_MIRRORABLE are exempt from that, because no placement can
      satisfy it: an MX switch's pins and its Kailh socket are physically asymmetric,
      and a mirror image of them is not a part you can buy. They are held to the two
      things that can hold instead -- the same part in its own frame, and the mirrored
      orientation.
    """
    a_fps, a_zones, a_gfx = components(a_path, False)
    b_fps, b_zones, b_gfx = components(b_path, True)
    fails = []

    pairs, only_a, only_b = _pair(a_fps, b_fps, lambda p, q: p["lib"] == q["lib"])
    for a, b in pairs:
        where = f"{a['ref']}/{b['ref']} ({a['lib']})"
        if a["layer"] != b["layer"]:
            fails.append(f"{where}: on {a['layer']} but {b['layer']} on the other half")
        elif a["lib"] in PINFIELD_NOT_MIRRORABLE:
            # Position, orientation and library between them pin the placement, and the
            # library pins the pin field, so this says everything that can be said.
            if a["sizes"] != b["sizes"]:
                fails.append(f"{where}: same footprint name but a different set of pads")
            elif abs(((a["rot"] - b["rot"] + 180) % 360) - 180) > ROT_TOLERANCE:
                fails.append(f"{where}: rotated {a['rot']:.2f} vs {b['rot']:.2f} mirrored")
        elif a["absolute"] != b["absolute"]:
            fails.append(f"{where}: pads do not land on mirrored positions; a part whose "
                         f"pin field is not mirror-symmetric needs a compensating rotation")

    for item, half in [(i, a_path) for i in only_a] + [(i, b_path) for i in only_b]:
        if item["lib"] not in KEY_FOOTPRINTS:
            fails.append(f"{item['ref']} ({item['lib']}) on {os.path.basename(half)}: "
                         f"no counterpart at the mirrored position, and only keys may "
                         f"differ between the halves")
    for half, unpaired in ((a_path, only_a), (b_path, only_b)):
        stem = os.path.splitext(os.path.basename(half))[0]
        # Keys only: a non-key with no counterpart is already its own failure above,
        # and counting it here would report the same thing twice.
        unpaired = [i for i in unpaired if i["lib"] in KEY_FOOTPRINTS]
        expected = UNPAIRED_KEYS.get(stem)
        if expected is None:
            fails.append(f"{os.path.basename(half)}: no expected unpaired-key count is "
                         f"recorded for this half in UNPAIRED_KEYS")
        elif len(unpaired) != expected:
            fails.append(f"{os.path.basename(half)}: {len(unpaired)} unpaired key "
                         f"footprint(s), expected {expected} for the outer pinky columns")

    zone_pairs, zone_a, zone_b = _pair(a_zones, b_zones,
                                       lambda p, q: (p["name"], p["layer"])
                                       == (q["name"], q["layer"]))
    for z, half in [(i, a_path) for i in zone_a] + [(i, b_path) for i in zone_b]:
        fails.append(f"zone {z['name']} on {z['layer']} of {os.path.basename(half)}: "
                     f"no counterpart at the mirrored position")
    for a, b in zone_pairs:
        # Outline, not bounding box. A rule area can be reshaped without moving its box:
        # keepout_perimeter_route is a full-board ring with the TRRS band carved out of
        # one side, and carving the wrong side leaves the box identical.
        #
        # Compared as a shape at TOLERANCE, not vertex for vertex. The perimeter rings
        # are built by inflating, deflating and intersecting the board outline, and
        # KiCad's polygon booleans do not emit the same vertices for mirrored input:
        # the two rings here differ by one vertex and ~9um of polygonization while
        # describing the same border. A carve on the wrong side is millimetres.
        shape_dist, _ = hausdorff(a["shape"], b["shape"])
        if shape_dist > TOLERANCE:
            fails.append(f"zone {a['name']} on {a['layer']}: same position and extent but "
                         f"an outline differing by {shape_dist * 1000:.2f}um, so one half "
                         f"is shaped differently inside")

    _, gfx_a, gfx_b = _pair(a_gfx, b_gfx,
                            lambda p, q: (p["kind"], p["layer"], p["text"], p["mirrored"],
                                          p["w"], p["h"])
                            == (q["kind"], q["layer"], q["text"], q["mirrored"],
                                q["w"], q["h"]))
    for g, half in [(i, a_path) for i in gfx_a] + [(i, b_path) for i in gfx_b]:
        # User.Eco1 carries the per-key case-reference curves (switch cutouts, keycap
        # recesses), so the keys that differ leave unpaired shapes there by design.
        # A graphic anywhere else is silk or copper and has to mirror.
        if g["layer"] != KEY_REFERENCE_LAYER:
            fails.append(f"{g['kind']} on {g['layer']} of {os.path.basename(half)} at "
                         f"({g['x']:.3f}, {g['y']:.3f}){': ' + g['text'] if g['text'] else ''}: "
                         f"no counterpart at the mirrored position")
    return fails


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    add_stage_argument(ap, "stage(s) to validate (default: both)")
    ap.add_argument("--tolerance", type=float, default=TOLERANCE,
                    help=f"worst accepted mirrored gap in mm (default {TOLERANCE})")
    args = ap.parse_args()
    stages = selected(args)

    version = os.environ.get("npm_package_config_VERSION")
    if not version:
        sys.exit("npm_package_config_VERSION not set -- run via npm (npm run validate:symmetry)")

    failed = set()
    checked = 0
    for stage in stages:
        boards = sorted(glob.glob(f"{version}/kicad/{stage}/[!_]*.kicad_pcb"))
        if not boards:
            sys.exit(f"No boards under {version}/kicad/{stage}/ to validate")
        if len(boards) != 2:
            sys.exit(f"{version}/kicad/{stage}/: expected 2 halves to compare, "
                     f"found {len(boards)}: {', '.join(map(os.path.basename, boards))}")

        a, b = boards
        a_segs, b_segs = edge_segments(a), edge_segments(b)
        ax0, ay0, ax1, ay1 = bbox(a_segs)
        bx0, by0, bx1, by1 = bbox(b_segs)
        dist, at = hausdorff(normalize(a_segs, False), normalize(b_segs, True))
        checked += 1

        name_a, name_b = os.path.basename(a), os.path.basename(b)
        if dist <= args.tolerance:
            note(f"  ok {version}/kicad/{stage}/: {name_a} and {name_b} mirror "
                 f"within {dist * 1000:.2f}um "
                 f"({ax1 - ax0:.4f} x {ay1 - ay0:.4f} vs {bx1 - bx0:.4f} x {by1 - by0:.4f} mm)")
        else:
            failed.add(stage)
            sys.stdout.flush()  # held `note` lines are stdout; a pipe would reorder them
            print(f"  ASYMMETRIC {version}/kicad/{stage}/: {name_a} and {name_b} differ by "
                  f"{dist * 1000:.2f}um (tolerance {args.tolerance * 1000:.0f}um), worst at "
                  f"({at[0]:.4f}, {at[1]:.4f}) relative to the board center",
                  file=sys.stderr)
            print(f"    {name_a}: {ax1 - ax0:.4f} x {ay1 - ay0:.4f} mm, "
                  f"{name_b}: {bx1 - bx0:.4f} x {by1 - by0:.4f} mm", file=sys.stderr)

        # The outline is only the envelope. Everything inside it -- components, their
        # pads, the keepout zones and the silk -- has to mirror too, or the halves are
        # the same shape with different insides.
        # Components are located from each board's own Edge.Cuts bbox center, so the two
        # frames agree only as closely as the outlines do: an outline difference offsets
        # every component by about half of it, and at FP_TOLERANCE that reads as nothing
        # pairing anywhere. Refuse to compare rather than report a board-wide asymmetry
        # that is really one edge, which is the more misleading of the two failures.
        if dist > FP_TOLERANCE:
            failed.add(stage)
            sys.stdout.flush()
            print(f"  ASYMMETRIC {version}/kicad/{stage}/: outlines differ by "
                  f"{dist * 1000:.2f}um, over the {FP_TOLERANCE * 1000:.0f}um the component "
                  f"check needs of the frame both halves are measured from; components not "
                  f"compared until the outline mirrors", file=sys.stderr)
            continue

        component_fails = check_components(a, b)
        if not component_fails:
            note(f"  ok {version}/kicad/{stage}/: components, pads, zones and silk mirror")
        else:
            failed.add(stage)
            sys.stdout.flush()
            print(f"  ASYMMETRIC {version}/kicad/{stage}/: {len(component_fails)} item(s) "
                  f"are not mirrored between {name_a} and {name_b}", file=sys.stderr)
            for line in component_fails:
                print(f"    {line}", file=sys.stderr)

    if failed:
        sys.stdout.flush()  # keep the per-stage lines above this summary under a pipe
        print(f"validate:symmetry: {len(failed)}/{checked} stage(s) have halves that are "
              "not mirror images. Both halves are built from one set of mirrored anchors in "
              "config.yaml, so this is a config change to undo, not a board to edit: the "
              "usual cause is a shape re-anchored to one half's own keys (the outer edge to "
              "its own pinky column) or a part placed on each half independently. Fix the "
              "config and re-run the pipeline",
              file=sys.stderr)
        sys.exit(1)

    print(f"OK: validate:symmetry: {checked} stage(s) have mirror-exact halves: outline "
          f"within {args.tolerance * 1000:.0f}um, components within "
          f"{FP_TOLERANCE * 1000:.0f}um")


if __name__ == "__main__":
    main()
