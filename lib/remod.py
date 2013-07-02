#!/usr/bin/python
# -*- coding: utf-8 -*-

import re


class MOWrapper(object):
    def __init__(self, rxw, txt): 
        self.patw = rxw.patw
        self.rx = rxw.rx
        self.mo = self.rx.match(txt)
        if self.mo is not None:
           d = dict([(k, v) for k, v in self.mo.groupdict().items() if v is not None])
           self.d = d

    def groupdict(self):
        assert self.mo
        return self.mo.groupdict()

    def smart(self):
        xxs = [tuple([x for x in k.split("_") if x]) for k in self.d.keys()]
        xxs.sort(key=lambda xs:len(xs))
        print(xxs)

        root = {}
        for xs in xxs:
            r = root
            for x in xs:
                c = r.get(x, None)
                if c is None:
                    c = {}
                r[x] = c
                r = c
            r[xs[-1]] = self.d["_"+"_".join(xs)]
        print(root)
        return root


class RXWrapper(object):
    def __init__(self, patw): 
        self.patw = patw
        self.rx = re.compile(patw.make(''))

    def match(self, txt):
        mow = MOWrapper(self, txt)
        if mow.mo is None:
            return None
        return mow

    @property
    def pattern(self):
        return self.rx.pattern


class Base(object):
    def __init__(self, *fs):
        self.fs = fs

    def make(self, parent):
        return "(?:{}){}".format(
                self.c.join([f.make(parent) for f in self.fs]),
                self.d)

    def compile(self):
        return RXWrapper(self)


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

