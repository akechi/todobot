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

ignore_rest = Option(OneOrMore(ws), blackhole)

def named(name, pat, *fs):
    def foo(parent, nth=0):
        p = make_path(parent, nth, name)
        return r"(?P<%s>%s"%(p, pat) + Cat(*fs)(p) + ")"
    return foo


def may_be(f):
    def foo(parent, nth=0):
        return Option(OneOrMore(ws), Option(f))(parent)
    return foo


description = named("description", ".+")
nickname = named("nickname", "[a-zA-Z@][a-zA-Z0-9]*")

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
        named("about", "about", ignore_rest),
        named("add", "add", may_be(description)),
        named("addto", "addto", Option(
            OneOrMore(ws),
            Option(Cat(named("u1", "", nickname), comma)),
            Option(Cat(named("u2", "", nickname), comma)),
            Option(Cat(named("u3", "", nickname), comma)),
            Option(Cat(named("u4", "", nickname), comma)),
            ZeroOrMore(named("too_many", "", Cat(nickname, comma))), 
            Option(nickname, unnamed("(?!,)"), may_be(description)))),
        named("help", "help",
            may_be(command),
            ignore_rest),
        named("edit", "edit",
            may_be(task_id),
            may_be(description)),
        named("debug", "debug",
            may_be(task_id),
            ignore_rest),
        named("del", "del",
            may_be(task_id),
            ignore_rest),
        named("done", "done",
            may_be(task_id),
            ignore_rest),
        named("list", "list", 
            may_be(rangespec),
            may_be(keyword),
            ignore_rest),
        named("list_all", "list-all",
            ignore_rest),
        named("list_done", "list-done",
            ignore_rest),
        named("list_everything", "list-everything",
            ignore_rest),
        named("listof", "listof",
            may_be(nickname),
            ignore_rest),
        named("listof_all", "listof-all",
            may_be(nickname),
            ignore_rest),
        named("listof_done", "listof-done",
            may_be(nickname),
            ignore_rest),
        named("show", "show", 
            may_be(nickname),
            ignore_rest),
        named("sudel", "sudel", 
            may_be(nickname),
            ignore_rest),
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

