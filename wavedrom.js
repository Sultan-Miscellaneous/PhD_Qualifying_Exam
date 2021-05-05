{ signal: [
  { name: "clk", wave: 'P..|...|...................' },
  { name: 'dram_read_p_0 [ifmap]', wave: '345|678|=', data: ["[0,0]", "[0,1]", "[0,2]", "[2,2]", "[2,3]", "[2,4]", "[3,0]", "[3,1]"] },
  { name: "Conv_3_3 [state]", wave: '=...=..|=', data: ["pipeline delay @450 cycles", "Compute", "Pad+Compute"]},
  { name: "Conv_3_3 [ofmap]", wave: '=.|.345', data: ["Pad 0", "[0,0]", "[0,1]", "[0,2]"]},
  ],
  config: { hscale: 3 }
}

