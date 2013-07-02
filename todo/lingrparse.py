#!/usr/bin/python
# -*- coding: utf-8 -*-

from lib.remod import *

import re



blackhole = unnamed(".*")
ws = unnamed(" ")
comma = unnamed(",")
hyph = unnamed("-")
expect_nohyph = unnamed("(?!-)")

ignore_rest = Option(OneOrMore(ws), blackhole)


class may_be(Base):
    def make(self, parent):
        return Option(OneOrMore(ws), Option(*(self.fs))).make(parent)


description = named("description", ".+")
nickname = named("nickname", "[a-zA-Z@][a-zA-Z0-9_]*")
nicknames = counted("nicknames", "[a-zA-Z@][a-zA-Z0-9_]*")

command = named("command", "[a-z]+")
task_id = named("task_id", "\d+")
task_ids = counted("task_ids", "\d+")

end = named("end", "\d+")
start = named("start", "\d+")

rangespec = named("range", "", 
        Or(
            Cat(expect_nohyph, start, hyph),
            Cat(Option(hyph), end, expect_nohyph),
            named('both', '', start, hyph, end),
            ))

        keyword = named("keyword", "\w+")


builder = Cat(
        named("hashtodo", "#todo"),
        may_be(Or(
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
                may_be(task_ids),
                may_be(task_ids),
                may_be(task_ids),
                may_be(task_ids),
                may_be(task_ids),
                ignore_rest),
            named("done", "done",
                may_be(task_ids),
                may_be(task_ids),
                may_be(task_ids),
                may_be(task_ids),
                may_be(task_ids),
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
                may_be(rangespec),
                may_be(keyword),
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
            )),
  unnamed('$'))

r = builder.compile()

def parse(text):
    m = r.match(text)
    if m is None:
        return None
    d = dict([(k, v) for k, v in m.groupdict().items() if v is not None])
    return d

if __name__ == '__main__':
    print(r.pattern)
    print("enjoy reading regexp!")

