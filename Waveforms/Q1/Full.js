{ signal: [
    { name: "clk", wave: 'P................' },
    { name: "Conv_3_3 [state]", wave: '==..=...|=..|=..|', data: ["Start", "Load Weights Fi_Cj  9 cycles", "Pipeline Delay (Pad) 451 cycles             ", "Valid_Output (222x224) cycles", "Pad 224 cycles", "Compute"]},
    { name: 'dram_read_p_0[ifmap_c_i] -> Conv_3_3[ifmap]', wave: 'x=.x345.|345|=..|', data: ["Load Weights Fi_Cj", "[0,0]", "[0,1]", "[0,2]", "[1,0]", "[1,1]", "[1,2]", "0", "[2,4]", "[2,5]", "[2,6]", "[2,223]", "Delay", "[3,0]", "[3,1]", "[3,2]", "[3,3]", "[3,4]", "[223, 222]", "[223, 223]"] },
    { name: "Conv_3_3[output] -> AGG[Input_0]", wave: 'x...=...|345|=..|', data: ["0", "[0,0]", "[0,1]", "[0,2]", "0", "[0, 220]", "[0,221]", "0", "[1,0]", "[1,1]", "[221, 219]", "[221, 220]", "[221, 221]"]},
    { name: 'dram_read_p_1 [psums] -> AGG[Input_1]', wave: 'x...=.=.|=..|=..|', data: [ "Start @224 cycles","psums (Fi_C(j-1))", "psums (Fi_C(j-1))",  "psums (Fi_C(j-1))", "[0,2]", "[1,0]", "[1,1]", "[1,2]", "[1,3]", "[2,4]", "[2,5]", "[2,6]", "[2,223]", "Delay", "[3,0]", "[3,1]", "[3,2]", "[3,3]", "[3,4]", "[223, 222]", "[223, 223]"] },
    { name: "AGG [ofmap/psums] -> dram_write_w_0", wave: 'x...=.=.|=..|=..|', data: ["Start @224 cycles", "[0,0]", "psums (Fi_Cj)", "psums (Fi_Cj)", "[0, 219]", "[0, 220]", "[0,221]", "0", "[1,0]", "[1,1]", "[221, 219]", "[221, 220]", "[221, 221]"]},
    { name: "dram_write_w_0 [ofmap]", wave: 'x.....=.|=..|=..|', data: ["[0,0]", "psums (Fi_Cj)", "psums (Fi_Cj)", "[0,2]", "[0, 219]", "[0, 220]", "[0,221]", "0", "[1,0]", "[1,1]", "[221, 219]", "[221, 220]", "[221, 221]"]},
    ],
    // edge: [
    //   'a|->b', 'b-c',
    //   'd|->e', 'e-f',
    //   'g|->h', 'h-i',
    // ],
    config: { hscale: 1.5 }
  }
  
  