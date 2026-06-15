// sod-123fl: single-side, side-aware SMD footprint for the SOD-123FL flat-lead
// package (e.g. the SMF5.0CA TVS, or SOD-123F diodes). The module, pads, silk
// and fab all follow `side`, so a `side: B` placement is reported on the back by
// `kicad-cli pcb export pos`.
//
// Source: the optional trace/via routing helper (the `include_traces_vias`
//   option with its `trace_*` / `via_*` params and segment/via emission) is
//   adapted from ceoloide/diode_tht_sod123.js by Marco Massarelli (@ceoloide),
//   https://github.com/ceoloide/ergogen-footprints. The land geometry is
//   original (see Geometry below).
// License: CC-BY-NC-SA-4.0 (inherited from the adapted ceoloide code).
//
// Geometry: SOD-123FL land for the Littelfuse SMF5.0CA. Body outline 3.0 x
// 1.85mm matches that datasheet's package (body length 2.70-3.10mm, width
// 1.70-2.00mm, lead-to-lead span 3.50-3.90mm). 1.2 x 1.2mm SMD pads at 3.0mm
// center-to-center: an oversized hand-solder land that still reflows fine.
//
// Params:
//   side                  F or B, the side to place the footprint and designator on
//   designator            reference prefix (default D)
//   from / to             pad nets. Pad "A" = anode = `from`; pad "K" = cathode
//                         (banded end) = `to`. Bidirectional parts (e.g. a TVS)
//                         ignore polarity.
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
        designator: 'D',                       // reference prefix -> D<n>
        side: 'B',                             // single-side placement: F or B
        // Optional vias for both-side routing (pads stay single-side for assembly):
        include_traces_vias: false,            // if true, add a via just outside each pad
        via_in_pad: false,                     // if true, put the via in the pad (no stub); needs filled-and-capped vias for reflow
        trace_width: 0.25,
        trace_distance: 1.2,                   // pad-edge-to-via gap along the part's long axis
        via_size: 0.6,
        via_drill: 0.3,
        from: { type: 'net', value: 'from' },    // anode  -> pad "A"
        to: { type: 'net', value: 'to' }         // cathode (banded end) -> pad "K"
    },
    body: p => {
        const s = p.side  // 'F' or 'B'
        const footprint = `
        (footprint "splinter:D_SOD-123FL"
            (layer "${s}.Cu")
            ${p.at}
            (attr smd)
            (descr "SOD-123FL flat-lead TVS/diode, SMD single-side (pin 1 = cathode / 'to' net). Custom footprint, not a KiCad stock part. Body 3.0x1.85mm, 1.2mm pads at 3.0mm pitch, sized for the Littelfuse SMF5.0CA (SOD-123FL).")
            (tags "SOD-123FL SOD-123F TVS ESD SMD")
            (property "Reference" "${p.ref}" (at 0 -1.6 ${p.r}) (layer "${s}.SilkS") ${p.ref_hide}
                (effects (font (size 0.8 0.8) (thickness 0.12)))
            )
            (property "Value" "SMF5.0CA" (at 0 1.6 ${p.r}) (layer "${s}.Fab") (hide yes)
                (effects (font (size 0.8 0.8) (thickness 0.12)))
            )

            ${''/* Body outline 3.0 x 1.85mm, cathode bar on the K side, courtyard */}
            (fp_line (start -1.5 -0.925) (end 1.5 -0.925) (stroke (width 0.1) (type solid)) (layer "${s}.Fab"))
            (fp_line (start 1.5 -0.925) (end 1.5 0.925) (stroke (width 0.1) (type solid)) (layer "${s}.Fab"))
            (fp_line (start 1.5 0.925) (end -1.5 0.925) (stroke (width 0.1) (type solid)) (layer "${s}.Fab"))
            (fp_line (start -1.5 -0.925) (end -1.5 0.925) (stroke (width 0.1) (type solid)) (layer "${s}.Fab"))
            (fp_line (start -0.95 -0.6) (end -0.95 0.6) (stroke (width 0.1) (type solid)) (layer "${s}.Fab"))
            (fp_line (start -1.5 -1.0) (end 0.9 -1.0) (stroke (width 0.12) (type solid)) (layer "${s}.SilkS"))
            (fp_line (start -1.5 1.0) (end 0.9 1.0) (stroke (width 0.12) (type solid)) (layer "${s}.SilkS"))
            (fp_line (start -1.5 -1.0) (end -1.5 1.0) (stroke (width 0.12) (type solid)) (layer "${s}.SilkS"))
            (fp_line (start -2.5 -1.15) (end 2.5 -1.15) (stroke (width 0.05) (type solid)) (layer "${s}.CrtYd"))
            (fp_line (start 2.5 -1.15) (end 2.5 1.15) (stroke (width 0.05) (type solid)) (layer "${s}.CrtYd"))
            (fp_line (start 2.5 1.15) (end -2.5 1.15) (stroke (width 0.05) (type solid)) (layer "${s}.CrtYd"))
            (fp_line (start -2.5 1.15) (end -2.5 -1.15) (stroke (width 0.05) (type solid)) (layer "${s}.CrtYd"))

            ${''/* Pad "K" = cathode (banded end) = 'to' net; pad "A" = anode = 'from' net. */}
            (pad "K" smd roundrect (at -1.5 0 ${p.r}) (size 1.2 1.2) (layers "${s}.Cu" "${s}.Paste" "${s}.Mask") (roundrect_rratio 0.1) (zone_connect 2) ${p.to.str})
            (pad "A" smd roundrect (at 1.5 0 ${p.r}) (size 1.2 1.2) (layers "${s}.Cu" "${s}.Paste" "${s}.Mask") (roundrect_rratio 0.1) (zone_connect 2) ${p.from.str})
        )
        `
        // Expose each pad's net on the opposite copper layer for routing. Either a
        // via in the pad center (via_in_pad, no stub), or a via just outside each
        // pad joined by a short stub (the safe-for-reflow default).
        const traces_vias = !p.include_traces_vias ? '' : p.via_in_pad ? `
        (via (at ${p.eaxy(1.5, 0)}) (size ${p.via_size}) (drill ${p.via_drill}) (layers "F.Cu" "B.Cu") (net ${p.from.index}))
        (via (at ${p.eaxy(-1.5, 0)}) (size ${p.via_size}) (drill ${p.via_drill}) (layers "F.Cu" "B.Cu") (net ${p.to.index}))
        ` : `
        (segment (start ${p.eaxy(1.5, 0)}) (end ${p.eaxy(1.5 + p.trace_distance, 0)}) (width ${p.trace_width}) (layer "${s}.Cu") (net ${p.from.index}))
        (via (at ${p.eaxy(1.5 + p.trace_distance, 0)}) (size ${p.via_size}) (drill ${p.via_drill}) (layers "F.Cu" "B.Cu") (net ${p.from.index}))
        (segment (start ${p.eaxy(-1.5, 0)}) (end ${p.eaxy(-1.5 - p.trace_distance, 0)}) (width ${p.trace_width}) (layer "${s}.Cu") (net ${p.to.index}))
        (via (at ${p.eaxy(-1.5 - p.trace_distance, 0)}) (size ${p.via_size}) (drill ${p.via_drill}) (layers "F.Cu" "B.Cu") (net ${p.to.index}))
        `
        return footprint + traces_vias
    }
}
