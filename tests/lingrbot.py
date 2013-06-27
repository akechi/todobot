#!/usr/bin/python
# -*- coding: utf-8 -*-

import unittest
from datetime import datetime
import json

from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker

from todo.lingrbot import ToDoBot, Postman 
from todo import models

from mocks import LingrUser


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
        self.assertEqual("""#todo done [id]""", d['handle_done'])



class ToDoBotDBTestCase(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine('sqlite:///:memory:', poolclass=QueuePool)


        conn = self.engine.connect()
        self.conn = conn
        models.get_session = scoped_session(sessionmaker(bind=self.conn))
        self.postman = Postman()
        self.bot = ToDoBot(self.postman)
    
        models.make_tables()

        models.ToDo.add(username='raa0121', description='test data 1',
                created_at=datetime.now(), status = False)
        models.ToDo.add(username='raa0121', description='test data 2',
                created_at=datetime.now(), status = False)
        models.ToDo.add(username='raa0121', description='test data 3',
                created_at=datetime.now(), status = True)
        models.ToDo.add(username='bgnori', description='test data 4',
                created_at=datetime.now(), status = False)
        models.ToDo.add(username='bgnori', description='test data 5',
                created_at=datetime.now(), status = True)
        self.raa0121 = LingrUser('raa0121')


    def tearDown(self):
        self.engine.dispose()


    def test_bad_command(self):
        req = self.raa0121.say('#todo foobar')
        event = json.loads(req)['events'][0]
        s = self.bot.on_json(event)

        xs = flatten([x.splitlines() for x in s.render_for_lingr(500)])
        self.assertIn('No such command.', xs)

    def test_help(self):
        req = self.raa0121.say('#todo help')
        event = json.loads(req)['events'][0]
        s = self.bot.on_json(event)

        xs = flatten([x.splitlines() for x in s.render_for_lingr(500)])
        self.assertIn('#todo done [id]', xs)
        self.assertIn('#todo show [id]', xs)


    def test_help_arg(self):
        req = self.raa0121.say('#todo help done')
        event = json.loads(req)['events'][0]
        s = self.bot.on_json(event)

        xs = flatten([x.splitlines() for x in s.render_for_lingr(500)])
        self.assertIn('#todo done [id]', xs)
        self.assertNotIn('#todo show [id]', xs)

    def test_help_bad_arg(self):
        req = self.raa0121.say('#todo help foo')
        event = json.loads(req)['events'][0]
        s = self.bot.on_json(event)


        xs = flatten([x.splitlines() for x in s.render_for_lingr(500)])
        self.assertIn('#todo done [id]', xs)
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


    def test_list_all(self):
        req = self.raa0121.say('#todo list-all')
        event = json.loads(req)['events'][0]
        s = self.bot.on_json(event)

        xs = [r.prnformat() for r in s.rows]
        self.assertEqual(1, len([x for x in xs if x.startswith('[X]')]))
        self.assertEqual(2, len([x for x in xs if x.startswith('[_]')]))


    def test_list_done(self):
        req = self.raa0121.say('#todo list-done')
        event = json.loads(req)['events'][0]
        s = self.bot.on_json(event)

        xs = [r.prnformat() for r in s.rows]
        self.assertEqual(1, len([x for x in xs if x.startswith('[X]')]))
        self.assertEqual(0, len([x for x in xs if x.startswith('[_]')]))

    def test_list(self):
        req = self.raa0121.say('#todo list')
        event = json.loads(req)['events'][0]
        s = self.bot.on_json(event)

        xs = [r.prnformat() for r in s.rows]
        self.assertEqual(0, len([x for x in xs if x.startswith('[X]')]))
        self.assertEqual(2, len([x for x in xs if x.startswith('[_]')]))

    def test_listof_all(self):
        req = self.raa0121.say('#todo listof-all bgnori')
        event = json.loads(req)['events'][0]
        s = self.bot.on_json(event)

        xs = [r.prnformat() for r in s.rows]
        self.assertEqual(1, len([x for x in xs if x.startswith('[X]')]))
        self.assertEqual(1, len([x for x in xs if x.startswith('[_]')]))

    def test_listof_done(self):
        req = self.raa0121.say('#todo listof-done bgnori')
        event = json.loads(req)['events'][0]
        s = self.bot.on_json(event)

        xs = [r.prnformat() for r in s.rows]
        self.assertEqual(1, len([x for x in xs if x.startswith('[X]')]))
        self.assertEqual(0, len([x for x in xs if x.startswith('[_]')]))

    def test_listof(self):
        req = self.raa0121.say('#todo listof bgnori')
        event = json.loads(req)['events'][0]
        s = self.bot.on_json(event)

        xs = [r.prnformat() for r in s.rows]
        self.assertEqual(0, len([x for x in xs if x.startswith('[X]')]))
        self.assertEqual(1, len([x for x in xs if x.startswith('[_]')]))


    def test_list_everything(self):
        req = self.raa0121.say('#todo list-everything')
        event = json.loads(req)['events'][0]
        s = self.bot.on_json(event)

        xs = [r.prnformat() for r in s.rows]
        self.assertEqual(3, len([x for x in xs if x.startswith('[_]')]))
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


    def test_edit(self):
        req = self.raa0121.say('#todo edit 1 testing edit')
        event = json.loads(req)['events'][0]
        s = self.bot.on_json(event)
        t = ''.join(s.render_for_lingr(500))
        self.assertIn("testing edit", t)

    def test_del(self):
        req = self.raa0121.say('#todo done 2')
        event = json.loads(req)['events'][0]
        s = self.bot.on_json(event)

        result = models.ToDo.list_whose('raa0121', status=False)
        self.assertEqual(1, len([r for r in result]))
        result = models.ToDo.list_whose('bgnori', status=False)
        self.assertEqual(1, len([r for r in result]))

    def test_show(self):
        req = self.raa0121.say('#todo show 3')

        event = json.loads(req)['events'][0]
        s = self.bot.on_json(event)

        xs = [r.prnformat() for r in s.rows]
        self.assertEqual(1, len([x for x in xs if x.startswith('[X]')]))
        self.assertEqual(0, len([x for x in xs if x.startswith('[_]')]))

    def test_about(self):
        req = self.raa0121.say('#todo about')
        event = json.loads(req)['events'][0]
        s = self.bot.on_json(event)

        xs = s.text.splitlines()
        self.assertIn("It provides task management feature to lingr room.", xs)
        self.assertIn("see https://github.com/akechi/todobot", xs)

if __name__ == '__main__':
    unittest.main()

