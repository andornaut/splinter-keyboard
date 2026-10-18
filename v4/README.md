# Version 4 of the Splinter keyboard

A 62-key split columnar ergonomic keyboard with symmetrical enclosures and non-traditional backspace and backslash placement.

- [QMK firmware](https://github.com/andornaut/qmk_firmware/tree/splinter/keyboards/splinter)
- Build and fabrication workflow: [root README](../README.md#developing)

Each PCB half:

| Outline                                      | Width     | Height    |
| -------------------------------------------- | --------- | --------- |
| Un-filleted hull                             | 160.00 mm | 119.00 mm |
| As fabricated, after the 1.5mm corner fillet | 160.00 mm | 118.59 mm |

The fillet rounds the corners off the height; the straight side edges hold the width. See the [case design notes](./onshape/README.md).

## Changes from v3

| Change                                                                                                                                         | Details                                    |
| ---------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------ |
| The [splitkb Liatris](https://splitkb.com/products/liatris) (RP2040) replaces the [Adafruit KB2040](https://www.adafruit.com/product/5302) MCU | [Microcontroller](#microcontroller)        |
| A TVS diode protects the TRRS serial line from ESD, and each jack contact has its own pad                                                      | [Split connection](#split-connection-trrs) |

## Microcontroller

The [splitkb Liatris](https://splitkb.com/products/liatris) wires its USB VBUS line to GP19, so QMK senses USB presence via `USB_VBUS_PIN` instead of the `SPLIT_USB_DETECT` polling loop. That removes the roughly two-second unresponsive window at boot and makes the board more reliable after KVM switches.

The MCU is socketed rather than soldered: each one sits in a pair of Mill-Max 12-pin sockets (see the [BOM](#bill-of-materials-bom)) so it can be removed and reused. It mounts on the bottom of the board, the same side as the diodes, hotswap sockets and the rest of the SMD parts, with its own components facing away from the board so the reset and boot buttons stay reachable. That seating determines which header column each matrix net lands on, so it is not interchangeable with the opposite orientation.

The matching firmware config (the `USB_VBUS_PIN` define and the `development_board` and split settings) lives in the [firmware repo](https://github.com/andornaut/qmk_firmware/tree/splinter/keyboards/splinter).

### Pinout

- [splitkb Liatris pinout](https://docs.splitkb.com/product-guides/liatris/pinout)
- [Custom Ergogen footprint: `mcu_liatris`](../ergogen/footprints/mcu_liatris.js), based on [ceoloide/mcu_nice_nano](../ergogen/footprints/ceoloide/mcu_nice_nano.js) and the [marbastlib KiCad footprint](https://github.com/ebastler/marbastlib)

| Left     |     |     | Right      |
| -------- | --- | --- | ---------- |
| P1 (GP0) |     |     | RAW        |
| P0 (GP1) |     |     | GND        |
| GND      |     |     | RST        |
| GND      |     |     | VCC        |
| P2 (GP2) |     |     | P21 (GP29) |
| P3 (GP3) |     |     | P20 (GP28) |
| P4 (GP4) |     |     | P19 (GP27) |
| P5 (GP5) |     |     | P18 (GP26) |
| P6 (GP6) |     |     | P15 (GP22) |
| P7 (GP7) |     |     | P14 (GP20) |
| P8 (GP8) |     |     | P16 (GP23) |
| P9 (GP9) |     |     | P10 (GP21) |

The Liatris also carries five extra bottom pins (GP12 to GP16) that the footprint can place but the matrix does not use.

GP19, the `USB_VBUS_PIN`, is the Liatris's internal VBUS-sense pin rather than a header net, so it is absent from the table. The `P19` row maps to GP27, a separate matrix pin.

Which column is which is set by one parameter, `raw_pin_column` on the [`mcu_liatris`](../ergogen/footprints/mcu_liatris.js) footprint: `front_left` or `front_right`, named from the PCB front. [ergogen/config.yaml](./ergogen/config.yaml) sets it explicitly to `front_right`, the footprint's default. From the back, where the MCU mounts, the columns read the other way round. The table above is `front_right`, the datasheet arrangement. Both halves must share the value, because the Liatris cannot be mirrored.

To check it on a physical board, seat the module and confirm its RAW pin lands on the pad silkscreened RAW. The board silk and the config net names cannot tell you: they move together when the parameter flips.

### Verifying the pin mapping

A board whose matrix nets reach the wrong MCU column is fully routed, shorts nothing, and passes DRC and every other check here. It fails only once an MCU is plugged in, which is after the boards are paid for. `npm run validate:firmware` is the gate for that, and both of its checks are required:

- **Half symmetry.** Both halves must wire the MCU header identically. Halves that disagree mean one of them is backwards.
- **Firmware agreement.** The matrix pins implied by the boards must equal the QMK [keyboard.json](https://github.com/andornaut/qmk_firmware/blob/splinter/keyboards/splinter/keyboard.json), both halves plus the serial pin.

What the checks guarantee is that the two halves agree and that the config's net assignments never silently drift from the firmware's pin arrays. What they cannot prove is that the mapping matches physical reality: both mirrorings of the header produce electrically valid boards, the footprint's silk pin labels are generated from the same table as the pad nets, and the firmware check compares net names through that same table. All three move together under a `raw_pin_column` flip.

Only hardware settles that, and it is settled: the current value, `front_right`, is confirmed on an assembled and working board. Treat it as fixed. Changing it, or changing how the MCU seats, invalidates that confirmation and needs a fresh check on hardware.

## Split connection (TRRS)

A TRRS cable joins two HCTL HC-PJ-320A-4P-D jacks. The half with USB is the primary; it powers the other half over the cable and talks to it on one half-duplex serial line.

**Never plug or unplug the TRRS cable while either half has USB.** Unplug USB first; connect the TRRS cable before USB.

### Pinout

| Plug contact | Jack pad | Net | Liatris pin | Carries                       |
| ------------ | -------- | --- | ----------- | ----------------------------- |
| Tip          | T        | VCC | VCC         | 3.6V supply to the other half |
| Ring 1       | R1       | -   | -           | nothing                       |
| Ring 2       | R2       | P2  | GP2         | half-duplex serial data       |
| Sleeve       | S        | GND | GND         | common ground                 |

The jack footprint, [`trrs_hc_pj320a`](../ergogen/footprints/trrs_hc_pj320a.js), follows HCTL's recommended layout and names each pad for the plug contact it reaches. Both halves mount the jack on the back, so both use the same pin pattern.

### Data path, each half

```text
jack R2 --(P2)--+-- Liatris GP2
                |
               TVS
                |
               GND
```

| Part            | Specification                                                                  | Function                       |
| --------------- | ------------------------------------------------------------------------------ | ------------------------------ |
| TVS             | Littelfuse SMF5.0CA (C1851363), bidirectional, 5V standoff, 6.4V breakdown min | Clamps ESD and cable discharge |
| Series resistor | None                                                                           | See below                      |

### Decisions

| Decision                                     | Rationale                                                                                                                                                                                                                                                                                                                                                  |
| -------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| No series resistance on the data line        | QMK's RP2040 half-duplex driver has the receiving half drive the line high (2mA setting) while the sender pulls it low (12mA), so the receiver reads a divider and series resistance lifts the low it sees. With nothing in series the low is about 0.36V against a 0.8V input-low limit; 100Ω per half lifts it well above that limit and the link fails. |
| Bidirectional TVS with a 5V standoff         | It conducts only above 6.4V, so never on the 3.6V line in either polarity. It absorbs ESD energy; the RP2040's own clamp diodes conduct from about 4.1V. Its capacitance, about 1nF per half, settles within a small fraction of a bit at the default 230400 baud because the receiver drives the line high actively.                                      |
| Sleeve on GND                                | The sleeve is the largest exposed contact on a loose plug, so it is the one that must not be live.                                                                                                                                                                                                                                                         |
| Ring 1 unconnected                           | Only the tip carries VCC. With ring 1 on VCC as well, two cable conductors meet at the far half's VCC, and a part-withdrawn plug bridges them from the near half's VCC spring to its sleeve (GND) spring: a direct short of the supply. With one VCC conductor no plug position closes that loop.                                                          |
| Liatris VCC jumper set to 3.6V (both halves) | The [VCC pin](https://docs.splitkb.com/product-guides/liatris/pinout) outputs USB voltage (about 5V) by default. A momentary VCC-to-data contact would then exceed the RP2040's 4.1V pin limit (IOVDD + 0.5V). At 3.6V nothing on the cable is above the logic supply. After setting it, confirm the half without USB still runs as the secondary.         |
| No hot-plugging                              | Each band of a 3.5mm plug slides across the jack's other springs on the way in and out, so no pinout avoids momentary contact between VCC, data and GND. The choices above reduce what that contact can do; they do not make hot-plugging safe.                                                                                                            |
| Never pair with a symmetric-footprint board  | Boards built with the symmetric `ceoloide/trrs_pj320a` footprint carry VCC on the sleeve and GND on ring 2. On one cable with a board of this revision, the sleeve joins VCC to GND. Build and use both halves from the same revision.                                                                                                                     |

Firmware: `split.serial.pin` is GP2 on both halves, using the vendor (PIO) driver in half-duplex mode; `USB_VBUS_PIN` (GP19) decides which half is primary.

## Copper keepout zones

`npm run ergogen` adds copper keepout rule areas to the generated boards. They ride the copy steps into `unrouted/` and `routed/` automatically. Do not hand-edit them.

| Zone                 | Excludes                      | Purpose                                                                                                                                                                                                                                         |
| -------------------- | ----------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Perimeter pour ring  | The GND pour                  | Keeps the plane off the whole board edge. A ring just inside the edge, sized to clear the case support-wall lip, bridged straight across the USB cutout.                                                                                        |
| Perimeter route ring | Tracks, vias, conductive pads | Same ring, minus a carved-out band above the TRRS: the case's top wall has the port opening there, so the TRRS top through-holes may reach the edge. The inner vertical edge stays full height, so copper under the side wall is still flagged. |
| Screw-boss disks     | Pour, tracks, vias            | One disk per mounting hole, extending past the boss edge by the margin the script sets.                                                                                                                                                         |

Bare mechanical (NPTH) holes, meaning the mounting holes and the TRRS locating hole, carry no copper and are always allowed. The conductive-pad check is a custom DRC rule in each board's `<name>.kicad_dru`; it keys on pad type, so SMD lands like the hotswap sockets are caught too.

## Bill of materials (BOM)

| Description              | Quantity | Part                                                                                                                                                                                                                                 |
| ------------------------ | -------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Diodes                   | 62       | [1N4148W](https://www.lcsc.com/product-detail/C81598.html) (C81598, SOD-123 switching; JLCPCB Basic, alt Jingdao C115103)                                                                                                            |
| Hot swap sockets         | 62       | [Adafruit 4958](https://www.digikey.ca/en/products/detail/adafruit-industries-llc/4958/13997772) (Kailh CPG151101S11 MX hotswap socket; DigiKey 1528-4958-ND, 20/pack)                                                               |
| Keycap set               | 1        | [GMK CYL Sixes keycaps](https://www.deskhero.ca/products/gmk-sixes-keycaps-extras) and [Ergo Kit](https://www.deskhero.ca/products/gmk-sixes-keycaps-extras?variant=40182207676482)                                                  |
| Key switches             | 62       | [Cherry MX Ergo Clear](https://shockport.ca/collections/switches-1/products/cherry-mx-ergo-clear)                                                                                                                                    |
| Microcontrollers         | 2        | [splitkb Liatris](https://splitkb.com/products/liatris) (RP2040). Set each module's VCC jumper to 3.6V before use; see [Split connection](#split-connection-trrs)                                                                    |
| Screws                   | 6        | M2.5x10 button head, ISO 7380 (one per boss, 3 per half). The counterbores put every head at one level, so one length serves all six; see the [case build sheet](./onshape/BUILD.md#screw-bosses)                                    |
| Silicon bumpers          | 8        | [10x2mm Silicone Rubber Bumpers](https://www.aliexpress.com/item/1005005315398342.html)                                                                                                                                              |
| Sockets (12-pin)         | 4        | [Mill-Max 315-43-112-41-003000](https://www.mouser.ca/ProductDetail/575-3154311241003000) ([series documentation](https://mm.digikey.com/Volume0/opasdata/d220001/medias/docus/2481/310%2C%20311%2C%20315%20Series%20%28in.%29.pdf)) |
| Socket pins              | 48       | [Mill-Max 3320-0-00-15-00-00-03-0](https://www.mouser.ca/ProductDetail/575-3320000150000030)                                                                                                                                         |
| Switches/buttons (reset) | 2        | [5.2mm SMD tact switch](https://www.lcsc.com/product-detail/C115351.html) (C115351, ALPS SKQGABE010; JLCPCB Extended, alt ALPS SKQGAFE010 C202424; hand-soldered)                                                                    |
| Threaded inserts         | 6        | [M2.5 threaded inserts](https://cnckitchen.store/products/gewindeeinsatz-threaded-insert-m2-5-standard-100-stk-pcs) (one per boss, 3 per half; 3.6mm hole, bore depth in the [case build sheet](./onshape/BUILD.md#screw-bosses))    |
| TRRS cables              | 1        | [King Cables TRRS Cable](https://www.kingcables.org/)                                                                                                                                                                                |
| TRRS jacks               | 2        | [HCTL HC-PJ-320A-4P-D](https://www.lcsc.com/product-detail/Audio-Connector-Headphone_HCTL-HC-PJ-320A-4P-D_C5372851.html)                                                                                                             |
| TVS diodes               | 2        | [Littelfuse SMF5.0CA](https://www.lcsc.com/product-detail/C1851363.html) (C1851363, SOD-123FL bidirectional, 5V standoff; JLCPCB Extended; alt MDD C364279, TWGMC C726939)                                                           |

## Fabrication (JLCPCB)

See the root README's [fabrication step](../README.md#step-5-fabrication-jlcpcb) for how `npm run fab`, the DRC gate, and [jlcpcb-parts.json](./kicad/jlcpcb-parts.json) work. This section covers only what is v4-specific.

| Part                                   | Assembly                                                                                                                                                                   |
| -------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Matrix diodes, TVS                     | Placed by JLCPCB                                                                                                                                                           |
| Hotswap sockets                        | Do-Not-Place. Keeping them off the assembly BOM is what holds the order on the cheaper **Economic** PCBA service: they are Standard-only and not stocked for JLC assembly. |
| MCU (Liatris), TRRS jack, reset switch | Do-Not-Place, hand-soldered                                                                                                                                                |

The LCSC and vendor links in the [BOM](#bill-of-materials-bom) for Do-Not-Place parts are for sourcing only.

The diode footprint (`diode_sod123`) carries `rotation: 180` in [jlcpcb-parts.json](./kicad/jlcpcb-parts.json) so the cathode band lands on pad 1, the cathode and row net. The TVS is bidirectional, so its rotation is irrelevant. After uploading, confirm orientation in JLCPCB's DFM viewer.
