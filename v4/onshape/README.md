# v4 case design (Onshape)

Case models live here. The case is modelled from the Ergogen outline
(`dist/v4/ergogen/outlines/full_unfilleted.dxf`), then printed (OrcaSlicer) or CNC-machined
(JLCCNC). See the root `README.md` steps 6-7 for the import and order workflow.

Three files, three jobs:

| File | Holds |
| --- | --- |
| [BUILD.md](./BUILD.md) | Every dimension, and the feature-by-feature recipe for Onshape |
| [gen-case.py](./gen-case.py) | The same design as geometry, built and self-verified |
| This file | Why the design is shaped the way it is. **No numbers**, so it cannot drift |

## Generating a model

```bash
npm run ergogen                     # the DXF this reads
freecadcmd v4/onshape/gen-case.py
```

Writes both halves to `dist/v4/onshape/`, then reads each file back and checks it before
exiting. Options come from the environment, since `freecadcmd` treats trailing arguments as
documents to open:

| Variable | Default | Effect |
| --- | --- | --- |
| `FC_HALF` | `both` | `left`, `right` or `both` |
| `FC_EXPLODE` | `0` | mm to drop the plate by, for viewing the cavity |
| `FC_DXF` | the Ergogen hull | source outline |
| `FC_OUTDIR` | `dist/v4/onshape` | destination |

Output is solid B-rep, not a mesh, so curved features measure their nominal size and the
result can be sketched against. The self-check reads the exported file rather than the
shape in memory, because **a STEP can carry valid geometry and still import as nothing**
if its product structure is missing, which is the failure it exists to catch.

This is a check model and a cross-reference, not the master. The master is the Onshape
document, built by hand from BUILD.md.

## Board dimensions, per half

| Outline | Width | Height |
| --- | --- | --- |
| Un-filleted hull, the nominal shape | 160.00 mm | 119.00 mm |
| `Edge.Cuts`, as fabricated | 160.00 mm | 118.59 mm |

The 1.5mm wall fillet rounds the corners, so the height drops while the width holds at the
straight side edges.

## What the case takes from the board, and what it does not

- **Model to the un-filleted hull.** The fillet cuts convex corners back, so the hull
  contains the fabricated edge and a pocket cut to it cannot come out undersized. The board
  then sits with a little corner gap, which is clearance rather than slop: the shelf and the
  plate's wall bear on the flat margin along every straight edge, not at the corners.
- **Measure the cut line**, KiCad's board outline polygon, not the board bounding box. The
  box is inflated by the `Edge.Cuts` stroke on every side.
- **Nothing follows the board's USB notch.** Not the outer profile, not the cavity, not the
  plate. That notch clears the plug's overmold, which sits below the board entirely, so to
  the case it is only a bite out of an edge that should run straight. The top edge is
  straight and both ports are simply openings in the back wall.
- **The outline mirrors; the switch cutouts do not.** Both halves' outer edges come from the
  same mirrored anchors, so the shell can be modelled once and mirrored. The key field
  cannot be: the left pinky is 1.5u where the right is 1u plus an extra inner column, so the
  halves carry different cutout counts and many positions have no counterpart. **Cut each
  half's switch openings from its own half of the DXF**, which is why the export carries
  both. Export every part as its own file, since JLCCNC quantity is per file.

## Topology: shell plus bottom plate

Each half is a **shell**, top face and side walls in one piece with the switch openings in
the top, closed by a separate **bottom plate**. The cavity then opens to exactly one face,
which is what both FDM and 3-axis CNC want, and screws enter from below so their heads land
in the plate.

The switch openings are **nested**: a wider recess at the top face over the plate cutout, so
each switch drops in and the surrounding top wall covers its lower body. That look is
inherently wider at the top, so nothing reaches it from below and the machined variant takes
a second setup for the recesses alone. There is no separate switch plate; the shell's top
face is the plate.

**The board is clamped around its whole perimeter**, between a shelf hanging from the case's
top and a matching wall rising from the plate, with the bosses and standoffs doing the same
at the three screw points. Both land on the board's outer keepout ring, which exists for
exactly this, so neither bears on a ground plane. Tracks are a different matter: the route
ring is deliberately carved open over the TRRS so the jack's through-holes are not flagged,
so the shelf can cross copper there, under soldermask.

**The plate's wall stops short of the top-inner corner.** Everything that hangs below the
board is there, the MCU and the jack, and so are both ports. A wall running the full
perimeter would sit on the jack's body and block both plugs.

**Which side the shelf sits on decides whether it can be made.** Above the board, pressed up
against, it narrows the opening going up and a mill reaches it from below without trouble.
Below the board, rested down on, it would put the full-width board pocket above a narrower
lip: an undercut no setup reaches, and equally impossible to print, since the board also
goes in from below.

## Printed case (OrcaSlicer)

- Print the shell top-face-down. Walls, bosses and standoffs then rise from a flat first
  layer and nothing needs support. The outer edge bezel is the one place the part flares
  outward, at 45 degrees over the first millimetre, which prints unsupported and keeps
  elephant's foot off the edge you actually look at.
- Mounting holes take heat-set inserts, so size them for the insert's melt diameter, not a
  tap.
- **Expect the switch recesses to come out tight.** FDM holes shrink, and the recess locates
  the switch, so open them up on the print and settle the figure on a coupon before
  committing a whole shell. The same goes for the plate's fit clearance.
- Port openings are holes in a vertical wall, so their top edges bridge. Chamfer or teardrop
  them if they sag.
- The silicone bumpers mount on the plate's outer face; leave a shallow recess for each,
  clear of the screw heads.

## CNC case (JLCCNC, 6061/6063 aluminium)

A mill removes material with a round tool. Every feature has to be reachable by a
cylindrical end mill from one of the setups.

1. **Internal corners carry the tool radius**, so the cavity's corners are specified as a
   *maximum* rather than a minimum: too large a tool leaves material where the board goes.
   Do not let a shop substitute a bigger end mill.
2. **No true internal cavities and no undercuts.** Cutting from below, a feature may narrow
   going up but never widen. A chamfer or rebate at the rim is fine; a lip under the board
   pocket is not.
3. **Ports need their own setup.** Both are holes through a vertical wall, which a 3-axis
   mill reaches from neither above nor below. A right-angle head folds it back into the
   first setup if the shop has one.
4. **Model tapped holes at the tap drill**, without modelled threads, and put the thread
   callout on a 2D PDF for JLCCNC. One note covering all mounting holes is accepted, since
   they share a spec.
5. **Add clearance at the port openings.** CNC tolerance is tight, so a slip-fit modelled
   opening can come out too snug.
6. **Chamfers over fillets on top edges**: a chamfer is one pass with a chamfer mill,
   while a top-edge fillet needs a separate ball or profiling operation. The outer edge
   bezel rides along in the setup that cuts the switch recesses, so it costs almost
   nothing.
7. **Prefer through holes to blind**, and keep pocket depth modest relative to tool
   diameter.

**Print and assemble a half before ordering aluminium.** The printed part settles switch
seating, MCU clearance and the port openings for a few hours of filament, and aluminium is
far more expensive to get wrong.
