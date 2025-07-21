import pkgutil
import inspect
from importlib import import_module

_funcs = {}
for mod in pkgutil.walk_packages(__path__, __name__ + "."):
    m = import_module(mod.name)
    for _, obj in inspect.getmembers(m, inspect.isfunction):
        if obj.__module__ == m.__name__:
            _funcs[obj.__name__] = obj
globals().update(_funcs)  # so users can `from ... import does_compile`
