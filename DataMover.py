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
                        access_idx = apply_access(iteration_vector, access_map)
                        if mode == 'read':
                            data.next = port(access_idx)
                        else:
                            port(access_idx, data.val)
                        
    
    return access_mem
