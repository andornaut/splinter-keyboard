# v4 case build sheet

Feature-by-feature recipe for modelling the case in Onshape. Design rationale is in
[README.md](./README.md); this file is the numbers.

Every position is a **dimension, not a reference**. That is deliberate: a re-import
replaces the imported entities, so anything projected off them loses its reference,
while a typed value does not.

## Topology

| Part | Contents |
| --- | --- |
| **Shell** | Top face and side walls, one piece. Switch cutouts are in the top |
| **Bottom** | Flat closing plate, carries the screw heads |

**No perimeter lip.** The cavity opens only at the bottom, so a 3-axis mill reaches in
from below and everything it cuts must be visible looking straight up. The board pocket
is at least as wide as the board and sits above any lip, so a lip puts a wider region
above a narrower one: an undercut no setup reaches. The same geometry blocks a printed
part, since the board also goes in from below. **The board is carried on the bosses**
and clamped by the bottom plate.

## Machining setups

Two, and the second one is bought deliberately.

| Setup | From | Features |
| --- | --- | --- |
| 1 | below | Outer profile, cavity, bosses, boss holes, port openings |
| 2 | above | The 16mm switch recesses |

The switch cutout is **nested**: a 16mm opening at the top face over a 14.5mm hole, so
the switch drops in and the surrounding top wall covers its lower body. That is the
intended look, and it is inherently wider at the top, so nothing reaches it from below.
The 14.5mm holes are through-features and can be cut in either setup.

There is no geometry that nests the switch and still machines in one setup. Flattening
the top to a single 14.5mm hole would do it, at the cost of the switch sitting proud on
a flat face.

## Decisions this sheet assumes

| Decision | Assumed | Why |
| --- | --- | --- |
| Process | Print first, then aluminium | The printed half confirms fitment before the expensive fab |
| Print orientation | Shell top-face-down on the bed | Walls and bosses rise from a flat first layer; no supports |
| Wall thickness | 3.0mm | Print wants a multiple of 0.4; CNC dislikes thin tall walls |
| Top thickness | 3.0mm, recessed 1.5mm at each switch | Stiff top; switch nests in and is carried on the recess floor |
| Cavity internal fillet | 2.0mm minimum | CNC tool radius; harmless when printed |
| Board pocket clearance | 0.25mm per side | Along the straight edges the hull *is* the board edge, so this is the whole fit allowance |

## Frame

Work in the **un-filleted hull frame**: origin at the left half's outline centre, +x
right, +y up, z=0 at the shell's top face, +z up.

Positions taken from the KiCad board sit in the *filleted* frame and gain **+0.205mm in
y** to convert, since the fillet shortens the board 0.41mm and moves its bbox centre
half of that. The values here are already converted.

| | Value |
| --- | --- |
| Hull (per half) | 160.000 x 119.000 mm |
| Top edge | y +59.500 |
| Bottom edge | y -59.500 |
| Side edges | x +-80.000 |

## Z stack

| Level | z | Source |
| --- | --- | --- |
| Shell top face | 0.00 | datum |
| Recess floor; switch flange bears here | -1.50 | switch nests 1.5mm into the top |
| Top underside | -3.00 | top thickness |
| PCB top face | -6.50 | MX plate-to-PCB 5.00 below the bearing surface **(verify on the print)** |
| PCB bottom face | -8.10 | PCB 1.6mm |
| Cavity floor / shell bottom rim | -15.60 | carried from v3, confirmed in service |
| Bottom plate underside | -17.60 | + 2.00mm plate |

The switch plate is the 1.50mm between the recess floor and the top underside.

## Parameters

| Parameter | Value | Source |
| --- | --- | --- |
| Wall thickness | 3.00 mm | decision |
| Top thickness | 3.00 mm | decision |
| Switch recess depth | 1.50 mm | nesting |
| Plate at a switch cutout | 1.50 mm | MX latch |
| Bottom plate thickness | 2.00 mm | decision |
| Board pocket | 160.50 x 119.50 mm | hull + 0.25/side |
| Shell outer profile | 166.50 x 125.50 mm | pocket + wall |
| Boss radius | 2.75 mm | DXF boss circles |
| Boss height (top underside to PCB) | 3.50 mm | z stack |
| Insert hole (print) | 3.60 dia x 5.00 deep | M2.5 melt diameter; leaves 1.50mm of top face |
| Tapped hole (machined) | 2.05 dia tap drill, M2.5x0.45 | README CNC note |
| Screw clearance (bottom plate) | 2.90 dia, counterbored | M2.5 |

### Screw bosses

Left half, from the outline centre. The right half is the exact mirror (negate x).

| Boss | Position |
| --- | --- |
| Outer pinky | (-42.375, -3.650) |
| Inner pinky | (33.825, 0.050) |
| Centre | (-3.325, 22.175) |

The outer pair sits 3.70mm apart in y. That is forced: the pinky columns are asymmetric,
so the two screws cannot share a y while clearing both switch holes and pads. Do not
level them.

### Ports, on the top edge

| Feature | Position |
| --- | --- |
| USB-C notch (already in the outline) | x +56.663 .. +66.663, cut 7.271mm down from y +59.500 |
| TRRS jack centre | (74.650, 59.500) |

Both need an opening through the side wall, sized to the plug body plus 0.3-0.4mm for a
print and 0.2-0.3mm machined.

## Part A: shell

1. **Sketch "Outline (imported)"**, Top plane. Insert
   `dist/v4/ergogen/outlines/full_unfilleted.dxf`. Constrain the left half's outline
   centre to the origin. **Never draw in this sketch.** Re-importing is the only edit it
   should ever take.
2. **Extrude "Shell body"**, from the left-half outline region of (1), offset outward
   **3.25mm** (clearance + wall), blind **15.60mm**, -Z.
3. **Extrude cut "Cavity"**, from the same region offset outward **0.25mm**, from
   **z -3.00** (the top underside) down through the open bottom. Apply the **2.0mm
   minimum internal fillet** to its vertical corners.
4. **Extrude cut "Switch recesses"**, the 16.0mm curves from the import, from the top
   face down to **z -1.50**.
5. **Extrude cut "Switch cutouts"**, the 14.5mm curves from the import, from the recess
   floor through the remaining 1.50mm. Cut both sets **as imported** rather than
   dimensioning them: they carry the correct corner fillets, and the two halves'
   patterns differ.
6. **Bosses**, sketch on the top underside (z -3.00): three circles r **2.75** at the
   positions above, extruded down **3.50mm** to meet the PCB top face.
7. **Boss holes**, from each boss's lower face upward: 3.60 dia x 5.00 deep for a
   heat-set insert, or 2.05 dia tap drill for M2.5x0.45 when machined. That leaves
   1.50mm of top face intact.
8. **Port openings** through the side wall at the two positions above.
9. Nothing else. The USB notch is in the imported profile and (2) carries it through.

## Part B: bottom plate

1. **Extrude**, from the same import sketch, the left-half outline region offset outward
   **3.25mm** so it matches the shell footprint, blind **2.00mm**.
2. **Screw holes**, 2.90 dia at the three boss positions, counterbored for the M2.5 head
   so it sits flush.
3. **Bumper recesses**, four shallow pads on the outer face, clear of the screw heads.

## Right half

Mirror **both** parts. This is safe here: the outline mirrors exactly, and with no
separate switch plate the only half-specific geometry is the switch cutouts.

Cut the right half's cutouts from the **right half of the DXF**, not from a mirrored
copy of the left half's: the halves carry 30 and 32 switch cutouts and 14 of those
positions have no mirrored counterpart, so a mirrored key field is the wrong key field.

## Printing

Top face down on the bed. The first layer is the top face with its 16mm openings; at
1.50mm the opening steps in to 14.5mm, a 0.75mm inward overhang per side that bridges
without support. Walls and bosses rise from there, so nothing else overhangs.

## Screw stack

Bottom plate (2.00) + PCB (1.60) = 3.60mm consumed before the fastener enters the boss.
An M2.5x8 leaves 4.40mm to engage a 5.00mm insert or tapped hole. A counterbore in the
bottom plate recovers whatever depth it removes.

## Verify

Export the shell as STEP and check it against the current outline rather than by eye. A
correct model reports:

| Check | Expected |
| --- | --- |
| Cavity loop size | 160.50 x 119.50 mm |
| Gap from cavity to board outline | near-constant around the whole perimeter |
| Board outline points outside the cavity | none |

A wide spread in that gap is the signal that the profile is not the outline. The v4.5
block-out spread 17-19mm and put 79% of the board outline outside its pocket, so this
check is not academic.

Then **print and assemble a half before ordering aluminium.** The printed part settles
the switch nesting depth, the port openings and the MCU clearance for a few hours of
filament rather than a CNC order.

The geometry tooling is not in the repo yet. Send the STEP and it can be run, or ask and
it can be landed as a `validate:case` step.
