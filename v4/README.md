# Version 4 of the Splinter keyboard

* [QMK firmware](https://github.com/andornaut/qmk_firmware/tree/splinter/keyboards/splinter)

A 62-key split columnar ergonomic keyboard with symmetrical enclosures and non-traditional backspace and backslash placement.

## Changes from v3

| Change | Details |
| --- | --- |
| The reverse-mounted [splitkb Liatris](https://splitkb.com/products/liatris) (RP2040) replaces the [Adafruit KB2040](https://www.adafruit.com/product/5302) MCU | [Microcontroller](#microcontroller) |
| A TVS diode and series resistor protect the TRRS serial line from hot-unplug transients | [TRRS data-line protection](#trrs-data-line-protection) |

## Microcontroller

The reverse-mounted (facing the PCB) [splitkb Liatris](https://splitkb.com/products/liatris) (RP2040) replaces the [Adafruit KB2040](https://www.adafruit.com/product/5302) (RP2040). Its USB VBUS line is wired to GP19, so QMK senses USB presence via `USB_VBUS_PIN` (GP19) instead of the `SPLIT_USB_DETECT` polling loop. This removes the ~2-second unresponsive window at boot and makes the board more reliable after KVM switches.

The MCU is socketed, not soldered: it sits in two pairs of Mill-Max 12-pin sockets (see the [BOM](#bill-of-materials-bom)) so it can be removed and reused.

The firmware config for this (the `USB_VBUS_PIN GP19` define and the matching `development_board`/split settings) lives in the [firmware repo](https://github.com/andornaut/qmk_firmware/tree/splinter/keyboards/splinter).

### Pinout

* [splitkb Liatris pinout](https://docs.splitkb.com/product-guides/liatris/pinout)
* [Custom Ergogen footprint: `mcu_liatris`](../ergogen/footprints/mcu_liatris.js) - based on [ceoloide/mcu_nice_nano](../ergogen/footprints/ceoloide/mcu_nice_nano.js) and [marbastlib KiCad footprint](https://github.com/ebastler/marbastlib)

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

GP19 (the `USB_VBUS_PIN`) is the Liatris's internal VBUS-sense pin, not a header net, so it does not appear in the table above. The `P19` row maps to GP27, a separate matrix pin.

## TRRS data-line protection

v4 adds a TVS diode and series resistor on the TRRS data line to protect the MCU's serial GPIO when the cable is hot-unplugged. The TVS (bidirectional, 5V standoff) clamps the line to GND: its 5V turn-on voltage stays above the 3.3V data signal so it does not conduct in normal use, and it clamps to ~9V under surge. The 100Ω resistor limits current into the MCU pin. Each half:

```text
TRRS Ring 2 --(DATA_RAW)--+-- 100Ω --(P2)-- MCU GP2
                          |
                         TVS (clamps to GND)
                          |
                         GND
```

The connector pinout also changed: GND on the sleeve, serial data on ring R2, VCC on the tip. The sleeve breaks last when you unplug, so the halves keep a common ground through the disconnect, and the data line sits on an inner ring instead of the exposed tip.

Neither change affects firmware: the data line still terminates at the MCU serial pin (GP2).

## Bill of materials (BOM)

| Description | Quantity | Part |
| --- | --- | --- |
| Diodes | 62 | [1N4148W](https://www.lcsc.com/product-detail/C81598.html) (C81598, SOD-123 switching; JLCPCB Basic, alt Jingdao C115103) |
| Hot swap sockets | 62 | [Adafruit 4958](https://www.digikey.ca/en/products/detail/adafruit-industries-llc/4958/13997772) (Kailh CPG151101S11 MX hotswap socket; DigiKey 1528-4958-ND, 20/pack) |
| Keycap set | 1 | [GMK Sixes keycaps](https://www.deskhero.ca/products/gmk-sixes) and [Ortho Kit](https://www.deskhero.ca/products/gmk-sixes?variant=39360309329986) |
| Key switches | 62 | [Cherry MX Ergo Clear](https://shockport.ca/collections/switches-1/products/cherry-mx-ergo-clear) ([developer information](https://www.cherrymx.de/en/dev.html)) |
| Microcontrollers | 2 | [splitkb Liatris](https://splitkb.com/products/liatris) (RP2040) |
| Resistors | 2 | [100Ω 0805 1%](https://www.lcsc.com/product-detail/C17408.html) (C17408, UNI-ROYAL 0805W8F1000T5E; JLCPCB Basic, alt YAGEO C105577) |
| Screws | 2 | [M3x8mm screws](https://www.amazon.ca/1021Pcs-Stainless-Assortment-Machinery-Furniture/dp/B0B292QDWG) |
| Screws | 2 | [M3x10mm screws](https://www.amazon.ca/1021Pcs-Stainless-Assortment-Machinery-Furniture/dp/B0B292QDWG) |
| Silicon bumpers | 8 | [10x2mm Silicone Rubber Bumpers](https://www.aliexpress.com/item/1005005315398342.html) |
| Sockets (12-pin) | 4 | [Mill-Max 315-43-112-41-003000](https://www.mouser.ca/ProductDetail/575-3154311241003000) ([Series documentation](https://mm.digikey.com/Volume0/opasdata/d220001/medias/docus/2481/310%2C%20311%2C%20315%20Series%20%28in.%29.pdf)) |
| Socket pins | 48 | [Mill-Max 3320-0-00-15-00-00-03-0](https://www.mouser.ca/ProductDetail/575-3320000150000030) |
| Switches/buttons (reset) | 2 | [5.2mm SMD tact switch](https://www.lcsc.com/product-detail/C115351.html) (C115351, ALPS SKQGABE010; JLCPCB Extended, alt ALPS SKQGAFE010 C202424; hand-soldered, not JLC-assembled) |
| Threaded inserts | 4 | [M3x5x4 threaded inserts](https://cnckitchen.store/products/made-for-voron-gewindeeinsatz-threaded-insert-m3x5x4-100-stk-pcs) |
| TRRS cables | 1 | [King Cables TRRS Cable](https://www.kingcables.org/) |
| TRRS jacks | 2 | [HCTL HC-PJ-320A-4P-D](https://www.lcsc.com/product-detail/Audio-Connector-Headphone_HCTL-HC-PJ-320A-4P-D_C5372851.html) |
| TVS diodes | 2 | [Littelfuse SMF5.0CA](https://www.lcsc.com/product-detail/C1851363.html) (C1851363, SOD-123FL bidirectional, 5V standoff; JLCPCB Extended; alt MDD C364279, TWGMC C726939) |

## Fabrication (JLCPCB)

See the root README's [Fabrication step](../README.md#step-5-fabrication-jlcpcb) for how `npm run fab`, the DRC gate, and [jlcpcb-parts.json](./kicad/jlcpcb-parts.json) work. This section covers only what is v4-specific.

JLCPCB assembles the three SMD parts that have an LCSC link: the matrix diodes, the 100Ω data-line resistor, and the TVS. Everything else is sourced separately and hand-soldered or hand-assembled. The MCU (Liatris), TRRS jack, reset switch, and hotswap sockets are **Do-Not-Place**; their LCSC/vendor links in the [BOM](#bill-of-materials-bom) are for sourcing only. The hotswap sockets are the parts kept off the assembly BOM to stay on the cheaper **Economic** PCBA service: they are Standard-only and not stocked for JLC assembly.

The diode (`diode_sod123`) carries `rotation: 180` in [jlcpcb-parts.json](./kicad/jlcpcb-parts.json) so the cathode band lands on pad 1 (the cathode/row net); the resistor and TVS are non-polar, so their rotation is irrelevant. After uploading, confirm orientation in JLCPCB's DFM viewer.
