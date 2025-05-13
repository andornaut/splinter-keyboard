# Splinter keyboard

A 62-key split columnar ergonomic keyboard

* [andornaut@github /til](https://github.com/andornaut/til/)
  * [3D Printing](https://github.com/andornaut/til/blob/master/docs/3d-printing.md)
  * [Electronics](https://github.com/andornaut/til/blob/master/docs/electronics.md)
  * [Keyboards](https://github.com/andornaut/til/blob/master/docs/keyboards.md)
* [Splinter qmk_firmware](https://github.com/andornaut/qmk_firmware/tree/splinter/keyboards/splinter)

## Versions

Version | Description | Layout
--- | --- | ---
[v1](./v1) | 61-keys. Asymetrical enclosures. Traditional layout. | [![v1](./v1/v1-300width.jpg)](./v1/v1.jpg)
[v2](./v2) | 62-keys. Symmetrical enclosures. Non-traditional placement of backspace and backslash keys. | [![v2](./v2/v2-300width.jpg)](./v2/v2.jpg)

## Installation

* [Ergogen](https://github.com/ergogen/ergogen)
  * [Footprints by ceoloide](https://github.com/ceoloide/ergogen-footprints)
  * [Footprints by infused-kim](https://github.com/infused-kim/kb_ergogen_fp)
  * [Footprints by sboysel](https://github.com/sboysel/ergogen/tree/develop/src/footprints)
  * [Helper scripts](https://github.com/infused-kim/kb_ergogen_helper)
* [KiCad](https://www.kicad.org)
  * [KiKit automation tools](https://github.com/yaqwsx/KiKit)
* [OrcaSlicer](https://github.com/SoftFever/OrcaSlicer)

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

# Update submodules
git submodule update --recursive --remote
```

Alternatively, you can install OrcaSlicer and Kicad using [these Ansible tasks](https://github.com/andornaut/ansible-ctrl/blob/master/roles/dev/tasks/hobbies.yml).

## Developing

1. Set the `VERSION` environment variable in [`.env`](./.env) to one of "v1" or "v2"
1. Prototype a keyboard layout using [Keyboard Layout Editor](http://www.keyboard-layout-editor.com/)
1. Convert the prototype to a production-ready design using [Ergogen](https://github.com/ergogen/ergogen)
1. Design the PCBs using [KiCad](https://www.kicad.org/)
    * Print the PCBs using [JLCPCB](https://jlcpcb.com/), [OSH Park](https://oshpark.com/), or [PCBWay](https://www.pcbway.com/)
1. Model a case using [OnShape](https://cad.onshape.com)
1. Print the case using [OrcaSlicer](https://github.com/SoftFever/OrcaSlicer)
1. Install the [custom QMK firmware](https://github.com/andornaut/qmk_firmware/tree/splinter/keyboards/splinter)

### Fix error when running `npm run build`

The `pcbnew` Python library, which is packaged with Kicad, may fail if it cannot find libTKBO, eg.:

```bash
$ python3
Python 3.12.3 (main, Apr 10 2024, 05:33:47) [GCC 13.2.0] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>> import pcbnew
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "/usr/lib/python3/dist-packages/pcbnew.py", line 12, in <module>
    import _pcbnew
ImportError: libTKBO.so.7: cannot open shared object file: No such file or directory
```

Workaround this issue by installing the missing library:

```bash
sudo apt install libocct-modeling-algorithms-7.6t64
```
