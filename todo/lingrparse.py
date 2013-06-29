#!/usr/bin/python
# -*- coding: utf-8 -*-

import re


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
        return "(?:%s"%(pat,)+ Cat(*fs)(parent) + ")"
    return foo

blackhole = unnamed(".*")
ws = unnamed(" ")
comma = unnamed(",")
hyph = unnamed("-")
expect_nohyph = unnamed("(?!-)")

ignore_rest = Option(OneOrMore(ws), blackhole)


def named(name, pat, *fs):
    def foo(parent):
        p = make_path(parent, name)
        return r"(?P<%s>%s"%(p, pat) + Cat(*fs)(p) + ")"
    return foo

_counted = {}
def counted(name, pat, *fs):
    def foo(parent):
        p = make_path(parent, name)
        count = _counted.get(p, 0)
        _counted[p] = count + 1
        return r"(?P<%s%d>%s"%(p, count, pat) + Cat(*fs)(p) + ")"
    return foo

def may_be(*fs):
    def foo(parent):
        return Option(OneOrMore(ws), Option(*fs))(parent)
    return foo


description = named("description", ".+")
nickname = named("nickname", "[a-zA-Z@][a-zA-Z0-9]*")
nicknames = counted("nicknames", "[a-zA-Z@][a-zA-Z0-9]*")

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
        named("addto", "addto", 
            may_be(
                Option(nicknames, comma),
                Option(nicknames, comma),
                Option(nicknames, comma),
                Option(nicknames, comma),
                ZeroOrMore(named("too_many", "", nickname, comma)), 
                Option(nickname, unnamed("(?!,)"))),
            may_be(description)),
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
        named("moveto", "moveto",
            may_be(nickname),
            may_be(task_id),
            ignore_rest),
        named("show", "show", 
            may_be(task_id),
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

