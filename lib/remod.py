#!/usr/bin/python
# -*- coding: utf-8 -*-



class Base(object):
    def __init__(self, *fs):
        self.fs = fs

    def __call__(self, parent):
        return "(?:{}){}".format(
                self.c.join([f(parent) for f in self.fs]),
                self.d)


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
    def __call__(self, parent):
        return "(?:{}".format(self.pat)+ Cat(*(self.fs))(parent) + ")"


class named(unnamed):
    SEP = '_'

    def __init__(self, name, pat, *fs):
        unnamed.__init__(self, pat, *fs)
        self.name = name

    def make_path(self, parent):
        return parent + self.SEP + self.name

    def __call__(self, parent):
        p = self.make_path(parent)
        return r"(?P<{0}>{1}{2})".format(p, self.pat, Cat(*(self.fs))(p))


class counted(named):
    #def counted(name, pat, *fs):
    _counted = {}
    def __call__(self, parent):
        p = self.make_path(parent)
        count = self._counted.get(p, 0)
        self._counted[p] = count + 1
        return r"(?P<{0}{1}>{2}{3})".format(p, count, self.pat, Cat(*self.fs)(p))


if __name__ == '__main__':
    blackhole = unnamed(".*")
    print(blackhole('foo'))
