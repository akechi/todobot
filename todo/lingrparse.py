#!/usr/bin/python
# -*- coding: utf-8 -*-

import re


SEP = '_'

def make_path(parent, nth, name):
    #return parent + SEP + str(nth) + SEP + name
    return parent + SEP + name

def Or(*fs):
    def foo(parent, nth=0):
        return "(?:" + '|'.join([f(parent) for f in fs]) + ")"
    return foo

def Cat(*fs):
    def foo(parent, nth=0):
        return "(?:" + ''.join([f(parent) for f in fs]) + ")"
    return foo

def Option(*fs):
    def foo(parent, nth=0):
        return "(?:" + ''.join([f(parent) for f in fs]) + ")?"
    return foo

def OneOrMore(*fs):
    def foo(parent, nth=0):
        return "(?:" + ''.join([f(parent) for f in fs]) + ")+"
    return foo

def ZeroOrMore(*fs):
    def foo(parent, nth=0):
        return "(?:" + ''.join([f(parent) for f in fs]) + ")*"
    return foo

def blackhole(parent, nth=0):
    return "(?:.*)"

def ws(parent, nth=0):
    return r" "

def comma(parent, nth=0):
    return r","

def named(name, pat, *fs):
    def foo(parent, nth=0):
        p = make_path(parent, nth, name)
        return r"(?P<%s>%s"%(p, pat) + Cat(*fs)(p) + ")"
    return foo


description = named("description", ".+")
nickname = named("nickname", "[a-zA-Z][a-zA-Z0-9]*")
command = named("command", "[a-z]+")
task_id = named("task_id", "\d+")


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
    return named("hashtodo", "#todo")(name) + Option(ws, Or(
        named("about", "about",
            Option(ws, blackhole)),
        named("add", "add",
            Option(ws, description)),
        named("addto", "addto", Or(
            ZeroOrMore(ws),
            Option(OneOrMore(ws),
                Option(named("u1", "", Cat(nickname, comma))), 
                Option(named("u2", "", Cat(nickname, comma))), 
                Option(named("u3", "", Cat(nickname, comma))), 
                Option(named("u4", "", Cat(nickname, comma))), 
                ZeroOrMore(named("too_maney", "", Cat(nickname, comma))), 
                nickname, 
                Option(OneOrMore(ws), Option(description))))),
        named("help", "help",
            Option(ws, Option(command, Option(ws, blackhole)))),
        named("edit", "edit",
            Option(ws, description)),
        named("debug", "debug", 
            Option(ws, Option(task_id, Option(ws, blackhole)))),
        named("del", "del", 
            Option(ws, Option(task_id, Option(ws, blackhole)))),
        named("done", "done", 
            Option(ws, Option(task_id, Option(ws, blackhole)))),

    ))(name) + '$'

r = re.compile(acceptable(""))

print(r.pattern)

def parse(text):
    m = r.match(text)
    if m is None:
        return None
    d = m.groupdict()
    return d



