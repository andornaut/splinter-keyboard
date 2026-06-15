# Splinter keyboard

A 62-key split columnar ergonomic keyboard.

This repo holds the hardware design files. The design pipeline is: Keyboard Layout Editor -> Ergogen -> KiCad -> Fabrication -> Onshape -> OrcaSlicer -> QMK firmware (see [Developing](#developing)).

* [QMK firmware](https://github.com/andornaut/qmk_firmware/tree/splinter/keyboards/splinter)
* [andornaut@github /til](https://github.com/andornaut/til/)
  * [3D Printing](https://github.com/andornaut/til/blob/master/docs/3d-printing.md)
  * [Electronics](https://github.com/andornaut/til/blob/master/docs/electronics.md)
  * [Keyboards](https://github.com/andornaut/til/blob/master/docs/keyboards.md)

## Versions

| Version | MCU | Changes from previous | Firmware | Photo |
| --- | --- | --- | --- | --- |
| [v4](./v4) | [splitkb Liatris](https://splitkb.com/products/liatris) (RP2040) | New MCU; added USB VBUS detection and TRRS data-line protection | [splinter](https://github.com/andornaut/qmk_firmware/tree/splinter/keyboards/splinter) | [![v4](./v4/v4-300width.jpg)](./v4/v4.jpg) |
| [v3](./v3) | [Adafruit KB2040](https://www.adafruit.com/product/5302) (RP2040) | New MCU; switched from AVR to RP2040 | [splinter-v3.0](https://github.com/andornaut/qmk_firmware/tree/splinter-3.0/keyboards/splinter) | [![v3](./v3/v3-300width.jpg)](./v3/v3.jpg) |
| [v2](./v2) | [SparkFun Pro Micro](https://www.sparkfun.com/products/15795) (ATmega32U4) | Switched to columnar layout and symmetrical enclosures; 62 keys | [splinter-v2.0](https://github.com/andornaut/qmk_firmware/tree/splinter-2.0/keyboards/splinter) | [![v2](./v2/v2-300width.jpg)](./v2/v2.jpg) |
| [v1](./v1) | [SparkFun Pro Micro](https://www.sparkfun.com/products/15795) (ATmega32U4) | Initial version: 61 keys, asymmetrical enclosures, traditional staggered layout | [splinter-v1.0](https://github.com/andornaut/qmk_firmware/tree/splinter-1.0/keyboards/splinter) | [![v1](./v1/v1-300width.jpg)](./v1/v1.jpg) |

## Installation

Install the following tools:

* [KiCad 10](https://www.kicad.org)
* [Node.js](https://nodejs.org) via [nvm](https://github.com/nvm-sh/nvm)
* [OrcaSlicer](https://github.com/SoftFever/OrcaSlicer) - 3D printing slicer
* [Python 3](https://www.python.org)
* [Freerouting](https://github.com/freerouting/freerouting) (optional)

```bash
# Include submodules when cloning
git clone --recursive git@github.com:andornaut/splinter-keyboard.git
cd splinter-keyboard

# Install the Node version from .nvmrc, then the deps (including Ergogen)
nvm install
npm install

# Install KiCad 10 (provides kicad-cli, used for fab file generation)
# Or use the Ansible task: https://github.com/andornaut/ansible-ctrl/blob/main/roles/hobbies/tasks/electronics.yml
sudo add-apt-repository ppa:kicad/kicad-10.0-releases
sudo apt install kicad

# Fallback only if you cloned without --recursive: fetch the submodules
git submodule update --init --recursive
```

Alternatively, you can install OrcaSlicer, KiCad, and Freerouting using [these Ansible tasks](https://github.com/andornaut/ansible-ctrl/blob/main/roles/hobbies/tasks/main.yml) (tags `orcaslicer`, `kicad`, `freerouting`).

### Updating footprint submodules

`npm run build` uses the vendored footprint submodules (`ceoloide`, `infused-kim`) at their pinned revision and does not advance them, so builds stay reproducible. To pull the latest upstream footprints and re-pin them:

```bash
git submodule update --remote ergogen/footprints/ceoloide ergogen/footprints/infused-kim
git add ergogen/footprints/ceoloide ergogen/footprints/infused-kim
git commit -m "Bump footprint submodules"
```

## Developing

### Step 1. Configure the environment

Set the active version in [`package.json`](./package.json) under `config.VERSION` to one of v1, v2, v3, or v4, either by editing the file or with `npm pkg set config.VERSION=v3`.

### Step 2. [Keyboard Layout Editor](http://www.keyboard-layout-editor.com/)

![Keyboard Layout preview](./v4/keyboard-layout-editor/keyboard-layout-editor.png)

1. Prototype a layout in [Keyboard Layout Editor](http://www.keyboard-layout-editor.com/).
1. Export it to [`keyboard-layout-editor/keyboard-layout-editor.json`](./v4/keyboard-layout-editor/keyboard-layout-editor.json) so you can re-import and iterate later.
1. Use it as the basis for the production Ergogen design.

### Step 3. [Ergogen](https://github.com/ergogen/ergogen)

* [Online version of Ergogen that includes ceoloide's footprints](https://ergogen.ceoloide.com/)

![Ergogen preview](./v4/ergogen/ergogen.png)

1. Run `docker compose up` to start the Ergogen GUI (it builds automatically), then open <http://ergogen.internal> (needs [docker_etc_hosts](https://github.com/andornaut/docker_etc_hosts) for the `/etc/hosts` entry).
1. Paste in, edit, then download [`ergogen/config.yaml`](./v4/ergogen/config.yaml).
1. Run `npm run build` to generate outlines and PCBs into `dist/v4/ergogen/`, then `npm run copy-pcbs-dist-to-unrouted`. Or use `npm run watch` / `npm run watch-and-copy-pcbs-to-unrouted`.

**Notes:**

* The GUI prototypes key placement, layout, and outlines but does not render PCBs. It runs client-side only (no filesystem access, no sync), so edit there and copy back to `config.yaml`, the source of truth. Use `npm run build` for full builds and PCB generation.
* Custom footprints are baked into the GUI image via the [`Dockerfile`](./Dockerfile) since the browser can't load them from disk. It registers this repo's footprints (`mcu_liatris`, `sod-123fl`, `sod-123w`) on top of the upstream `ceoloide` and `infused-kim` libraries; any unregistered `what:` shows up as unknown. After adding one, rebuild with `docker compose build --no-cache`.

### Step 4. [KiCad](https://www.kicad.org/)

![KiCad preview](./v4/kicad/kicad.png)

1. Copy Ergogen's generated boards into [`kicad/unrouted/`](./v4/kicad/unrouted/) with `npm run copy-pcbs-dist-to-unrouted` (existing boards are first backed up to gitignored `kicad/backups/<name>-<timestamp>.kicad_pcb`), then open one in KiCad, e.g. [`left.kicad_pcb`](./v4/kicad/unrouted/left.kicad_pcb).
1. Route the boards in [`kicad/unrouted/`](./v4/kicad/unrouted/). Once routing is done, clean each board up before saving:
   * **Cleanup Tracks & Vias** (Tools > Cleanup Tracks & Vias): enable all options to merge collinear segments, delete redundant/dangling tracks and vias, and remove tracks inside pads.
   * **Add Teardrops** (Edit > Edit Teardrops, with nothing selected to apply board-wide): smooths track-to-pad/via junctions for stronger joints and better DFM. Re-run after any reroute.
   * **Run DRC** (Inspect > Design Rules Checker) with "Refill all zones before performing DRC" checked: resolve every violation and confirm there are no unrouted nets. `npm run fab-jlcpcb` re-runs this same check headlessly and refuses to emit gerbers if it fails (see [Step 5](#step-5-fabrication-jlcpcb)), but fixing violations interactively in KiCad is far easier than reading the JSON report.
   * **Check copper/silk** visually: confirm the GND zone has no isolated islands or stranded pads, and that silkscreen text and reference designators clear pads and the board edge.

   Then `npm run copy-pcbs-unrouted-to-routed` to save them to [`kicad/routed/`](./v4/kicad/routed/).
   * KiCad has no built-in autorouter. `npm run autoroute` routes the [`kicad/unrouted/`](./v4/kicad/unrouted/) `*.kicad_pcb` boards in place via [Freerouting](https://github.com/freerouting/freerouting) (DSN export -> headless route -> SES import); intermediate files go to `dist/v4/kicad/freerouting/`, never `kicad/routed/`. Expect to hand-clean the result (the matrix routes nicer by hand), then File > Revert to load it. Defaults below aim for a fully-connected, DRC-clean board; raising via cost trades vias for *unrouted nets*, so it can't beat hand-routing on via count.

     | Env var | Default |
     | --- | --- |
     | `FREEROUTING_PASSES` | 100 |
     | `FREEROUTING_STRATEGY` | greedy |
     | `FREEROUTING_SELECTION` | prioritized |
     | `FREEROUTING_VIA_COST` | 50 |
     | `FREEROUTING_UNDESIRED_DIR_COST` | unset |
     | `FREEROUTING_LOG_LEVEL` | WARN |

   * After regenerating boards with Ergogen, `npm run copy-traces-routed-to-unrouted` copies traces from [`kicad/routed/`](./v4/kicad/routed/) back into the same-named boards in [`kicad/unrouted/`](./v4/kicad/unrouted/) (then File > Revert in KiCad).

### Step 5. Fabrication (JLCPCB)

With the boards saved to `routed/` (Step 4), `npm run fab-jlcpcb` exports everything a fab house needs from the routed masters [`v4/kicad/routed/`](./v4/kicad/routed/) into `dist/v4/kicad/jlcpcb/<name>/`:

* **Gerbers + drill** (`<name>-gerber.zip`): upload to order the bare PCB.
* **BOM + CPL** (`<name>-BOM.csv`, `<name>-CPL.csv`): assembly files for JLCPCB PCBA, generated only when [`v4/kicad/jlcpcb-parts.json`](./v4/kicad/jlcpcb-parts.json) is present; without it the script produces gerbers only.
* **DRC report** (`<name>-drc.json`): before exporting each board, `fab-jlcpcb` runs a headless DRC gate (`kicad-cli pcb drc --refill-zones --severity-error --exit-code-violations`) on the routed master and aborts the whole fab (no gerbers written) if any error-level violation or unrouted net remains, so a board that isn't fully routed and clean never reaches a gerber. `--refill-zones` is in-memory only, so the master is untouched. The report is written whether the gate passes or fails. No schematic-parity check: the Ergogen boards have no `.kicad_sch`.

**How parts are assigned (PCBA).** LCSC part numbers live in [`v4/kicad/jlcpcb-parts.json`](./v4/kicad/jlcpcb-parts.json), not in the `.kicad_pcb`, so they survive when Ergogen regenerates the boards. The file is keyed by **footprint name** (the `Package` column of the position file), because the generated footprints have empty `Value` fields, which rules out value-based keying. Each entry has `lcsc`, `comment` (BOM Comment), `package` (BOM Footprint), and `rotation` (added to KiCad's angle to fix pick-and-place orientation). [`scripts/gen-jlcpcb-bom-cpl.py`](./scripts/gen-jlcpcb-bom-cpl.py) joins this against the position file:

* footprint **absent** from the JSON -> Do-Not-Place (hand-soldered or hand-assembled)
* footprint present with **empty `lcsc`** -> error; nothing is written until you fill it in
* footprint present with **`lcsc` set** -> placed in both the BOM (grouped by LCSC) and CPL (rotation-corrected)

Keep a part off the assembly BOM (mark it Do-Not-Place) when assembling it would raise the order cost: JLCPCB's cheaper **Economic** PCBA service only places parts JLC stocks for it, so a part that is Standard-only or out of stock forces the whole order onto the pricier **Standard** service. Hand-solder those instead.

**Ordering** from [JLCPCB](https://jlcpcb.com/) (or [OSH Park](https://oshpark.com/), [PCBWay](https://www.pcbway.com/)):

1. Bare boards: submit each `<name>-gerber.zip`.
1. Assembly (PCBA): also upload the matching `<name>-BOM.csv` and `<name>-CPL.csv`; verify every LCSC part in [`v4/kicad/jlcpcb-parts.json`](./v4/kicad/jlcpcb-parts.json) is in stock first.
1. Check placement in JLCPCB's [DFM viewer](https://cart.jlcpcb.com/quote/gerberviewThree). If a part is mis-oriented, adjust its `rotation` in [`v4/kicad/jlcpcb-parts.json`](./v4/kicad/jlcpcb-parts.json) and re-run.

Which components are placed vs. hand-soldered, and their sourcing, are version-specific; see the version README (e.g. [v4](./v4/README.md#fabrication-jlcpcb)).

### Step 6. [Onshape](https://cad.onshape.com)

![Onshape preview](./v4/onshape/onshape.png)

1. In [Onshape](https://cad.onshape.com), create a document and start a sketch.
1. Select "Insert a DXF or DWG file" > "Import ..." (bottom of the dialog) > `dist/v4/ergogen/outlines/full.dxf`.
1. Design the case, then export `*.step` files to [`onshape/`](./v4/onshape/).

### Step 7. [OrcaSlicer](https://github.com/SoftFever/OrcaSlicer)

1. Open or create an OrcaSlicer project.
1. Import the `*.step` files from [`onshape/`](./v4/onshape/).
1. Slice and print the case.

### Step 8. [QMK Firmware](https://qmk.fm/)

1. Install the [custom QMK firmware](https://github.com/andornaut/qmk_firmware/tree/splinter/keyboards/splinter)
