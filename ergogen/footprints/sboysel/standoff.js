module.exports = {
  params: {
    size: 3.429,
  },
  body: p => {
    return `(module Standoff (layer "F.Cu") (tedit 5F880A3E)
    ${p.at}
  (pad "" np_thru_hole circle (at 0 0) (size ${p.param.size} ${p.param.size}) (drill ${p.param.size}) (layers *.Cu *.Mask) )
)
`
  }

}
