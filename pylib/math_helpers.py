from interpreter import Context
import math

ctx = Context()

@ctx.use("read_bits")
def read_bits(bits):
    value = 0
    for i, bit in enumerate(reversed(bits)):
        value += bit << i
    return value

def register(global_ctx):
    global_ctx.merge(ctx)
