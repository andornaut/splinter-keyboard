// https://www.snapeda.com/parts/IC-WE%20TSSOP20/iC-Haus/view-part/
module.exports = {
  params: {
    side: 'F',
    reference: 'U1',
    P1: {type: 'net', value: 'P1'},
    P2: {type: 'net', value: 'P2'},  
    P3: {type: 'net', value: 'P3'},
    P4: {type: 'net', value: 'P4'}, 
    P5: {type: 'net', value: 'P5'},
    P6: {type: 'net', value: 'P6'},  
    P7: {type: 'net', value: 'P7'},
    P8: {type: 'net', value: 'P8'}, 
    P9: {type: 'net', value: 'P9'},
    P10: {type: 'net', value: 'P10'},  
    P11: {type: 'net', value: 'P11'},
    P12: {type: 'net', value: 'P12'}, 
    P13: {type: 'net', value: 'P13'},
    P14: {type: 'net', value: 'P14'},  
    P15: {type: 'net', value: 'P15'},
    P16: {type: 'net', value: 'P16'}, 
    P17: {type: 'net', value: 'P17'},
    P18: {type: 'net', value: 'P18'},  
    P19: {type: 'net', value: 'P19'},
    P20: {type: 'net', value: 'P20'} 
  },
  body: p => {
    const body = `
    (module "TSSOP20" (layer ${ p.side }.Cu)
      ${ p.at }
      (attr smd)
      (fp_text reference ${ p.reference } (at 0 0) (layer ${ p.side }.Fab)
          (effects (font (size 0.3 0.3) (thickness 0.075)))
        (tstamp 4e6d9590-8346-46fa-bcec-3c0b970993a6)
      )
      (fp_text value "PCA9518PW" (at -0.05 0.66) (layer ${ p.side }.Fab)
          (effects (font (size 0.3 0.3) (thickness 0.075)))
        (tstamp 6c6fede3-348a-4455-85fe-17364c642cfb)
      )
      (fp_line (start -3.24866 -2.19964) (end -3.24866 2.19964)
        (stroke (width 0.001) (type solid)) (layer ${ p.side }.Fab) (tstamp 79719a1d-3535-448f-90da-92fc95fc8351))
      (fp_line (start -3.24866 -2.19964) (end 3.24866 -2.19964)
        (stroke (width 0.001) (type solid)) (layer ${ p.side }.Fab) (tstamp a54aa0c7-ac05-492b-b2fe-bbf4e0e5d8c8))
      (fp_line (start -3.24866 1.59766) (end -2.64922 2.19964)
        (stroke (width 0.001) (type solid)) (layer ${ p.side }.Fab) (tstamp 5481bac5-ddd8-48e3-9745-4fc9ec75fd80))
      (fp_line (start -3.24866 2.19964) (end 3.24866 2.19964)
        (stroke (width 0.001) (type solid)) (layer ${ p.side }.Fab) (tstamp bdae560a-ee69-49ef-8e70-77861c6423ca))
      (fp_line (start 3.24866 -2.19964) (end 3.24866 2.19964)
        (stroke (width 0.001) (type solid)) (layer ${ p.side }.Fab) (tstamp 46ab36a4-0d6e-4f73-9879-10809ed3cc81))
      (pad "P1" smd rect (at -2.92354 2.84988 ${ p.rot + 180 }) (size 0.39878 1.09982) (layers ${ p.side }.Cu ${ p.side }.Paste ${ p.side }.Mask) ${ p.P1 } (tstamp f98c6027-eb36-4535-882b-b75cef4af2ba))
      (pad "P2" smd rect (at -2.2733 2.84988 ${ p.rot + 180 }) (size 0.39878 1.09982) (layers ${ p.side }.Cu ${ p.side }.Paste ${ p.side }.Mask) ${ p.P2 } (tstamp 550e5f7a-94bb-48ff-968f-5a0b0c348e93))
      (pad "P3" smd rect (at -1.62306 2.84988 ${ p.rot + 180 }) (size 0.39878 1.09982) (layers ${ p.side }.Cu ${ p.side }.Paste ${ p.side }.Mask) ${ p.P3 } (tstamp 93b99a16-c5ef-4313-9bec-ae841bb08567))
      (pad "P4" smd rect (at -0.97282 2.84988 ${ p.rot + 180 }) (size 0.39878 1.09982) (layers ${ p.side }.Cu ${ p.side }.Paste ${ p.side }.Mask) ${ p.P4 } (tstamp b0d88d84-c046-442d-90e0-00859df3ef5d))
      (pad "P5" smd rect (at -0.32258 2.84988 ${ p.rot + 180 }) (size 0.39878 1.09982) (layers ${ p.side }.Cu ${ p.side }.Paste ${ p.side }.Mask) ${ p.P5 } (tstamp bd362a69-33d7-4dcb-882c-cd71d3a8f995))
      (pad "P6" smd rect (at 0.32258 2.84988 ${ p.rot + 180 }) (size 0.39878 1.09982) (layers ${ p.side }.Cu ${ p.side }.Paste ${ p.side }.Mask) ${ p.P6 } (tstamp 19bc6f9b-ec25-4e8a-be32-01f548e76d8c))
      (pad "P7" smd rect (at 0.97282 2.84988 ${ p.rot + 180 }) (size 0.39878 1.09982) (layers ${ p.side }.Cu ${ p.side }.Paste ${ p.side }.Mask) ${ p.P7 } (tstamp c2f8a5b2-14c7-4e36-8f3d-c8c6edcbf75a))
      (pad "P8" smd rect (at 1.62306 2.84988 ${ p.rot + 180 }) (size 0.39878 1.09982) (layers ${ p.side }.Cu ${ p.side }.Paste ${ p.side }.Mask) ${ p.P8 } (tstamp 4101e31e-d347-4342-83cf-86036c95f84c))
      (pad "P9" smd rect (at 2.2733 2.84988 ${ p.rot + 180 }) (size 0.39878 1.09982) (layers ${ p.side }.Cu ${ p.side }.Paste ${ p.side }.Mask) ${ p.P9 } (tstamp 759d95e4-f07c-4846-8ba2-253ac13463ba))
      (pad "P10" smd rect (at 2.92354 2.84988 ${ p.rot + 180 }) (size 0.39878 1.09982) (layers ${ p.side }.Cu ${ p.side }.Paste ${ p.side }.Mask) ${ p.P10 } (tstamp 3e8cb981-f9e1-4872-b50a-62ac67ce4dc7))
      (pad "P11" smd rect (at 2.92354 -2.84988 ${ p.rot }) (size 0.39878 1.09982) (layers ${ p.side }.Cu ${ p.side }.Paste ${ p.side }.Mask) ${ p.P11 } (tstamp a2628a42-f10e-495e-8f11-6a92b0755562))
      (pad "P12" smd rect (at 2.2733 -2.84988 ${ p.rot }) (size 0.39878 1.09982) (layers ${ p.side }.Cu ${ p.side }.Paste ${ p.side }.Mask) ${ p.P12 } (tstamp 8edf05cf-a60e-4236-8fbf-ad1443fd482a))
      (pad "P13" smd rect (at 1.62306 -2.84988 ${ p.rot }) (size 0.39878 1.09982) (layers ${ p.side }.Cu ${ p.side }.Paste ${ p.side }.Mask) ${ p.P13 } (tstamp 240550be-b579-4054-9db5-9e8683909c19))
      (pad "P14" smd rect (at 0.97282 -2.84988 ${ p.rot }) (size 0.39878 1.09982) (layers ${ p.side }.Cu ${ p.side }.Paste ${ p.side }.Mask) ${ p.P14 } (tstamp c4d7d2da-8520-4add-aba2-b96ed0278390))
      (pad "P15" smd rect (at 0.32258 -2.84988 ${ p.rot }) (size 0.39878 1.09982) (layers ${ p.side }.Cu ${ p.side }.Paste ${ p.side }.Mask) ${ p.P15 } (tstamp 13fa6907-0a86-4d0a-ac29-1fffd1a653e1))
      (pad "P16" smd rect (at -0.32258 -2.84988 ${ p.rot }) (size 0.39878 1.09982) (layers ${ p.side }.Cu ${ p.side }.Paste ${ p.side }.Mask) ${ p.P16 } (tstamp 4ec248f8-acdb-40ae-a202-8dde038366a0))
      (pad "P17" smd rect (at -0.97282 -2.84988 ${ p.rot }) (size 0.39878 1.09982) (layers ${ p.side }.Cu ${ p.side }.Paste ${ p.side }.Mask) ${ p.P17 } (tstamp 03c35cd5-385c-4e84-b71b-68aff92bb421))
      (pad "P18" smd rect (at -1.62306 -2.84988 ${ p.rot }) (size 0.39878 1.09982) (layers ${ p.side }.Cu ${ p.side }.Paste ${ p.side }.Mask) ${ p.P18 } (tstamp 604d9b65-7a77-44b1-9c1e-0747be156cb1))
      (pad "P19" smd rect (at -2.2733 -2.84988 ${ p.rot }) (size 0.39878 1.09982) (layers ${ p.side }.Cu ${ p.side }.Paste ${ p.side }.Mask) ${ p.P19 } (tstamp fc952e06-9b1a-4dda-a15f-c2c9fdb8fc74))
      (pad "P20" smd rect (at -2.92354 -2.84988 ${ p.rot }) (size 0.39878 1.09982) (layers ${ p.side }.Cu ${ p.side }.Paste ${ p.side }.Mask) ${ p.P20 } (tstamp e7c9b196-65fd-4d75-945e-a599595a8f4c))
    )    
    `
    return body
  }
}
