#!/usr/bin/env python3
"""Autoroute a KiCad PCB with Freerouting via the Specctra DSN/SES round-trip.

Routes in place: reads and writes the given working .kicad_pcb (the kicad/ copy).
It deliberately never touches kicad/routed/ -- promoting a routed board is a manual
step (npm run copy-pcbs-to-routed).

Usage: autoroute.py <pcb_path> <work_dir> [passes]
  pcb_path  working .kicad_pcb to route (overwritten in place)
  work_dir  directory for intermediate .dsn/.ses files
  passes    freerouting max passes (default 100; env FREEROUTING_PASSES overrides)
"""
import os
import shutil
import subprocess
import sys

import pcbnew


def autoroute(pcb_path, work_dir, passes):
    freerouting = shutil.which("freerouting")
    if not freerouting:
        sys.exit(
            "freerouting not found on PATH. Install it via ansible-ctrl "
            "(ansible-playbook hobbies.yml --tags freerouting) or see "
            "https://github.com/freerouting/freerouting"
        )

    pcb_path = os.path.abspath(pcb_path)
    name = os.path.splitext(os.path.basename(pcb_path))[0]
    os.makedirs(work_dir, exist_ok=True)
    dsn_path = os.path.join(work_dir, name + ".dsn")
    ses_path = os.path.join(work_dir, name + ".ses")

    board = pcbnew.LoadBoard(pcb_path)
    if not pcbnew.ExportSpecctraDSN(board, dsn_path):
        sys.exit(f"Failed to export Specctra DSN for {pcb_path}")

    # Force headless; otherwise freerouting 2.x pops up a GUI window.
    subprocess.run(
        [freerouting, "-de", dsn_path, "-do", ses_path, "-mp", str(passes)],
        check=True,
        env={**os.environ, "FREEROUTING__GUI__ENABLED": "false"},
    )
    if not os.path.exists(ses_path):
        sys.exit(f"Freerouting did not produce {ses_path}")

    # Re-load the board so the session import applies to a clean copy, then save
    # back over the working file.
    board = pcbnew.LoadBoard(pcb_path)
    if not pcbnew.ImportSpecctraSES(board, ses_path):
        sys.exit(f"Failed to import Specctra SES into {pcb_path}")
    board.Save(pcb_path)
    print(f"Routed {pcb_path}")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    passes = sys.argv[3] if len(sys.argv) > 3 else os.environ.get("FREEROUTING_PASSES", "100")
    autoroute(sys.argv[1], sys.argv[2], passes)
