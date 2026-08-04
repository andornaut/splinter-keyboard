#!/usr/bin/env python3
"""Shared copper-connectivity helpers: does anything touch this point?

cleanup-tracks.py deletes the copper nothing connects to, and add-gnd-zone.py
must not score a pour layer on copper cleanup is about to delete. Both ask the
same question, so both ask it here and get the same answer.

Not an entry point: import it, do not run it.
"""
from pcbnew_quiet import pcbnew

TOUCH_TOL = pcbnew.FromMM(0.001)  # coincidence slack on top of the copper's own width
VIA_CLASS = "PCB_VIA"


def is_via(item):
    return item.GetClass() == VIA_CLASS


def ids(items):
    """Identity set for membership tests. Never use `item in items` on board items:
    PCB_TRACK.__eq__ compares by value, so a doomed track's twin (two segments laid
    over each other, which happens and is exactly what cleanup is for) tests as a
    member too, and the survivor is dropped along with it."""
    return {id(i) for i in items}


def dist(p, q):
    return ((p.x - q.x) ** 2 + (p.y - q.y) ** 2) ** 0.5


def point_to_segment(p, a, b):
    """Distance from p to segment ab."""
    dx, dy = b.x - a.x, b.y - a.y
    span = dx * dx + dy * dy
    if span == 0:
        return dist(p, a)
    t = max(0.0, min(1.0, ((p.x - a.x) * dx + (p.y - a.y) * dy) / span))
    return (((a.x + t * dx) - p.x) ** 2 + ((a.y + t * dy) - p.y) ** 2) ** 0.5


def covers(p, layer, track):
    """True if p lies on this track's copper on `layer`. A via is its annular ring
    there, which needs the layer because PCB_VIA sizes per layer. An arc is handed
    to its own HitTest, which follows the true curve, so a track branching off the
    middle of one is seen (Freerouting and KiCad's arc mode both emit arc tracks,
    and copy-traces carries them)."""
    if is_via(track):
        return dist(p, track.GetPosition()) <= track.GetWidth(layer) / 2 + TOUCH_TOL
    if track.GetClass() == "PCB_ARC":
        return track.HitTest(p, TOUCH_TOL)
    return point_to_segment(p, track.GetStart(), track.GetEnd()) <= track.GetWidth() / 2 + TOUCH_TOL


def copper_pads(board):
    """Every pad that is actually copper. NPTH pads (the mounting holes and the
    TRRS locating holes) are bare drilled holes, but they still report a copper
    layer and hit-test like a land, so a track ending in one would read as
    connected. Type, not plating, is the discriminator: IsPlated() is true only for
    a plated hole, so it passes every SMD land."""
    return [p for p in board.GetPads() if p.GetAttribute() != pcbnew.PAD_ATTRIB_NPTH]


def fill_zones(board):
    """Every filled copper pour. Rule areas carry no copper, and a teardrop is not
    independent copper: it is a flare on the very track/via under test, so counting
    it would let a dangling stub hold itself up."""
    return [z for z in board.Zones()
            if not z.GetIsRuleArea() and not z.IsTeardropArea() and z.IsFilled()]


def connected(p, layer, net, tracks, pads, zones, skip):
    """True if copper of `net` other than `skip` covers p on `layer`. Everything is
    net-checked: copper of another net crossing this point is a clearance violation,
    not a connection, and treating it as one would keep dead copper alive."""
    for t in tracks:
        if t is not skip and t.GetNetCode() == net and t.IsOnLayer(layer) and covers(p, layer, t):
            return True
    for pad in pads:
        if pad.GetNetCode() == net and pad.IsOnLayer(layer) and pad.HitTest(p):
            return True
    return any(z.GetNetCode() == net and z.IsOnLayer(layer) and z.HitTestFilledArea(layer, p)
               for z in zones)


def dangling_tracks(tracks, pads, zones):
    """The tracks in `tracks` with a start or end no other copper touches. Vias are
    skipped (a via has no free end; it is judged by how many layers it reaches).

    Pass a filled-pour zone list to count the pour as copper, which is what keeps a
    GND stitching via's stub; pass [] before a board is poured, where only the
    pour's own net could be affected."""
    doomed = []
    for t in tracks:
        if is_via(t):
            continue
        layer, net = t.GetLayer(), t.GetNetCode()
        if any(not connected(p, layer, net, tracks, pads, zones, t)
               for p in (t.GetStart(), t.GetEnd())):
            doomed.append(t)
    return doomed
