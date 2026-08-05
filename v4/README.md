# Version 4 of the Splinter keyboard

A 62-key split columnar ergonomic keyboard with symmetrical enclosures and non-traditional backspace and backslash placement.

* [QMK firmware](https://github.com/andornaut/qmk_firmware/tree/splinter/keyboards/splinter)
* Build and fabrication workflow: [root README](../README.md#developing)

Each PCB half:

| Outline | Width | Height |
| --- | --- | --- |
| Un-filleted hull | 160.00 mm | 119.00 mm |
| As fabricated, after the 1.5mm corner fillet | 160.00 mm | 118.59 mm |

The fillet rounds the corners off the height; the straight side edges hold the width. See the [case design notes](./onshape/README.md).

## Changes from v3

| Change | Details |
| --- | --- |
| The [splitkb Liatris](https://splitkb.com/products/liatris) (RP2040) replaces the [Adafruit KB2040](https://www.adafruit.com/product/5302) MCU | [Microcontroller](#microcontroller) |
| A TVS diode and series resistor protect the TRRS serial line from hot-unplug transients | [TRRS data-line protection](#trrs-data-line-protection) |

## Microcontroller

The [splitkb Liatris](https://splitkb.com/products/liatris) wires its USB VBUS line to GP19, so QMK senses USB presence via `USB_VBUS_PIN` instead of the `SPLIT_USB_DETECT` polling loop. That removes the roughly two-second unresponsive window at boot and makes the board more reliable after KVM switches.

The MCU is socketed rather than soldered: it sits in two pairs of Mill-Max 12-pin sockets (see the [BOM](#bill-of-materials-bom)) so it can be removed and reused. It mounts on the bottom of the board, the same side as the diodes, hotswap sockets and the rest of the SMD parts, with its own components facing away from the board so the reset and boot buttons stay reachable. That seating determines which header column each matrix net lands on, so it is not interchangeable with the opposite orientation.

The matching firmware config (the `USB_VBUS_PIN` define and the `development_board` and split settings) lives in the [firmware repo](https://github.com/andornaut/qmk_firmware/tree/splinter/keyboards/splinter).

### Pinout

* [splitkb Liatris pinout](https://docs.splitkb.com/product-guides/liatris/pinout)
* [Custom Ergogen footprint: `mcu_liatris`](../ergogen/footprints/mcu_liatris.js), based on [ceoloide/mcu_nice_nano](../ergogen/footprints/ceoloide/mcu_nice_nano.js) and the [marbastlib KiCad footprint](https://github.com/ebastler/marbastlib)

| Left | | | Right |
| --- | --- | --- | --- |
| P1 (GP0) | | | RAW |
| P0 (GP1) | | | GND |
| GND | | | RST |
| GND | | | VCC |
| P2 (GP2) | | | P21 (GP29) |
| P3 (GP3) | | | P20 (GP28) |
| P4 (GP4) | | | P19 (GP27) |
| P5 (GP5) | | | P18 (GP26) |
| P6 (GP6) | | | P15 (GP22) |
| P7 (GP7) | | | P14 (GP20) |
| P8 (GP8) | | | P16 (GP23) |
| P9 (GP9) | | | P10 (GP21) |

The Liatris also carries five extra bottom pins (GP12 to GP16) that the footprint can place but the matrix does not use.

GP19, the `USB_VBUS_PIN`, is the Liatris's internal VBUS-sense pin rather than a header net, so it is absent from the table. The `P19` row maps to GP27, a separate matrix pin.

Which column is which is set by one parameter, `raw_pin_column` on the `mcu` footprint in [ergogen/config.yaml](./ergogen/config.yaml): `front_left` or `front_right`, named from the PCB front. From the back, where the MCU mounts, the columns read the other way round. The table above is `front_right`, the datasheet arrangement. Both halves must share the value, because the Liatris cannot be mirrored.

To check it on a physical board, seat the module and confirm its RAW pin lands on the pad silkscreened RAW. The board silk and the config net names cannot tell you: they move together when the parameter flips.

### Verifying the pin mapping

A board whose matrix nets reach the wrong MCU column is fully routed, shorts nothing, and passes DRC and every other check here. It fails only once an MCU is plugged in, which is after the boards are paid for. `npm run validate:firmware` is the gate for that, and both of its checks are required:

* **Half symmetry.** Both halves must wire the MCU header identically. Halves that disagree mean one of them is backwards.
* **Firmware agreement.** The matrix pins implied by the boards must equal the QMK [keyboard.json](https://github.com/andornaut/qmk_firmware/blob/splinter/keyboards/splinter/keyboard.json), both halves plus the serial pin.

What the checks guarantee is that the two halves agree and that the config's net assignments never silently drift from the firmware's pin arrays. What they cannot prove is that the mapping matches physical reality: both mirrorings of the header produce electrically valid boards, the footprint's silk pin labels are generated from the same table as the pad nets, and the firmware check compares net names through that same table. All three move together under a `raw_pin_column` flip.

Only hardware settles that, and it is settled: the current value, `front_right`, is confirmed on an assembled and working board. Treat it as fixed. Changing it, or changing how the MCU seats, invalidates that confirmation and needs a fresh check on hardware.

## TRRS data-line protection

v4 adds a TVS diode and series resistor on the TRRS data line to protect the MCU's serial GPIO when the cable is hot-unplugged. Each half:

```text
TRRS Ring 2 --(DATA_RAW)--+-- 100Ω --(P2)-- MCU GP2
                          |
                         TVS (clamps to GND)
                          |
                         GND
```

| Part | Role |
| --- | --- |
| TVS (bidirectional, 5V standoff) | Clamps the line to GND. Its 5V turn-on stays above the 3.3V data signal, so it does not conduct in normal use, and it clamps to roughly 9V under surge. |
| 100Ω series resistor | Limits current into the MCU pin. |

The connector pinout also changed: **GND on the sleeve, serial data on ring R2, VCC on the tip.** The sleeve breaks last when you unplug, so the halves keep a common ground through the disconnect, and the data line sits on an inner ring instead of the exposed tip.

Neither change affects firmware: the data line still terminates at the MCU serial pin, GP2.

## Copper keepout zones

`npm run ergogen` adds copper keepout rule areas to the generated boards. They ride the copy steps into `unrouted/` and `routed/` automatically. Do not hand-edit them.

| Zone | Excludes | Purpose |
| --- | --- | --- |
| Perimeter pour ring | The GND pour | Keeps the plane off the whole board edge. A 2mm ring just inside the edge, sized to clear the case support-wall lip, bridged straight across the USB cutout. |
| Perimeter route ring | Tracks, vias, conductive pads | Same ring, minus a carved-out band above the TRRS: the case's top wall has the port opening there, so the TRRS top through-holes may reach the edge. The inner vertical edge stays full height, so copper under the side wall is still flagged. |
| Screw-boss disks | Pour, tracks, vias | One disk per mounting hole, 1mm past the boss edge. |

Bare mechanical (NPTH) holes, meaning the mounting holes and the TRRS locating hole, carry no copper and are always allowed. The conductive-pad check is a custom DRC rule in each board's `<name>.kicad_dru`; it keys on pad type, so SMD lands like the hotswap sockets are caught too.

## Bill of materials (BOM)

| Description | Quantity | Part |
| --- | --- | --- |
| Diodes | 62 | [1N4148W](https://www.lcsc.com/product-detail/C81598.html) (C81598, SOD-123 switching; JLCPCB Basic, alt Jingdao C115103) |
| Hot swap sockets | 62 | [Adafruit 4958](https://www.digikey.ca/en/products/detail/adafruit-industries-llc/4958/13997772) (Kailh CPG151101S11 MX hotswap socket; DigiKey 1528-4958-ND, 20/pack) |
| Keycap set | 1 | [GMK CYL Sixes keycaps](https://www.deskhero.ca/products/gmk-sixes-keycaps-extras) and [Ergo Kit](https://www.deskhero.ca/products/gmk-sixes-keycaps-extras?variant=40182207676482) |
| Key switches | 62 | [Cherry MX Ergo Clear](https://shockport.ca/collections/switches-1/products/cherry-mx-ergo-clear) ([developer information](https://www.cherrymx.de/en/dev.html)) |
| Microcontrollers | 2 | [splitkb Liatris](https://splitkb.com/products/liatris) (RP2040) |
| Resistors | 2 | [100Ω 0805 1%](https://www.lcsc.com/product-detail/C17408.html) (C17408, UNI-ROYAL 0805W8F1000T5E; JLCPCB Basic, alt YAGEO C105577) |
| Screws | 6 | [M2.5x8mm screws](https://www.amazon.ca/gp/product/B0DLKCYKN6) (one per boss, 3 per half; the slanted case varies each screw-well depth so one length fits every boss) |
| Silicon bumpers | 8 | [10x2mm Silicone Rubber Bumpers](https://www.aliexpress.com/item/1005005315398342.html) |
| Sockets (12-pin) | 4 | [Mill-Max 315-43-112-41-003000](https://www.mouser.ca/ProductDetail/575-3154311241003000) ([series documentation](https://mm.digikey.com/Volume0/opasdata/d220001/medias/docus/2481/310%2C%20311%2C%20315%20Series%20%28in.%29.pdf)) |
| Socket pins | 48 | [Mill-Max 3320-0-00-15-00-00-03-0](https://www.mouser.ca/ProductDetail/575-3320000150000030) |
| Switches/buttons (reset) | 2 | [5.2mm SMD tact switch](https://www.lcsc.com/product-detail/C115351.html) (C115351, ALPS SKQGABE010; JLCPCB Extended, alt ALPS SKQGAFE010 C202424; hand-soldered) |
| Threaded inserts | 6 | [M2.5 threaded inserts](https://cnckitchen.store/products/gewindeeinsatz-threaded-insert-m2-5-standard-100-stk-pcs) (one per boss, 3 per half; ~3.6mm hole, ~5mm deep) |
| TRRS cables | 1 | [King Cables TRRS Cable](https://www.kingcables.org/) |
| TRRS jacks | 2 | [HCTL HC-PJ-320A-4P-D](https://www.lcsc.com/product-detail/Audio-Connector-Headphone_HCTL-HC-PJ-320A-4P-D_C5372851.html) |
| TVS diodes | 2 | [Littelfuse SMF5.0CA](https://www.lcsc.com/product-detail/C1851363.html) (C1851363, SOD-123FL bidirectional, 5V standoff; JLCPCB Extended; alt MDD C364279, TWGMC C726939) |

## Fabrication (JLCPCB)

See the root README's [fabrication step](../README.md#step-5-fabrication-jlcpcb) for how `npm run fab`, the DRC gate, and [jlcpcb-parts.json](./kicad/jlcpcb-parts.json) work. This section covers only what is v4-specific.

| Part | Assembly |
| --- | --- |
| Matrix diodes, 100Ω data-line resistor, TVS | Placed by JLCPCB |
| Hotswap sockets | Do-Not-Place. Keeping them off the assembly BOM is what holds the order on the cheaper **Economic** PCBA service: they are Standard-only and not stocked for JLC assembly. |
| MCU (Liatris), TRRS jack, reset switch | Do-Not-Place, hand-soldered |

The LCSC and vendor links in the [BOM](#bill-of-materials-bom) for Do-Not-Place parts are for sourcing only.

The diode footprint (`diode_sod123`) carries `rotation: 180` in [jlcpcb-parts.json](./kicad/jlcpcb-parts.json) so the cathode band lands on pad 1, the cathode and row net. The resistor and TVS are non-polar, so their rotation is irrelevant. After uploading, confirm orientation in JLCPCB's DFM viewer.
