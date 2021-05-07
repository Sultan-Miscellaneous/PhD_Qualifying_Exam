# %%
import numpy as np
from myhdl import block, Signal, delay, always, instance, traceSignals
from numpy.lib.stride_tricks import sliding_window_view
from itertools import product as vanilla_product
from tqdm.contrib.itertools import product
from collections import Counter
import pickle
from collections import defaultdict
from functools import partial

rcvd_output = []
with open("./pe_golden", 'rb') as golden_file:
    expected_output = pickle.load(golden_file)
    
class Memory:
    def __init__(self, read_port_count, write_port_count, access_cost, initialization_vals = None, size=None):
        self.storage = [0]*size if size is not None else defaultdict(lambda: 0)
        self.available_read_ports = read_port_count
        self.available_write_ports = write_port_count
        self.access_cost = access_cost
        self.request_count = 0
        if initialization_vals is not None:
            self.initialize(initialization_vals)
        
    def initialize(self, vals):
        for idx, val in enumerate(vals):
            self.storage[idx] = vals

    def get_write_port(self):
        if self.available_write_ports > 0:
            self.available_write_ports -= 1
            return self.write
        else:
            raise Exception("Too many write ports requested... aborting...")

    def get_read_port(self):
        if self.available_read_ports > 0:
            self.available_read_ports -= 1
            return self.read
        else:
            raise Exception("Too many read ports requested... aborting...")

    def read(self, port_index):
        self.request_count += 1
        return self.storage[port_index]

    def write(self, addr, data):
        self.storage[addr] = data
        self.request_count += 1
    
    def compute_energy_cost(self):
        return self.request_count*self.access_cost


@block
def memory_tb():
    clk = Signal(0)
    stop_sim = Signal(0)

    dut = Memory(2, 2, 200)
    dut_read_ports = {0: dut.get_read_port(), 1: dut.get_read_port()}
    dut_write_ports = {0: dut.get_write_port(), 1: dut.get_write_port()}

    @instance
    def clk_driver():
        while True:
            yield delay(1)
            if not stop_sim:
                clk.next = not clk
            else:
                break

    @instance
    def testbench():
        stop_sim.next = False
        yield clk.posedge
        addr = 0
        for (i, j) in product(range(100), range(0,100,2), desc="Writing to Mem"):
            dut_write_ports[0](addr, i*100+j)
            dut_write_ports[1](addr+1, 0)
            addr += 2
            yield clk.posedge
        addr = 0
        for (i, j) in product(range(100), range(0,100,2), desc="Reading from Mem"):
            if dut_read_ports[0](addr) != i*100+j or dut_read_ports[1](addr+1) != 0:
                print("\nMemory test failed")
                break
            addr += 2
            yield clk.posedge
        print("\nMemory Test passed")
        stop_sim.next = True
        

    return clk_driver, testbench
 
@block
def agg(clk, enable, input_0, input_1, output):

    @always(clk.posedge)
    def compute():
        if enable:
            output.next = input_0.val + input_1.val

    return compute

@block
def datamover(clk, enable, data, port, program, mode = 'read'):
    
    def apply_access(iteration_vector, access_map):
        access_idx = 0
        for iteration_dim, constant in zip(iteration_vector, access_map[:-1]):
            access_idx += (iteration_dim*constant)
        access_idx += access_map[-1]
        return access_idx
 
    @always(clk.posedge)
    def access_mem():
        if enable:
            for (domain, access_map, condition) in program:
                for iteration_vector in domain:
                    if condition(iteration_vector):
                        access_idx = apply_access(iteration_vector, access_map)
                        if mode == 'read':
                            data.next = port(access_idx)
                        else:
                            port(access_idx, data.val)
                        
    
    return access_mem
 
@block
def pe(clk, enable, pad_origin, pads, weights, ifmap_in, ofmap_out):

    pad_completion_counter = Counter()

    @always(clk.posedge)
    def compute():
        if enable:
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

    return compute

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
        global rcvd_output
        while(True):
            yield ofmap_out
            if enable:
                rcvd_output.append(ofmap_out.val)
                # print("ofmal_out changed! ofmap_out:{}".format(ofmap_out.val))
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


inst = pe_tb()
# inst = traceSignals(inst)
inst.run_sim()

# %%
