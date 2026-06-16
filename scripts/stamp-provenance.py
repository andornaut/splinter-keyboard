#!/usr/bin/env python3
"""Write the provenance stamp into a generated PCB's title block and silkscreen.

Sets title_block comment 1 to a stamp derived from the active config.yaml (see
provenance.py for the format), and also draws the stamp onto silkscreen (both
F.SilkS and B.SilkS) in the top corner on the pinky (outer) side so the provenance
is visible on the fabricated board. The pinky side is detected per board as the
side opposite the TRRS jack, so the left half stamps top-left and the right half
stamps top-right. Run at the end of build.sh, after recenter.py, on each
dist/ board; the stamp then rides the plain cp steps unchanged into
kicad/unrouted and kicad/routed, and survives manual routing and the GND-zone
resave because every script round-trips the board via LoadBoard()/Save(), which
preserves both the title block and board drawings.

The title-block comment is the only field validate-provenance reads; the silk text
is human-facing. The silk copy drops the 'splinter v=<ver>' prefix (already on the
credit label) and is re-stamped idempotently each run (prior silk stamps, matched
by their leading 'built=', are removed first), so rebuilding does not stack
duplicates.

Usage: stamp-provenance.py --version <vN> --config <config.yaml> <board.kicad_pcb> [more ...]
"""

import argparse

import pcbnew
from provenance import build_stamp, silk_from_stamp, write_stamp

SILK_SIZE_MM = 0.8  # glyph height/width, matching the component labels
SILK_THICKNESS_MM = 0.15
SILK_MARGIN_MM = 0.6  # inset from the top and pinky-side board edges
SILK_TAG = "built="  # leading text identifying a prior provenance silk stamp


def _remove_prior_silk(board):
    """Drop any earlier provenance silk text so a re-stamp does not stack copies."""
    for d in list(board.GetDrawings()):
        if (
            isinstance(d, pcbnew.PCB_TEXT)
            and d.GetLayer() in (pcbnew.F_SilkS, pcbnew.B_SilkS)
            and d.GetText().startswith(SILK_TAG)
        ):
            board.Remove(d)


def _pinky_is_left(board):
    """True if the pinky (outer) side is the board's left edge.

    The TRRS jack marks the inner side (where the two halves meet), so the pinky
    side is opposite it: TRRS on the right -> pinky on the left, and vice versa.
    Defaults to the right edge if no TRRS footprint is found."""
    center_x = board.GetBoardEdgesBoundingBox().GetCenter().x
    for fp in board.GetFootprints():
        if "trrs" in str(
            fp.GetFPID().GetLibItemName()
        ).lower() or fp.GetReference().upper().startswith("TRRS"):
            return fp.GetPosition().x > center_x
    return False


def _add_silk(board, text):
    """Draw `text` in the top corner on the pinky (outer) side, on both F.SilkS and
    B.SilkS.

    Center-justified so the mirrored back copy lands on the same on-board spot as
    the front copy (a left/right-justified reversible text would mirror off the
    edge). Anchored half a text-width plus a margin in from the pinky edge so the
    whole string stays on the board."""
    bbox = board.GetBoardEdgesBoundingBox()
    size = pcbnew.VECTOR2I(pcbnew.FromMM(SILK_SIZE_MM), pcbnew.FromMM(SILK_SIZE_MM))
    margin = pcbnew.FromMM(SILK_MARGIN_MM)
    pinky_left = _pinky_is_left(board)
    for layer, mirror in ((pcbnew.F_SilkS, False), (pcbnew.B_SilkS, True)):
        t = pcbnew.PCB_TEXT(board)
        t.SetText(text)
        t.SetLayer(layer)
        t.SetMirrored(mirror)
        t.SetTextSize(size)
        t.SetTextThickness(pcbnew.FromMM(SILK_THICKNESS_MM))
        t.SetHorizJustify(pcbnew.GR_TEXT_H_ALIGN_CENTER)
        t.SetVertJustify(pcbnew.GR_TEXT_V_ALIGN_CENTER)
        board.Add(t)
        half_width = (
            t.GetBoundingBox().GetWidth() // 2
        )  # rendered width, position-independent
        if pinky_left:
            x = bbox.GetLeft() + margin + half_width
        else:
            x = bbox.GetRight() - margin - half_width
        y = bbox.GetTop() + margin + size.y // 2
        t.SetPosition(pcbnew.VECTOR2I(int(x), int(y)))


def stamp(text, path):
    board = pcbnew.LoadBoard(path)
    write_stamp(board, text)
    _remove_prior_silk(board)
    _add_silk(board, silk_from_stamp(text))
    board.Save(path)
    print(f"{path}: {text}")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--version", required=True, help="active version, e.g. v4")
    ap.add_argument("--config", required=True, help="path to the version's config.yaml")
    ap.add_argument("pcb", nargs="+", help="board(s) to stamp")
    args = ap.parse_args()
    # Build the stamp once so every board in a run shares one timestamp/commit/hash
    # (and git + the config hash run once, not once per board).
    text = build_stamp(args.config, args.version)
    for p in args.pcb:
        stamp(text, p)


if __name__ == "__main__":
    main()
