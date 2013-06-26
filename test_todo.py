

from todo.lingrbot import ToDoBot, Postman 
from todo import models
import unittest

import json

from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker

from datetime import datetime

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


    def tearDown(self):
        self.engine.dispose()


    def test_get_handle_XXX(self):
        bot = self.bot
        d = dict([(k, getattr(m, "__doc__", bot.nohelp%(k,))) for k, m in bot.get_handle_XXX()])

        self.assertIn('handle_done', d)
        self.assertIn('handle_help', d)
        self.assertEqual("""#todo done [id]""", d['handle_done'])


    def test_help(self):
        req = """{"events":[{"message":{"text":"#todo help","speaker_id":"raa0121","room":"computer_science"}}]}"""
        event = json.loads(req)['events'][0]
        s = self.bot.on_json(event)

        xs = s.text.splitlines()
        self.assertIn('#todo done [id]', xs)
        self.assertIn('#todo show [id]', xs)


    def test_help_arg(self):
        req = """{"events":[{"message":{"text":"#todo help done","speaker_id":"raa0121","room":"computer_science"}}]}"""
        event = json.loads(req)['events'][0]
        s = self.bot.on_json(event)

        xs = s.text.splitlines()
        self.assertIn('#todo done [id]', xs)
        self.assertNotIn('#todo show [id]', xs)

    def test_add(self):
        req = """{"events":[{"message":{"text":"#todo add test_add","speaker_id":"raa0121","room":"computer_science"}}]}"""
        event = json.loads(req)['events'][0]
        s = self.bot.on_json(event)

        #conn = self.conn
        conn = self.conn
        result = conn.execute("select * from TODO where username = ? AND status = 0", ('raa0121',))
        self.assertEqual(3, len([r for r in result]))


    def test_addto(self):
        req = """{"events":[{"message":{"text":"#todo addto bgnori test_addto","speaker_id":"raa0121","room":"computer_science"}}]}"""
        event = json.loads(req)['events'][0]
        s = self.bot.on_json(event)

        conn = self.conn
        result = conn.execute("select * from TODO where username = ? AND status = 0", ('raa0121',))
        self.assertEqual(2, len([r for r in result]))
        result = conn.execute("select * from TODO where username = ? AND status = 0", ('bgnori',))
        self.assertEqual(2, len([r for r in result]))


    def test_list_all(self):
        req = """{"events":[{"message":{"text":"#todo list-all","speaker_id":"raa0121","room":"computer_science"}}]}"""
        event = json.loads(req)['events'][0]
        s = self.bot.on_json(event)

        xs = [r.prnformat() for r in s.rows]
        self.assertEqual(2, len([x for x in xs if x.startswith('[_]')]))
        self.assertEqual(1, len([x for x in xs if x.startswith('[X]')]))


    def test_list_done(self):
        req = """{"events":[{"message":{"text":"#todo list-done","speaker_id":"raa0121","room":"computer_science"}}]}"""
        event = json.loads(req)['events'][0]
        s = self.bot.on_json(event)

        xs = [r.prnformat() for r in s.rows]
        self.assertEqual(0, len([x for x in xs if x.startswith('[_]')]))
        self.assertEqual(1, len([x for x in xs if x.startswith('[X]')]))

    def test_list(self):
        req = """{"events":[{"message":{"text":"#todo list","speaker_id":"raa0121","room":"computer_science"}}]}"""
        event = json.loads(req)['events'][0]
        s = self.bot.on_json(event)

        xs = [r.prnformat() for r in s.rows]
        self.assertEqual(2, len([x for x in xs if x.startswith('[_]')]))
        self.assertEqual(0, len([x for x in xs if x.startswith('[X]')]))


    def test_listof_all(self):
        req = """{"events":[{"message":{"text":"#todo listof-all bgnori","speaker_id":"raa0121","room":"computer_science"}}]}"""
        event = json.loads(req)['events'][0]
        s = self.bot.on_json(event)

        xs = [r.prnformat() for r in s.rows]
        self.assertEqual(1, len([x for x in xs if x.startswith('[_]')]))



    def test_listof_done(self):
        req = """{"events":[{"message":{"text":"#todo listof-done bgnori","speaker_id":"raa0121","room":"computer_science"}}]}"""
        event = json.loads(req)['events'][0]
        s = self.bot.on_json(event)

        xs = [r.prnformat() for r in s.rows]
        self.assertEqual(1, len([x for x in xs if x.startswith('[X]')]))

    def test_listof(self):
        req = """{"events":[{"message":{"text":"#todo listof bgnori","speaker_id":"raa0121","room":"computer_science"}}]}"""
        event = json.loads(req)['events'][0]
        s = self.bot.on_json(event)

        xs = [r.prnformat() for r in s.rows]
        self.assertEqual(1, len([x for x in xs if x.startswith('[_]')]))


    def test_list_everything(self):
        req = """{"events":[{"message":{"text":"#todo list-everything","speaker_id":"raa0121","room":"computer_science"}}]}"""
        event = json.loads(req)['events'][0]
        s = self.bot.on_json(event)

        xs = [r.prnformat() for r in s.rows]
        self.assertEqual(3, len([x for x in xs if x.startswith('[_]')]))
        self.assertEqual(2, len([x for x in xs if x.startswith('[X]')]))

    def test_done(self):
        req = """{"events":[{"message":{"text":"#todo done 1","speaker_id":"raa0121","room":"computer_science"}}]}"""
        event = json.loads(req)['events'][0]
        s = self.bot.on_json(event)


        conn = self.conn
        result = conn.execute("select * from TODO where username = ? AND status = 1", ('raa0121',))
        self.assertEqual(2, len([r for r in result]))


        self.assertTrue(s.text.startswith('[X]'))


    def test_del(self):
        req = """{"events":[{"message":{"text":"#todo del 2","speaker_id":"raa0121","room":"computer_science"}}]}"""
        event = json.loads(req)['events'][0]
        s = self.bot.on_json(event)


        conn = self.conn
        result = conn.execute("select * from TODO where username = ? AND status = 0", ('raa0121',))
        self.assertEqual(1, len([r for r in result]))
        result = conn.execute("select * from TODO where username = ? AND status = 0", ('bgnori',))
        self.assertEqual(1, len([r for r in result]))


    def test_show(self):
        req = """{"events":[{"message":{"text":"#todo show 3","speaker_id":"raa0121","room":"computer_science"}}]}"""
        event = json.loads(req)['events'][0]
        s = self.bot.on_json(event)

        xs = [r.prnformat() for r in s.rows]
        self.assertEqual(1, len([x for x in xs if x.startswith('[X]')]))
        self.assertEqual(0, len([x for x in xs if x.startswith('[_]')]))

    def test_about(self):
        req = """{"events":[{"message":{"text":"#todo about","speaker_id":"raa0121","room":"computer_science"}}]}"""
        event = json.loads(req)['events'][0]
        s = self.bot.on_json(event)

        xs = s.text.splitlines()
        self.assertIn("It provides task management feature to lingr room.", xs)
        self.assertIn("see https://github.com/akechi/todobot", xs)

if __name__ == '__main__':
    unittest.main()

