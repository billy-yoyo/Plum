
class Context:
    def __init__(self, parent=None, inner_context=False):
        self.parent = parent
        self.variables = {}
        self.this = None
        self.inner_context = inner_context

    def get(self, name):
        if name in self.variables:
            return self.variables.get(name, None)
        elif self.parent is not None:
            return self.parent.get(name)
        else:
            return None

    def set(self, name, value):
        self.variables[name] = value
        return value

    def use(self, name):
        def decorator(func):
            self.set(name, func)
            return func
        return decorator

    def branch(self, inner=False):
        return Context(parent=self, inner_context=inner)

    def get_outer(self):
        ctx = self
        while ctx.inner_context:
            ctx = ctx.parent
        return ctx

    def merge(self, ctx):
        self.variables.update(ctx.variables)


class Interpreter:
    def __init__(self):
        self.visitors = {}

    def visitor(self, name):
        def decorator(func):
            self.visitors[name] = func
            return func
        return decorator

    def visit(self, node):
        if node.type in self.visitors:
            return self.visitors[node.type](self, node)
        else:
            raise Exception(f"No visitor defined for node type {node.type}")

    def visit_all(self, nodes):
        values = [self.visit(node) for node in nodes]
        def executor(ctx):
            value = None
            for v in values:
                value = v(ctx)
            return value
        return executor

