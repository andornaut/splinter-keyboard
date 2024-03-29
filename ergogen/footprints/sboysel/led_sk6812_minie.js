module.exports = {
    params: {
        designator: 'LED',
        side: 'F',
        DIN: undefined,
        DOUT: undefined,
        VCC: 'VCC',
        GND: 'GND'
    },
    body: p => `
        (module "SK6812-MINI-E" (layer F.Cu) (tedit 5ECEB660)
          
          ${p.at /* parametric position */}

          ${'' /* footprint reference */}

          (fp_text reference "${p.ref}" (at 0 2.1 unlocked) (layer ${p.side}.SilkS) ${p.ref.hide}
            (effects (font (size 0.7 0.7) (thickness 0.15)))
          )
          (fp_text value "SK6812-MINI-E" (at 0 -0.5 unlocked) (layer ${p.side}.SilkS) hide
            (effects (font (size 1 1) (thickness 0.15)))
          )
          (fp_poly (pts (xy 2.8 -1.4) (xy 2.2 -1.4) (xy 2.2 -2)) (layer F.SilkS) (width 0.1))
          (fp_line (start 1.6 -1.4) (end 1.6 1.4) (layer Cmts.User) (width 0.12))
          (fp_line (start 1.6 1.4) (end -1.6 1.4) (layer Cmts.User) (width 0.12))
          (fp_line (start -1.6 1.4) (end -1.6 -1.4) (layer Cmts.User) (width 0.12))
          (fp_line (start -1.6 -1.4) (end 1.6 -1.4) (layer Cmts.User) (width 0.12))
          (fp_line (start 1.7 -1.5) (end 1.7 1.5) (layer Edge.Cuts) (width 0.12))
          (fp_line (start 1.7 1.5) (end -1.7 1.5) (layer Edge.Cuts) (width 0.12))
          (fp_line (start -1.7 1.5) (end -1.7 -1.5) (layer Edge.Cuts) (width 0.12))
          (fp_line (start -1.7 -1.5) (end 1.7 -1.5) (layer Edge.Cuts) (width 0.12))
          (pad 1 smd rect (at -2.55 0.75 ${p.rot}) (size 1.7 0.82) (layers ${p.side}.Cu ${p.side}.Paste ${p.side}.Mask))
          (pad 2 smd rect (at -2.55 -0.75 ${p.rot}) (size 1.7 0.82) (layers ${p.side}.Cu ${p.side}.Paste ${p.side}.Mask))
          (pad 4 smd rect (at 2.55 0.75 ${p.rot}) (size 1.7 0.82) (layers ${p.side}.Cu ${p.side}.Paste ${p.side}.Mask))
          (pad 3 smd roundrect (at 2.55 -0.75 ${p.rot}) (size 1.7 0.82) (layers ${p.side}.Cu ${p.side}.Paste ${p.side}.Mask) (roundrect_rratio 0.25))
        )    
    `
}
