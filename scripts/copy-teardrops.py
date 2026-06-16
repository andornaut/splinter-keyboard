#!/usr/bin/env python3
"""Copy teardrop zones from a source PCB onto a destination PCB.

kb_ergogen_helper's `copy-traces` copies only PCB_TRACK objects (segments, arcs,
vias) via GetTracks(); teardrops are stored as ZONE objects (IsTeardropArea()),
so copy-traces alone never carries them across. This complements it: it removes
any teardrop zones already on the destination (so re-runs are idempotent and do
not stack duplicates), then copies the source's teardrop zones over.

Invoked per board from copy-traces-to-unrouted.sh right after the trace
copy. Usage: copy-teardrops.py <src.kicad_pcb> <dst.kicad_pcb>
"""
import sys
import pcbnew


def teardrop_zones(board):
    return [z for z in board.Zones() if z.IsTeardropArea()]


def copy_teardrops(src_path, dst_path):
    src = pcbnew.LoadBoard(src_path)
    dst = pcbnew.LoadBoard(dst_path)

    # Clear the destination's teardrops first so a re-run replaces rather than
    # duplicates them. RemoveNative (not Remove) deletes each zone's C++ object;
    # a bare Remove only unlinks it, leaving an orphan that swig reports as a
    # leaked ZONE * at interpreter shutdown.
    stale = teardrop_zones(dst)
    for z in stale:
        dst.RemoveNative(z)

    # Add a Duplicate of each source teardrop so dst owns its own copy and src
    # frees its originals; adding the src object directly would leave both boards
    # claiming ownership (the same swig "leaked ZONE *" warning).
    fresh = teardrop_zones(src)
    for z in fresh:
        dst.Add(z.Duplicate())

    dst.Save(dst_path)
    print(f'Copied {len(fresh)} teardrop zone(s) (removed {len(stale)} stale) into {dst_path}')


if __name__ == '__main__':
    if len(sys.argv) != 3:
        raise SystemExit(__doc__)
    copy_teardrops(sys.argv[1], sys.argv[2])
