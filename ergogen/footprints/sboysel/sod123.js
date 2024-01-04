// src: Keebio
module.exports = {
    params: {
        from: undefined,
        to: undefined,
        side: 'F',
        class: 'D'
    },
    body: p => `
  
    (module D_SOD123 (layer ${ p.side }.Cu) (tedit 561B69D3)
      (attr smd)
      ${ p.at }
      (fp_text reference D_SOD123 (at 0 1.925) (layer ${ p.side }.Fab)
        (effects (font (size 0.8 0.8) (thickness 0.15)))
      )
      (fp_text value VAL** (at 0 -1.925) (layer ${ p.side }.Fab) hide
        (effects (font (size 0.8 0.8) (thickness 0.15)))
      )
      (fp_line (start -3.075 1.2) (end -3.075 -1.2) (layer ${ p.side }.SilkS) (width 0.2))
      (fp_line (start -2.8 -1.2) (end -2.8 1.2) (layer ${ p.side }.SilkS) (width 0.2))
      (fp_line (start -2.925 -1.2) (end -2.925 1.2) (layer ${ p.side }.SilkS) (width 0.2))
      (fp_line (start -3.2 -1.2) (end 2.8 -1.2) (layer ${ p.side }.SilkS) (width 0.2))
      (fp_line (start 2.8 -1.2) (end 2.8 1.2) (layer ${ p.side }.SilkS) (width 0.2))
      (fp_line (start 2.8 1.2) (end -3.2 1.2) (layer ${ p.side }.SilkS) (width 0.2))
      (fp_line (start -3.2 1.2) (end -3.2 -1.2) (layer ${ p.side }.SilkS) (width 0.2))
      (pad 2 smd rect (at 1.7 0 ${ p.rot }) (size 1.2 1.4) (layers ${ p.side }.Cu ${ p.side }.Paste ${ p.side }.Mask) ${ p.to })
      (pad 1 smd rect (at -1.7 0 ${ p.rot }) (size 1.2 1.4) (layers ${ p.side }.Cu ${ p.side }.Paste ${ p.side }.Mask) ${ p.from })
    )
    
    `
}

