from compiler import Compiler
from node import Node   

compiler = Compiler()

@compiler.define
def define_variable(parser):
    parser.assert_flag("value")
    parser.assert_next_is({ "type": "word" })
    return Node("variable", name=parser.last_content())

@compiler.define
def define_property(parser):
    parser.assert_flag("value")
    parser.assert_next_is({ "type": "period" })
    parser.assert_next_is({ "type": "word" })
    return Node("property", name=parser.last_content())

@compiler.define
def define_whitebreak(parser):
    parser.assert_next_is({ "type": "whitebreak" })
    return Node("whitebreak")

@compiler.define_post
def define_whitebreak_post(parser, value):
    parser.assert_next_is({ "type": "whitebreak" })
    return Node("whitebreak")

@compiler.define_post
def define_property_access(parser, value):
    parser.assert_flag("value")
    parser.assert_next_is({ "type": "period" })
    parser.assert_next_is({ "type": "word" })
    return Node("property_access", target=value, name=parser.last_content())

@compiler.define_post
def define_assign(parser, location):
    parser.assert_true(location.type in ["variable", "property", "property_access"])
    parser.assert_flag("value")
    parser.assert_no_flag("ignore_assign")
    parser.assert_next_is({ "type": "assign" })
    value = parser.read("value")
    return Node("assign", location=location, value=value)

@compiler.define_post
def define_function_call(parser, value):
    parser.assert_flag("value")
    parser.assert_next_is({ "type": "bracket_open" })
    # allow for empty arguments
    args = parser.maybe_read("value") or Node("tuple", values=[])
    parser.assert_next_is({ "type": "bracket_close" })
    return Node("function_call", target=value, args=args)

@compiler.define_post
def define_binary_operator(parser, value):
    parser.assert_flag("value")
    parser.assert_no_flag("ignore_binary_operator")
    parser.assert_next_is({ "type": "binary_operator" })
    operator = parser.last_content()
    next_value = parser.read("value", "ignore_binary_operator", "ignore_flow")

    if value.type == "binary_operator":
        value.values.append(next_value)
        value.operators.append(operator)
        return value
    else:
        return Node("binary_operator", values=[value, next_value], operators=[operator])

@compiler.define_post
def define_flow(parser, value):
    parser.assert_flag("value")
    parser.assert_no_flag("ignore_flow")
    parser.assert_next_is([{ "type": "pipe" }, { "type": "map" }, { "type": "write" }, { "type": "read" }, { "type": "pop" }])
    flow_type = parser.last_type()
    next_value = None
    if flow_type != "pop":
        next_value = parser.read("value", "ignore_flow")
    return Node("flow", flow_type=flow_type, flow_from=value, flow_to=next_value)

def read_arguments(parser):
    parser.assert_flag("arguments")
    parser.assert_next_is({ "type": "word" })
    arguments = [parser.last_content()]
    while parser.next_is({ "type": "comma" }):
        parser.assert_next_is({ "type": "word" })
        arguments.append(parser.last_content())
    return Node("arguments", arguments=arguments)

def parse_argument(parser, arg):
    if arg.type == "list":
        return [parse_argument(parser, subarg) for subarg in arg.values]
    elif arg.type == "variable":
        return arg.name
    else:
        parser.assert_true(False)

def parse_arguments(parser, arglist):
    return [parse_argument(parser, arg) for arg in arglist]

@compiler.define_post
def define_function(parser, value):
    parser.assert_flag("value")
    parser.assert_no_flag("ignore_function")
    parser.assert_true(value.type in ["tuple", "variable", "list"])
    parser.assert_next_is({ "type": "arrow" })

    if value.type == "tuple":
        arguments = value.values
    else:
        arguments = [value]

    arguments = parse_arguments(parser, arguments)
    
    if parser.has_flag("ignore_flow"):
        body = parser.read("value", "ignore_flow")
    else:
        body = parser.read("value")

    return Node("function", arguments=arguments, body=body)

@compiler.define_post
def define_index(parser, value):
    parser.assert_flag("value")
    parser.assert_no_flag("ignore_index")
    parser.assert_next_is({ "type": "index" })
    index = parser.read("value", "ignore_index", "ignore_flow", "ignore_binary_operator", "ignore_assign", "ignore_tuple")
    return Node("index", target=value, index=index)

@compiler.define
def define_block(parser):
    parser.assert_flag("value")
    parser.assert_next_is({ "type": "curly_open" })
    body = parser.read_many("value")
    parser.assert_next_is({ "type": "curly_close" })
    return Node("block", body=body)

@compiler.define
def define_int(parser):
    parser.assert_flag("value")
    parser.assert_next_is({ "type": "int" })
    return Node("int", value=int(parser.last_content()))

@compiler.define
def define_float(parser):
    parser.assert_flag("value")
    parser.assert_next_is({ "type": "float" })
    return Node("float", value=float(parser.last_content()))

@compiler.define
def define_string(parser):
    parser.assert_flag("value")
    parser.assert_next_is({ "type": "string" })
    return Node("string", value=parser.last_content()[1:-1])

@compiler.define
def define_boolean(parser):
    parser.assert_flag("value")
    parser.assert_next_is({ "type": "boolean" })
    return Node("boolean", value=parser.last_content() == "true")

@compiler.define
def define_list(parser):
    parser.assert_flag("value")
    parser.assert_next_is({ "type": "square_open" })
    value = parser.read("value")
    parser.assert_next_is({ "type": "square_close" })
    if value.type == "tuple":
        values = value.values
    else:
        values = [value]
    return Node("list", values=values)

@compiler.define_post
def define_tuple(parser, value):
    parser.assert_flag("value")
    parser.assert_no_flag("ignore_tuple")
    
    parser.assert_next_is({ "type": "comma" })

    if parser.has_flag("allow_function"):
        next_value = parser.maybe_read("value", "ignore_tuple")
    else:
        next_value = parser.maybe_read("value", "ignore_tuple", "ignore_function")

    if value.type == "tuple":
        if next_value is None:
            return value
        else:
            value.values.append(next_value)
            return value
    elif next_value is None:
        return Node("tuple", values=[value])
    else:
        return Node("tuple", values=[value, next_value])

@compiler.define
def define_wrapped_value(parser):
    parser.assert_flag("value")
    parser.assert_next_is({ "type": "bracket_open" })
    value = parser.read("value", "allow_function")
    parser.assert_next_is({ "type": "bracket_close" })
    return value

@compiler.define
def define_if(parser):
    parser.assert_flag("value")
    def read_clause():
        condition = parser.read("value")
        body = parser.read("value")
        return condition, body
    
    parser.assert_next_is({ "type": "if" })
    
    if_clause = read_clause()
    
    elif_clauses = []
    while parser.next_is({ "type": "elif" }):
        elif_clauses.append(read_clause())

    else_block = None
    if parser.next_is({ "type": "else" }):
        else_block = parser.read("value")
    
    return Node("if", if_clause=if_clause, elif_clauses=elif_clauses, else_block=else_block)

@compiler.define
def define_for(parser):
    parser.assert_flag("value")
    parser.assert_next_is({ "type": "for" })
    parser.assert_next_is({ "type": "word" })
    variable = parser.last_content()
    parser.assert_next_is({ "type": "in" })
    iterable = parser.read("value")
    body = parser.read("value")
    return Node("for", variable=variable, iterable=iterable, body=body)

@compiler.define
def define_break(parser):
    parser.assert_flag("value")
    parser.assert_next_is({ "type": "break" })
    return Node("break")


