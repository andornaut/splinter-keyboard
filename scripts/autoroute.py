#!/usr/bin/env python3
"""Autoroute a KiCad PCB with Freerouting via the Specctra DSN/SES round-trip.

Routes in place: reads and writes the given working .kicad_pcb (the kicad/ copy).
It deliberately never touches kicad/routed/ -- promoting a routed board is a manual
step (npm run copy-pcbs-to-routed).

Tuning via env vars (defaults are aggressive: they bias hard against vias):
  FREEROUTING_PASSES             router max passes (default 100)
  FREEROUTING_STRATEGY           optimizer update strategy: greedy|global|hybrid (default global)
  FREEROUTING_SELECTION          optimizer item selection: prioritized|random|sequential (default random)
  FREEROUTING_VIA_COST           per-via cost; higher = fewer vias (default 300)
  FREEROUTING_UNDESIRED_DIR_COST cost of routing against a layer's preferred direction (default 8.0)

Caveat: high via cost trades vias for *unrouted nets*, not a cleverer low-via
topology -- freerouting will abandon nets before it routes them with fewer vias.
On a regular matrix, hand-routing still beats this. See README.

Usage: autoroute.py <pcb_path> <work_dir> [passes]
  pcb_path  working .kicad_pcb to route (overwritten in place)
  work_dir  directory for intermediate .dsn/.ses files and the freerouting config
  passes    freerouting max passes (default 100; env FREEROUTING_PASSES overrides)
"""
import json
import os
import shutil
import subprocess
import sys
import uuid

import pcbnew

# freerouting resets unknown settings (including scoring) to defaults when the
# config has no version, so this must be set. A version mismatch only warns and
# still applies our standard scoring keys, so a hardcoded value is safe enough.
FREEROUTING_CONFIG_VERSION = "2.2.4"


def write_freerouting_config(config_dir, max_passes, via_cost, undesired_dir_cost):
    """Write freerouting.json so the scoring knobs (config-only, no CLI flag) apply.

    profile.id is required -- freerouting throws a startup NPE (and pops an error
    dialog) when it is missing.
    """
    os.makedirs(config_dir, exist_ok=True)
    config = {
        "profile": {"id": str(uuid.uuid4()), "email": "",
                    "allow_telemetry": False, "allow_contact": False},
        "gui": {"enabled": False},
        "router": {
            "max_passes": int(max_passes),
            "optimizer": {"enabled": True},
            "scoring": {
                "via_costs": int(via_cost),
                "plane_via_costs": int(via_cost),
                "default_preferred_direction_trace_cost": 1.0,
                "default_undesired_direction_trace_cost": float(undesired_dir_cost),
            },
        },
        "usage_and_diagnostic_data": {"disable_analytics": True},
        "version": FREEROUTING_CONFIG_VERSION,
    }
    with open(os.path.join(config_dir, "freerouting.json"), "w") as f:
        json.dump(config, f, indent=2)


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
    config_dir = os.path.join(work_dir, "config")

    strategy = os.environ.get("FREEROUTING_STRATEGY", "global")
    selection = os.environ.get("FREEROUTING_SELECTION", "random")
    via_cost = os.environ.get("FREEROUTING_VIA_COST", "300")
    undesired_dir_cost = os.environ.get("FREEROUTING_UNDESIRED_DIR_COST", "8.0")

    board = pcbnew.LoadBoard(pcb_path)
    if not pcbnew.ExportSpecctraDSN(board, dsn_path):
        sys.exit(f"Failed to export Specctra DSN for {pcb_path}")

    write_freerouting_config(config_dir, passes, via_cost, undesired_dir_cost)

    # Force headless and point freerouting at our tuned config dir; otherwise it
    # pops up a GUI window and ignores the scoring knobs.
    subprocess.run(
        [freerouting, "-de", dsn_path, "-do", ses_path,
         "-mp", str(passes), "-us", strategy, "-is", selection],
        check=True,
        env={**os.environ,
             "FREEROUTING__GUI__ENABLED": "false",
             "FREEROUTING__USER_DATA_PATH": config_dir},
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
