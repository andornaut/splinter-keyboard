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
    GP15: {type: 'net', value: 'GP15'},
    GP16: {type: 'net', value: 'GP16'},
    GP17: {type: 'net', value: 'GP17'},
    GND: {type: 'net', value: 'GND'},
    GP18: {type: 'net', value: 'GP18'},
    GP19: {type: 'net', value: 'GP19'},
    GP20: {type: 'net', value: 'GP20'},
    GP21: {type: 'net', value: 'GP21'},
    GND: {type: 'net', value: 'GND'},
    GP22: {type: 'net', value: 'GP22'},
    GP26: {type: 'net', value: 'GP26'},
    GP27: {type: 'net', value: 'GP27'},
    GP28: {type: 'net', value: 'GP28'},
    GND: {type: 'net', value: 'GND'},
    GP29: {type: 'net', value: 'GP29'},
    ADC_VREF: {type: 'net', value: 'ADC_VREF'},
    GP24: {type: 'net', value: 'GP24'},
    _3V3: {type: 'net', value: '3V3'},
    GND: {type: 'net', value: 'GND'},
    VSYS: {type: 'net', value: 'VSYS'},
    VBUS: {type: 'net', value: 'VBUS'}
  },
  body: p => {
    // pins run counter-clockwise from
    if(p.orientation == 'up') {
      return `
      (module RPi_Pico_TH_oval_face_up 
        (layer F.Cu)
        (attr through_hole)
        ${p.at}
        (fp_text reference U0 (at 0 0) (layer F.Fab) hide
          (effects (font (size 1 1) (thickness 0.15)))
          (tstamp db43bf1b-fd5c-4a08-b779-663eec4fe496)
        )
        (pad 1 thru_hole oval (at -8.82 -24.13) (size 1.84 1.7) (drill oval 1.16 1.02) (layers *.Cu *.Mask) (tstamp 261789c0-418e-4ec0-8cdf-89abe1f96c5d) ${p.GP0.str})
        (pad 2 thru_hole oval (at -8.82 -21.59) (size 1.84 1.7) (drill oval 1.16 1.02) (layers *.Cu *.Mask) (tstamp 82df91bd-b1f7-4cb5-a4b8-f014077ed225) ${p.GP1.str})
        (pad 3 thru_hole rect (at -8.82 -19.05) (size 1.84 1.7) (drill oval 1.16 1.02) (layers *.Cu *.Mask) (tstamp e2d28f85-8433-4782-86c1-698d98ca355b) ${p.GND.str})
        (pad 4 thru_hole oval (at -8.82 -16.51) (size 1.84 1.7) (drill oval 1.16 1.02) (layers *.Cu *.Mask) (tstamp 6c215906-b1c0-41e7-a1ee-f64340a0df1f) ${p.GP2.str})
        (pad 5 thru_hole oval (at -8.82 -13.97) (size 1.84 1.7) (drill oval 1.16 1.02) (layers *.Cu *.Mask) (tstamp 76c55b2f-8f9b-48f6-a612-6fe3631d36eb) ${p.GP3.str})
        (pad 6 thru_hole oval (at -8.82 -11.43) (size 1.84 1.7) (drill oval 1.16 1.02) (layers *.Cu *.Mask) (tstamp 210013bf-6406-44cc-a685-766765aa871b) ${p.GP4.str})
        (pad 7 thru_hole oval (at -8.82 -8.89) (size 1.84 1.7) (drill oval 1.16 1.02) (layers *.Cu *.Mask) (tstamp 2a1ac614-5190-4c1d-94c5-f92822392dbd) ${p.GP5.str})
        (pad 8 thru_hole rect (at -8.82 -6.35) (size 1.84 1.7) (drill oval 1.16 1.02) (layers *.Cu *.Mask) (tstamp 3aca05ca-5eaa-49fe-b403-9e2bce888982) ${p.GND.str})
        (pad 9 thru_hole oval (at -8.82 -3.81) (size 1.84 1.7) (drill oval 1.16 1.02) (layers *.Cu *.Mask) (tstamp fc3ee03b-64c4-4765-a4db-f9ccddc815c0) ${p.GP6.str})
        (pad 10 thru_hole oval (at -8.82 -1.27) (size 1.84 1.7) (drill oval 1.16 1.02) (layers *.Cu *.Mask) (tstamp 1cbf2788-2f4d-4a14-987b-1ca92d4e80a5) ${p.GP7.str})
        (pad 11 thru_hole oval (at -8.82 1.27) (size 1.84 1.7) (drill oval 1.16 1.02) (layers *.Cu *.Mask) (tstamp b8d2415c-f56e-4a89-978d-a2919d2209f5) ${p.GP8.str})
        (pad 12 thru_hole oval (at -8.82 3.81) (size 1.84 1.7) (drill oval 1.16 1.02) (layers *.Cu *.Mask) (tstamp 721079ce-6e9b-4142-b40e-724402815846) ${p.GP9.str})
        (pad 13 thru_hole rect (at -8.82 6.35) (size 1.84 1.7) (drill oval 1.16 1.02) (layers *.Cu *.Mask) (tstamp 156789ac-0299-4e4b-9bdc-aae415420eec) ${p.GND.str})
        (pad 14 thru_hole oval (at -8.82 8.89) (size 1.84 1.7) (drill oval 1.16 1.02) (layers *.Cu *.Mask) (tstamp fda6fba3-26de-4533-ab37-f87bb8ca8965) ${p.GP10.str})
        (pad 15 thru_hole oval (at -8.82 11.43) (size 1.84 1.7) (drill oval 1.16 1.02) (layers *.Cu *.Mask) (tstamp db248dbe-bef4-43e0-991f-f8907ae081d4) ${p.GP11.str})
        (pad 16 thru_hole oval (at -8.82 13.97) (size 1.84 1.7) (drill oval 1.16 1.02) (layers *.Cu *.Mask) (tstamp 8b5154dc-4718-4a03-ad67-ed035a4319ce) ${p.GP12.str})
        (pad 17 thru_hole oval (at -8.82 16.51) (size 1.84 1.7) (drill oval 1.16 1.02) (layers *.Cu *.Mask) (tstamp eb64b7d2-d623-452c-9703-2bb0265ee337) ${p.GP13.str})
        (pad 18 thru_hole rect (at -8.82 19.05) (size 1.84 1.7) (drill oval 1.16 1.02) (layers *.Cu *.Mask) (tstamp f7386878-6bd2-49fb-be47-6588e913174b) ${p.GND.str})
        (pad 19 thru_hole oval (at -8.82 21.59) (size 1.84 1.7) (drill oval 1.16 1.02) (layers *.Cu *.Mask) (tstamp fa8076fb-ecc2-4918-a4f3-511178e9ad37) ${p.GP14.str})
        (pad 20 thru_hole oval (at -8.82 24.13) (size 1.84 1.7) (drill oval 1.16 1.02) (layers *.Cu *.Mask) (tstamp 4b6b7c47-5e11-4065-b26e-9c14c9c8ee50) ${p.GP15.str})
        (pad 21 thru_hole oval (at 8.82 24.13) (size 1.84 1.7) (drill oval 1.16 1.02) (layers *.Cu *.Mask) (tstamp 7a45c78c-faae-432b-8399-806250e23db7) ${p.GP16.str})
        (pad 22 thru_hole oval (at 8.82 21.59) (size 1.84 1.7) (drill oval 1.16 1.02) (layers *.Cu *.Mask) (tstamp 852f4f24-f0ec-4812-8953-10a1c9ba8b18) ${p.GP17.str})
        (pad 23 thru_hole rect (at 8.82 19.05) (size 1.84 1.7) (drill oval 1.16 1.02) (layers *.Cu *.Mask) (tstamp 6fbe5d8d-e43a-4207-a531-c4dfe41759ce) ${p.GND.str})
        (pad 24 thru_hole oval (at 8.82 16.51) (size 1.84 1.7) (drill oval 1.16 1.02) (layers *.Cu *.Mask) (tstamp 48f29450-601c-4f43-bede-558f16a2580a) ${p.GP18.str})
        (pad 25 thru_hole oval (at 8.82 13.97) (size 1.84 1.7) (drill oval 1.16 1.02) (layers *.Cu *.Mask) (tstamp 0cf035fe-7441-41a9-8ecd-8633f9511a86) ${p.GP19.str})
        (pad 26 thru_hole oval (at 8.82 11.43) (size 1.84 1.7) (drill oval 1.16 1.02) (layers *.Cu *.Mask) (tstamp 4aa34793-001c-422a-9a9e-f2fa24b7c918) ${p.GP20.str})
        (pad 27 thru_hole oval (at 8.82 8.89) (size 1.84 1.7) (drill oval 1.16 1.02) (layers *.Cu *.Mask) (tstamp 07bfbc8a-823e-44b5-ab95-5c0659fd56bb) ${p.GP21.str})
        (pad 28 thru_hole rect (at 8.82 6.35) (size 1.84 1.7) (drill oval 1.16 1.02) (layers *.Cu *.Mask) (tstamp 6fd23c62-f256-47b1-9fb2-80a0473029fb) ${p.GND.str})
        (pad 29 thru_hole oval (at 8.82 3.81) (size 1.84 1.7) (drill oval 1.16 1.02) (layers *.Cu *.Mask) (tstamp 0e54c542-e3a2-4db6-883d-37a3ad94739d) ${p.GP22.str})
        (pad 30 thru_hole oval (at 8.82 1.27) (size 1.84 1.7) (drill oval 1.16 1.02) (layers *.Cu *.Mask) (tstamp 49dcd950-fbab-4ac5-9a36-86d2c2a0259e) ${p.GP26.str})
        (pad 31 thru_hole oval (at 8.82 -1.27) (size 1.84 1.7) (drill oval 1.16 1.02) (layers *.Cu *.Mask) (tstamp 84cce8d0-f83b-4f08-af4b-1d62af837a54) ${p.GP27.str})
        (pad 32 thru_hole oval (at 8.82 -3.81) (size 1.84 1.7) (drill oval 1.16 1.02) (layers *.Cu *.Mask) (tstamp da79c04c-a207-48dc-a5d7-8a078322a160) ${p.GP28.str})
        (pad 33 thru_hole rect (at 8.82 -6.35) (size 1.84 1.7) (drill oval 1.16 1.02) (layers *.Cu *.Mask) (tstamp 9db6e273-f7b0-4ab9-9b75-cb2195ede133) ${p.GND.str})
        (pad 34 thru_hole oval (at 8.82 -8.89) (size 1.84 1.7) (drill oval 1.16 1.02) (layers *.Cu *.Mask) (tstamp 36be125c-d820-40b1-81f5-37cb6c4c1027) ${p.GP29.str})
        (pad 35 thru_hole oval (at 8.82 -11.43) (size 1.84 1.7) (drill oval 1.16 1.02) (layers *.Cu *.Mask) (tstamp 510cc5c4-e61c-4e17-93d1-bd10b62ad6fb) ${p.ADC_VREF.str})
        (pad 36 thru_hole oval (at 8.82 -13.97) (size 1.84 1.7) (drill oval 1.16 1.02) (layers *.Cu *.Mask) (tstamp 33256a6e-b053-471b-ac8e-081487946d0e) ${p.GP24.str})
        (pad 37 thru_hole oval (at 8.82 -16.51) (size 1.84 1.7) (drill oval 1.16 1.02) (layers *.Cu *.Mask) (tstamp ac928fb2-0ce9-4e34-8e2d-402b47a0d641) ${p._3V3.str})
        (pad 38 thru_hole rect (at 8.82 -19.05) (size 1.84 1.7) (drill oval 1.16 1.02) (layers *.Cu *.Mask) (tstamp cb792c93-111c-4188-a8ba-8930e71f97d8) ${p.GND.str})
        (pad 39 thru_hole oval (at 8.82 -21.59) (size 1.84 1.7) (drill oval 1.16 1.02) (layers *.Cu *.Mask) (tstamp b8260a4c-72c5-48e1-9736-d2140182d3fc) ${p.VSYS.str})
        (pad 40 thru_hole oval (at 8.82 -24.13) (size 1.84 1.7) (drill oval 1.16 1.02) (layers *.Cu *.Mask) (tstamp 1a60f562-a956-4d54-a00f-6201c5b12308) ${p.VBUS.str})
      )
      `
    } else if(p.orientation == 'down') {
    return `
    (module "RPi_Pico_TH_oval_face_down"
    (layer "F.Cu")
    (attr through_hole)
    ${p.at}
    (fp_text reference "U0" (at 0 0) (layer "F.Fab") hide
      (effects (font (size 1 1) (thickness 0.15)))
      (tstamp db43bf1b-fd5c-4a08-b779-663eec4fe496)
    )
    (pad "1" thru_hole oval (at 8.82 -24.13) (size 1.84 1.7) (drill oval 1.16 1.02) (layers *.Cu *.Mask) (tstamp 261789c0-418e-4ec0-8cdf-89abe1f96c5d) ${p.GP0.str})
    (pad "2" thru_hole oval (at 8.82 -21.59) (size 1.84 1.7) (drill oval 1.16 1.02) (layers *.Cu *.Mask) (tstamp 82df91bd-b1f7-4cb5-a4b8-f014077ed225) ${p.GP1.str})
    (pad "3" thru_hole rect (at 8.82 -19.05) (size 1.84 1.7) (drill oval 1.16 1.02) (layers *.Cu *.Mask) (tstamp e2d28f85-8433-4782-86c1-698d98ca355b) ${p.GND.str})
    (pad "4" thru_hole oval (at 8.82 -16.51) (size 1.84 1.7) (drill oval 1.16 1.02) (layers *.Cu *.Mask) (tstamp 6c215906-b1c0-41e7-a1ee-f64340a0df1f) ${p.GP2.str})
    (pad "5" thru_hole oval (at 8.82 -13.97) (size 1.84 1.7) (drill oval 1.16 1.02) (layers *.Cu *.Mask) (tstamp 76c55b2f-8f9b-48f6-a612-6fe3631d36eb) ${p.GP3.str})
    (pad "6" thru_hole oval (at 8.82 -11.43) (size 1.84 1.7) (drill oval 1.16 1.02) (layers *.Cu *.Mask) (tstamp 210013bf-6406-44cc-a685-766765aa871b) ${p.GP4.str})
    (pad "7" thru_hole oval (at 8.82 -8.89) (size 1.84 1.7) (drill oval 1.16 1.02) (layers *.Cu *.Mask) (tstamp 2a1ac614-5190-4c1d-94c5-f92822392dbd) ${p.GP5.str})
    (pad "8" thru_hole rect (at 8.82 -6.35) (size 1.84 1.7) (drill oval 1.16 1.02) (layers *.Cu *.Mask) (tstamp 3aca05ca-5eaa-49fe-b403-9e2bce888982) ${p.GND.str})
    (pad "9" thru_hole oval (at 8.82 -3.81) (size 1.84 1.7) (drill oval 1.16 1.02) (layers *.Cu *.Mask) (tstamp fc3ee03b-64c4-4765-a4db-f9ccddc815c0) ${p.GP6.str})
    (pad "10" thru_hole oval (at 8.82 -1.27) (size 1.84 1.7) (drill oval 1.16 1.02) (layers *.Cu *.Mask) (tstamp 1cbf2788-2f4d-4a14-987b-1ca92d4e80a5) ${p.GP7.str})
    (pad "11" thru_hole oval (at 8.82 1.27) (size 1.84 1.7) (drill oval 1.16 1.02) (layers *.Cu *.Mask) (tstamp b8d2415c-f56e-4a89-978d-a2919d2209f5) ${p.GP8.str})
    (pad "12" thru_hole oval (at 8.82 3.81) (size 1.84 1.7) (drill oval 1.16 1.02) (layers *.Cu *.Mask) (tstamp 721079ce-6e9b-4142-b40e-724402815846) ${p.GP9.str})
    (pad "13" thru_hole rect (at 8.82 6.35) (size 1.84 1.7) (drill oval 1.16 1.02) (layers *.Cu *.Mask) (tstamp 156789ac-0299-4e4b-9bdc-aae415420eec) ${p.GND.str})
    (pad "14" thru_hole oval (at 8.82 8.89) (size 1.84 1.7) (drill oval 1.16 1.02) (layers *.Cu *.Mask) (tstamp fda6fba3-26de-4533-ab37-f87bb8ca8965) ${p.GP10.str})
    (pad "15" thru_hole oval (at 8.82 11.43) (size 1.84 1.7) (drill oval 1.16 1.02) (layers *.Cu *.Mask) (tstamp db248dbe-bef4-43e0-991f-f8907ae081d4) ${p.GP11.str})
    (pad "16" thru_hole oval (at 8.82 13.97) (size 1.84 1.7) (drill oval 1.16 1.02) (layers *.Cu *.Mask) (tstamp 8b5154dc-4718-4a03-ad67-ed035a4319ce) ${p.GP12.str})
    (pad "17" thru_hole oval (at 8.82 16.51) (size 1.84 1.7) (drill oval 1.16 1.02) (layers *.Cu *.Mask) (tstamp eb64b7d2-d623-452c-9703-2bb0265ee337) ${p.GP13.str})
    (pad "18" thru_hole rect (at 8.82 19.05) (size 1.84 1.7) (drill oval 1.16 1.02) (layers *.Cu *.Mask) (tstamp f7386878-6bd2-49fb-be47-6588e913174b) ${p.GND.str})
    (pad "19" thru_hole oval (at 8.82 21.59) (size 1.84 1.7) (drill oval 1.16 1.02) (layers *.Cu *.Mask) (tstamp fa8076fb-ecc2-4918-a4f3-511178e9ad37) ${p.GP14.str})
    (pad "20" thru_hole oval (at 8.82 24.13) (size 1.84 1.7) (drill oval 1.16 1.02) (layers *.Cu *.Mask) (tstamp 4b6b7c47-5e11-4065-b26e-9c14c9c8ee50) ${p.GP15.str})
    (pad "21" thru_hole oval (at -8.82 24.13) (size 1.84 1.7) (drill oval 1.16 1.02) (layers *.Cu *.Mask) (tstamp 7a45c78c-faae-432b-8399-806250e23db7) ${p.GP16.str})
    (pad "22" thru_hole oval (at -8.82 21.59) (size 1.84 1.7) (drill oval 1.16 1.02) (layers *.Cu *.Mask) (tstamp 852f4f24-f0ec-4812-8953-10a1c9ba8b18) ${p.GP17.str})
    (pad "23" thru_hole rect (at -8.82 19.05) (size 1.84 1.7) (drill oval 1.16 1.02) (layers *.Cu *.Mask) (tstamp 6fbe5d8d-e43a-4207-a531-c4dfe41759ce) ${p.GND.str})
    (pad "24" thru_hole oval (at -8.82 16.51) (size 1.84 1.7) (drill oval 1.16 1.02) (layers *.Cu *.Mask) (tstamp 48f29450-601c-4f43-bede-558f16a2580a) ${p.GP18.str})
    (pad "25" thru_hole oval (at -8.82 13.97) (size 1.84 1.7) (drill oval 1.16 1.02) (layers *.Cu *.Mask) (tstamp 0cf035fe-7441-41a9-8ecd-8633f9511a86) ${p.GP19.str})
    (pad "26" thru_hole oval (at -8.82 11.43) (size 1.84 1.7) (drill oval 1.16 1.02) (layers *.Cu *.Mask) (tstamp 4aa34793-001c-422a-9a9e-f2fa24b7c918) ${p.GP20.str})
    (pad "27" thru_hole oval (at -8.82 8.89) (size 1.84 1.7) (drill oval 1.16 1.02) (layers *.Cu *.Mask) (tstamp 07bfbc8a-823e-44b5-ab95-5c0659fd56bb) ${p.GP21.str})
    (pad "28" thru_hole rect (at -8.82 6.35) (size 1.84 1.7) (drill oval 1.16 1.02) (layers *.Cu *.Mask) (tstamp 6fd23c62-f256-47b1-9fb2-80a0473029fb) ${p.GND.str})
    (pad "29" thru_hole oval (at -8.82 3.81) (size 1.84 1.7) (drill oval 1.16 1.02) (layers *.Cu *.Mask) (tstamp 0e54c542-e3a2-4db6-883d-37a3ad94739d) ${p.GP22.str})
    (pad "30" thru_hole oval (at -8.82 1.27) (size 1.84 1.7) (drill oval 1.16 1.02) (layers *.Cu *.Mask) (tstamp 49dcd950-fbab-4ac5-9a36-86d2c2a0259e) ${p.GP26.str})
    (pad "31" thru_hole oval (at -8.82 -1.27) (size 1.84 1.7) (drill oval 1.16 1.02) (layers *.Cu *.Mask) (tstamp 84cce8d0-f83b-4f08-af4b-1d62af837a54) ${p.GP27.str})
    (pad "32" thru_hole oval (at -8.82 -3.81) (size 1.84 1.7) (drill oval 1.16 1.02) (layers *.Cu *.Mask) (tstamp da79c04c-a207-48dc-a5d7-8a078322a160) ${p.GP28.str})
    (pad "33" thru_hole rect (at -8.82 -6.35) (size 1.84 1.7) (drill oval 1.16 1.02) (layers *.Cu *.Mask) (tstamp 9db6e273-f7b0-4ab9-9b75-cb2195ede133) ${p.GND.str})
    (pad "34" thru_hole oval (at -8.82 -8.89) (size 1.84 1.7) (drill oval 1.16 1.02) (layers *.Cu *.Mask) (tstamp 36be125c-d820-40b1-81f5-37cb6c4c1027) ${p.GP29.str})
    (pad "35" thru_hole oval (at -8.82 -11.43) (size 1.84 1.7) (drill oval 1.16 1.02) (layers *.Cu *.Mask) (tstamp 510cc5c4-e61c-4e17-93d1-bd10b62ad6fb) ${p.ADC_VREF.str})
    (pad "36" thru_hole oval (at -8.82 -13.97) (size 1.84 1.7) (drill oval 1.16 1.02) (layers *.Cu *.Mask) (tstamp 33256a6e-b053-471b-ac8e-081487946d0e) ${p.GP24.str})
    (pad "37" thru_hole oval (at -8.82 -16.51) (size 1.84 1.7) (drill oval 1.16 1.02) (layers *.Cu *.Mask) (tstamp ac928fb2-0ce9-4e34-8e2d-402b47a0d641) ${p._3V3.str})
    (pad "38" thru_hole rect (at -8.82 -19.05) (size 1.84 1.7) (drill oval 1.16 1.02) (layers *.Cu *.Mask) (tstamp cb792c93-111c-4188-a8ba-8930e71f97d8) ${p.GND.str})
    (pad "39" thru_hole oval (at -8.82 -21.59) (size 1.84 1.7) (drill oval 1.16 1.02) (layers *.Cu *.Mask) (tstamp b8260a4c-72c5-48e1-9736-d2140182d3fc) ${p.VSYS.str})
    (pad "40" thru_hole oval (at -8.82 -24.13) (size 1.84 1.7) (drill oval 1.16 1.02) (layers *.Cu *.Mask) (tstamp 1a60f562-a956-4d54-a00f-6201c5b12308) ${p.VBUS.str})
    )
    `
    }
  }
}


