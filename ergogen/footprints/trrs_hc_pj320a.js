// Copyright (c) 2023 Marco Massarelli
//
// SPDX-License-Identifier: MIT
//
// To view a copy of this license, visit https://opensource.org/license/mit/
//
// trrs_hc_pj320a: single-sided footprint for the HCTL HC-PJ-320A-4P-D 3.5mm TRRS jack
// (LCSC C5372851).
// Source: forked from ceoloide/trrs_pj320a.js by Marco Massarelli.
//
// Upstream divergence:
//  - Pad positions follow HCTL's recommended PCB layout for this part (datasheet on the
//    LCSC C5372851 page): pins at 3.2, 6.3, 10.4 and 11.5 from the body front, rows
//    4.5 apart, locating pegs at 1.6 and 8.6. Hole sizes stay upstream's (0.9 x 1.5
//    slots, 1.5 peg holes; HCTL draws 0.5 x 1.5 and 1.0), so the jack can shift a few
//    tenths before soldering: solder it pressed flat against the board.
//  - Pad names. ceoloide labels the 3-pin row SL, R2, TP and the lone pin R1. On this
//    jack the 3-pin row is R2, R1, T (mouth to back) and the lone pin is the sleeve,
//    confirmed on hardware by continuity from a plug.
//  - One pad per contact, and no reversible or symmetric mode. The symmetric mode puts
//    the tip and sleeve pins on two slotted pads of one net, so they cannot carry
//    different nets. Both halves of this board mount the jack on the same face, so one
//    pattern at the body centre is all that is needed.
//
// Layout, viewed from the side the jack mounts on, mouth at -y:
//
//      mouth
//   ____|____
//  |        (R2)    y 3.2
//  |        (R1)    y 6.3
//  |        (T)     y 10.4
//  |(S)_____|       y 11.5
//
// The 3-pin row sits on +x for side F. Side B is the mirror image (3-pin row on -x),
// because a part mounted on the back is seen mirrored from the front.
//
// Params:
//    side: F or B, the face the jack body mounts on.
//    T, R1, R2, S: nets for tip, ring 1, ring 2 and sleeve. Leave a net empty ('')
//      to leave that contact unconnected.

module.exports = {
  params: {
    designator: "TRRS",
    side: "F",
    T: { type: "net", value: "" },
    R1: { type: "net", value: "" },
    R2: { type: "net", value: "" },
    S: { type: "net", value: "" },
  },
  body: (p) => {
    const row = p.side === "F" ? 2.25 : -2.25; // the 3-pin row; the sleeve pin sits opposite
    const net = (n) => (n.name ? n.str : "");
    const pin = (name, x, y, n) =>
      `(pad "${name}" thru_hole oval (at ${x} ${y} ${p.r}) (size 1.6 2.2) (drill oval 0.9 1.5) (layers "*.Cu" "*.Mask") ${net(n)})`;
    return `
  (footprint "splinter:trrs_hc_pj320a"
    (layer "${p.side}.Cu")
    ${p.at}
    (property "Reference" "${p.ref}"
      (at 0 14.2 ${p.r})
      (layer "${p.side}.SilkS")
      ${p.ref_hide}
      (effects (font (size 1 1) (thickness 0.15)))
    )
    (fp_line (start 2.8 -2) (end -2.8 -2) (layer "Dwgs.User") (stroke (width 0.15) (type solid)))
    (fp_line (start -2.8 0) (end -2.8 -2) (layer "Dwgs.User") (stroke (width 0.15) (type solid)))
    (fp_line (start 2.8 0) (end 2.8 -2) (layer "Dwgs.User") (stroke (width 0.15) (type solid)))
    (fp_line (start -3.05 0) (end -3.05 12.1) (layer "Dwgs.User") (stroke (width 0.15) (type solid)))
    (fp_line (start 3.05 0) (end 3.05 12.1) (layer "Dwgs.User") (stroke (width 0.15) (type solid)))
    (fp_line (start 3.05 12.1) (end -3.05 12.1) (layer "Dwgs.User") (stroke (width 0.15) (type solid)))
    (fp_line (start 3.05 0) (end -3.05 0) (layer "Dwgs.User") (stroke (width 0.15) (type solid)))
    (pad "" np_thru_hole circle (at 0 8.6 ${p.r}) (size 1.5 1.5) (drill 1.5) (layers "*.Cu" "*.Mask"))
    (pad "" np_thru_hole circle (at 0 1.6 ${p.r}) (size 1.5 1.5) (drill 1.5) (layers "*.Cu" "*.Mask"))
    ${pin("R2", row, 3.2, p.R2)}
    ${pin("R1", row, 6.3, p.R1)}
    ${pin("T", row, 10.4, p.T)}
    ${pin("S", -row, 11.5, p.S)}
  )
    `;
  },
};
