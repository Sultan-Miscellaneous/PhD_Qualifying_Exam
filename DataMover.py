from itertools import cycle
from myhdl import block, instance, delay, join, traceSignals, now
from Memory import *
from itertools import product


@block
def datamover(identifier, clk, enable, data, port, program, done, output_enable=None, cycle_program=False, repeat=1, mode='read'):

    program = cycle(program) if cycle_program else program * repeat

    @instance
    def compute():
        nonlocal identifier
        while True:
            yield clk.posedge
            if enable:
                for instruction in program:

                    try:
                        (domain, access_map, condition) = instruction
                        instr_out_enable = None
                    except:
                        (domain, access_map, condition,
                         instr_out_enable) = instruction

                    for iteration_vector in domain:
                        try:
                            attempt_access = condition(*iteration_vector)
                        except:
                            attempt_access = condition(iteration_vector)

                        if attempt_access:
                            if mode == 'read' or mode == 'write':

                                try:
                                    access_idx = access_map(*iteration_vector)
                                except:
                                    access_idx = access_map(iteration_vector)

                                if mode == 'read':
                                    data.next = port(access_idx)
                                elif mode == 'write':
                                    port(access_idx, data.val)
                            elif mode == 'filter':
                                data.next = port.val
                            else:
                                raise Exception(
                                    "Invalid Datamover mode specified")
                        
                        if output_enable is not None:
                            output_enable.next = instr_out_enable if (instr_out_enable is not None) else True
                        yield clk.posedge
                break
        done.next = True
        yield clk.posedge

    return compute


@block
def datamover_tb():

    clk = Signal(True)
    stop_sim = Signal(False)
    enable = Signal(False)
    data = Signal(0)
    mm2s_done = Signal(False)
    s2mm_done = Signal(False)

    memory_size = 200
    memory_monitor = [Signal(0) for i in range(memory_size)]
    initialization_list = list(range(1, 101))

    memory = Memory(
        1, 1, 200, initialization_vals=initialization_list, size=memory_size)

    mm2s = datamover("mm2s", clk, enable, data, memory.get_read_port(), [
        (product(range(10), range(10)), lambda i, j: i*10+j, lambda i, j: True)
    ], mm2s_done)

    s2mm = datamover("s2mm", clk, enable, data, memory.get_write_port(), [
        (range(1), lambda i: 0, lambda i: False),
        (range(100), lambda i: i+100, lambda i: True)
    ], s2mm_done, mode='write')

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
        nonlocal memory
        enable.next = True
        stop_sim.next = False
        yield clk.posedge
        yield join(mm2s_done, s2mm_done)
        for idx in range(100):
            if memory.storage[idx] != memory.storage[idx+100]:
                raise Exception(
                    "Datamover testbench failed, mismatch in memory... aborting...")
        print("Datamover testbench passed")
        stop_sim.next = True
        yield clk.posedge

    @instance
    def monitor():
        nonlocal memory
        yield delay(1)
        while not stop_sim:
            for idx in range(200):
                memory_monitor[idx].next = memory.storage[idx]
            yield delay(2)

    return clk_driver, stimulus, monitor, mm2s, s2mm


if __name__ == '__main__':
    print("Running DataMover testbench")
    inst = datamover_tb()
    inst = traceSignals(inst)
    inst.run_sim()
