# %%
import numpy as np
from numpy.core.fromnumeric import prod
from numpy.lib.stride_tricks import sliding_window_view
from itertools import product as quite_product
import torch
from tqdm.contrib.itertools import product
from collections import Counter
import pickle
import torch.nn as nn
import torch.nn.functional as F
import numpy as np

from myhdl import block, Signal, delay, always, instance, traceSignals, enum, now
from Memory import *
from Maps import *

def clk_delay(val):
    return delay(val*2)

@block
def pe(clk, memory, enable, ifmaps, weights, ifmap_in, ofmap_out):

    states = enum('LOAD', 'IDLE', 'COMPUTE')
    
    current_state = Signal(states.LOAD)
    input_counter = Signal(0)
    current_fmap_index = Signal(0)
    output_counter = Signal(0)
    
    def precompute_ofmaps(ifmaps, weights):
        ofmaps = []
        for ifmap, weight in zip(ifmaps, weights):
            ifmap = torch.tensor(ifmap).unsqueeze(0).unsqueeze(0)
            weight = torch.tensor(weight).unsqueeze(0).unsqueeze(0)
            ofmap = F.pad(F.conv2d(ifmap, weight), (1,1,1,1)).squeeze().numpy()
            ofmaps.append(ofmap)
        return ofmaps
    
    
    ofmaps = precompute_ofmaps(ifmaps, weights)      

    @instance
    def validate_input():
        while True:
            if enable:
                if current_state.val == states.LOAD:
                    input_counter.next = 0
                elif current_state.val == states.IDLE or current_state.val == states.COMPUTE:
                    if input_counter.val < ifmaps[current_fmap_index.val].flatten().shape[0]:
                        if ifmap_in.val != ifmaps[current_fmap_index.val].flatten()[input_counter.val]:
                            raise Exception("Invalid ifmap input recieved... aborting...")
                        input_counter.next = input_counter.val + 1
            
            yield clk.posedge
    
    @instance
    def compute_output():
        nonlocal current_state
        current_fmap_index.next = 0
        while True:
            if enable:
                if current_state.val == states.LOAD:
                    memory.fake_access(9)
                    for _ in range(9):
                        yield clk.posedge
                    current_state.next = states.IDLE
                    yield clk.posedge
                    
                elif current_state.val == states.IDLE:
                    for _ in range(224):
                        yield clk.posedge
                    current_state.next = states.COMPUTE
                    output_counter.next = 0
                    yield clk.posedge
                        
                elif current_state.val == states.COMPUTE:
                    ofmap_out.next = ofmaps[current_fmap_index].flatten()[output_counter.val].item()
                    output_counter.next = output_counter.val + 1
                    if output_counter.val == ((224*224)-1):
                        yield clk.posedge # clock out last output
                        current_state.next = states.LOAD
                        current_fmap_index.next = current_fmap_index.val + 1
                        output_counter.next = 0
                    yield clk.posedge
            else:
                yield clk.posedge
            
            
    return compute_output, validate_input


@block
def pe_tb():

    clk = Signal(True)
    enable = Signal(0)
    stop_sim = Signal(0)
    ifmap_in = Signal(0)
    ofmap_out = Signal(0)
    
    memory = Memory(2, 2, 200)

    ifmaps, l0, l1, weights_0, weights_1 = get_network_maps()
    pe_ifmaps = [ifmaps[0], ifmaps[1], ifmaps[2]]
    pe_weights = [weights_0[0][0], weights_0[0][1], weights_0[0][2]]
    dut = pe(clk, memory, enable, pe_ifmaps, pe_weights, ifmap_in, ofmap_out)

    @instance
    def clk_driver():
        while True:
            yield delay(1)
            if not stop_sim:
                clk.next = not clk
            else:
                break

    @instance
    def stimulus():
        yield clk.posedge
        ifmap_in.next = -1
        enable.next = True
        stop_sim.next = False
        yield clk.posedge
        for ifmap in pe_ifmaps:
            for _ in range(9):
                yield clk.posedge
            for val in ifmap.flatten():
                ifmap_in.next = val.item()
                yield clk.posedge
            yield clk.posedge # clk out last input
            for _ in range(226): # 2 cycle 
                yield clk.posedge
        enable.next = False
        stop_sim.next = True

    return clk_driver, stimulus, dut


if __name__ == '__main__':
    print("Running PE testbench")
    inst = pe_tb()
    inst = traceSignals(inst)
    inst.run_sim()
