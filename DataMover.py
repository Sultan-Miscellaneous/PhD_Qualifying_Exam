# %%
from myhdl import block, always

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
                        
    
    return access_mem
