

from todo import ToDoBot
import unittest

from io import StringIO
import sys

class ToDoBotTestCase(unittest.TestCase):
    def setUp(self):
        self.bot = ToDoBot('lion', bot_secret=None, dbpath=':memory:')
        c = self.bot.con.cursor()
        with open('todo_schema.sql') as f:
            c.execute(f.read())
        self.bot.con.commit()

        c.execute("insert into TODO (username, description, created_at, status) values (?, ?, datetime('now', 'localtime'), 0);", ('raa0121', str('test data 1')))
        c.execute("insert into TODO (username, description, created_at, status) values (?, ?, datetime('now', 'localtime'), 0);", ('raa0121', str('test data 2')))
        c.execute("insert into TODO (username, description, created_at, status) values (?, ?, datetime('now', 'localtime'), 1);", ('raa0121', str('test data 3')))
        c.execute("insert into TODO (username, description, created_at, status) values (?, ?, datetime('now', 'localtime'), 0);", ('bgnori', str('test data 4')))
        c.execute("insert into TODO (username, description, created_at, status) values (?, ?, datetime('now', 'localtime'), 1);", ('bgnori', str('test data 5')))
        self.bot.con.commit()

        c.execute("select * from TODO where username = ? AND status = 0", ('raa0121',))
        i = None
        for i, r in enumerate(c):
            self.assertEqual('raa0121', r[1])
        self.assertEqual(1, i)

        sys.stdout = StringIO()

    def test_get_handle_XXX(self):
        bot = self.bot
        d = dict([(k, getattr(m, "__doc__", bot.nohelp%(k,))) for k, m in bot.get_handle_XXX()])

        self.assertIn('handle_done', d)
        self.assertIn('handle_help', d)
        self.assertEqual("""#todo done [id]""", d['handle_done'])


    def test_help(self):
        req = """{"events":[{"message":{"text":"#todo help","speaker_id":"raa0121","room":"computer_science"}}]}"""
        sys.stdin = StringIO(req)
        self.bot.serve_as_cgi(len(req))
        v = sys.stdout.getvalue()
        self.assertTrue(v.startswith('Content-type: text/html\n'))
        xs = v.splitlines()
        self.assertIn('#todo done [id]', xs)
        self.assertIn('#todo show [id]', xs)

    def test_help_arg(self):
        req = """{"events":[{"message":{"text":"#todo help done","speaker_id":"raa0121","room":"computer_science"}}]}"""
        sys.stdin = StringIO(req)
        self.bot.serve_as_cgi(len(req))
        v = sys.stdout.getvalue()
        self.assertTrue(v.startswith('Content-type: text/html\n'))
        xs = v.splitlines()
        self.assertIn('#todo done [id]', xs)
        self.assertNotIn('#todo show [id]', xs)

    def test_add(self):
        req = """{"events":[{"message":{"text":"#todo add test_add","speaker_id":"raa0121","room":"computer_science"}}]}"""
        sys.stdin = StringIO(req)
        self.bot.serve_as_cgi(len(req))
        v = sys.stdout.getvalue()
        self.assertTrue(v.startswith('Content-type: text/html\n'))
        c = self.bot.con.cursor()
        c.execute("select * from TODO where username = ? AND status = 0", ('raa0121',))
        self.assertEqual(3, len([r for r in c]))


    def test_addto(self):
        req = """{"events":[{"message":{"text":"#todo addto bgnori test_addto","speaker_id":"raa0121","room":"computer_science"}}]}"""
        sys.stdin = StringIO(req)
        self.bot.serve_as_cgi(len(req))
        v = sys.stdout.getvalue()
        self.assertTrue(v.startswith('Content-type: text/html\n'))
        c = self.bot.con.cursor()
        c.execute("select * from TODO where username = ? AND status = 0", ('raa0121',))
        self.assertEqual(2, len([r for r in c]))
        c = self.bot.con.cursor()
        c.execute("select * from TODO where username = ? AND status = 0", ('bgnori',))
        self.assertEqual(2, len([r for r in c]))


    def test_list_all(self):
        req = """{"events":[{"message":{"text":"#todo list-all","speaker_id":"raa0121","room":"computer_science"}}]}"""
        sys.stdin = StringIO(req)
        self.bot.serve_as_cgi(len(req))
        v = sys.stdout.getvalue()
        self.assertTrue(v.startswith('Content-type: text/html\n'))
        xs = v.splitlines()
        self.assertEqual(2, len([x for x in xs if x.startswith('[_]')]))
        self.assertEqual(1, len([x for x in xs if x.startswith('[X]')]))


    def test_list_done(self):
        req = """{"events":[{"message":{"text":"#todo list-done","speaker_id":"raa0121","room":"computer_science"}}]}"""
        sys.stdin = StringIO(req)
        self.bot.serve_as_cgi(len(req))
        v = sys.stdout.getvalue()
        self.assertTrue(v.startswith('Content-type: text/html\n'))
        xs = v.splitlines()
        self.assertEqual(0, len([x for x in xs if x.startswith('[_]')]))
        self.assertEqual(1, len([x for x in xs if x.startswith('[X]')]))

    def test_list(self):
        req = """{"events":[{"message":{"text":"#todo list","speaker_id":"raa0121","room":"computer_science"}}]}"""
        sys.stdin = StringIO(req)
        self.bot.serve_as_cgi(len(req))
        v = sys.stdout.getvalue()
        self.assertTrue(v.startswith('Content-type: text/html\n'))
        xs = v.splitlines()
        self.assertEqual(2, len([x for x in xs if x.startswith('[_]')]))
        self.assertEqual(0, len([x for x in xs if x.startswith('[X]')]))


    def test_listof_all(self):
        req = """{"events":[{"message":{"text":"#todo listof-all bgnori","speaker_id":"raa0121","room":"computer_science"}}]}"""
        sys.stdin = StringIO(req)
        self.bot.serve_as_cgi(len(req))
        v = sys.stdout.getvalue()
        self.assertTrue(v.startswith('Content-type: text/html\n'))
        xs = v.splitlines()
        self.assertEqual(1, len([x for x in xs if x.startswith('[_]')]))



    def test_listof_done(self):
        req = """{"events":[{"message":{"text":"#todo listof-done bgnori","speaker_id":"raa0121","room":"computer_science"}}]}"""
        sys.stdin = StringIO(req)
        self.bot.serve_as_cgi(len(req))
        v = sys.stdout.getvalue()
        self.assertTrue(v.startswith('Content-type: text/html\n'))
        ''' need some assertions '''
        xs = v.splitlines()
        self.assertEqual(1, len([x for x in xs if x.startswith('[X]')]))

    def test_listof(self):
        req = """{"events":[{"message":{"text":"#todo listof bgnori","speaker_id":"raa0121","room":"computer_science"}}]}"""
        sys.stdin = StringIO(req)
        self.bot.serve_as_cgi(len(req))
        v = sys.stdout.getvalue()
        self.assertTrue(v.startswith('Content-type: text/html\n'))
        xs = v.splitlines()
        self.assertEqual(1, len([x for x in xs if x.startswith('[_]')]))


    def test_list_everything(self):
        req = """{"events":[{"message":{"text":"#todo list-everything","speaker_id":"raa0121","room":"computer_science"}}]}"""
        sys.stdin = StringIO(req)
        self.bot.serve_as_cgi(len(req))
        v = sys.stdout.getvalue()
        self.assertTrue(v.startswith('Content-type: text/html\n'))
        xs = v.splitlines()
        self.assertEqual(3, len([x for x in xs if x.startswith('[_]')]))
        self.assertEqual(2, len([x for x in xs if x.startswith('[X]')]))

    def test_done(self):
        req = """{"events":[{"message":{"text":"#todo done 1","speaker_id":"raa0121","room":"computer_science"}}]}"""
        sys.stdin = StringIO(req)
        self.bot.serve_as_cgi(len(req))
        v = sys.stdout.getvalue()
        self.assertTrue(v.startswith('Content-type: text/html\n'))
        xs = v.splitlines()
        self.assertEqual(0, len([x for x in xs if x.startswith('[_]')]))
        self.assertEqual(1, len([x for x in xs if x.startswith('[X]')]))

    def test_del(self):
        req = """{"events":[{"message":{"text":"#todo del 2","speaker_id":"raa0121","room":"computer_science"}}]}"""
        sys.stdin = StringIO(req)
        self.bot.serve_as_cgi(len(req))
        v = sys.stdout.getvalue()
        self.assertTrue(v.startswith('Content-type: text/html\n'))

        c = self.bot.con.cursor()
        c.execute("select * from TODO where username = ? AND status = 0", ('raa0121',))
        self.assertEqual(1, len([r for r in c]))
        c = self.bot.con.cursor()
        c.execute("select * from TODO where username = ? AND status = 0", ('bgnori',))
        self.assertEqual(1, len([r for r in c]))


    def test_show(self):
        req = """{"events":[{"message":{"text":"#todo show 3","speaker_id":"raa0121","room":"computer_science"}}]}"""
        sys.stdin = StringIO(req)
        self.bot.serve_as_cgi(len(req))
        v = sys.stdout.getvalue()
        self.assertTrue(v.startswith('Content-type: text/html\n'))
        ''' need some assertions '''

        xs = v.splitlines()
        self.assertEqual(1, len([x for x in xs if x.startswith('[X]')]))
        self.assertEqual(0, len([x for x in xs if x.startswith('[_]')]))

    def test_about(self):
        req = """{"events":[{"message":{"text":"#todo about","speaker_id":"raa0121","room":"computer_science"}}]}"""
        sys.stdin = StringIO(req)
        self.bot.serve_as_cgi(len(req))
        v = sys.stdout.getvalue()
        self.assertTrue(v.startswith('Content-type: text/html\n'))
        ''' need some assertions '''

        xs = v.splitlines()
        self.assertIn("It provides task management feature to lingr room.", xs)
        self.assertIn("see https://github.com/akechi/todobot", xs)

if __name__ == '__main__':
    unittest.main()

