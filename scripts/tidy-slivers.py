#!/usr/bin/env python3
"""Collapse the segments a hand edit left that are shorter than they are wide.

Dragging a track in KiCad can leave a segment a few microns long where two runs
meet: a lateral jog between two nearly-collinear traces, or a stub between a via
and the run leaving it. It is copper the route does not need, it is smaller than
anything a fab can resolve, and it is invisible to DRC because it carries its own
net. cleanup-tracks.py cannot remove it, since every rule there deletes copper
outright and deleting a sliver would strand the run on the far side of it.

A sliver is collapsed by pulling what meets it onto a single point and deleting
it, which is the one operation in this pipeline that MOVES copper rather than
only removing it. That is capped hard at MAX_MOVE: the cap is what makes the
collapse a tidy rather than a re-route, since copper that moves less than a
hundredth of a millimetre cannot change what the board does. Where a collapse
would need more than that, the sliver is left exactly as it is and reported as an
error, because deciding to move real copper is a routing decision and belongs to
whoever is routing. Nothing is saved in that case: the step either tidies
everything it found or changes nothing.

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

`--max-move` raises the cap for one deliberate run, for the case the cap exists to
prevent: a board carrying slivers a person is willing to have closed for them.
The pipeline never passes it, so the default cap is what every build enforces.
Re-run DRC after using it.

Usage: tidy-slivers.py <board.kicad_pcb> [more.kicad_pcb ...] [--max-move <mm>]
"""
import argparse

from pcb_copper import TOUCH_TOL, copper_pads, dist, is_via
from pcbnew_quiet import pcbnew

MAX_MOVE = pcbnew.FromMM(0.01)  # furthest a tidy may drag copper, per endpoint

SEGMENT_CLASS = "PCB_TRACK"  # a straight segment; an arc endpoint cannot be moved freely


def _segments(board):
    return [t for t in board.GetTracks() if t.GetClass() == SEGMENT_CLASS]


def _slivers(board):
    """Segments shorter than their own width. A segment that cannot be as long as
    it is wide is a rounding artifact of an edit, never a routing decision."""
    return [t for t in _segments(board) if t.GetLength() < t.GetWidth()]


def _pinned(board, sliver, point):
    """True if a via or a pad of the sliver's net holds this point in place."""
    net, layer = sliver.GetNetCode(), sliver.GetLayer()
    if any(is_via(v) and v.GetNetCode() == net and dist(point, v.GetPosition()) <= TOUCH_TOL
           for v in board.GetTracks()):
        return True
    return any(pad.GetNetCode() == net and pad.IsOnLayer(layer) and pad.HitTest(point)
               for pad in copper_pads(board))


def _movers(board, sliver, point):
    """Every other track ending on this point: what a collapse would drag. Arcs
    are reported too, so a sliver hanging off one is refused rather than
    distorted (moving an arc's endpoint re-shapes the whole curve)."""
    net, layer = sliver.GetNetCode(), sliver.GetLayer()
    return [t for t in board.GetTracks()
            if t is not sliver and not is_via(t) and t.GetNetCode() == net and t.GetLayer() == layer
            and any(dist(point, p) <= TOUCH_TOL for p in (t.GetStart(), t.GetEnd()))]


def _plan(board, sliver):
    """How this sliver would collapse, as (target, movers, move) where every mover
    ends up on target and none of them travels further than `move`. Returns a
    (None, [], reason) triple for a sliver that must be left alone."""
    a, b = sliver.GetStart(), sliver.GetEnd()
    pinned_a, pinned_b = _pinned(board, sliver, a), _pinned(board, sliver, b)
    movers_a, movers_b = _movers(board, sliver, a), _movers(board, sliver, b)

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


def _collapse(board, sliver, target, movers):
    for t in movers:
        for setter, getter in ((t.SetStart, t.GetStart), (t.SetEnd, t.GetEnd)):
            if dist(getter(), sliver.GetStart()) <= TOUCH_TOL or dist(getter(), sliver.GetEnd()) <= TOUCH_TOL:
                setter(target)
    # RemoveNative, not Remove: Remove hands ownership to Python, which has no
    # destructor for a PCB_TRACK and reports every one as a leak at exit.
    board.RemoveNative(sliver)
    for t in movers:
        if dist(t.GetStart(), t.GetEnd()) <= TOUCH_TOL:
            board.RemoveNative(t)  # a mover the collapse shortened to nothing


def _refusal(board, sliver):
    """Why this sliver cannot be collapsed, or None if it can."""
    target, _, detail = _plan(board, sliver)
    if target is None:
        return detail
    if detail > MAX_MOVE:
        return (f"collapsing it would move copper {pcbnew.ToMM(detail):.4f}mm, "
                f"over the {pcbnew.ToMM(MAX_MOVE):.2f}mm cap")
    return None


def tidy_slivers(path):
    board = pcbnew.LoadBoard(path)
    collapsed = 0
    # One at a time, re-scanning: a collapse moves its neighbours, and a neighbour
    # may itself be a sliver whose plan those moves have just changed.
    while True:
        doable = [(s, *_plan(board, s)[:2]) for s in _slivers(board) if not _refusal(board, s)]
        if not doable:
            break
        _collapse(board, *doable[0])
        collapsed += 1

    # Whatever is left is, by definition, something the loop could not collapse.
    refused = [(s, _refusal(board, s)) for s in _slivers(board)]
    if refused:
        lines = [f"ERROR: {len(refused)} sliver(s) cannot be tidied within "
                 f"{pcbnew.ToMM(MAX_MOVE):.2f}mm: {path}"]
        for sliver, detail in refused:
            p = sliver.GetStart()
            lines.append(f"  {board.GetLayerName(sliver.GetLayer())} {sliver.GetNetname()} "
                         f"{pcbnew.ToMM(sliver.GetLength()):.4f}mm at "
                         f"({pcbnew.ToMM(p.x):.3f}, {pcbnew.ToMM(p.y):.3f}): {detail}")
        lines.append("  Fix these by hand in KiCad (drag the two runs together so the sliver "
                     "closes), then re-run the pipeline. The board was NOT modified.")
        raise SystemExit("\n".join(lines))

    if not collapsed:
        print(f"  UNCHANGED: no slivers to tidy: {path}")
        return

    pcbnew.ZONE_FILLER(board).Fill(board.Zones())  # re-pour around the moved copper
    board.Save(path)
    print(f"  TIDIED: collapsed {collapsed} sliver(s) within {pcbnew.ToMM(MAX_MOVE):.2f}mm, "
          f"zones re-filled: {path}")


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
