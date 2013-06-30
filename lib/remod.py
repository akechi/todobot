#!/usr/bin/python
# -*- coding: utf-8 -*-

SEP = '_'


def make_path(parent, name):
    return parent + SEP + name

def Or(*fs):
    def foo(parent):
        return "(?:" + '|'.join([f(parent) for f in fs]) + ")"
    return foo

def Cat(*fs):
    def foo(parent):
        return "(?:" + ''.join([f(parent) for f in fs]) + ")"
    return foo

def Option(*fs):
    def foo(parent):
        return "(?:" + ''.join([f(parent) for f in fs]) + ")?"
    return foo

def OneOrMore(*fs):
    def foo(parent):
        return "(?:" + ''.join([f(parent) for f in fs]) + ")+"
    return foo

def ZeroOrMore(*fs):
    def foo(parent):
        return "(?:" + ''.join([f(parent) for f in fs]) + ")*"
    return foo

def unnamed(pat, *fs):
    def foo(parent):
        return "(?:{}".format(pat)+ Cat(*fs)(parent) + ")"
    return foo


def named(name, pat, *fs):
    def foo(parent):
        p = make_path(parent, name)
        return r"(?P<{0}>{1}".format(p, pat) + Cat(*fs)(p) + ")"
    return foo

_counted = {}
def counted(name, pat, *fs):
    def foo(parent):
        p = make_path(parent, name)
        count = _counted.get(p, 0)
        _counted[p] = count + 1
        return r"(?P<{0}{1}>{2}".format(p, count, pat) + Cat(*fs)(p) + ")"
    return foo


