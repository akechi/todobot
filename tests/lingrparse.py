#!/usr/bin/python
# -*- coding: utf-8 -*-

import unittest
import json

from todo.lingrparse import parse, builder
from mocks import LingrUser


class ParseTestCase(unittest.TestCase):

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
        self.assertIn('_hashtodo', found)

    def test_bad_command(self):
        found = parse("#todo foobar")
        self.assertIsNotNone(found)
        self.assertIn('_hashtodo', found)

    def test_about(self):
        found = parse("#todo about")
        self.assertIsNotNone(found)
        self.assertIn('_hashtodo', found)
        self.assertIn('_about', found)

    def test_about_blackhole(self):
        found = parse("#todo about xhaxeha foabar")
        self.assertIsNotNone(found)
        self.assertIn('_hashtodo', found)
        self.assertIn('_about', found)

    def test_add(self):
        found = parse("#todo add foo")
        self.assertIsNotNone(found)
        self.assertIn('_hashtodo', found)
        self.assertIn('_add', found)
        self.assertIn('_add_description', found)
        self.assertEqual('foo', found['_add_description'])

    def test_add_no_description(self):
        found = parse("#todo add")
        self.assertIsNotNone(found)
        self.assertIn('_hashtodo', found)
        self.assertIn('_add', found)
        self.assertNotIn('_add_description', found)

    def test_addto(self):
        found = parse("#todo addto who bar")
        self.assertIsNotNone(found)
        self.assertIn('_hashtodo', found)
        self.assertIn('_addto', found)
        self.assertIn('_addto_nickname', found)
        self.assertHas(found, '_addto_nickname', 'who')
        self.assertIn('_addto_description', found)
        self.assertHas(found, '_addto_description', 'bar')

    def test_addto_multi(self):
        found = parse("#todo addto alice,bob,charlie bar")
        self.assertIsNotNone(found)
        self.assertIn('_hashtodo', found)
        self.assertIn('_addto', found)
        self.assertIn('_addto_nickname', found)
        self.assertHas(found, '_addto_nicknames0', 'alice')
        self.assertHas(found, '_addto_nicknames1', 'bob')
        self.assertHas(found, '_addto_nickname', 'charlie')
        self.assertIn('_addto_description', found)
        self.assertHas(found, '_addto_description', 'bar')

    def test_addto_multi_too_many(self):
        found = parse("#todo addto one,two,three,four,five,six,seven bar")
        self.assertIsNotNone(found)
        self.assertIn('_hashtodo', found)
        self.assertIn('_addto', found)
        self.assertIn('_addto_nickname', found)
        self.assertHas(found, '_addto_nicknames0', 'one')
        self.assertHas(found, '_addto_nicknames1', 'two')
        self.assertHas(found, '_addto_too_many_nickname', 'six')
        self.assertIn('_addto_description', found)
        self.assertHas(found, '_addto_description', 'bar')

    def test_addto_no_nickname(self):
        found = parse("#todo addto")
        self.assertIsNotNone(found)
        self.assertIn('_hashtodo', found)
        self.assertIn('_addto', found)
        self.assertNotIn('_addto_nickname', found)
        self.assertNotIn('_addto_description', found)

    def test_addto_no_nickname_with_space(self):
        found = parse("#todo addto ")
        self.assertIsNotNone(found)
        self.assertIn('_hashtodo', found)
        self.assertIn('_addto', found)
        self.assertNotIn('_addto_nickname', found)
        self.assertNotIn('_addto_description', found)

    def test_addto_no_description(self):
        found = parse("#todo addto who")
        self.assertIn('_hashtodo', found)
        self.assertIn('_addto', found)
        self.assertIn('_addto_nickname', found)
        self.assertHas(found, '_addto_nickname', 'who')
        self.assertNotIn('_addto_description', found)

    def test_addto_no_description_with_space(self):
        found = parse("#todo addto who ")
        self.assertIn('_hashtodo', found)
        self.assertIn('_addto', found)
        self.assertIn('_addto_nickname', found)
        self.assertHas(found, '_addto_nickname', 'who')
        self.assertNotIn('_addto_description', found)

    def test_help(self):
        found = parse("#todo help")
        self.assertIsNotNone(found)
        self.assertIn('_hashtodo', found)
        self.assertIn('_help', found)
        self.assertNotIn('_help_command', found)

    def test_help_with_space(self):
        found = parse("#todo help ")
        self.assertIsNotNone(found)
        self.assertIn('_hashtodo', found)
        self.assertIn('_help', found)
        self.assertNotIn('_help_command', found)

    def test_help_xxx(self):
        found = parse("#todo help xxx")
        self.assertIsNotNone(found)
        self.assertIn('_hashtodo', found)
        self.assertIn('_help', found)
        self.assertIn('_help_command', found)
        self.assertHas(found, '_help_command', 'xxx')

    def test_help_xxx_with_space(self):
        found = parse("#todo help xxx ")
        self.assertIsNotNone(found)
        self.assertIn('_hashtodo', found)
        self.assertIn('_help', found)
        self.assertIn('_help_command', found)
        self.assertHas(found, '_help_command', 'xxx')

    def test_edit(self):
        found = parse("#todo edit 1 bar")
        self.assertIsNotNone(found)
        self.assertIn('_hashtodo', found)
        self.assertIn('_edit', found)
        self.assertIn('_edit_task_id', found)
        self.assertHas(found, '_edit_task_id', '1')
        self.assertIn('_edit_description', found)
        self.assertHas(found, '_edit_description', 'bar')

    def test_edit_bad_id(self):
        found = parse("#todo edit xone bar")
        self.assertIsNotNone(found)
        self.assertIn('_hashtodo', found)
        self.assertIn('_edit', found)
        self.assertNotIn('_edit_task_id', found)

    def test_edit_no_description(self):
        found = parse("#todo edit 1")
        self.assertIsNotNone(found)
        self.assertIn('_hashtodo', found)
        self.assertIn('_edit', found)
        self.assertIn('_edit_task_id', found)
        self.assertHas(found, '_edit_task_id', '1')
        self.assertNotIn('_edit_description', found)

    def test_edit_no_description_with_space(self):
        found = parse("#todo edit 1 ")
        self.assertIsNotNone(found)
        self.assertIn('_hashtodo', found)
        self.assertIn('_edit', found)
        self.assertIn('_edit_task_id', found)
        self.assertHas(found, '_edit_task_id', '1')
        self.assertNotIn('_edit_description', found)

    def test_edit_has_no_id(self):
        found = parse("#todo edit")
        self.assertIsNotNone(found)
        self.assertIn('_hashtodo', found)
        self.assertIn('_edit', found)
        self.assertNotIn('_edit_task_id', found)

    def test_data_from_json(self):
        raa0121 = LingrUser('raa0121')
        req = raa0121.say('#todo add have more unittests')
        j = json.loads(req)
        t = j['events'][0]['message']['text']
        found = parse(t)
        self.assertIsNotNone(found)
        self.assertIn('_hashtodo', found)
        self.assertIn('_add', found)
        self.assertIn('_add_description', found)
        self.assertEqual('have more unittests', found['_add_description'])

    def test_list(self):
        found = parse("#todo list")
        self.assertIsNotNone(found)
        self.assertIn('_hashtodo', found)
        self.assertIn('_list', found)

        self.assertNotIn('_list_start', found)
        self.assertNotIn('_list_end', found)
        self.assertNotIn('_list_keyword', found)

    def test_list_with_keyword(self):
        found = parse("#todo list momonga")
        self.assertIsNotNone(found)
        self.assertIn('_hashtodo', found)
        self.assertIn('_list', found)

        self.assertNotIn('_list_start', found)
        self.assertNotIn('_list_end', found)
        self.assertIn('_list_keyword', found)
        self.assertEqual(found['_list_keyword'], 'momonga')

    def test_list_with_jpkeyword(self):
        found = parse("#todo list 仕様")
        self.assertIsNotNone(found)
        self.assertIn('_hashtodo', found)
        self.assertIn('_list', found)

        self.assertNotIn('_list_start', found)
        self.assertNotIn('_list_end', found)
        self.assertIn('_list_keyword', found)
        self.assertEqual(found['_list_keyword'], '仕様')

    def test_list_with_end_of_range(self):
        found = parse("#todo list 12")
        self.assertIsNotNone(found)
        self.assertIn('_hashtodo', found)
        self.assertIn('_list', found)

        self.assertNotIn('_list_start', found)
        self.assertIn('_list_end', found)
        self.assertNotIn('_list_keyword', found)
        self.assertEqual(found['_list_end'], '12')

    def test_list_with_end_of_hyph(self):
        found = parse("#todo list -12")
        self.assertIsNotNone(found)
        self.assertIn('_hashtodo', found)
        self.assertIn('_list', found)

        self.assertNotIn('_list_start', found)
        self.assertIn('_list_end', found)
        self.assertNotIn('_list_keyword', found)
        self.assertEqual(found['_list_end'], '12')

    def test_list_with_start_of_range(self):
        found = parse("#todo list 3-")
        self.assertIsNotNone(found)
        self.assertIn('_hashtodo', found)
        self.assertIn('_list', found)

        self.assertIn('_list_start', found)
        self.assertNotIn('_list_end', found)
        self.assertNotIn('_list_both', found)
        self.assertNotIn('_list_keyword', found)
        self.assertEqual(found['_list_start'], '3')

    def test_list_with_range(self):
        found = parse("#todo list 3-12")
        self.assertIsNotNone(found)
        self.assertIn('_hashtodo', found)
        self.assertIn('_list', found)

        self.assertIn('_list_start', found)
        self.assertIn('_list_end', found)
        self.assertNotIn('_list_keyword', found)
        self.assertEqual(found['_list_start'], '3')
        self.assertEqual(found['_list_end'], '12')

    def test_list_with_and_keyword(self):
        found = parse("#todo list 3-12 momonga")
        self.assertIsNotNone(found)
        self.assertIn('_hashtodo', found)
        self.assertIn('_list', found)

        self.assertIn('_list_start', found)
        self.assertIn('_list_end', found)
        self.assertIn('_list_keyword', found)
        self.assertEqual(found['_list_start'], '3')
        self.assertEqual(found['_list_end'], '12')
        self.assertEqual(found['_list_keyword'], 'momonga')

    def test_list_with_jpkeyword_and_end_of_range(self):
        found = parse("#todo list 12 小指")
        self.assertIsNotNone(found)
        self.assertIn('_hashtodo', found)
        self.assertIn('_list', found)

        self.assertNotIn('_list_start', found)
        self.assertIn('_list_end', found)
        self.assertIn('_list_keyword', found)
        self.assertEqual(found['_list_keyword'], '小指')
        self.assertEqual(found['_list_end'], '12')

    def test_list_with_keyword_and_end_of_hyph(self):
        found = parse("#todo list -12 momonga")
        self.assertIsNotNone(found)
        self.assertIn('_hashtodo', found)
        self.assertIn('_list', found)

        self.assertNotIn('_list_start', found)
        self.assertIn('_list_end', found)
        self.assertIn('_list_keyword', found)
        self.assertEqual(found['_list_keyword'], 'momonga')
        self.assertEqual(found['_list_end'], '12')

    def test_list_with_jpkeyword_and_end_of_hyph(self):
        found = parse("#todo list -12 小指")
        self.assertIsNotNone(found)
        self.assertIn('_hashtodo', found)
        self.assertIn('_list', found)

        self.assertNotIn('_list_start', found)
        self.assertIn('_list_end', found)
        self.assertIn('_list_keyword', found)
        self.assertEqual(found['_list_keyword'], '小指')
        self.assertEqual(found['_list_end'], '12')

    def test_listof(self):
        found = parse("#todo listof raa0121")
        self.assertIsNotNone(found)
        self.assertIn('_hashtodo', found)
        self.assertIn('_listof', found)
        self.assertIn('_listof_nickname', found)
        self.assertEqual('raa0121', found['_listof_nickname'])

    def test_listof_with_end(self):
        found = parse("#todo listof raa0121 4")
        self.assertIsNotNone(found)
        self.assertIn('_hashtodo', found)
        self.assertIn('_listof', found)
        self.assertIn('_listof_nickname', found)
        self.assertIn('_listof_end', found)
        self.assertEqual('raa0121', found['_listof_nickname'])
        self.assertEqual(found['_listof_end'], '4')

    def test_listof_with_range(self):
        found = parse("#todo listof raa0121 3-12")
        self.assertIsNotNone(found)
        self.assertIn('_hashtodo', found)
        self.assertIn('_listof', found)
        self.assertIn('_listof_nickname', found)
        self.assertIn('_listof_start', found)
        self.assertIn('_listof_end', found)
        self.assertEqual('raa0121', found['_listof_nickname'])
        self.assertEqual(found['_listof_start'], '3')
        self.assertEqual(found['_listof_end'], '12')

    def test_done_multi(self):
        found = parse("#todo done 0 1 13 04 ")
        self.assertIsNotNone(found)
        self.assertIn('_hashtodo', found)
        self.assertIn('_done', found)
        self.assertIn('_done_task_ids0', found)
        self.assertHas(found, '_done_task_ids0', '0')
        self.assertHas(found, '_done_task_ids1', '1')
        self.assertHas(found, '_done_task_ids2', '13')
        self.assertHas(found, '_done_task_ids3', '04')


class AstNodeTestCase(unittest.TestCase):
    def setUp(self):
        self.ast = builder.build()
        self.cap = self.ast.make_capture()

    def test_xxx(self):
        found = parse("#todo listof raa0121 3-12")
        self.assertEqual(set([
            '_listof',
            '_listof_nickname',
            '_listof_start',
            '_listof_end',
            '_hashtodo']),
            set(self.cap.associate(found).keys()))


if __name__ == '__main__':
    unittest.main()
