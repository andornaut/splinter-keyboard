module.exports = {
    params: {
        designator: 'D',
        from: {type: 'net', value: 'from'},
        to: {type: 'net', value: 'to'}
    },
    body: p => `
        (footprint "Diode_SMD:D_SOD-323"
            ${p.at}
            (descr "SOD-323 ESD/TVS diode, hand-solder reversible pads (pin 1 = cathode / 'to' net)")
            (tags "SOD-323 TVS ESD")
            (attr smd)
            (fp_text reference "${p.ref}" (at 0 -1.6 ${p.rot}) (layer "F.SilkS") ${p.ref_hide}
                (effects (font (size 0.8 0.8) (thickness 0.12)))
            )
            (fp_text value "SOD-323" (at 0 1.6 ${p.rot}) (layer "F.Fab") hide
                (effects (font (size 0.8 0.8) (thickness 0.12)))
            )

            (fp_line (start -0.85 -0.63) (end 0.85 -0.63) (stroke (width 0.1) (type solid)) (layer "F.Fab"))
            (fp_line (start 0.85 -0.63) (end 0.85 0.63) (stroke (width 0.1) (type solid)) (layer "F.Fab"))
            (fp_line (start 0.85 0.63) (end -0.85 0.63) (stroke (width 0.1) (type solid)) (layer "F.Fab"))
            (fp_line (start -0.85 -0.63) (end -0.85 0.63) (stroke (width 0.1) (type solid)) (layer "F.Fab"))
            (fp_line (start -0.6 -0.4) (end -0.6 0.4) (stroke (width 0.1) (type solid)) (layer "F.Fab"))
            (fp_line (start -1.55 -0.85) (end -1.55 0.85) (stroke (width 0.12) (type solid)) (layer "F.SilkS"))
            (fp_line (start 1.55 -0.85) (end 1.55 0.85) (stroke (width 0.12) (type solid)) (layer "F.SilkS"))
            (fp_line (start -1.7 -0.9) (end 1.7 -0.9) (stroke (width 0.05) (type solid)) (layer "F.CrtYd"))
            (fp_line (start 1.7 -0.9) (end 1.7 0.9) (stroke (width 0.05) (type solid)) (layer "F.CrtYd"))
            (fp_line (start 1.7 0.9) (end -1.7 0.9) (stroke (width 0.05) (type solid)) (layer "F.CrtYd"))
            (fp_line (start -1.7 0.9) (end -1.7 -0.9) (stroke (width 0.05) (type solid)) (layer "F.CrtYd"))

            (fp_line (start -0.85 -0.63) (end 0.85 -0.63) (stroke (width 0.1) (type solid)) (layer "B.Fab"))
            (fp_line (start 0.85 -0.63) (end 0.85 0.63) (stroke (width 0.1) (type solid)) (layer "B.Fab"))
            (fp_line (start 0.85 0.63) (end -0.85 0.63) (stroke (width 0.1) (type solid)) (layer "B.Fab"))
            (fp_line (start -0.85 -0.63) (end -0.85 0.63) (stroke (width 0.1) (type solid)) (layer "B.Fab"))
            (fp_line (start -0.6 -0.4) (end -0.6 0.4) (stroke (width 0.1) (type solid)) (layer "B.Fab"))
            (fp_line (start -1.55 -0.85) (end -1.55 0.85) (stroke (width 0.12) (type solid)) (layer "B.SilkS"))
            (fp_line (start 1.55 -0.85) (end 1.55 0.85) (stroke (width 0.12) (type solid)) (layer "B.SilkS"))
            (fp_line (start -1.7 -0.9) (end 1.7 -0.9) (stroke (width 0.05) (type solid)) (layer "B.CrtYd"))
            (fp_line (start 1.7 -0.9) (end 1.7 0.9) (stroke (width 0.05) (type solid)) (layer "B.CrtYd"))
            (fp_line (start 1.7 0.9) (end -1.7 0.9) (stroke (width 0.05) (type solid)) (layer "B.CrtYd"))
            (fp_line (start -1.7 0.9) (end -1.7 -0.9) (stroke (width 0.05) (type solid)) (layer "B.CrtYd"))

            (pad "1" thru_hole rect (at -1.2 0 ${p.rot}) (size 0.9 0.9) (drill 0.3) (layers *.Cu *.Mask) (zone_connect 2) ${p.to.str})
            (pad "2" thru_hole rect (at 1.2 0 ${p.rot}) (size 0.9 0.9) (drill 0.3) (layers *.Cu *.Mask) (zone_connect 2) ${p.from.str})
        )
    `
}
