# v4 case build sheet

Feature-by-feature recipe for modelling the case in Onshape. Design rationale is in
[README.md](./README.md); this file is the numbers.

Every position is a **dimension, not a reference**. That is deliberate: a re-import
replaces the imported entities, so anything projected off them loses its reference,
while a typed value does not.

## Decisions this sheet assumes

Change any of these and the affected rows change with them.

| Decision | Assumed | Why |
| --- | --- | --- |
| Topology | Bottom tray + separate switch plate | The split falls on the mirror line: the tray mirrors, the plate cannot |
| Process | FDM print first | Prototype before committing to CNC; CNC deltas are in README.md |
| Wall thickness | 2.4mm | Six passes of a 0.4mm nozzle, so no gap fill |
| Top face | Flat | The v4.5 model's top is a single planar face; it is not slanted today |
| Board pocket clearance | 0.25mm per side | Along the straight edges the hull *is* the board edge, so this is the whole fit allowance |

## Frame

Work in the **un-filleted hull frame**: origin at the left half's outline centre,
+x right, +y up. Everything below is in that frame.

Positions taken from the KiCad board sit in the *filleted* frame and gain
**+0.205mm in y** to convert, since the fillet shortens the board 0.41mm and moves
its bbox centre half of that. The values here are already converted.

| | Value |
| --- | --- |
| Hull (per half) | 160.000 x 119.000 mm |
| Top edge | y +59.500 |
| Bottom edge | y -59.500 |
| Side edges | x ±80.000 |

## Parameters

| Parameter | Value | Source |
| --- | --- | --- |
| Total height | 15.60 mm | v4.5 model |
| Rim to board ledge | 6.00 mm | v4.5 model |
| Ledge to cavity floor (boss height) | 8.00 mm | derived |
| Ledge to tray floor | 9.60 mm | derived |
| Floor thickness | 1.60 mm | decision (4 layers at 0.4) |
| Wall thickness | 2.40 mm | decision |
| Pocket | 160.50 x 119.50 mm | hull + 0.25/side |
| Outer profile | 165.30 x 124.30 mm | pocket + wall |
| Lip inward reach | 1.50 mm | inside the board's 2mm copper keepout margin |
| Plate thickness | 1.50 mm | MX switch clip latch depth |
| Boss radius (at ledge) | 2.75 mm | DXF boss circles |
| Boss flare radius (below) | 3.75 mm | README wall-thickness note |
| Insert hole | ⌀3.60 x 5.50 deep | M2.5 heat-set melt diameter |

### Screw bosses

Left half, from the outline centre. The right half is the exact mirror (negate x).

| Boss | Position |
| --- | --- |
| Outer pinky | (-42.375, -3.650) |
| Inner pinky | (33.825, 0.050) |
| Centre | (-3.325, 22.175) |

The outer pair sits 3.70mm apart in y. That is forced: the pinky columns are
asymmetric, so the two screws cannot share a y while clearing both switch holes and
pads. Do not level them.

### Ports, on the top edge

| Feature | Position |
| --- | --- |
| USB-C notch (already in the outline) | x +56.663 .. +66.663, cut 7.271mm down from y +59.500 |
| TRRS jack centre | (74.650, 59.500) |

The USB notch is part of the imported profile, so the tray wall inherits it. The TRRS
needs an opening cut into the wall; the board's copper keepout already carves its
route ring there, so the jack's through-holes reach the edge. Add 0.3-0.4mm around
each plug body for FDM tolerance.

## Part A: tray

1. **Sketch "Outline (imported)"**, Top plane. Insert
   `dist/v4/ergogen/outlines/full_unfilleted.dxf`. Constrain the left half's outline
   centre to the origin. **Never draw in this sketch.** Re-importing is the only edit
   it should ever take.
2. **Extrude "Tray body"**, from the left-half outline region of (1), offset outward
   **2.65mm** (clearance + wall), blind **15.60mm**, -Z.
3. **Extrude cut "Board pocket"**, from the same region offset outward **0.25mm**,
   blind **6.00mm** from the rim, -Z.
4. **Extrude cut "Cavity"**, from the same region offset **inward 1.25mm** (leaving the
   1.50mm lip), from the pocket floor down to **1.60mm above the tray floor**.
5. **Bosses**, sketch on the cavity floor: three circles r **2.75** at the positions
   above; extrude up to the pocket floor, **8.00mm**. Add a second concentric extrude
   at r **3.75** for the lower 6.00mm so the insert sits in thicker wall, leaving the
   top 2.00mm at r 2.75 to match the boss circle in the DXF.
6. **Insert holes**, ⌀**3.60** blind **5.50mm** down from each boss top.
7. **TRRS opening**, cut through the wall at x **74.650**, sized to the jack body plus
   0.3-0.4mm.
8. **Bumper pads**, four shallow recesses on the bottom face, clear of the bosses.

The USB notch needs no step: it is in the imported profile and (2) carries it through.

## Part B: switch plate, per half

1. **Extrude "Plate"**, from the same import sketch, that half's outline region,
   blind **1.50mm**.
2. **Extrude cut "Switch cutouts"**, using the switch-hole curves already in the
   import. Cut them **as imported** rather than dimensioning them: they carry the
   correct corner fillets, and the two halves' patterns differ.
3. **Screw clearance holes**, ⌀2.90 at the three boss positions, counterbored for the
   M2.5 head so it sits flush.

Build the left plate and the right plate **separately**. The halves carry 30 and 32
switch cutouts, and 14 of those positions have no mirrored counterpart, so a mirrored
plate puts the wrong key field on one half. Only the tray may be mirrored.

## Screw stack

M2.5x8 through plate (1.50) + PCB (1.60) leaves 4.90mm engaging a 5.00mm insert.
A counterbore in the plate recovers whatever depth it removes, so keep it shallow or
step up a length.

## Verify before printing

Export the tray as STEP and check it against the current outline rather than by eye.
A correct model reports:

| Check | Expected |
| --- | --- |
| Pocket loop size | 160.50 x 119.50 mm |
| Gap from pocket to board outline | near-constant around the whole perimeter |
| Board outline points outside the pocket | none |

A wide spread in that gap is the signal that the profile is not the outline. The v4.5
block-out spread 17-19mm and put 79% of the board outline outside its pocket, so this
check is not academic.

The tooling that measures it is not in the repo yet. Send the STEP and it can be run,
or ask and it can be landed as a `validate:case` step.
