// https://raw.githubusercontent.com/SecretPocketCat/ergogen/main/src/footprints/blackpill_f4x1.js

module.exports = {
  params: {
    class: "MCU",
    orientation: "up",
    nets: {
      GND: "GND",
      P5V1: "P5V1",
      VDD24: "VDD24",
      B10: "B10",
      B2: "B2",
      B1: "B1",
      B0: "B0",
      A7: "A7",
      A6: "A6",
      A5: "A5",
      A4: "A4",
      A3: "A3",
      A2: "A2",
      A1: "A1",
      A0: "A0",
      R: "R",
      C15: "C15",
      C14: "C14",
      C13: "C13",
      VB: "VB",
      B12: "B12",
      B13: "B13",
      B14: "B14",
      B15: "B15",
      A8: "A8",
      A9: "A9",
      A10: "A10",
      A11: "A11",
      A12: "A12",
      A15: "A15",
      B3: "B3",
      B4: "B4",
      B5: "B5",
      B6: "B6",
      B7: "B7",
      B8: "B8",
      B9: "B9",
      P5V2: "P5V2",
      VDD48: "VDD48",
    },
  },
  body: (p) => {
    function standard(silk_layer) {
      // todo: USB overhang?
      // fix outline
      return `
        (module BlackPillF4x1 (layer F.Cu) (tedit 615F665A)
        ${p.at /* parametric position */}

        ${"" /* footprint reference */}
          (fp_text reference "${p.ref}" (at 0 0) (layer ${silk_layer}) ${p.ref_hide
        } (effects (font (size 1.27 1.27) (thickness 0.15))))
          (fp_text value "" (at 0 0) (layer ${silk_layer}) hide (effects (font (size 1.27 1.27) (thickness 0.15))))
      
        ${"" /* component outline */}
        (fp_line (start -11.375 -2.445) (end 11.375 -2.445) (layer ${silk_layer}) (width 0.12))
        (fp_line (start 11.375 -2.445) (end 11.375 50.705) (layer ${silk_layer}) (width 0.12))
        (fp_line (start 11.375 50.705) (end -11.375 50.705) (layer ${silk_layer}) (width 0.12))
        (fp_line (start -11.375 50.705) (end -11.375 -2.445) (layer ${silk_layer}) (width 0.12))
        (fp_line (start -8.95 -1.27) (end -6.29 -1.27) (layer ${silk_layer}) (width 0.12))
        (fp_line (start -6.29 -1.27) (end -6.29 49.59) (layer ${silk_layer}) (width 0.12))
        (fp_line (start -6.29 49.59) (end -8.95 49.59) (layer ${silk_layer}) (width 0.12))
        (fp_line (start -8.95 49.59) (end -8.95 -1.27) (layer ${silk_layer}) (width 0.12))
        (fp_line (start 6.35 -1.27) (end 8.89 -1.27) (layer ${silk_layer}) (width 0.12))
        (fp_line (start 8.89 -1.27) (end 8.89 49.53) (layer ${silk_layer}) (width 0.12))
        (fp_line (start 8.89 49.53) (end 6.35 49.53) (layer ${silk_layer}) (width 0.12))
        (fp_line (start 6.35 49.53) (end 6.35 -1.27) (layer ${silk_layer}) (width 0.12))
      `;
    }

    function pins(def_neg, def_pos, silk_layer) {
      return `
        ${"" /* extra top left B12 pin outline */}
        (fp_line (start ${def_pos}9.525 -0.5115) (end ${def_pos}9.525 -1.8415) (layer ${silk_layer}) (width 0.2))
        (fp_line (start ${def_pos}9.525 -1.8415) (end ${def_pos}8.195 -1.8415) (layer ${silk_layer}) (width 0.2))

        ${"" /* actual pins */}
        (pad 40 thru_hole circle (at ${def_pos}7.62 0 ${p.rot
        }) (size 1.7 1.7) (drill 1) (layers *.Cu *.Mask) ${p.nets.P5V1.str})
        (pad 39 thru_hole circle (at ${def_pos}7.62 2.54 ${p.rot
        }) (size 1.7 1.7) (drill 1) (layers *.Cu *.Mask) ${p.nets.GND.str})
        (pad 38 thru_hole circle (at ${def_pos}7.62 5.08 ${p.rot
        }) (size 1.7 1.7) (drill 1) (layers *.Cu *.Mask) ${p.nets.VDD24.str})
        (pad 37 thru_hole circle (at ${def_pos}7.62 7.62 ${p.rot
        }) (size 1.7 1.7) (drill 1) (layers *.Cu *.Mask) ${p.nets.B10.str})
        (pad 36 thru_hole circle (at ${def_pos}7.62 10.16 ${p.rot
        }) (size 1.7 1.7) (drill 1) (layers *.Cu *.Mask) ${p.nets.B2.str})
        (pad 35 thru_hole circle (at ${def_pos}7.62 12.7 ${p.rot
        }) (size 1.7 1.7) (drill 1) (layers *.Cu *.Mask) ${p.nets.B1.str})
        (pad 34 thru_hole circle (at ${def_pos}7.62 15.24 ${p.rot
        }) (size 1.7 1.7) (drill 1) (layers *.Cu *.Mask) ${p.nets.B0.str})
        (pad 33 thru_hole circle (at ${def_pos}7.62 17.78 ${p.rot
        }) (size 1.7 1.7) (drill 1) (layers *.Cu *.Mask) ${p.nets.A7.str})
        (pad 32 thru_hole circle (at ${def_pos}7.62 20.32 ${p.rot
        }) (size 1.7 1.7) (drill 1) (layers *.Cu *.Mask) ${p.nets.A6.str})
        (pad 31 thru_hole circle (at ${def_pos}7.62 22.86 ${p.rot
        }) (size 1.7 1.7) (drill 1) (layers *.Cu *.Mask) ${p.nets.A5.str})
        (pad 30 thru_hole circle (at ${def_pos}7.62 25.4 ${p.rot
        }) (size 1.7 1.7) (drill 1) (layers *.Cu *.Mask) ${p.nets.A4.str})
        (pad 29 thru_hole circle (at ${def_pos}7.62 27.94 ${p.rot
        }) (size 1.7 1.7) (drill 1) (layers *.Cu *.Mask) ${p.nets.A3.str})
        (pad 28 thru_hole circle (at ${def_pos}7.62 30.48 ${p.rot
        }) (size 1.7 1.7) (drill 1) (layers *.Cu *.Mask) ${p.nets.A2.str})
        (pad 27 thru_hole circle (at ${def_pos}7.62 33.02 ${p.rot
        }) (size 1.7 1.7) (drill 1) (layers *.Cu *.Mask) ${p.nets.A1.str})
        (pad 26 thru_hole circle (at ${def_pos}7.62 35.56 ${p.rot
        }) (size 1.7 1.7) (drill 1) (layers *.Cu *.Mask) ${p.nets.A0.str})
        (pad 25 thru_hole circle (at ${def_pos}7.62 38.1 ${p.rot
        }) (size 1.7 1.7) (drill 1) (layers *.Cu *.Mask) ${p.nets.R.str})
        (pad 24 thru_hole circle (at ${def_pos}7.62 40.64 ${p.rot
        }) (size 1.7 1.7) (drill 1) (layers *.Cu *.Mask) ${p.nets.C15.str})
        (pad 23 thru_hole circle (at ${def_pos}7.62 43.18 ${p.rot
        }) (size 1.7 1.7) (drill 1) (layers *.Cu *.Mask) ${p.nets.C14.str})
        (pad 22 thru_hole circle (at ${def_pos}7.62 45.72 ${p.rot
        }) (size 1.7 1.7) (drill 1) (layers *.Cu *.Mask) ${p.nets.C13.str})
        (pad 21 thru_hole circle (at ${def_pos}7.62 48.26 ${p.rot
        }) (size 1.7 1.7) (drill 1) (layers *.Cu *.Mask) ${p.nets.VB.str})
  
        (pad 1 thru_hole rect (at ${def_neg}7.62 0 ${p.rot
        }) (size 1.7 1.7) (drill 1) (layers *.Cu *.Mask) ${p.nets.B12.str})
        (pad 2 thru_hole circle (at ${def_neg}7.62 2.54 ${p.rot
        }) (size 1.7 1.7) (drill 1) (layers *.Cu *.Mask) ${p.nets.B13.str})
        (pad 3 thru_hole circle (at ${def_neg}7.62 5.08 ${p.rot
        }) (size 1.7 1.7) (drill 1) (layers *.Cu *.Mask) ${p.nets.B14.str})
        (pad 4 thru_hole circle (at ${def_neg}7.62 7.62 ${p.rot
        }) (size 1.7 1.7) (drill 1) (layers *.Cu *.Mask) ${p.nets.B15.str})
        (pad 5 thru_hole circle (at ${def_neg}7.62 10.16 ${p.rot
        }) (size 1.7 1.7) (drill 1) (layers *.Cu *.Mask) ${p.nets.A8.str})
        (pad 6 thru_hole circle (at ${def_neg}7.62 12.7 ${p.rot
        }) (size 1.7 1.7) (drill 1) (layers *.Cu *.Mask) ${p.nets.A9.str})
        (pad 7 thru_hole circle (at ${def_neg}7.62 15.24 ${p.rot
        }) (size 1.7 1.7) (drill 1) (layers *.Cu *.Mask) ${p.nets.A10.str})
        (pad 8 thru_hole circle (at ${def_neg}7.62 17.78 ${p.rot
        }) (size 1.7 1.7) (drill 1) (layers *.Cu *.Mask) ${p.nets.A11.str})
        (pad 9 thru_hole circle (at ${def_neg}7.62 20.32 ${p.rot
        }) (size 1.7 1.7) (drill 1) (layers *.Cu *.Mask) ${p.nets.A12.str})
        (pad 10 thru_hole circle (at ${def_neg}7.62 22.86 ${p.rot
        }) (size 1.7 1.7) (drill 1) (layers *.Cu *.Mask) ${p.nets.A15.str})
        (pad 11 thru_hole circle (at ${def_neg}7.62 25.4 ${p.rot
        }) (size 1.7 1.7) (drill 1) (layers *.Cu *.Mask) ${p.nets.B3.str})
        (pad 12 thru_hole circle (at ${def_neg}7.62 27.94 ${p.rot
        }) (size 1.7 1.7) (drill 1) (layers *.Cu *.Mask) ${p.nets.B4.str})
        (pad 13 thru_hole circle (at ${def_neg}7.62 30.48 ${p.rot
        }) (size 1.7 1.7) (drill 1) (layers *.Cu *.Mask) ${p.nets.B5.str})
        (pad 14 thru_hole circle (at ${def_neg}7.62 33.02 ${p.rot
        }) (size 1.7 1.7) (drill 1) (layers *.Cu *.Mask) ${p.nets.B6.str})
        (pad 15 thru_hole circle (at ${def_neg}7.62 35.56 ${p.rot
        }) (size 1.7 1.7) (drill 1) (layers *.Cu *.Mask) ${p.nets.B7.str})
        (pad 16 thru_hole circle (at ${def_neg}7.62 38.1 ${p.rot
        }) (size 1.7 1.7) (drill 1) (layers *.Cu *.Mask) ${p.nets.B8.str})
        (pad 17 thru_hole circle (at ${def_neg}7.62 40.64 ${p.rot
        }) (size 1.7 1.7) (drill 1) (layers *.Cu *.Mask) ${p.nets.B9.str})
        (pad 18 thru_hole circle (at ${def_neg}7.62 43.18 ${p.rot
        }) (size 1.7 1.7) (drill 1) (layers *.Cu *.Mask) ${p.nets.P5V2.str})
        (pad 19 thru_hole circle (at ${def_neg}7.62 45.72 ${p.rot
        }) (size 1.7 1.7) (drill 1) (layers *.Cu *.Mask) ${p.nets.GND.str})
        (pad 20 thru_hole circle (at ${def_neg}7.62 48.26 ${p.rot
        }) (size 1.7 1.7) (drill 1) (layers *.Cu *.Mask) ${p.nets.VDD48.str})
      `;
    }

    if (p.orientation == "down") {
      return `
        ${standard("B.SilkS")}
        ${pins("", "-", "B.SilkS")})
        `;
    } else {
      return `
        ${standard("F.SilkS")}
        ${pins("-", "", "F.SilkS")})
        `;
    }
  },
};
