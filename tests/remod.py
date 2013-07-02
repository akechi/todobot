#!/usr/bin/python
# -*- coding: utf-8 -*-

import unittest
import re

from lib.remod import *

ws = unnamed(" ")
class may_be(Base):
    def make(self, parent):
        return Option(OneOrMore(ws), Option(*(self.fs))).make(parent)


class RemodTestCase(unittest.TestCase):
    def test_make(self):
        x = named('a', 'a')
        self.assertEqual("(?P<_a>a(?:))", x.make(''))
        
    def test_compile(self): 
        x = named('a', 'a')
        got = x.compile()
        self.assertIsNotNone(got.rx)# _sre.SRE_Pattern

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
        self.assertIsNotNone(m.mo)

        m = r.match('a bar')
        self.assertIsNotNone(m.mo)

    def test_smart(self):
        x = named('a', 'a',
                may_be(named("foo", "foo")),
                may_be(named("bar", "bar")),
                may_be(named("baz", "baz")),
                unnamed("$"))
        r = x.compile()
        m = r.match('a bar')
        s = m.smart()
        self.assertIsNotNone(s["a"])
        self.assertIn("bar", s["a"])
        self.assertIsNotNone(s["a"]["bar"])
        self.assertEqual("bar", s["a"]["bar"])



if __name__ == '__main__':
    unittest.main()
