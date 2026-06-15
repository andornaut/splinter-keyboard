#!/usr/bin/env python3
"""Autoroute a KiCad PCB with Freerouting via the Specctra DSN/SES round-trip.

Routes in place: reads and writes the given working .kicad_pcb (the kicad/ copy).
It deliberately never touches kicad/routed/ -- promoting a routed board is a manual
step (npm run copy-pcbs-kicad-to-routed).

Tuning via env vars. Defaults favour a fully-connected, DRC-clean board (greedy
strategy, freerouting's native via cost), which empirically routes the most nets
with the fewest violations on this design:
  FREEROUTING_PASSES             router max passes (default 100)
  FREEROUTING_STRATEGY           optimizer update strategy: greedy|global|hybrid (default greedy)
  FREEROUTING_SELECTION          optimizer item selection: prioritized|random|sequential (default prioritized)
  FREEROUTING_VIA_COST           per-via cost; higher = fewer vias (default 50)
  FREEROUTING_UNDESIRED_DIR_COST cost of routing against a layer's preferred direction (default: unset)
  FREEROUTING_LOG_LEVEL          log level for freerouting + wx output: ERROR|WARN|INFO|DEBUG|TRACE (default WARN)

Caveat: cranking via cost trades vias for *unrouted nets*, not a cleverer low-via
topology -- freerouting abandons nets before it routes them with fewer vias. On a
regular matrix, hand-routing still beats this for a low via count. See README.

Run via: npm run autoroute (sets npm_package_config_VERSION from package.json).
With no arguments it routes every working .kicad_pcb for the active version
(${VERSION}/kicad/[!_]*.kicad_pcb) in place; intermediates go to
dist/${VERSION}/kicad/freerouting/. Pass explicit paths to route just those:

  autoroute.py [pcb_path ...]
  pcb_path  working .kicad_pcb to route in place (default: all for the version)
            FREEROUTING_PASSES sets freerouting max passes (default 100)
"""
import glob
import json
import os
import shutil
import subprocess
import sys
import uuid

import pcbnew
import wx

# Single tuneable log level (env FREEROUTING_LOG_LEVEL, default WARN) applied to
# both freerouting's own logs and the wxWidgets chatter pcbnew emits to stderr
# (e.g. "Adding duplicate image handler") when it re-initializes between loads.
LOG_LEVEL = os.environ.get("FREEROUTING_LOG_LEVEL", "WARN").upper()
_WX_LOG_LEVELS = {
    "ERROR": wx.LOG_Error,
    "WARN": wx.LOG_Warning,
    "INFO": wx.LOG_Info,
    "DEBUG": wx.LOG_Debug,
    "TRACE": wx.LOG_Trace,
}
wx.Log.SetLogLevel(_WX_LOG_LEVELS.get(LOG_LEVEL, wx.LOG_Warning))

# freerouting resets unknown settings (including scoring) to defaults when the
# config has no version, so this must be set. A version mismatch only warns and
# still applies our standard scoring keys, so a hardcoded value is safe enough.
FREEROUTING_CONFIG_VERSION = "2.2.4"


def write_freerouting_config(config_dir, max_passes, scoring):
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
            "scoring": scoring,
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

    strategy = os.environ.get("FREEROUTING_STRATEGY", "greedy")
    selection = os.environ.get("FREEROUTING_SELECTION", "prioritized")
    via_cost = int(os.environ.get("FREEROUTING_VIA_COST", "50"))
    scoring: dict[str, float] = {"via_costs": via_cost, "plane_via_costs": via_cost}
    # Only impose a direction penalty when asked; freerouting's default has no
    # strong preference, which routes cleaner here.
    undesired_dir_cost = os.environ.get("FREEROUTING_UNDESIRED_DIR_COST")
    if undesired_dir_cost is not None:
        scoring["default_preferred_direction_trace_cost"] = 1.0
        scoring["default_undesired_direction_trace_cost"] = float(undesired_dir_cost)

    board = pcbnew.LoadBoard(pcb_path)
    if not pcbnew.ExportSpecctraDSN(board, dsn_path):
        sys.exit(f"Failed to export Specctra DSN for {pcb_path}")

    write_freerouting_config(config_dir, passes, scoring)

    # Point freerouting at our tuned config dir via the CLI arg (the
    # FREEROUTING__USER_DATA_PATH env var works too but its generic settings
    # binder logs a spurious "Unknown settings property" warning). GUI/logging
    # are real settings keys, so they bind cleanly as env vars.
    subprocess.run(
        [freerouting, "-de", dsn_path, "-do", ses_path,
         "-mp", str(passes), "-us", strategy, "-is", selection,
         f"--user_data_path={config_dir}"],
        check=True,
        env={**os.environ,
             "FREEROUTING__GUI__ENABLED": "false",
             "FREEROUTING__LOGGING__CONSOLE__LEVEL": LOG_LEVEL,
             "FREEROUTING__LOGGING__FILE__LEVEL": LOG_LEVEL},
    )
    if not os.path.exists(ses_path):
        sys.exit(f"Freerouting did not produce {ses_path}")

    # Import onto the board already in memory: ExportSpecctraDSN only serialized
    # it (no mutation) and pcb_path is untouched until the Save below, so this is
    # the same unrouted board a reload would give. Then save over the working file.
    if not pcbnew.ImportSpecctraSES(board, ses_path):
        sys.exit(f"Failed to import Specctra SES into {pcb_path}")
    board.Save(pcb_path)
    print(f"Routed {pcb_path}")


if __name__ == "__main__":
    version = os.environ.get("npm_package_config_VERSION")
    if not version:
        sys.exit("npm_package_config_VERSION unset -- run via npm (npm run autoroute).")
    passes = os.environ.get("FREEROUTING_PASSES", "100")
    work_dir = f"dist/{version}/kicad/freerouting"

    pcbs = sys.argv[1:] or sorted(glob.glob(f"{version}/kicad/[!_]*.kicad_pcb"))
    if not pcbs:
        sys.exit(f"No PCBs in {version}/kicad/ -- nothing to do.")
    for pcb in pcbs:
        autoroute(pcb, work_dir, passes)
