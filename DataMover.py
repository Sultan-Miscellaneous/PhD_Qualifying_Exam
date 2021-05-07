# %%
from itertools import cycle
from myhdl import block, instance, delay, Signal


@block
def datamover(clk : Signal, enable, data, port, program, startup_delay = None, cycle_program = False, repeat = 1, mode = 'read'):
    
    program = cycle(program) if cycle_program else program * repeat
    
    def apply_access(iteration_vector, access_map):
        access_idx = 0
        for iteration_dim, constant in zip(iteration_vector, access_map[:-1]):
            access_idx += (iteration_dim*constant)
        access_idx += access_map[-1]
        return access_idx
 
    @instance
    def compute():
        if enable:
            if startup_delay is not None:
                yield delay(startup_delay)
            for (domain, access_map, condition) in program:
                for iteration_vector in domain:
                    if condition(iteration_vector):
                        if mode == 'read' or mode == 'write':
                            access_idx = apply_access(iteration_vector, access_map)
                            if mode == 'read':
                                data.next = port(access_idx)
                            elif mode == 'write':
                                port(access_idx, data.val)
                        elif mode == 'filter':
                            data.next = port.val
                        else:
                            raise Exception("Invalid Datamover mode specified")
                    yield clk.posedge
                        
    
    return compute
