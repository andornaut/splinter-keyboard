module.exports = {
    params: {
        designator: 'R',
        from: {type: 'net', value: 'from'},
        to: {type: 'net', value: 'to'}
    },
    body: p => `
        (footprint "Resistor_SMD:R_0603_1608Metric"
            ${p.at}
            (descr "Resistor 0603 (1608 Metric), hand-solder reversible pads")
            (tags "0603 1608 resistor")
            (attr smd)
            (fp_text reference "${p.ref}" (at 0 -1.5 ${p.rot}) (layer "F.SilkS") ${p.ref_hide}
                (effects (font (size 0.8 0.8) (thickness 0.12)))
            )
            (fp_text value "0603" (at 0 1.5 ${p.rot}) (layer "F.Fab") hide
                (effects (font (size 0.8 0.8) (thickness 0.12)))
            )

            (fp_line (start -0.8 -0.4) (end 0.8 -0.4) (stroke (width 0.1) (type solid)) (layer "F.Fab"))
            (fp_line (start 0.8 -0.4) (end 0.8 0.4) (stroke (width 0.1) (type solid)) (layer "F.Fab"))
            (fp_line (start 0.8 0.4) (end -0.8 0.4) (stroke (width 0.1) (type solid)) (layer "F.Fab"))
            (fp_line (start -0.8 -0.4) (end -0.8 0.4) (stroke (width 0.1) (type solid)) (layer "F.Fab"))
            (fp_line (start -1.6 -0.6) (end -1.6 0.6) (stroke (width 0.05) (type solid)) (layer "F.CrtYd"))
            (fp_line (start 1.6 -0.6) (end 1.6 0.6) (stroke (width 0.05) (type solid)) (layer "F.CrtYd"))
            (fp_line (start -1.6 -0.6) (end 1.6 -0.6) (stroke (width 0.05) (type solid)) (layer "F.CrtYd"))
            (fp_line (start -1.6 0.6) (end 1.6 0.6) (stroke (width 0.05) (type solid)) (layer "F.CrtYd"))

            (fp_line (start -0.8 -0.4) (end 0.8 -0.4) (stroke (width 0.1) (type solid)) (layer "B.Fab"))
            (fp_line (start 0.8 -0.4) (end 0.8 0.4) (stroke (width 0.1) (type solid)) (layer "B.Fab"))
            (fp_line (start 0.8 0.4) (end -0.8 0.4) (stroke (width 0.1) (type solid)) (layer "B.Fab"))
            (fp_line (start -0.8 -0.4) (end -0.8 0.4) (stroke (width 0.1) (type solid)) (layer "B.Fab"))
            (fp_line (start -1.6 -0.6) (end -1.6 0.6) (stroke (width 0.05) (type solid)) (layer "B.CrtYd"))
            (fp_line (start 1.6 -0.6) (end 1.6 0.6) (stroke (width 0.05) (type solid)) (layer "B.CrtYd"))
            (fp_line (start -1.6 -0.6) (end 1.6 -0.6) (stroke (width 0.05) (type solid)) (layer "B.CrtYd"))
            (fp_line (start -1.6 0.6) (end 1.6 0.6) (stroke (width 0.05) (type solid)) (layer "B.CrtYd"))

            (pad "1" thru_hole rect (at -0.825 0 ${p.rot}) (size 0.9 0.95) (drill 0.3) (layers *.Cu *.Mask) (zone_connect 2) ${p.from.str})
            (pad "2" thru_hole rect (at 0.825 0 ${p.rot}) (size 0.9 0.95) (drill 0.3) (layers *.Cu *.Mask) (zone_connect 2) ${p.to.str})
        )
    `
}
