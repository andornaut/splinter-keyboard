module.exports = {
  params: {
    TX: {type: 'net', value: 'TX'},
    RX: {type: 'net', value: 'RX'},
    POWER: {type: 'net', value: 'POWER'},
    GND: {type: 'net', value: 'GND'}
  },
  body: p => {
    const body = `
    (module "44144-0003" (layer F.Cu)
      ${p.at}
      (fp_line (start -7.62 0) (end 7.62 0) (layer F.Fab) (width 0.2))
      (fp_line (start 7.62 0) (end 7.62 16.89) (layer F.Fab) (width 0.2))
      (fp_line (start 7.62 16.89) (end -7.62 16.89) (layer F.Fab) (width 0.2))
      (fp_line (start -7.62 16.89) (end -7.62 0) (layer F.Fab) (width 0.2))
      (fp_circle (center -4.48 -2.704) (end -4.48 -2.61208) (layer F.SilkS) (width 0.2))

      (pad 1 smd rect (at -4.445 -0.83 ${p.rot}) (size 0.64 2.54) (layers F.Cu F.Paste F.Mask) ${p.POWER.str})
      (pad 2 smd rect (at -3.175 -0.83 ${p.rot}) (size 0.64 2.54) (layers F.Cu F.Paste F.Mask) ${p.GND.str})
      (pad 3 smd rect (at -1.905 -0.83 ${p.rot}) (size 0.64 2.54) (layers F.Cu F.Paste F.Mask) ${p.RX.str})
      (pad 4 smd rect (at -0.635 -0.83 ${p.rot}) (size 0.64 2.54) (layers F.Cu F.Paste F.Mask) ${p.RX.str})
      (pad 5 smd rect (at 0.635 -0.83 ${p.rot}) (size 0.64 2.54) (layers F.Cu F.Paste F.Mask) ${p.TX.str})
      (pad 6 smd rect (at 1.905 -0.83 ${p.rot}) (size 0.64 2.54) (layers F.Cu F.Paste F.Mask) ${p.TX.str})
      (pad 7 smd rect (at 3.175 -0.83 ${p.rot}) (size 0.64 2.54) (layers F.Cu F.Paste F.Mask) ${p.GND.str})
      (pad 8 smd rect (at 4.445 -0.83 ${p.rot}) (size 0.64 2.54) (layers F.Cu F.Paste F.Mask) ${p.POWER.str})
      (pad 9 smd rect (at -6.35 10.945 ${p.rot}) (size 2.54 5.21) (layers F.Cu F.Paste F.Mask))
      (pad 10 smd rect (at 6.35 10.945 ${p.rot}) (size 2.54 5.21) (layers F.Cu F.Paste F.Mask))

      (fp_line (start -7.62 0) (end 7.62 0) (layer B.Fab) (width 0.2))
      (fp_line (start 7.62 0) (end 7.62 16.89) (layer B.Fab) (width 0.2))
      (fp_line (start 7.62 16.89) (end -7.62 16.89) (layer B.Fab) (width 0.2))
      (fp_line (start -7.62 16.89) (end -7.62 0) (layer B.Fab) (width 0.2))
      (fp_circle (center -4.48 -2.704) (end -4.48 -2.61208) (layer B.SilkS) (width 0.2))

      (pad 1 smd rect (at -4.445 -0.83 ${p.rot}) (size 0.64 2.54) (layers B.Cu B.Paste B.Mask) ${p.POWER.str})
      (pad 2 smd rect (at -3.175 -0.83 ${p.rot}) (size 0.64 2.54) (layers B.Cu B.Paste B.Mask) ${p.GND.str})
      (pad 3 smd rect (at -1.905 -0.83 ${p.rot}) (size 0.64 2.54) (layers B.Cu B.Paste B.Mask) ${p.RX.str})
      (pad 4 smd rect (at -0.635 -0.83 ${p.rot}) (size 0.64 2.54) (layers B.Cu B.Paste B.Mask) ${p.RX.str})
      (pad 5 smd rect (at 0.635 -0.83 ${p.rot}) (size 0.64 2.54) (layers B.Cu B.Paste B.Mask) ${p.TX.str})
      (pad 6 smd rect (at 1.905 -0.83 ${p.rot}) (size 0.64 2.54) (layers B.Cu B.Paste B.Mask) ${p.TX.str})
      (pad 7 smd rect (at 3.175 -0.83 ${p.rot}) (size 0.64 2.54) (layers B.Cu B.Paste B.Mask) ${p.GND.str})
      (pad 8 smd rect (at 4.445 -0.83 ${p.rot}) (size 0.64 2.54) (layers B.Cu B.Paste B.Mask) ${p.POWER.str})
      (pad 9 smd rect (at -6.35 10.945 ${p.rot}) (size 2.54 5.21) (layers B.Cu B.Paste B.Mask))
      (pad 10 smd rect (at 6.35 10.945 ${p.rot}) (size 2.54 5.21) (layers B.Cu B.Paste B.Mask))

    )
    `
    return body
  }
}
