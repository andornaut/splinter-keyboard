#!/usr/bin/env python3
"""Shared copper geometry: does anything touch this point, and may copper go here?

cleanup-tracks.py deletes the copper nothing connects to, and add-gnd-zone.py
must not score a pour layer on copper cleanup is about to delete. Both ask the
same question, so both ask it here and get the same answer.

tidy-slivers.py and tidy-patterns.py are the two steps that MOVE copper, and each
has to ask both halves of "may this copper go here" before it changes the board:
`clearance_blocker` for whether the copper would crowd another net, and
`keepout_blocker` for whether it may be there at all. Both take the same
proposals, so a caller builds them once and asks both.

Not an entry point: import it, do not run it.
"""

from .pcbnew_quiet import pcbnew

TOUCH_TOL = pcbnew.FromMM(0.001)  # coincidence slack on top of the copper's own width
VIA_CLASS = "PCB_VIA"


def net_class(board, name):
    """The named net class, read from the board's own project.

    apply-project-settings.py is what writes the net classes into the `.kicad_pro`,
    so a step needing one of their values must ask the board rather than restate
    the number: a second copy goes stale the moment the project is retuned, and
    nothing reports it. A step comparing against a stale width simply stops
    matching anything and does nothing, silently.

    Missing is a hard error, not a default, for the same reason: falling back
    would let the step run on against a value the board does not use.

    The keys are normalized because GetAllNetClasses() mixes types: the built-in
    class comes back as a str and every added one as a wxString, which neither
    compares nor hashes equal to the same text as a str. Looking a name up
    directly therefore finds "Default" and misses every custom class."""
    classes = {str(key): value for key, value in board.GetAllNetClasses().items()}
    if name not in classes:
        raise SystemExit(
            f"ERROR {board.GetFileName()}: no '{name}' net class in this board's project\n"
            f"    found {sorted(classes)}; apply-project-settings.py writes them, and"
            f" must run on a stage before any step that reads them"
        )
    return classes[name]


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
    return (
        point_to_segment(p, track.GetStart(), track.GetEnd())
        <= track.GetWidth() / 2 + TOUCH_TOL
    )


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
    return [
        z
        for z in board.Zones()
        if not z.GetIsRuleArea() and not z.IsTeardropArea() and z.IsFilled()
    ]


def connected(p, layer, net, tracks, pads, zones, skip):
    """True if copper of `net` other than `skip` covers p on `layer`. Everything is
    net-checked: copper of another net crossing this point is a clearance violation,
    not a connection, and treating it as one would keep dead copper alive."""
    for t in tracks:
        if (
            t is not skip
            and t.GetNetCode() == net
            and t.IsOnLayer(layer)
            and covers(p, layer, t)
        ):
            return True
    for pad in pads:
        if pad.GetNetCode() == net and pad.IsOnLayer(layer) and pad.HitTest(p):
            return True
    return any(
        z.GetNetCode() == net and z.IsOnLayer(layer) and z.HitTestFilledArea(layer, p)
        for z in zones
    )


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
        if any(
            not connected(p, layer, net, tracks, pads, zones, t)
            for p in (t.GetStart(), t.GetEnd())
        ):
            doomed.append(t)
    return doomed


def clearance_blocker(tracks, pads, proposals, replaced=()):
    """The first item of another net that a piece of copper about to be laid down
    would sit too close to, as (item, clearance it wanted), or None.

    A proposal is `(layer, net_code, clearance, shape)`: where the copper will be,
    not where it is. The caller has to ask before changing the board, because a
    refused move must leave no trace. `replaced` holds the ids of the items the
    proposals stand in for, which are not measured against themselves.

    This is the check MAX_MOVE-style caps cannot do. Moving one endpoint of a
    segment pivots the whole segment about its far end, so copper swings along its
    entire length, millimetres away from the edit; on a run already close to
    another net a move of microns is enough to break clearance.

    Zones are not measured: the pour re-flows around whatever the copper becomes.
    """
    others = [t for t in tracks if id(t) not in replaced] + list(pads)
    for layer, net, clearance, shape in proposals:
        for other in others:
            if other.GetNetCode() == net or not other.IsOnLayer(layer):
                continue
            gap = max(clearance, other.GetOwnClearance(layer))
            if not shape.BBox(gap).Intersects(other.GetBoundingBox()):
                continue
            if shape.Collide(other.GetEffectiveShape(layer), gap):
                return other, gap
    return None


def keepout_blocker(zones, proposals):
    """The first rule area that a piece of copper about to be laid down would enter,
    or None. Proposals are the `(layer, net_code, clearance, shape)` the clearance
    test takes, so a caller builds them once and asks both questions of them.

    A rule area is not copper, so clearance_blocker cannot see one. This is the
    check that binds hardest on the largest moves: the deviations a move must not
    flatten are mostly detours drawn around these zones, and pulling one back puts
    copper inside the zone the detour was drawn to avoid.

    Intrusion, not clearance: KiCad reports items_not_allowed for copper that enters
    the area and passes copper that merely runs alongside it, so the test asks for a
    gap of zero and refuses exactly what DRC would.

    Only the areas that disallow tracks are consulted, since a move lays nothing
    else. The perimeter pour ring excludes the fill alone and must not veto a track:
    routing inside it is the intent.
    """
    areas = [z for z in zones if z.GetIsRuleArea() and z.GetDoNotAllowTracks()]
    for layer, _net, _clearance, shape in proposals:
        for area in areas:
            if area.IsOnLayer(layer) and shape.Collide(area.Outline(), 0):
                return area
    return None


def describe(item):
    """An item named the way its DRC violation would name it."""
    p = item.GetPosition()
    return (
        f"{item.GetClass()} [{item.GetNetname()}] at "
        f"({pcbnew.ToMM(p.x):.3f}, {pcbnew.ToMM(p.y):.3f})"
    )
