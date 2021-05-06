from myhdl import block, always_seq

@block
def inc(count, enable, clock, reset):
    """ Incrementer with enable.

    count -- output
    enable -- control input, increment when 1
    clock -- clock input
    reset -- asynchronous reset input
    """
    
    @always_seq(clock.posedge, reset=reset)
    def seq():
        if enable:
            count.next = count + 1

    return seq

from myhdl import Signal, ResetSignal, modbv

def convert_inc(hdl):
    """Convert inc block to Verilog or VHDL."""

    m = 8

    count = Signal(modbv(0)[m:])
    enable = Signal(bool(0))
    clock  = Signal(bool(0))
    reset = ResetSignal(0, active=0, isasync=True)

    inc_1 = inc(count, enable, clock, reset)

    inc_1.convert(hdl=hdl)


convert_inc(hdl='Verilog')
convert_inc(hdl='VHDL')