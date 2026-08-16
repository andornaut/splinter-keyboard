#!/usr/bin/env python3
"""Delete the copper a finished route does not use, and merge what it split.

The generated footprints emit routing aids the finished routing does not always
use: with `include_traces_vias`, diode_sod123 (and r_0805, sod-123fl) puts a short
stub and a via at every pad, exposing that pad's net on the opposite copper layer.
Wherever a route never picks one up, it stays on the board as copper connected at
one end only: a wasted drill hit and a stub punched through the ground pour. Hand
routing leaves its own litter too: a segment split by an edit that was never
re-joined, a via dropped on a through-hole pad that already spans every layer.

This is KiCad's Tools > Cleanup Tracks & Vias as a pipeline step, so every build
produces a cleaned board:

  - a track laid over another of the same net, layer and path is doubled copper,
    and the narrower of the pair is deleted
  - a segment lying along a no-narrower one of its own net and layer is buried
    inside it, and is deleted
  - a track whose start or end touches no other copper (a track, a via, a pad, or
    a filled pour of its own net) is dangling, and is deleted
  - a track that lies entirely inside a pad of its own net adds nothing, and is
    deleted
  - a via left with copper on fewer than two layers connects nothing, and is
    deleted
  - a via duplicating another via at the same spot, or sitting in a plated
    through-hole pad of its net, is redundant, and is deleted
  - two segments meeting end to end with nothing else at the junction, collinear
    to within a micron, are merged into one

Deleting any of these can strand another, so the deletions run to a fixpoint, and
the merge runs after them.

A pour counts as copper, which is what keeps a GND stitching via sitting in the
plane: it is connected on the pour layer. Run this AFTER the pour is added (see
copy-unrouted-to-routed.sh), never before, or every stitching via looks orphaned
and is deleted. A teardrop does NOT count (see pcb_copper.fill_zones): it is a
flare on the very copper under test, so counting it would let a dangling stub
hold itself up. Teardrops left with nothing to decorate are deleted with the
copper they decorated, so a deleted via cannot leave an island behind.

Zones are re-filled at the end of every pass, for the same reason KiCad offers to
re-pour after its own cleanup: removing copper changes what the pour can flow
into. That re-pour is also why the whole pass repeats until one of them changes
nothing: a track the old pour propped up only reads as dangling once the pour has
been re-flowed without it, and the merge and the teardrop scan both run after the
deletion fixpoint, so nothing tests what they leave behind. Every rule only ever
removes copper, so a changing pass strictly shrinks the board and the loop always
ends; MAX_PASSES is a canary for rules interacting in a way this file does not
predict, not a termination guard, and a board still changing that deep is a hard
error rather than a truncated cleanup.

Idempotent: a board with nothing to clean is not modified or even re-saved, so
running it on every build is safe.

Usage: cleanup-tracks.py <board.kicad_pcb> [more.kicad_pcb ...]
"""

import sys

from lib.pcb_copper import (
    TOUCH_TOL,
    connected,
    copper_pads,
    covers,
    dangling_tracks,
    dist,
    fill_zones,
    ids,
    is_via,
    point_to_segment,
)
from lib.pcbnew_quiet import pcbnew
from lib.pipeline_log import note

ARC_ERROR = pcbnew.FromMM(0.01)  # polygon approximation of a pad/via outline
MAX_PASSES = 3  # passes allowed to change the board before it is called an error


def _fill_zones(board):
    """Flow every zone. Run before the analysis as well as after it: the analysis
    reads filled copper, so on a board whose zones are unfilled every stitching via
    would look orphaned and every teardrop would look like it decorates nothing,
    and the cleanup would strip both. The pour is filled by the time the pipeline
    calls this, so the pre-pass is a no-op there and only guards a hand run."""
    pcbnew.ZONE_FILLER(board).Fill(board.Zones())


def _dead_vias(vias, live_tracks, pads, zones):
    """Vias reaching copper on fewer than two layers: they connect nothing."""
    doomed = []
    for v in vias:
        p, net = v.GetPosition(), v.GetNetCode()
        reached = sum(
            1 for layer in (v.TopLayer(), v.BottomLayer()) if connected(p, layer, net, live_tracks, pads, zones, v)
        )
        if reached < 2:
            doomed.append(v)
    return doomed


def _redundant_vias(vias, pads):
    """Vias duplicating copper that already joins the same layers: a second via at
    the same spot, or a plated through-hole pad of the net (its barrel is already a
    layer-to-layer connection, so a via inside it is an extra drill hit)."""
    doomed = []
    for i, v in enumerate(vias):
        p, net = v.GetPosition(), v.GetNetCode()
        if any(dist(p, other.GetPosition()) <= TOUCH_TOL and other.GetNetCode() == net for other in vias[:i]):
            doomed.append(v)
            continue
        if any(
            pad.GetAttribute() == pcbnew.PAD_ATTRIB_PTH and pad.GetNetCode() == net and pad.HitTest(p) for pad in pads
        ):
            doomed.append(v)
    return doomed


def _tracks_in_pads(tracks, pads):
    """Tracks buried in a pad of their own net: the pad already carries the copper.
    Both ends inside means the whole track is inside for every stock pad shape
    (circle, oval, rect, roundrect: all convex), so custom-shaped pads, which need
    not be convex, are skipped rather than guessed at."""
    doomed = []
    for t in tracks:
        if is_via(t):
            continue
        layer, net = t.GetLayer(), t.GetNetCode()
        if any(
            pad.GetShape() != pcbnew.PAD_SHAPE_CUSTOM
            and pad.GetNetCode() == net
            and pad.IsOnLayer(layer)
            and pad.HitTest(t.GetStart())
            and pad.HitTest(t.GetEnd())
            for pad in pads
        ):
            doomed.append(t)
    return doomed


def _duplicate_tracks(tracks):
    """Tracks laid over each other: same net, layer and path. Doubled copper is
    invisible to DRC (same net, same place) and outlives every other rule here,
    since each copy covers the other's ends and so props it up. The widest of a set
    is kept, in case an edit widened one copy and left the old one underneath."""
    seen = {}
    doomed = []
    for t in tracks:
        if is_via(t):
            continue
        ends = tuple(sorted((p.x, p.y) for p in (t.GetStart(), t.GetEnd())))
        mid = (t.GetMid().x, t.GetMid().y) if t.GetClass() == "PCB_ARC" else None
        key = (t.GetNetCode(), t.GetLayer(), ends, mid)
        kept = seen.get(key)
        if kept is None:
            seen[key] = t
        elif t.GetWidth() > kept.GetWidth():
            seen[key] = t
            doomed.append(kept)
        else:
            doomed.append(t)
    return doomed


def _covered_tracks(tracks, doomed_ids):
    """Segments buried inside another segment of their own net: same layer, both
    ends on the other's centreline, and no wider than it. Those three together mean
    every point of this segment's copper is already inside the other's, so deleting
    it moves no copper and can strand nothing: whatever touched it still touches
    what covered it.

    The path rule above cannot see these, since a buried segment and its cover
    share neither endpoint and so never collide in its key. They arrive as the
    footprints' `include_traces_vias` stubs, when a route happens to run along a
    stub instead of picking it up: the stub is not dangling (both ends sit on the
    route's copper) and not buried in a pad, so every other rule here passes it
    too, and doubled copper of exactly the kind this file exists to remove reaches
    the master, invisible to DRC because it carries its own net.

    Straight segments only, as cover and as covered. An arc is buried only if it
    shares the other's circle as well as its extent, which is a different test, and
    a chord is never inside its own arc.
    """
    segments = [t for t in tracks if t.GetClass() == "PCB_TRACK" and id(t) not in doomed_ids]
    doomed = []
    dead = set(doomed_ids)
    for a in segments:
        for b in segments:
            # A pair that buries each other is identical, so the path rule has
            # already taken one of them; skipping the dead as covers is what keeps
            # this from taking the survivor too.
            if a is b or id(b) in dead:
                continue
            if a.GetNetCode() != b.GetNetCode() or a.GetLayer() != b.GetLayer() or a.GetWidth() > b.GetWidth():
                continue
            if all(point_to_segment(p, b.GetStart(), b.GetEnd()) <= TOUCH_TOL for p in (a.GetStart(), a.GetEnd())):
                doomed.append(a)
                dead.add(id(a))
                break
    return doomed


def _doomed(board):
    """One pass of every deletion rule, as (tracks, vias)."""
    tracks = list(board.GetTracks())
    pads = copper_pads(board)
    zones = fill_zones(board)

    doomed_tracks = _duplicate_tracks(tracks)
    doomed_ids = ids(doomed_tracks)
    for t in _covered_tracks(tracks, doomed_ids):
        doomed_tracks.append(t)
        doomed_ids.add(id(t))
    # Judge the rest against a board the duplicates have already left, so a track
    # only its own twin held up is seen as dangling in this same pass.
    survivors = [t for t in tracks if id(t) not in doomed_ids]
    for t in dangling_tracks(survivors, pads, zones) + _tracks_in_pads(survivors, pads):
        if id(t) not in doomed_ids:
            doomed_tracks.append(t)
            doomed_ids.add(id(t))

    live = [t for t in tracks if id(t) not in doomed_ids]
    vias = [t for t in tracks if is_via(t)]
    doomed_vias = _dead_vias(vias, live, pads, zones)
    doomed_ids = ids(doomed_vias)
    doomed_vias += [v for v in _redundant_vias(vias, pads) if id(v) not in doomed_ids]
    return doomed_tracks, doomed_vias


def _mergeable(a, b, junction, tracks, pads):
    """True if segments a and b can become one segment through `junction`: same
    net/layer/width, nothing else meeting them there, and collinear to within
    TOUCH_TOL (so the merge moves no copper a fab could resolve)."""
    if a.GetNetCode() != b.GetNetCode() or a.GetLayer() != b.GetLayer() or a.GetWidth() != b.GetWidth():
        return False
    layer, net = a.GetLayer(), a.GetNetCode()
    if any(t is not a and t is not b and t.IsOnLayer(layer) and covers(junction, layer, t) for t in tracks):
        return False
    if any(pad.GetNetCode() == net and pad.IsOnLayer(layer) and pad.HitTest(junction) for pad in pads):
        return False
    return point_to_segment(junction, _far_end(a, junction), _far_end(b, junction)) <= TOUCH_TOL


def _far_end(track, junction):
    """The endpoint of `track` that is not the junction."""
    return track.GetEnd() if dist(track.GetStart(), junction) <= TOUCH_TOL else track.GetStart()


def _merge_collinear(board):
    """Re-join segments an edit split. Returns the number of segments removed."""
    merged = 0
    while True:
        tracks = list(board.GetTracks())
        pads = copper_pads(board)
        segments = [t for t in tracks if t.GetClass() == "PCB_TRACK"]
        pair = None
        for i, a in enumerate(segments):
            for b in segments[i + 1 :]:
                for pa in (a.GetStart(), a.GetEnd()):
                    if not any(dist(pa, pb) <= TOUCH_TOL for pb in (b.GetStart(), b.GetEnd())):
                        continue
                    if _mergeable(a, b, pa, tracks, pads):
                        pair = (a, b, pa)
                        break
                if pair:
                    break
            if pair:
                break
        if not pair:
            return merged
        a, b, junction = pair
        a.SetStart(_far_end(a, junction))
        a.SetEnd(_far_end(b, junction))
        board.RemoveNative(b)
        merged += 1


def _item_poly(item, layer):
    poly = pcbnew.SHAPE_POLY_SET()
    item.TransformShapeToPolygon(poly, layer, 0, ARC_ERROR, pcbnew.ERROR_INSIDE)
    return poly


def _orphan_teardrops(board):
    """Teardrop zones with none of their own copper left under them. A teardrop is
    a flare on a track-to-pad/via junction; delete the via and the flare is an
    island of copper decorating nothing, which no DRC severity and no
    teardrop-count gate reports. Tested by polygon overlap against the surviving
    tracks, vias and pads of the teardrop's net (pours are excluded: a GND flare
    sits inside the GND plane and would always look anchored)."""
    teardrops = [z for z in board.Zones() if z.IsTeardropArea()]
    if not teardrops:
        return []
    items = list(board.GetTracks()) + copper_pads(board)
    orphans = []
    for z in teardrops:
        layer, net, box = z.GetLayer(), z.GetNetCode(), z.GetBoundingBox()
        filled = z.GetFilledPolysList(layer)
        anchored = False
        for item in items:
            if item.GetNetCode() != net or not item.IsOnLayer(layer):
                continue
            if not box.Intersects(item.GetBoundingBox()):
                continue
            overlap = pcbnew.SHAPE_POLY_SET(filled)
            overlap.BooleanIntersection(_item_poly(item, layer))
            if overlap.OutlineCount():
                anchored = True
                break
        if not anchored:
            orphans.append(z)
    return orphans


def _cleanup_pass(board):
    """Every rule once: the deletions to a fixpoint, then the merge, then the
    teardrops the deletions stranded, then a re-pour if any of it went. Returns the
    four counts, all zero on a board this pass found nothing to do to."""
    removed_tracks = removed_vias = 0
    while True:
        doomed_tracks, doomed_vias = _doomed(board)
        if not doomed_tracks and not doomed_vias:
            break
        for item in doomed_tracks + doomed_vias:
            # RemoveNative, not Remove: Remove hands ownership to Python, which has
            # no destructor for a PCB_TRACK and reports every one as a leak at exit.
            board.RemoveNative(item)
        removed_tracks += len(doomed_tracks)
        removed_vias += len(doomed_vias)

    merged = _merge_collinear(board)
    # Only a removal can strand a teardrop, so the untouched board skips this scan.
    orphans = _orphan_teardrops(board) if removed_tracks or removed_vias else []
    for z in orphans:
        board.RemoveNative(z)

    if removed_tracks or removed_vias or merged or orphans:
        _fill_zones(board)  # re-pour around the freed copper, before the next pass reads it
    return removed_tracks, removed_vias, merged, len(orphans)


def cleanup_tracks(path):
    board = pcbnew.LoadBoard(path)
    if any(not z.IsFilled() for z in board.Zones() if not z.GetIsRuleArea()):
        note(f"  filling {path}: unfilled zone(s), flowed before analysis")
        _fill_zones(board)

    totals = [0, 0, 0, 0]
    # run is read after the loop to report how many passes it took, which B007
    # does not see because it only looks inside the body.
    for run in range(1, MAX_PASSES + 1):  # noqa: B007
        counts = _cleanup_pass(board)
        if not any(counts):
            break
        totals = [total + count for total, count in zip(totals, counts, strict=False)]
    else:
        raise SystemExit(
            f"ERROR {path}: still cleaning up after {MAX_PASSES} passes\n"
            f"    the last pass removed {counts[0]} track(s), {counts[1]} via(s) and "
            f"{counts[3]} teardrop(s), and merged {counts[2]} segment(s)"
        )

    if not any(totals):
        note(f"  unchanged {path}: nothing to clean up")
        return

    board.Save(path)
    print(
        f"  CLEANED {path}: removed {totals[0]} dangling/buried/duplicate track(s), "
        f"{totals[1]} unconnected/redundant via(s) and {totals[3]} stranded teardrop(s), "
        f"merged {totals[2]} split segment(s) over {run - 1} pass(es), zones re-filled"
    )


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    for p in sys.argv[1:]:
        cleanup_tracks(p)
