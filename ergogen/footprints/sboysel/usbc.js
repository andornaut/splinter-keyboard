// https://www.lcsc.com/product-detail/USB-Type-C_Korean-Hroparts-Elec-TYPE-C-31-M-12_C165948.html
module.exports = {
  params: {
    side: 'F',
    reference: 'J1',
    A1_B12: {type: 'net', value: 'A1_B12'},
    A4_B9: {type: 'net', value: 'A4_B9'},
    A6: {type: 'net', value: 'A6'},
    B7: {type: 'net', value: 'B7'},
    A5: {type: 'net', value: 'A5'},
    B8: {type: 'net', value: 'B8'},
    A7: {type: 'net', value: 'A7'},
    B6: {type: 'net', value: 'B6'},
    A8: {type: 'net', value: 'A8'},
    B5: {type: 'net', value: 'B5'},
    B4_A9: {type: 'net', value: 'B4_A9'},
    B1_A12: {type: 'net', value: 'B1_A12'},
    S1: {type: 'net', value: 'S1'},
    S2: {type: 'net', value: 'S2'},
    S3: {type: 'net', value: 'S3'},
    S4: {type: 'net', value: 'S4'}
  },
  body: p => {
    const body = `
    (module "HRO_TYPE-C-31-M-12" (layer ${ p.side }.Cu)
      (descr "")
      (attr smd)
      ${p.at}
      (fp_text reference ${ p.reference } (at -1.85 -7.205 0) (layer ${ p.side }.Fab)
        (effects (font (size 1.0 1.0) (thickness 0.15)))
      )
      (fp_text value HRO_TYPE-C-31-M-12 (at 6.405 3.685 0) (layer ${ p.side }.Fab)
        (effects (font (size 1.0 1.0) (thickness 0.15)))
      )
      (pad A1_B12 smd rect (at -3.2 -4.75 ${ p.rot }) (size 0.6 1.14) (layers ${ p.side }.Cu ${ p.side }.Paste) ${ p.A1_B12 })
      (pad A4_B9 smd rect (at -2.4 -4.75 ${ p.rot }) (size 0.6 1.14) (layers ${ p.side }.Cu ${ p.side }.Paste) ${ p.A4_B9 })
      (pad A6 smd rect (at -0.25 -4.75 ${ p.rot }) (size 0.3 1.14) (layers ${ p.side }.Cu ${ p.side }.Paste) ${ p.A6 })
      (pad B7 smd rect (at -0.75 -4.75 ${ p.rot }) (size 0.3 1.14) (layers ${ p.side }.Cu ${ p.side }.Paste) ${ p.B7 })
      (pad A5 smd rect (at -1.25 -4.75 ${ p.rot }) (size 0.3 1.14) (layers ${ p.side }.Cu ${ p.side }.Paste) ${ p.A5 })
      (pad B8 smd rect (at -1.75 -4.75 ${ p.rot }) (size 0.3 1.14) (layers ${ p.side }.Cu ${ p.side }.Paste) ${ p.B8 })
      (pad A7 smd rect (at 0.25 -4.75 ${ p.rot }) (size 0.3 1.14) (layers ${ p.side }.Cu ${ p.side }.Paste) ${ p.A7 })
      (pad B6 smd rect (at 0.75 -4.75 ${ p.rot }) (size 0.3 1.14) (layers ${ p.side }.Cu ${ p.side }.Paste) ${ p.B6 })
      (pad A8 smd rect (at 1.25 -4.75 ${ p.rot }) (size 0.3 1.14) (layers ${ p.side }.Cu ${ p.side }.Paste) ${ p.A8 })
      (pad B5 smd rect (at 1.75 -4.75 ${ p.rot }) (size 0.3 1.14) (layers ${ p.side }.Cu ${ p.side }.Paste) ${ p.B5 })
      (pad B4_A9 smd rect (at 2.4 -4.75 ${ p.rot }) (size 0.6 1.14) (layers ${ p.side }.Cu ${ p.side }.Paste) ${ p.B4_A9 })
      (pad B1_A12 smd rect (at 3.2 -4.75 ${ p.rot }) (size 0.6 1.14) (layers ${ p.side }.Cu ${ p.side }.Paste) ${ p.B1_A12 })
      (pad None np_thru_hole circle (at -2.89 -3.68) (size 0.6 0.6) (drill 0.6) (layers *.Cu *.Mask))
      (pad None np_thru_hole circle (at 2.89 -3.68) (size 0.6 0.6) (drill 0.6) (layers *.Cu *.Mask))
      (pad S1 thru_hole oval (at -4.325 -4.17 ${ p.rot }) (size 0.9 2.0) (drill oval 0.6 1.7) (layers *.Cu *.Mask) (solder_mask_margin 0.102) ${ p.S1 })
      (pad S2 thru_hole oval (at 4.325 -4.17 ${ p.rot }) (size 0.9 2.0) (drill oval 0.6 1.7) (layers *.Cu *.Mask) (solder_mask_margin 0.102) ${ p.S2 })
      (pad S3 thru_hole oval (at -4.325 0.0 ${ p.rot }) (size 0.9 1.7) (drill oval 0.6 1.4) (layers *.Cu *.Mask) (solder_mask_margin 0.102) ${ p.S3 })
      (pad S4 thru_hole oval (at 4.325 0.0 ${ p.rot }) (size 0.9 1.7) (drill oval 0.6 1.4) (layers *.Cu *.Mask) (solder_mask_margin 0.102) ${ p.S4 })
      (fp_line (start -4.47 2.6) (end 4.47 2.6) (layer ${ p.side }.Fab) (width 0.127))
      (fp_line (start 4.47 2.6) (end 4.47 -4.75) (layer ${ p.side }.Fab) (width 0.127))
      (fp_line (start 4.47 -4.75) (end -4.47 -4.75) (layer ${ p.side }.Fab) (width 0.127))
      (fp_line (start -4.47 -4.75) (end -4.47 2.6) (layer ${ p.side }.Fab) (width 0.127))
      (fp_line (start 4.47 -2.85) (end 4.47 -1.17) (layer ${ p.side }.SilkS) (width 0.127))
      (fp_line (start 4.47 2.6) (end 4.47 1.17) (layer ${ p.side }.SilkS) (width 0.127))
      (fp_line (start -4.47 -2.85) (end -4.47 -1.17) (layer ${ p.side }.SilkS) (width 0.127))
      (fp_line (start -4.47 2.6) (end -4.47 1.17) (layer ${ p.side }.SilkS) (width 0.127))
      (fp_line (start -4.47 2.6) (end 4.47 2.6) (layer ${ p.side }.SilkS) (width 0.127))
      (fp_line (start -5.025 -5.57) (end -5.025 2.85) (layer ${ p.side }.CrtYd) (width 0.05))
      (fp_line (start -5.025 2.85) (end 5.025 2.85) (layer ${ p.side }.CrtYd) (width 0.05))
      (fp_line (start 5.025 2.85) (end 5.025 -5.57) (layer ${ p.side }.CrtYd) (width 0.05))
      (fp_line (start 5.025 -5.57) (end -5.025 -5.57) (layer ${ p.side }.CrtYd) (width 0.05))
      (fp_line (start -5.5 2.11) (end 9.0 2.11) (layer ${ p.side }.Fab) (width 0.127))
      (fp_text user "PCB EDGE" (at 5.2 1.9) (layer ${ p.side }.Fab)
        (effects (font (size 0.48 0.48) (thickness 0.15)))
      )
      (fp_circle (center -3.2 -6.0) (end -3.1 -6.0) (layer ${ p.side }.SilkS) (width 0.2))
      (fp_circle (center -3.2 -6.0) (end -3.1 -6.0) (layer ${ p.side }.Fab) (width 0.2))
      (fp_poly
        (pts
          (xy -1.95 -5.37)
          (xy -1.55 -5.37)
          (xy -1.55 -4.13)
          (xy -1.95 -4.13)
        ) (layer ${ p.side }.Mask) (width 0.01)
      )
      (fp_poly
        (pts
          (xy -1.45 -5.37)
          (xy -1.05 -5.37)
          (xy -1.05 -4.13)
          (xy -1.45 -4.13)
        ) (layer ${ p.side }.Mask) (width 0.01)
      )
      (fp_poly
        (pts
          (xy -0.95 -5.37)
          (xy -0.55 -5.37)
          (xy -0.55 -4.13)
          (xy -0.95 -4.13)
        ) (layer ${ p.side }.Mask) (width 0.01)
      )
      (fp_poly
        (pts
          (xy 1.55 -5.37)
          (xy 1.95 -5.37)
          (xy 1.95 -4.13)
          (xy 1.55 -4.13)
        ) (layer ${ p.side }.Mask) (width 0.01)
      )
      (fp_poly
        (pts
          (xy 1.05 -5.37)
          (xy 1.45 -5.37)
          (xy 1.45 -4.13)
          (xy 1.05 -4.13)
        ) (layer ${ p.side }.Mask) (width 0.01)
      )
      (fp_poly
        (pts
          (xy 0.55 -5.37)
          (xy 0.95 -5.37)
          (xy 0.95 -4.13)
          (xy 0.55 -4.13)
        ) (layer ${ p.side }.Mask) (width 0.01)
      )
      (fp_poly
        (pts
          (xy -0.45 -5.37)
          (xy -0.05 -5.37)
          (xy -0.05 -4.13)
          (xy -0.45 -4.13)
        ) (layer ${ p.side }.Mask) (width 0.01)
      )
      (fp_poly
        (pts
          (xy 0.05 -5.37)
          (xy 0.45 -5.37)
          (xy 0.45 -4.13)
          (xy 0.05 -4.13)
        ) (layer ${ p.side }.Mask) (width 0.01)
      )
      (fp_poly
        (pts
          (xy -3.55 -5.37)
          (xy -2.85 -5.37)
          (xy -2.85 -4.13)
          (xy -3.55 -4.13)
        ) (layer ${ p.side }.Mask) (width 0.01)
      )
      (fp_poly
        (pts
          (xy 2.85 -5.37)
          (xy 3.55 -5.37)
          (xy 3.55 -4.13)
          (xy 2.85 -4.13)
        ) (layer ${ p.side }.Mask) (width 0.01)
      )
      (fp_poly
        (pts
          (xy -2.75 -5.37)
          (xy -2.05 -5.37)
          (xy -2.05 -4.13)
          (xy -2.75 -4.13)
        ) (layer ${ p.side }.Mask) (width 0.01)
      )
      (fp_poly
        (pts
          (xy 2.05 -5.37)
          (xy 2.75 -5.37)
          (xy 2.75 -4.13)
          (xy 2.05 -4.13)
        ) (layer ${ p.side }.Mask) (width 0.01)
      )
    )    
    `
    return body
  }
}
