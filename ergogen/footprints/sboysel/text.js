module.exports = {
  params: {
    side: 'F',
    text: '',
    h_size: 1,
    v_size: 1,
    thickness: 0.15,
    justify: '',
    layer: 'SilkS'
  },
  body: p => {
    justify = p.justify != '' && `(justify ${p.justify})` || '';
    // const mirror = p.param.side != 'F' ? 'mirror' : ''
    return `
            (gr_text "${p.text}" ${p.at} (layer ${p.side}.${p.layer})
                (effects (font (size ${p.h_size} ${p.v_size}) (thickness ${p.thickness})) ${justify})
            )
        `
  }
}
