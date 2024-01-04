// https://www.te.com/usa-en/product-BAT-HLD-001.html
// https://www.snapeda.com/parts/BAT-HLD-001/Linx%20Technologies%20Inc./view-part/
module.exports = {
    params: {
        pos: undefined,
        neg: undefined
    },
    body: p => `

    (module BAT_BAT-HLD-001 (layer F.Cu) (tedit 64E035EE)
      (attr through_hole)
      ${p.at /* parametric position */}
      (pad N1 thru_hole circle (at 0.0 0.0) (size 17.8 17.8) (layers *.Cu *.Mask) ${p.neg.str})
      (pad P1 thru_hole rect (at -11.45 0.0 ${p.rot}) (size 2.5 5.1) (layers *.Cu *.Mask *.Paste) ${p.pos.str})
      (pad P2 thru_hole rect (at 11.45 0.0 ${p.rot}) (size 2.5 5.1) (layers *.Cu *.Mask *.Paste) ${p.pos.str})
      (fp_line (start -10.55 -7.55) (end 10.55 -7.55) (layer F.Fab) (width 0.127))
      (fp_line (start 10.55 -7.55) (end 10.55 7.95) (layer F.Fab) (width 0.127))
      (fp_line (start 10.55 7.95) (end 5.5 7.95) (layer F.Fab) (width 0.127))
      (fp_arc (start 3.00578623502e-06 14.7314017786) (end 0.0 6.0) (angle 39.0435) (layer F.Fab) (width 0.127))
      (fp_arc (start -3.00578623502e-06 14.7314017786) (end -5.5 7.95) (angle 39.0435) (layer F.Fab) (width 0.127))
      (fp_line (start -5.5 7.95) (end -10.55 7.95) (layer F.Fab) (width 0.127))
      (fp_line (start -10.55 7.95) (end -10.55 -7.55) (layer F.Fab) (width 0.127))
      (fp_line (start -10.55 -2.87) (end -10.55 -7.55) (layer F.SilkS) (width 0.127))
      (fp_line (start -10.55 -7.55) (end -6.0 -7.55) (layer F.SilkS) (width 0.127))
      (fp_line (start 6.0 -7.55) (end 10.55 -7.55) (layer F.SilkS) (width 0.127))
      (fp_line (start 10.55 -7.55) (end 10.55 -2.87) (layer F.SilkS) (width 0.127))
      (fp_line (start -10.55 2.87) (end -10.55 7.95) (layer F.SilkS) (width 0.127))
      (fp_line (start -10.55 7.95) (end -5.5 7.95) (layer F.SilkS) (width 0.127))
      (fp_line (start 5.5 7.95) (end 10.55 7.95) (layer F.SilkS) (width 0.127))
      (fp_line (start 10.55 7.95) (end 10.55 2.87) (layer F.SilkS) (width 0.127))
      (fp_line (start -12.95 -9.15) (end 12.95 -9.15) (layer F.CrtYd) (width 0.05))
      (fp_line (start 12.95 -9.15) (end 12.95 9.15) (layer F.CrtYd) (width 0.05))
      (fp_line (start 12.95 9.15) (end -12.95 9.15) (layer F.CrtYd) (width 0.05))
      (fp_line (start -12.95 9.15) (end -12.95 -9.15) (layer F.CrtYd) (width 0.05))
    )
    
    `
}
