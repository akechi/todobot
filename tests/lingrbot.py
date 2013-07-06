#!/usr/bin/python
# -*- coding: utf-8 -*-

import unittest
from datetime import datetime
import json
import io

from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker

from todo.lingrbot import ToDoBot, Postman 
from todo import models

from mocks import LingrUser

DBTESTDATA = """\
{"created_at": "2013-05-15 14:02:50.910459", "username": "raa0121", "description": "test data 1", "status": false}
{"created_at": "2013-05-15 14:02:51.910459", "username": "raa0121", "description": "test data 2", "status": false}
{"created_at": "2013-05-15 14:02:52.910459", "username": "raa0121", "description": "test data 3", "status": true}
{"created_at": "2013-05-15 14:02:53.910459", "username": "bgnori", "description": "test data 4", "status": false}
{"created_at": "2013-05-15 14:02:54.910459", "username": "bgnori", "description": "test data 5", "status": true}
{"created_at": "2013-06-02 04:53:54", "username": "xyz", "description": "BD\u304c\u5272\u308c\u305f\u3053\u3068\u3092\u78ba\u8a8d\u3059\u308b", "status": false}
{"created_at": "2013-06-02 20:21:28", "username": "xyz", "description": "\u6b21\u56de\u4ee5\u964d\u306e\u70ba\u306e\u8cc7\u6599\u3092\u4f5c\u308b(BBQ)", "status": false}
{"created_at": "2013-05-30 20:39:37", "username": "xyz", "description": "\u30ed\u30fc\u30bd\u30f3\u3067L\u30c1\u30ad\u3068\u30a4\u30e4\u30db\u30f3\u8cb7\u3044\u306b\u884c\u304f", "status": false}
"""


def flatten_iter(xxs):
    for xs in xxs:
        if isinstance(xs, list):
            for x in xs:
                yield x
        else:
            yield xs


def flatten(xxs):
    return list(flatten_iter(xxs))

class ToDoBotDipatchTestCase(unittest.TestCase):
    def setUp(self):
        self.postman = Postman()
        self.bot = ToDoBot(self.postman)

    def test_strip(self):
        bot = self.bot
        d = bot.strip(dict(_add=1, _add_description='test 1'), '_add')

        self.assertNotIn('_add', d)
        self.assertNotIn('_add_description', d)
        self.assertIn('description', d)


    def test_find_method_empty(self):
        bot = self.bot
        m, n = bot.find_method(dict())
        self.assertIsNone(m)
        self.assertIsNone(n)

    def test_find_method_found(self):
        bot = self.bot
        m, n = bot.find_method(dict(_add=1, _add_description='test 1'))
        self.assertIsNotNone(m)
        self.assertEqual(bot.handle_add, m)
        self.assertIsNotNone(n)
        self.assertEqual(n, '_add')


    def test_make_help_map(self):
        bot = self.bot
        d = bot.make_help_map()

        self.assertIn('handle_done', d)
        self.assertIn('handle_help', d)
        self.assertEqual(d['handle_add'], "#todo add [description]")
        self.assertEqual("""#todo done [id] [id] [id] [id] [id]""", d['handle_done'])



class ToDoBotDBTestCase(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine('sqlite:///:memory:', poolclass=QueuePool)

        conn = self.engine.connect()
        self.conn = conn
        models.get_session = scoped_session(sessionmaker(bind=self.conn))
        self.postman = Postman()
        self.bot = ToDoBot(self.postman)
    
        models.make_tables()

        for line in io.StringIO(DBTESTDATA):
            td = models.ToDo.from_json(line)
        
        self.raa0121 = LingrUser('raa0121')
        self.xyz = LingrUser('xyz')

        self.now = datetime.now()

    def tearDown(self):
        self.engine.dispose()


    def test_not_implemented(self):
        req = self.raa0121.say('#todo notimplemented')
        event = json.loads(req)['events'][0]
        s = self.bot.on_json(event)

        xs = flatten([x.splitlines() for x in s.render_for_lingr(500)])

        self.assertTrue(xs)
        self.assertEqual('そのcommand実装されてない. "#todo notimplemented"', xs[0])

    def test_help(self):
        req = self.raa0121.say('#todo help')
        event = json.loads(req)['events'][0]
        s = self.bot.on_json(event)

        xs = flatten([x.splitlines() for x in s.render_for_lingr(500)])
        self.assertIn('#todo done [id] [id] [id] [id] [id]', xs)
        self.assertIn('#todo show [id]', xs)


    def test_help_arg(self):
        req = self.raa0121.say('#todo help done')
        event = json.loads(req)['events'][0]
        s = self.bot.on_json(event)

        xs = flatten([x.splitlines() for x in s.render_for_lingr(500)])
        self.assertIn('#todo done [id] [id] [id] [id] [id]', xs)
        self.assertNotIn('#todo show [id]', xs)

    def test_help_bad_arg(self):
        req = self.raa0121.say('#todo help foo')
        event = json.loads(req)['events'][0]
        s = self.bot.on_json(event)


        xs = flatten([x.splitlines() for x in s.render_for_lingr(500)])
        self.assertIn('#todo done [id] [id] [id] [id] [id]', xs)
        self.assertIn('#todo show [id]', xs)

    def test_add(self):
        req = self.raa0121.say('#todo add test_add')
        event = json.loads(req)['events'][0]
        s = self.bot.on_json(event)

        result = models.ToDo.list_whose('raa0121', status=False)
        self.assertEqual(3, len([r for r in result]))


    def test_addto(self):
        req = self.raa0121.say('#todo addto bgnori test_add')
        event = json.loads(req)['events'][0]
        s = self.bot.on_json(event)

        result = models.ToDo.list_whose('raa0121', status=False)
        self.assertEqual(2, len([r for r in result]))
        result = models.ToDo.list_whose('bgnori', status=False)
        self.assertEqual(2, len([r for r in result]))

    def test_addto_multi(self):
        req = self.raa0121.say('#todo addto bgnori,raa0121,mopp test_add')
        event = json.loads(req)['events'][0]
        s = self.bot.on_json(event)

        result = models.ToDo.list_whose('raa0121', status=False)
        self.assertEqual(3, len([r for r in result]))
        result = models.ToDo.list_whose('bgnori', status=False)
        self.assertEqual(2, len([r for r in result]))
        result = models.ToDo.list_whose('mopp', status=False)
        self.assertEqual(1, len([r for r in result]))

    def test_list_all(self):
        req = self.raa0121.say('#todo list-all')
        event = json.loads(req)['events'][0]
        s = self.bot.on_json(event)

        xs = [r.prnformat(self.now) for r in s.rows]
        self.assertEqual(1, len([x for x in xs if x.startswith('[X]')]))
        self.assertEqual(2, len([x for x in xs if x.startswith('[_]')]))


    def test_list_done(self):
        req = self.raa0121.say('#todo list-done')
        event = json.loads(req)['events'][0]
        s = self.bot.on_json(event)

        xs = [r.prnformat(self.now) for r in s.rows]
        self.assertEqual(1, len([x for x in xs if x.startswith('[X]')]))
        self.assertEqual(0, len([x for x in xs if x.startswith('[_]')]))

    def test_list(self):
        req = self.raa0121.say('#todo list')
        event = json.loads(req)['events'][0]
        s = self.bot.on_json(event)

        xs = [r.prnformat(self.now) for r in s.rows]
        self.assertEqual(0, len([x for x in xs if x.startswith('[X]')]))
        self.assertEqual(2, len([x for x in xs if x.startswith('[_]')]))

    def test_list_arg(self):
        req = self.xyz.say('#todo list 0-10 イヤホン')
        event = json.loads(req)['events'][0]
        s = self.bot.on_json(event)

        xs = [r.prnformat(self.now) for r in s.rows]
        self.assertEqual(0, len([x for x in xs if x.startswith('[X]')]))
        self.assertEqual(1, len([x for x in xs if x.startswith('[_]')]))


    def test_listof_all(self):
        req = self.raa0121.say('#todo listof-all bgnori')
        event = json.loads(req)['events'][0]
        s = self.bot.on_json(event)

        xs = [r.prnformat(self.now) for r in s.rows]
        self.assertEqual(1, len([x for x in xs if x.startswith('[X]')]))
        self.assertEqual(1, len([x for x in xs if x.startswith('[_]')]))

    def test_listof_done(self):
        req = self.raa0121.say('#todo listof-done bgnori')
        event = json.loads(req)['events'][0]
        s = self.bot.on_json(event)

        xs = [r.prnformat(self.now) for r in s.rows]
        self.assertEqual(1, len([x for x in xs if x.startswith('[X]')]))
        self.assertEqual(0, len([x for x in xs if x.startswith('[_]')]))

    def test_listof(self):
        req = self.raa0121.say('#todo listof bgnori')
        event = json.loads(req)['events'][0]
        s = self.bot.on_json(event)

        xs = [r.prnformat(self.now) for r in s.rows]
        self.assertEqual(0, len([x for x in xs if x.startswith('[X]')]))
        self.assertEqual(1, len([x for x in xs if x.startswith('[_]')]))


    def test_list_everything(self):
        req = self.raa0121.say('#todo list-everything')
        event = json.loads(req)['events'][0]
        s = self.bot.on_json(event)

        xs = [r.prnformat(self.now) for r in s.rows]
        self.assertEqual(6, len([x for x in xs if x.startswith('[_]')]))
        self.assertEqual(2, len([x for x in xs if x.startswith('[X]')]))

    def test_done(self):
        req = self.raa0121.say('#todo done 1')
        event = json.loads(req)['events'][0]
        s = self.bot.on_json(event)
        self.assertTrue(s.text.startswith('[X]'))

        result = models.ToDo.list_whose('raa0121', status=False)
        self.assertEqual(1, len([r for r in result]))
        result = models.ToDo.list_whose('raa0121', status=True)
        self.assertEqual(2, len([r for r in result]))
        result = models.ToDo.list_whose('bgnori', status=False)
        self.assertEqual(1, len([r for r in result]))
        result = models.ToDo.list_whose('bgnori', status=True)
        self.assertEqual(1, len([r for r in result]))

    def test_done_multi(self):
        req = self.raa0121.say('#todo done 1 2 3 4 5')
        event = json.loads(req)['events'][0]
        s = self.bot.on_json(event)

        result = models.ToDo.list_whose('raa0121', status=False)
        self.assertEqual(0, len([r for r in result]))
        result = models.ToDo.list_whose('raa0121', status=True)
        self.assertEqual(3, len([r for r in result]))
        result = models.ToDo.list_whose('bgnori', status=False)
        self.assertEqual(1, len([r for r in result]))
        result = models.ToDo.list_whose('bgnori', status=True)
        self.assertEqual(1, len([r for r in result]))


    def test_edit(self):
        req = self.raa0121.say('#todo edit 1 testing edit')
        event = json.loads(req)['events'][0]
        s = self.bot.on_json(event)
        t = ''.join(s.render_for_lingr(500))
        self.assertIn("testing edit", t)

    def test_del(self):
        req = self.raa0121.say('#todo del 2')
        event = json.loads(req)['events'][0]
        s = self.bot.on_json(event)

        result = models.ToDo.list_whose('raa0121', status=True)
        self.assertEqual(1, len([r for r in result]))
        result = models.ToDo.list_whose('raa0121', status=False)
        self.assertEqual(1, len([r for r in result]))

    def test_del_multi(self):
        req = self.raa0121.say('#todo del 2 3 1')
        event = json.loads(req)['events'][0]
        s = self.bot.on_json(event)

        result = models.ToDo.list_whose('raa0121', status=True)
        self.assertEqual(0, len([r for r in result]))
        result = models.ToDo.list_whose('raa0121', status=False)
        self.assertEqual(0, len([r for r in result]))

    def test_show(self):
        req = self.raa0121.say('#todo show 3')

        event = json.loads(req)['events'][0]
        s = self.bot.on_json(event)

        xs = [r.prnformat(self.now) for r in s.rows]
        self.assertEqual(1, len([x for x in xs if x.startswith('[X]')]))
        self.assertEqual(0, len([x for x in xs if x.startswith('[_]')]))

    def test_about(self):
        req = self.raa0121.say('#todo about')
        event = json.loads(req)['events'][0]
        s = self.bot.on_json(event)

        xs = s.text.splitlines()
        self.assertIn("It provides task management feature to lingr room.", xs)
        self.assertIn("see https://github.com/akechi/todobot", xs)


LISTCOMMAND_TESTDATA = """\
{"created_at": "2013-06-02 04:53:54", "username": "raa0121", "description": "BD\u304c\u5272\u308c\u305f\u3053\u3068\u3092\u78ba\u8a8d\u3059\u308b", "status": false}
{"created_at": "2013-06-02 20:21:28", "username": "raa0121", "description": "\u6b21\u56de\u4ee5\u964d\u306e\u70ba\u306e\u8cc7\u6599\u3092\u4f5c\u308b(BBQ)", "status": false}
{"created_at": "2013-05-30 20:39:37", "username": "raa0121", "description": "\u30ed\u30fc\u30bd\u30f3\u3067L\u30c1\u30ad\u3068\u30a4\u30e4\u30db\u30f3\u8cb7\u3044\u306b\u884c\u304f", "status": false}
{"created_at": "2013-05-31 04:24:44", "username": "raa0121", "description": "VAC\u306e\u8a18\u4e8b\u660e\u65e5\u304b\u3089\u672c\u6c17\u3092\u51fa\u3059", "status": false}
{"created_at": "2013-05-31 05:34:34", "username": "raa0121", "description": "\u30cb\u30e3\u30eb\u5b50\u306eBD\u304c\u5272\u308c\u308b\u307e\u3048\u306b\u8996\u8074\u3059\u308b", "status": false}
"""


class ToDoBotListCommandTestCase(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine('sqlite:///:memory:', poolclass=QueuePool)

        conn = self.engine.connect()
        self.conn = conn
        models.get_session = scoped_session(sessionmaker(bind=self.conn))
        self.postman = Postman()
        self.bot = ToDoBot(self.postman)
    
        models.make_tables()

        for line in io.StringIO(LISTCOMMAND_TESTDATA):
            td = models.ToDo.from_json(line)
        
        self.raa0121 = LingrUser('raa0121')
        self.xyz = LingrUser('xyz')
        self.now = datetime.now()

    def test_start_hyph_end_jpkw(self):
        req = self.raa0121.say('#todo list 0-10 イヤホン')
        event = json.loads(req)['events'][0]
        s = self.bot.on_json(event)

        xs = [r.prnformat(self.now) for r in s.rows]
        self.assertEqual(0, len([x for x in xs if x.startswith('[X]')]))
        self.assertEqual(1, len([x for x in xs if x.startswith('[_]')]))
        self.assertIn('ローソンでLチキとイヤホン買いに行く', xs[0])

    def test_jpkw(self):
        req = self.raa0121.say('#todo list 割')
        event = json.loads(req)['events'][0]
        s = self.bot.on_json(event)

        xs = [r.prnformat(self.now) for r in s.rows]
        self.assertEqual(0, len([x for x in xs if x.startswith('[X]')]))
        self.assertEqual(2, len([x for x in xs if x.startswith('[_]')]))

    def test_start_jpkw(self):
        req = self.raa0121.say('#todo list 1- 割')
        event = json.loads(req)['events'][0]
        s = self.bot.on_json(event)

        xs = [r.prnformat(self.now) for r in s.rows]
        self.assertEqual(0, len([x for x in xs if x.startswith('[X]')]))
        self.assertEqual(1, len([x for x in xs if x.startswith('[_]')]))

    def test_listof_start_jpkw(self):
        req = self.xyz.say('#todo listof raa0121 1- 割')
        event = json.loads(req)['events'][0]
        s = self.bot.on_json(event)

        xs = [r.prnformat(self.now) for r in s.rows]
        self.assertEqual(0, len([x for x in xs if x.startswith('[X]')]))
        self.assertEqual(1, len([x for x in xs if x.startswith('[_]')]))




GROUPTESTDATA = """\
{"id": 216, "created_at": "2013-06-15 08:41:14", "username": "@VAC", "description": "Vim \u306b\u30d5\u30a1\u30a4\u30eb\u3092\u30c9\u30ed\u30c3\u30d7\u3057\u305f\u6642\u306b\u65b0\u3057\u3044\u30bf\u30d6\u3067\u958b\u3044\u3066\u6b32\u3057\u3044", "status": false}
{"id": 217, "created_at": "2013-06-15 08:42:29", "username": "@VAC", "description": "neocomplete.vim \u3078\u306e\u79fb\u884c\u8a18\u4e8b", "status": false}
{"id": 219, "created_at": "2013-06-15 18:41:57", "username": "@VAC", "description": "autoload\u304b\u3089 doc \u96db\u4f5c\u3063\u3066\u304f\u308c\u308b\u30d7\u30e9\u30b0\u30a4\u30f3\u304c\u307b\u3057\u3044", "status": false}
{"id": 220, "created_at": "2013-06-16 00:36:15", "username": "@VAC", "description": "reunions.vim\u306b\u3064\u3044\u3066", "status": false}
"""

class ToDoBotGroupTestCase(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine('sqlite:///:memory:', poolclass=QueuePool)

        conn = self.engine.connect()
        self.conn = conn
        models.get_session = scoped_session(sessionmaker(bind=self.conn))
        self.postman = Postman()
        self.bot = ToDoBot(self.postman)
    
        models.make_tables()

        for line in io.StringIO(GROUPTESTDATA):
            td = models.ToDo.from_json(line)
        
        self.raa0121 = LingrUser('raa0121')

        self.now = datetime.now()

    def test_listof(self):
        pass

    def test_addto(self):
        pass

    def test_del(self):
        pass

    def test_done(self):
        pass

    def test_edit(self):
        pass


if __name__ == '__main__':
    unittest.main()

