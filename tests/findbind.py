#!/usr/bin/python
# -*- coding: utf-8 -*-


import unittest

from lib.findbind import findbind
from functools import partial


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

if __name__ == '__main__':
    unittest.main()


