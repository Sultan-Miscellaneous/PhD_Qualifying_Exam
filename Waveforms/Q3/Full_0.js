{ signal: [
  { name: "clk", wave: 'P.........................' },
  { name: "Conv_3_3_0 [state]", wave: 'xxxx==..=........=...|=...', data: ["Start", "Weights F0_C0", "Sync", "Pipeline Delay (451) ", "ofmap(222x224)    "]},
  { name: "Conv_3_3_4 [state]", wave: 'xxxx==..=........=...|=...', data: ["Start", "Weights F0_C1", "Sync", "Pipeline Delay (451) ", "ofmap(222x224)    "]},
  { name: "Conv_3_3_1 [state]", wave: 'xxxxx..==..=.....=...|=...', data: ["Start", "Weights F0_C2", "Sync", "Pipeline Delay (451) ", "ofmap(222x224)    "]},
  { name: "Conv_3_3_5 [state]", wave: 'xxxxx..==..=.....=...|=...', data: ["Start", "Weights F0_C4", "Sync", "Pipeline Delay (451) ", "ofmap(222x224)    "]},
  { name: "Conv_3_3_2 [state]", wave: 'xxxxx.....==..=..=...|=...', data: ["Start", "Weights F1_C0", "Sync", "Pipeline Delay (451) ", "ofmap(222x224)    "]},
  { name: "Conv_3_3_6 [state]", wave: 'xxxxx.....==..=..=...|=...', data: ["Start", "Weights F1_C1", "Sync", "Pipeline Delay (451) ", "ofmap(222x224)    "]},
  { name: "Conv_3_3_3 [state]", wave: 'xxxxx........==..=...|=...', data: ["Start", "Weights F1_C2", "Pipeline Delay (451) ", "ofmap(222x224)    "]},
  { name: "Conv_3_3_7 [state]", wave: 'xxxxx........==..=...|=...', data: ["Start", "Weights F1_C3", "Pipeline Delay (451) ", "ofmap(222x224)    "]},
  { name: 'dram_read_p_0[ifmap_C] -> Buffer', wave: '=....xxxxxxxxxxxxxxxxxxxxxxxxx', data: ["Transfer Ifmap (224x224x3/2)", "[0,1]", "[0,2]", "[1,0]", "[1,1]", "[1,2]", "0", "[2,4]", "[2,5]", "[2,6]", "[2,223]", "Delay", "[3,0]", "[3,1]", "[3,2]", "[3,3]", "[3,4]", "[223, 222]", "[223, 223]"] },
  { name: 'dram_read_p_1[ifmap_C] -> Buffer', wave: '=....xxxxxxxxxxxxxxxxxxxxxxxxx', data: ["Transfer Ifmap (224x224x3/2)", "[0,1]", "[0,2]", "[1,0]", "[1,1]", "[1,2]", "0", "[2,4]", "[2,5]", "[2,6]", "[2,223]", "Delay", "[3,0]", "[3,1]", "[3,2]", "[3,3]", "[3,4]", "[223, 222]", "[223, 223]"] },
  { name: 'Buffer [ifmap_ci] -> Conv_3_3_i & Conv_3_3_(i+4)', wave: 'xxxxxxxxxxxxxxxxx345.|345|=..|', data: ["[i,0,1]", "[i,0,1]", "[i,0,2]", "[i,2,0]", "[i,2,1]", "[i,2,2]", "0", "[2,4]", "[2,5]", "[2,6]", "[2,223]", "Delay", "[3,0]", "[3,1]", "[3,2]", "[3,3]", "[3,4]", "[223, 222]", "[223, 223]"] },
  { name: 'Conv_3_3_(i) -> AGG[Input_0]', wave: 'x...=...|=..|=..|', data: [ "ofmap_Fi_C", "psums (Fi_C(j-1))",  "psums (Fi_C(j-1))", "[0,2]", "[1,0]", "[1,1]", "[1,2]", "[1,3]", "[2,4]", "[2,5]", "[2,6]", "[2,223]", "Delay", "[3,0]", "[3,1]", "[3,2]", "[3,3]", "[3,4]", "[223, 222]", "[223, 223]"] },
  { name: 'Conv_3_3_(i+4) -> AGG[Input_1]', wave: 'x...=...|=..|=..|', data: [ "psums (Fi_C(j-1))", "psums (Fi_C(j-1))",  "psums (Fi_C(j-1))", "[0,2]", "[1,0]", "[1,1]", "[1,2]", "[1,3]", "[2,4]", "[2,5]", "[2,6]", "[2,223]", "Delay", "[3,0]", "[3,1]", "[3,2]", "[3,3]", "[3,4]", "[223, 222]", "[223, 223]"] },
  { name: "AGG [ofmap/psums] -> dram_write_w_0", wave: 'x...=.=.|=..|=..|', data: ["Start @224 cycles", "[0,0]", "psums (Fi_Cj)", "psums (Fi_Cj)", "[0, 219]", "[0, 220]", "[0,221]", "0", "[1,0]", "[1,1]", "[221, 219]", "[221, 220]", "[221, 221]"]},
  { name: "buffer_r_0 [ofmap]", wave: 'x.....=.|=..|=..|', data: ["[0,0]", "psums (Fi_Cj)", "psums (Fi_Cj)", "[0,2]", "[0, 219]", "[0, 220]", "[0,221]", "0", "[1,0]", "[1,1]", "[221, 219]", "[221, 220]", "[221, 221]"]},
  { name: "dram_write_p_0 [ofmap]", wave: 'x......=|=..|=..|', data: ["[0,0]", "ofmap (Fi)", "ofmap (Fi)", "[0,2]", "[0, 219]", "[0, 220]", "[0,221]", "0", "[1,0]", "[1,1]", "[221, 219]", "[221, 220]", "[221, 221]"]},
  ],
  // edge: [
  //   'a|->b', 'b-c',
  //   'd|->e', 'e-f',
  //   'g|->h', 'h-i',
  // ],
  config: { hscale: 1 }
}

