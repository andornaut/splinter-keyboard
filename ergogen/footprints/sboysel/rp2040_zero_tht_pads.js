module.exports = {
  params: {
    orientation: 'up',
    GP0: {type: 'net', value: 'GP0'},
    GP1: {type: 'net', value: 'GP1'},
    GP2: {type: 'net', value: 'GP2'},
    GP3: {type: 'net', value: 'GP3'},
    GP4: {type: 'net', value: 'GP4'},
    GP5: {type: 'net', value: 'GP5'},
    GP6: {type: 'net', value: 'GP6'},
    GP7: {type: 'net', value: 'GP7'},
    GP8: {type: 'net', value: 'GP8'},
    GP9: {type: 'net', value: 'GP9'},
    GP10: {type: 'net', value: 'GP10'},
    GP11: {type: 'net', value: 'GP11'},
    GP12: {type: 'net', value: 'GP12'},
    GP13: {type: 'net', value: 'GP13'},
    GP14: {type: 'net', value: 'GP14'},
    GP15: {type: 'net', value: 'GP15'},
    GP26: {type: 'net', value: 'GP26'},
    GP27: {type: 'net', value: 'GP27'},
    GP28: {type: 'net', value: 'GP28'},
    GP29: {type: 'net', value: 'GP29'},
    _3V3: {type: 'net', value: '3V3'},
    GND: {type: 'net', value: 'GND'},
    _5V: {type: 'net', value: '5V'}
  },
  body: p => {
    
    const standard = `
    (module rp2040_zero_tht_pads (layer F.Cu)
      ${p.at}
      (attr through_hole)
    `

    function pins(def_neg, def_pos) {
      return `
        (pad 1 thru_hole roundrect (at ${def_pos}7.62 -10.16 ${p.rot + 180}) (size 2.5 1.5) (drill 1 (offset ${def_neg}0.5 0)) (layers *.Cu *.Mask) (roundrect_rratio 0.2) ${p.GP0.str})
        (pad 2 thru_hole roundrect (at ${def_pos}7.62 -7.62 ${p.rot + 180}) (size 2.5 1.5) (drill 1 (offset ${def_neg}0.5 0)) (layers *.Cu *.Mask) (roundrect_rratio 0.2) ${p.GP1.str})
        (pad 3 thru_hole roundrect (at ${def_pos}7.62 -5.08 ${p.rot + 180}) (size 2.5 1.5) (drill 1 (offset ${def_neg}0.5 0)) (layers *.Cu *.Mask) (roundrect_rratio 0.2) ${p.GP2.str})
        (pad 4 thru_hole roundrect (at ${def_pos}7.62 -2.54 ${p.rot + 180}) (size 2.5 1.5) (drill 1 (offset ${def_neg}0.5 0)) (layers *.Cu *.Mask) (roundrect_rratio 0.2) ${p.GP3.str})
        (pad 5 thru_hole roundrect (at ${def_pos}7.62 0 ${p.rot + 180}) (size 2.5 1.5) (drill 1 (offset ${def_neg}0.5 0)) (layers *.Cu *.Mask) (roundrect_rratio 0.2) ${p.GP4.str})
        (pad 6 thru_hole roundrect (at ${def_pos}7.62 2.54 ${p.rot + 180}) (size 2.5 1.5) (drill 1 (offset ${def_neg}0.5 0)) (layers *.Cu *.Mask) (roundrect_rratio 0.2) ${p.GP5.str})
        (pad 7 thru_hole roundrect (at ${def_pos}7.62 5.08 ${p.rot + 180}) (size 2.5 1.5) (drill 1 (offset ${def_neg}0.5 0)) (layers *.Cu *.Mask) (roundrect_rratio 0.2) ${p.GP6.str})
        (pad 8 thru_hole roundrect (at ${def_pos}7.62 7.62 ${p.rot + 180}) (size 2.5 1.5) (drill 1 (offset ${def_neg}0.5 0)) (layers *.Cu *.Mask) (roundrect_rratio 0.2) ${p.GP7.str})
        (pad 9 thru_hole roundrect (at ${def_pos}7.62 10.16 ${p.rot + 180}) (size 2.5 1.5) (drill 1 (offset ${def_neg}0.5 0)) (layers *.Cu *.Mask) (roundrect_rratio 0.2) ${p.GP8.str})

        (pad 10 thru_hole roundrect (at ${def_pos}5.08 10.16 ${p.rot + 90}) (size 2.5 1.5) (drill 1 (offset -0.5 0)) (layers *.Cu *.Mask) (roundrect_rratio 0.2) ${p.GP9.str})
        (pad 11 thru_hole roundrect (at ${def_pos}2.54 10.16 ${p.rot + 90}) (size 2.5 1.5) (drill 1 (offset -0.5 0)) (layers *.Cu *.Mask) (roundrect_rratio 0.2) ${p.GP10.str})
        (pad 12 thru_hole roundrect (at 0 10.16 ${p.rot + 90}) (size 2.5 1.5) (drill 1 (offset -0.5 0)) (layers *.Cu *.Mask) (roundrect_rratio 0.2) ${p.GP11.str})
        (pad 13 thru_hole roundrect (at ${def_neg}2.54 10.16 ${p.rot + 90}) (size 2.5 1.5) (drill 1 (offset -0.5 0)) (layers *.Cu *.Mask) (roundrect_rratio 0.2) ${p.GP12.str})
        (pad 14 thru_hole roundrect (at ${def_neg}5.08 10.16 ${p.rot + 90}) (size 2.5 1.5) (drill 1 (offset -0.5 0)) (layers *.Cu *.Mask) (roundrect_rratio 0.2) ${p.GP13.str})
        
        (pad 15 thru_hole roundrect (at ${def_neg}7.62 10.16 ${p.rot}) (size 2.5 1.5) (drill 1 (offset ${def_neg}0.5 0)) (layers *.Cu *.Mask) (roundrect_rratio 0.2) ${p.GP14.str})
        (pad 16 thru_hole roundrect (at ${def_neg}7.62 7.62 ${p.rot}) (size 2.5 1.5) (drill 1 (offset ${def_neg}0.5 0)) (layers *.Cu *.Mask) (roundrect_rratio 0.2) ${p.GP15.str})
        (pad 17 thru_hole roundrect (at ${def_neg}7.62 5.08 ${p.rot}) (size 2.5 1.5) (drill 1 (offset ${def_neg}0.5 0)) (layers *.Cu *.Mask) (roundrect_rratio 0.2) ${p.GP26.str})
        (pad 18 thru_hole roundrect (at ${def_neg}7.62 2.54 ${p.rot}) (size 2.5 1.5) (drill 1 (offset ${def_neg}0.5 0)) (layers *.Cu *.Mask) (roundrect_rratio 0.2) ${p.GP27.str})
        (pad 19 thru_hole roundrect (at ${def_neg}7.62 0 ${p.rot}) (size 2.5 1.5) (drill 1 (offset ${def_neg}0.5 0)) (layers *.Cu *.Mask) (roundrect_rratio 0.2) ${p.GP28.str})
        (pad 20 thru_hole roundrect (at ${def_neg}7.62 -2.54 ${p.rot}) (size 2.5 1.5) (drill 1 (offset ${def_neg}0.5 0)) (layers *.Cu *.Mask) (roundrect_rratio 0.2) ${p.GP29.str})
        (pad 21 thru_hole roundrect (at ${def_neg}7.62 -5.08 ${p.rot}) (size 2.5 1.5) (drill 1 (offset ${def_neg}0.5 0)) (layers *.Cu *.Mask) (roundrect_rratio 0.2) ${p._3V3.str})
        (pad 22 thru_hole roundrect (at ${def_neg}7.62 -7.62 ${p.rot}) (size 2.5 1.5) (drill 1 (offset ${def_neg}0.5 0)) (layers *.Cu *.Mask) (roundrect_rratio 0.2) ${p.GND.str})
        (pad 23 thru_hole roundrect (at ${def_neg}7.62 -10.16 ${p.rot}) (size 2.5 1.5) (drill 1 (offset ${def_neg}0.5 0)) (layers *.Cu *.Mask) (roundrect_rratio 0.2) ${p._5V.str})
        
        (fp_circle (center ${def_neg}10.5 -10.16) (end ${def_neg}10.75 -10.16) (layer F.SilkS) (width 0.25) (fill solid))
        (fp_circle (center ${def_neg}10.5 -10.16) (end ${def_neg}10.75 -10.16) (layer B.SilkS) (width 0.25) (fill solid))

      `
    }

    if(p.orientation == 'up') {
      return `
        ${standard}
        ${pins('-', '')})
        `
    } else {
      return `
        ${standard}
        ${pins('', '-')})
        `
    }
  
  }
}
