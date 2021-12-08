
from interpreter import Context
import math

class Vector:
    def __init__(self, values):
        self.values = values

    @property
    def dimension(self):
        return len(self.values)

    @property
    def x(self):
        return self.values[0]

    @property
    def y(self):
        return self.values[1]
    
    @property
    def z(self):
        return self.values[2]

    @property
    def w(self):
        return self.values[3]

    def __add__(self, other):
        if isinstance(other, Vector):
            if self.dimension != other.dimension:
                raise ValueError(f"vector dimension mismatch, cannot add vector of dimension {self.dimension} with {other.dimension}")
            return Vector([x + y for x, y in zip(self.values, other.values)])
        else:
            return Vector([x + other for x in self.values])

    def __sub__(self, other):
        if isinstance(other, Vector):
            if self.dimension != other.dimension:
                raise ValueError(f"vector dimension mismatch, cannot add vector of dimension {self.dimension} with {other.dimension}")
            return Vector([x - y for x, y in zip(self.values, other.values)])
        else:
            return Vector([x - other for x in self.values])

    def __mul__(self, other):
        if isinstance(other, Vector):
            if self.dimension != other.dimension:
                raise ValueError(f"vector dimension mismatch, cannot add vector of dimension {self.dimension} with {other.dimension}")
            return Vector([x * y for x, y in zip(self.values, other.values)])
        else:
            return Vector([x * other for x in self.values])

    def __div__(self, other):
        if isinstance(other, Vector):
            if self.dimension != other.dimension:
                raise ValueError(f"vector dimension mismatch, cannot add vector of dimension {self.dimension} with {other.dimension}")
            return Vector([x / y for x, y in zip(self.values, other.values)])
        else:
            return Vector([x / other for x in self.values])

    def square_length(self):
        return sum([x * x for x in self.values])

    def length(self):
        return math.sqrt(self.square_length())

    def unit(self):
        return self / self.length()

    def __iter__(self):
        return iter(self.values)

    def __reversed__(self):
        return reversed(self.values)

    def __str__(self):
        return f"Vector({', '.join([str(x) for x in self.values])})"

ctx = Context()

ctx.set("vec", lambda values: Vector(values))

def register(global_ctx):
    global_ctx.merge(ctx)
