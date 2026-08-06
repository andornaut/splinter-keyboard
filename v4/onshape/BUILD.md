# v4 case build sheet

Feature-by-feature recipe for modelling the case in Onshape. Design rationale is in
[README.md](./README.md); this file is the numbers.

Every position is a **dimension, not a reference**. That is deliberate: a re-import
replaces the imported entities, so anything projected off them loses its reference,
while a typed value does not.

## Terms

| Term | Means |
| --- | --- |
| **Boss** | A cylindrical pillar that takes a fastener. Three per half, hanging from the top underside down to the PCB |
| **Hull** | The un-filleted board outline, 160.00 x 119.00mm. The case is modelled to this, not to the fabricated edge |
| **Nesting / recess** | The 16mm opening at the top face that each switch drops into, so the surrounding wall covers its lower body |
| **Setup** | One fixturing of the part in the mill. Every flip is another setup and another fixed fee |

## How it goes together

```text
   top face   ------------------------------   z   0.00
                    | |            <- boss, r 2.75, 3.50mm long
   recess floor ----| |------------------      z  -1.50   switch flange bears here
   top underside ---+-+------------------      z  -3.00
                    | |
   PCB top    ------+-+------------------      z  -6.50   boss ends here
   PCB        #######o#######################  <- 2.9mm clearance hole
                     |
   bottom     -------|------------------       z -15.60
   plate      -------#------------------       M2.5x8 up from below, head counterbored
```

The PCB is clamped between the boss ends and the bottom plate. Nothing rests on a
perimeter lip, because this topology cannot have one.

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

### What the second setup costs

**Quote both variants before deciding.** Model the nested version and a flat-top version
with a single 14.5mm through-hole, upload each to JLCCNC, and compare. That delta is the
answer; everything below is only for judging whether the number looks sane.

| Factor | Assessment |
| --- | --- |
| Cutting time | Small. The recesses remove ~2cm^3 per half if the hole is cut first, ~12cm^3 if cut full-face. Roughly 10-25 min of spindle time |
| Fixed cost | Dominates. Re-fixturing, a second work offset, probing, and usually a soft jaw or vacuum plate. The same fee whether the op is 10 minutes or an hour |
| Whether it is truly additive | Possibly not. Without the recess one setup is *possible* (hold by the flat top face, hollow and profile from below). A shop may plan two ops regardless, in which case the recess costs only its cutting time |
| Quantity | Works against you. Setup amortises over parts and you need two. Spares are disproportionately cheap once the fee is paid |
| Context | Hollowing a ~19mm block to a 3mm shell likely dominates the whole part cost, so the recess op may be a modest percentage rather than a doubling |

**Fallback if the delta is large:** flatten the top for the aluminium variant only and
keep the nested look on the printed one. The nesting is a finish detail, and anodised
aluminium is the variant where surface finish already does the most work.

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
| Bottom plate top face | -14.69 | usable cavity ends here |
| Shell bottom rim / plate underside | -16.69 | plate is **inset**, flush with the rim |

The switch plate is the 1.50mm between the recess floor and the top underside.

### Where the height comes from

Everything tall mounts on side B, below the PCB: the MCU, the TRRS jack, the hotswap
sockets, the resistor and the TVS. So the 3.50mm above the PCB only has to clear the
switches, and the whole height question is below the board.

| Below the PCB | mm | Source |
| --- | --- | --- |
| Mill-Max 315-43-112-41-003000 socket, above board | 2.00 - 2.41 | measured ~2.0; datasheet `.095"` reads 2.41 |
| Liatris PCB | 1.00 | splitkb states a 1mm PCB |
| Liatris down-facing, pin stubs tallest | 2.00 | measured; the USB-C and buttons are shorter |
| MCU stack | 5.40 | measured (7.00 overall less the 1.60 main PCB) |
| **TRRS jack body (PJ-320A)** | **5.20** | **binds**; measured |
| Hotswap socket | 1.85 | Kailh CPG151101S11 |

**The TRRS jack sets the depth, not the MCU.** The Liatris is a deliberately low-profile
board and its socketed stack comes in under the jack.

| | mm |
| --- | --- |
| Top face to PCB top (MX 5.00 + 1.50 recess, fixed) | 6.50 |
| PCB | 1.60 |
| Below-PCB, set by the MCU | 5.40 |
| Bottom plate | 2.00 |
| **Minimum total** | **15.1 - 16.1** |
| Current design | 17.60 |

**There is 1.5 to 2.5mm of slack.** The case can lose height if you want it thinner,
and the amount depends on the jack, which is the number worth measuring on your v3.

Two caveats on using that slack. **The v3 service history does not transfer**: v3 carried
a KB2040, not a socketed Liatris, so the inherited 15.60mm cavity was never measured
against these parts. And the jack's height also fixes where its opening lands in the side
wall, so shrinking the cavity moves that opening.

### The slant is measured, and the clearance it leaves is thin

The case is slanted **1.4445 deg**: the top face is flat and the bottom slopes, from
**15.86mm** at the inner edge down to **11.5mm** at the outer. Confirmed two ways, from
the tilted face normals in the v4.5 STEP and from Onshape directly.

Both tall parts sit near the inner (deep) edge, which is the right place for them, but
the inset plate leaves very little:

| Part | x span | Usable at its worst x | Needs | Margin |
| --- | --- | --- | --- | --- |
| TRRS jack | 71.55 .. 77.75 | 6.35 mm | 5.20 | **+1.15** |
| Liatris | 52.78 .. 70.80 | 5.87 mm | 5.40 | **+0.47** |

**The slant is not what is squeezing this.** At 1.4445 deg it costs 0.21mm at the jack
and 0.69mm at the Liatris' far end. The 2.00mm inset plate costs far more. Four ways out,
cheapest first:

| Option | Recovers |
| --- | --- |
| Measure the jack; if it is 5.0mm rather than 6.0mm | resolves it outright, +0.55mm at the jack |
| Thin the plate to 1.2mm | +0.80mm everywhere |
| Grow the thick end 15.86 -> 17.31mm | +1.45mm, for a 1.0mm margin on a 6mm jack |
| Hang the plate below the rim instead of insetting | +2.00mm, but loses the flush look |

**Thicken the plate only where the screws are.** The MCU hangs 5.40mm below the board
and the jack 5.20mm, and a uniform 2.00mm plate leaves -0.33mm and +0.35mm. But the plate
only needs to be thick where a screw head is buried, and none of the three screws is
anywhere near the MCU or the jack. A **1.20mm plate with local bosses** gives +0.47mm and
+1.15mm at the **current** case height, so no growth is needed.

| General plate | Thick end | MCU | Jack |
| --- | --- | --- | --- |
| Uniform 2.00mm | 15.86 | -0.33 | +0.35 |
| 1.20mm, head pocket cutting into the standoff | 15.86 | +0.47 | +1.15 |
| **1.50mm, head fully inside the plate** | **16.16** | **+0.47** | **+1.15** |

**Keep the head pocket out of the standoff.** A countersunk M2.5 head is exactly 1.50mm,
so a 1.50mm plate takes it entirely and the standoff stays solid. The alternative works
geometrically, since the standoff is wider than the head, but every millimetre of pocket
forces the standoff's wide portion higher, and higher up is where the hotswap sockets are.

The standoffs have room, but not much at one position:

| Boss | Nearest side-B pad | at 8.00mm | at **5.50mm** |
| --- | --- | --- | --- |
| Outer pinky | 6.29 | 2.29 | 3.54 |
| **Inner pinky** | **4.79** | **0.79** | **2.04** |
| Centre | 6.73 | 2.73 | 3.98 |

**Use 6.00mm.** Those distances are measured to the pads, and the Kailh socket body is
larger than its lands, so the real gap is smaller by an amount the board file cannot
tell us. At 8.00mm the tightest position has 0.79mm to absorb that; at 6.00mm it has
1.79mm. Switch pitch is 19.05mm against a ~13.9mm body, leaving about 5.15mm between
switches, so there is no room to recover if it turns out tight.

**Use 5.50mm, because it is the one diameter already in the source.** It equals
2 x `screw_boss_radius`, which the DXF draws as the `_screwbosses` circles, and it is the
same diameter as the shell boss above the PCB. Project it from the import rather than
dimensioning it, and it tracks a retuned screw automatically; the board is then clamped
between identical diameters above and below.

It gives 1.00mm of wall around a 3.50mm bore, 14.1mm^2 in compression and a 1.25mm
bearing ring on the PCB, all far beyond what a clamp screw needs.

### An aluminium plate does not short anything

The only intended contact is the three standoff faces, and all three are copper-free:
`keepout_screw_bosses` clears pour, tracks and vias to 3.75mm radius and the `.kicad_dru`
rule excludes conductive pads, so a 5.50mm standoff sits well inside. Verified on the
board rather than inferred from the rule.

Elsewhere the plate stays clear: +0.47mm from the MCU, +1.07mm from the outermost hotswap
socket, +1.15mm from the jack. **Do not treat anodising as the insulator**: the layer is
microns thick, brittle, and breached by a burr or an assembly scratch. The clearance is
what protects the board. If the +0.47mm at the MCU feels thin once assembled, a film on
the plate's inner face is the cheap belt-and-braces.

The 0.30mm of cavity that a 1.50mm plate costs is bought back by 0.30mm of case height.

Span still matters more than height for the MCU: it reaches 27.22mm in from the inner
edge against the jack's 2.25mm, so it loses three times as much depth to the slope
despite being the shorter part.

Socket height is read off the series drawing rather than a labelled table: `.165"` recurs
in the two figures that differ only in tail length, which identifies it as the
above-board dimension, and the ultra-low-profile figure gives `.095"` in that position.

## Parameters

| Parameter | Value | Source |
| --- | --- | --- |
| Wall thickness | 3.00 mm | decision |
| Top thickness | 3.00 mm | decision |
| Switch recess depth | 1.50 mm | nesting |
| Plate at a switch cutout | 1.50 mm | MX latch |
| Bottom plate thickness | 1.50 mm | takes the countersunk head's full height, so the pocket never enters the standoff |
| Standoff diameter | 5.50 mm | = 2 x `screw_boss_radius`, so it is the DXF's own boss circle |
| Usable cavity below the PCB | 7.00 mm | PCB underside to plate top face |
| Board pocket | 160.50 x 119.50 mm | hull + 0.25/side |
| Shell outer profile | 166.50 x 125.50 mm | pocket + wall |
| Boss radius | 2.75 mm | DXF boss circles |
| Boss height (top underside to PCB) | 3.50 mm | z stack |
| Insert hole (print) | 3.60 dia x 5.00 deep | M2.5 melt diameter; leaves 1.50mm of top face |
| Tapped hole (machined) | 2.05 dia tap drill, M2.5x0.45 | README CNC note |
| Screw clearance (bottom plate) | 2.90 dia, 90 deg countersink | M2.5 countersunk head, ISO 7046 |

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

### The plate is inset

The plate drops into the bottom of the cavity and finishes flush with the shell rim,
rather than covering the shell's whole footprint. Its outline is therefore the cavity
outline less a fit clearance, not the shell outer profile.

**This costs 2.00mm of cavity depth**, which is why the shell is 17.10mm rather than
15.60mm. It needs no rebate: the cavity is a straight extrusion, so the plate slides up
into it and the screws locate it, which also keeps the cavity machinable from below.

The MCU's reset and boot buttons and the board's own reset switch all face the plate.
Access is by removing the plate, so no holes are needed.

### Plate thickness is set by the screw head

The heads must sit inside the plate, and enough material has to remain under them to
carry the load. M2.5 head heights, measured against the standards:

| Head type | dk | Head height | Seat | Min plate |
| --- | --- | --- | --- | --- |
| Socket head cap, ISO 4762 | 4.50 | 2.50 | counterbore | 3.30 |
| Pan head, ISO 7045 | 5.00 | 2.00 | counterbore | 2.80 |
| **Countersunk, ISO 7046** | **4.70** | **1.50** | **conical seat** | **2.00** |

Counterbore allowance is head height plus 0.80mm of material beneath. A countersink needs
less because the cone spreads load into the plate rather than bearing on a thin shoulder.

**ISO 7380 button heads do not exist in M2.5**; that standard starts at M3. So the
realistic choice is countersunk or pan head.

Plate thickness then drives the case, because the plate is inset and eats cavity:

| Plate | Suits | Thick end for a 0.50mm MCU margin | vs current 15.86 |
| --- | --- | --- | --- |
| 3.30 | socket head cap | 17.99 | +2.13 |
| 2.80 | pan head | 17.49 | +1.63 |
| **2.00** | **countersunk** | **16.69** | **+0.83** |

**M3 is not an option here**, despite being the safer default generally:

| | M2.5 | M3 |
| --- | --- | --- |
| Fits the fabricated 3.00mm board hole | 0.50mm clearance | **0.00mm, interference** |
| Countersunk head height | 1.50 | 1.65, so a thicker plate |
| Heat-set insert melt diameter | 3.60 | 4.20, leaving 0.65mm of boss wall against 0.95 |

The hole alone settles it: M3 needs 3.2 to 3.4mm, which is a config change and new boards.
The boss cannot grow to carry a larger insert either, since 5.5mm already does not fit
between 1u-spaced switch columns, which is why the screws sit in the diagonal gaps.

**Countersunk M2.5 in a 2.00mm plate is the recommendation.** It is the only head that
keeps the plate near the thickness the cavity wants, and it lands the case at a 16.69mm
thick end, under a millimetre more than today. It also suits both processes: a countersink
machines in one pass and prints acceptably face-down, which is how this plate prints.

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

**The plate carries standoffs up to the PCB underside**, so one screw runs plate,
standoff, PCB, shell boss, and everything is in compression with nothing spanning bare
air. The local thickening that buries the countersunk head is the base of the same
feature.

The standoffs must dodge components on the underside of the board, which the three screw
positions already do: none is near the MCU or the jack. The boss has 5.00mm of material
above the PCB to engage, fixed by the MX plate-to-PCB spacing.

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
