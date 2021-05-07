# %%
from myhdl import block, Signal, delay, always, instance
from tqdm.contrib.itertools import product

@block
def agg(clk, enable, input_0, input_1, output):

    @always(clk.posedge)
    def compute():
        if enable:
            output.next = input_0.val + input_1.val

    return compute

@block
def agg_tb():
    clk = Signal(0)
    input_0 = Signal(0)
    input_1 = Signal(0)
    output_0 = Signal(0)
    enable = Signal(0)
    stop_sim = Signal(0)

    dut = agg(clk, enable, input_0, input_1, output_0)

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
        for i,j in product(range(100), range(100)):
            input_0.next = i
            input_1.next = j
            yield clk.posedge
            if(output_0.val != i+j):
                raise Exception("Agg testbench failed... aborting...")
        print("Agg testbench pass")
        
        
    return clk_driver, stimulus, dut

 
if __name__ == '__main__':
    print("Running AGG testbench")
    inst = agg_tb()
    inst.run_sim()