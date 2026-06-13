module.exports = {
    params: {
        designator: 'D',
        from: {type: 'net', value: 'from'},
        to: {type: 'net', value: 'to'}
    },
    body: p => `
        (footprint "Diode_SMD:D_SOD-123FL"
            ${p.at}
            (descr "SOD-123FL flat-lead TVS/diode, hand-solder reversible pads (pin 1 = cathode / 'to' net)")
            (tags "SOD-123FL SOD-123F TVS ESD")
            (attr smd)
            (fp_text reference "${p.ref}" (at 0 -2 ${p.rot}) (layer "F.SilkS") ${p.ref_hide}
                (effects (font (size 0.8 0.8) (thickness 0.12)))
            )
            (fp_text value "SOD-123FL" (at 0 2 ${p.rot}) (layer "F.Fab") hide
                (effects (font (size 0.8 0.8) (thickness 0.12)))
            )

            (fp_line (start -1.35 -0.75) (end 1.35 -0.75) (stroke (width 0.1) (type solid)) (layer "F.Fab"))
            (fp_line (start 1.35 -0.75) (end 1.35 0.75) (stroke (width 0.1) (type solid)) (layer "F.Fab"))
            (fp_line (start 1.35 0.75) (end -1.35 0.75) (stroke (width 0.1) (type solid)) (layer "F.Fab"))
            (fp_line (start -1.35 -0.75) (end -1.35 0.75) (stroke (width 0.1) (type solid)) (layer "F.Fab"))
            (fp_line (start -0.85 -0.5) (end -0.85 0.5) (stroke (width 0.1) (type solid)) (layer "F.Fab"))
            (fp_line (start -2.05 -1.0) (end -2.05 1.0) (stroke (width 0.12) (type solid)) (layer "F.SilkS"))
            (fp_line (start 2.05 -1.0) (end 2.05 1.0) (stroke (width 0.12) (type solid)) (layer "F.SilkS"))
            (fp_line (start -2.2 -1.1) (end 2.2 -1.1) (stroke (width 0.05) (type solid)) (layer "F.CrtYd"))
            (fp_line (start 2.2 -1.1) (end 2.2 1.1) (stroke (width 0.05) (type solid)) (layer "F.CrtYd"))
            (fp_line (start 2.2 1.1) (end -2.2 1.1) (stroke (width 0.05) (type solid)) (layer "F.CrtYd"))
            (fp_line (start -2.2 1.1) (end -2.2 -1.1) (stroke (width 0.05) (type solid)) (layer "F.CrtYd"))

            (fp_line (start -1.35 -0.75) (end 1.35 -0.75) (stroke (width 0.1) (type solid)) (layer "B.Fab"))
            (fp_line (start 1.35 -0.75) (end 1.35 0.75) (stroke (width 0.1) (type solid)) (layer "B.Fab"))
            (fp_line (start 1.35 0.75) (end -1.35 0.75) (stroke (width 0.1) (type solid)) (layer "B.Fab"))
            (fp_line (start -1.35 -0.75) (end -1.35 0.75) (stroke (width 0.1) (type solid)) (layer "B.Fab"))
            (fp_line (start -0.85 -0.5) (end -0.85 0.5) (stroke (width 0.1) (type solid)) (layer "B.Fab"))
            (fp_line (start -2.05 -1.0) (end -2.05 1.0) (stroke (width 0.12) (type solid)) (layer "B.SilkS"))
            (fp_line (start 2.05 -1.0) (end 2.05 1.0) (stroke (width 0.12) (type solid)) (layer "B.SilkS"))
            (fp_line (start -2.2 -1.1) (end 2.2 -1.1) (stroke (width 0.05) (type solid)) (layer "B.CrtYd"))
            (fp_line (start 2.2 -1.1) (end 2.2 1.1) (stroke (width 0.05) (type solid)) (layer "B.CrtYd"))
            (fp_line (start 2.2 1.1) (end -2.2 1.1) (stroke (width 0.05) (type solid)) (layer "B.CrtYd"))
            (fp_line (start -2.2 1.1) (end -2.2 -1.1) (stroke (width 0.05) (type solid)) (layer "B.CrtYd"))

            (pad "1" thru_hole rect (at -1.65 0 ${p.rot}) (size 1.1 1.0) (drill 0.3) (layers *.Cu *.Mask) (zone_connect 2) ${p.to.str})
            (pad "2" thru_hole rect (at 1.65 0 ${p.rot}) (size 1.1 1.0) (drill 0.3) (layers *.Cu *.Mask) (zone_connect 2) ${p.from.str})
        )
    `
}
