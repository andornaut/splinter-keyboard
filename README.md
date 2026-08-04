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
| [v4](./v4) | [splitkb Liatris](https://splitkb.com/products/liatris) (RP2040) | Added USB VBUS detection and TRRS data-line protection | [splinter](https://github.com/andornaut/qmk_firmware/tree/splinter/keyboards/splinter) | [![v4](./v4/v4-300width.jpg)](./v4/v4.jpg) |
| [v3](./v3) | [Adafruit KB2040](https://www.adafruit.com/product/5302) (RP2040) | Switched from AVR to RP2040 | [splinter-v3.0](https://github.com/andornaut/qmk_firmware/tree/splinter-3.0/keyboards/splinter) | [![v3](./v3/v3-300width.jpg)](./v3/v3.jpg) |
| [v2](./v2) | [SparkFun Pro Micro](https://www.sparkfun.com/products/15795) (ATmega32U4) | Symmetrical enclosures; added a key (62 keys) | [splinter-v2.0](https://github.com/andornaut/qmk_firmware/tree/splinter-2.0/keyboards/splinter) | [![v2](./v2/v2-300width.jpg)](./v2/v2.jpg) |
| [v1](./v1) | [SparkFun Pro Micro](https://www.sparkfun.com/products/15795) (ATmega32U4) | Initial version: 61 keys, columnar layout, asymmetrical enclosures | [splinter-v1.0](https://github.com/andornaut/qmk_firmware/tree/splinter-1.0/keyboards/splinter) | [![v1](./v1/v1-300width.jpg)](./v1/v1.jpg) |

## Installation

Install the following tools:

* [KiCad 10](https://www.kicad.org)
* [Node.js](https://nodejs.org)
* [OrcaSlicer](https://github.com/SoftFever/OrcaSlicer)
* [Python 3](https://www.python.org)
* [Freerouting](https://github.com/freerouting/freerouting) (Optional, for `npm run route`. See [Autorouting](#autorouting-optional).)
* [KiKit](https://github.com/yaqwsx/KiKit) (Optional, for `npm run panelize`; needs the git-master build. See [Panelization](#panelization-optional-for-pcba-cost).)

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

`npm run ergogen` uses the vendored footprint submodules (`ceoloide`, `infused-kim`) at their pinned revision and does not advance them, so builds stay reproducible. To pull the latest upstream footprints and re-pin them:

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

![Ergogen preview](./v4/ergogen/ergogen.png)

1. Run `docker compose up` to start the Ergogen GUI (it builds automatically), then open <http://ergogen.internal> (needs [docker_etc_hosts](https://github.com/andornaut/docker_etc_hosts) for the `/etc/hosts` entry).
1. Paste in, edit, then download [`ergogen/config.yaml`](./v4/ergogen/config.yaml).
1. Run `npm run ergogen` to generate outlines and PCBs into `dist/v4/ergogen/`, then `npm run copy:dist-to-unrouted`. Or use `npm run watch` / `npm run watch:sync-unrouted`.

**Notes:**

* The GUI prototypes placement and outlines but renders no PCBs, and is client-side only: edit there, copy back to `config.yaml` (the source of truth), and build with `npm run ergogen`.
* The browser can't load footprints from disk, so the [`Dockerfile`](./Dockerfile) bakes this repo's [custom footprints](./ergogen/footprints/) into the GUI image on top of `ceoloide` and `infused-kim`; an unregistered `what:` shows up as unknown. After adding one, `docker compose build --no-cache`.

### Step 4. [KiCad](https://www.kicad.org/)

![KiCad preview](./v4/kicad/kicad.png)

1. `npm run copy:dist-to-unrouted` copies Ergogen's boards into [`kicad/unrouted/`](./v4/kicad/unrouted/) (backing up the old ones to gitignored `kicad/backups/`); open one in KiCad, e.g. [`left.kicad_pcb`](./v4/kicad/unrouted/left.kicad_pcb).
   * v4 carries [copper keepout zones](./v4/README.md#copper-keepout-zones) that flag stray copper near the board edge or screw bosses.
1. Route the boards in [`kicad/unrouted/`](./v4/kicad/unrouted/), then before saving:
   * **Add Teardrops** (Edit > Edit Teardrops, nothing selected for board-wide): stronger pad/via joints. Re-run after any reroute.
   * **Run DRC** (Inspect > Design Rules Checker, "Refill all zones" checked): clear every violation and unrouted net. `npm run fab` re-runs it headlessly and refuses to emit gerbers if it fails, but fixing it here beats reading the JSON.
   * **Check copper/silk** visually: no isolated GND islands or stranded pads; silk and reference designators clear of pads and the board edge.

   Then `npm run copy:unrouted-to-routed` to save them to [`kicad/routed/`](./v4/kicad/routed/), which adds the GND pour and strips the copper no route uses (dangling tracks and the vias they strand, tracks buried in pads, redundant vias, split segments). The working boards keep that copper, mainly the footprints' unused `include_traces_vias` stubs, since a later reroute may pick it up.

   It then tidies away any segment left shorter than it is wide: the few-micron jog or via stub a drag leaves behind. Collapsing one moves an endpoint along the sliver, over ground that sliver's own copper already covered, and is capped at 0.2mm. Anything needing more is reported as an error naming its net, layer and position, and the step stops rather than shipping copper nobody chose. Close those by dragging the two runs together in KiCad, or re-run `python3 ./scripts/tidy-slivers.py v4/kicad/routed/*.kicad_pcb --max-move <mm>` by hand (then re-run DRC). Builds always use the default cap.
   * After regenerating with Ergogen, `npm run copy:traces-to-unrouted` copies the traces and teardrops from `routed/` back into `unrouted/` (then File > Revert in KiCad).

#### Autorouting (optional)

KiCad has no built-in autorouter. `npm run route` routes the [`kicad/unrouted/`](./v4/kicad/unrouted/) boards in place via [Freerouting](https://github.com/freerouting/freerouting), leaving `routed/` untouched; expect to hand-clean the result, then File > Revert to load it. Raising via cost trades vias for *unrouted nets*, so it can't beat hand-routing on via count.

| Env var | Default |
| --- | --- |
| `FREEROUTING_PASSES` | 100 |
| `FREEROUTING_STRATEGY` | greedy |
| `FREEROUTING_SELECTION` | prioritized |
| `FREEROUTING_VIA_COST` | 50 |
| `FREEROUTING_UNDESIRED_DIR_COST` | unset |
| `FREEROUTING_LOG_LEVEL` | WARN |

### One-command pipeline

`npm run pipeline` re-syncs already-routed boards after a config change, running `ergogen`, `copy:dist-to-unrouted`, `copy:traces-to-unrouted`, `copy:unrouted-to-routed`, `validate:provenance`, `validate:firmware`, `fab`, `validate:fab`, then `panelize`. Every step is a hard gate except `panelize`, which is skipped when [KiKit](#panelization-optional-for-pcba-cost) is absent.

**It requires existing routed masters in [`kicad/routed/`](./v4/kicad/routed/)** (it copies their traces onto the freshly generated boards, and aborts if a master has no human routing) and it does not route for you: for a first route, or when geometry moves enough that the old traces no longer fit, route by hand in KiCad (Step 4).

`validate:firmware` (step 6) reads the QMK `keyboard.json` named by `config.FIRMWARE` in [package.json](./package.json), a path to a sibling `qmk_firmware` checkout, so it checks what you are about to flash rather than what is pushed. Without that checkout the step fails and no gerbers are produced; use `npm run validate:firmware -- --firmware <raw.githubusercontent.com URL>` or `$SPLINTER_FIRMWARE_JSON` instead.

### Provenance stamp (keeping routed/ in sync with config.yaml)

The `cp` steps and manual routing let `routed/` drift from `config.yaml`, so you could fab a stale board. `npm run ergogen` stamps each board with a hash of `config.yaml`; `npm run fab` refuses a drifted or unstamped master, and `npm run validate:provenance` checks without fabbing. Clear a mismatch by re-running the pipeline (re-routing if needed).

Only `config.yaml` is hashed, so a footprint `.js` or Ergogen-version change can move geometry without tripping the check, while a comment-only config edit trips a false "stale".

### Step 5. Fabrication (JLCPCB)

With the boards saved to `routed/` (Step 4), `npm run fab` exports from [`kicad/routed/`](./v4/kicad/routed/) into `dist/v4/kicad/jlcpcb/<name>/`:

* **Gerbers + drill** (`<name>-gerber.zip`): the bare PCB.
* **BOM + CPL** (`<name>-BOM.csv`, `<name>-CPL.csv`): JLCPCB PCBA assembly files, generated only when [`kicad/jlcpcb-parts.json`](./v4/kicad/jlcpcb-parts.json) is present.
* **DRC report** (`<name>-drc.json`): a headless DRC gate runs first and aborts the whole fab (no gerbers written) on any error-level violation or unrouted net.

Then `npm run validate:fab` (step 8 of the pipeline) audits those outputs for what DRC and provenance miss: a board-spanning GND plane on both the master and the gerbers, a complete gerber set, and every assembled part present in the BOM/CPL.

LCSC part numbers live in [`kicad/jlcpcb-parts.json`](./v4/kicad/jlcpcb-parts.json), kept out of the `.kicad_pcb` so they survive Ergogen regen. Which parts JLCPCB places vs. which you hand-solder is version-specific; see the [version README](./v4/README.md#fabrication-jlcpcb).

**Ordering** from [JLCPCB](https://jlcpcb.com/): upload each `<name>-gerber.zip`, plus the matching `<name>-BOM.csv` / `<name>-CPL.csv` for assembly. Check placement in the [DFM viewer](https://cart.jlcpcb.com/quote/gerberviewThree); fix a mis-oriented part via its `rotation` in the JSON and re-run.

#### Panelization (optional, for PCBA cost)

`npm run panelize` combines `left` + `right` into one panel so JLCPCB's per-order assembly setup and stencil fees are paid once instead of twice: worth it for PCBA orders, skip it for bare boards. Outputs gerbers + BOM/CPL to `dist/v4/kicad/jlcpcb/panel/`; the per-half `fab` remains the strict DRC gate. Requires [KiKit](https://github.com/yaqwsx/KiKit) (git-master build for KiCad 10); point `panelize.sh` at its interpreter with `KIKIT_PYTHON`.

### Step 6. [Onshape](https://cad.onshape.com)

![Onshape preview](./v4/onshape/onshape.png)

1. In [Onshape](https://cad.onshape.com), create a document and start a sketch.
1. Select "Insert a DXF or DWG file" > "Import ..." (bottom of the dialog) > `dist/v4/ergogen/outlines/full.dxf`.
1. Design the case, then export `*.step` files to [`onshape/`](./v4/onshape/).

### Step 7. [OrcaSlicer](https://github.com/SoftFever/OrcaSlicer)

1. Open or create an OrcaSlicer project.
1. Import the `*.step` files from [`onshape/`](./v4/onshape/).
1. Slice and print the case.
1. Install an [M2.5 heat-set insert](https://cnckitchen.store/products/gewindeeinsatz-threaded-insert-m2-5-standard-100-stk-pcs) (CNC Kitchen) into each mounting boss with a soldering iron, then clamp the PCB with the [M2.5 screws](./v4/README.md#bill-of-materials-bom).

#### Alternative: machined aluminium case (JLCCNC)

Instead of 3D printing, the case can be CNC-machined in aluminium via [JLCCNC](https://jlccnc.com). Upload each half's `*.step` (left and right are separate mirrored parts, so set quantity per file) and set:

* **Material:** 6061 aluminium (JLCCNC's standard alloy).
* **Surface finish:** bead blasting + matte anodizing; drop the bead blasting for a glossier sheen. Black is the safe color.
* **Tolerance:** the default (ISO 2768 medium).
* **Threaded holes:** tap the M2.5 holes directly (the heat-set inserts in the [BOM](./v4/README.md#bill-of-materials-bom) are for the printed case only). A STEP can't carry threads, so model each hole at the ~2.05mm tap-drill diameter and upload a PDF with an `M2.5x0.45` callout and depth. Since every hole shares one spec, a note reading "All mounting holes: M2.5x0.45 tapped, N mm deep" is enough; in Onshape, a Drawing of the half with a hole/thread callout (right-click the hole edge > Callout) emits it.

### Step 8. [QMK Firmware](https://qmk.fm/)

1. Install the [custom QMK firmware](https://github.com/andornaut/qmk_firmware/tree/splinter/keyboards/splinter)
