# %%
from myhdl import block, Signal, delay, always, instance
from tqdm.contrib.itertools import product
from itertools import product as silent_product

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
    stop_sim = Signal(False)

    dut = agg(clk, enable, input_0, input_1, output_0)

    stimulus_testcases = product(range(0,100), range(0,100), desc="Pushing input into AG")
    monitor_testcases = silent_product(range(0,100), range(0,100))
    
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
        yield clk.posedge
        for i,j in stimulus_testcases:
            input_0.next = i
            input_1.next = j
            yield clk.posedge
        stop_sim.next = True
        yield clk.posedge # last input
        
        
    @instance
    def monitor():
        yield enable
        while not stop_sim:
            expected_next = next(monitor_testcases)
            if(output_0.val != sum(expected_next)):
                raise Exception("Agg testbench failed... aborting...")
            yield output_0, stop_sim
        print("\n Agg testbench pass")
    return clk_driver, monitor, stimulus, dut

 
if __name__ == '__main__':
    print("Running AGG testbench")
    inst = agg_tb()
    inst.run_sim(quiet=True)