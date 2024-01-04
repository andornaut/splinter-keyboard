module.exports = {
    params: {
        designator: 'T', // for Toggle
        side: 'F',
        silkscreen: true, 
        from: undefined,
        to: undefined
    },
    body: p => {

        const left = p.side == 'F' ? '-' : ''
        const right = p.side == 'F' ? '' : '-'

        const silkscreen = `
            ${'' /* outline */}
            (fp_line (start 1.95 -1.35) (end -1.95 -1.35) (layer ${p.side}.SilkS) (width 0.15))
            (fp_line (start 0 -1.35) (end -3.3 -1.35) (layer ${p.side}.SilkS) (width 0.15))
            (fp_line (start -3.3 -1.35) (end -3.3 1.5) (layer ${p.side}.SilkS) (width 0.15))
            (fp_line (start -3.3 1.5) (end 3.3 1.5) (layer ${p.side}.SilkS) (width 0.15))
            (fp_line (start 3.3 1.5) (end 3.3 -1.35) (layer ${p.side}.SilkS) (width 0.15))
            (fp_line (start 0 -1.35) (end 3.3 -1.35) (layer ${p.side}.SilkS) (width 0.15))
        `

        return `
        
        (module E73:SPDT_C128955 (layer F.Cu) (tstamp 5BF2CC3C)

            ${p.at /* parametric position */}
            
            ${p.silkscreen ? silkscreen : ''} 
            
            ${'' /* extra indicator for the slider */}
            (fp_line (start -1.95 -3.85) (end 1.95 -3.85) (layer Dwgs.User) (width 0.15))
            (fp_line (start 1.95 -3.85) (end 1.95 -1.35) (layer Dwgs.User) (width 0.15))
            (fp_line (start -1.95 -1.35) (end -1.95 -3.85) (layer Dwgs.User) (width 0.15))

            ${'' /* pins */}

            (pad 1 smd rect (at ${right}2.25 2.075 ${p.rot}) (size 0.9 1.25) (layers ${p.side}.Cu ${p.side}.Paste ${p.side}.Mask))
            (pad 2 smd rect (at ${left}0.75 2.075 ${p.rot}) (size 0.9 1.25) (layers ${p.side}.Cu ${p.side}.Paste ${p.side}.Mask) ${p.from.str})
            (pad 3 smd rect (at ${left}2.25 2.075 ${p.rot}) (size 0.9 1.25) (layers ${p.side}.Cu ${p.side}.Paste ${p.side}.Mask) ${p.to.str})
            
            ${'' /* side mounts */}
            (pad "" smd rect (at 3.7 -1.1 ${p.r}) (size 0.9 0.9) (layers ${p.side}.Cu ${p.side}.Paste ${p.side}.Mask))
            (pad "" smd rect (at 3.7 1.1 ${p.r}) (size 0.9 0.9) (layers ${p.side}.Cu ${p.side}.Paste ${p.side}.Mask))
            (pad "" smd rect (at -3.7 1.1 ${p.r}) (size 0.9 0.9) (layers ${p.side}.Cu ${p.side}.Paste ${p.side}.Mask))
            (pad "" smd rect (at -3.7 -1.1 ${p.r}) (size 0.9 0.9) (layers ${p.side}.Cu ${p.side}.Paste ${p.side}.Mask))
        )
        
        `
    }
}
