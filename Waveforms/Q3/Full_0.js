{ signal: [
  { name: "clk", wave: 'P..............................' },
  { name: "Conv_3_3_0 [state]", wave: 'xxxx==..=........=...|=........', data: ["Start", "Weights F0_C0", "Sync", "Pipeline Delay (451) ", "ofmap(222x224)    "]},
  { name: "Conv_3_3_1 [state]", wave: 'xxxx==..=........=...|=........', data: ["Start", "Weights F0_C1", "Sync", "Pipeline Delay (451) ", "ofmap(222x224)    "]},
  { name: "Conv_3_3_2 [state]", wave: 'xxxxx..==..=.....=...|=........', data: ["Start", "Weights F0_C2", "Sync", "Pipeline Delay (451) ", "ofmap(222x224)    "]},
  { name: "Conv_3_3_3 [state]", wave: 'xxxxx..==..=.....=...|=........', data: ["Start", "Weights F0_C3", "Sync", "Pipeline Delay (451) ", "ofmap(222x224)    "]},
  { name: "Conv_3_3_4 [state]", wave: 'xxxxx.....==..=..=...|=........', data: ["Start", "Weights F1_C0", "Sync", "Pipeline Delay (451) ", "ofmap(222x224)    "]},
  { name: "Conv_3_3_5 [state]", wave: 'xxxxx.....==..=..=...|=........', data: ["Start", "Weights F1_C1", "Sync", "Pipeline Delay (451) ", "ofmap(222x224)    "]},
  { name: "Conv_3_3_6 [state]", wave: 'xxxxx........==..=...|=........', data: ["Start", "Weights F1_C2", "Pipeline Delay (451) ", "ofmap(222x224)    "]},
  { name: "Conv_3_3_7 [state]", wave: 'xxxxx........==..=...|=........', data: ["Start", "Weights F1_C3", "Pipeline Delay (451) ", "ofmap(222x224)    "]},
  // { name: 'dram_r_p_0[ifmap_C_0 & ifmap_C_1] -> Buffer', wave: '=....xxxxxxxxxxxxxxxxxxxxxxxxxx', data: ["Transfer Ifmap (224x224x2)", "[0,1]", "[0,2]", "[1,0]", "[1,1]", "[1,2]", "0", "[2,4]", "[2,5]", "[2,6]", "[2,223]", "Delay", "[3,0]", "[3,1]", "[3,2]", "[3,3]", "[3,4]", "[223, 222]", "[223, 223]"] },
  // { name: 'dram_r_p_1[ifmap_C_2 & ifmap_C_3] -> Buffer', wave: '=....xxxxxxxxxxxxxxxxxxxxxxxxxx', data: ["Transfer Ifmap (224x224x2)", "[0,1]", "[0,2]", "[1,0]", "[1,1]", "[1,2]", "0", "[2,4]", "[2,5]", "[2,6]", "[2,223]", "Delay", "[3,0]", "[3,1]", "[3,2]", "[3,3]", "[3,4]", "[223, 222]", "[223, 223]"] },
  { name: 'buffer_r_i [ifmap_ci] -> Conv_3_3_i & Conv_3_3_(i+4)', wave: 'xxxxxxxxxxxxxxxxx345.|345|xxxxx', data: ["[i,0,0]", "[i,0,1]", "[i,0,1]", "[i,0,2]", "[i,2,0]", "[i,2,1]", "[i,2,2]", "0", "[2,4]", "[2,5]", "[2,6]", "[2,223]", "Delay", "[3,0]", "[3,1]", "[3,2]", "[3,3]", "[3,4]", "[223, 222]", "[223, 223]"] },
  { name: "AGG [Ofmap_Fj] -> buffer_w_j", wave: 'x.......................=.....x', data: ["AGG & Filter Fj", "[0,0]", "psums (Fi_Cj)", "psums (Fi_Cj)", "[0, 219]", "[0, 220]", "[0,221]", "0", "[1,0]", "[1,1]", "[221, 219]", "[221, 220]", "[221, 221]"]},
  { name: "buffer_r_0 -> dram_w_p_0 [ofmap]", wave: 'x........................=.....', data: ["Transfer ofmap (224x224)", "[0,0]", "psums (Fi_Cj)", "psums (Fi_Cj)", "[0, 219]", "[0, 220]", "[0,221]", "0", "[1,0]", "[1,1]", "[221, 219]", "[221, 220]", "[221, 221]"]},
  { name: "buffer_r_1 -> dram_w_p_1 [ofmap]", wave: 'x........................=.....', data: ["Transfer ofmap (224x224)", "[0,0]", "psums (Fi_Cj)", "psums (Fi_Cj)", "[0, 219]", "[0, 220]", "[0,221]", "0", "[1,0]", "[1,1]", "[221, 219]", "[221, 220]", "[221, 221]"]},
  ],
  // edge: [
  //   'a|->b', 'b-c',
  //   'd|->e', 'e-f',
  //   'g|->h', 'h-i',
  // ],
  config: { hscale: 1 }
}

