#!/usr/bin/env python3
"""Combine the routed boards into one JLCPCB panel with KiKit.

Lays the input boards out in a single left-to-right row inside a frame, joins
each board to the frame with mouse-bite tabs, and adds corner fiducials and
tooling holes for assembly. Each board's references and nets are prefixed with
the board's file stem (e.g. left_D1, right_D1) so the two mirrored halves stay
unique in the position file / CPL. The panel is re-stamped with the provenance
string (see provenance.py) when --version and --config are given.

Unlike the other scripts/*.py helpers this one is NOT stdlib-only: it needs KiKit
(kikit.panelize) plus the KiCad pcbnew bindings. KiCad 10 support is only in
KiKit/pcbnewTransition git master (no PyPI release yet), so panelize.sh runs this
under a dedicated venv. inheritDrc=False is required: KiKit cannot merge the two
boards' net-class/DRC rules and aborts on save otherwise.

Usage: panelize.py <board.kicad_pcb> [more ...] --output panel.kicad_pcb \
         [--version v4 --config v4/ergogen/config.yaml] [tuning flags]
"""
import argparse
import os
import sys

import pcbnew
from kikit.panelize import Panel, Origin
from kikit.units import mm

from provenance import build_stamp, write_stamp


def stem(path):
    return os.path.splitext(os.path.basename(path))[0]


def build(boards, output, rail, gap, frame_space, tabs, tab_width,
          mb_diameter, mb_spacing, tab_min_distance):
    panel = Panel(output)

    # Lay the boards out in one row, each placed by its top-left corner, with a
    # gap between neighbours. Prefix refs/nets per board so the mirrored halves
    # do not collide in the pos file / CPL.
    x = 0
    for f in boards:
        pre = stem(f)
        # appendBoard returns the placed board's Edge.Cuts bounding box, so the
        # next board's x-advance reuses it instead of re-loading f from disk.
        bbox = panel.appendBoard(
            f, pcbnew.VECTOR2I(x, 0), origin=Origin.TopLeft,
            refRenamer=lambda n, r, pre=pre: f"{pre}_{r}",
            netRenamer=lambda n, net, pre=pre: f"{pre}_{net}",
            inheritDrc=False)
        x += bbox.GetWidth() + gap

    # Frame (rails on all four sides) + mouse-bite tabs joining boards to it.
    panel.makeFrame(widthH=rail, widthV=rail, hspace=frame_space, vspace=frame_space)
    panel.buildPartitionLineFromBB()
    panel.buildTabAnnotationsFixed(tabs, tabs, tab_width, tab_width, tab_min_distance, [])
    cuts = panel.buildTabsFromAnnotations(0)
    panel.makeMouseBites(cuts, diameter=mb_diameter, spacing=mb_spacing)

    # Assembly aids on the rails: fiducials for optical alignment, tooling holes
    # for the pick-and-place. Offsets keep them within the rail width.
    panel.addCornerFiducials(4, rail, rail, 1 * mm, 2 * mm)
    panel.addCornerTooling(4, rail, rail, 1.5 * mm)

    panel.save()


def stamp(output, version, config):
    board = pcbnew.LoadBoard(output)
    text = build_stamp(config, version)
    write_stamp(board, text)
    board.Save(output)
    print(f"{output}: {text}")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("board", nargs="+", help="routed .kicad_pcb file(s), laid out left-to-right")
    ap.add_argument("--output", required=True, help="output panel .kicad_pcb path")
    ap.add_argument("--version", help="active version (for the provenance stamp)")
    ap.add_argument("--config", help="config.yaml path (for the provenance stamp)")
    ap.add_argument("--rail", type=float, default=5.0, help="frame rail width, mm (default 5)")
    ap.add_argument("--gap", type=float, default=3.0, help="gap between boards, mm (default 3)")
    ap.add_argument("--frame-space", type=float, default=3.0, help="board-to-frame gap, mm (default 3)")
    ap.add_argument("--tabs", type=int, default=2, help="tabs per board edge (default 2)")
    ap.add_argument("--tab-width", type=float, default=3.0, help="tab width, mm (default 3)")
    ap.add_argument("--mousebite-diameter", type=float, default=0.5, help="mouse-bite hole diameter, mm")
    ap.add_argument("--mousebite-spacing", type=float, default=0.9, help="mouse-bite hole spacing, mm")
    ap.add_argument("--tab-min-distance", type=float, default=8.0, help="min distance between tabs, mm")
    args = ap.parse_args()

    if len(args.board) < 2:
        sys.exit("panelize.py needs at least 2 boards (left + right)")
    for f in args.board:
        if not os.path.isfile(f):
            sys.exit(f"no such board: {f}")

    # KiCad internal units are integer nanometres; mm scales up, so round to int
    # (argparse gives floats) before these reach pcbnew/KiKit geometry calls.
    def nm(v):
        return int(round(v * mm))

    os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
    build(args.board, args.output,
          rail=nm(args.rail), gap=nm(args.gap), frame_space=nm(args.frame_space),
          tabs=args.tabs, tab_width=nm(args.tab_width),
          mb_diameter=nm(args.mousebite_diameter), mb_spacing=nm(args.mousebite_spacing),
          tab_min_distance=nm(args.tab_min_distance))

    if args.version and args.config:
        stamp(args.output, args.version, args.config)
    print(f"panel written to {args.output}")


if __name__ == "__main__":
    main()
