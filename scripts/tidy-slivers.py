#!/usr/bin/env python3
"""Collapse the segments a hand edit left that are shorter than they are wide.

Dragging a track in KiCad can leave a segment a few microns long where two runs
meet: a lateral jog between two nearly-collinear traces, or a stub between a via
and the run leaving it. It is copper the route does not need, it is smaller than
anything a fab can resolve, and it is invisible to DRC because it carries its own
net. cleanup-tracks.py cannot remove it, since every rule there deletes copper
outright and deleting a sliver would strand the run on the far side of it.

A sliver is collapsed by pulling what meets it onto a single point and deleting
it, which is one of the two operations in this pipeline that MOVE copper rather
than only removing it (tidy-patterns.py is the other). A cap and two geometry
tests bound the move, and all three are needed:

MAX_MOVE caps how far any endpoint travels. It binds only on traces wider than
the cap, since a sliver is by definition shorter than it is wide. Where a
collapse would need more, the sliver is left exactly as it is, because moving
copper that far is a routing decision and belongs to whoever is routing.

Two geometry tests catch what the cap cannot, both asked of the moved copper
before the board is changed. Moving one endpoint of a segment pivots the WHOLE
segment about its far end, so copper swings along its entire length, metres from
the sliver, by up to the same distance:

  - clearance (pcb_copper.clearance_blocker), against the copper of every other
    net. On a run already close to one, that swing is enough to break clearance:
    the move is small, but so is the margin it eats. The GND pour is not
    measured, since it re-flows around whatever the copper ends up being.
  - rule areas (pcb_copper.keepout_blocker), against the keepout_* zones that
    keep copper out. A rule area is not copper, so the clearance test cannot see
    one, and a run drawn wide of a screw boss can swing back inside the keepout
    the detour exists to clear.

Any refusal is a hard error naming the sliver. Nothing is saved in that case:
the step tidies everything it found or changes nothing.

  - a sliver whose ends both hang on other segments collapses to its midpoint, so
    each side moves by half its length
  - a sliver with one end pinned (on a via, or inside a pad of its own net)
    collapses onto that end, so the free side moves by its full length
  - a sliver pinned at both ends, or with an end that nothing else touches, is
    never collapsed: the first would drag a via or a pad, and the second is
    dangling copper for cleanup-tracks.py to delete

Run it AFTER cleanup-tracks.py, on a board that is already stripped to the copper
the route uses, so every remaining sliver sits in a live run rather than in
copper that is about to disappear. Collapsing leaves the two sides collinear and
meeting end to end, which the next build's cleanup merges into one segment.

Idempotent: a board with no slivers is not modified or even re-saved.

`--max-move` changes the cap for one deliberate run. The pipeline never passes it,
so the default is what every build enforces. Re-run DRC after raising it.

Usage: tidy-slivers.py <board.kicad_pcb> [more.kicad_pcb ...] [--max-move <mm>]
"""
import argparse

from pcb_copper import (TOUCH_TOL, clearance_blocker, copper_pads, describe, dist, is_via,
                        keepout_blocker)
from pcbnew_quiet import pcbnew
from pipeline_log import note

MAX_MOVE = pcbnew.FromMM(0.2)  # furthest a tidy may drag copper, per endpoint

SEGMENT_CLASS = "PCB_TRACK"  # a straight segment; an arc endpoint cannot be moved freely


def _slivers(tracks):
    """Segments shorter than their own width. A segment that cannot be as long as
    it is wide is a rounding artifact of an edit, never a routing decision."""
    return [t for t in tracks if t.GetClass() == SEGMENT_CLASS and t.GetLength() < t.GetWidth()]


def _pinned(tracks, pads, sliver, point):
    """True if a via or a pad of the sliver's net holds this point in place."""
    net, layer = sliver.GetNetCode(), sliver.GetLayer()
    if any(is_via(v) and v.GetNetCode() == net and dist(point, v.GetPosition()) <= TOUCH_TOL
           for v in tracks):
        return True
    return any(pad.GetNetCode() == net and pad.IsOnLayer(layer) and pad.HitTest(point)
               for pad in pads)


def _movers(tracks, sliver, point):
    """Every other track ending on this point: what a collapse would drag. Arcs
    are reported too, so a sliver hanging off one is refused rather than
    distorted (moving an arc's endpoint re-shapes the whole curve).

    `sliver` must come from `tracks`, the one snapshot a caller works from: each
    board.GetTracks() call hands back fresh proxies for the same copper, so a
    sliver read from a second call is never `is` the one in this list and would
    pass the filter as its own neighbour."""
    net, layer = sliver.GetNetCode(), sliver.GetLayer()
    return [t for t in tracks
            if t is not sliver and not is_via(t) and t.GetNetCode() == net and t.GetLayer() == layer
            and any(dist(point, p) <= TOUCH_TOL for p in (t.GetStart(), t.GetEnd()))]


def _plan(tracks, pads, sliver):
    """How this sliver would collapse, as (target, movers, move) where every mover
    ends up on target and none of them travels further than `move`. Returns a
    (None, [], reason) triple for a sliver that must be left alone."""
    a, b = sliver.GetStart(), sliver.GetEnd()
    pinned_a, pinned_b = _pinned(tracks, pads, sliver, a), _pinned(tracks, pads, sliver, b)
    movers_a, movers_b = _movers(tracks, sliver, a), _movers(tracks, sliver, b)

    if pinned_a and pinned_b:
        return None, [], "pinned at both ends (a via or pad holds each end)"
    if any(t.GetClass() != SEGMENT_CLASS for t in movers_a + movers_b):
        return None, [], "an arc meets it, and an arc endpoint cannot be moved without re-shaping it"
    if pinned_a or pinned_b:
        target, movers = (a, movers_b) if pinned_a else (b, movers_a)
        if not movers:
            return None, [], "dangling: nothing holds its free end, so cleanup-tracks.py owns it"
        return target, movers, sliver.GetLength()
    if not movers_a or not movers_b:
        return None, [], "dangling: nothing holds one of its ends, so cleanup-tracks.py owns it"
    target = pcbnew.VECTOR2I((a.x + b.x) // 2, (a.y + b.y) // 2)
    return target, movers_a + movers_b, max(dist(target, a), dist(target, b))


def _ends(sliver):
    """The sliver's endpoints, copied. They are what a mover is matched against, and
    a mover that turned out to alias the sliver would otherwise move them mid-loop."""
    return (pcbnew.VECTOR2I(sliver.GetStart()), pcbnew.VECTOR2I(sliver.GetEnd()))


def _moved(ends, target, mover):
    """Where `mover` would sit after the collapse, as a shape. Not applied: the
    clearance test has to ask before the board is changed, not after."""
    points = [target if any(dist(p, end) <= TOUCH_TOL for end in ends) else p
              for p in (mover.GetStart(), mover.GetEnd())]
    return pcbnew.SHAPE_SEGMENT(points[0], points[1], mover.GetWidth())


def _blocked(tracks, pads, zones, sliver, target, movers):
    """Why the copper this collapse would lay down may not go there, as a phrase
    completing "collapsing it would ...", or None if it may. Two questions asked of
    the same proposals: does the copper crowd another net, and is it allowed there at
    all."""
    ends = _ends(sliver)
    proposals = [(m.GetLayer(), m.GetNetCode(), m.GetOwnClearance(m.GetLayer()),
                  _moved(ends, target, m)) for m in movers]
    crowded = clearance_blocker(tracks, pads, proposals, replaced={id(sliver)})
    if crowded is not None:
        other, gap = crowded
        return (f"swing copper inside the {pcbnew.ToMM(gap):.2f}mm clearance of "
                f"{describe(other)}")
    area = keepout_blocker(zones, proposals)
    if area is not None:
        return f"swing copper inside the {area.GetZoneName()} rule area"
    return None


def _collapse(board, sliver, target, movers):
    ends = _ends(sliver)
    for mover in movers:
        for setter, getter in ((mover.SetStart, mover.GetStart), (mover.SetEnd, mover.GetEnd)):
            if any(dist(getter(), end) <= TOUCH_TOL for end in ends):
                setter(target)
    # RemoveNative, not Remove: Remove hands ownership to Python, which has no
    # destructor for a PCB_TRACK and reports every one as a leak at exit.
    board.RemoveNative(sliver)
    for mover in movers:
        if dist(mover.GetStart(), mover.GetEnd()) <= TOUCH_TOL:
            board.RemoveNative(mover)  # a mover the collapse shortened to nothing


def _refusal(tracks, pads, zones, sliver):
    """Why this sliver cannot be collapsed, or None if it can."""
    target, movers, detail = _plan(tracks, pads, sliver)
    if target is None:
        return detail
    if detail > MAX_MOVE:
        return (f"collapsing it would move copper {pcbnew.ToMM(detail):.4f}mm, "
                f"over the {pcbnew.ToMM(MAX_MOVE):.2f}mm cap")
    why = _blocked(tracks, pads, zones, sliver, target, movers)
    if why is not None:
        return f"collapsing it would {why}"
    return None


def _collapse_one(board):
    """Collapse the first sliver that can be, and say whether one was. Everything is
    read from one snapshot of the board's tracks, so a sliver and its neighbours are
    the same Python objects and a sliver cannot be its own neighbour."""
    tracks = list(board.GetTracks())
    pads = copper_pads(board)
    zones = list(board.Zones())
    for sliver in _slivers(tracks):
        if _refusal(tracks, pads, zones, sliver) is None:
            target, movers, _ = _plan(tracks, pads, sliver)
            _collapse(board, sliver, target, movers)
            return True
    return False


def tidy_slivers(path):
    board = pcbnew.LoadBoard(path)
    collapsed = 0
    # One at a time, re-scanning: a collapse moves its neighbours, and a neighbour
    # may itself be a sliver whose plan those moves have just changed.
    while _collapse_one(board):
        collapsed += 1

    # Whatever is left is, by definition, something the loop could not collapse.
    tracks = list(board.GetTracks())
    pads = copper_pads(board)
    zones = list(board.Zones())
    refused = [(s, _refusal(tracks, pads, zones, s)) for s in _slivers(tracks)]
    if refused:
        lines = [f"ERROR {path}: {len(refused)} sliver(s) cannot be tidied within "
                 f"{pcbnew.ToMM(MAX_MOVE):.2f}mm"]
        for sliver, detail in refused:
            p = sliver.GetStart()
            lines.append(f"    {board.GetLayerName(sliver.GetLayer())} {sliver.GetNetname()} "
                         f"{pcbnew.ToMM(sliver.GetLength()):.4f}mm at "
                         f"({pcbnew.ToMM(p.x):.3f}, {pcbnew.ToMM(p.y):.3f}): {detail}")
        lines.append("    Close these in KiCad by dragging the two runs together, then re-run\n"
                     "    the pipeline. Where the reason is clearance, give the run room from\n"
                     "    the item named first, or closing it by hand will fail DRC where this\n"
                     "    refused. Where it is a rule area, the copper may not be there at all,\n"
                     "    so re-route the run clear of it. The board was NOT modified")
        raise SystemExit("\n".join(lines))

    if not collapsed:
        note(f"  unchanged {path}: no slivers to tidy")
        return

    pcbnew.ZONE_FILLER(board).Fill(board.Zones())  # re-pour around the moved copper
    board.Save(path)
    print(f"  TIDIED {path}: collapsed {collapsed} sliver(s) within "
          f"{pcbnew.ToMM(MAX_MOVE):.2f}mm, zones re-filled")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("boards", nargs="+", metavar="board.kicad_pcb")
    parser.add_argument("--max-move", type=float, metavar="MM",
                        help="raise the copper-movement cap for this run (default "
                             f"{pcbnew.ToMM(MAX_MOVE)}mm); re-run DRC afterwards")
    args = parser.parse_args()
    if args.max_move is not None:
        MAX_MOVE = pcbnew.FromMM(args.max_move)
    for board_path in args.boards:
        tidy_slivers(board_path)
