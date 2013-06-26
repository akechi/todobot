#!/usr/bin/python
# -*- coding: utf-8 -*-

import unittest

from todo.lingrparse import parse


class ParseTestCase(unittest.TestCase):

    def test_bad_1(self):
        found = parse("hello, world!")
        self.assertIsNone(found)

    def test_bad_2(self):
        found = parse("#tod")
        self.assertIsNone(found)

    def test_bad_3(self):
        found = parse("#todos")
        self.assertIsNone(found)

    def test_no_command(self):
        found = parse("#todo")
        self.assertIsNotNone(found)
        self.assertIn('_sharptodo' ,found)

    def test_about(self):
        found = parse("#todo about")
        self.assertIsNotNone(found)
        self.assertIn('_sharptodo', found)
        self.assertIn('_about', found)

    def test_about_blackhole(self):
        found = parse("#todo about xhaxeha foabar")
        self.assertIsNotNone(found)
        self.assertIn('_sharptodo', found)
        self.assertIn('_about', found)

    def test_add(self):
        found = parse("#todo add foo")
        self.assertIsNotNone(found)
        self.assertIn('_sharptodo', found)
        self.assertIn('_add', found)
        self.assertIn('_add_description', found)
        self.assertEqual('foo', found['_add_description'])

    def test_addto(self):
        found = parse("#todo addto who bar")
        self.assertIsNotNone(found)
        self.assertIn('_sharptodo', found)
        self.assertIn('_addto', found)
        self.assertIn('_addto_nickname', found)
        self.assertEqual('who', found['_addto_nickname'])
        self.assertIn('_addto_description', found)
        self.assertEqual('bar', found['_addto_description'])


if __name__ == '__main__':
    unittest.main()
