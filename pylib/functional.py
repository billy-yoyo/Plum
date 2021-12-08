
from interpreter import Context

ctx = Context()

@ctx.use("reduce")
def reduce(start, iter):
    def reducer(upstream, this):
        if "stop" in this:
            raise StopIteration
        
        current = start
        for value in upstream:
            current = iter(value, current)
        
        this["stop"] = True
        return current
    return reducer

ctx.set("sum", reduce(0, lambda x, t: x + t))
ctx.set("mult", reduce(1, lambda x, t: x * t))

@ctx.use("window")
def window(size):
    def window_slide(upstream, this):
        if "window" not in this:
            this["window"] = [upstream.next() for x in range(size)]
            return this["window"]
        else:
            window = this["window"]
            window.pop(0)
            window.append(upstream.next())
            return window
    return window_slide

ctx.set("range", range)

def register(global_ctx):
    global_ctx.merge(ctx)
