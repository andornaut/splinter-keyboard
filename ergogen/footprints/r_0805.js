// r_0805: single-component, single-side 0805 SMD chip footprint (resistor or
// other 2-pad 0805 passive). The module, pads, silk and fab all follow `side`,
// so a `side: B` placement is reported on the back by `kicad-cli pcb export pos`.
//
// Source: the 0805 land geometry and roundrect pads are derived from
//   infused-kim/smd_0805.js by @infused-kim,
//   https://github.com/infused-kim/kb_ergogen_fp. The optional trace/via routing
//   helper (the `include_traces_vias` option with its `trace_*` / `via_*` params
//   and segment/via emission) is adapted from ceoloide/diode_tht_sod123.js by
//   Marco Massarelli (@ceoloide), https://github.com/ceoloide/ergogen-footprints.
// License: CC-BY-NC-SA-4.0 (both upstream sources).
//
// Differs from infused-kim/smd_0805, which places pads on both copper sides and
// hardcodes its module layer to F.Cu (so a `side: B` part is still reported on
// the Top side by the position file): this footprint is single-side (only the
// chosen side gets pads/paste) and its module/reference layer follow `side`. It
// also drops the multi-component, reversible, and 3D-model options.
//
// Geometry: standard 0805 land, 1.4 x 1.025mm pads at 1.9mm center-to-center.
// Default orientation is vertical (pads stacked on the Y axis); rotate the
// footprint 90 degrees to lay it horizontal.
//
// Params:
//   side                  F or B, the side to place the footprint and designator on
//   designator            reference prefix (default R)
//   from / to             pad nets (non-polar, so the assignment is arbitrary)
//   include_traces_vias   if true, add a via just outside each pad joined by a
//                         short stub, exposing each pad's net on the opposite
//                         copper layer for routing (pads stay single-side for
//                         assembly). Default false.
//   via_in_pad            if true (with include_traces_vias), drop the stub and
//                         place the via at the pad center instead of outside it.
//                         Saves space but the via is an open (untented) hole in a
//                         reflow pad, so the assembler must fill-and-cap it (a paid
//                         JLCPCB option) or solder will wick down the barrel. Leave
//                         false for JLCPCB Economic PCBA. Default false.
//   trace_width           routing-helper trace width (default 0.25)
//   trace_distance        pad-edge-to-via gap along the part's long axis (default 1.2)
//   via_size / via_drill  routing-helper via dimensions (defaults 0.6 / 0.3)
module.exports = {
  params: {
    designator: 'R',
    side: 'B',
    // Optional vias for both-side routing (pads stay single-side for assembly):
    include_traces_vias: false, // if true, add a via just outside each pad
    via_in_pad: false,          // if true, put the via in the pad (no stub); needs filled-and-capped vias for reflow
    trace_width: 0.25,
    trace_distance: 1.2,        // pad-edge-to-via gap along the part's long axis
    via_size: 0.6,
    via_drill: 0.3,
    from: { type: 'net', value: 'from' },
    to: { type: 'net', value: 'to' }
  },
  body: p => {
    const s = p.side  // 'F' or 'B'
    const footprint = `
    (footprint "splinter:R_0805"
        (layer "${s}.Cu")
        ${p.at}
        (attr smd)
        (descr "0805 (2012 metric) SMD chip resistor, single-side. Custom footprint.")
        (tags "resistor R0805 0805 SMD")
        (property "Reference" "${p.ref}"
            (at 0 -1.5 ${p.r})
            (layer "${s}.SilkS")
            ${p.ref_hide}
            (effects (font (size 0.8 0.8) (thickness 0.12)))
        )
        (property "Value" "100R"
            (at 0 1.5 ${p.r})
            (layer "${s}.Fab")
            (hide yes)
            (effects (font (size 0.8 0.8) (thickness 0.12)))
        )
        (fp_line (start -0.625 -1.0) (end 0.625 -1.0) (stroke (width 0.1) (type solid)) (layer "${s}.Fab"))
        (fp_line (start 0.625 -1.0) (end 0.625 1.0) (stroke (width 0.1) (type solid)) (layer "${s}.Fab"))
        (fp_line (start 0.625 1.0) (end -0.625 1.0) (stroke (width 0.1) (type solid)) (layer "${s}.Fab"))
        (fp_line (start -0.625 1.0) (end -0.625 -1.0) (stroke (width 0.1) (type solid)) (layer "${s}.Fab"))
        (fp_line (start -0.95 -1.65) (end 0.95 -1.65) (stroke (width 0.05) (type solid)) (layer "${s}.CrtYd"))
        (fp_line (start 0.95 -1.65) (end 0.95 1.65) (stroke (width 0.05) (type solid)) (layer "${s}.CrtYd"))
        (fp_line (start 0.95 1.65) (end -0.95 1.65) (stroke (width 0.05) (type solid)) (layer "${s}.CrtYd"))
        (fp_line (start -0.95 1.65) (end -0.95 -1.65) (stroke (width 0.05) (type solid)) (layer "${s}.CrtYd"))
        (pad "1" smd roundrect (at 0 0.95 ${p.r}) (size 1.4 1.025) (layers "${s}.Cu" "${s}.Paste" "${s}.Mask") (roundrect_rratio 0.243902) ${p.from.str})
        (pad "2" smd roundrect (at 0 -0.95 ${p.r}) (size 1.4 1.025) (layers "${s}.Cu" "${s}.Paste" "${s}.Mask") (roundrect_rratio 0.243902) ${p.to.str})
    )
    `
    // Expose each pad's net on the opposite copper layer for routing. Either a
    // via in the pad center (via_in_pad, no stub), or a via just outside each pad
    // joined by a short stub (the safe-for-reflow default).
    const traces_vias = !p.include_traces_vias ? '' : p.via_in_pad ? `
    (via (at ${p.eaxy(0, 0.95)}) (size ${p.via_size}) (drill ${p.via_drill}) (layers "F.Cu" "B.Cu") (net ${p.from.index}))
    (via (at ${p.eaxy(0, -0.95)}) (size ${p.via_size}) (drill ${p.via_drill}) (layers "F.Cu" "B.Cu") (net ${p.to.index}))
    ` : `
    (segment (start ${p.eaxy(0, 0.95)}) (end ${p.eaxy(0, 0.95 + p.trace_distance)}) (width ${p.trace_width}) (layer "${s}.Cu") (net ${p.from.index}))
    (via (at ${p.eaxy(0, 0.95 + p.trace_distance)}) (size ${p.via_size}) (drill ${p.via_drill}) (layers "F.Cu" "B.Cu") (net ${p.from.index}))
    (segment (start ${p.eaxy(0, -0.95)}) (end ${p.eaxy(0, -0.95 - p.trace_distance)}) (width ${p.trace_width}) (layer "${s}.Cu") (net ${p.to.index}))
    (via (at ${p.eaxy(0, -0.95 - p.trace_distance)}) (size ${p.via_size}) (drill ${p.via_drill}) (layers "F.Cu" "B.Cu") (net ${p.to.index}))
    `
    return footprint + traces_vias
  }
}
