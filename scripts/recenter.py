#!/usr/bin/env python3
"""Translate a KiCad PCB so its Edge.Cuts bounding box is centered on the page.

Ergogen lays both halves out in one shared coordinate space, so each half's own
.kicad_pcb opens off to one side of the sheet. This recenters each board in its
own file. The applied translation is snapped to whole millimeters (the board's
center and the page center are both fractional, so exact centering would need a
fractional shift); each board lands within ~0.5mm of the true page center.

Usage: recenter.py <board.kicad_pcb> [more.kicad_pcb ...]
"""
import re
import sys
import pcbnew

# Standard KiCad page sizes in landscape orientation (width, height) mm.
PAGE_SIZES = {
    "A5": (210.0, 148.0), "A4": (297.0, 210.0), "A3": (420.0, 297.0),
    "A2": (594.0, 420.0), "A1": (841.0, 594.0), "A0": (1189.0, 841.0),
    "A": (279.4, 215.9), "B": (431.8, 279.4), "C": (558.8, 431.8),
}


def page_center(path):
    """Read the (paper ...) line and return the page center (x, y) in mm."""
    with open(path) as f:
        text = f.read()
    m = re.search(r'\(paper\s+"?([A-Za-z0-9]+)"?(.*?)\)', text)
    if not m:
        raise SystemExit(f"{path}: no (paper ...) line found")
    name, rest = m.group(1), m.group(2)
    if name == "User":
        nums = re.findall(r"[\d.]+", rest)
        w, h = float(nums[0]), float(nums[1])
    else:
        w, h = PAGE_SIZES[name]
        if "portrait" in rest:
            w, h = h, w
    return w / 2, h / 2


def recenter(path):
    board = pcbnew.LoadBoard(path)

    # Edge.Cuts bounding box (line width is symmetric, so center is exact).
    bbox = None
    for d in board.GetDrawings():
        if d.GetLayerName() == "Edge.Cuts":
            if bbox is None:
                bbox = d.GetBoundingBox()
            else:
                bbox.Merge(d.GetBoundingBox())
    if bbox is None:
        raise SystemExit(f"{path}: no Edge.Cuts geometry found")
    cx, cy = pcbnew.ToMM(bbox.GetCenter().x), pcbnew.ToMM(bbox.GetCenter().y)

    # Page center (A3 etc.), parsed from the file's (paper ...) line.
    px, py = page_center(path)

    # Whole-millimeter translation toward the page center.
    dx, dy = round(px - cx), round(py - cy)
    offset = pcbnew.VECTOR2I(pcbnew.FromMM(dx), pcbnew.FromMM(dy))

    for item in list(board.GetFootprints()) + list(board.GetDrawings()) \
            + list(board.GetTracks()) + list(board.Zones()):
        item.Move(offset)

    board.Save(path)
    print(f"{path}: center ({cx:.3f},{cy:.3f}) -> ({cx+dx:.3f},{cy+dy:.3f}) "
          f"offset ({dx},{dy})mm, page center ({px:.1f},{py:.1f})")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    for p in sys.argv[1:]:
        recenter(p)
