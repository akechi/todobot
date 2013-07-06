#!/usr/bin/python
# -*- coding: utf-8 -*-

import re
import inspect
from inspect import Parameter
from functools import partial


class Node(object):
    def __init__(self, name, parent=None):
        self.name = name
        self.children = {}
        self.parent = parent

    def make_child(self, name):
        c = Node(name, self)
        if name in self.children:
            xs = self.children[name]
            xs.append(c)
            self.children[name] = xs
        else:
            self.children[name] = [c]
        return c

    def __getitem__(self, name):
        return self.children[name]

    def __contains__(self, name):
        return name in self.children

    def __iter__(self):
        for xs in self.children.values():
            for x in xs:
                yield x

    def pprint(self, indent=None):
        if indent is None:
            indent = 0
        print(' '*indent + self.name)
        for c in self:
            c.pprint(indent+4)

    def path(self):
        if self.parent:
            return self.parent.path() + (self.name, )
        else:
            return ()

    def associate(self, d):
        '''
            associate regular expression match object groupdict() and ast.
        '''
        seen = dict()
        for xs in self.children.values():
            for i, c in enumerate(xs):
                if len(xs) == 1:
                    p = '_' + '_'.join(c.path())
                else:
                    p = '_' + '_'.join(c.path()) + '{}'.format(i)
                if p in d and d[p] is not None:
                    seen[p] = c
                    seen.update(c.associate(d))#{k: v for k, v in d.items() if k != p}))
        return seen



class Base(object):
    def __init__(self, *fs):
        self.fs = fs

    def visit(self, enter, leave):
        enter(self)
        for f in self.fs:
            f.visit(enter, leave)
        leave(self)

    def make(self, parent):
        return "(?:{}){}".format(
                self.c.join([f.make(parent) for f in self.fs]),
                self.d)

    def compile(self):
        return re.compile(self.make(''))

    def make_ast(self):
        root = Node('')

        stack = [root]
        def enter(rnode):
            if isinstance(rnode, named):
                top = stack[-1]
                c = top.make_child(rnode.name)
                stack.append(c)

        def leave(rnode):
            if isinstance(rnode, named):
                assert stack[-1].name == rnode.name
                stack.pop(-1)

        self.visit(enter, leave)

        return root



class Or(Base):
    c = '|'
    d = ''

class Cat(Base):
    c = ''
    d = ''


class Option(Base):
    c = ''
    d = '?'

class OneOrMore(Base):
    c = ''
    d = '+'

class ZeroOrMore(Base):
    c = ''
    d = '*'


class unnamed(Base):
    def __init__(self, pat, *fs):
        Base.__init__(self, *fs)
        self.pat = pat
    def make(self, parent):
        return "(?:{}".format(self.pat)+ Cat(*(self.fs)).make(parent) + ")"


class named(unnamed):
    SEP = '_'

    def __init__(self, name, pat, *fs):
        unnamed.__init__(self, pat, *fs)
        self.name = name

    def make_path(self, parent):
        return parent + self.SEP + self.name

    def make(self, parent):
        p = self.make_path(parent)
        return r"(?P<{0}>{1}{2})".format(p, self.pat, Cat(*(self.fs)).make(p))


class counted(named):
    def __init__(self, name, pat, *fs):
        named.__init__(self, name, pat, *fs)
        self._counted = {}
    def make(self, parent):
        p = self.make_path(parent)
        count = self._counted.get(p, 0)
        self._counted[p] = count + 1
        return r"(?P<{0}{1}>{2}{3})".format(p, count, self.pat, Cat(*self.fs).make(p))


def findbind(f, d):
    '''
    success: able to call bound
    fail:
        missing <name>: first arg named <name> is needed to call bound
        TooManyFound <name>: key <name> in d is not used in bound.

    limitations:
        user MUST supply name.
        cannot use positional only parameters
    '''
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


if __name__ == '__main__':
    pass
