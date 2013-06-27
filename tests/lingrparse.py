#!/usr/bin/python
# -*- coding: utf-8 -*-

import unittest

from todo.lingrparse import parse


class ParseTestCase(unittest.TestCase):

    def assertHasNotNone(self, d, k):
        self.assertIsNotNone(d)
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
        self.assertHasNotNone(found, '_hashtodo')

    def test_about(self):
        found = parse("#todo about")
        self.assertIsNotNone(found)
        self.assertHasNotNone(found, '_hashtodo')
        self.assertHasNotNone(found, '_about')

    def test_about_blackhole(self):
        found = parse("#todo about xhaxeha foabar")
        self.assertIsNotNone(found)
        self.assertHasNotNone(found, '_hashtodo')
        self.assertHasNotNone(found, '_about')

    def test_add(self):
        found = parse("#todo add foo")
        self.assertIsNotNone(found)
        self.assertHasNotNone(found, '_hashtodo')
        self.assertHasNotNone(found, '_add')
        self.assertHasNotNone(found, '_add_description')
        self.assertEqual('foo', found['_add_description'])

    def test_add_no_description(self):
        found = parse("#todo add")
        self.assertIsNotNone(found)
        self.assertHasNotNone(found, '_hashtodo')
        self.assertHasNotNone(found, '_add')
        self.assertHasNone(found, '_add_description')

    def test_addto(self):
        found = parse("#todo addto who bar")
        self.assertIsNotNone(found)
        self.assertHasNotNone(found, '_hashtodo')
        self.assertHasNotNone(found, '_addto')
        self.assertHasNotNone(found, '_addto_nickname')
        self.assertHas(found, '_addto_nickname', 'who')
        self.assertHasNotNone(found, '_addto_description')
        self.assertHas(found, '_addto_description', 'bar')

    def test_addto_multi(self):
        found = parse("#todo addto alice,bob,charlie bar")
        self.assertIsNotNone(found)
        self.assertHasNotNone(found, '_hashtodo')
        self.assertHasNotNone(found, '_addto')
        self.assertHasNotNone(found, '_addto_nickname')
        self.assertHas(found, '_addto_u1_nickname', 'alice')
        self.assertHas(found, '_addto_u2_nickname', 'bob')
        self.assertHas(found, '_addto_nickname', 'charlie')
        self.assertHasNotNone(found, '_addto_description')
        self.assertHas(found, '_addto_description', 'bar')

    def test_addto_multi_too_many(self):
        found = parse("#todo addto one,two,three,four,five,six,seven bar")
        self.assertIsNotNone(found)
        self.assertHasNotNone(found, '_hashtodo')
        self.assertHasNotNone(found, '_addto')
        self.assertHasNotNone(found, '_addto_nickname')
        self.assertHas(found, '_addto_u1_nickname', 'one')
        self.assertHas(found, '_addto_u2_nickname', 'two')
        self.assertHas(found, '_addto_too_maney_nickname', 'six')
        self.assertHasNotNone(found, '_addto_description')
        self.assertHas(found, '_addto_description', 'bar')

    def test_addto_no_nickname(self):
        found = parse("#todo addto")
        self.assertIsNotNone(found)
        self.assertHasNotNone(found, '_hashtodo')
        self.assertHasNotNone(found, '_addto')
        self.assertHasNone(found, '_addto_nickname')
        self.assertHasNone(found, '_addto_description')

    def test_addto_no_nickname_with_space(self):
        found = parse("#todo addto ")
        self.assertIsNotNone(found)
        self.assertHasNotNone(found, '_hashtodo')
        self.assertHasNotNone(found, '_addto')
        self.assertHasNone(found, '_addto_nickname')
        self.assertHasNone(found, '_addto_description')

    def test_addto_no_description(self):
        found = parse("#todo addto who")
        self.assertHasNotNone(found, '_hashtodo')
        self.assertHasNotNone(found, '_addto')
        self.assertHasNotNone(found, '_addto_nickname')
        self.assertHas(found, '_addto_nickname', 'who')
        self.assertHasNone(found, '_addto_description')

    def test_addto_no_description_with_space(self):
        found = parse("#todo addto who ")
        self.assertHasNotNone(found, '_hashtodo')
        self.assertHasNotNone(found, '_addto')
        self.assertHasNotNone(found, '_addto_nickname')
        self.assertHas(found, '_addto_nickname', 'who')
        self.assertHasNone(found, '_addto_description')

    def test_help(self):
        found = parse("#todo help")
        self.assertIsNotNone(found)
        self.assertHasNotNone(found, '_hashtodo')
        self.assertHasNotNone(found, '_help')
        self.assertHasNone(found, '_help_command')

    def test_help_with_space(self):
        found = parse("#todo help ")
        self.assertIsNotNone(found)
        self.assertHasNotNone(found, '_hashtodo')
        self.assertHasNotNone(found, '_help')
        self.assertHasNone(found, '_help_command')

    def test_help_xxx(self):
        found = parse("#todo help xxx")
        self.assertIsNotNone(found)
        self.assertHasNotNone(found, '_hashtodo')
        self.assertHasNotNone(found, '_help')
        self.assertHasNotNone(found, '_help_command')
        self.assertHas(found, '_help_command', 'xxx')

    def test_help_xxx_with_space(self):
        found = parse("#todo help xxx ")
        self.assertIsNotNone(found)
        self.assertHasNotNone(found, '_hashtodo')
        self.assertHasNotNone(found, '_help')
        self.assertHasNotNone(found, '_help_command')
        self.assertHas(found, '_help_command', 'xxx')




if __name__ == '__main__':
    unittest.main()

