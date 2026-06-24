# v4 case design (Onshape)

3D case models (`*.step`) live here. The case is designed in Onshape from the
Ergogen outline (`dist/v4/ergogen/outlines/full.dxf`), then printed
(OrcaSlicer) or CNC-machined (JLCCNC). See the root `README.md` steps 6-7 for
the import/order workflow; this file is design guidance.

Each half is 160 x 119mm un-filleted (the nominal hull); the actual Edge.Cuts
outline is ~160.0 x 118.5mm after the 1.5mm wall fillet rounds the corners (the
straight side edges set the 160mm width, so only the height drops ~0.5mm). Model
the case to the filleted outline. The case's support-wall lip rests on the
board's outer ~2mm margin (the perimeter copper keepout keeps that margin clear,
so the lip presses on bare substrate, not copper). Left and right are mirrored, so
model one and mirror, and export each as its own `*.step` (JLCCNC quantity is set
per file).

## Topology: two-piece sandwich

Design each half as a **bottom tray + a separate switch plate** that bolt
together (the v3 model does this: 2 trays + 2 plates). This keeps every part a
shallow 2.5D shape with no enclosed cavities, which is what both FDM and 3-axis
CNC want. Avoid a single body with an internal hollow.

## Printed case (OrcaSlicer)

- Internal corners can be sharp; fillet only for feel/strength.
- M2.5 mounting holes use heat-set inserts (see the v4 BOM), so size the holes
  for the insert's melt diameter (~3.6mm), not a tap.
- Mounting-boss wall is thin at the PCB face: the boss is ~5.5mm across (it sits
  tangent in the diagonal gap between switch cutouts, so it cannot grow in-plane),
  and a ~3.6mm insert leaves under ~1mm of wall, which can split under install
  heat or clamp load. Flare the boss below the plate plane (e.g. ~5.5mm at the
  face, ~7-8mm lower down, away from the switch cutouts) so the insert sits in
  thicker wall. The DXF boss-reference circle and PCB keepout only constrain the
  board plane, not the geometry below it.
- The insert is ~5mm deep, so make each boss column >= ~6mm tall (this is
  separate from the floor >= 1mm rule below).
- Cut the USB-C and TRRS port openings into the side wall (the PCB keepout
  already carves the route ring above the TRRS so its top through-holes reach the
  board edge). Add ~0.3-0.4mm clearance around each plug body for FDM tolerance.
- Recess each screw head in a counterbored well so it sits flush. The case is
  slanted (inner edge taller than the outer), so vary each well's depth to keep a
  single screw length (M2.5x8mm) at every boss instead of stocking two lengths.
- The 8 silicone bumpers (4 per half) mount on the bottom face; leave a flat pad
  or shallow recess for each, clear of the screw wells.
- Watch overhangs > 45 degrees and bridging over the switch cutouts.

## CNC case (JLCCNC, 6061/6063 aluminium)

A mill removes material with a round tool from above. Every feature must be
reachable by a cylindrical end mill from the top (or after one flip).

1. **No sub-tool internal corners.** Every internal vertical corner carries the
   tool radius. Design body pockets with **>= 2mm internal fillets** so a fast
   tool clears them. The MX switch cutouts (14 x 14mm; the 14.5mm figure in the
   PCB keepout/boss-clearance rules is the surround inset around each hole, a
   separate feature) need only ~1mm corner fillets, but those force a <= 2mm end
   mill on the plate, which is slow and fragile. This is why the switch plate
   should be a **separate thin flat part** (1.5mm steel or aluminium, cut as a 2D
   profile) rather than 60+ pockets milled into a thick body.
2. **No true internal cavities and no undercuts.** Open every pocket to one
   face. Keep the curved outer hull walls vertical (no overhang that narrows
   toward the bottom), or a 3-axis mill cannot reach them.
3. **Wall >= 1.5mm, floor >= 1mm.** Print walls are often thinner than what
   mills without chatter; thicken them for the CNC variant.
4. **Shallow pockets.** Keep pocket depth <= ~4x the tool diameter; widen or
   step deep narrow pockets.
5. **Chamfers over fillets on top edges (prototype).** A 45-degree chamfer is
   one pass and looks sharp on anodized aluminium; top-edge fillets each need a
   separate ball/chamfer operation. Keep fillets only where you want soft feel.
6. **M2.5 holes: model at ~2.05mm tap-drill** (no modeled threads) and add CAD
   **counterbores** for the screw heads (free to machine, lets the plate sit
   flush). Upload a 2D PDF with an `M2.5x0.45` thread callout (depth, through/blind)
   for JLCCNC to tap; one note "all mounting holes M2.5x0.45 tapped, N mm deep" is
   accepted since every hole shares the spec.
7. **Connector cutouts:** add ~0.2-0.3mm clearance around the USB and TRRS
   openings for the plug body. CNC tolerance is tight, so a slip-fit modeled
   opening can come out too snug.
8. **One setup is cheapest.** Put the precision features (plate, port cutouts)
   on one face; each flip to reach the bottom adds a setup and cost. Through
   holes are cheaper than blind.

**Order one half first** as a prototype before the mirrored pair: aluminium CNC
is far more expensive than a print, and a plate/port/boss fit problem is cheaper
to catch on a single part.
