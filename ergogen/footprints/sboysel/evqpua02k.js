module.exports = {
    params: {
        designator: 'R', // for reset
        side: 'F',
        silkscreen: true,
        from: undefined,
        to: undefined
    },
    body: p => {
      
      const silkscreen = `
        ${'' /* outline */}
        (fp_line (start -2.4000000000 2.3500000000) (end -2.4000000000 -2.3500000000) (layer ${p.side}.Fab) (width 0.15))
        (fp_line (start -2.4000000000 -2.3500000000) (end 2.4000000000 -2.3500000000) (layer ${p.side}.Fab) (width 0.15))
        (fp_line (start 2.4000000000 -2.3500000000) (end 2.4000000000 2.3500000000) (layer ${p.side}.Fab) (width 0.15))
        (fp_line (start 2.4000000000 2.3500000000) (end -2.4000000000 2.3500000000) (layer ${p.side}.Fab) (width 0.15))
        (fp_circle (center 3.9750000000 -1.3500000000) (end 4.1000000000 -1.3500000000) (layer ${p.side}.SilkS) (width 0.25))
        (fp_line (start 3.4250000000 -2.3750000000) (end 3.4250000000 -2.3750000000) (layer ${p.side}.CrtYd) (width 0.15))
        (fp_line (start 3.4250000000 -2.3750000000) (end -3.4250000000 -2.3750000000) (layer ${p.side}.CrtYd) (width 0.15))
        (fp_line (start -3.4250000000 -2.3750000000) (end -3.4250000000 2.3750000000) (layer ${p.side}.CrtYd) (width 0.15))
        (fp_line (start -3.4250000000 2.3750000000) (end 3.4250000000 2.3750000000) (layer ${p.side}.CrtYd) (width 0.15))
        (fp_line (start 3.4250000000 2.3750000000) (end 3.4250000000 -2.3750000000) (layer ${p.side}.CrtYd) (width 0.15))
        (fp_line (start -2.4000000000 -2.3500000000) (end 2.4000000000 -2.3500000000) (layer ${p.side}.SilkS) (width 0.15))
        (fp_line (start 2.4000000000 -2.2250000000) (end 2.4000000000 -2.3500000000) (layer ${p.side}.SilkS) (width 0.15))
        (fp_line (start -2.4000000000 -2.2250000000) (end -2.4000000000 -2.3500000000) (layer ${p.side}.SilkS) (width 0.15))
        (fp_line (start -2.4000000000 1.2500000000) (end -1.3000000000 1.2500000000) (layer ${p.side}.SilkS) (width 0.15))
        (fp_line (start 2.4000000000 1.2500000000) (end 1.3000000000 1.2500000000) (layer ${p.side}.SilkS) (width 0.15))
        (fp_line (start -1.3000000000 1.2500000000) (end -1.3000000000 2.3500000000) (layer ${p.side}.SilkS) (width 0.15))
        (fp_line (start 1.3000000000 1.2500000000) (end 1.3000000000 2.3500000000) (layer ${p.side}.SilkS) (width 0.15))
        (fp_line (start -1.3000000000 2.3500000000) (end 1.3000000000 2.3500000000) (layer ${p.side}.SilkS) (width 0.15))
        (fp_line (start -2.4000000000 1.2500000000) (end -2.4000000000 1.2250000000) (layer ${p.side}.SilkS) (width 0.15))
        (fp_line (start 2.4000000000 1.2500000000) (end 2.4000000000 1.2250000000) (layer ${p.side}.SilkS) (width 0.15))
      `

      return `
      (module Panasonic_Electronic_Components-EVQ-PUA02K-MFG (layer F.Cu) (tedit 5F8C6198)

          ${p.at /* parametric position */}
         
          ${p.silkscreen ? silkscreen : ''} 

          ${'' /* pins */}
          (pad 1 smd rect (at 2.6250000000 -1.3500000000 ${p.rot})(size 1.5500000000 1.0000000000)(layers ${p.side}.Cu ${p.side}.Paste ${p.side}.Mask) ${p.from.str})
          (pad 3 smd rect (at -2.6250000000 -1.3500000000 ${p.rot})(size 1.5500000000 1.0000000000)(layers ${p.side}.Cu ${p.side}.Paste ${p.side}.Mask) ${p.to.str})
          (pad 2 smd rect (at 2.6250000000 0.3500000000 ${p.rot})(size 1.5500000000 1.0000000000)(layers ${p.side}.Cu ${p.side}.Paste ${p.side}.Mask) ${p.from.str})
          (pad 4 smd rect (at -2.6250000000 0.3500000000 ${p.rot})(size 1.5500000000 1.0000000000)(layers ${p.side}.Cu ${p.side}.Paste ${p.side}.Mask) ${p.to.str})

      )

      `
    }


}
