
class StopPipeException(Exception):
    pass

def default_executor(upstream, this):
    return next(upstream)

def default_close():
    pass

class IterablePipeStream:
    def __init__(self, stream):
        self.stream = stream

    def __next__(self):
        try:
            return next(self.stream)
        except StopPipeException:
            self.stream.close()
            raise StopIteration()

class PipeStream:
    def __init__(self, source, executor=None, close=None, stream_converter=None):
        self.source = source
        self.executor = executor or default_executor
        self.close = close or default_close
        self.stream_converter = stream_converter
        self.this = {}

    def __next__(self):
        try:
            next_value = self.executor(self.source, self.this)
            return next_value
        except StopIteration:
            self.close()
            raise StopPipeException()

    def __iter__(self):
        return IterablePipeStream(self)

    def next(self):
        return next(self)

    def convert_stream(self, values):
        if self.stream_converter is not None:
            return self.stream_converter(values)
        else:
            return values
    