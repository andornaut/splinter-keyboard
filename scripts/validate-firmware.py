#!/usr/bin/env python3
"""Check the generated PCBs against each other and against the QMK firmware.

Two gates, because the MCU pin mapping is the one design error no other check in
this repo can see. A board whose matrix nets land on the wrong MCU header pin
is fully routed, shorts nothing, and passes provenance, DRC and validate:fab. It
fails only when a human plugs an MCU in, which is after the boards are paid for.

  1. Half symmetry (always runs, no external dependency). Every board's MCU pad
     net arrangement, measured in absolute board space, must be identical. The
     MCU is a physical part and cannot be mirrored, so a split whose halves
     disagree has exactly one half wired backwards.

  2. Firmware agreement (required). The matrix pins implied by the boards must
     equal keyboards/splinter/keyboard.json. Scope: the comparison runs net
     names through the footprint's fixed net-to-GPIO table (P4 -> GP4), and
     raw_pin_column does not move that table (it swaps which net name occupies
     each row's left/right pad, and the silk label follows the net). So this
     catches config.yaml drifting from keyboard.json (a renamed net, a
     reordered column, a moved serial pin) but is invariant under a
     raw_pin_column flip.

Neither check can prove the boards match physical reality. Both mirrorings of
the header are electrically valid and nothing on the board distinguishes them,
so which physical pin each net reaches rests on raw_pin_column matching how the
MCU is seated, which only hardware settles. It is settled: the current value,
front_right, is confirmed on an assembled and working board, so treat it as
fixed and re-confirm on hardware if it or the MCU seating ever changes.

Usage: validate-firmware.py [unrouted|routed] [--firmware <source>]

The firmware source is an http(s) URL or a local path (absolute, or relative to
the repo root; ~ is expanded). It is resolved from, in order: --firmware, then
$SPLINTER_FIRMWARE_JSON, then package.json's config.FIRMWARE. It is required and
any failure to read it is fatal: a board is not fab-ready until firmware is
proven to match it, so an unset, unreachable or malformed source is a reason to
stop rather than to proceed with one fewer check.

The shipped config.FIRMWARE is a path to a sibling qmk_firmware checkout, so
this gate (and therefore the whole pipeline) needs that checkout present. That
is deliberate: the firmware is developed alongside the boards, and a local path
checks what you are about to flash rather than what is pushed. On a machine
without it, pass --firmware with the raw.githubusercontent.com URL.

Run via: npm run validate:firmware
"""

import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

from lib.pcbnew_quiet import pcbnew
from lib.pipeline_log import note
from lib.stages import add_stage_argument, selected

FOOTPRINT_JS = "ergogen/footprints/mcu_liatris.js"
FETCH_TIMEOUT_S = 15
# Nets on the MCU header that are power/programming rather than matrix lines.
NON_MATRIX = {"GND", "VCC", "RAW", "RST", ""}
# Socket rows on the Liatris header, 2 pads each. The extra bottom pins
# (GP12-GP16) sit near x 0, so they never reach the +-7.62mm column filter.
HEADER_ROWS = 12


def pin_labels():
    """Map ergogen net name -> MCU GPIO label, from the footprint's own table.

    The leading boundary matters: without it `GP15_label` also matches `P15_label`
    and the extra-pin entries silently overwrite the header pins.
    """
    with Path(FOOTPRINT_JS).open() as fh:
        src = fh.read()
    return dict(re.findall(r"(?:^|[^A-Za-z0-9_])(P\d+)_label:\s*'(GP\d+)'", src, re.MULTILINE))


def mcu_pad_map(board):
    """MCU header nets keyed by (row y, column side) in absolute board space.

    Local footprint coordinates are not comparable between boards: a footprint on
    B.Cu is flipped, so pcbnew's absolute positions are the only common frame.

    Finding nothing is a hard error, not an empty result: the callers would then
    compare empty maps and report agreement, passing the gate having measured
    nothing.
    """
    name = Path(board.GetFileName()).name or "<board>"
    fps = [f for f in board.GetFootprints() if "mcu_liatris" in f.GetFPIDAsString()]
    if len(fps) != 1:
        raise SystemExit(f"{name}: expected exactly 1 MCU footprint, found {len(fps)}")
    fp = fps[0]
    ox, oy = fp.GetPosition().x, fp.GetPosition().y
    rows = {}
    for pad in fp.Pads():
        x, y = pad.GetPosition().x, pad.GetPosition().y
        if abs(abs(x - ox) - 7620000) > 50000:  # header columns sit at +-7.62mm
            continue
        rows.setdefault(round((y - oy) / 1e6, 2), {})["L" if x < ox else "R"] = pad.GetNetname()
    if len(rows) != HEADER_ROWS or any(len(r) != 2 for r in rows.values()):
        raise SystemExit(
            f"{name}: found {len(rows)} MCU header row(s), expected {HEADER_ROWS} of 2 pads.\n"
            "  The pad filter assumes an unrotated footprint with its columns at\n"
            "  +-7.62mm; a rotate: on the MCU or a pitch change breaks it. Fix the\n"
            "  filter rather than letting the check pass having measured nothing."
        )
    return [rows[k] for k in sorted(rows)]


def _median(values):
    s = sorted(values)
    return s[len(s) // 2]


def matrix_order(board):
    """(ordered column nets, ordered row nets) derived from board geometry.

    Columns sort left to right, rows top to bottom, matching QMK's arrays. Splayed
    thumb switches are excluded from the column sort: they sit far from their own
    column's matrix keys and would scramble the ordering.
    """
    cols, rows = {}, {}
    for fp in board.GetFootprints():
        fpid = fp.GetFPIDAsString()
        pos = fp.GetPosition()
        if "switch_mx" in fpid:
            splayed = abs(fp.GetOrientationDegrees() % 180.0) > 0.5
            for pad in fp.Pads():
                if pad.GetPadName() == "1" and not splayed:
                    cols.setdefault(pad.GetNetname(), []).append(pos.x)
        elif "diode" in fpid:
            for pad in fp.Pads():
                if pad.GetPadName() == "1":  # cathode, carries the row net
                    rows.setdefault(pad.GetNetname(), []).append(pos.y)
    ordered_cols = sorted(cols, key=lambda n: _median(cols[n]))
    ordered_rows = sorted(rows, key=lambda n: _median(rows[n]))
    return ordered_cols, ordered_rows


def serial_net(board):
    """The post-protection data net: the resistor net that also lands on the MCU."""
    mcu_nets = {n for row in mcu_pad_map(board) for n in row.values()}
    for fp in board.GetFootprints():
        if "R_0805" not in fp.GetFPIDAsString():
            continue
        for pad in fp.Pads():
            net = pad.GetNetname()
            if net in mcu_nets and net not in NON_MATRIX:
                return net
    return None


def load_boards(version, stages):
    boards = {}
    for stage in stages:
        d = f"{version}/kicad/{stage}"
        if not Path(d).is_dir():
            continue
        for entry in sorted(Path(d).iterdir()):
            name = entry.name
            if not name.endswith(".kicad_pcb") or name.startswith("_"):
                continue
            # str(): pcbnew takes a file name, not a Path.
            boards[f"{stage}/{name}"] = pcbnew.LoadBoard(str(entry))
    return boards


def check_symmetry(boards):
    """Every board must present the same MCU pad arrangement in absolute space."""
    failures = []
    by_stage = {}
    for key, board in boards.items():
        stage = key.split("/")[0]
        by_stage.setdefault(stage, {})[key] = mcu_pad_map(board)
    for stage, mapped in sorted(by_stage.items()):
        distinct = {tuple(tuple(sorted(r.items())) for r in v) for v in mapped.values()}
        if len(distinct) > 1:
            failures.append(stage)
            sys.stdout.flush()  # keep the ok lines above this under a pipe
            print(f"  FAIL {stage}: halves disagree on MCU pad wiring", file=sys.stderr)
            print(
                "    Columns named from the PCB front; from the back, swap them",
                file=sys.stderr,
            )
            for key, pads in sorted(mapped.items()):
                top = pads[0]
                print(
                    f"    {key}: row 0 is {top.get('L')} (front-left) | {top.get('R')} (front-right)",
                    file=sys.stderr,
                )
            print(
                "    The MCU cannot be mirrored, so one half is wired backwards, and\n"
                "    both halves must share one raw_pin_column value",
                file=sys.stderr,
            )
        else:
            note(f"  ok {stage}: all {len(mapped)} board(s) agree on MCU pad wiring")
    return failures


def resolve_firmware_source(override):
    """The firmware source. Required: boards are not fab-ready without one."""
    if override:
        return override
    for env in ("SPLINTER_FIRMWARE_JSON", "npm_package_config_FIRMWARE"):
        if os.environ.get(env):
            return os.environ[env]
    raise SystemExit(
        "validate:firmware: no firmware source configured. A board cannot be fabbed\n"
        "  without firmware proven to match it, so this is required, not optional.\n"
        "  Set one of: --firmware <url|path>, $SPLINTER_FIRMWARE_JSON, or\n"
        "  package.json config.FIRMWARE."
    )


def load_firmware(source):
    """Parse keyboard.json from an http(s) URL or a local path.

    Returns (parsed, None) or (None, reason). Relative paths resolve against the
    cwd, which is the repo root for every npm-run script here.
    """
    if re.match(r"^https?://", source, re.IGNORECASE):
        try:
            # The source is the operator's own --firmware argument.
            with urllib.request.urlopen(source, timeout=FETCH_TIMEOUT_S) as resp:  # noqa: S310
                return json.loads(resp.read().decode("utf-8")), None
        except (urllib.error.URLError, OSError, TimeoutError) as exc:
            return None, f"could not fetch {source}: {exc}"
        except (ValueError, UnicodeDecodeError) as exc:
            return None, f"{source} is not valid JSON: {exc}"
    path = Path(source).expanduser()
    if not path.is_file():
        return None, f"{path} not found"
    try:
        with path.open() as fh:
            return json.load(fh), None
    except ValueError as exc:
        return None, f"{path} is not valid JSON: {exc}"


def check_firmware(boards, fw, labels):
    want = {
        "left": (fw["matrix_pins"]["cols"], fw["matrix_pins"]["rows"]),
        "right": (
            fw["split"]["matrix_pins"]["right"]["cols"],
            fw["split"]["matrix_pins"]["right"]["rows"],
        ),
    }
    failures = []
    for key, board in sorted(boards.items()):
        half = key.rsplit("/", 1)[-1].replace(".kicad_pcb", "")
        if half not in want:
            continue
        cols, rows = matrix_order(board)
        got_cols = [labels.get(n, n) for n in cols]
        got_rows = [labels.get(n, n) for n in rows]
        fw_cols = [p for p in want[half][0] if p != "NO_PIN"]
        fw_rows = [p for p in want[half][1] if p != "NO_PIN"]
        for what, got, expected in (
            ("cols", got_cols, fw_cols),
            ("rows", got_rows, fw_rows),
        ):
            if got != expected:
                failures.append(key)
                sys.stdout.flush()  # keep the ok lines above this under a pipe
                print(f"  FAIL {key}: {what} disagree", file=sys.stderr)
                print(f"    board    {got}", file=sys.stderr)
                print(f"    firmware {expected}", file=sys.stderr)
        net = serial_net(board)
        got_serial = labels.get(net, net)
        if got_serial != fw["split"]["serial"]["pin"]:
            failures.append(key)
            sys.stdout.flush()  # keep the ok lines above this under a pipe
            print(
                f"  FAIL {key}: serial pin, board {got_serial}, firmware {fw['split']['serial']['pin']}",
                file=sys.stderr,
            )
        if key not in failures:
            note(f"  ok {key}: matrix pins and serial pin match the firmware")
    return failures


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    add_stage_argument(ap, "stage(s) to check (default: both)")
    ap.add_argument(
        "--firmware",
        metavar="SOURCE",
        help="keyboard.json URL or path (default: $SPLINTER_FIRMWARE_JSON, else package.json's config.FIRMWARE)",
    )
    args = ap.parse_args()

    stages = selected(args)
    version = os.environ.get("npm_package_config_VERSION")
    if not version:
        raise SystemExit("set npm_package_config_VERSION via npm (npm run validate:firmware)")

    labels = pin_labels()
    boards = load_boards(version, stages)
    if not boards:
        raise SystemExit(f"no PCBs found for {version} in {stages}")

    source = resolve_firmware_source(args.firmware)

    note(f"validate:firmware: {len(boards)} board(s) for {version}")
    failures = check_symmetry(boards)

    fw, reason = load_firmware(source)
    if fw is None:
        raise SystemExit(f"validate:firmware: {reason}")
    note(f"  firmware source: {source}")
    failures += check_firmware(boards, fw, labels)

    if failures:
        sys.stdout.flush()
        print(
            f"validate:firmware: {len(failures)} check(s) failed for {version}",
            file=sys.stderr,
        )
        raise SystemExit(1)
    # The firmware source names an external input that varies by machine, so the
    # summary carries it rather than a line of its own.
    print(f"OK: validate:firmware: {len(boards)} board(s) match {source}")


if __name__ == "__main__":
    main()
