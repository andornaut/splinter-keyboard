# Version 4 of the Splinter keyboard

* [QMK firmware](https://github.com/andornaut/qmk_firmware/tree/splinter/keyboards/splinter)

A 62-key split columnar ergonomic keyboard - Symmetrical enclosures.
Non-traditional placement of backspace and backslash keys.

## Changes from v3

| Change | Details |
| --- | --- |
| The reverse-mounted [splitkb Liatris](https://splitkb.com/products/liatris) (RP2040) replaces the [Adafruit KB2040](https://www.adafruit.com/product/5302) MCU | [Microcontroller](#microcontroller) |
| A TVS diode and series resistor protect the TRRS serial line from hot-unplug transients | [TRRS data-line protection](#trrs-data-line-protection) |
| Silkscreen credit text and component-identification labels are stamped on both halves | [Silkscreen text](#silkscreen-text) |

## Microcontroller

The reverse-mounted (facing the PCB) [splitkb Liatris](https://splitkb.com/products/liatris) (RP2040) replaces the [Adafruit KB2040](https://www.adafruit.com/product/5302) (RP2040). Its `USB_VBUS_PIN` (GP19) lets QMK detect USB connectivity via a dedicated GPIO instead of the `SPLIT_USB_DETECT` polling loop, removing the ~2-second unresponsive window at boot and improving reliability after KVM switches.

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

Remove the `SPLIT_USB_DETECT` comment block from `config.h`: it no longer applies since VBUS detection bypasses the polling loop entirely.

Update `keyboard.json`:

```json
"development_board": "liatris"
```

### Pinout

* [splitkb Liatris pinout](https://docs.splitkb.com/product-guides/liatris/pinout)
* [Custom Ergogen footprint: `mcu_liatris`](../../ergogen/footprints/mcu_liatris.js) - based on [ceoloide/mcu_nice_nano](../../ergogen/footprints/ceoloide/mcu_nice_nano.js) and [marbastlib KiCad footprint](https://github.com/ebastler/marbastlib), which was used as a reference for bottom pin placement

| Left | | | Right |
| --- | --- | --- | --- |
| P1 (GP0) | | | RAW |
| P0 (GP1) | | | GND |
| GND | | | RST |
| GND | | | VCC |
| P2 (GP2) | | | P21 (GP29) |
| P3 (GP3) | | | P20 (GP28) |
| P4 (GP4) | | | P19 (GP27/VBUS) |
| P5 (GP5) | | | P18 (GP26) |
| P6 (GP6) | | | P15 (GP22) |
| P7 (GP7) | | | P14 (GP20) |
| P8 (GP8) | | | P16 (GP23) |
| P9 (GP9) | | | P10 (GP21) |

## TRRS data-line protection

v4 adds a TVS diode and series resistor on the TRRS data line to protect the MCU's serial GPIO from hot-unplug transients. A bidirectional 3.3V TVS clamps the line to GND; a 100Ω resistor limits inrush into the MCU pin. Each half:

```text
TRRS Ring 2 --(DATA_RAW)--+-- 100Ω --(P0)-- MCU GP1
                          |
                         TVS (clamps to GND)
                          |
                         GND
```

The connector pinout also moved: GND on the sleeve, serial data on ring R2, VCC on the tip. The sleeve breaks last on withdrawal, so the halves keep a common ground throughout the disconnect, and the data line sits on an interior ring rather than the exposed tip.

Both changes are electrically transparent to firmware: same serial pin (GP1).

## Silkscreen text

Both halves are stamped with silkscreen text (front and back) via the `ceoloide/utility_text` footprint:

* **Credit**: `"Splinter" keyboard v4 by @andornaut` and the repo URL, in the top pinky-side margin. Center-justified so the reversible back copy mirrors onto the same on-board spot.
* **Component labels**: small tags ("Liatris", "TRRS", "TVS", "100R", "RESET", "M3x0.5") in the gaps next to each component. The right half re-anchors to the `mirror_` refs so placement stays symmetric.

## Hardware

### Bill of materials (BOM)

| Description | Quantity | Part |
| --- | --- | --- |
| Diodes | 62 | [1N4148W](https://www.lcsc.com/product-detail/C81598.html) (C81598, SOD-123 switching) |
| Hot swap sockets | 62 | [Adafruit 4958](https://www.digikey.ca/en/products/detail/adafruit-industries-llc/4958/13997772) (Kailh CPG151101S11 MX hotswap socket; DigiKey 1528-4958-ND, 20/pack) |
| Keycap set | 1 | [GMK Sixes keycaps](https://www.deskhero.ca/products/gmk-sixes) and [Ortho Kit](https://www.deskhero.ca/products/gmk-sixes?variant=39360309329986) |
| Key switches | 62 | [Cherry MX Ergo Clear](https://shockport.ca/collections/switches-1/products/cherry-mx-ergo-clear) ([developer information](https://www.cherrymx.de/en/dev.html)) |
| Microcontrollers | 2 | [splitkb Liatris](https://splitkb.com/products/liatris) (RP2040) |
| Resistors | 2 | [100Ω 0805 1%](https://www.lcsc.com/product-detail/C17408.html) (C17408, UNI-ROYAL 0805W8F1000T5E) |
| Screws | 2 | [M3x8mm screws](https://www.amazon.ca/1021Pcs-Stainless-Assortment-Machinery-Furniture/dp/B0B292QDWG) |
| Screws | 2 | [M3x10mm screws](https://www.amazon.ca/1021Pcs-Stainless-Assortment-Machinery-Furniture/dp/B0B292QDWG) |
| Silicon bumpers | 8 | [10x2mm Silicone Rubber Bumpers](https://www.aliexpress.com/item/1005005315398342.html) |
| Sockets (12-pin) | 4 | [Mill-Max 315-43-112-41-003000](https://www.mouser.ca/ProductDetail/575-3154311241003000) ([Series documentation](https://mm.digikey.com/Volume0/opasdata/d220001/medias/docus/2481/310%2C%20311%2C%20315%20Series%20%28in.%29.pdf)) |
| Socket pins | 48 | [Mill-Max 3320-0-00-15-00-00-03-0](https://www.mouser.ca/ProductDetail/575-3320000150000030) |
| Switches/buttons (reset) | 2 | [5.2mm SMD tact switch](https://www.lcsc.com/product-detail/C115351.html) (C115351, `SW_SKQG` footprint, see [Reset switch caveat](#reset-switch-caveat)) |
| Threaded inserts | 4 | [M3x5x4 threaded inserts](https://cnckitchen.store/products/made-for-voron-gewindeeinsatz-threaded-insert-m3x5x4-100-stk-pcs) |
| TRRS cables | 1 | [Monoprice Onyx TRRS Cable](https://www.monoprice.com/product?p_id=18632) |
| TRRS jacks | 2 | [HCTL HC-PJ-320A-4P-D](https://www.lcsc.com/product-detail/Audio-Connector-Headphone_HCTL-HC-PJ-320A-4P-D_C5372851.html) |
| TVS diodes | 2 | [SMF3.3CA](https://www.lcsc.com/product-detail/C782876.html) (C782876, SOD-123FL bidirectional 3.3V) |

JLCPCB assembles the four SMD parts with an LCSC link (diode, resistor, TVS, reset switch); everything else is sourced separately and hand-soldered or hand-assembled. Hand-soldering the hotswap sockets keeps the board eligible for JLCPCB's cheaper **Economic** PCBA service: the sockets are Standard-only and not stocked for JLC assembly, so leaving them on the assembly BOM would force the pricier Standard service. The MCU (Liatris), TRRS jack, and hotswap sockets are **Do-Not-Place** (hand-soldered); their LCSC/vendor links are for sourcing only.

The TVS is a generic `SMF3.3CA` (the Littelfuse part is not stocked on LCSC); C782876 is a Leiditech equivalent in the same SOD-123FL package (ZHIDE C2917876 is an LCSC alternative). Verify it is in stock before ordering and substitute any other in-stock `SMF3.3CA` if not.

#### Reset switch caveat

The reset switch must match the land pattern the design actually generates, not a specific catalog part. Ergogen's built-in `button` footprint emits the KiCad `SW_SKQG` land pattern (a 5.2×5.2mm SMD tact switch); C115351 drops onto those pads as-is.

If you substitute a different part, pick one whose pads match the `SW_SKQG` footprint, or change the footprint in the Ergogen config and regenerate the PCBs. Keep the reset-switch `lcsc` entry in [jlcpcb-parts.json](./kicad/jlcpcb-parts.json) in sync.

## Fabrication (JLCPCB)

`npm run fab-jlcpcb` exports everything JLCPCB needs from the routed masters `v4/kicad/routed/{left,right}.kicad_pcb` via `kicad-cli`, writing per-board output to `dist/v4/kicad/jlcpcb/<name>/`:

* **Gerbers + drill**: zipped per board; upload this to order the bare PCB.
* **BOM + CPL** (`<name>-BOM.csv`, `<name>-CPL.csv`): assembly files for JLCPCB PCBA, generated only when [jlcpcb-parts.json](./kicad/jlcpcb-parts.json) is present. With no parts file the script produces gerbers only.

### How parts are assigned

LCSC part numbers live in [jlcpcb-parts.json](./kicad/jlcpcb-parts.json), not in the `.kicad_pcb`, so they survive Ergogen regeneration of the boards. The file is keyed by **footprint name** (the `Package` column of the position file, since the generated footprints have empty `Value` fields). Each entry carries `lcsc`, `comment` (BOM Comment), `package` (BOM Footprint), and `rotation` (added to KiCad's angle to correct pick-and-place orientation). `scripts/gen-jlcpcb-bom-cpl.py` joins this against the position file:

* footprint **absent** from the JSON → Do-Not-Place (MCU, TRRS jack, mounting holes)
* footprint present with **empty `lcsc`** → error; nothing is written until you fill it in
* footprint present with **`lcsc` set** → placed in both the BOM (grouped by LCSC) and CPL (rotation-corrected)

The hotswap sockets are deliberately left off the assembly BOM and hand-soldered to keep the board on JLCPCB's cheaper Economic PCBA service (see the BOM note above).

### Ordering

1. Route `v4/kicad/{left,right}.kicad_pcb`, copy them to the routed masters with `npm run copy-pcbs-kicad-to-routed`, then run `npm run fab-jlcpcb`.
2. Upload the gerber zip (`dist/v4/kicad/jlcpcb/{left,right}/{left,right}-gerber.zip`) to order the bare PCB; upload the per-board BOM/CPL (`{left,right}-BOM.csv` and `{left,right}-CPL.csv` in the same `dist/v4/kicad/jlcpcb/<name>/` dirs) for PCBA.
3. Check the placement against JLCPCB's [DFM viewer](https://cart.jlcpcb.com/quote/gerberviewThree) (2D/3D, layers, DFM check) and adjust per-part `rotation` in [jlcpcb-parts.json](./kicad/jlcpcb-parts.json) if any part is mis-oriented, then re-run.
