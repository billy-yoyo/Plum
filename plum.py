import sys

from compiler_definitions import compiler
from global_context import global_ctx
from interpreter import Context
from tokenizer import TokenStream
from tokenizer_definitions import tokenizer
from node import Node
from interpreter_definitions import interpreter

def run_code(code, ctx):
    stream = TokenStream(tokenizer, code)
    nodes = compiler.copy(stream).read_all(["value"])
    if stream.string:
        print(f"Syntax error, failed to parse: {stream.string}")
    executor = interpreter.visit_all(nodes)
    return executor(ctx)

if len(sys.argv) >= 2:
    file = sys.argv[1]

    with open(file) as f:
        code = f.read()

    run_code(code, global_ctx.branch())
else:
    ctx = global_ctx.branch()

    while True:
        line = input("> ")
        if line.strip() == "quit":
            break
        value = run_code(line, ctx)
        if value is not None:
            print(value)

