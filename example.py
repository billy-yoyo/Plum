from compiler_definitions import compiler
from global_context import global_ctx
from tokenizer import TokenStream
from tokenizer_definitions import tokenizer
from node import Node
from interpreter_definitions import interpreter

#with open("example.lang") as f:
#    code = f.read()

code = """
[1, 2, 3] :: window(2) -> [x, y] => print(x, y)
"""

stream = TokenStream(tokenizer, code)

nodes = compiler.copy(stream).read_all(["value"])

def print_value(title, value, prefix=""):
    if isinstance(value, list):
        if title:
            print(f"{prefix}{title}")
        for i, x in enumerate(value):
            print_value("", x, prefix=prefix + " ")
    elif isinstance(value, Node):
        if title:
            print(f"{prefix}{title}")
        print_value(f"Node: ", value.__dict__, prefix=prefix + " ")
    elif isinstance(value, dict):
        if title:
            print(f"{prefix}{title}")
        for k, v in value.items():
            print_value(f"{k}: ", v, prefix=prefix + " ")
    else:
        print(f"{prefix}{title}{value}")

#print_value("Nodes:", nodes)
#print("read tokens:")
#print([x.content for x in stream.tokens])

executor = interpreter.visit_all(nodes)
executor(global_ctx.branch())

