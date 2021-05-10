
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

memory = Memory(1, 1, 200, initialization_vals=all_ifmaps.tolist())
buffer = Memory(1, 2, 6, size=total_ifmaps_size+single_ofmap_size)

@block 
def q2_processor(clk, enable, done):
    
    mm2s_data = Signal(0)
    ifmap_in = Signal(0)
    ofmap_out = Signal(0)
    psums = Signal(0)
    agg_output = Signal(0)
    pe_enable = Signal(0)
    
    # mm2s = datamover("mm2s", clk, enable, mm2s_data, memory.get_read_port(), [
    #     (range(9), lambda i: 0, lambda i: False),
    #     (range(single_ifmap_size), lambda i: i, lambda i: True),
    #     (range(227), lambda i: 0, lambda i: False),
    #     (range(9), lambda i: 0, lambda i: False),
    #     (range(single_ifmap_size), lambda i: i+single_ifmap_size, lambda i: True),
    #     (range(227), lambda i: 0, lambda i: False),
    #     (range(9), lambda i: 0, lambda i: False),
    #     (range(single_ifmap_size), lambda i: i+single_ifmap_size*2, lambda i: True),
    #     (range(227), lambda i: 0, lambda i: False)
    # ], mode = 'read')

    # s2buffer = datamover("s2buffer", clk, enable, mm2s_data, buffer.get_write_port(), [
    #     (range(1), lambda i: 0, lambda i: False),
    #     (range(9), lambda i: 0, lambda i: False),
    #     (range(single_ifmap_size), lambda i: i, lambda i: True),
    #     (range(227), lambda i: 0, lambda i: False),
    #     (range(9), lambda i: 0, lambda i: False),
    #     (range(single_ifmap_size), lambda i: i+single_ifmap_size, lambda i: True),
    #     (range(227), lambda i: 0, lambda i: False),
    #     (range(9), lambda i: 0, lambda i: False),
    #     (range(single_ifmap_size), lambda i: i+single_ifmap_size*2, lambda i: True),
    #     (range(227), lambda i: 0, lambda i: False)
    # ], mode = 'write')

    buffer2pe = datamover("buffer2pe", clk, enable, ifmap_in, memory.get_read_port(), [
        (range(1), lambda i: 0, lambda i: False, True),
        (range(9), lambda i: 0, lambda i: False),
        (range(single_ifmap_size), lambda i: i, lambda i: True),
        (range(227), lambda i: 0, lambda i: False),
        (range(9), lambda i: 0, lambda i: False),
        (range(single_ifmap_size), lambda i: i+single_ifmap_size, lambda i: True),
        (range(227), lambda i: 0, lambda i: False),
        (range(9), lambda i: 0, lambda i: False),
        (range(single_ifmap_size), lambda i: i+single_ifmap_size*2, lambda i: True),
        # reload same ifmaps at same location because it effectively doesn't matter
        # they were written twice to memory because the list needs to have them repeated 
        # for pytorch to calculate expected outputs
        # (range(227), lambda i: 0, lambda i: False),
        # (range(9), lambda i: 0, lambda i: False, True),
        # (range(single_ifmap_size), lambda i: i, lambda i: True),
        # (range(227), lambda i: 0, lambda i: False),
        # (range(9), lambda i: 0, lambda i: False),
        # (range(single_ifmap_size), lambda i: i+single_ifmap_size, lambda i: True),
        # (range(227), lambda i: 0, lambda i: False),
        # (range(9), lambda i: 0, lambda i: False),
        # (range(single_ifmap_size), lambda i: i+single_ifmap_size*2, lambda i: True),
        # (range(227), lambda i: 0, lambda i: False)
    ], output_enable = pe_enable, mode = 'read')
    
    agg_loader = datamover("agg_loader", clk, enable, psums, buffer.get_read_port(), [
        (range(1), lambda i: 0, lambda i: False), # agg delay
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
        (range(single_ofmap_size), lambda i: i+total_ifmaps_size, lambda i: True),
        # (range(1), lambda i: 0, lambda i: False),
        # (range(9), lambda i: 0, lambda i: False),
        # (range(224+2), lambda i: 0, lambda i: False),
        # (range(single_ofmap_size), lambda i: i+total_ifmaps_size, lambda i: True),
        # (range(1), lambda i: 0, lambda i: False),
        # (range(9), lambda i: 0, lambda i: False),
        # (range(224+2), lambda i: 0, lambda i: False),
        # (range(single_ofmap_size), lambda i: i+total_ifmaps_size, lambda i: True),
        # (range(1), lambda i: 0, lambda i: False),
        # (range(9), lambda i: 0, lambda i: False),
        # (range(224+2), lambda i: 0, lambda i: False),
        # (range(single_ofmap_size), lambda i: i+total_ifmaps_size, lambda i: True)
    ], mode = 'read')
    
    agg_writeback = datamover("agg_writeback", clk, enable, agg_output, buffer.get_write_port(), [
        (range(2), lambda i: 0, lambda i: False), # agg delay
        (range(1), lambda i: 0, lambda i: False),
        (range(9), lambda i: 0, lambda i: False),
        (range(224+2), lambda i: 0, lambda i: False),
        (range(single_ofmap_size), lambda i: i+total_ifmaps_size, lambda i: True),
        (range(1), lambda i: 0, lambda i: False),
        (range(9), lambda i: 0, lambda i: False),
        (range(224+2), lambda i: 0, lambda i: False),
        (range(single_ofmap_size), lambda i: i+total_ifmaps_size, lambda i: True),
        # (range(1), lambda i: 0, lambda i: False),
        # (range(9), lambda i: 0, lambda i: False),
        # (range(224+2), lambda i: 0, lambda i: False),
        # (range(single_ofmap_size), lambda i: i+total_ifmaps_size, lambda i: True),
        # (range(1), lambda i: 0, lambda i: False),
        # (range(9), lambda i: 0, lambda i: False),
        # (range(224+2), lambda i: 0, lambda i: False),
        # (range(single_ofmap_size), lambda i: i+total_ifmaps_size, lambda i: True),
        # (range(1), lambda i: 0, lambda i: False),
        # (range(9), lambda i: 0, lambda i: False),
        # (range(224+2), lambda i: 0, lambda i: False),
        # (range(single_ofmap_size), lambda i: i+total_ifmaps_size, lambda i: True),
        # (range(1), lambda i: 0, lambda i: False),
        # (range(9), lambda i: 0, lambda i: False),
        # (range(224+2), lambda i: 0, lambda i: False),
        # (range(single_ofmap_size), lambda i: i+total_ifmaps_size, lambda i: True)
    ], mode = 'write')

    s2mm = datamover("s2mm", clk, enable, agg_output, memory.get_write_port(), [
        # (range(252062), lambda i: 0, lambda i: False), # agg delay
        (range(100826), lambda i: 0, lambda i: False), # agg delay
        (range(1), lambda i: 0, lambda i: False),
        (range(9), lambda i: 0, lambda i: False),
        (range(224+2), lambda i: 0, lambda i: False),
        (range(single_ofmap_size), lambda i: i+total_ifmaps_size, lambda i: True)
    ], done = done, mode = 'write')

    agg_0 = agg(clk, enable, psums, ofmap_out, agg_output)
    
    conv_3_3 = pe(clk, memory, pe_enable, pe_ifmaps, pe_weights, ifmap_in, ofmap_out)
    
    return buffer2pe, conv_3_3, agg_0, agg_writeback, agg_loader, s2mm

@block
def q2_processor_tb():

    clk = Signal(True)
    enable = Signal(0)
    stop_sim = Signal(0)
    s2mm_done = Signal(0)
    q2 = q2_processor(clk, enable, s2mm_done)
    
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
        latency = now()
        stop_sim.next = True
        yield clk.posedge

    return clk_driver, q2, stimulus


if __name__ == '__main__':
    print("Running PE testbench")
    inst = q2_processor_tb()
    inst = traceSignals(inst, directory="vcd")
    inst.run_sim()
    print("For two filters")
    print("DRAM Transfer Energy: {}".format(memory.compute_energy_cost()))
    print("Buffer Transfer Energy: {}".format(buffer.compute_energy_cost()))
    print("Total Data Transfer Energy: {}".format(memory.compute_energy_cost()+buffer.compute_energy_cost()))
    print("Number of read memory accesses: {}".format(memory.read_request_count))
    print("Number of write memory accesses: {}".format(memory.write_request_count))
    print("Number of read buffer accesses: {}".format(buffer.read_request_count))
    print("Number of write buffer accesses: {}".format(buffer.write_request_count))
    print("Total Latency In Cycles: {}".format(latency/2))
