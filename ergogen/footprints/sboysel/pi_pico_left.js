module.exports = {
  params: {
    orientation: 'up',
    GP0: {type: 'net', value: 'GP0'},
    GP1: {type: 'net', value: 'GP1'},
    GND: {type: 'net', value: 'GND'},
    GP2: {type: 'net', value: 'GP2'},
    GP3: {type: 'net', value: 'GP3'},
    GP4: {type: 'net', value: 'GP4'},
    GP5: {type: 'net', value: 'GP5'},
    GND: {type: 'net', value: 'GND'},
    GP6: {type: 'net', value: 'GP6'},
    GP7: {type: 'net', value: 'GP7'},
    GP8: {type: 'net', value: 'GP8'},
    GP9: {type: 'net', value: 'GP9'},
    GND: {type: 'net', value: 'GND'},
    GP10: {type: 'net', value: 'GP10'},
    GP11: {type: 'net', value: 'GP11'},
    GP12: {type: 'net', value: 'GP12'},
    GP13: {type: 'net', value: 'GP13'},
    GND: {type: 'net', value: 'GND'},
    GP14: {type: 'net', value: 'GP14'},
    GP15: {type: 'net', value: 'GP15'}
  },
  body: p => {
      return `
      (module RPi_Pico_TH_oval_face_up_left 
        (layer F.Cu)
        (attr through_hole)
        ${p.at}
        (pad 1 thru_hole oval (at 0 -24.13) (size 1.84 1.7) (drill oval 1.16 1.02) (layers *.Cu *.Mask) (tstamp 261789c0-418e-4ec0-8cdf-89abe1f96c5d) ${p.GP0.str})
        (pad 2 thru_hole oval (at 0 -21.59) (size 1.84 1.7) (drill oval 1.16 1.02) (layers *.Cu *.Mask) (tstamp 82df91bd-b1f7-4cb5-a4b8-f014077ed225) ${p.GP1.str})
        (pad 3 thru_hole rect (at 0 -19.05) (size 1.84 1.7) (drill oval 1.16 1.02) (layers *.Cu *.Mask) (tstamp e2d28f85-8433-4782-86c1-698d98ca355b) ${p.GND.str})
        (pad 4 thru_hole oval (at 0 -16.51) (size 1.84 1.7) (drill oval 1.16 1.02) (layers *.Cu *.Mask) (tstamp 6c215906-b1c0-41e7-a1ee-f64340a0df1f) ${p.GP2.str})
        (pad 5 thru_hole oval (at 0 -13.97) (size 1.84 1.7) (drill oval 1.16 1.02) (layers *.Cu *.Mask) (tstamp 76c55b2f-8f9b-48f6-a612-6fe3631d36eb) ${p.GP3.str})
        (pad 6 thru_hole oval (at 0 -11.43) (size 1.84 1.7) (drill oval 1.16 1.02) (layers *.Cu *.Mask) (tstamp 210013bf-6406-44cc-a685-766765aa871b) ${p.GP4.str})
        (pad 7 thru_hole oval (at 0 -8.89) (size 1.84 1.7) (drill oval 1.16 1.02) (layers *.Cu *.Mask) (tstamp 2a1ac614-5190-4c1d-94c5-f92822392dbd) ${p.GP5.str})
        (pad 8 thru_hole rect (at 0 -6.35) (size 1.84 1.7) (drill oval 1.16 1.02) (layers *.Cu *.Mask) (tstamp 3aca05ca-5eaa-49fe-b403-9e2bce888982) ${p.GND.str})
        (pad 9 thru_hole oval (at 0 -3.81) (size 1.84 1.7) (drill oval 1.16 1.02) (layers *.Cu *.Mask) (tstamp fc3ee03b-64c4-4765-a4db-f9ccddc815c0) ${p.GP6.str})
        (pad 10 thru_hole oval (at 0 -1.27) (size 1.84 1.7) (drill oval 1.16 1.02) (layers *.Cu *.Mask) (tstamp 1cbf2788-2f4d-4a14-987b-1ca92d4e80a5) ${p.GP7.str})
        (pad 11 thru_hole oval (at 0 1.27) (size 1.84 1.7) (drill oval 1.16 1.02) (layers *.Cu *.Mask) (tstamp b8d2415c-f56e-4a89-978d-a2919d2209f5) ${p.GP8.str})
        (pad 12 thru_hole oval (at 0 3.81) (size 1.84 1.7) (drill oval 1.16 1.02) (layers *.Cu *.Mask) (tstamp 721079ce-6e9b-4142-b40e-724402815846) ${p.GP9.str})
        (pad 13 thru_hole rect (at 0 6.35) (size 1.84 1.7) (drill oval 1.16 1.02) (layers *.Cu *.Mask) (tstamp 156789ac-0299-4e4b-9bdc-aae415420eec) ${p.GND.str})
        (pad 14 thru_hole oval (at 0 8.89) (size 1.84 1.7) (drill oval 1.16 1.02) (layers *.Cu *.Mask) (tstamp fda6fba3-26de-4533-ab37-f87bb8ca8965) ${p.GP10.str})
        (pad 15 thru_hole oval (at 0 11.43) (size 1.84 1.7) (drill oval 1.16 1.02) (layers *.Cu *.Mask) (tstamp db248dbe-bef4-43e0-991f-f8907ae081d4) ${p.GP11.str})
        (pad 16 thru_hole oval (at 0 13.97) (size 1.84 1.7) (drill oval 1.16 1.02) (layers *.Cu *.Mask) (tstamp 8b5154dc-4718-4a03-ad67-ed035a4319ce) ${p.GP12.str})
        (pad 17 thru_hole oval (at 0 16.51) (size 1.84 1.7) (drill oval 1.16 1.02) (layers *.Cu *.Mask) (tstamp eb64b7d2-d623-452c-9703-2bb0265ee337) ${p.GP13.str})
        (pad 18 thru_hole rect (at 0 19.05) (size 1.84 1.7) (drill oval 1.16 1.02) (layers *.Cu *.Mask) (tstamp f7386878-6bd2-49fb-be47-6588e913174b) ${p.GND.str})
        (pad 19 thru_hole oval (at 0 21.59) (size 1.84 1.7) (drill oval 1.16 1.02) (layers *.Cu *.Mask) (tstamp fa8076fb-ecc2-4918-a4f3-511178e9ad37) ${p.GP14.str})
        (pad 20 thru_hole oval (at 0 24.13) (size 1.84 1.7) (drill oval 1.16 1.02) (layers *.Cu *.Mask) (tstamp 4b6b7c47-5e11-4065-b26e-9c14c9c8ee50) ${p.GP15.str})
      )
      `
  }
}


