# Splinter keyboard

A 62-key split columnar ergonomic keyboard.

This repo holds the hardware design files. The design pipeline is: Keyboard Layout Editor -> Ergogen -> KiCad -> OnShape -> OrcaSlicer -> QMK firmware (see [Developing](#developing)).

* [QMK firmware](https://github.com/andornaut/qmk_firmware/tree/splinter/keyboards/splinter)
* [andornaut@github /til](https://github.com/andornaut/til/)
  * [3D Printing](https://github.com/andornaut/til/blob/master/docs/3d-printing.md)
  * [Electronics](https://github.com/andornaut/til/blob/master/docs/electronics.md)
  * [Keyboards](https://github.com/andornaut/til/blob/master/docs/keyboards.md)

## Versions

| Version | Keys | MCU | Features | Firmware | Photo |
| --- | --- | --- | --- | --- | --- |
| [v4](./v4) | 62 | [splitkb Liatris](https://splitkb.com/products/liatris) (RP2040) | Symmetrical enclosures, USB VBUS detection, TRRS data-line protection | [splinter](https://github.com/andornaut/qmk_firmware/tree/splinter/keyboards/splinter) | [![v4](./v4/v4-300width.jpg)](./v4/v4.jpg) |
| [v3](./v3) | 62 | [Adafruit KB2040](https://www.adafruit.com/product/5302) (RP2040) | Symmetrical enclosures | [splinter-v3.0](https://github.com/andornaut/qmk_firmware/tree/splinter-3.0/keyboards/splinter) | [![v3](./v3/v3-300width.jpg)](./v3/v3.jpg) |
| [v2](./v2) | 62 | [SparkFun Pro Micro](https://www.sparkfun.com/products/15795) (ATmega32U4) | Symmetrical enclosures | [splinter-v2.0](https://github.com/andornaut/qmk_firmware/tree/splinter-2.0/keyboards/splinter) | [![v2](./v2/v2-300width.jpg)](./v2/v2.jpg) |
| [v1](./v1) | 61 | [SparkFun Pro Micro](https://www.sparkfun.com/products/15795) (ATmega32U4) | Asymmetrical enclosures, traditional layout | [splinter-v1.0](https://github.com/andornaut/qmk_firmware/tree/splinter-1.0/keyboards/splinter) | [![v1](./v1/v1-300width.jpg)](./v1/v1.jpg) |

## Installation

Install the following tools:

* [Ergogen](https://github.com/ergogen/ergogen) - PCB generation from YAML config
  * [Footprints by ceoloide](https://github.com/ceoloide/ergogen-footprints)
  * [Helper scripts](https://github.com/infused-kim/kb_ergogen_helper)
* [KiCad](https://www.kicad.org) - PCB editor
  * [KiKit automation tools](https://github.com/yaqwsx/KiKit) - Gerber file generation
* [OrcaSlicer](https://github.com/SoftFever/OrcaSlicer) - 3D printing slicer
* [Freerouting](https://github.com/freerouting/freerouting) (optional) - PCB autorouter; KiCad has no built-in autorouter

```bash
# Include submodules when cloning
git clone --recursive git@github.com:andornaut/splinter-keyboard.git
cd splinter-keyboard

# Install dependencies, including Ergogen
nvm use
npm install

# Install KiCad
sudo add-apt-repository ppa:kicad/kicad-8.0-releases
sudo apt install kicad

# Install KiKit
# Must use the same Python interpreter as KiCad (will not work in a venv)
sudo pip install kikit --break-system-packages

# Check out the pinned submodule revisions
git submodule update --init --recursive
```

Alternatively, you can install OrcaSlicer, KiCad, and Freerouting using [these Ansible tasks](https://github.com/andornaut/ansible-ctrl/blob/master/roles/hobbies/tasks/main.yml) (tags `orcaslicer`, `kicad`, `freerouting`).

### Updating footprint submodules

`npm run build` uses the vendored footprint submodules (`ceoloide`, `infused-kim`) at their pinned, checked-out revision -- it does not advance them, so builds stay reproducible. To intentionally pull the latest upstream footprints and re-pin them:

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

1. Prototype a keyboard layout using [Keyboard Layout Editor](http://www.keyboard-layout-editor.com/)
1. Export the layout configuration to [`keyboard-layout-editor/keyboard-layout-editor.json`](./v4/keyboard-layout-editor/keyboard-layout-editor.json), so that you can import it and iterate on it in the future
1. Use the prototype as inspiration for creating a production-ready design using Ergogen

### Step 3. [Ergogen](https://github.com/ergogen/ergogen)

* [Online version of Ergogen that includes ceoloide's footprints](https://ergogen.ceoloide.com/)

![Ergogen preview](./v4/ergogen/ergogen.png)

1. Run `docker compose up` to start Ergogen GUI (it builds automatically)
1. Open <http://ergogen.internal> (install [docker_etc_hosts](https://github.com/andornaut/docker_etc_hosts) to manage `/etc/hosts` entries)
1. Paste in, work on, and then download and save [`ergogen/config.yaml`](./v4/ergogen/config.yaml)
1. Run `npm run build` to generate and save outlines and pcbs to `dist/v4/ergogen/` then `npm run copy-pcbs-dist-to-kicad`
    * Alternatively, run `npm run watch` or `npm run watch-and-copy-pcbs-to-kicad`

**Notes:**

* The GUI prototypes key placement, layout, and outlines but does not render PCBs. It is client-side only: no host filesystem access, no sync. Edit there, then copy the result back to `config.yaml` (the source of truth). Use `npm run build` for full builds and PCB generation.
* Custom footprints are baked into the GUI image via the [`Dockerfile`](./Dockerfile) (the browser can't load them from disk). It registers this repo's footprints (`mcu_liatris`, `sod-123fl`, `sod-123w`) on top of the upstream `ceoloide` and `infused-kim` libraries. Any custom `what:` not registered there reports as unknown; rebuild with `docker compose build --no-cache` after adding one.

### Step 4. [KiCad](https://www.kicad.org/)

![KiCad preview](./v4/kicad/kicad.png)

1. Design the PCBs using [KiCad](https://www.kicad.org/)
1. Run `npm run copy-pcbs-dist-to-kicad` to copy Ergogen's `dist/v4/ergogen/pcbs/*.kicad_pcb` to [`kicad/`](./v4/kicad/) (existing boards are backed up to gitignored `kicad/backups/<name>-<timestamp>.kicad_pcb` first).
1. Run `open ./v4/kicad/left.kicad_pcb`
1. Route the PCBs in [`kicad/`](./v4/kicad/), and then save them to [`kicad/routed/`](./v4/kicad/routed/)
   * KiCad has no built-in autorouter. Run `npm run autoroute` to route the working `kicad/*.kicad_pcb` boards in place with [Freerouting](https://github.com/freerouting/freerouting) (DSN export -> headless route -> SES import). Intermediate files go to `dist/v4/kicad/freerouting/`; it never writes to `kicad/routed/`. Expect to hand-clean the result (the matrix is usually nicer hand-routed), then File > Revert to load it. Tune with the env vars below; defaults favour a fully-connected, DRC-clean board. Raising via cost trades vias for *unrouted nets*, not a low-via topology, so it can't beat hand-routing for via count.

     | Env var | Default |
     | --- | --- |
     | `FREEROUTING_PASSES` | 100 |
     | `FREEROUTING_STRATEGY` | greedy |
     | `FREEROUTING_SELECTION` | prioritized |
     | `FREEROUTING_VIA_COST` | 50 |
     | `FREEROUTING_UNDESIRED_DIR_COST` | unset |
     | `FREEROUTING_LOG_LEVEL` | WARN |

   * Once you're happy with the routing, run `npm run copy-pcbs-kicad-to-routed` to copy the PCBs to [`kicad/routed/`](./v4/kicad/routed/)
   * If you've generated new PCB files using Ergogen, then you can run `npm run copy-traces-routed-to-kicad` to copy traces from the PCBs in [`kicad/routed/`](./v4/kicad/routed/) back to those of the same name in [`kicad/`](./v4/kicad/). Select File > Revert > Yes to refresh the PCB in KiCad.
1. Run `npm run copy-pcbs-kicad-to-routed && npm run fab-jlcpcb` to generate and save gerber and drill files to `dist/v4/kicad/jlcpcb/*.zip`
1. Print the PCBs using [JLCPCB](https://jlcpcb.com/) (or [OSH Park](https://oshpark.com/) or [PCBWay](https://www.pcbway.com/))
   * Submit the `dist/v4/kicad/jlcpcb/*.zip` files to [JLCPCB](https://jlcpcb.com/)

### Step 5. [OnShape](https://cad.onshape.com)

![OnShape preview](./v4/onshape/onshape.png)

1. Model the case using [OnShape](https://cad.onshape.com)
1. Create a new document
1. Start a new sketch
1. Select "Insert a DXF or DWG file" > "Import ..." (at the bottom of the dialog) > Select `dist/v4/ergogen/outlines/full.dxf`
1. Design a keyboard case
1. Export `*.step` files to [`onshape/`](./v4/onshape/)

### Step 6. [OrcaSlicer](https://github.com/SoftFever/OrcaSlicer)

1. Print the case using [OrcaSlicer](https://github.com/SoftFever/OrcaSlicer)
1. Open or create an OrcaSlicer project file
1. Import `*.step` files from [`onshape/`](./v4/onshape/)
1. Print the keyboard case

### Step 7. [QMK Firmware](https://qmk.fm/)

1. Install the [custom QMK firmware](https://github.com/andornaut/qmk_firmware/tree/splinter/keyboards/splinter)
