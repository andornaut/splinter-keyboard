# v4 case build sheet

Feature-by-feature recipe for modelling the case in Onshape. Design rationale is in
[README.md](./README.md); this file is the numbers.

**The Onshape document is the master, modelled by hand from this sheet.** `gen-case.py`
builds the same design from the same numbers and is the validator: every difference between
the two is decided, as set out in [Validating your model](#validating-your-model).

Every position is a **dimension, not a reference**. A re-import replaces the imported
entities, so anything projected off them loses its reference while a typed value does not.
The exceptions are the switch cutouts and the boss circles, which are cut from the import
itself so they track the board.

## Target board

The case is for the assembled board stamped `config=b05d803d9317 commit=51522ad clean=yes`.
`main` carries the same `Edge.Cuts` and the same footprint placements on both halves: the
later config changes only add the un-filleted DXF export, and the later board changes are
copper. **Generate the DXF from `main`**, since 51522ad predates `full_unfilleted.dxf`.

A config change that moves the outline, a switch, a screw or a port makes the case stop
fitting this board. Re-check it against the board in hand before taking one.

## Terms

| Term         | Means                                                                                                                                  |
| ------------ | -------------------------------------------------------------------------------------------------------------------------------------- |
| **Boss**     | A cylindrical pillar that takes a fastener. Three per half, hanging from the top underside down to the PCB                             |
| **Standoff** | The matching pillar rising from the bottom plate to the PCB underside, bored through for the screw                                     |
| **Hull**     | The un-filleted board outline, 160.000 x 119.000mm, in `full_unfilleted.dxf`. The case is modelled to this, not to the fabricated edge |
| **Recess**   | The 16mm opening at the top face each switch nests into, so the surrounding wall covers its lower body                                 |
| **Plate**    | The bottom plate                                                                                                                       |
| **Setup**    | One fixturing of the part in the mill. Every flip is another setup and another fixed fee                                               |

## How it goes together

```text
   top face   ------------------------------   z   0.00
                    |:|            <- insert bore, top of the screw path
   recess floor ----|:|------------------      z  -1.50   switch flange bears here
   top underside ---+:+---------------+##+     z  -3.00
                    |:|            <- boss, 5.50 dia
   PCB top    ------+:+---------------+##+     z  -6.00   boss ends; SHELF underside
   PCB        #######:#################|  |    <- 3.00mm NPTH
                    |:|               |##|     z  -7.60   PLATE WALL top
                    |:|            <- standoff, 5.50 dia, 2.90 clearance hole
   plate      -----[===]--------------+##+     M2.5 flat head in its counterbore, up from below
```

The board is clamped all the way round, not only at the three screws: a **shelf** hangs
from the case's top and the plate carries a matching **wall** up to meet it. The bosses and
standoffs are the same sandwich at the three screw points.

## Topology

| Part             | Contents                                                                              |
| ---------------- | ------------------------------------------------------------------------------------- |
| **Shell**        | Top face and side walls, one piece. Switch cutouts in the top, shelf inside the walls |
| **Bottom plate** | Inset closing plate with a perimeter wall, the screw heads and the standoffs          |

**The shelf goes above the board.** Which side it sits on decides whether
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

## Machining setups

| Part  | Setup | From                   | Features                                                          |
| ----- | ----- | ---------------------- | ----------------------------------------------------------------- |
| Shell | 1     | below                  | Outer profile, cavity, bosses, boss holes, the bottom edge fillet |
| Shell | 2     | above                  | The 16mm switch recesses, the top edge fillet                     |
| Shell | 3     | the top edge (+y face) | TRRS and USB openings                                             |
| Plate | 1     | inner face             | Profile, standoffs, screw holes                                   |
| Plate | 2     | outer face             | Counterbores, bumper recesses                                     |

**Setup 3 is not optional.** Both ports are holes through a vertical wall, and a 3-axis
mill reaches those from neither above nor below. A right-angle head folds it back into
setup 1 if the shop has one; otherwise it is a third fixturing. Both ports sit on the same
face, so one setup covers both.

The nested switch cutout is inherently wider at the top, so nothing reaches it from below.
The 14.5mm holes are through-features and can be cut in setup 1 or 2. Flattening the top
to a single 14.5mm hole would drop setup 2, at the cost of the switch sitting proud on a
flat face.

**Quote both variants before deciding.** The recesses are ~10-25 minutes of spindle time,
so the adder is dominated by the fixed cost of re-fixturing, and a shop may plan the op
regardless. Hollowing the block likely dominates the part cost either way. If the delta is
large, flatten the top for the aluminium variant only and keep the nesting on the print.

## Decisions this sheet assumes

| Decision               | Assumed                                                                         |
| ---------------------- | ------------------------------------------------------------------------------- |
| Process                | Print first, then aluminium; the printed half confirms fitment                  |
| Print orientation      | Shell top-face-down; walls and bosses rise from a flat first layer, no supports |
| Wall thickness         | 2.0mm                                                                           |
| Top thickness          | 3.0mm, recessed to 1.5mm at each switch                                         |
| Cavity internal fillet | 2.0mm                                                                           |
| Board pocket clearance | 0.50mm per side on the hull                                                     |

**The pocket clearance is a print number, not a machining fit.** An FDM part loses 0.2 to
0.3% to XY shrink across 160mm and another 0.1 to 0.2 per wall to perimeter
over-extrusion, which closes a tenth-millimetre pocket outright and leaves a board that
will not go in. 0.50 survives that and costs the milled variant nothing, because the board
is located by its screws rather than by the pocket either way.

**The cavity fillet is concentric with the board's.** It is an internal corner, so the
tool leaves material _inside_ the pocket, and that material has to miss the board's own
1.5mm exterior fillet. At 2.00 the pocket's corner arc and the board's fillet are both
centred 1.50 in from the sharp hull corner, so at a 90 deg corner the clearance is the tool
radius less the board fillet uniformly around the arc rather than only at its tightest
point. That is 0.500, the same as the straight edges, and no corner is tighter than an edge.

## Frame

Outline centre at the origin, +x toward the inner (thick) edge, +y up, z=0 at the shell's
top face, +z up.

Positions read off the KiCad board are in the _filleted_ frame and gain **+0.205mm in y**
to convert, since the fillet shortens the board 0.410mm and moves its bbox centre half of
that. Every value here is already converted.

|                            | Value               |
| -------------------------- | ------------------- |
| Hull, per half             | 160.000 x 119.000   |
| `Edge.Cuts`, as fabricated | 160.000 x 118.590   |
| Top edge / bottom edge     | y +59.500 / -59.500 |
| Side edges                 | x +-80.000          |

The 1.5mm wall fillet rounds the corners, so the fabricated height drops while the width
holds at the straight side edges.

## Z stack

| Level                                          | z      |
| ---------------------------------------------- | ------ |
| Shell top face                                 | 0.00   |
| Recess floor; switch flange bears here         | -1.50  |
| Top underside; 1.50mm switch plate above       | -3.00  |
| PCB top face; boss ends here                   | -6.00  |
| PCB bottom face                                | -7.60  |
| Bottom plate top face, inner edge              | -15.50 |
| Shell bottom rim / plate underside, inner edge | -17.00 |

**Specify the two edge heights, not the angle: 17.00mm inner, 13.00mm outer.** Over the
165.00mm shell that is 1.3887 deg, but the angle is derived. If the wall thickness
changes, the case width changes with it and the angle follows while the heights stay put.

The bottom slopes, so the last two rows are at the inner edge; at the outer edge the rim
is at -13.00. Usable cavity below the PCB runs **7.84mm at the inner edge to 3.96mm at the
outer**, measured at the board edges rather than the shell's.

**The case is 1.00 deeper than the parts alone need, in place of a relief pocket in the
plate.** That puts the plate +1.78 under the Liatris, +1.04 if the module bottoms out in
its sockets, at full thickness. On an aluminium plate, a conductor beside exposed pin
tails, that margin is the point.

**What the taper costs.** 1.3887 deg is not a working tent angle, so the slope is there for
the look, and it buys that at the price of three standoff heights, recessed screw heads, and
putting the tightest clearance in the design on the shallow side. A flat 16.50mm case would
give the Liatris +2.00, the jack +2.20 and the socket +5.55 with one standoff height and
every head flush.

## Parameters

| Parameter                          | Value                         | Source                                                                                  |
| ---------------------------------- | ----------------------------- | --------------------------------------------------------------------------------------- |
| Wall thickness                     | 2.00                          | decision; see below                                                                     |
| Top thickness                      | 3.00                          | decision                                                                                |
| Switch recess depth                | 1.50                          | nesting                                                                                 |
| Plate at a switch cutout           | 1.50                          | MX standard, 1.5mm +-0.1mm                                                              |
| Bottom plate                       | 1.50                          | takes the flat head's full height                                                       |
| Board pocket                       | 161.00 x 120.00               | hull + 0.50/side; the board itself is 0.705/side loose in y                             |
| Shell outer profile                | 165.00 x 124.00               | pocket + wall                                                                           |
| Boss and standoff diameter         | 5.50                          | = 2 x `screw_boss_radius`, the DXF's own circle                                         |
| Boss height                        | 3.00                          | top underside to PCB                                                                    |
| Material above the PCB at a boss   | 6.00                          | top 3.00 + boss 3.00; **4.50 where a recess overlaps**                                  |
| Insert hole, filament              | 3.60 dia                      | M2.5 melt diameter; 4.00 deep at every boss, see below                                  |
| Tapped hole, machined              | 2.05 tap drill, M2.5x0.45     | same 4.00 drill; full thread to 3.60, see Aluminium variant                             |
| Screw                              | M2.5 button head, ISO 7380    | head 4.70 dia x 1.50, **flat underside**; one length, M2.5x10                           |
| Screw clearance hole               | 2.90 dia                      | through the plate and the standoff                                                      |
| Counterbore in the plate           | 5.00 dia, **flat bottomed**   | head + 0.30; every floor on one level plane                                             |
| Perimeter shelf, on the shell      | 1.75 wide, underside at -6.00 | measured in from the cavity, so it laps the board by 1.25, inside its 2.00 keepout ring |
| Perimeter wall, on the plate       | 1.55 wide, top at -7.60       | out to the shelf's inner loop, so it laps the board by the same 1.25                    |
| Wall relief                        | 30.00 in from the plate edge  | x +-50.30 on, down to y 56.25; clears the USB plug's path, the jack and the MCU         |
| Flared standoff base               | 8.00 dia, up to -10.35        | = the built v4 lid; gives the counterbore a 1.50 annulus                                |
| Switch cutout / recess             | 14.50 / 16.00, R1.00 corners  | see below                                                                               |
| Outer edge fillets, top and bottom | R1.00, one radius             | one corner-rounding pass each; the switch recesses and the cavity mouth stay square     |
| Kink, the re-entrant corner        | R2.50 outside, R2.00 inside   | each loop's own corner radius; for looks                                                |

**The wall is 2.00 so a TRRS plug seats.** The jack's barrel stands 2.00 past the board
edge, 1.50 into the wall, which leaves its mouth 0.50 behind the case face; a 3.00 wall
leaves it 1.50 behind. A cable whose overmold is wider than the 5.50 opening stops at the
face, so that distance comes straight off the plug's travel into the jack. Stiffness does
not need more: 2.00 is five perimeters printed, and the top face and the clamped board
carry the shell.

**The wall is cut away over the top-inner corner.** There the top edge carries the USB
plug's path and the jack's body, so a band running on would block the USB plug and sit on
the jack. The cut starts 30.00 in from the plate's inner edge, 2.60 clear of the Liatris
body (its edge at x 52.90) in plan, and takes the inner wall down to where its corner arc
begins.

**The standoff needs a flared base.** The counterbore runs the plate's full thickness, so
without a flare a 5.00 bore inside a 5.50 standoff joins the two by a 0.25mm annulus, 4.12
mm2 per boss: the head bears on the standoff and the plate hangs off that ring, which on an
FDM part is under one extrusion width. Flaring the base to 8.00 makes it 1.50mm and 30.63
mm2, seven times the area.

**Height is what constrains a flare, not diameter.** It stops under the hotswap sockets
hanging 1.85 below the board, and every pad it would otherwise have to dodge is above it,
so the 2.04mm inner-boss pad clearance that caps the standoff does not cap this. It stops
2.75 below the board underside, at -10.35, which leaves 0.90 to the sockets.

**The 14.50 cutout is not slack.** An internal corner rounds _into_ the void, so an R1.00
corner cut into a 14.00 hole would bind a switch by 0.207mm. At 14.50 it clears by 0.146mm
against a 14.00 section with 0.5mm corner radii. The switch is located by the 16.00 recess,
not by this hole.

### Screw bosses

Left half, from the outline centre. The right half is the exact mirror (negate x). Outer
and inner name the board edge each boss is nearer, as in the config's `screw_left_outer`,
`screw_left_inner` and `screw_left_center` zones.

| Boss   | Position          | Standoff height | Head recessed | Stack | Bore depth | Screw   | Engagement |
| ------ | ----------------- | --------------- | ------------- | ----- | ---------- | ------- | ---------- |
| Outer  | (-42.375, -3.650) | 4.87            | 0.00          | 6.47  | 4.00       | M2.5x10 | 3.53       |
| Inner  | (33.825, 0.050)   | 6.72            | 1.85          | 6.47  | 4.00       | M2.5x10 | 3.53       |
| Centre | (-3.325, 22.175)  | 5.82            | 0.95          | 6.47  | 4.00       | M2.5x10 | 3.53       |

**Every counterbore floor lies on one level plane, z -12.47**: the plate's top face over
the outer boss, the highest of the three. A flat-underside head bears on that floor, inside
the flare, and its length is measured from there to the board's top face, so the stack is
6.47 at every boss and one screw length, M2.5x10, serves all three with 3.53mm of thread,
0.47 short of the bore's bottom. The plane can go no lower: the outer head sits flush, and
the others are recessed by however far the slope drops the plate under them. Derive it
from the slope, not as a typed z.

**Any flat-underside head works; the counterbore diameter is what follows from the choice.**
5.00 suits a 4.70 head (button ISO 7380, socket cap DIN 912) with 0.30 to spare, and leaves
0.25 of standoff outside it. A 5.00 pan head needs 5.30, which leaves 0.10 and a knife edge
on the standoff, so grow the standoff if you go that way. Head height decides flushness
only: 1.50 finishes level with the plate at the outer boss, 1.70 stands 0.20 proud there,
and neither affects the screw length, since that is measured under the head.

The outer and inner bosses sit 3.70mm apart in y. That is forced: the pinky columns are
asymmetric, so the two screws cannot share a y while clearing both switch holes and pads.
Do not level them.

**Every bore is 4.00 deep.** A 16.00 switch recess overlaps the inner and centre bosses,
so the material above them is 1.50 (top left over the recess) + 3.00 (boss) = 4.50, not
6.00, and a 5.00 bore breaks out into the recess floor. A 4.00 bore stops at z -2.00, 0.50
below the recess floor, so no recess reaches it on any boss of either half:

| Boss   | Recess edge from the boss axis | 1.80 bore radius | Breakout      |
| ------ | ------------------------------ | ---------------- | ------------- |
| Inner  | 1.745                          | 1.80             | 0.88 x 0.06mm |
| Centre | 1.695                          | 1.80             | 1.21 x 0.11mm |

The placement rule holds the boss clear of the 14.50 **hole** (tangent on both halves at
these two), which is what stops the boss fouling the switch body. It says nothing about the
16.00 **recess** above, which is what the bore has to miss.

**The bosses mirror; the key field they sit in does not.** On the right half a recess also
clips the outer boss, putting its recess edge 2.25mm from the bore axis against a 1.80
bore radius. The left half's outer boss has no recess over it and could take a deeper
bore, but on the right half that would leave 0.45mm of wall beside the recess. Do not read
the table's "exact mirror" as covering what surrounds them.

`gen-case.py` hard-errors on a bore that reaches the recess band without clearing the
recess wall, so this table cannot go stale against the key field. Readback cannot cover
it: a breakout trims the bore's face without splitting it or changing its height, so the
depth check and the face census both pass a shell that has one.

**The standoffs are three different heights** because the plate is sloped. The
counterbores absorb the difference, reaching up into the flare under the lower bosses, so
the screws need not.

**Clearance to the nearest side-B pad**: 3.54mm outer, **2.04mm inner**,
3.98mm centre. Those are measured to the pads, and the Kailh socket body is larger than
its lands, so the real gap at the inner boss is smaller by an unknown amount. That is why
the standoff is 5.50 and not larger.

### Ports, on the top edge

| Feature                             | Position                                              | Relative to                                    |
| ----------------------------------- | ----------------------------------------------------- | ---------------------------------------------- |
| USB-C notch, already in the outline | x +56.663 .. +66.663, cut 7.271mm down from y +59.500 | centred on the Liatris, x +61.663              |
| TRRS jack centre                    | (74.650, 59.500)                                      | 12.987 toward the inner edge from notch centre |

**Model both openings from the notch, not from the frame.** The config places the notch at
`mcu_reset_x - 0.127` and the jack at `mcu_reset_x + 12.860`, so the 12.987 between them
holds wherever the MCU column moves.

**Both parts mount on side B, so both openings sit entirely below the PCB.**

| Opening     | Size            | Centre z   | Below the board underside | Source                                                                |
| ----------- | --------------- | ---------- | ------------------------- | --------------------------------------------------------------------- |
| TRRS, round | 5.50 dia        | **-10.50** | 2.90                      | measured off the built v4 case                                        |
| USB-C, slot | 9.50 w x 4.00 h | **-10.25** | 2.65                      | measured on a printed part of this design; width is stated, see below |

**The USB opening is a slot, R2.00 at both ends.** A USB-C plug shell is rounded the same
way, and an end mill cutting through the wall from the side cannot make a rectangle's
internal corners.

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

**Why 9.50 wide, and why it is stated rather than derived.** It sits inside the board's own
10.00 notch, so the plug clears the board edge, and it clears an 8.34mm plug shell by 0.58
per side. How far inside the notch it has to sit is set by how far the board can move,
which is the screws and not the pocket: a 2.5mm screw in a 3.00mm hole is 0.25 per side
whatever the pocket fit is. Deriving the width from the pocket clearance would shrink the
port every time the pocket was loosened, which is the wrong direction.

Wall left below each opening: 3.56mm at the TRRS, 4.25mm at the USB. The TRRS is thin
enough that a printed shell wants an extra perimeter there.

**Nothing in the case follows the board's USB notch.** Not the outer profile, not the
cavity, not the plate. That notch clears the plug's overmold, which sits below the board
entirely, so to the case it is only a bite out of an edge that should run straight.
Inheriting it puts a jog in all three outlines and leaves a pointless tongue of material in
the pocket. Fill it in the hull before offsetting any of them. The result is a void where
the board is absent, which costs nothing and gives the plug more room rather than less: the
top edge is straight and both ports are simply openings in the back wall.

## Measure the built board first

Several figures below the board come from memory or from the previous case. With the
board in hand, measure these before modelling. Where a measurement differs, change the
parameter here and in `gen-case.py`, then re-run it so its guards see the new value.

| Measure, on the assembled board                                | Sheet assumes | Decides                                                         |
| -------------------------------------------------------------- | ------------- | --------------------------------------------------------------- |
| Board thickness                                                | 1.60          | every z below the board; whether the plate sits flush           |
| Board underside to the lowest point of the installed MCU       | 5.40          | the binding margin; see "MCU seating" under Open risks          |
| Board underside to the bottom of a hotswap socket              | 1.85          | the 0.90 between the sockets and the standoff flares            |
| Board underside to the bottom of the TRRS jack body            | 5.20          | jack margin                                                     |
| Board underside to the USB-C receptacle centre                 | 2.65          | USB opening centre, z -10.25                                    |
| Board underside to the TRRS bore centre                        | 2.90          | TRRS opening centre, z -10.50                                   |
| Board top to the plate-bearing shoulder of a seated switch     | 4.50          | recess depth; see "Switch seating" under Open risks             |
| Kailh socket body edge to the right half's inner screw hole    | lands only    | whether the 5.50 standoff and 8.00 flare clear the body         |
| Switch top housing width                                       | 15.60         | the 16.00 recess fit                                            |
| Plug shell width, and overmold size of the cables you will use | 8.34          | USB opening width; whether the outer-face counterbore is needed |

A port centre measured from the board underside sets the opening's z as -7.60 less that
figure (on a 1.60 board).

## Modelling in Onshape

**Put every Parameters row in a Variable feature** at the top of the tree and type
`#name` into features, never the number. A number typed into a feature is a second copy,
and the sheet changes.

**One Part Studio holds both halves.** Build the left half's shell and plate up to, but not
including, the switch features, with its outline centre at the origin. Mirror both parts,
keeping the originals, about a plane midway between the DXF's two halves: x +91.4497, half
the 182.8994 between their outline centres. The right half then lands on the DXF's own
right-half curves, and each half cuts its switch recesses and cutouts from its own half
of the DXF. The body mirrors exactly; the key field does not (see Right half).

Traps:

- **Fill the USB notch in the hull before any offset.** Every loop below is offset from the
  notch-filled hull. See Ports for why nothing follows the notch.
- **Offset each loop from the hull, never from another offset loop.** The cavity loop's
  corners are R2.00. Offsetting it inward 1.75 for either ring leaves R0.25 corners where
  R2.00 is meant. The shelf's inner loop is the hull inset 1.25 and so is the plate
  wall's, each with its own corners rounded at R2.00.
- **The one exception is the plate outline**, which is the finished cavity loop inset 0.20,
  so it matches the pocket it drops into. The inset leaves its five convex corners at
  R1.80 and its kink at R2.20: fillet all six to R2.00, the design's minimum corner
  radius.
- **Round all six corners of every loop, each at its loop's own radius.** The hull has
  five convex corners and one re-entrant one, the kink where the thumb cluster meets the
  main field. The kink is rounded for looks, R2.50 outside and R2.00 inside, so the wall
  stays about 2.00 thick through it. Outside the arc adds wall and inside it trims a point of wall, so
  neither reaches the board.
- **One construction plane for the slope**, through z -17.00 at the inner shell edge and
  z -13.00 at the outer (x +82.50 and -82.50 on the left half). The shell's bottom cut,
  both plate faces (that plane and a 1.50 offset) and every standoff's lower end reference
  it.
- **Sketch plate holes on a horizontal plane.** Onshape's Hole feature drills normal to
  its sketch plane, so a hole sketched on the sloped plate face comes out tilted 1.39 deg
  and its projected centre shifts. The counterbores end on one level plane rather than a
  depth from the plate, so cut them with an extrude up to that plane. The bumper recesses are sketched on a horizontal plane too and end on
  a plane parallel to the plate, so their floors run parallel to it.
- **Extend port cuts past both wall faces.** A cut ending exactly on a face leaves
  coincident faces and a non-manifold solid.
- **Cut switch features straight from the imported curves**, not redrawn. They carry the
  corner fillets the cutout width depends on.

## Validating your model

Export from Onshape as STEP, shell and plate assembled (plate in place, not exploded), in
millimetres. Each half is either in the sheet's [Frame](#frame) or, for the right half,
where the DXF places it beside the left, which the script detects and moves back. One
file holding both halves (four solids), one per half, or one per part all work. Put exports
under `dist/v4/onshape/`, which is not committed. Then, once per half:

```bash
FC_HALF=left FC_COMPARE=dist/v4/onshape/onshape-left.step \
  freecadcmd v4/onshape/gen-case.py
```

It builds the reference half, Boolean-subtracts each way, and reports every region where
the two disagree: `extra` is material in your model the reference lacks, `missing` the
reverse, each with its volume, centre and size in the sheet's frame. It exits nonzero on
any region not on record. A part whose centre is over 1mm from the reference's stops it
before comparing, since every face would differ and the cause is the export frame. Where no
Boolean computes, as where two faces cross at a shallow angle, it compares the part in
smaller cells; a cell that still fails is reported with its box, to check by hand, and also
fails the run.

**Decide every region one of three ways.**

| Decision               | When                                                                | Then                                                                 |
| ---------------------- | ------------------------------------------------------------------- | -------------------------------------------------------------------- |
| Move to the reference  | your model departs from the sheet, and the sheet's version is right | change your model; nothing is recorded                               |
| Intentional difference | a deliberate departure in something the sheet does not model        | add the entry the report prints to `differences.json`, with a reason |
| Error                  | either side is wrong against the sheet or the board                 | fix the side that is wrong; nothing is recorded                      |

**A deliberate change to a sheet dimension is not an intentional difference.** Change it
in this sheet and in `gen-case.py`, and the region goes away. Recording it instead leaves
the sheet describing a case nobody is building. Intentional is for what the sheet does not
model: a cosmetic feature, an extra fillet, a fit opened up on a printed coupon.

**An intentional difference is outside the script's guards.** The bore-breakout and
bumper-floor checks run on the reference only, so a recorded region that touches a bore or
a bumper recess needs its [Verify](#verify) row checked by hand.

An error on the script's side goes into `gen-case.py`, and into this sheet too if the
number was wrong here.

**`differences.json`** holds one entry per intentional difference:

```json
{ "half": "left", "part": "shell", "kind": "extra", "box": [x0, y0, z0, x1, y1, z1], "reason": "..." }
```

A region is accepted when its bounding box lies inside an entry's `box`. For each
unrecorded region the report prints a ready entry, its box rounded outward to 0.1mm, with
an empty `reason` to fill in. An entry that matches no region fails as stale: the
difference is gone, so delete it. Each half is recorded separately, since the key fields
differ.

## Part A: shell

1. **Sketch "Outline (imported)"**, Top plane. Insert
   `dist/v4/ergogen/outlines/full_unfilleted.dxf` in millimetres. Constrain the left half's
   outline centre to the origin. **Never draw in this sketch**; re-importing is the only
   edit it should take.
2. **Sketch "Hull"**, the left-half outline with the USB notch closed by a straight line
   along the top edge. Every offset below starts from this loop.
3. **Extrude "Shell body"**, Hull offset outward **2.50mm** (clearance + wall), from z 0
   down past z -17.00, then cut away everything below the slope plane. The bottom rim lands
   at **-17.00 at the inner edge and -13.00 at the outer**.
4. **Extrude cut "Cavity"**, Hull offset outward **0.50mm**, from **z -3.00** down through
   the open bottom. Fillet its five internal vertical corners at **2.0mm**.
5. **Extrude "Shelf"**, the ring between the cavity loop and Hull inset **1.25mm** (corners
   R2.00), from **z -3.00 down to -6.00**. The board is pressed up against its underside.
6. **Bosses**, on the top underside: three circles r **2.75** at the positions above,
   extruded down **3.00mm** to the PCB top face.
7. **Boss holes**, from each boss's lower face upward, 3.60 dia (or the 2.05 tap drill),
   **4.00 deep** at every boss.
8. **Port openings** cut straight through the side wall, overshooting both faces.
9. **Edge fillets**, R1.00 (one variable) on the top face's outer edge and on the bottom
   rim's outer edge only.

On each half, after the mirror, from that half's own curves:

1. **Extrude cut "Switch recesses"**, the 16.0mm curves from the import, top face down to
   **z -1.50**.
2. **Extrude cut "Switch cutouts"**, the 14.5mm curves from the import, through the
   remaining 1.50mm. Cut both sets **as imported**. The recess openings get no fillet:
   the nesting look depends on the switch meeting a crisp edge.

## Part B: bottom plate

1. **Extrude**, the cavity loop (with its R2.00 corners) inset **0.20mm**, all six corners
   filleted to **R2.00**, the kink included, **1.50mm** thick, between the slope plane and its
   1.50 offset, flush with the rim.
2. **Perimeter wall**, the ring between the plate outline and Hull inset **1.25mm**
   (corners R2.00), from the plate's top face up to **z -7.60**. Remove the wall over
   the top-inner corner: **30.00** in from the plate's inner edge (x > +50.30), down to
   **y 56.25**, where the inner loop's corner arc begins, so the inner wall ends flat
   there.
3. **Standoffs**, r **2.75** at the three boss positions, rising to the PCB underside at
   z -7.60. Heights are in the boss table. Each sits on a flared base, r **4.00**, from
   the plate up to **z -10.35**, 2.75 below the board underside.
4. **Screw holes**, 2.90 dia, through the plate and up the full height of each standoff
   to z -7.60, so the screw passes through the standoff and the PCB into the boss's
   insert. Each has a flat-bottomed 5.00 counterbore, cut from below up to one level
   plane: the plate's top face over the outer boss, z -12.47. Sketch the circles on a
   horizontal plane, concentric with the screw circles.
5. **Bumper recesses**, 12.00 dia x 0.50 deep on the outer face at (-72.75, +52.25),
   (+72.75, +52.25), (-72.75, -34.50), (+69.36, -50.27), each tangent to the wall's inner
   loop in its corner. Sketch them on a horizontal plane, where the loop projects straight
   down, and extrude up to a plane 0.50 above the plate's underside: on the sloped plane the
   wall's edges project up to 0.2 sideways. Floor **parallel to the plate faces**, so the
   depth is 0.50 and the plate left is 1.00 right across every foot. All are well clear of the
   three screw heads.

**Only the counterbores have level floors.** The plate is a parallel-sided slab lying at
1.3887 deg, so "flat" and "level" are different instructions here. The counterbores mean
level: a flat head seats square to its vertical screw, and one plane gives one screw
length. Every other feature means parallel to the faces. A bumper recess cut level instead
would run 0.355 to 0.645 deep and leave 1.145 to 0.855 of plate, different at each edge of
every foot.

The MCU's reset and boot buttons and the board's own reset switch all face the plate;
access is by removing it, so no holes are needed.

**No support posts.** A post short enough not to lift the board off its bosses is too short
to carry anything, and typing load reaches the shell through the switch flange rather than
the PCB. The plate is unloaded.

## Right half

Mirror both parts about the plane midway between the DXF's halves: the outline mirrors
exactly and the only half-specific geometry is the switch cutouts. Cut those from the **right half of the DXF**, not from a mirrored copy of
the left's. The halves carry 30 and 32 switch cutouts and 14 positions have no mirrored
counterpart, so a mirrored key field is the wrong key field.

## Assembly

**Switches go into the shell first, then the board goes on.** A 15.6mm top housing cannot
pass a 14.5mm hole from below. Clip all 30 (or 32) switches
into the shell's top face from the outside, then bring the board up into the cavity onto
every socket at once.

The cavity is a straight bore, so the board cannot be rocked in the way a bare
plate-and-switch assembly usually is. Seat it evenly, thumb cluster last, until it meets
the shelf all the way round. Then the plate goes on and its wall closes the sandwich.

**If the sockets fight the pins, fit the plate first and let the screws press the board
home.** The plate's perimeter wall and its three standoffs all top out at -7.60, the board's
underside, and the screws draw the plate up toward the shell, so the wall bears on the
board right around its edge and pushes it onto every pin at once while the screws hold it
to 0.25 per side. That is tighter than the pocket and it spreads the seating load over the
whole perimeter rather than through the three bosses. Draw the three evenly, a turn at a
time, so the board goes up flat.

**Nothing datums the board.** The 5.50 boss butts its top face and never enters the 3.00mm
hole, and a boss cannot pilot into that hole because the 3.60 insert bore is wider than the
hole itself. **Which constraint registers it depends on whether the screws are in.** Press
the board on by hand and only the pocket is holding it; fit the plate and draw the screws
and they take over at 0.25, which is tighter.

| Constraint                 | Play, per side                                                                     | In force                                                        |
| -------------------------- | ---------------------------------------------------------------------------------- | --------------------------------------------------------------- |
| Pocket in x                | 0.50                                                                               | whenever the screws are not                                     |
| Pocket in y                | 0.705 (the fillet takes 0.410 off the board height, the pocket is cut to the hull) | whenever the screws are not                                     |
| Screw in its 3.00 hole     | 0.25                                                                               | once the plate is on, including while it presses the board home |
| Switch in its 16.00 recess | 0.20                                                                               | always                                                          |

So a socket seated by hand can sit **0.54mm** off its switch pins in x and **0.73mm** in y,
root sum square against the switch's own play, and 0.70 / 0.91 worst case. Seated on the
screws it is **0.32mm**, whatever the pocket is cut to. That is the reason to reach for the
plate rather than for a tighter pocket if the sockets fight: the pocket has to stay loose
enough that a printed shell accepts the board at all.

**A printed shell and a milled one part company on the hand-seated figures**, and the
pocket clearance is what splits them. A printed pocket comes out undersize, which is the
whole reason the clearance is 0.50, so its effective play lands near half those numbers. A
milled pocket is 0.50 true. The screw-seated figure is the same for both.

## Aluminium variant

`FC_VARIANT=aluminium` builds it, written beside the filament reference with an `-aluminium`
suffix. In Onshape, a configuration on the shell's screw holes keeps both variants in one
document. Everything else, the whole plate included, is shared.

| Feature                 | Filament                                           | Aluminium                                                                                       |
| ----------------------- | -------------------------------------------------- | ----------------------------------------------------------------------------------------------- |
| Screw hole in each boss | 3.60 bore, 4.00 deep, for a 4.00mm heat-set insert | 2.05 tap drill, 4.00 deep plus its 118 deg point, M2.5x0.45 full thread to 3.60 (bottoming tap) |

**The counterbores stay level in aluminium.** The 2.90 screw hole runs up to 9.3 tall
through the plate and standoff, and drilled square to the plate its top would land 0.22 off
the screw, more than the 0.20 radial clearance. So a mill drills it with the plate tilted
1.39 deg, and in that setup a level floor is a plain counterbore on the hole's own axis,
concentric with it and seating the head square.

**The full thread runs to 3.60** because the screw engages 3.53 and a standard tap leaves
its last threads incomplete at the bottom of a blind hole. State it on the drawing.
The drill's 118 deg point reaches 0.62 past the 4.00, narrowing inside the hole, so it stays
far inside the switch recesses' edges.

**The taper is this variant's cost.** The sloped rim and its fillet, and the plate's wall,
standoff and flare tops, are each tilted to the part that carries them, so each takes a 3D
pass or a wedge fixture. Quote it against a flat-bottomed case before ordering.

## Printing

Top face down. The first layer is the top face with its 16mm openings; at 1.50mm the
opening steps in to 14.5mm, a 0.75mm inward overhang per side that bridges without
support. Walls, bosses and standoffs rise from there, so nothing else overhangs.

**The top edge fillet is the first layers' outer edge.** Its overhang starts almost flat at
the bed and steepens over the first 1.00mm, so those layers droop slightly at the very
edge. Slow the first layers and run full cooling from layer two. The bottom edge fillet is
the last layers' outer edge and prints as an ordinary sloping surface.

**Expect the printed recesses to need opening up.** 16.00 on a 15.60 switch is 0.20 per
side and FDM holes come out 0.1-0.3mm under, so plan on 16.2-16.4 for the print while the
machined part keeps 16.00. Print a three-switch coupon and settle it before committing a
whole shell. The same goes for the plate's 0.20mm fit clearance.

The port openings are holes in a vertical wall, so their top edges bridge. Chamfer or
teardrop them if they sag.

## Clearances

| Item                       | Available | Needs | Margin    |
| -------------------------- | --------- | ----- | --------- |
| **Liatris**                | 7.18      | 5.40  | **+1.78** |
| Hotswap socket, right half | 4.05      | 1.85  | +2.20     |
| TRRS jack                  | 7.63      | 5.20  | +2.43     |

Everything tall mounts on side B, so the 3.00mm above the PCB only has to clear the
switches and the whole height question is below the board.

| Below the PCB                          | mm          | Source                           |
| -------------------------------------- | ----------- | -------------------------------- |
| Mill-Max 315-43-112-41-003000 socket   | 2.00 - 2.41 | measured ~2.0; datasheet `.095"` |
| Liatris PCB                            | 1.00        | splitkb states 1mm               |
| Liatris down-facing, pin stubs tallest | 2.00        | measured                         |
| **MCU stack**                          | **5.40**    | measured; **binds**              |
| TRRS jack body, PJ-320A                | 5.20        | measured                         |
| Hotswap socket, Kailh CPG151101S11     | 1.85        | **unverified, from memory**      |

**Evaluate any outer-edge change on the RIGHT half.** Its 1u pinky plus the `zones.extra`
inner column puts a socket land 3.68mm from the outer board edge against the left's
16.73mm, so the outer edge height bites there first.

**Span costs more than height on a sloped floor.** Read a part's clearance at its
outermost extent: that is where the floor has risen furthest. The MCU
is shorter than the jack but reaches 27.22mm in from the inner edge against the jack's
8.45mm, so it loses three times as much depth to the slope and is the binding part.

## Open risks

**Switch seating.** The PCB sits 4.50 below the bearing surface.

| Shoulder to PCB | Recess floor | PCB top               | Source                                                         |
| --------------- | ------------ | --------------------- | -------------------------------------------------------------- |
| **4.25**        | -1.75        | -6.00                 | the built v4 case, measured off its STEP                       |
| 4.50            | -1.50        | **-6.00** (used here) | this sheet's 1.50 recess on the same PCB plane                 |
| 5.00            | -1.50        | -6.50                 | Cherry's 5mm PCB-to-plate figure, if measured to the plate top |

The built case puts its PCB plane at exactly -6.00 and -7.60, the same as here, so that
much is confirmed on hardware. What differs is the recess: it is 1.75 deep there and 1.50
here, which moves the bearing surface up 0.25 and is the whole of the 4.25-to-4.50 change.
The 1.50 recess is a deliberate choice for a 1.50mm switch plate, not a carry-over.

**Deeper is the safe direction**: too deep and the switch seats on the plate with its base
floating clear; too shallow and the base hits the PCB before the shoulder reaches the
recess floor, so the switch sits proud. 4.50 is therefore 0.25 to the safe side of a case
that works. Whether Cherry's 5mm is to
the plate's top or bottom face could not be established; the datasheet drawings are raster
images. **The built board settles it**: measure the shoulder height on a seated switch (see
Measure the built board first).

**Switch seating and MCU clearance pull against each other.** Dropping the PCB to -6.50
takes 0.50 off the MCU margin, since every millimetre the board goes down is a millimetre
off the cavity below it. If the printed half shows switches sitting proud, add 0.50mm of
case height rather than moving the board. Seating also decides where typing load goes: a
switch that seats on the recess floor puts it into the shell, and one that bottoms on the
PCB puts it into a board whose three screws all sit between y -3.65 and +22.18.

**MCU seating.** The +1.78mm assumes the module's 4.75mm pin tail passes through the
4.01mm of socket and board bore and stands proud above the main PCB. If it bottoms out the
MCU seats 0.74mm lower and the margin is +1.04mm. **The built board settles it**: 5.40 from
the main board's underside to the lowest point of the MCU means it seated.

**Hotswap socket height.** 1.85mm is from memory, not a datasheet. It has +2.20mm of
margin to the plate and +0.90 to the standoff flares, so it is unlikely to bite. Measure
it on the built board.

**Seat every insert flush with the boss's lower face.** A 4.00mm insert fills its 4.00
bore, so one driven past flush bottoms against the top of the bore and pushes into what is
above it: 0.50 of top face where a recess overlaps the boss.

**The plate finishes flush by tolerance stack, not by a datum.** Its z is set by boss, PCB
and standoff, so JLCPCB's +-10% on a 1.6mm board moves it +-0.16 against the rim and it can
sit that far proud. Left alone deliberately: recessing it means shortening the standoffs,
which raises the plate and takes the same amount off the cavity below the PCB, where the
MCU margin is the tightest number in the design. The lever, if the seam bothers you, is
+0.20mm of case height rather than a shorter standoff. Bumpers carry the case either way.

## Verify

The `FC_COMPARE` run holds your model to the reference everywhere it has not been
recorded as intentional, so these rows need checking by hand only where a recorded
difference touches them:

| Check                                   | Expected                                                    |
| --------------------------------------- | ----------------------------------------------------------- |
| Cavity loop size                        | 161.00 x 120.00                                             |
| Gap from cavity to board outline        | near-constant around the perimeter                          |
| Board outline points outside the cavity | none                                                        |
| Boss bore depths                        | 4.00 at every boss; none breaks into a recess               |
| Port opening centres                    | z -10.50 TRRS, -10.25 USB, both below the board             |
| Top edge in plan                        | straight across; no notch inherited from the board          |
| Plate under each bumper                 | 1.00                                                        |
| Shelf underside / plate wall top        | z -6.00 / -7.60, meeting through the board                  |
| Both halves' switch cutouts             | each cut from its own half of the DXF, 30 left and 32 right |

A wide spread in that gap means the profile is not the outline. The bore and bumper
rows are the defects a closed, correctly sized solid can still carry, so check
them with the Measure tool rather than by eye. Then **print and assemble a half before
ordering aluminium**: the printed part settles switch seating, MCU
clearance and the port openings for a few hours of filament.
