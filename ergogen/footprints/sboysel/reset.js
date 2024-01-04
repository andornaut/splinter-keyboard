module.exports = {
  nets: {
    from: undefined,
    to: undefined
  },
  params: {
    class: 'B',
    side: 'F'
  },
  body: p => {
    const model = `(model "${'${KICAD6_3DMODEL_DIR}'}/Button_Switch_SMD.3dshapes/SW_SPST_B3U-1000P.wrl" (offset(xyz 0 0 0)) (scale(xyz 1 1 1)) (rotate(xyz ${p.param.side == 'F' ? '180' : '0'} 0 0 )) )`

    return `(module SW_SPST_B3U-1000P (layer "F.Cu")
  ${p.at}
(attr smd)
  (fp_text reference "${p.ref}" (at 0 -2.5) (layer "${p.param.side}.SilkS") ${p.ref_hide} (effects (font (size 1 1) (thickness 0.15))) )
  (fp_text value "" (at 0 2.5) (layer "${p.param.side}.Fab") (effects (font (size 1 1) (thickness 0.15))) )
  (fp_text user "${p.ref}" (at 0 -2.5) (layer "${p.param.side}.Fab") (effects (font (size 1 1) (thickness 0.15))) )

  (fp_line (start -1.65 1.1) (end -1.65 1.4) (layer "${p.param.side}.SilkS") (width 0.12) )
  (fp_line (start -1.65 -1.1) (end -1.65 -1.4) (layer "${p.param.side}.SilkS") (width 0.12) )
  (fp_line (start -1.65 -1.4) (end 1.65 -1.4) (layer "${p.param.side}.SilkS") (width 0.12) )
  (fp_line (start 1.65 1.4) (end 1.65 1.1) (layer "${p.param.side}.SilkS") (width 0.12) )
  (fp_line (start -1.65 1.4) (end 1.65 1.4) (layer "${p.param.side}.SilkS") (width 0.12) )
  (fp_line (start 1.65 -1.4) (end 1.65 -1.1) (layer "${p.param.side}.SilkS") (width 0.12) )
  (fp_line (start -2.4 1.65) (end 2.4 1.65) (layer "${p.param.side}.CrtYd") (width 0.05) )
  (fp_line (start 2.4 1.65) (end 2.4 -1.65) (layer "${p.param.side}.CrtYd") (width 0.05) )
  (fp_line (start -2.4 -1.65) (end -2.4 1.65) (layer "${p.param.side}.CrtYd") (width 0.05) )
  (fp_line (start 2.4 -1.65) (end -2.4 -1.65) (layer "${p.param.side}.CrtYd") (width 0.05) )
  (fp_line (start -1.5 -1.25) (end 1.5 -1.25) (layer "${p.param.side}.Fab") (width 0.1) )
  (fp_line (start 1.5 -1.25) (end 1.5 1.25) (layer "${p.param.side}.Fab") (width 0.1) )
  (fp_line (start 1.5 1.25) (end -1.5 1.25) (layer "${p.param.side}.Fab") (width 0.1) )
  (fp_line (start -1.5 1.25) (end -1.5 -1.25) (layer "${p.param.side}.Fab") (width 0.1) )
  (fp_circle (center 0 0) (end 0.75 0) (layer "${p.param.side}.Fab") (width 0.1) (fill none) )
  
  (pad "1" smd rect (at -1.7 0 ${p.rot}) (size 0.9 1.7) (layers "${p.param.side}.Cu" "${p.param.side}.Paste" "${p.param.side}.Mask") ${p.net.from.str})
  (pad "2" smd rect (at 1.7 0 ${p.rot}) (size 0.9 1.7) (layers "${p.param.side}.Cu" "${p.param.side}.Paste" "${p.param.side}.Mask") ${p.net.to.str})

)
    `
  }
}