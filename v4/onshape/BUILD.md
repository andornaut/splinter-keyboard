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
| **Setup** | One fixturing of the part in the mill. Every flip is another setup and another fixed fee |

## How it goes together

```text
   top face   ------------------------------   z   0.00
                    | |            <- boss, 5.50 dia
   recess floor ----| |------------------      z  -1.50   switch flange bears here
   top underside ---+-+------------------      z  -3.00
   PCB top    ------+-+------------------      z  -6.00   boss ends here
   PCB        #######o#######################  <- 3.00mm NPTH
                    | |            <- standoff, 5.50 dia
   plate      -------#------------------       M2.5 countersunk, up from below
```

The PCB is clamped between the boss ends and the standoffs. Nothing rests on a perimeter
lip, because this topology cannot have one.

## Topology

| Part | Contents |
| --- | --- |
| **Shell** | Top face and side walls, one piece. Switch cutouts in the top |
| **Bottom plate** | Flat closing plate, inset, carries the screw heads and the standoffs |

**No perimeter lip.** The cavity opens only at the bottom, so a 3-axis mill reaches in
from below and everything it cuts must be visible looking straight up. The board pocket is
at least as wide as the board and sits above any lip, so a lip puts a wider region above a
narrower one: an undercut no setup reaches. The same geometry blocks a printed part, since
the board also goes in from below.

**The plate is inset**, finishing flush with the shell rim, so its outline is the cavity
outline less a fit clearance rather than the shell's outer profile. It consumes 1.50mm of
cavity depth. No rebate is needed or wanted: the cavity is a straight extrusion, the
screws locate the plate, and a rebate would reintroduce the undercut.

## Machining setups

| Setup | From | Features |
| --- | --- | --- |
| 1 | below | Outer profile, cavity, bosses, boss holes, port openings |
| 2 | above | The 16mm switch recesses |

The nested switch cutout is inherently wider at the top, so nothing reaches it from below.
The 14.5mm holes are through-features and can be cut in either setup. Flattening the top
to a single 14.5mm hole would buy one setup back, at the cost of the switch sitting proud
on a flat face.

**Quote both variants before deciding.** The recesses are ~10-25 minutes of spindle time,
so the adder is dominated by the fixed cost of re-fixturing, and a shop may plan two ops
regardless. Hollowing the block likely dominates the part cost either way. If the delta is
large, flatten the top for the aluminium variant only and keep the nesting on the print.

## Decisions this sheet assumes

| Decision | Assumed |
| --- | --- |
| Process | Print first, then aluminium; the printed half confirms fitment |
| Print orientation | Shell top-face-down; walls and bosses rise from a flat first layer, no supports |
| Wall thickness | 3.0mm |
| Top thickness | 3.0mm, recessed to 1.5mm at each switch |
| Cavity internal fillet | 2.0mm minimum, for CNC tool radius |
| Board pocket clearance | 0.25mm per side |

## Frame

Outline centre at the origin, +x toward the inner (thick) edge, +y up, z=0 at the shell's
top face, +z up.

Positions read off the KiCad board are in the *filleted* frame and gain **+0.205mm in y**
to convert, since the fillet shortens the board 0.41mm and moves its bbox centre half of
that. Every value here is already converted.

| | Value |
| --- | --- |
| Hull, per half | 160.000 x 119.000 |
| Top edge / bottom edge | y +59.500 / -59.500 |
| Side edges | x +-80.000 |

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
outer**.

## Parameters

| Parameter | Value | Source |
| --- | --- | --- |
| Wall thickness | 3.00 | decision |
| Top thickness | 3.00 | decision |
| Switch recess depth | 1.50 | nesting |
| Plate at a switch cutout | 1.50 | MX standard, 1.5mm +-0.1mm |
| Bottom plate | 1.50 | takes the countersunk head's full height |
| Board pocket | 160.50 x 119.50 | hull + 0.25/side |
| Shell outer profile | 166.50 x 125.50 | pocket + wall |
| Boss and standoff diameter | 5.50 | = 2 x `screw_boss_radius`, the DXF's own circle |
| Boss height | 3.00 | top underside to PCB |
| Material above the PCB at a boss | 6.00 | top 3.00 + boss 3.00 |
| Insert hole, printed | 3.60 dia x 5.00 deep | M2.5 melt diameter; leaves 1.00mm of top |
| Tapped hole, machined | 2.05 tap drill, M2.5x0.45 | |
| Screw | M2.5 countersunk, ISO 7046 | head 4.70 dia x 1.50 |
| Screw clearance in the plate | 2.90 dia, 90 deg countersink | |

### Screw bosses

Left half, from the outline centre. The right half is the exact mirror (negate x).

| Boss | Position | Standoff height | Plate + standoff + PCB |
| --- | --- | --- | --- |
| Outer pinky | (-42.375, -3.650) | 3.88 | 6.98 |
| Inner pinky | (33.825, 0.050) | 5.71 | 8.81 |
| Centre | (-3.325, 22.175) | 4.82 | 7.92 |

The outer pair sits 3.70mm apart in y. That is forced: the pinky columns are asymmetric,
so the two screws cannot share a y while clearing both switch holes and pads. Do not level
them.

**The standoffs are three different heights** because the plate is sloped, so the three
screws see stacks from 6.98 to 8.81mm before engaging. Either use three lengths or vary
the countersink depth to suit one, as the case notes already suggest for the screw wells.

**Clearance to the nearest side-B pad**: 3.54mm outer pinky, **2.04mm inner pinky**,
3.98mm centre. Those are measured to the pads, and the Kailh socket body is larger than
its lands, so the real gap at the inner pinky is smaller by an unknown amount. That is why
the standoff is 5.50 and not larger.

### Ports, on the top edge

| Feature | Position |
| --- | --- |
| USB-C notch, already in the outline | x +56.663 .. +66.663, cut 7.271mm down from y +59.500 |
| TRRS jack centre | (74.650, 59.500) |

Both need an opening through the side wall, plug body plus 0.3-0.4mm printed, 0.2-0.3mm
machined.

## Part A: shell

1. **Sketch "Outline (imported)"**, Top plane. Insert
   `dist/v4/ergogen/outlines/full_unfilleted.dxf`. Constrain the left half's outline centre
   to the origin. **Never draw in this sketch**; re-importing is the only edit it should
   take.
2. **Extrude "Shell body"**, the left-half outline region offset outward **3.25mm**
   (clearance + wall), blind **16.00mm** at the inner edge, -Z, bottom face sloped down to
   **12.00mm** at the outer edge.
3. **Extrude cut "Cavity"**, the same region offset outward **0.25mm**, from **z -3.00**
   down through the open bottom. Apply the 2.0mm minimum internal fillet to its vertical
   corners.
4. **Extrude cut "Switch recesses"**, the 16.0mm curves from the import, top face down to
   **z -1.50**.
5. **Extrude cut "Switch cutouts"**, the 14.5mm curves from the import, through the
   remaining 1.50mm. Cut both sets **as imported**: they carry the correct corner fillets,
   and the two halves' patterns differ.
6. **Bosses**, on the top underside: three circles r **2.75** at the positions above,
   extruded down **3.00mm** to the PCB top face.
7. **Boss holes**, from each boss's lower face upward, 3.60 dia x 5.00 deep or the tap
   drill.
8. **Port openings** through the side wall.

The USB notch needs no step; it is in the imported profile and (2) carries it through.

## Part B: bottom plate

1. **Extrude**, the left-half outline region offset outward **0.10mm** (cavity less a
   0.15mm fit clearance), **1.50mm** thick, lying in the sloped bottom plane and flush
   with the rim.
2. **Standoffs**, r **2.75** at the three boss positions, rising to the PCB underside at
   z -7.60. Heights are in the boss table.
3. **Screw holes**, 2.90 dia with a 90 degree countersink taking the head's full 1.50mm.
4. **Bumper recesses**, four shallow pads on the outer face, clear of the screw heads.

The MCU's reset and boot buttons and the board's own reset switch all face the plate;
access is by removing it, so no holes are needed.

## Right half

Mirror both parts: the outline mirrors exactly and the only half-specific geometry is the
switch cutouts. Cut those from the **right half of the DXF**, not from a mirrored copy of
the left's. The halves carry 30 and 32 switch cutouts and 14 positions have no mirrored
counterpart, so a mirrored key field is the wrong key field.

## Printing

Top face down. The first layer is the top face with its 16mm openings; at 1.50mm the
opening steps in to 14.5mm, a 0.75mm inward overhang per side that bridges without
support. Walls, bosses and standoffs rise from there, so nothing else overhangs.

## Clearances

| Item | Available | Needs | Margin |
| --- | --- | --- | --- |
| **Liatris** | 6.17 | 5.40 | **+0.77** |
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

**Span costs more than height on a sloped floor.** The MCU is shorter than the jack but
reaches 27.22mm in from the inner edge against the jack's 2.25mm, so it loses three times
as much depth to the slope and is the binding part.

## Open risks

**Switch seating.** The PCB sits 4.50 below the bearing surface.

| Shoulder to PCB | PCB top | Source |
| --- | --- | --- |
| 4.50 | **-6.00** (used here) | a design that works in practice |
| 5.00 | -6.50 | Cherry's 5mm PCB-to-plate figure, if measured to the plate top |

**Deeper is the safe direction**: too deep and the switch seats on the plate with its base
floating clear; too shallow and the base hits the PCB before the shoulder reaches the
recess floor, so the switch sits proud. -6.00 is the riskier of the two. Whether Cherry's
5mm is to the plate's top or bottom face could not be established; the datasheet drawings
are raster images. **To settle it**, pull a switch and measure plate top to PCB top.

**MCU seating.** The +0.77mm assumes the module's 4.75mm pin tail passes through the
4.01mm of socket and board bore and stands proud above the main PCB. If it bottoms out the
MCU seats 0.74mm lower and the margin is +0.03mm. **To settle it**, measure from the main
PCB's underside to the lowest point of the installed MCU: 5.40 means it seated.

**Hotswap socket height.** 1.85mm is from memory, not a datasheet. It has +1.22mm of
margin, so it is unlikely to bite.

## Verify

Export the shell as STEP and check it against the outline rather than by eye:

| Check | Expected |
| --- | --- |
| Cavity loop size | 160.50 x 119.50 |
| Gap from cavity to board outline | near-constant around the perimeter |
| Board outline points outside the cavity | none |

A wide spread in that gap means the profile is not the outline. Then **print and assemble
a half before ordering aluminium**: the printed part settles switch seating, MCU
clearance and the port openings for a few hours of filament.
