#!/usr/bin/python
# -*- coding: utf-8 -*-

import unittest
import re

from functools import partial
from lib.reast import *

ws = unnamed(" ")

def may_be(*xs):
    return Option(OneOrMore(ws), Option(*xs))


class ReastTestCase(unittest.TestCase):
    def test_make(self):
        x = named('a', 'a')
        ast = x.build()
        self.assertEqual("(?P<_a>a)", ast.make_pat())
        
    def test_compile(self): 
        x = named('a', 'a')
        ast = x.build()
        got = ast.compile()
        self.assertIsNotNone(got)# _sre.SRE_Pattern

    def test_match(self):
        x = named('a', 'a')
        ast = x.build()
        r = ast.compile()
        m = r.match('abc')
        self.assertIsNotNone(m.mo)

    def test_match(self):
        x = named('a', 'a',
                may_be(named("foo", "foo")),
                may_be(named("bar", "bar")),
                may_be(named("buz", "buz")),
                unnamed("$"))
        ast = x.build()
        r = ast.compile()
        m = r.match('abc')
        self.assertIsNone(m)
    
        m = r.match('a foo')
        self.assertIsNotNone(m)

        m = r.match('a bar')
        self.assertIsNotNone(m)

    def test_make_capture(self):
        x = named('a', 'a',
                may_be(named("foo", "foo")),
                may_be(named("bar", "bar")),
                may_be(named("baz", "baz")),
                unnamed("$"))
        ast = x.build()
        cap = ast.make_capture()
        self.assertIsNotNone(cap["a"])
        self.assertIn("foo", cap["a"][0])
        self.assertIsNotNone(cap["a"][0]["foo"][0])
        self.assertIn("bar", cap["a"][0])
        self.assertIsNotNone(cap["a"][0]["bar"][0])
        self.assertIn("baz", cap["a"][0])
        self.assertIsNotNone(cap["a"][0]["baz"][0])

    def test_smart_deep_nesting(self):
        x = named('a', 'a',
                may_be(named("foo", "foo",
                    may_be(named("bar", "bar",
                        may_be(named("baz", "baz")))))),
                unnamed("$"))
        astt = x.build()
        cap = astt.make_capture()
        self.assertIn("foo", cap["a"][0])
        self.assertIn("bar", cap["a"][0]["foo"][0])
        self.assertIn("baz", cap["a"][0]["foo"][0]["bar"][0])
        self.assertIsNotNone(cap["a"][0]["foo"][0]["bar"][0]["baz"])



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
        self.x = x
        self.ast = x.build()
        self.cap = self.ast.make_capture()
        self.r = self.ast.compile()

    def test_add_arg(self):
        m = self.r.match("add hogehoge")
        d = m.groupdict()
        ast = self.ast
        assoc = self.cap.associate(d)

        self.assertIn('_add', assoc)
        self.assertEqual('add', assoc['_add'].name)

        self.assertIn('_add_description', assoc)
        self.assertEqual('description', assoc['_add_description'].name)
        self.assertEqual('hogehoge', d['_add_description'])

    def test_addto_args(self):
        m = self.r.match("addto raa0121,deris0126,thinca hogehoge")
        d = m.groupdict()
        assoc = self.cap.associate(d)

        self.assertIn('_addto', assoc)
        self.assertEqual('addto', assoc['_addto'].name)

        self.assertIn('_addto_nickname', assoc)
        self.assertEqual('nickname', assoc['_addto_nickname'].name)
        self.assertEqual('thinca', d['_addto_nickname'])

        ast = self.ast
        found = ast.find(('addto', ))
        self.assertTrue(found)
        self.assertEqual(len(found), 1)
        found = found.pop()
        print(found.name, found.regexp_name)

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
        notfound, toomany = findbind(foo, d)
        self.assertEmpty(notfound)
        self.assertEmpty(toomany)
        self.assertEqual(1, foo(**d))


    def test_one(self):
        def foo(a):
            return a
        d = {"a":10}
        notfound, toomany = findbind(foo, d)
        self.assertEmpty(notfound)
        self.assertEmpty(toomany)
        self.assertEqual(10, foo(**d))

    def test_one_not_found(self):
        def foo(a):
            return a
        d = {}
        notfound, toomany = findbind(foo, d)
        self.assertIn('a', notfound)
        self.assertEmpty(toomany)

    def test_one_too_many(self):
        def foo(a):
            return a
        d = dict(a=1, b=2)
        notfound, toomany = findbind(foo, d)
        self.assertEmpty(notfound)
        self.assertIn('b', toomany)

    def test_one_too_many_not_found(self):
        def foo(a):
            return a
        d = dict(b=2)
        notfound, toomany = findbind(foo, d)
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
        t = x.build()
        c = t.make_capture()
        r = t.compile()
        self.x = x
        self.ast = t
        self.c = c
        self.r = r

        def foo(nickname, nicknames, description):
            return nickname, nicknames, description

        self.f = foo 
    

    def test_(self):
        m = self.r.match("addto raa0121,deris0126,thinca hogehoge")
        d = m.groupdict()
        assoc = self.c.associate(d)
        b = bindable(assoc, d, ('addto',))
        missing, too_many = findbind(self.f, b)
        self.assertFalse(missing)
        self.assertFalse(too_many)
        r = self.f(**b)
        self.assertEqual('thinca', r[0])
        self.assertEqual(set(['raa0121', 'deris0126']), r[1])
        self.assertEqual('hogehoge', r[2])


if __name__ == '__main__':
    unittest.main()
