# v4 case design (Onshape)

3D case models (`*.step`) live here. The case is designed in Onshape from the
Ergogen outline (`dist/v4/ergogen/outlines/full.dxf`), then printed
(OrcaSlicer) or CNC-machined (JLCCNC). See the root `README.md` steps 6-7 for
the import/order workflow; this file is design guidance.

Each half is 158 x 119mm. Left and right are mirrored, so model one and mirror,
and export each as its own `*.step` (JLCCNC quantity is set per file).

## Topology: two-piece sandwich

Design each half as a **bottom tray + a separate switch plate** that bolt
together (the v3 model does this: 2 trays + 2 plates). This keeps every part a
shallow 2.5D shape with no enclosed cavities, which is what both FDM and 3-axis
CNC want. Avoid a single body with an internal hollow.

## Printed case (OrcaSlicer)

- Internal corners can be sharp; fillet only for feel/strength.
- M3 mounting holes use heat-set inserts (see the v4 BOM), so size the holes
  for the insert's melt diameter, not a tap.
- Watch overhangs > 45 degrees and bridging over the switch cutouts.

## CNC case (JLCCNC, 6061/6063 aluminium)

A mill removes material with a round tool from above. Every feature must be
reachable by a cylindrical end mill from the top (or after one flip).

1. **No sub-tool internal corners.** Every internal vertical corner carries the
   tool radius. Design body pockets with **>= 2mm internal fillets** so a fast
   tool clears them. The MX switch cutouts (14 x 14mm) need only ~1mm corner
   fillets, but those force a <= 2mm end mill on the plate, which is slow and
   fragile. This is why the switch plate should be a **separate thin flat part**
   (1.5mm steel or aluminium, cut as a 2D profile) rather than 60+ pockets
   milled into a thick body.
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
6. **M3 holes: model at ~2.5mm tap-drill** (no modeled threads) and add CAD
   **counterbores** for the screw heads (free to machine, lets the plate sit
   flush). Upload a 2D PDF with an `M3x0.5` thread callout (depth, through/blind)
   for JLCCNC to tap; one note "all mounting holes M3x0.5 tapped, N mm deep" is
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
