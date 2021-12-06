from interpreter import Context
from pylib.functional import register as register_functional
from pylib.basic import register as register_basic
from pylib.io import register as register_io

global_ctx = Context()

register_functional(global_ctx)
register_basic(global_ctx)
register_io(global_ctx)
