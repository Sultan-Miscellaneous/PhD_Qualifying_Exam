import numpy as np
from myhdl import block, Signal, delay, always, instance, traceSignals
from numpy.lib.stride_tricks import sliding_window_view
from itertools import product as vanilla_product
from tqdm.contrib.itertools import product
from collections import Counter
import pickle

@block
def pe(clk, weights_load, memory, enable, pad_origin, pads, all_weights, ifmap_in, ofmap_out):

    current_weight_index = 0
    weights = all_weights[0]
    pad_completion_counter = Counter()

    @instance
    def load_new_weights():
        while True:
            yield weights_load
            pad_completion_counter.clear()
            current_weight_index += 1
            weights = all_weights[current_weight_index]
            memory.fake_access(9)
            yield delay(9)

    @always(clk.posedge)
    def compute():
        if enable and not weights_load:
            output_added = False
            for assosciated_pads in pad_origin[ifmap_in.val]:
                pad_idx = assosciated_pads['pad_idx']
                pad_completion_counter[pad_idx] += 1
                if pad_completion_counter[pad_idx] == 9:
                    ofmap_out.next = np.einsum(
                        'ij,ij', pads[pad_idx], weights.squeeze()).item()
                    output_added = True
            if not output_added:
                ofmap_out.next = 0

    return compute, load_new_weights

@block
def pe_tb():

    weights_M = 3
    weights_N = 3
    ifmap_M = 224
    ifmap_N = 224
    channels = 1

    clk = Signal(0)
    enable = Signal(0)
    stop_sim = Signal(0)
    ifmap_in = Signal(0)
    ofmap_out = Signal(0)

    def load_ifmap():
        ifmap = np.arange(channels*ifmap_M *
                          ifmap_N).reshape(channels, ifmap_M, ifmap_N)
        pads = sliding_window_view(ifmap, window_shape=[1, 3, 3]).squeeze()
        pad_origin = {}
        for p_i, p_j in product(range(pads.shape[0]), range(pads.shape[1]), desc="Loading ifmap"):
            for w_i, w_j in vanilla_product(range(pads.shape[2]), range(pads.shape[3])):
                cur_ifmap = pads[p_i, p_j, w_i, w_j]
                origin = {"pad_idx": (p_i, p_j), "weight_idx": (w_i, w_j)}
                if cur_ifmap not in pad_origin.keys():
                    pad_origin[cur_ifmap] = [origin]
                else:
                    pad_origin[cur_ifmap].append(origin)
        return ifmap, pads, pad_origin

    ifmap, pads, pad_origin = load_ifmap()
    weights = np.arange(channels*weights_M *
                        weights_N).reshape(channels, weights_M, weights_N)

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
        enable.next = True
        stop_sim.next = False
        yield clk.posedge
        for k, i, j in product(range(channels), range(ifmap_M), range(ifmap_N), desc="Pushing ifmap"):
            ifmap_in.next = ifmap[k][i][j].item()
            yield clk.posedge
        yield clk.posedge  # for last input
        enable.next = False
        stop_sim.next = True

    @instance
    def monitor():
        rcvd_output = []
        with open("./pe_golden", 'rb') as golden_file:
            expected_output = pickle.load(golden_file)
        while(True):
            yield ofmap_out
            if enable:
                rcvd_output.append(ofmap_out.val)
            if stop_sim:
                break
        rcvd_output = [val for val in rcvd_output if val > 0]
        print("\n")
        if rcvd_output == expected_output:
            print("Testbench pass")
        else:
            print("Testbench fail")

    dut = pe(clk, enable, pad_origin, pads, weights, ifmap_in, ofmap_out)

    return clk_driver, stimulus, monitor, dut


if __name__ == '__main__':
    print("Running PE testbench")
    inst = pe_tb()
    inst.run_sim()
