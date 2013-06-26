#!/usr/bin/python
# -*- coding: utf-8 -*-

import unittest

from todo.lingrparse import parse


class ParseTestCase(unittest.TestCase):

    def assertHasNotNone(self, d, k):
        self.assertIsNotNone(d[k])

    def assertHasNone(self, d, k):
        self.assertIsNone(d[k])

    def assertHas(self, d, k, v):
        self.assertEqual(d[k], v)

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
        self.assertHasNotNone(found, '_sharptodo')
        self.assertHasNotNone(found, '_about')

    def test_add(self):
        found = parse("#todo add foo")
        self.assertIsNotNone(found)
        self.assertHasNotNone(found, '_sharptodo')
        self.assertHasNotNone(found, '_add')
        self.assertHasNotNone(found, '_add_description')
        self.assertEqual('foo', found['_add_description'])

    def test_add_no_description(self):
        found = parse("#todo add")
        self.assertIsNotNone(found)
        self.assertHasNotNone(found, '_sharptodo')
        self.assertHasNotNone(found, '_add')
        self.assertHasNone(found, '_add_description')

    def test_addto(self):
        found = parse("#todo addto who bar")
        self.assertIsNotNone(found)
        self.assertHasNotNone(found, '_sharptodo')
        self.assertHasNotNone(found, '_addto')
        self.assertHasNotNone(found, '_addto_nickname')
        self.assertHas(found, '_addto_nickname', 'who')
        self.assertHasNotNone(found, '_addto_description')
        self.assertHas(found, '_addto_description', 'bar')

    def test_addto_no_nickname(self):
        found = parse("#todo addto")
        self.assertIsNotNone(found)
        self.assertHasNotNone(found, '_sharptodo')
        self.assertHasNotNone(found, '_addto')
        self.assertHasNone(found, '_addto_nickname')
        self.assertHasNone(found, '_addto_description')

    def test_addto_no_nickname_with_space(self):
        found = parse("#todo addto ")
        self.assertIsNotNone(found)
        self.assertHasNotNone(found, '_sharptodo')
        self.assertHasNotNone(found, '_addto')
        self.assertHasNone(found, '_addto_nickname')
        self.assertHasNone(found, '_addto_description')

    def test_addto_no_description(self):
        found = parse("#todo addto who")
        self.assertHasNotNone(found, '_sharptodo')
        self.assertHasNotNone(found, '_addto')
        self.assertHasNotNone(found, '_addto_nickname')
        self.assertHas(found, '_addto_nickname', 'who')
        self.assertHasNone(found, '_addto_description')

    def test_addto_no_description_with_space(self):
        found = parse("#todo addto who ")
        self.assertHasNotNone(found, '_sharptodo')
        self.assertHasNotNone(found, '_addto')
        self.assertHasNotNone(found, '_addto_nickname')
        self.assertHas(found, '_addto_nickname', 'who')
        self.assertHasNone(found, '_addto_description')



if __name__ == '__main__':
    unittest.main()

