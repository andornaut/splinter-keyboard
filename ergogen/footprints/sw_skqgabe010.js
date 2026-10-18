// sw_skqgabe010: ALPS SKQGABE010 5.2mm SMD tact switch (LCSC C115351), the MCU reset
// button. The module follows `side`, so a `side: B` placement is reported on the back
// by `kicad-cli pcb export pos`.
//
// Source: forked from ergogen's built-in button.js (MIT), https://github.com/ergogen/ergogen.
//
// Differs from upstream button.js in one way: the module and reference layers follow
// `side` instead of being fixed to F. With `side: B` upstream drew its pads on the back
// but reported the part on the Top side, so JLCPCB single-side (Economic) assembly would
// try to place it on the bare front.
//
// Geometry: unchanged from upstream, and identical at 0 degrees to the EasyEDA footprint
// JLCPCB assembles C115351 from (KEY-SMD_4P-L5.2-W5.2-P3.70-LS6.4): pads at x +-3.1,
// y +-1.85. Each row of pads is one terminal pair (`from` on the -y row, `to` on +y), and
// pressing joins the rows, so 0 and 180 degrees are equivalent.
//
// Params:
//   side        F or B, the side to place the footprint and designator on
//   designator  reference prefix (default B)
//   from / to   nets for the -y and +y pad rows

module.exports = {
  params: {
    designator: "B", // for Button
    side: "F",
    from: undefined,
    to: undefined,
  },
  body: (p) => `
    (module E73:SW_TACT_ALPS_SKQGABE010 (layer ${p.side}.Cu) (tstamp 5BF2CC94)
        (descr "ALPS SKQGABE010 5.2mm SMD tact switch")
        (tags "SPST Tactile Switch")
        ${p.at /* parametric position */}
        (fp_text reference "${p.ref}" (at 0 0) (layer ${p.side}.SilkS) ${p.ref_hide} (effects (font (size 1.27 1.27) (thickness 0.15))))
        (fp_text value "" (at 0 0) (layer ${p.side}.SilkS) hide (effects (font (size 1.27 1.27) (thickness 0.15))))
        (fp_line (start 2.75 1.25) (end 1.25 2.75) (layer ${p.side}.SilkS) (width 0.15))
        (fp_line (start 2.75 -1.25) (end 1.25 -2.75) (layer ${p.side}.SilkS) (width 0.15))
        (fp_line (start 2.75 -1.25) (end 2.75 1.25) (layer ${p.side}.SilkS) (width 0.15))
        (fp_line (start -1.25 2.75) (end 1.25 2.75) (layer ${p.side}.SilkS) (width 0.15))
        (fp_line (start -1.25 -2.75) (end 1.25 -2.75) (layer ${p.side}.SilkS) (width 0.15))
        (fp_line (start -2.75 1.25) (end -1.25 2.75) (layer ${p.side}.SilkS) (width 0.15))
        (fp_line (start -2.75 -1.25) (end -1.25 -2.75) (layer ${p.side}.SilkS) (width 0.15))
        (fp_line (start -2.75 -1.25) (end -2.75 1.25) (layer ${p.side}.SilkS) (width 0.15))
        (pad 1 smd rect (at -3.1 -1.85 ${p.r}) (size 1.8 1.1) (layers ${p.side}.Cu ${p.side}.Paste ${p.side}.Mask) ${p.from})
        (pad 1 smd rect (at 3.1 -1.85 ${p.r}) (size 1.8 1.1) (layers ${p.side}.Cu ${p.side}.Paste ${p.side}.Mask) ${p.from})
        (pad 2 smd rect (at -3.1 1.85 ${p.r}) (size 1.8 1.1) (layers ${p.side}.Cu ${p.side}.Paste ${p.side}.Mask) ${p.to})
        (pad 2 smd rect (at 3.1 1.85 ${p.r}) (size 1.8 1.1) (layers ${p.side}.Cu ${p.side}.Paste ${p.side}.Mask) ${p.to})
    )
    `,
};
