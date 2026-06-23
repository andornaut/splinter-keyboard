#!/usr/bin/env python3
"""Idempotently ensure custom KiCad project settings (net class + DRC floors)
and the keepout DRC custom-rules file.

These live only in the .kicad_pro project JSON (not in the .kicad_pcb or the
ergogen config), so ergogen-generated and freshly-opened projects start without
them, plus a sibling `<board>.kicad_dru` custom-rules file. This applies four
things:

  * A "VCC" net class (wider clearance/track for the power nets) plus a pattern
    that assigns the "VCC" net to it, matching the manual Board Setup > Net
    Classes steps that used to be documented in the README.
  * DRC floors (min track width / min clearance), which KiCad leaves disabled
    (0.0) by default. Setting them to the fab's recommended minimum makes DRC
    flag any accidental sub-fab feature without touching the intentional 0.20mm+
    widths. Only filled when currently disabled, so an explicit floor is kept.
  * DRC severity overrides. The footprints are embedded ergogen-generated parts
    whose library nicknames (ceoloide, splinter, E73) are not in any footprint
    library table, so KiCad raises a "library not included" warning per part.
    There is no on-disk library to register, so the check is downgraded to
    "ignore". Only set when not already "ignore", so a manual override is kept.
  * A `<board>.kicad_dru` custom-rules file next to each project, which the GUI
    and `kicad-cli pcb drc` auto-load. It enforces that the copper keepout rule
    areas from scripts/add-keepout-zones.py reject conductive pads (any pad that
    is not a bare 'NPTH, mechanical' hole) while allowing the mechanical holes
    (mounting holes, the TRRS locating hole). The rule-area pad keepout cannot
    tell a copper pad from a bare hole, so that policy lives here; tracks/vias/
    pour are handled by the rule areas.

Re-running is a no-op: each piece is only added when absent/disabled, and a file
is rewritten only when it actually changed. Missing files are skipped quietly,
so a manually-passed glob that matches nothing is harmless.

Usage: apply-project-settings.py <project.kicad_pro> [more.kicad_pro ...]
"""
import json
import os
import sys

# Spacing between routes. Raised from KiCad's 0.20mm default to give the
# hand-routed matrix more yield margin at JLCPCB. Track width stays 0.20mm (the
# matrix nets carry ~no current, and a fatter track would eat the new spacing in
# the tight MCU pin field); only the gap grows.
DEFAULT_CLEARANCE = 0.25

# Track stays wider than Default to give the power nets more copper; clearance
# now matches Default (both 0.25mm), unifying the gap across the board.
VCC_CLEARANCE = 0.25
VCC_TRACK_WIDTH = 0.25
VCC_PATTERN = {"netclass": "VCC", "pattern": "VCC"}

# JLCPCB's recommended 2-layer minimum; below the intentional 0.20mm features, so
# it acts purely as a guardrail against accidental hair-thin tracks/gaps.
DRC_FLOORS = {"min_track_width": 0.15, "min_clearance": 0.15}

# Generated footprints carry library nicknames (ceoloide, splinter, E73) that are
# not in any footprint library table; the parts are embedded so this is harmless.
SEVERITY_OVERRIDES = {"lib_footprint_issues": "ignore"}

# Custom DRC rules, written verbatim to each board's sibling <name>.kicad_dru.
# Disallows conductive pads inside the keepout rule areas that
# scripts/add-keepout-zones.py adds (the route ring keepout_perimeter_route and
# the screw-boss disks keepout_screw_bosses), so a copper pad straying under the
# case wall or onto a boss is flagged, while bare mechanical holes are left alone.
# The discriminator is the pad TYPE, not plating: flag everything except
# 'NPTH, mechanical'. (A.isPlated() is wrong here -- it is true only for a plated
# HOLE, so it misses SMD copper pads, which is most of this board: the hotswap
# socket lands, SMD diodes, resistor, TVS. NPTH holes report onCu, so a copper-
# layer test cannot tell them from real pads either.) NPTH stays allowed so the
# mounting holes (which sit dead-center in their own boss keepouts) and the TRRS
# locating holes pass. The pour-only ring (keepout_perimeter_pour) is omitted on
# purpose: it excludes only the GND plane, not pads, so the TRRS corner through-
# holes (inside the pour ring but outside the route ring) are not flagged.
# Keep the zone names in sync with add-keepout-zones.py.
DRC_RULES = (
    "(version 1)\n"
    '(rule "keepout_conductive_pads"\n'
    "\t(constraint disallow pad)\n"
    "\t(condition \"A.Pad_Type != 'NPTH, mechanical'"
    " && (A.insideArea('keepout_perimeter_route')"
    " || A.insideArea('keepout_screw_bosses'))\"))\n"
)


def ensure_default_clearance(net_settings):
    """Set the Default net class clearance in place; return True if changed."""
    for c in net_settings.get("classes") or []:
        if c.get("name") == "Default" and c.get("clearance") != DEFAULT_CLEARANCE:
            c["clearance"] = DEFAULT_CLEARANCE
            return True
    return False


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


def ensure_severity_overrides(severities):
    """Set DRC severities to the desired value in place; return True if changed."""
    changed = False
    for key, value in SEVERITY_OVERRIDES.items():
        if severities.get(key) != value:  # respect an existing matching override
            severities[key] = value
            changed = True
    return changed


def ensure_drc_rules(pro_path):
    """Write the sibling <board>.kicad_dru custom-rules file if missing or stale;
    return the path if it was (re)written, else None."""
    dru_path = pro_path[:-len(".kicad_pro")] + ".kicad_dru"
    existing = None
    if os.path.isfile(dru_path):
        with open(dru_path) as f:
            existing = f.read()
    if existing == DRC_RULES:
        return None
    with open(dru_path, "w") as f:
        f.write(DRC_RULES)
    return dru_path


def apply(path):
    with open(path) as f:
        project = json.load(f)
    net_settings = project.setdefault("net_settings", {})
    design_settings = project.setdefault("board", {}).setdefault("design_settings", {})
    rules = design_settings.setdefault("rules", {})
    severities = design_settings.setdefault("rule_severities", {})
    changed = ensure_default_clearance(net_settings)
    changed = ensure_vcc(net_settings) or changed
    changed = ensure_drc_floors(rules) or changed
    changed = ensure_severity_overrides(severities) or changed
    if changed:
        with open(path, "w") as f:
            json.dump(project, f, indent=2)
            f.write("\n")
        print(f"  updated project settings: {path}")
    else:
        print(f"  ok (already up to date): {path}")
    dru = ensure_drc_rules(path)
    if dru:
        print(f"  wrote custom DRC rules: {dru}")


def main(paths):
    for path in paths:
        if not os.path.isfile(path):
            continue  # tolerate globs that did not match
        apply(path)


if __name__ == "__main__":
    main(sys.argv[1:])
