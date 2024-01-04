// https://github.com/siderakb/key-switches.pretty/blob/main/SW_Gateron_LowProfile_HotSwap_THT.kicad_mod

module.exports = {
  params: {
    from: undefined,
    to: undefined
  },
  body: p => {
    return `
      (module "gateron-ks27-reversible"
        (layer "F.Cu")
        
        (attr through_hole)

        ${p.at /* parametric position */}  
  
        (fp_line (start 1.8 -6.3) (end -3.2 -6.3) (layer "Eco2.User") (width 0.12) (tstamp 21ae9c3a-7138-444e-be38-56a4842ab594))
        (fp_line (start -7 -7) (end -7 7) (layer "Eco2.User") (width 0.12) (tstamp 632acde9-b7fd-4f04-8cb4-d2cbb06b3595))
        (fp_line (start 7 7) (end 7 -7) (layer "Eco2.User") (width 0.12) (tstamp 67621f9e-0a6a-4778-ad69-04dcf300659c))
        (fp_line (start -3.2 -6.3) (end -3.2 -3.1) (layer "Eco2.User") (width 0.12) (tstamp 81a15393-727e-448b-a777-b18773023d89))
        (fp_line (start 7 -7) (end -7 -7) (layer "Eco2.User") (width 0.12) (tstamp 98e81e80-1f85-4152-be3f-99785ea97751))
        (fp_line (start -7 7) (end 7 7) (layer "Eco2.User") (width 0.12) (tstamp 9dab0cb7-2557-4419-963b-5ae736517f62))
        (fp_line (start 1.8 -6.3) (end 1.8 -3.1) (layer "Eco2.User") (width 0.12) (tstamp a29f8df0-3fae-4edf-8d9c-bd5a875b13e3))
        (fp_line (start 1.8 -3.1) (end -3.2 -3.1) (layer "Eco2.User") (width 0.12) (tstamp abe07c9a-17c3-43b5-b7a6-ae867ac27ea7))
        (fp_line (start 7.5 7.5) (end 7.5 -7.5) (layer "F.Fab") (width 0.1) (tstamp 0d35483a-0b12-46cc-b9f2-896fd6831779))
        (fp_line (start -7.5 -7.5) (end -7.5 7.5) (layer "F.Fab") (width 0.1) (tstamp 786b6072-5772-4bc1-8eeb-6c4e19f2a91b))
        (fp_line (start -7.5 7.5) (end 7.5 7.5) (layer "F.Fab") (width 0.1) (tstamp c3c93de0-69b1-4a04-8e0b-d78caf487c63))
        (fp_line (start 7.5 -7.5) (end -7.5 -7.5) (layer "F.Fab") (width 0.1) (tstamp ef1b4b98-541b-4673-a04f-2043250fc40a))
        (pad "" np_thru_hole circle (at 0 0) (size 5 5) (drill 5) (layers *.Cu *.Mask) (tstamp afb8e687-4a13-41a1-b8c0-89a749e897fe))
        (pad "1" thru_hole circle (at 4.4 4.7) (size 2.5 2.5) (drill 1.5) (layers *.Cu *.Mask) (tstamp 410bb148-ed54-4cc7-b862-6e9453dc29ed) ${p.from.str})
        (pad "1" thru_hole circle (at 2.6 5.75) (size 2.5 2.5) (drill 1.5) (layers *.Cu *.Mask) (tstamp babeabf2-f3b0-4ed5-8d9e-0215947e6cf3) ${p.from.str})
        (pad "2" thru_hole circle (at -4.4 4.7) (size 2.5 2.5) (drill 1.5) (layers *.Cu *.Mask) (tstamp 7bbf981c-a063-4e30-8911-e4228e1c0743) ${p.to.str})
        (pad "2" thru_hole circle (at -2.6 5.75) (size 2.5 2.5) (drill 1.5) (layers *.Cu *.Mask) (tstamp c0588b1d-e46f-4d62-8e9a-42a1a0823057) ${p.to.str})
      )
    `
  }
}
