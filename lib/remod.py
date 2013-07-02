#!/usr/bin/python
# -*- coding: utf-8 -*-

import re


class Node(object):
    def __init__(self, name, parent=None):
        self.name = name
        self.children = {}
        self.parent = parent

    def make_child(self, name):
        assert name not in self.children
        c = Node(name, self)
        self.children[name] = c

    def __getitem__(self, name):
        return self.children[name]

    def __contains__(self, name):
        return name in self.children

    def pprint(self, indent=None):
        if indent is None:
            indent = 0
        print(' '*indent + self.name)
        for c in self.children.values():
            c.pprint(indent+4)


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
                top.make_child(rnode.name)
                stack.append(top[rnode.name])

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
    #def counted(name, pat, *fs):
    _counted = {}
    def make(self, parent):
        p = self.make_path(parent)
        count = self._counted.get(p, 0)
        self._counted[p] = count + 1
        return r"(?P<{0}{1}>{2}{3})".format(p, count, self.pat, Cat(*self.fs).make(p))


if __name__ == '__main__':
    ws = unnamed(" ")
    class may_be(Base):
        def make(self, parent):
            return Option(OneOrMore(ws), Option(*(self.fs))).make(parent)
    x = named('a', 'a',
            may_be(named("foo", "foo",
                may_be(named("bar", "bar",
                    may_be(named("baz", "baz")))))),
            unnamed("$"))
    t = x.make_ast()
    t.pprint()



