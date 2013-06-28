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

def unnamed(pat, *fs):
    def foo(parent, nth=0):
        return "(?:%s"%(pat,)+ Cat(*fs)(parent) + ")"
    return foo

blackhole = unnamed(".*")
ws = unnamed(" ")
comma = unnamed(",")
hyph = unnamed("-")
expect_nohyph = unnamed("(?!-)")


def named(name, pat, *fs):
    def foo(parent, nth=0):
        p = make_path(parent, nth, name)
        return r"(?P<%s>%s"%(p, pat) + Cat(*fs)(p) + ")"
    return foo


description = named("description", ".+")
nickname = named("nickname", "[a-zA-Z][a-zA-Z0-9]*")
command = named("command", "[a-z]+")
task_id = named("task_id", "\d+")

end = named("end", "\d+")
start = named("start", "\d+")

rangespec = named("range", "", 
    Or(
      Cat(expect_nohyph, start, hyph),
      Cat(Option(hyph), end, expect_nohyph),
      named('both', '', start, hyph, end),
      ))

keyword = named("keyword", "\w+")


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
                Option(Cat(named("u1", "", nickname), comma)),
                Option(Cat(named("u2", "", nickname), comma)),
                Option(Cat(named("u3", "", nickname), comma)),
                Option(Cat(named("u4", "", nickname), comma)),
                ZeroOrMore(named("too_many", "", Cat(nickname, comma))), 
                nickname, 
                Option(OneOrMore(ws), Option(description))))),
        named("help", "help",
            Option(ws, Option(command, Option(ws, blackhole)))),
        named("edit", "edit",
            Option(ws, Option(Or(task_id, blackhole), Option(ws, Option(description))))),
        named("debug", "debug", 
            Option(ws, Option(Or(task_id, blackhole), Option(ws, blackhole)))),
        named("del", "del", 
            Option(ws, Option(Or(task_id, blackhole), Option(ws, blackhole)))),
        named("done", "done", 
            Option(ws, Option(Or(task_id, blackhole), Option(ws, blackhole)))),
        named("list", "list", 
            Option(ws, rangespec),
            Option(ws, keyword),
            Option(ws, blackhole)),
        named("list_all", "list-all",
            Option(ws, blackhole)),
        named("list_done", "list-done",
            Option(ws, blackhole)),
        named("list_everything", "list-everything",
            Option(ws, blackhole)),
        named("listof", "listof",
            Option(ws, Option(nickname, Option(ws, blackhole)))),
        named("listof_all", "listof-all",
            Option(ws, Option(nickname, Option(ws, blackhole)))),
        named("listof_done", "listof-done",
            Option(ws, Option(nickname, Option(ws, blackhole)))),
        named("show", "show", 
            Option(ws, Option(Or(task_id, blackhole), Option(ws, blackhole)))),
        named("sudel", "sudel", 
            Option(ws, Option(Or(task_id, blackhole), Option(ws, blackhole)))),
    ))(name) + '$'

r = re.compile(acceptable(""))

def parse(text):
    m = r.match(text)
    if m is None:
        return None
    d = dict([(k, v) for k, v in m.groupdict().items() if v is not None])
    return d

if __name__ == '__main__':
    print(r.pattern)
    print("enjoy reading regexp!")

