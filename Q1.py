# %%
import numpy as np
from numpy.core.fromnumeric import prod, repeat
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
from DataMover import *
from Pe import *
from Agg import *

latency = 0

ifmaps, l0, l1, weights_0, weights_1 = get_network_maps()
pe_ifmaps = [ifmaps[0], ifmaps[1], ifmaps[2]]

single_ifmap_size = ifmaps[0].flatten().shape[0]
single_ofmap_size = single_ifmap_size
all_ifmaps = np.array(pe_ifmaps).flatten()
total_ifmaps_size = np.array(pe_ifmaps).flatten().shape[0]
total_ofmaps_size = total_ifmaps_size
pe_weights = [weights_0[0][0], weights_0[0][1], weights_0[0][2]]

memory = Memory(2, 1, 200, initialization_vals=all_ifmaps.tolist(), size=total_ifmaps_size+single_ofmap_size)

@block 
def q1_processor(clk, enable, mm2s_done, s2mm_done, agg_done):
    
    ifmap_in = Signal(0)
    ofmap_out = Signal(0)
    psums = Signal(0)
    agg_output = Signal(0)
    
    mm2s = datamover("mm2s", clk, enable, ifmap_in, memory.get_read_port(), [
        (range(9), lambda i: 0, lambda i: False),
        (range(single_ifmap_size), lambda i: i, lambda i: True),
        (range(227), lambda i: 0, lambda i: False),
        (range(9), lambda i: 0, lambda i: False),
        (range(single_ifmap_size), lambda i: i+single_ifmap_size, lambda i: True),
        (range(227), lambda i: 0, lambda i: False),
        (range(9), lambda i: 0, lambda i: False),
        (range(single_ifmap_size), lambda i: i+single_ifmap_size*2, lambda i: True),
        (range(227), lambda i: 0, lambda i: False)
    ], mm2s_done, mode = 'read')
    
    agg_loader = datamover("agg_loader", clk, enable, psums, memory.get_read_port(), [
        (range(9), lambda i: 0, lambda i: False),
        (range(224+2), lambda i: 0, lambda i: False),
        (range(single_ofmap_size), lambda i: i+total_ifmaps_size, lambda i: False),
        (range(1), lambda i: 0, lambda i: False),
        (range(9), lambda i: 0, lambda i: False),
        (range(224+2), lambda i: 0, lambda i: False),
        (range(single_ofmap_size), lambda i: i+total_ifmaps_size, lambda i: True),
        (range(1), lambda i: 0, lambda i: False),
        (range(9), lambda i: 0, lambda i: False),
        (range(224+2), lambda i: 0, lambda i: False),
        (range(single_ofmap_size), lambda i: i+total_ifmaps_size, lambda i: True)
    ], agg_done, mode = 'read')
    
    s2mm = datamover("s2mm", clk, enable, agg_output, memory.get_write_port(), [
        (range(1), lambda i: 0, lambda i: False), # agg delay
        (range(1), lambda i: 0, lambda i: False),
        (range(9), lambda i: 0, lambda i: False),
        (range(224+2), lambda i: 0, lambda i: False),
        (range(single_ofmap_size), lambda i: i+total_ifmaps_size, lambda i: True),
        (range(1), lambda i: 0, lambda i: False),
        (range(9), lambda i: 0, lambda i: False),
        (range(224+2), lambda i: 0, lambda i: False),
        (range(single_ofmap_size), lambda i: i+total_ifmaps_size, lambda i: True),
        (range(1), lambda i: 0, lambda i: False),
        (range(9), lambda i: 0, lambda i: False),
        (range(224+2), lambda i: 0, lambda i: False),
        (range(single_ofmap_size), lambda i: i+total_ifmaps_size, lambda i: True)
    ], s2mm_done, mode = 'write')
    
    conv_3_3 = pe(clk, memory, enable, pe_ifmaps, pe_weights, ifmap_in, ofmap_out)
    agg_0 = agg(clk, enable, psums, ofmap_out, agg_output)
    
    return mm2s, conv_3_3, s2mm, agg_0, agg_loader

@block
def q1_processor_tb():

    clk = Signal(True)
    enable = Signal(0)
    stop_sim = Signal(0)
    
    mm2s_done = Signal(0)
    s2mm_done = Signal(0)
    agg_done = Signal(0)
    q1 = q1_processor(clk, enable, mm2s_done, s2mm_done, agg_done)
    
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
        global latency
        enable.next = True
        stop_sim.next = False
        yield clk.posedge
        yield s2mm_done
        stop_sim.next = True
        latency = now()
        yield clk.posedge

    return clk_driver, q1, stimulus


if __name__ == '__main__':
    print("Running Q1 testbench")
    inst = q1_processor_tb()
    inst = traceSignals(inst)
    inst.run_sim()
    print("To process one filter")
    print("Data Transfer Energy: {}".format(memory.compute_energy_cost()))
    print("Number of read accesses: {}".format(memory.read_request_count))
    print("Number of write accesses: {}".format(memory.write_request_count))
    print("Total Latency In Cycles: {}".format(latency/2))
