# %%
import numpy as np
from myhdl import block, Signal, delay, instance
from tqdm.contrib.itertools import product
from collections import defaultdict
    
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
            self.storage[idx] = val

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
    
    def fake_access(self, count):
        self.request_count += count


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
                raise Exception("\nMemory test failed")
            addr += 2
            yield clk.posedge
        print("\nMemory Test passed")
        stop_sim.next = True
        

    return clk_driver, testbench
 
 
if __name__ == '__main__':
    print("Running Memory testbench")
    inst = memory_tb()
    inst.run_sim()
    
    
    