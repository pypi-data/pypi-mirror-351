"""
@since 0.3.46 \\
© 2025-Present Aveyzan // License: MIT

Used to warrant type subscription working for builtins in Python 3.8. Not for import. \\
It doesn't use `~._types` submodule.
"""

from __future__ import annotations
import builtins as _b
import collections as _c
import sys as _s
import typing as _t

if _s.version_info >= (3, 9):
    
    deque = _c.deque
    dict = _b.dict
    frozenset = _b.frozenset
    list = _b.list
    set = _b.set
    tuple = _b.tuple
    
else:
    
    deque = _t.Deque
    dict = _t.Dict
    frozenset = _t.FrozenSet
    list = _t.List
    set = _t.Set
    tuple = _t.Tuple

if __name__ == "__main__":
    error = RuntimeError("import-only module")
    raise error