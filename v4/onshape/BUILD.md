# v4 case build sheet

Feature-by-feature recipe for modelling the case in Onshape. Design rationale is in
[README.md](./README.md); this file is the numbers.

Every position is a **dimension, not a reference**. That is deliberate: a re-import
replaces the imported entities, so anything projected off them loses its reference,
while a typed value does not.

## Topology

Two parts, and one design consequence that drives most of the rest:

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

That buys a **single machining setup**: screws enter from below, so counterbores live in
the bottom plate and every shell feature is reachable from one direction.

## Decisions this sheet assumes

| Decision | Assumed | Why |
| --- | --- | --- |
| Process | Print first, same model must machine | Drives the no-undercut rule above |
| Print orientation | Shell top-face-down on the bed | Bosses and walls rise from a flat first layer; no supports |
| Wall thickness | 3.0mm | Print wants a multiple of 0.4; CNC wants >= 1.5mm and dislikes thin tall walls |
| Top thickness | 1.5mm | MX switch clip latch depth |
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

Measured down from the top face. **The MX spacing is the binding constraint; verify the
two marked rows against a switch and your assembled v3 before printing.**

| Level | z | Source |
| --- | --- | --- |
| Shell top face | 0.00 | datum |
| Top underside | -1.50 | top thickness |
| PCB top face | -5.00 | MX plate-to-PCB standard **(verify)** |
| PCB bottom face | -6.60 | PCB 1.6mm |
| Cavity floor / shell bottom rim | -15.60 | v4.5 model **(verify against the MCU + Mill-Max stack)** |
| Bottom plate underside | -17.60 | + 2.00mm plate |

## Parameters

| Parameter | Value | Source |
| --- | --- | --- |
| Wall thickness | 3.00 mm | decision |
| Top thickness | 1.50 mm | MX latch |
| Bottom plate thickness | 2.00 mm | decision |
| Board pocket | 160.50 x 119.50 mm | hull + 0.25/side |
| Shell outer profile | 166.50 x 125.50 mm | pocket + wall |
| Boss radius | 2.75 mm | DXF boss circles |
| Boss height (top underside to PCB) | 3.50 mm | z stack |
| Insert hole (print) | 3.60 dia x 5.50 deep | M2.5 heat-set melt diameter |
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
   **z -1.50** down through the open bottom. Apply the **2.0mm minimum internal fillet**
   to its vertical corners.
4. **Extrude cut "Switch cutouts"**, using the switch-hole curves already in the import,
   through the top face. Cut them **as imported** rather than dimensioning them: they
   carry the correct corner fillets, and the two halves' patterns differ.
5. **Bosses**, sketch on the top underside (z -1.50): three circles r **2.75** at the
   positions above, extruded down **3.50mm** to meet the PCB top face.
6. **Boss holes**, from each boss's lower face: 3.60 dia x 5.50 deep for a heat-set
   insert, or 2.05 dia tap drill for M2.5x0.45 when machined.
7. **Port openings** through the side wall at the two positions above.
8. Nothing else. The USB notch is in the imported profile and (2) carries it through.

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

## Screw stack

Bottom plate (2.00) + PCB (1.60) = 3.60mm before the fastener enters the boss. An
M2.5x8 leaves 4.40mm of engagement, which suits a 5mm insert or a tapped boss. A
counterbore in the bottom plate recovers whatever depth it removes.

## Verify before printing

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

The tooling that measures it is not in the repo yet. Send the STEP and it can be run, or
ask and it can be landed as a `validate:case` step.
