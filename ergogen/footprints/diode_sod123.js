// diode_sod123: combined thru-hole and SMD diode footprint for the SOD-123
// package (e.g. the Semtech 1N4148W matrix diode), single- or both-side. The
// module and reference designator follow `side`, so a `side: B` placement is
// reported on the back by `kicad-cli pcb export pos`.
//
// Source: forked from ceoloide/diode_tht_sod123.js by Marco Massarelli
//   (@ceoloide + @ergogen, @infused-kim, @achamian, @im-AMS),
//   https://github.com/ceoloide/ergogen-footprints.
// License: CC-BY-NC-SA-4.0 (inherited from upstream).
//
// Differs from upstream ceoloide/diode_tht_sod123 in two ways:
//   1. The module and reference-designator layers follow `side` instead of being
//      forced to F whenever `reversible` is true (upstream hardcoded
//      `${p.reversible ? 'F' : p.side}`). A reversible `side: B` diode was
//      therefore reported on the Top side by the position file, splitting JLCPCB
//      single-side (Economic) assembly across both sides (diodes on Top, the
//      TVS/resistor on Bottom). Pads and silk are still drawn on both copper
//      sides when `reversible` is true; only the module/designator side tracks
//      `side`.
//   2. `include_traces_vias` is independent of `reversible`: the routing
//      traces/vias emit whenever `include_traces_vias` is true, so single-side
//      placements get both-side routing too. Upstream gated it on `reversible`.
//
// Geometry: unchanged from upstream. SOD-123 land, 0.9 x 1.2mm SMD pads at 3.3mm
// center-to-center; optional THT pads (`include_tht`) at 7.62mm pitch.
//
// Params:
//   side                  F or B, the side to place the footprint and designator on
//   designator            reference prefix (default D)
//   from / to             pad nets. Pad "1" = cathode (banded end) = `to`;
//                         pad "2" = anode = `from`.
//   reversible            if true, draw pads and silk on both copper sides for a
//                         reversible PCB (module/designator still follow `side`).
//                         Default false.
//   include_tht           if true, add through-hole pads alongside the SMD ones.
//                         Default false.
//   include_thru_hole_smd_pads  if true (with reversible), make the SMD pads
//                         thru-hole to connect front to back, easing routing at
//                         the cost of slightly harder hand-soldering. Default false.
//   include_traces_vias   if true, add traces and vias exposing each pad's net on
//                         the opposite copper layer for routing. Works with or
//                         without `reversible`; skipped when
//                         `include_thru_hole_smd_pads` is set (the pad already
//                         spans both layers). Default false.
//   trace_width           routing-helper trace width (default 0.25). Below 0.15
//                         not recommended (JLCPCB min 0.127).
//   trace_distance        pad-to-via gap along the part's long axis (default 1.2).
//                         Negative moves the via inward, under the diode.
//   via_size / via_drill  routing-helper via dimensions (defaults 0.6 / 0.3).
//                         Stay within JLCPCB min (0.56 / 0.3) and KiCad default (0.8 / 0.4).
//   diode_3dmodel_filename  path to a STEP/WRL 3D model (default ''); use the
//                         ${VAR_NAME} syntax for a KiCad-configured path.
//   diode_3dmodel_xyz_offset / _rotation / _scale  3D-model placement adjustments
//                         (defaults [0, 0, 0] / [0, 0, 0] / [1, 1, 1]).
module.exports = {
  params: {
    designator: 'D',
    side: 'B',
    reversible: false,
    include_traces_vias: false,
    trace_distance: { type: 'number', value: 1.2 },
    trace_width: 0.25,
    via_size: 0.6,
    via_drill: 0.3,
    include_tht: false,
    include_thru_hole_smd_pads: false,
    diode_3dmodel_filename: '',
    diode_3dmodel_xyz_offset: [0, 0, 0],
    diode_3dmodel_xyz_rotation: [0, 0, 0],
    diode_3dmodel_xyz_scale: [1, 1, 1],
    from: { type: 'net', value: undefined },
    to: { type: 'net', value: undefined }
  },
  body: p => {
    const standard_opening = `
    (footprint "splinter:diode_sod123"
        (layer "${p.side}.Cu")
        ${p.at}
        (property "Reference" "${p.ref}"
            (at 0 0 ${p.r})
            (layer "${p.side}.SilkS")
            ${p.ref_hide}
            (effects (font (size 1 1) (thickness 0.15)))
        )
        `
    // This can be useful to avoid confusion from the fab, since via-in-pads are usually premium
    const thru_hole_smd_pads_description = `
      (property "Description" "Thru-hole SMD pads, *NOT* via-in-pad (do not plug or tent)."
        (at 0 0 0)
        (unlocked yes)
        (layer "F.Fab")
        (hide yes)
        (effects
          (font
            (size 1.27 1.27)
          )
        )
      )
    `
    const front_silk = `
      (fp_line (start 0.25 0) (end 0.75 0) (layer "F.SilkS") (stroke (width 0.1) (type solid)))
      (fp_line (start 0.25 0.4) (end -0.35 0) (layer "F.SilkS") (stroke (width 0.1) (type solid)))
      (fp_line (start 0.25 -0.4) (end 0.25 0.4) (layer "F.SilkS") (stroke (width 0.1) (type solid)))
      (fp_line (start -0.35 0) (end 0.25 -0.4) (layer "F.SilkS") (stroke (width 0.1) (type solid)))
      (fp_line (start -0.35 0) (end -0.35 0.55) (layer "F.SilkS") (stroke (width 0.1) (type solid)))
      (fp_line (start -0.35 0) (end -0.35 -0.55) (layer "F.SilkS") (stroke (width 0.1) (type solid)))
      (fp_line (start -0.75 0) (end -0.35 0) (layer "F.SilkS") (stroke (width 0.1) (type solid)))
        `

    const front_smd_pads = `
      (pad "1" smd rect (at -1.65 0 ${p.r}) (size 0.9 1.2) (layers "F.Cu" "F.Paste" "F.Mask") ${p.to.str})
      (pad "2" smd rect (at 1.65 0 ${p.r}) (size 0.9 1.2) (layers "F.Cu" "F.Paste" "F.Mask") ${p.from.str})
        `
    const back_silk = `
      (fp_line (start 0.25 0) (end 0.75 0) (layer "B.SilkS") (stroke (width 0.1) (type solid)))
      (fp_line (start 0.25 0.4) (end -0.35 0) (layer "B.SilkS") (stroke (width 0.1) (type solid)))
      (fp_line (start 0.25 -0.4) (end 0.25 0.4) (layer "B.SilkS") (stroke (width 0.1) (type solid)))
      (fp_line (start -0.35 0) (end 0.25 -0.4) (layer "B.SilkS") (stroke (width 0.1) (type solid)))
      (fp_line (start -0.35 0) (end -0.35 0.55) (layer "B.SilkS") (stroke (width 0.1) (type solid)))
      (fp_line (start -0.35 0) (end -0.35 -0.55) (layer "B.SilkS") (stroke (width 0.1) (type solid)))
      (fp_line (start -0.75 0) (end -0.35 0) (layer "B.SilkS") (stroke (width 0.1) (type solid)))
        `
    const back_smd_pads = `
      (pad "1" smd rect (at -1.65 0 ${p.r}) (size 0.9 1.2) (layers "B.Cu" "B.Paste" "B.Mask") ${p.to.str})
      (pad "2" smd rect (at 1.65 0 ${p.r}) (size 0.9 1.2) (layers "B.Cu" "B.Paste" "B.Mask") ${p.from.str})
        `

    const reversible_tht_pads = `
      (pad "1" thru_hole rect (at -1.65 0 ${p.r}) (size 0.9 1.2) (drill 0.3) (layers "*.Cu" "*.Paste" "*.Mask") ${p.to.str})
      (pad "2" thru_hole rect (at 1.65 0 ${p.r}) (size 0.9 1.2) (drill 0.3) (layers "*.Cu" "*.Paste" "*.Mask") ${p.from.str})
        `

    const tht = `
      (pad "1" thru_hole rect (at -3.81 0 ${p.r}) (size 1.778 1.778) (drill 0.9906) (layers "*.Cu" "*.Mask") ${p.to.str})
      (pad "2" thru_hole circle (at 3.81 0 ${p.r}) (size 1.905 1.905) (drill 0.9906) (layers "*.Cu" "*.Mask") ${p.from.str})
        `

    const diode_3dmodel = `
      (model ${p.diode_3dmodel_filename}
          (offset (xyz ${p.diode_3dmodel_xyz_offset[0]} ${p.diode_3dmodel_xyz_offset[1]} ${p.diode_3dmodel_xyz_offset[2]}))
          (scale (xyz ${p.diode_3dmodel_xyz_scale[0]} ${p.diode_3dmodel_xyz_scale[1]} ${p.diode_3dmodel_xyz_scale[2]}))
          (rotate (xyz ${p.diode_3dmodel_xyz_rotation[0]} ${p.diode_3dmodel_xyz_rotation[1]} ${p.diode_3dmodel_xyz_rotation[2]})))
        `
    const standard_closing = `
    )
        `
    const tht_traces = `
    (segment
      (start ${p.eaxy(3.81, 0)})
      (end ${p.eaxy(1.65, 0)})
      (width ${p.trace_width})
      (layer "F.Cu")
      (net ${p.from.index})
    )
    (segment
      (start ${p.eaxy(3.81, 0)})
      (end ${p.eaxy(1.65, 0)})
      (width ${p.trace_width})
      (layer "B.Cu")
      (net ${p.from.index})
    )
    (segment
      (start ${p.eaxy(-1.65, 0)})
      (end ${p.eaxy(-3.81, 0)})
      (width ${p.trace_width})
      (layer "F.Cu")
      (net ${p.to.index})
    )
    (segment
      (start ${p.eaxy(-1.65, 0)})
      (end ${p.eaxy(-3.81, 0)})
      (width ${p.trace_width})
      (layer "B.Cu")
      (net ${p.to.index})
    )
    `

    const smd_pad_traces = `
    (segment
      (start ${p.eaxy(1.65, 0)})
      (end ${p.eaxy(1.65 + 1*p.trace_distance, 0)})
      (width ${p.trace_width})
      (layer "F.Cu")
      (net ${p.from.index})
    )
    (via
      (at ${p.eaxy(1.65 + 1*p.trace_distance, 0)})
      (size ${p.via_size})
      (drill ${p.via_drill})
      (layers "F.Cu" "B.Cu")
      (net ${p.from.index})
    )
    (segment
      (start ${p.eaxy(1.65 + 1*p.trace_distance, 0)})
      (end ${p.eaxy(1.65, 0)})
      (width ${p.trace_width})
      (layer "B.Cu")
      (net ${p.from.index})
    )
    (segment
      (start ${p.eaxy(-1.65, 0)})
      (end ${p.eaxy(-1.65 - 1*p.trace_distance, 0)})
      (width ${p.trace_width})
      (layer "F.Cu")
      (net ${p.to.index})
    )
    (via
      (at ${p.eaxy(-1.65 - 1*p.trace_distance, 0)})
      (size ${p.via_size})
      (drill ${p.via_drill})
      (layers "F.Cu" "B.Cu")
      (net ${p.to.index})
    )
    (segment
      (start ${p.eaxy(-1.65 - 1*p.trace_distance, 0)})
      (end ${p.eaxy(-1.65, 0)})
      (width ${p.trace_width})
      (layer "B.Cu")
      (net ${p.to.index})
    )
    `

    let final = standard_opening;

    if (p.side == "F" || p.reversible) {
      final += front_silk;
      if(!p.include_thru_hole_smd_pads) {
        final += front_smd_pads;
      }
    }
    if (p.side == "B" || p.reversible) {
      final += back_silk;
      if(!p.include_thru_hole_smd_pads) {
        final += back_smd_pads;
      }
    }
    if (p.include_tht) {
      final += tht;
    }
    if (p.reversible && p.include_thru_hole_smd_pads) {
      final += thru_hole_smd_pads_description;
      final += reversible_tht_pads;
    }

    if (p.diode_3dmodel_filename) {
      final += diode_3dmodel;
    }

    final += standard_closing;

    if (p.include_traces_vias) {
      if(p.include_tht) {
        final += tht_traces;
      } else if (!p.include_thru_hole_smd_pads) {
        final += smd_pad_traces;
      }
    }

    return final;
  }
}
