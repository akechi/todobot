#!/usr/bin/python
# -*- coding: utf-8 -*-

import inspect
from functools import partial


'''
success: able to call bound
fail:
    missing <name>: first arg named <name> is needed to call bound
    TooManyFound <name>: key <name> in d is not used in bound.

'''


def findbind(f, d):
    sig = inspect.signature(f)
    bound = None
    missing = set([])
    toomany = set(d.keys())

    for k in sig.parameters:
        if k:
            if k in d:
                toomany.remove(k)
            else:
                missing.add(k)


    if not missing and not toomany:
        bound = partial(f, **d)

    return bound, missing, toomany,




if __name__ == "__main__":
    def foo(a, b, c=None, *d, **e):
        pass
