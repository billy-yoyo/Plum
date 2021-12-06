
from interpreter import Context


ctx = Context()

ctx.set("print", lambda *args: print(*args))
ctx.set("int", lambda x: int(x))
ctx.set("float", lambda x: float(x))
ctx.set("str", lambda x: str(x))

def register(global_ctx):
    global_ctx.merge(ctx)
