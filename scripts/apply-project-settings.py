#!/usr/bin/env python3
"""Idempotently ensure custom KiCad project settings (net class + DRC floors).

These live only in the .kicad_pro project JSON (not in the .kicad_pcb or the
ergogen config), so ergogen-generated and freshly-opened projects start without
them. This applies two things:

  * A "VCC" net class (wider clearance/track for the power nets) plus a pattern
    that assigns the "VCC" net to it, matching the manual Board Setup > Net
    Classes steps that used to be documented in the README.
  * DRC floors (min track width / min clearance), which KiCad leaves disabled
    (0.0) by default. Setting them to the fab's recommended minimum makes DRC
    flag any accidental sub-fab feature without touching the intentional 0.20mm+
    widths. Only filled when currently disabled, so an explicit floor is kept.

Re-running is a no-op: each piece is only added when absent/disabled, and a file
is rewritten only when it actually changed. Missing files are skipped quietly,
so a manually-passed glob that matches nothing is harmless.

Usage: apply-project-settings.py <project.kicad_pro> [more.kicad_pro ...]
"""
import json
import os
import sys

# Wider than Default (0.20mm) to give the power nets more copper / clearance.
VCC_CLEARANCE = 0.25
VCC_TRACK_WIDTH = 0.25
VCC_PATTERN = {"netclass": "VCC", "pattern": "VCC"}

# JLCPCB's recommended 2-layer minimum; below the intentional 0.20mm features, so
# it acts purely as a guardrail against accidental hair-thin tracks/gaps.
DRC_FLOORS = {"min_track_width": 0.15, "min_clearance": 0.15}


def ensure_vcc(net_settings):
    """Mutate net_settings in place; return True if anything changed."""
    changed = False

    classes = net_settings.get("classes") or []  # handles absent and null
    net_settings["classes"] = classes
    if not any(c.get("name") == "VCC" for c in classes):
        default = next((c for c in classes if c.get("name") == "Default"), None)
        if default is None:
            print("  skip: no Default net class to derive VCC from", file=sys.stderr)
        else:
            vcc = dict(default)
            vcc["name"] = "VCC"
            vcc["clearance"] = VCC_CLEARANCE
            vcc["track_width"] = VCC_TRACK_WIDTH
            # Default ships with priority 2147483647 (KiCad's lowest-priority
            # sentinel), which dict(default) copies in. Lower number = higher
            # priority, so 0 makes the VCC pattern win over Default for the VCC net.
            vcc["priority"] = 0
            classes.append(vcc)
            changed = True

    patterns = net_settings.get("netclass_patterns") or []  # handles absent and null
    net_settings["netclass_patterns"] = patterns
    if not any(p.get("netclass") == "VCC" for p in patterns):
        patterns.append(dict(VCC_PATTERN))
        changed = True

    return changed


def ensure_drc_floors(rules):
    """Fill disabled (0.0/missing) DRC floors in place; return True if changed."""
    changed = False
    for key, value in DRC_FLOORS.items():
        if not rules.get(key):  # 0.0 or absent = disabled; respect an explicit floor
            rules[key] = value
            changed = True
    return changed


def apply(path):
    with open(path) as f:
        project = json.load(f)
    net_settings = project.setdefault("net_settings", {})
    rules = (
        project.setdefault("board", {})
        .setdefault("design_settings", {})
        .setdefault("rules", {})
    )
    changed = ensure_vcc(net_settings)
    changed = ensure_drc_floors(rules) or changed
    if changed:
        with open(path, "w") as f:
            json.dump(project, f, indent=2)
            f.write("\n")
        print(f"  updated project settings: {path}")
    else:
        print(f"  ok (already up to date): {path}")


def main(paths):
    for path in paths:
        if not os.path.isfile(path):
            continue  # tolerate globs that did not match
        apply(path)


if __name__ == "__main__":
    main(sys.argv[1:])
