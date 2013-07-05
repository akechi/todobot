#!/usr/bin/python
# -*- coding: utf-8 -*-

import unittest
import re

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




if __name__ == '__main__':
    unittest.main()

