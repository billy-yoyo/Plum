
from interpreter import Context
from pipe_stream import PipeStream


ctx = Context()

class FilePipe:
    def __init__(self, *args):
        self.file = open(*args)
    
    def readlines(self):
        return PipeStream(self.file, close=lambda: self.file.close())

ctx.set("file", lambda *args: FilePipe(*args))

def register(global_ctx):
    global_ctx.merge(ctx)
