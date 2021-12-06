import sys

from compiler_definitions import compiler
from global_context import global_ctx
from tokenizer import TokenStream
from tokenizer_definitions import tokenizer
from node import Node
from interpreter_definitions import interpreter

file = sys.argv[1]

with open(file) as f:
    code = f.read()

stream = TokenStream(tokenizer, code)
nodes = compiler.copy(stream).read_all(["value"])
executor = interpreter.visit_all(nodes)
executor(global_ctx.branch())
