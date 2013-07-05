#!/usr/bin/python
# -*- coding: utf-8 -*-

import inspect
from inspect import Parameter
from functools import partial


'''
success: able to call bound
fail:
    missing <name>: first arg named <name> is needed to call bound
    TooManyFound <name>: key <name> in d is not used in bound.

limitations:
    user MUST supply name.
    cannot use positional only parameters
'''


def findbind(f, d):
    sig = inspect.signature(f)
    bound = None
    missing = set([])
    toomany = set(d.keys())

    for p in sig.parameters.values():
        assert p.kind is not Parameter.POSITIONAL_ONLY
        k = p.name
        if k in d:
            toomany.remove(k)
        if k not in d and p.default is Parameter.empty:
            ''' if f has default,
            we donot need to supply'''
            missing.add(k)

    if not missing and not toomany:
        bound = partial(f, **d)

    return bound, missing, toomany,




if __name__ == "__main__":
    def foo(a, b, c=None, *d, **e):
        pass
