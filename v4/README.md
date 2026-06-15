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

### Firmware changes required

Add to `config.h`:

```c
#define USB_VBUS_PIN GP19
```

Remove from `config.h` (no longer needed):

```c
#define SPLIT_WATCHDOG_ENABLE
#define SPLIT_WATCHDOG_TIMEOUT 3000
```

Remove the `SPLIT_USB_DETECT` comment block from `config.h`: VBUS detection replaces the polling loop, so it no longer applies.

Update `keyboard.json`:

```json
"development_board": "liatris"
```

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

## TRRS data-line protection

v4 adds a TVS diode and series resistor on the TRRS data line to protect the MCU's serial GPIO when the cable is hot-unplugged. The TVS (bidirectional, 5V standoff) clamps the line to GND; the 100Ω resistor limits current into the MCU pin. Each half:

```text
TRRS Ring 2 --(DATA_RAW)--+-- 100Ω --(P0)-- MCU GP1
                          |
                         TVS (clamps to GND)
                          |
                         GND
```

The connector pinout also changed: GND on the sleeve, serial data on ring R2, VCC on the tip. The sleeve breaks last when you unplug, so the halves keep a common ground through the disconnect, and the data line sits on an inner ring instead of the exposed tip.

Neither change affects firmware: the serial pin is still GP1.

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
| TVS diodes | 2 | [Littelfuse SMF5.0CA](https://www.lcsc.com/product-detail/C1851363.html) (C1851363, SOD-123FL bidirectional, 5V standoff; JLCPCB Extended, low stock, re-confirm before ordering; alt MDD C364279, TWGMC C726939) |

## Fabrication (JLCPCB)

JLCPCB assembles the three SMD parts that have an LCSC link (diode, resistor, TVS). Everything else is sourced separately and hand-soldered or hand-assembled. The MCU (Liatris), TRRS jack, reset switch, and hotswap sockets are **Do-Not-Place**; their LCSC/vendor links are for sourcing only. The hotswap sockets stay off the assembly BOM on purpose: they are Standard-only and not stocked for JLC assembly, so including them would push the order to JLCPCB's pricier **Standard** PCBA service instead of the cheaper **Economic** one.

`npm run fab-jlcpcb` exports everything JLCPCB needs from the routed masters `v4/kicad/routed/{left,right}.kicad_pcb` to `dist/v4/kicad/jlcpcb/{left,right}/`:

* **Gerbers + drill**: zipped per board; upload this to order the bare PCB.
* **BOM + CPL** (`<name>-BOM.csv`, `<name>-CPL.csv`): assembly files for JLCPCB PCBA. Generated only when [jlcpcb-parts.json](./kicad/jlcpcb-parts.json) is present; without it, the script produces gerbers only.

### How parts are assigned

LCSC part numbers live in [jlcpcb-parts.json](./kicad/jlcpcb-parts.json), not in the `.kicad_pcb`, so they survive when Ergogen regenerates the boards. The file is keyed by **footprint name** (the `Package` column of the position file), because the generated footprints have empty `Value` fields. Each entry has `lcsc`, `comment` (BOM Comment), `package` (BOM Footprint), and `rotation` (added to KiCad's angle to fix pick-and-place orientation). `scripts/gen-jlcpcb-bom-cpl.py` joins this against the position file:

* footprint **absent** from the JSON -> Do-Not-Place (MCU, TRRS jack, reset switch, hotswap sockets, mounting holes)
* footprint present with **empty `lcsc`** -> error; nothing is written until you fill it in
* footprint present with **`lcsc` set** -> placed in both the BOM (grouped by LCSC) and CPL (rotation-corrected)

### Ordering

1. Route `v4/kicad/{left,right}.kicad_pcb`, copy them to the routed masters with `npm run copy-pcbs-kicad-to-routed`, then run `npm run fab-jlcpcb`.
2. Order the bare PCB: upload the gerber zip (`dist/v4/kicad/jlcpcb/{left,right}/{left,right}-gerber.zip`). For PCBA: also upload the per-board BOM/CPL (`{left,right}-BOM.csv` and `{left,right}-CPL.csv`, in the same `dist/v4/kicad/jlcpcb/<name>/` dir).
3. Check placement in JLCPCB's [DFM viewer](https://cart.jlcpcb.com/quote/gerberviewThree). If a part is mis-oriented, adjust its `rotation` in [jlcpcb-parts.json](./kicad/jlcpcb-parts.json) and re-run.
