#!/usr/bin/python
# -*- coding: utf-8 -*-

import re
import inspect
from inspect import Parameter
from functools import partial
from itertools import filterfalse


class Capture(object):
    def __init__(self, name, parent=None):
        self.name = name
        self.children = {}
        self.parent = parent
        self.named_matches = []

    def make_child(self, name):
        c = Capture(name, self)
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
                p = c.regex_path_string(i)
                if p in d and d[p] is not None:
                    seen[p] = c
                    c.named_matches.append(p)
                    seen.update(c.associate(d))#{k: v for k, v in d.items() if k != p}))
        return seen

    def regex_path_string(self, i):
        if self.multimatch:
            return '_' + '_'.join(self.path()) + '{}'.format(i)
        else:
            return '_' + '_'.join(self.path())

    def guess_pos(self, path):
        pos = path.rfind('s')
        assert pos != -1
        return int(path[pos+1:])

    @property
    def n_lets(self):
        if self.parent is None:
            return []
        return self.parent[self.name]

    @property
    def multimatch(self):
        return len(self.n_lets) > 1


class ASTNode(object):
    c = ''
    d = ''
    def __init__(self, parent=None):
        self.parent = parent
        self.children = []

    @property
    def path(self):
        if self.parent is None:
            return ''
        return self.parent.path

    def visit(self, enter, leave):
        enter(self)
        for c in self.children:
            c.visit(enter, leave)
        leave(self)

    def make_pat(self):
        return "(?:{}){}".format(
                self.c.join([c.make_pat() for c in self.children]),
                self.d)

    def compile(self):
        return re.compile(self.make_pat())

    def make_capture(self):
        root = Capture('')

        stack = [root]
        def enter(rnode):
            if isinstance(rnode, _named):
                top = stack[-1]
                c = top.make_child(rnode.name)
                stack.append(c)

        def leave(rnode):
            if isinstance(rnode, _named):
                assert stack[-1].name == rnode.name
                stack.pop(-1)

        self.visit(enter, leave)

        return root


class _Or(ASTNode):
    c = '|'
    d = ''

class _Cat(ASTNode):
    c = ''
    d = ''


class _Option(ASTNode):
    c = ''
    d = '?'

class _OneOrMore(ASTNode):
    c = ''
    d = '+'

class _ZeroOrMore(ASTNode):
    c = ''
    d = '*'


class _unnamed(ASTNode):
    def __init__(self, parent, pat):
        ASTNode.__init__(self, parent)
        self.pat = pat

    def make_pat(self):
        return "(?:{0}{1}{2})".format(self.pat,
                self.c.join([c.make_pat() for c in self.children]),
                self.d)


class _named(_unnamed):
    SEP = '_'

    def __init__(self, parent, name, pat):
        _unnamed.__init__(self, parent, pat)
        self.name = name

    @property
    def path(self):
        if self.parent is None:
            return self.SEP + self.name
        assert isinstance(self.parent, ASTNode)
        return self.parent.path + self.SEP + self.name

    def make_pat(self):
        return r"(?P<{0}>{1}{2})".format(self.path, self.pat, 
                self.c.join([c.make_pat() for c in self.children]),
                self.d)


class _counted(_named):
    _counted = {}
    def __init__(self, parent, name, pat):
        _named.__init__(self, parent, name, pat)

    def make_pat(self):
        p = self.path
        count = self._counted.get(p, 0)
        self._counted[p] = count + 1
        return r"(?P<{0}{1}>{2}{3})".format(p, count, self.pat, 
                self.c.join([c.make_pat() for c in self.children]),
                self.d)
                

class Builder(object):
    ast_class = ASTNode
    def __init__(self, *xs):
        self.xs = xs

    def build(self, parent=None):
        assert isinstance(parent, ASTNode) or parent is None
        param = [x for x in self.xs if not isinstance(x, Builder)]
        print(self.ast_class, param)
        node = self.ast_class(parent, *param)
        node.children = [x.build(node) for x in self.xs if isinstance(x, Builder)]
        return node

class Or(Builder):
    ast_class = _Or

class Cat(Builder):
    ast_class = _Cat

class Option(Builder):
    ast_class = _Option

class OneOrMore(Builder):
    ast_class = _OneOrMore

class ZeroOrMore(Builder):
    ast_class = _ZeroOrMore

class unnamed(Builder):
    ast_class = _unnamed

class named(Builder):
    ast_class = _named

class counted(Builder):
    ast_class = _counted




def bindable(assoc, d, nots):
    result = {}
    for k, v in filterfalse(lambda x : x[1].name in nots , assoc.items()):
        if v.multimatch:
            x = result.get(v.name, None)
            if x is None:
                x = [None for _ in enumerate(v.n_lets)]
            pos = v.guess_pos(k)
            x[pos] = d[k]
        else:
            x = d[k]
        result[v.name] = x
    return result


def findbind(f, d):
    '''
    success: able to call f with **d
    fail:
        missing <name>: first arg named <name> is needed to call f 
        TooManyFound <name>: key <name> in d is not used in f.

    limitations:
        user MUST supply name.
        cannot use positional only parameters
    '''
    sig = inspect.signature(f)
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
    return missing, toomany,


if __name__ == '__main__':
    x = named('a', 'a')
    t = x.build()
    print(t.make_pat())
    assert "(?P<_a>a(?:))" == t.make_pat()

