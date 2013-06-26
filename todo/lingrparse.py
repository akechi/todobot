#!/usr/bin/python
# -*- coding: utf-8 -*-

import re


SEP = '_'

def make_path(*xs):
    return SEP.join([x for x in xs])

def Or(*fs):
    def foo(parent):
        return "(?:" + '|'.join([f(parent) for f in fs]) + ")"
    return foo

def Cat(*fs):
    def foo(parent):
        return "(?:" + ''.join([f(parent) for f in fs]) + ")"
    return foo

def Option(f):
    def foo(parent):
        return "(?:" + f(parent) + ")?"
    return foo

def OpCat(*fs):
    def foo(parent):
        return "(?:" + ''.join([f(parent) for f in fs]) + ")?"
    return foo


def blackhole(parent):
    return "(?:.*)"


def ws(parent):
    return r" "

def todo(parent):
    return r"(?P<%s>#todo)"%(make_path(parent, 'sharptodo'),)

def description(parent):
    return "(?P<%s>.+)"%(make_path(parent, 'description'))

def nickname(parent):
    return "(?P<%s>\w+)"%(make_path(parent, 'nickname'))

def command(parent):
    return "(?P<%s>\w+)"%(make_path(parent, 'command'))

def about(parent):
    return r"(?P<%s>about)"%(make_path(parent, 'about'),)

def add(parent):
    """#todo add [description]"""
    name = make_path(parent, "add")
    return r"(?P<%s>add"%(name,) + OpCat(ws, description)(name) + ")"

def addto(parent):
    name = make_path(parent, "addto")
    return r"(?P<%s>addto"%(name,) + Option(ws)(name) \
        + OpCat(nickname, Option(ws), OpCat(ws, description))(name) + ")"

def help(parent):
    """#todo help [command] ... if no command supplied, list all commands."""
    name = make_path(parent, "help")
    return r"(?P<%s>help"%(name,) + Option(ws)(name) \
        + OpCat(ws, command, OpCat(ws, blackhole))(name) + ")"



"""#todo edit [id] [new description]"""
"""#todo debug [id]"""
"""#todo del [id]"""
"""#todo done [id]"""
"""#todo list"""
"""#todo list-all"""
"""#todo list-done"""
"""#todo list-everything"""
"""#todo listof [nickname]"""
"""#todo listof-all [nickname]"""
"""#todo listof-done [nickname]"""
"""#todo show [id]"""
"""#todo sudodel [id]"""


def acceptable(parent):
    name = parent
    return todo(name) + OpCat(ws, 
        Or(Cat(about, OpCat(ws, blackhole)),
            add,
            addto,
            help))(name) + '$'

r = re.compile(acceptable(""))

print(r.pattern)

def parse(text):
    m = r.match(text)
    if m is not None:
        m = m.groupdict()
    return m



