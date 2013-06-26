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

class ToDoBotTestCase(unittest.TestCase):
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


    def test_get_handle_XXX(self):
        bot = self.bot
        d = dict([(k, getattr(m, "__doc__", bot.nohelp%(k,))) for k, m in bot.get_handle_XXX()])

        self.assertIn('handle_done', d)
        self.assertIn('handle_help', d)
        self.assertEqual(d['handle_add'], "#todo add [description]")
        self.assertEqual("""#todo done [id]""", d['handle_done'])


    def test_help(self):
        req = self.raa0121.say('#todo help')
        event = json.loads(req)['events'][0]
        s = self.bot.on_json(event)

        xs = [x for x in s.render_for_lingr(500)][0].splitlines()
        self.assertIn('#todo done [id]', xs)
        self.assertIn('#todo show [id]', xs)


    def test_help_arg(self):
        req = self.raa0121.say('#todo help done')
        event = json.loads(req)['events'][0]
        s = self.bot.on_json(event)

        xs = [x for x in s.render_for_lingr(500)][0].splitlines()
        self.assertIn('#todo done [id]', xs)
        self.assertNotIn('#todo show [id]', xs)


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

