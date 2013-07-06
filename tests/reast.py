#!/usr/bin/python
# -*- coding: utf-8 -*-

import unittest
import re

from functools import partial
from lib.reast import *

ws = unnamed(" ")
class may_be(Base):
    def make(self, parent):
        return Option(OneOrMore(ws), Option(*(self.fs))).make(parent)


class ReastTestCase(unittest.TestCase):
    def test_make(self):
        x = named('a', 'a')
        self.assertEqual("(?P<_a>a(?:))", x.make(''))
        
    def test_compile(self): 
        x = named('a', 'a')
        got = x.compile()
        self.assertIsNotNone(got)# _sre.SRE_Pattern

    def test_match(self):
        x = named('a', 'a')
        r = x.compile()
        m = r.match('abc')
        self.assertIsNotNone(m.mo)

    def test_match(self):
        x = named('a', 'a',
                may_be(named("foo", "foo")),
                may_be(named("bar", "bar")),
                may_be(named("buz", "buz")),
                unnamed("$"))
        r = x.compile()
        m = r.match('abc')
        self.assertIsNone(m)
    
        m = r.match('a foo')
        self.assertIsNotNone(m)

        m = r.match('a bar')
        self.assertIsNotNone(m)

    def test_make_ast(self):
        x = named('a', 'a',
                may_be(named("foo", "foo")),
                may_be(named("bar", "bar")),
                may_be(named("baz", "baz")),
                unnamed("$"))
        t = x.make_ast()
        self.assertIsNotNone(t["a"])
        self.assertIn("foo", t["a"][0])
        self.assertIsNotNone(t["a"][0]["foo"][0])
        self.assertIn("bar", t["a"][0])
        self.assertIsNotNone(t["a"][0]["bar"][0])
        self.assertIn("baz", t["a"][0])
        self.assertIsNotNone(t["a"][0]["baz"][0])

    def test_smart_deep_nesting(self):
        x = named('a', 'a',
                may_be(named("foo", "foo",
                    may_be(named("bar", "bar",
                        may_be(named("baz", "baz")))))),
                unnamed("$"))
        t = x.make_ast()
        self.assertIn("foo", t["a"][0])
        self.assertIn("bar", t["a"][0]["foo"][0])
        self.assertIn("baz", t["a"][0]["foo"][0]["bar"][0])
        self.assertIsNotNone(t["a"][0]["foo"][0]["bar"][0]["baz"])



class ReastComplexTestCase(unittest.TestCase):
    def setUp(self):
        description = named("description", ".+")
        nicknames = counted("nicknames", "[a-zA-Z@][a-zA-Z0-9_]*")
        nickname = named("nickname", "[a-zA-Z@][a-zA-Z0-9_]*")
        comma = unnamed(",")

        x = Cat(Or(named("add", "add", may_be(description)),
                named("addto", "addto", 
                    may_be(
                        Option(nicknames, comma),
                        Option(nicknames, comma),
                        Option(nicknames, comma),
                        Option(nicknames, comma),
                        ZeroOrMore(named("too_many", "", nickname, comma)), 
                        Option(nickname, unnamed("(?!,)"))),
                    may_be(description))
                ), unnamed("$"))
        t = x.make_ast()
        r = x.compile()
        self.x = x
        self.t = t
        self.r = r

    def test_add_arg(self):
        m = self.r.match("add hogehoge")
        d = m.groupdict()
        assoc = self.t.associate(d)

    def test_addto_args(self):
        m = self.r.match("addto raa0121,deris0126,thinca hogehoge")
        d = m.groupdict()
        assoc = self.t.associate(d)

        self.assertIn('_addto', assoc)
        self.assertEqual('addto', assoc['_addto'].name)

        self.assertIn('_addto_nickname', assoc)
        self.assertEqual('nickname', assoc['_addto_nickname'].name)
        self.assertEqual('thinca', d['_addto_nickname'])

        self.assertIn('_addto_nicknames0', assoc)
        self.assertIn('nicknames', assoc['_addto_nicknames0'].name)
        self.assertIn('raa0121', d['_addto_nicknames0'])

        self.assertIn('_addto_nicknames1', assoc)
        self.assertIn('nicknames', assoc['_addto_nicknames1'].name)
        self.assertIn('deris0126', d['_addto_nicknames1'])

        self.assertIn('_addto_description', assoc)
        self.assertEqual('description', assoc['_addto_description'].name)
        self.assertEqual('hogehoge', d['_addto_description'])



class FindBindTestCase(unittest.TestCase):
    def assertEmpty(self, s):
        self.assertFalse(s)

    def test_none(self):
        def foo():
            return 1
        d = {}
        bound, notfound, toomany = findbind(foo, d)
        self.assertIsInstance(bound, partial)
        self.assertEqual(1, bound())
        self.assertEmpty(notfound)
        self.assertEmpty(toomany)

    def test_one(self):
        def foo(a):
            return a
        d = {"a":10}
        bound, notfound, toomany = findbind(foo, d)
        self.assertIsInstance(bound, partial)
        self.assertEqual(10, bound())
        self.assertEmpty(notfound)
        self.assertEmpty(toomany)

    def test_one_not_found(self):
        def foo(a):
            return a
        d = {}
        bound, notfound, toomany = findbind(foo, d)
        self.assertIsNone(bound)
        self.assertIn('a', notfound)
        self.assertEmpty(toomany)

    def test_one_too_many(self):
        def foo(a):
            return a
        d = dict(a=1, b=2)
        bound, notfound, toomany = findbind(foo, d)
        self.assertIsNone(bound)
        self.assertEmpty(notfound)
        self.assertIn('b', toomany)

    def test_one_too_many_not_found(self):
        def foo(a):
            return a
        d = dict(b=2)
        bound, notfound, toomany = findbind(foo, d)
        self.assertIsNone(bound)
        self.assertIn('a', notfound)
        self.assertNotIn('b', notfound)
        self.assertIn('b', toomany)
        self.assertNotIn('a', toomany)



class BindComplexTestCase(unittest.TestCase):
    def setUp(self):
        description = named("description", ".+")
        nicknames = counted("nicknames", "[a-zA-Z@][a-zA-Z0-9_]*")
        nickname = named("nickname", "[a-zA-Z@][a-zA-Z0-9_]*")
        comma = unnamed(",")

        x = Cat(Or(named("add", "add", may_be(description)),
                named("addto", "addto", 
                    may_be(
                        Option(nicknames, comma),
                        Option(nicknames, comma),
                        Option(nicknames, comma),
                        Option(nicknames, comma),
                        ZeroOrMore(named("too_many", "", nickname, comma)), 
                        Option(nickname, unnamed("(?!,)"))),
                    may_be(description))
                ), unnamed("$"))
        t = x.make_ast()
        r = x.compile()
        self.x = x
        self.t = t
        self.r = r
        self.f = lambda nickname, nicknames, description : {}.format(nickname, nicknames, description)
    

    def test_(self):
        m = self.r.match("addto raa0121,deris0126,thinca hogehoge")
        b = self.t.bindable(m.groupdict(), 'addto')
        bound, missing, too_many = findbind(self.f, b)
        self.assertIsNotNone(bound)


if __name__ == '__main__':
    unittest.main()
