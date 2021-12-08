
from interpreter import Context


ctx = Context()

ctx.set("print", print)
ctx.set("int", int)
ctx.set("float", float)
ctx.set("str", str)
ctx.set("list", list)
ctx.set("tuple", tuple)
ctx.set("len", len)

def register(global_ctx):
    global_ctx.merge(ctx)
