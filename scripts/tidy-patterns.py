#!/usr/bin/env python3
"""Pull hand-routed copper back onto the pattern its siblings already follow.

The matrix is a grid, so most of the routing is one shape repeated: the same hop
between every adjacent pair of column vias, the same run from every switch to its
diode. Drawing those by hand lands them a fraction of a millimetre apart, which no
DRC rule can see because every one of them is individually legal. This snaps the
strays onto the shape the majority already share.

Two rules, both of which only ever move a vertex that is already within MAX_MOVE
of where the pattern puts it. A deviation larger than that is a routing decision
(the detours around the screw-boss keepouts are all of them), so it is reported
and left exactly as it is rather than being flattened into the pattern.

The cap is measured on the travel, not on the deviation, and for a row leg the two
differ: both corners move diagonally to hold their 45 degrees, so a leg one GRID
line off the pattern travels sqrt(2) times as far as the leg itself moves. At
MAX_MOVE the rule admits a leg two grid lines off and refuses one three lines off,
which is the line between a hand-drag that missed and a leg drawn where it is on
purpose.

MAX_MOVE bounds how far a vertex travels, which is not the same as bounding where
the copper ends up: moving one end of a run pivots the whole run about its other
end, so copper swings along its entire length, millimetres from the vertex that
moved. A run already close to another net can break clearance on a move of
microns, and a run drawn wide of a screw boss can come back inside the keepout the
detour exists to clear. So every snap is measured before it is applied, against the
copper of every other net (pcb_copper.clearance_blocker) and against the rule areas
that keep copper out (pcb_copper.keepout_blocker). A snap that would land inside
either is reported and left alone, like one over the cap.

  ROW LEG    a row trunk crosses from one column's via to the next as a
             three-segment staircase: 45 degree riser, horizontal leg, 45 degree
             riser. The leg's y is the only free choice, and it belongs on the
             GRID line nearest LEG_DROP below the lower of the two vias. Both
             risers' corners move with it so they stay at 45 degrees.

  KEY MOTIF  the switch-to-diode run. Keys are grouped into families by where
             their switch and diode pads sit relative to the switch, so the
             splayed thumb keys form their own family: their pads are rotated, so
             their run is a different shape by construction rather than by hand.
             Within a family the shape most keys share wins, and a stray is re-laid
             on it. Sharing means two or more keys: a family where every key routes
             differently has no pattern in it, and picking one to impose on the
             others would be a coin toss, so it is left alone entire.

Run it AFTER cleanup-tracks.py, which merges the collinear fragments an edit
leaves behind. A fragmented run does not read as a three-segment staircase, so a
leg that needs moving would go unrecognised.

Idempotent: a board already on the pattern is not modified or even re-saved.

Usage: tidy-patterns.py <board.kicad_pcb> [more.kicad_pcb ...]
"""
import collections
import math
import sys

from lib.pcb_copper import (VIA_CLASS, clearance_blocker, describe, ids, keepout_blocker,
                            net_class)
from lib.pcbnew_quiet import pcbnew
from lib.pipeline_log import note

MAX_MOVE = pcbnew.FromMM(1.0)  # furthest a snap may drag copper, per endpoint

GRID = pcbnew.FromMM(0.25)  # the grid the row legs are drawn on
LEG_DROP = pcbnew.FromMM(1.65)  # nominal gap from the lower via down to the leg
COLUMN_STAGGER = pcbnew.FromMM(3.0)  # vertical offset between adjacent columns
MIN_LEG = pcbnew.FromMM(3.0)  # shorter than this is a jog, not a trunk leg
TRUNK_NET_CLASS = "VCC"  # row trunks are drawn at this class's track width
ANGLE_TOL = pcbnew.FromMM(0.0005)  # slack when testing a segment for 45 degrees
FAMILY_GRID = pcbnew.FromMM(0.01)  # pad-offset rounding when grouping keys

SEGMENT_CLASS = "PCB_TRACK"  # a straight segment; an arc cannot be re-cornered
MATRIX_NETS = ("GND", "VCC", "RST", "DATA_RAW")  # never a key-local net


def _snap(v, grid=GRID):
    return int(round(v / grid)) * grid


def _pt(p):
    return (p.x, p.y)


def _dist(a, b):
    return math.hypot(a[0] - b[0], a[1] - b[1])


def _is_45(a, b):
    return a != b and abs(abs(b[0] - a[0]) - abs(b[1] - a[1])) <= ANGLE_TOL


def _paths(tracks, pads):
    """Every maximal chain of segments running between two terminals, where a
    terminal is a via, a pad, or anywhere other than exactly two segments meet.

    `tracks` must be the caller's one snapshot: each board.GetTracks() call hands
    back fresh proxies for the same copper, so a segment read from a second call
    is never `is` the one walked here and the chains would not close."""
    segments = [t for t in tracks if t.GetClass() == SEGMENT_CLASS]
    vias = {_pt(t.GetPosition()) for t in tracks if t.GetClass() == VIA_CLASS}
    pads = {_pt(p.GetPosition()) for p in pads}
    out = []
    by_net = collections.defaultdict(list)
    for s in segments:
        by_net[(s.GetNetCode(), s.GetLayer())].append(s)
    for group in by_net.values():
        adjacent = collections.defaultdict(list)
        for s in group:
            a, b = _pt(s.GetStart()), _pt(s.GetEnd())
            adjacent[a].append((s, b))
            adjacent[b].append((s, a))

        def terminal(p):
            return len(adjacent[p]) != 2 or p in vias or p in pads

        walked = set()
        for start in list(adjacent):
            if not terminal(start):
                continue
            for first, nxt in adjacent[start]:
                if id(first) in walked:
                    continue
                walked.add(id(first))
                points, chain, here, came_from = [start, nxt], [first], nxt, first
                while not terminal(here):
                    onward = [(s, p) for s, p in adjacent[here] if id(s) != id(came_from)]
                    if len(onward) != 1 or id(onward[0][0]) in walked:
                        break
                    s, p = onward[0]
                    walked.add(id(s))
                    chain.append(s)
                    points.append(p)
                    came_from, here = s, p
                out.append((points, chain, points[0] in vias and points[-1] in vias))
    return out


def _blocked(tracks, pads, zones, proposals, replaced):
    """Why this copper may not go where the pattern wants it, as a phrase completing
    "snapping it would ...", or None if it may. Two questions, asked of the same
    proposals: does the copper crowd another net, and is it allowed there at all."""
    crowded = clearance_blocker(tracks, pads, proposals, replaced)
    if crowded is not None:
        other, gap = crowded
        return (f"put copper inside the {pcbnew.ToMM(gap):.2f}mm clearance of "
                f"{describe(other)}")
    area = keepout_blocker(zones, proposals)
    if area is not None:
        return f"put copper inside the {area.GetZoneName()} rule area"
    return None


def _row_legs(trunk_width, tracks, pads, zones):
    """(chain, [(old, new)]) per staircase whose leg is off the pattern's grid line,
    plus the hops left alone and why."""
    snaps, skipped = [], []
    for points, chain, via_ends in _paths(tracks, pads):
        if not via_ends or len(chain) != 3:
            continue
        if any(s.GetLayer() != pcbnew.F_Cu or s.GetWidth() != trunk_width for s in chain):
            continue
        start, corner_a, corner_b, end = points
        if corner_a[1] != corner_b[1] or abs(corner_a[0] - corner_b[0]) < MIN_LEG:
            continue
        if not (_is_45(start, corner_a) and _is_45(corner_b, end)):
            continue
        net = chain[0].GetNetname()
        if abs(start[1] - end[1]) not in (0, COLUMN_STAGGER):
            # Not a hop between adjacent columns, so the row rule does not describe it.
            skipped.append((net, points, "not a column-stagger hop"))
            continue
        want = _want_leg_y(start, end, corner_a[1])
        if want == corner_a[1]:
            continue
        moves = []
        for corner, anchor in ((corner_a, start), (corner_b, end)):
            run = abs(want - anchor[1])
            x = anchor[0] + (run if corner[0] > anchor[0] else -run)
            moves.append((corner, (x, want)))
        travel = max(_dist(old, new) for old, new in moves)
        if travel > MAX_MOVE:
            skipped.append((net, points,
                            f"leg is {pcbnew.ToMM(abs(want - corner_a[1])):.3f}mm off the "
                            f"pattern, which would move copper {pcbnew.ToMM(travel):.3f}mm"))
            continue
        why = _blocked(tracks, pads, zones, _leg_shapes(chain, moves), ids(chain))
        if why is not None:
            skipped.append((net, points, f"snapping the leg would {why}"))
            continue
        snaps.append((net, chain, moves, corner_a[1], want, travel))
    return snaps, skipped


def _want_leg_y(start, end, leg_y):
    """Where the pattern puts this staircase's leg: LEG_DROP from a via, on the grid.

    Which via, and which side of it, is not fixed. The leg can run between the two
    vias (dropping away from the lower one) or bulge clear above or below both, and
    those are the same shape reflected, all three drawn by hand on these boards. So
    all three are the pattern and the one nearest the leg's own position wins. A
    single fixed answer would report every trunk drawn the other way as a stray
    needing a move right across its own vias, which is not a stray and not a move
    anyone would want made."""
    lower, upper = max(start[1], end[1]), min(start[1], end[1])
    return min((_snap(lower - LEG_DROP), _snap(upper - LEG_DROP), _snap(lower + LEG_DROP)),
               key=lambda y: abs(y - leg_y))


def _leg_shapes(chain, moves):
    """The staircase's segments where the snap would put them, for the clearance
    test, which has to ask before the board is changed."""
    moved = {old: new for old, new in moves}
    out = []
    for s in chain:
        a, b = moved.get(_pt(s.GetStart()), _pt(s.GetStart())), moved.get(_pt(s.GetEnd()), _pt(s.GetEnd()))
        out.append((s.GetLayer(), s.GetNetCode(), s.GetOwnClearance(s.GetLayer()),
                    pcbnew.SHAPE_SEGMENT(_vec(a), _vec(b), s.GetWidth())))
    return out


def _vec(p):
    return pcbnew.VECTOR2I(int(p[0]), int(p[1]))


def _key_families(board, tracks):
    """Key-local nets grouped by where their switch and diode pads sit relative to
    the switch, then by the shape of their run. Only keys whose pads agree can be
    expected to route the same way."""
    switch, diode = {}, {}
    for f in board.GetFootprints():
        library = f.GetFPIDAsString()
        for pad in f.Pads():
            net = pad.GetNetname()
            if not net or net.startswith("P") or net in MATRIX_NETS:
                continue
            if "switch_mx" in library:
                switch[net] = (f, pad)
            elif "diode" in library:
                diode[net] = pad
    runs, vias = collections.defaultdict(list), collections.defaultdict(list)
    for t in tracks:
        net = t.GetNetname()
        if net not in switch:
            continue
        (vias if t.GetClass() == VIA_CLASS else runs)[net].append(t)
    families = collections.defaultdict(dict)
    for net, tracks in runs.items():
        if any(t.GetClass() != SEGMENT_CLASS for t in tracks):
            continue  # an arc cannot be rebuilt from a straight-segment template
        origin = switch[net][0].GetPosition()

        def relative(p):
            return (_snap(p.x - origin.x, FAMILY_GRID), _snap(p.y - origin.y, FAMILY_GRID))

        family = (relative(switch[net][1].GetPosition()),
                  relative(diode[net].GetPosition()) if net in diode else None,
                  tuple(sorted(relative(v.GetPosition()) for v in vias[net])))
        shape = []
        for t in tracks:
            a, b = _pt(t.GetStart()), _pt(t.GetEnd())
            a, b = (a, b) if a <= b else (b, a)
            shape.append((t.GetLayer(), t.GetWidth(),
                          a[0] - origin.x, a[1] - origin.y, b[0] - origin.x, b[1] - origin.y))
        families[family].setdefault(tuple(sorted(shape)), []).append(net)
    return families, switch, runs


def _vertices(shape):
    out = set()
    for _, _, ax, ay, bx, by in shape:
        out.add((ax, ay))
        out.add((bx, by))
    return out


def _reshape_cost(have, want):
    """Furthest any vertex travels turning `have` into `want`, both relative to the
    switch. Symmetric, because a vertex the rewrite drops still has to collapse
    onto one it keeps."""
    a, b = _vertices(have), _vertices(want)
    return max(max(min(_dist(p, q) for q in b) for p in a),
               max(min(_dist(q, p) for p in a) for q in b))


def _profile(shape):
    """The layers and widths a shape is drawn with, one entry per segment.
    _reshape_cost measures vertex positions only, so it scores an identical run on
    the wrong layer, or at the wrong width, at 0.000mm and MAX_MOVE cannot veto it.
    Two runs are the same motif only if they agree here first.

    Being one entry per segment, this tests segment count as much as layer and
    width, and count is the commoner difference: a run carrying one fragment more
    than the pattern does not match either. Anything reporting a mismatch has to say
    which it was, or it sends the reader looking for the wrong difference."""
    return sorted((layer, width) for layer, width, *_ in shape)


def _profile_desc(board, shape):
    """A shape's profile, named so a report can put two of them side by side."""
    counts = collections.Counter(
        (board.GetLayerName(layer), pcbnew.ToMM(width)) for layer, width, *_ in shape)
    return ", ".join(f"{n} x {layer} {width:.2f}mm"
                     for (layer, width), n in sorted(counts.items()))


def _key_motifs(board, tracks, pads, zones):
    """(net, tracks, canonical segments) per key off its family's dominant shape,
    plus the keys left alone and why."""
    families, switch, runs = _key_families(board, tracks)
    rewrites, skipped = [], []
    for shapes in families.values():
        ranked = sorted(shapes.items(), key=lambda kv: -len(kv[1]))
        best = len(ranked[0][1])
        if best < 2:
            # No two keys route the same way, so there is no pattern here to snap
            # to and the "dominant" shape would be whichever one sorted first.
            skipped.append((", ".join(sorted(n for _, nets in ranked for n in nets)),
                            f"no two of these {len(ranked)} keys route the same shape, "
                            f"so the family has no pattern to snap to"))
            continue
        # A tie has no majority to defer to, so take the medoid: the shape that
        # asks the least of the others.
        canon, canon_nets = min(
            (s for s in ranked if len(s[1]) == best),
            key=lambda s: max([_reshape_cost(o, s[0]) for o, _ in ranked if o is not s[0]] or [0]))
        for shape, nets in ranked:
            if shape == canon:
                continue
            cost = _reshape_cost(shape, canon)
            for net in nets:
                if _profile(shape) != _profile(canon):
                    skipped.append((net, f"its run is {_profile_desc(board, shape)} where the "
                                         f"other {best} are {_profile_desc(board, canon)}, so it "
                                         f"is not the same motif"))
                    continue
                if cost > MAX_MOVE:
                    skipped.append((net, f"its run is a different shape, not a stray: "
                                         f"matching the other {best} would move copper "
                                         f"{pcbnew.ToMM(cost):.3f}mm"))
                    continue
                origin = switch[net][0].GetPosition()
                want = [(layer, width,
                         (ax + origin.x, ay + origin.y), (bx + origin.x, by + origin.y))
                        for layer, width, ax, ay, bx, by in canon]
                why = _blocked(tracks, pads, zones, _motif_shapes(runs[net][0], want),
                               ids(runs[net]))
                if why is not None:
                    skipped.append((net, f"re-laying it would {why}"))
                    continue
                rewrites.append((net, runs[net], want, cost))
    return rewrites, skipped


def _motif_shapes(proto, want):
    """The re-laid run where the rewrite would put it, for the clearance test."""
    return [(layer, proto.GetNetCode(), proto.GetOwnClearance(layer),
             pcbnew.SHAPE_SEGMENT(_vec(a), _vec(b), width))
            for layer, width, a, b in want]


def _apply_row_leg(chain, moves):
    for old, new in moves:
        target = pcbnew.VECTOR2I(int(new[0]), int(new[1]))
        for s in chain:
            if _pt(s.GetStart()) == old:
                s.SetStart(target)
            if _pt(s.GetEnd()) == old:
                s.SetEnd(target)


def _apply_key_motif(board, tracks, want):
    proto = tracks[0]
    for t in tracks:
        # RemoveNative, not Remove: Remove hands ownership to Python, which has no
        # destructor for a PCB_TRACK and reports every one as a leak at exit.
        board.RemoveNative(t)
    for layer, width, a, b in want:
        t = pcbnew.PCB_TRACK(board)
        t.SetStart(pcbnew.VECTOR2I(int(a[0]), int(a[1])))
        t.SetEnd(pcbnew.VECTOR2I(int(b[0]), int(b[1])))
        t.SetLayer(layer)
        t.SetWidth(width)
        t.SetNetCode(proto.GetNetCode())
        board.Add(t)


def tidy_patterns(path):
    board = pcbnew.LoadBoard(path)
    # One snapshot for the whole run: the identity of these proxies is what the
    # chain walk and the rewrite both work from.
    tracks, pads = list(board.GetTracks()), list(board.GetPads())
    zones = list(board.Zones())
    trunk_width = net_class(board, TRUNK_NET_CLASS).GetTrackWidth()
    legs, leg_skips = _row_legs(trunk_width, tracks, pads, zones)
    motifs, motif_skips = _key_motifs(board, tracks, pads, zones)

    for _, chain, moves, _, _, _ in legs:
        _apply_row_leg(chain, moves)
    for _, tracks, want, _ in motifs:
        _apply_key_motif(board, tracks, want)

    for net, points, why in leg_skips:
        a, b = points[0], points[-1]
        print(f"  LEFT ALONE {net}: {why}, hop "
              f"({pcbnew.ToMM(a[0]):.3f}, {pcbnew.ToMM(a[1]):.3f}) -> "
              f"({pcbnew.ToMM(b[0]):.3f}, {pcbnew.ToMM(b[1]):.3f})")
    for net, why in motif_skips:
        print(f"  LEFT ALONE {net}: {why}")

    if not legs and not motifs:
        note(f"  unchanged {path}: already on the pattern")
        return

    for net, _, _, was, now, travel in legs:
        print(f"  SNAPPED {net}: row leg y {pcbnew.ToMM(was):.3f} -> "
              f"{pcbnew.ToMM(now):.3f}, copper moved {pcbnew.ToMM(travel):.3f}mm")
    for net, _, _, cost in motifs:
        print(f"  RELAID {net}: onto its family's shape, copper moved "
              f"{pcbnew.ToMM(cost):.3f}mm")

    pcbnew.ZONE_FILLER(board).Fill(board.Zones())  # re-pour around the moved copper
    board.Save(path)
    worst = max([t for *_, t in legs] + [c for *_, c in motifs])
    print(f"  TIDIED {path}: {len(legs)} row leg(s) and {len(motifs)} key run(s) snapped "
          f"to the pattern within {pcbnew.ToMM(worst):.3f}mm, zones re-filled")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    for board_path in sys.argv[1:]:
        tidy_patterns(board_path)
