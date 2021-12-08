from interpreter import Context
from pylib.functional import register as register_functional
from pylib.basic import register as register_basic
from pylib.io import register as register_io
from pylib.vector import register as register_vector
from pylib.math_helpers import register as register_math

global_ctx = Context()

register_functional(global_ctx)
register_basic(global_ctx)
register_io(global_ctx)
register_vector(global_ctx)
register_math(global_ctx)
