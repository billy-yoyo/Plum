from interpreter import Interpreter
from functools import reduce

from pipe_stream import PipeStream, StopPipeException

interpreter = Interpreter()

def get_property(target, property):
    if isinstance(target, dict):
        return target.get(property, None)
    elif isinstance(target, list) or isinstance(target, tuple):
        try:
            return target[property]
        except:
            return None
    else:
        return getattr(target, property, None)

def set_property(target, property, value):
    if isinstance(target, dict) or isinstance(target, list):
        target[property] = value
    else:
        setattr(target, property, value)
    return value

def call_function(target, args):
    if isinstance(args, tuple):
        return target(*args)
    else:
        return target(args)

def split_operators(values, operators, operator):
    split_values = []
    split_operators = []
    last_i = 0
    for i, op in enumerate(operators):
        if op == operator:
            split_values.append(values[last_i:(i+1)])
            split_operators.append(operators[last_i:i])
            last_i = i + 1
    split_values.append(values[last_i:len(values)])
    split_operators.append(operators[last_i:len(operators)])
    return zip(split_values, split_operators)

def create_operator_executor(values, operator):
    if operator == "+":
        return lambda ctx: sum(v(ctx) for v in values)
    elif operator == "-":
        return lambda ctx: reduce(lambda x, t: t - x(ctx), values[1:], values[0](ctx))
    elif operator == "*":
        return lambda ctx: reduce(lambda x, t: t * x(ctx), values[1:], values[0](ctx))
    elif operator == "/":
        return lambda ctx: reduce(lambda x, t: t / x(ctx), values[1:], values[0](ctx))
    elif operator == "??":
        def executor(ctx):
            for value in values:
                evaluated = value(ctx)
                if evaluated is not None:
                    return evaluated
            return None
        return executor
    elif operator in [">", "<", ">=", "<=", "==", "!="]:
        if len(values) > 2:
            raise Exception("cannot use comparators on more than 2 values")
        if operator == ">":
            return lambda ctx: values[0](ctx) > values[1](ctx)
        elif operator == "<":
            return lambda ctx: values[0](ctx) < values[1](ctx)
        elif operator == ">=":
            return lambda ctx: values[0](ctx) >= values[1](ctx)
        elif operator == "<=":
            return lambda ctx: values[0](ctx) <= values[1](ctx)
        elif operator == "==":
            return lambda ctx: values[0](ctx) == values[1](ctx)
        elif operator == "!=":
            return lambda ctx: values[0](ctx) != values[1](ctx)

def parse_binary_operators(visitor, values, operators):
    if len(operators) == 0:
        value = visitor.visit(values[0])
        return lambda ctx: value(ctx)
    elif all(op == operators[0] for op in operators):
        values = [visitor.visit(value) for value in values]
        return create_operator_executor(values, operators[0])
    else:
        operator_order = ["+", "-", "*", "/", "??", ">", "<", ">=", "<=", "==", "!="]
        for operator in operator_order:
            if operator in operators:
                split_pairs = split_operators(values, operators, operator)
                values = [parse_binary_operators(visitor, *pair) for pair in split_pairs]
                return create_operator_executor(values, operator)
        else:
            raise Exception(f"unknown operators {operators}")

def wrap_as_stream(value):
    if isinstance(value, PipeStream):
        return value
    elif isinstance(value, list):
        return PipeStream(iter(value))
    else:
        return PipeStream(iter([value]))

def create_pipe_flow(visitor, node_flow_from, node_flow_to):
    flow_from = visitor.visit(node_flow_from)
    flow_to = visitor.visit(node_flow_to)
    def executor(ctx):
        from_value = wrap_as_stream(flow_from(ctx))

        sub_ctx = ctx.get_outer().branch(inner=True)
        sub_ctx.this = from_value

        to_value = flow_to(sub_ctx)
        return PipeStream(from_value, to_value)
    return executor

def create_map_flow(visitor, node_flow_from, node_flow_to):
    flow_from = visitor.visit(node_flow_from)
    flow_to = visitor.visit(node_flow_to)
    def executor(ctx):
        from_value = wrap_as_stream(flow_from(ctx))

        sub_ctx = ctx.get_outer().branch(inner=True)
        sub_ctx.this = from_value

        to_value = flow_to(sub_ctx)
        return PipeStream(from_value, lambda upstream, this: call_function(to_value, next(upstream)))
    return executor

def create_write_flow(visitor, node_flow_from, node_flow_to):
    flow_from = visitor.visit(node_flow_from)
    
    if node_flow_to.flow_type == "variable":
        setter = lambda inner, outer, values: outer.set(node_flow_to.name, values)
    elif node_flow_to.flow_type == "property":
        setter = lambda inner, outer, values: set_property(inner.this, node_flow_to.name, values)
    elif node_flow_to.flow_type == "property_access":
        target = visitor.visit(node_flow_to.target)
        setter = lambda inner, outer, values: set_property(target(outer), node_flow_to.name, values)
    else:
        raise Exception("invalid write flow, can only write into a variable, property or property accessor")

    def executor(ctx):
        from_value = wrap_as_stream(flow_from(ctx))
        values = []
        try:
            while True:
                values.append(next(from_value))
        except StopPipeException:
            pass

        outer_ctx = ctx.get_outer()
        setter(ctx, outer_ctx, values)
    return executor

def create_read_flow(visitor, node_flow_from, node_flow_to):
    flow_from = visitor.visit(node_flow_from)
    flow_to = visitor.visit(node_flow_to)
    def executor(ctx):
        from_value = wrap_as_stream(flow_from(ctx))
        
        sub_ctx = ctx.get_outer().branch(inner=True)
        sub_ctx.this = from_value

        to_value = flow_to(sub_ctx)

        values = []
        try:
            while True:
                values.append(call_function(to_value, next(from_value)))
        except StopPipeException:
            pass
            
        return wrap_as_stream(values)
    return executor

def create_pop_flow(visitor, node_flow_from):
    flow_from = visitor.visit(node_flow_from)
    def executor(ctx):
        from_value = wrap_as_stream(flow_from(ctx))
        return next(from_value)
    return executor

@interpreter.visitor("variable")
def visit_variable(visitor, node):
    return lambda ctx: ctx.get(node.name)

@interpreter.visitor("property")
def visit_property(visitor, node):
    return lambda ctx: get_property(ctx.this, node.name)

@interpreter.visitor("property_access")
def visit_property_access(visitor, node):
    value = visitor.visit(node.target)
    return lambda ctx: get_property(value(ctx), node.name)

@interpreter.visitor("assign")
def visit_assign(visitor, node):
    value = visitor.visit(node.value)
    if node.location.type == "variable":
        return lambda ctx: ctx.set(node.location.name, value(ctx))
    elif node.location.type == "property":
        return lambda ctx: set_property(ctx.this, node.location.name, value(ctx))
    elif node.location.type == "property_access":
        target = visitor.visit(node.location.target)
        return lambda ctx: set_property(target(ctx), node.location.name, value(ctx))
    else:
        raise Exception(f"cannot assign {node.location.type} to a value, must be a variable or property")

@interpreter.visitor("function_call")
def visit_function_call(visitor, node):
    target = visitor.visit(node.target)
    args = visitor.visit(node.args)
    return lambda ctx: call_function(target(ctx), args(ctx))

@interpreter.visitor("binary_operator")
def visit_binary_operator(visitor, node):
    return parse_binary_operators(visitor, node.values, node.operators)

@interpreter.visitor("flow")
def visit_flow(visitor, node):
    flow_type = node.flow_type
    if flow_type == "pipe":
        return create_pipe_flow(visitor, node.flow_from, node.flow_to)
    elif flow_type == "map":
        return create_map_flow(visitor, node.flow_from, node.flow_to)
    elif flow_type == "write":
        return create_write_flow(visitor, node.flow_from, node.flow_to)
    elif flow_type == "read":
        return create_read_flow(visitor, node.flow_from, node.flow_to)
    elif flow_type == "pop":
        return create_pop_flow(visitor, node.flow_from)
    else:
        raise Exception(f"unknown flow type {flow_type}")

def bind_arguments(ctx, values, args):
    for i, arg in enumerate(args):
        if i < len(values):
            value = values[i]
            if isinstance(arg, list):
                bind_arguments(ctx, value, arg)
            else:
                ctx.set(arg, value)
        else:
            break

@interpreter.visitor("function")
def visit_function(visitor, node):
    body = visitor.visit(node.body)
    arguments = node.arguments
    def executor(ctx):
        def func(*values):
            func_ctx = ctx.branch()
            bind_arguments(func_ctx, values, arguments)
            return body(func_ctx)
        return func
    return executor

@interpreter.visitor("index")
def visit_index(visitor, node):
    target = visitor.visit(node.target)
    index = visitor.visit(node.index)
    return lambda ctx: get_property(target(ctx), index(ctx))

@interpreter.visitor("block")
def visit_int(visitor, node):
    body = [visitor.visit(v) for v in node.body]
    def executor(ctx):
        value = None
        for v in body:
            value = v(ctx)
        return value
    return executor

@interpreter.visitor("int")
def visit_int(visitor, node):
    return lambda ctx: node.value

@interpreter.visitor("float")
def visit_float(visitor, node):
    return lambda ctx: node.value

@interpreter.visitor("string")
def visit_string(visitor, node):
    return lambda ctx: node.value

@interpreter.visitor("boolean")
def visit_boolean(visitor, node):
    return lambda ctx: node.value

@interpreter.visitor("list")
def visit_list(visitor, node):
    values = [visitor.visit(v) for v in node.values]
    return lambda ctx: list(v(ctx) for v in values)

@interpreter.visitor("tuple")
def visit_tuple(visitor, node):
    values = [visitor.visit(v) for v in node.values]
    return lambda ctx: tuple(v(ctx) for v in values)

@interpreter.visitor("if")
def visit_if(visitor, node):
    if_clause = [visitor.visit(x) for x in node.if_clause]
    elif_clauses = [[visitor.visit(x) for x in clause] for clause in node.elif_clauses]
    else_block = visitor.visit(node.else_block) if node.else_block else None
    def executor(ctx):
        if if_clause[0](ctx):
            return if_clause[1](ctx)
        else:
            for elif_clause in elif_clauses:
                if elif_clause[0](ctx):
                    return elif_clause[1](ctx)
            if else_block is not None:
                return else_block(ctx)
    return executor

@interpreter.visitor("for")
def visit_for(visitor, node):
    variable = node.variable
    body = visitor.visit(node.body)
    iterable = visitor.visit(node.iterable)
    def executor(ctx):
        value = None
        for x in iterable(ctx):
            ctx.set(variable, x)
            value = body(ctx)
        return value
    return executor

@interpreter.visitor("break")
def visit_break(visitor, node):
    def executor(ctx):
        raise StopIteration()
    return executor
