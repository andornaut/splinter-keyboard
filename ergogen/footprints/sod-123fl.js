module.exports = {
    params: {
        designator: 'D',
        from: {type: 'net', value: 'from'},
        to: {type: 'net', value: 'to'}
    },
    body: p => `
        (footprint "splinter:D_SOD-123FL_HandSolder"
            ${p.at}
            (descr "SOD-123FL flat-lead TVS/diode, hand-solder reversible pads (pin 1 = cathode / 'to' net). Custom footprint, not a KiCad stock part. Body 3.0x1.85mm, lead span ~3.7mm, pitch 3.2mm per Nexperia SOD123FL.")
            (tags "SOD-123FL SOD-123F TVS ESD")
            (attr through_hole)
            (fp_text reference "${p.ref}" (at 0 -2 ${p.rot}) (layer "F.SilkS") ${p.ref_hide}
                (effects (font (size 0.8 0.8) (thickness 0.12)))
            )
            (fp_text value "SOD-123FL" (at 0 2 ${p.rot}) (layer "F.Fab") hide
                (effects (font (size 0.8 0.8) (thickness 0.12)))
            )

            ${''/* Front: body outline 3.0 x 1.85mm (nominal), cathode bar, silk, courtyard */}
            (fp_line (start -1.5 -0.925) (end 1.5 -0.925) (stroke (width 0.1) (type solid)) (layer "F.Fab"))
            (fp_line (start 1.5 -0.925) (end 1.5 0.925) (stroke (width 0.1) (type solid)) (layer "F.Fab"))
            (fp_line (start 1.5 0.925) (end -1.5 0.925) (stroke (width 0.1) (type solid)) (layer "F.Fab"))
            (fp_line (start -1.5 -0.925) (end -1.5 0.925) (stroke (width 0.1) (type solid)) (layer "F.Fab"))
            (fp_line (start -0.95 -0.6) (end -0.95 0.6) (stroke (width 0.1) (type solid)) (layer "F.Fab"))
            (fp_line (start -0.9 -0.95) (end 0.9 -0.95) (stroke (width 0.12) (type solid)) (layer "F.SilkS"))
            (fp_line (start -0.9 0.95) (end 0.9 0.95) (stroke (width 0.12) (type solid)) (layer "F.SilkS"))
            (fp_line (start -2.4 -1.15) (end 2.4 -1.15) (stroke (width 0.05) (type solid)) (layer "F.CrtYd"))
            (fp_line (start 2.4 -1.15) (end 2.4 1.15) (stroke (width 0.05) (type solid)) (layer "F.CrtYd"))
            (fp_line (start 2.4 1.15) (end -2.4 1.15) (stroke (width 0.05) (type solid)) (layer "F.CrtYd"))
            (fp_line (start -2.4 1.15) (end -2.4 -1.15) (stroke (width 0.05) (type solid)) (layer "F.CrtYd"))

            ${''/* Back: mirrored for reversibility */}
            (fp_line (start -1.5 -0.925) (end 1.5 -0.925) (stroke (width 0.1) (type solid)) (layer "B.Fab"))
            (fp_line (start 1.5 -0.925) (end 1.5 0.925) (stroke (width 0.1) (type solid)) (layer "B.Fab"))
            (fp_line (start 1.5 0.925) (end -1.5 0.925) (stroke (width 0.1) (type solid)) (layer "B.Fab"))
            (fp_line (start -1.5 -0.925) (end -1.5 0.925) (stroke (width 0.1) (type solid)) (layer "B.Fab"))
            (fp_line (start -0.95 -0.6) (end -0.95 0.6) (stroke (width 0.1) (type solid)) (layer "B.Fab"))
            (fp_line (start -0.9 -0.95) (end 0.9 -0.95) (stroke (width 0.12) (type solid)) (layer "B.SilkS"))
            (fp_line (start -0.9 0.95) (end 0.9 0.95) (stroke (width 0.12) (type solid)) (layer "B.SilkS"))
            (fp_line (start -2.4 -1.15) (end 2.4 -1.15) (stroke (width 0.05) (type solid)) (layer "B.CrtYd"))
            (fp_line (start 2.4 -1.15) (end 2.4 1.15) (stroke (width 0.05) (type solid)) (layer "B.CrtYd"))
            (fp_line (start 2.4 1.15) (end -2.4 1.15) (stroke (width 0.05) (type solid)) (layer "B.CrtYd"))
            (fp_line (start -2.4 1.15) (end -2.4 -1.15) (stroke (width 0.05) (type solid)) (layer "B.CrtYd"))

            (pad "1" thru_hole rect (at -1.6 0 ${p.rot}) (size 1.1 1.35) (drill 0.3) (layers *.Cu *.Mask) (zone_connect 2) ${p.to.str})
            (pad "2" thru_hole rect (at 1.6 0 ${p.rot}) (size 1.1 1.35) (drill 0.3) (layers *.Cu *.Mask) (zone_connect 2) ${p.from.str})
        )
    `
}
