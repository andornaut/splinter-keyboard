# v4 case build sheet

Feature-by-feature recipe for modelling the case in Onshape. Design rationale is in
[README.md](./README.md); this file is the numbers.

Every position is a **dimension, not a reference**. A re-import replaces the imported
entities, so anything projected off them loses its reference while a typed value does not.
The exceptions are the switch cutouts and the boss circles, which are cut from the import
itself so they track the board.

## Terms

| Term | Means |
| --- | --- |
| **Boss** | A cylindrical pillar that takes a fastener. Three per half, hanging from the top underside down to the PCB |
| **Standoff** | The matching pillar rising from the bottom plate to the PCB underside |
| **Hull** | The un-filleted board outline, 160.000 x 119.000mm, in `full_unfilleted.dxf`. The case is modelled to this, not to the fabricated edge |
| **Recess** | The 16mm opening at the top face each switch nests into, so the surrounding wall covers its lower body |
| **Plate** | The bottom plate, always. The shell's top face is what the switches clip into, but it is never called a plate here |
| **Setup** | One fixturing of the part in the mill. Every flip is another setup and another fixed fee |

## How it goes together

```text
   top face   ------------------------------   z   0.00
                    | |            <- boss, 5.50 dia
   recess floor ----| |------------------      z  -1.50   switch flange bears here
   top underside ---+-+---------------+##+     z  -3.00
   PCB top    ------+-+---------------+##+     z  -6.00   boss ends; SHELF underside
   PCB        #######o#################|  |    <- 3.00mm NPTH
                    | |               |##|     z  -7.60   PLATE WALL top
   plate      -------#----------------+##+     M2.5 flat head, up from below
```

The board is clamped all the way round, not only at the three screws: a **shelf** hangs
from the case's top and the plate carries a matching **wall** up to meet it. The bosses and
standoffs are the same sandwich at the three screw points.

## Topology

| Part | Contents |
| --- | --- |
| **Shell** | Top face and side walls, one piece. Switch cutouts in the top, shelf inside the walls |
| **Bottom plate** | Inset closing plate with a perimeter wall, the screw heads and the standoffs |

**The shelf goes above the board, never below it.** Which side it sits on decides whether
it can be made at all. A shelf the board is pressed UP against narrows the opening going
up, which a mill reaches from below without trouble. A lip the board RESTS DOWN on would
put the full-width board pocket above a narrower lip, which is an undercut no setup
reaches, and it blocks a printed part equally since the board also goes in from below.

**The plate is inset**, finishing flush with the shell rim, so its outline is the cavity
outline less a fit clearance rather than the shell's outer profile. Deriving it from the
cavity rather than from the hull is what makes its corners match the pocket it drops into.
It consumes 1.50mm of cavity depth. No rebate is needed: the cavity is a straight extrusion
and the screws hold the plate against the stack above it. A rebate would be legal, being
wider at the open face, but it would thin the wall at the rim for nothing.

**Undercut, precisely.** Cutting from below, a feature may narrow going up but never
widen. So a chamfer or rebate at the rim is fine, and a lip under the board pocket is not.

## Machining setups

| Part | Setup | From | Features |
| --- | --- | --- | --- |
| Shell | 1 | below | Outer profile, cavity, bosses, boss holes |
| Shell | 2 | above | The 16mm switch recesses, the top edge bezel |
| Shell | 3 | the top edge (+y face) | TRRS and USB openings |
| Plate | 1 | inner face | Profile, standoffs, screw holes, relief pocket |
| Plate | 2 | outer face | Counterbores, bumper recesses |

**Setup 3 is not optional.** Both ports are holes through a vertical wall, and a 3-axis
mill reaches those from neither above nor below. A right-angle head folds it back into
setup 1 if the shop has one; otherwise it is a third fixturing. Both ports sit on the same
face, so one setup covers both.

The plate's two setups are inherent to it having features on both faces.

The nested switch cutout is inherently wider at the top, so nothing reaches it from below.
The 14.5mm holes are through-features and can be cut in setup 1 or 2. Flattening the top
to a single 14.5mm hole would drop setup 2, at the cost of the switch sitting proud on a
flat face.

**Quote both variants before deciding.** The recesses are ~10-25 minutes of spindle time,
so the adder is dominated by the fixed cost of re-fixturing, and a shop may plan the op
regardless. Hollowing the block likely dominates the part cost either way. If the delta is
large, flatten the top for the aluminium variant only and keep the nesting on the print.

## Decisions this sheet assumes

| Decision | Assumed |
| --- | --- |
| Process | Print first, then aluminium; the printed half confirms fitment |
| Print orientation | Shell top-face-down; walls and bosses rise from a flat first layer, no supports |
| Wall thickness | 3.0mm |
| Top thickness | 3.0mm, recessed to 1.5mm at each switch |
| Cavity internal fillet | 2.0mm nominal, **2.35mm absolute maximum** |
| Board pocket clearance | 0.25mm per side on the hull |

**The cavity fillet is a maximum, not a minimum.** It is an internal corner, so the tool
leaves material *inside* the pocket, and that material has to miss the board's own 1.5mm
exterior fillet. Do not let a shop substitute a larger end mill.

| Cavity fillet | Clearance to the fabricated board at a 90 deg pocket corner |
| --- | --- |
| 1.50 | +0.354 |
| 2.00 | +0.146 |
| 2.35 | +0.001 |
| 3.00 | -0.268 |

## Frame

Outline centre at the origin, +x toward the inner (thick) edge, +y up, z=0 at the shell's
top face, +z up.

Positions read off the KiCad board are in the *filleted* frame and gain **+0.205mm in y**
to convert, since the fillet shortens the board 0.410mm and moves its bbox centre half of
that. Every value here is already converted.

| | Value |
| --- | --- |
| Hull, per half | 160.000 x 119.000 |
| `Edge.Cuts`, as fabricated | 160.000 x 118.590 |
| Top edge / bottom edge | y +59.500 / -59.500 |
| Side edges | x +-80.000 |

The 1.5mm wall fillet rounds the corners, so the fabricated height drops while the width
holds at the straight side edges. The case is modelled to the hull, never to that edge.

## Z stack

| Level | z |
| --- | --- |
| Shell top face | 0.00 |
| Recess floor; switch flange bears here | -1.50 |
| Top underside; 1.50mm switch plate above | -3.00 |
| PCB top face; boss ends here | -6.00 |
| PCB bottom face | -7.60 |
| Bottom plate top face, inner edge | -14.50 |
| Shell bottom rim / plate underside, inner edge | -16.00 |

**Specify the two edge heights, not the angle: 16.00mm inner, 12.00mm outer.** Over the
166.50mm shell that is 1.3762 deg, but the angle is derived. If the wall thickness
changes, the case width changes with it and the angle follows while the heights stay put.

The bottom slopes, so the last two rows are at the inner edge; at the outer edge the rim
is at -12.00. Usable cavity below the PCB runs **6.82mm at the inner edge to 2.98mm at the
outer**, measured at the board edges rather than the shell's.

**What the taper costs.** 1.3762 deg is not a working tent angle, so the slope is there for
the look, and it buys that at the price of three standoff heights, two screw lengths, and
putting the tightest clearance in the design on the shallow side. A flat 15.50mm case would
give the Liatris +1.00, the jack +1.20 and the socket +4.55 with one standoff height and
one screw length. Recorded so the trade is visible, not as a proposal.

## Parameters

| Parameter | Value | Source |
| --- | --- | --- |
| Wall thickness | 3.00 | decision |
| Top thickness | 3.00 | decision |
| Switch recess depth | 1.50 | nesting |
| Plate at a switch cutout | 1.50 | MX standard, 1.5mm +-0.1mm |
| Bottom plate | 1.50 | takes the flat head's full height |
| Board pocket | 160.50 x 119.50 | hull + 0.25/side; the board itself is 0.455/side loose in y |
| Shell outer profile | 166.50 x 125.50 | pocket + wall |
| Boss and standoff diameter | 5.50 | = 2 x `screw_boss_radius`, the DXF's own circle |
| Boss height | 3.00 | top underside to PCB |
| Material above the PCB at a boss | 6.00 | top 3.00 + boss 3.00; **4.50 where a recess overlaps** |
| Insert hole, printed | 3.60 dia | M2.5 melt diameter; depth is per boss, see below |
| Tapped hole, machined | 2.05 tap drill, M2.5x0.45 | same per-boss depths |
| Screw | M2.5 button head, ISO 7380 | head 4.70 dia x 1.50, **flat underside**; two lengths, see below |
| Screw clearance in the plate | 2.90 dia | |
| Counterbore in the plate | 5.00 dia x 1.50 deep, **flat bottomed** | head + 0.30; floor is the standoff base |
| Perimeter shelf, on the shell | 2.00 wide, underside at -6.00 | = the board's own keepout ring |
| Perimeter wall, on the plate | 2.00 wide, top at -7.60 | meets the shelf through the board |
| Wall relief | none inward of x +-50.00 above y +45.00 | the MCU, the jack and both ports are there |
| Flared standoff base | 8.00 dia, up to -9.75 | = the built v4 lid; gives the counterbore a 1.50 annulus |
| Switch cutout / recess | 14.50 / 16.00, R1.00 corners | see below |
| Top outer edge bezel | 1.00 x 45 deg | one chamfer pass; the switch recesses stay square |

**The wall stops short of the top-inner corner.** Everything hanging below the board is
there, the MCU and the jack, and so are both ports. A wall running the full perimeter sits
on the jack's body and blocks both plugs.

**The standoff needs a flared base.** The counterbore runs the plate's full thickness, so
without a flare a 5.00 bore inside a 5.50 standoff joins the two by a 0.25mm annulus, 4.12
mm2 per boss: the head bears on the standoff and the plate hangs off that ring, which on an
FDM part is under one extrusion width. Flaring the base to 8.00 makes it 1.50mm and 30.63
mm2, seven times the area. The built v4 lid uses 8.00 as well.

**Height is what constrains a flare, not diameter.** It stops under the hotswap sockets
hanging 1.85 below the board, and every pad it would otherwise have to dodge is above it,
so the 2.04mm inner-pinky pad clearance that caps the standoff does not cap this. Stopping
at -9.75 leaves 0.30 to the sockets. Do not let it reach them: that clearance is the only
thing between the flare and a part.

**The 14.50 cutout is not slack.** An internal corner rounds *into* the void, so an R1.00
corner cut into a 14.00 hole would bind a switch by 0.207mm. At 14.50 it clears by 0.146mm
against a 14.00 section with 0.5mm corner radii. The switch is located by the 16.00 recess,
not by this hole.

### Screw bosses

Left half, from the outline centre. The right half is the exact mirror (negate x).

| Boss | Position | Standoff height | Standoff + PCB | Bore depth | Screw | Engagement |
| --- | --- | --- | --- | --- | --- | --- |
| Outer pinky | (-42.375, -3.650) | 3.88 | 5.48 | 5.00 | M2.5x10 | 4.52 |
| Inner pinky | (33.825, 0.050) | 5.71 | 7.31 | **4.00** | M2.5x11 | 3.69 |
| Centre | (-3.325, 22.175) | 4.82 | 6.42 | **4.00** | M2.5x10 | 3.58 |

**The plate is not in the stack.** A flat-underside head bears on the counterbore floor,
which is the standoff's base, and its length is measured from there. A countersunk head
would have added the plate's 1.50 to every row and needed a longer screw.

**Any flat-underside head works; the counterbore diameter is what follows from the choice.**
5.00 suits a 4.70 head (button ISO 7380, socket cap DIN 912) with 0.30 to spare, and leaves
0.25 of standoff outside it. A 5.00 pan head needs 5.30, which leaves 0.10 and a knife edge
on the standoff, so grow the standoff if you go that way. Head height decides flushness
only: 1.50 finishes level with the plate, 1.70 stands 0.20 proud, and neither affects the
screw length, since that is measured under the head.

The outer pair sits 3.70mm apart in y. That is forced: the pinky columns are asymmetric,
so the two screws cannot share a y while clearing both switch holes and pads. Do not level
them.

**Two bosses take a 4.00 bore, not 5.00.** A 16.00 switch recess overlaps the inner-pinky
and centre bosses, so the material above them is 1.50 (top left over the recess) + 3.00
(boss) = 4.50, not 6.00. A 5.00 bore breaks out into the recess floor:

| Boss | Recess edge from the boss axis | 1.80 bore radius | Breakout |
| --- | --- | --- | --- |
| Inner pinky | 1.745 | 1.80 | 0.88 x 0.06mm |
| Centre | 1.695 | 1.80 | 1.21 x 0.11mm |

The placement rule holds the boss clear of the 14.50 **hole** (tangent on both halves at
these two), which is what stops the boss fouling the switch body. It says nothing about the
16.00 **recess** above, which is what the bore has to miss.

**The bosses mirror; the key field they sit in does not.** On the right half a recess also
clips the outer-pinky boss, putting its recess edge 2.25mm from the bore axis against a
1.80 bore radius. That is 0.45mm of wall over the bore's top 0.50mm, where the left half
has 1.12mm. No breakout either way, so the 5.00 bore stands, but do not read the table's
"exact mirror" as covering what surrounds them, and see the printed-insert risk below.

`gen-case.py` hard-errors on a bore that reaches the recess band without clearing the
recess wall, so this table cannot go stale against the key field. Readback cannot cover
it: a breakout trims the bore's face without splitting it or changing its height, so the
depth check and the face census both pass a shell that has one.

**The standoffs are three different heights** because the plate is sloped, so the three
screws see stacks from 5.48 to 7.31mm. Two lengths cover it, as tabulated: every screw
takes at least 3.00mm of thread and none bottoms in its bore. Do not try to absorb the
spread in the counterbore: it is 1.50 deep and the head is 1.50 tall, so there is no depth
to give.

**Clearance to the nearest side-B pad**: 3.54mm outer pinky, **2.04mm inner pinky**,
3.98mm centre. Those are measured to the pads, and the Kailh socket body is larger than
its lands, so the real gap at the inner pinky is smaller by an unknown amount. That is why
the standoff is 5.50 and not larger.

### Ports, on the top edge

| Feature | Position |
| --- | --- |
| USB-C notch, already in the outline | x +56.663 .. +66.663, cut 7.271mm down from y +59.500 |
| TRRS jack centre | (74.650, 59.500) |

**Both parts mount on side B, so both openings sit entirely below the PCB.** Neither is
anywhere near the z=-6.00 board plane, which is the mistake to avoid.

| Opening | Size | Centre z | Source |
| --- | --- | --- | --- |
| TRRS, round | 5.50 dia | **-10.50** | measured off the built v4 case |
| USB-C, through the wall | 9.50 w x 4.00 h | **-10.25** | measured on a printed part of this design; width is the cavity notch |

**The heights are measured, never derived.** The built v4 case shares this z stack exactly
(top face 0, top underside -3.00, PCB -6.00 to -7.60), so its port centres transfer
directly, and the TRRS is taken straight from it. The USB sits 0.50 higher than that case
carries: the inherited height printed low on this design. Re-measure on hardware before
changing either, and treat the TRRS as due for the same check, since it comes from the same
source as the height that moved.

Add 0.3-0.4mm printed, 0.2-0.3mm machined. **Both are plain cutouts straight through the
wall.** No counterbore and no recess: a pocket on the outer face reads as the port being
sunk into the case rather than opened through it.

The cost is cable boots. The connector sits back from the case face and a USB-C plug shell
is only about 6.5mm long, so a cable with a fat overmold may bottom on the outer face
before it seats. Settle it on the printed half with the cables you actually own; a
13.00 x 7.00 x 1.50 counterbore on the outer face is the fix if one of them will not go.

**Why 9.50 wide.** It sits inside the board's own 10.00 notch, so the plug clears the board
edge, and it clears an 8.34mm plug shell by 0.58 per side.

Wall left below each opening: 2.54mm at the TRRS, 3.23mm at the USB. The TRRS is thin
enough that a printed shell wants an extra perimeter there.

**Nothing in the case follows the board's USB notch.** Not the outer profile, not the
cavity, not the plate. That notch clears the plug's overmold, which sits below the board
entirely, so to the case it is only a bite out of an edge that should run straight.
Inheriting it puts a jog in all three outlines and leaves a pointless tongue of material in
the pocket. Fill it in the hull before offsetting any of them. The result is a void where
the board is absent, which costs nothing and gives the plug more room rather than less: the
top edge is straight and both ports are simply openings in the back wall.

## Part A: shell

1. **Sketch "Outline (imported)"**, Top plane. Insert
   `dist/v4/ergogen/outlines/full_unfilleted.dxf`. Constrain the left half's outline centre
   to the origin. **Never draw in this sketch**; re-importing is the only edit it should
   take.
2. **Extrude "Shell body"**, the left-half outline region offset outward **3.25mm**
   (clearance + wall), blind **16.00mm** at the inner edge, -Z, bottom face sloped down to
   **12.00mm** at the outer edge.
3. **Extrude cut "Cavity"**, the same region offset outward **0.25mm**, from **z -3.00**
   down through the open bottom. Fillet its vertical corners at **2.0mm, 2.35mm maximum**.
4. **Extrude cut "Switch recesses"**, the 16.0mm curves from the import, top face down to
   **z -1.50**.
5. **Extrude cut "Switch cutouts"**, the 14.5mm curves from the import, through the
   remaining 1.50mm. Cut both sets **as imported**: they carry the correct corner fillets,
   and the two halves' patterns differ.
6. **Bezel**, 1.00 x 45 deg on the top face's outer edge only. The recess openings stay
   square: the nesting look depends on the switch meeting a crisp edge.
7. **Bosses**, on the top underside: three circles r **2.75** at the positions above,
   extruded down **3.00mm** to the PCB top face.
8. **Boss holes**, from each boss's lower face upward, 3.60 dia (or the 2.05 tap drill),
   **to the per-boss depth in the boss table**: 5.00 outer pinky, 4.00 the other two.
9. **Port openings** cut straight through the side wall.

The USB notch needs no step; it is in the imported profile and (2) carries it through.

## Part B: bottom plate

1. **Extrude**, the left-half outline region offset outward **0.10mm** (cavity less a
   0.15mm fit clearance), **1.50mm** thick, lying in the sloped bottom plane and flush
   with the rim.
2. **Standoffs**, r **2.75** at the three boss positions, rising to the PCB underside at
   z -7.60. Heights are in the boss table.
3. **Screw holes**, 2.90 dia, each with a flat-bottomed 5.00 counterbore through the
   plate's full 1.50mm. The floor is the standoff's base, so the standoff keeps its
   height and nothing is cut into it.
4. **Relief pocket**, on the inner face, **0.75mm deep**, one plain rectangle over
   x **+50.25 .. +77.60**, y **+23.35 .. +58.60**. Leaves 0.75mm of plate.
5. **Bumper recesses**, 8.00 dia x 0.50 deep on the outer face at (-70, +50), (+45, +50),
   (-70, -32), (+65, -50). Floor **parallel to the plate faces**, so the depth is 0.50 and
   the plate left is 1.00 right across every foot. All are well clear of the three screw
   heads.

**Only the screw counterbore has a horizontal floor.** The plate is a parallel-sided slab
lying at 1.3762 deg, so "flat" and "level" are different instructions here and each feature
has to say which it means. The counterbore means level: the screw axis is vertical and a
flat head seats square to its own axis, so its floor is horizontal and its depth below the
outer face therefore varies 1.447 to 1.553 across its width. Every other feature means
parallel to the faces. A bumper recess cut level instead would run 0.417 to 0.585 deep and
leave 1.084 to 0.916 of plate, different at each edge of every foot.

**Keep every bumper out of the relief pocket.** The two cut opposite faces, so an overlap
leaves 0.25mm of plate, and leaves it directly under the parts the relief is there for.
Nothing fits between the pocket and the plate edge in the top-inner corner, which is why
the top-edge bumper sits at x +45.00 rather than out at +70.00 with its opposite number.
`gen-case.py` hard-errors on an overlap; readback cannot see one, since both features are
present, the right size, at the right depth, and the plate is still one closed solid.

**The relief pocket is not optional on an aluminium plate.** The MCU stack has +0.77mm of
nominal clearance and +0.03mm if the module bottoms out in its sockets, and the plate would
be a conductor that close to exposed pin tails. The pocket takes the worst case to +1.52mm
and costs nothing to machine in the same setup.

**One rectangle, covering the Liatris and the jack together**, rather than a pocket each
with an island between them: it is meant to be lined with tape, and a plain rectangle takes
a strip.

**The margin around the parts is one-sided, and has to be.** Inward the pocket runs over
bare board and carries 2.58 in x and 3.00 in y, comfortably past the 0.46 of board
registration play, so a part cannot end up standing over full-thickness plate. Outward
there is nowhere to buffer into, because both parts run out to the board's own top edge and
the plate ends 0.10 past it. Every limit here is set by the plate, not by the parts:

| Edge | Limit | Set by |
| --- | --- | --- |
| x +50.25 | 2.58 clear of the Liatris | the top perimeter wall survives inboard of x +50.00, and a pocket at its foot would undercut it |
| y +23.35 | 3.00 clear of the Liatris | free; nothing is near |
| x +77.60 | 0.18 short of the jack body | the perimeter wall runs at 78.10 below y 45, same undercut |
| y +58.60 | 0.90 short of the board edge | a 1.00 rim at the plate edge |

**The wall is what bounds the pocket on three sides.** It is half the board's clamp and it
stands on the plate's full thickness, so a pocket reaching its foot thins the root. That
undercut is invisible to a solid intersection test, since the wall rises from the plate's
top face while the pocket cuts down from it and the two touch without sharing volume;
`gen-case.py` tests the footprints instead, and hard-errors.

**Neither shortfall is a clearance problem.** Under the uncovered sliver of jack body the
plate is still 1.42 away, and under the uncovered top strip the Liatris is 3.76 away, its
pin tails having ended well below at y 56.54. Both are larger than the 0.75 the pocket
would add. Widening either means thinning the rim or stepping the pocket, which buys
fractions of a millimetre where there are already millimetres.

The MCU's reset and boot buttons and the board's own reset switch all face the plate;
access is by removing it, so no holes are needed.

**No support posts.** A post short enough not to lift the board off its bosses is too short
to carry anything, and typing load reaches the shell through the switch flange rather than
the PCB. The plate is unloaded.

## Right half

Mirror both parts: the outline mirrors exactly and the only half-specific geometry is the
switch cutouts. Cut those from the **right half of the DXF**, not from a mirrored copy of
the left's. The halves carry 30 and 32 switch cutouts and 14 positions have no mirrored
counterpart, so a mirrored key field is the wrong key field.

## Assembly

**Switches go into the shell first, then the board goes on.** A 15.6mm top housing cannot
pass a 14.5mm hole from below, so there is no other order: clip all 30 (or 32) switches
into the shell's top face from the outside, then bring the board up into the cavity onto
every socket at once.

The cavity is a straight bore, so the board cannot be rocked in the way a bare
plate-and-switch assembly usually is. Seat it evenly, thumb cluster last, until it meets
the shelf all the way round. Then the plate goes on and its wall closes the sandwich.

**Nothing datums the board.** The 5.50 boss butts its top face and never enters the 3.00mm
hole, and a boss cannot pilot into that hole because the 3.60 insert bore is wider than the
hole itself. Registration is therefore the looser of the pocket and the screws:

| Constraint | Play, per side |
| --- | --- |
| Pocket in x | 0.25 |
| Pocket in y | 0.455 (the fillet takes 0.410 off the board height, the pocket is cut to the hull) |
| Screw in its 3.00 hole | 0.25 |
| Switch in its 16.00 recess | 0.20 |

So a socket can sit up to about 0.3mm off its switch pins. That is ordinary for a hotswap
plate build. If the printed half shows the switches fighting the sockets, the fix is a
close-fit band in the cavity over the board's own 1.60mm of height, cut to `full.dxf`
plus 0.10 rather than to the hull. Narrower above wider is legal, so it machines from
below like everything else.

## Printing

Top face down. The first layer is the top face with its 16mm openings; at 1.50mm the
opening steps in to 14.5mm, a 0.75mm inward overhang per side that bridges without
support. Walls, bosses and standoffs rise from there, so nothing else overhangs.

**Expect the printed recesses to need opening up.** 16.00 on a 15.60 switch is 0.20 per
side and FDM holes come out 0.1-0.3mm under, so plan on 16.2-16.4 for the print while the
machined part keeps 16.00. Print a three-switch coupon and settle it before committing a
whole shell. The same goes for the plate's 0.15mm fit clearance.

The port openings are holes in a vertical wall, so their top edges bridge. Chamfer or
teardrop them if they sag.

## Clearances

| Item | Available | Needs | Margin |
| --- | --- | --- | --- |
| **Liatris** | 6.17, 6.92 over the relief pocket | 5.40 | +0.77, **+1.52** with the pocket |
| Hotswap socket, right half | 3.07 | 1.85 | +1.22 |
| TRRS jack | 6.62 | 5.20 | +1.42 |

Everything tall mounts on side B, so the 3.00mm above the PCB only has to clear the
switches and the whole height question is below the board.

| Below the PCB | mm | Source |
| --- | --- | --- |
| Mill-Max 315-43-112-41-003000 socket | 2.00 - 2.41 | measured ~2.0; datasheet `.095"` |
| Liatris PCB | 1.00 | splitkb states 1mm |
| Liatris down-facing, pin stubs tallest | 2.00 | measured |
| **MCU stack** | **5.40** | measured; **binds** |
| TRRS jack body, PJ-320A | 5.20 | measured |
| Hotswap socket, Kailh CPG151101S11 | 1.85 | **unverified, from memory** |

**Evaluate any outer-edge change on the RIGHT half.** Its 1u pinky plus the `zones.extra`
inner column puts a socket land 3.68mm from the outer board edge against the left's
16.73mm, so the outer edge height bites there first.

**Span costs more than height on a sloped floor.** Read a part's clearance at its
outermost extent, not its innermost: that is where the floor has risen furthest. The MCU
is shorter than the jack but reaches 27.22mm in from the inner edge against the jack's
8.45mm, so it loses three times as much depth to the slope and is the binding part.

## Open risks

**Switch seating.** The PCB sits 4.50 below the bearing surface.

| Shoulder to PCB | Recess floor | PCB top | Source |
| --- | --- | --- | --- |
| **4.25** | -1.75 | -6.00 | the built v4 case, measured off its STEP |
| 4.50 | -1.50 | **-6.00** (used here) | this sheet's 1.50 recess on the same PCB plane |
| 5.00 | -1.50 | -6.50 | Cherry's 5mm PCB-to-plate figure, if measured to the plate top |

The built case puts its PCB plane at exactly -6.00 and -7.60, the same as here, so that
much is confirmed on hardware. What differs is the recess: it is 1.75 deep there and 1.50
here, which moves the bearing surface up 0.25 and is the whole of the 4.25-to-4.50 change.
The 1.50 recess is a deliberate choice for a 1.50mm switch plate, not a carry-over.

**Deeper is the safe direction**: too deep and the switch seats on the plate with its base
floating clear; too shallow and the base hits the PCB before the shoulder reaches the
recess floor, so the switch sits proud. 4.50 is therefore 0.25 to the safe side of a case
that works, which is the reassuring direction to be wrong in. Whether Cherry's 5mm is to
the plate's top or bottom face could not be established; the datasheet drawings are raster
images. **To settle it**, pull a switch and measure plate top to PCB top.

**Switch seating and MCU clearance pull against each other.** Dropping the PCB to -6.50
spends the entire MCU margin, since every millimetre the board goes down is a millimetre
off the cavity below it. If the printed half shows switches sitting proud, add 0.50mm of
case height rather than moving the board. Seating also decides where typing load goes: a
switch that seats on the recess floor puts it into the shell, and one that bottoms on the
PCB puts it into a board whose three screws all sit between y -3.65 and +22.18.

**MCU seating.** The +0.77mm assumes the module's 4.75mm pin tail passes through the
4.01mm of socket and board bore and stands proud above the main PCB. If it bottoms out the
MCU seats 0.74mm lower and the margin is +0.03mm. **To settle it**, measure from the main
PCB's underside to the lowest point of the installed MCU: 5.40 means it seated.

**Hotswap socket height.** 1.85mm is from memory, not a datasheet. It has +1.22mm of
margin, so it is unlikely to bite.

**The right half's outer-pinky boss has a 0.45mm band of wall.** A recess clips that boss
on the right half only, over the bore's top 0.50mm. Machined, 0.45mm of aluminium beside a
tapped hole is fine. Printed, it is about one perimeter, thin enough that a slicer may drop
it and leave the bore open to the recess, which is cosmetic rather than structural.

**Seat every insert flush with the boss's lower face, not deeper.** A 4.00mm insert in the
5.00 bore then ends 0.50 short of the band, so nothing is pressed against the thin wall.
Driving one past flush is the way to blow it out. **Check it** on the right half's outer
pinky first, before doing the other five.

**The plate finishes flush by tolerance stack, not by a datum.** Its z is set by boss, PCB
and standoff, so JLCPCB's +-10% on a 1.6mm board moves it +-0.16 against the rim and it can
sit that far proud. Left alone deliberately: recessing it means shortening the standoffs,
which raises the plate and takes the same amount off the cavity below the PCB, where the
MCU margin is the tightest number in the design. The lever, if the seam bothers you, is
+0.20mm of case height rather than a shorter standoff. Bumpers carry the case either way.

## Verify

Export the shell as STEP and check it against the outline rather than by eye:

| Check | Expected |
| --- | --- |
| Cavity loop size | 160.50 x 119.50 |
| Gap from cavity to board outline | near-constant around the perimeter |
| Board outline points outside the cavity | none |
| Boss bore depths | 5.00 outer pinky, 4.00 the other two; none breaks into a recess |
| Port opening centres | z -10.50 TRRS, -10.25 USB, both below the board |
| Top edge in plan | straight across; no notch inherited from the board |
| Plate relief pocket | present, 0.75 deep, over the whole Liatris footprint |
| Plate under each bumper | 1.00; no bumper recess inside the relief pocket |

A wide spread in that gap means the profile is not the outline. Then **print and assemble
a half before ordering aluminium**: the printed part settles switch seating, MCU
clearance and the port openings for a few hours of filament.
