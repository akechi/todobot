

from todo_read import ToDoBot
import unittest

from StringIO import StringIO
import sys

class ToDoBotTestCase(unittest.TestCase):
    def setUp(self):
        self.bot = ToDoBot('lion', bot_secret=None, dbpath=':memory:')
        sys.stdout = StringIO()

    def test_help(self):
        req = """{"events":[{"message":{"text":"#todo help","speaker_id":"raa0121","room":"computer_science"}}]}"""
        sys.stdin = StringIO(req)
        self.bot.serve_as_cgi(len(req))
        v = sys.stdout.getvalue()
        self.assertTrue(v.startswith('Content-type: text/html\n'))
        xs = v.splitlines()
        self.assertTrue('#todo show [id]' in xs)

    @unittest.skip('no database schema')
    def test_add(self):
        req = """{"events":[{"message":{"text":"#todo add test_add","speaker_id":"raa0121","room":"computer_science"}}]}"""
        self.bot.serve_as_cgi(len(req))
        v = sys.stdout.getvalue()
        self.assertTrue(v.startswith('Content-type: text/html\n'))
        ''' need some assertions '''

    @unittest.skip('no database schema')
    def test_addto(self):
        req = """{"events":[{"message":{"text":"#todo addto bgnori test_addto","speaker_id":"raa0121","room":"computer_science"}}]}"""
        self.bot.serve_as_cgi(len(req))
        v = sys.stdout.getvalue()
        self.assertTrue(v.startswith('Content-type: text/html\n'))
        ''' need some assertions '''

    @unittest.skip('no database schema')
    def test_list_all(self):
        req = """{"events":[{"message":{"text":"#todo list-all","speaker_id":"raa0121","room":"computer_science"}}]}"""
        self.bot.serve_as_cgi(len(req))
        v = sys.stdout.getvalue()
        self.assertTrue(v.startswith('Content-type: text/html\n'))
        ''' need some assertions '''

    @unittest.skip('no database schema')
    def test_list_done(self):
        req = """{"events":[{"message":{"text":"#todo list-done","speaker_id":"raa0121","room":"computer_science"}}]}"""
        self.bot.serve_as_cgi(len(req))
        v = sys.stdout.getvalue()
        self.assertTrue(v.startswith('Content-type: text/html\n'))
        ''' need some assertions '''

    @unittest.skip('no database schema')
    def test_list(self):
        req = """{"events":[{"message":{"text":"#todo list","speaker_id":"raa0121","room":"computer_science"}}]}"""
        self.bot.serve_as_cgi(len(req))
        v = sys.stdout.getvalue()
        self.assertTrue(v.startswith('Content-type: text/html\n'))
        ''' need some assertions '''


    @unittest.skip('no database schema')
    def test_listof_all(self):
        req = """{"events":[{"message":{"text":"#todo listof-all","speaker_id":"raa0121","room":"computer_science"}}]}"""
        self.bot.serve_as_cgi(len(req))
        v = sys.stdout.getvalue()
        self.assertTrue(v.startswith('Content-type: text/html\n'))
        ''' need some assertions '''

    @unittest.skip('no database schema')
    def test_listof_done(self):
        req = """{"events":[{"message":{"text":"#todo listof-done","speaker_id":"raa0121","room":"computer_science"}}]}"""
        self.bot.serve_as_cgi(len(req))
        v = sys.stdout.getvalue()
        self.assertTrue(v.startswith('Content-type: text/html\n'))
        ''' need some assertions '''

    @unittest.skip('no database schema')
    def test_listof(self):
        req = """{"events":[{"message":{"text":"#todo listof bgnori","speaker_id":"raa0121","room":"computer_science"}}]}"""
        self.bot.serve_as_cgi(len(req))
        v = sys.stdout.getvalue()
        self.assertTrue(v.startswith('Content-type: text/html\n'))
        ''' need some assertions '''

    @unittest.skip('no database schema')
    def test_list_everything(self):
        req = """{"events":[{"message":{"text":"#todo list-everything","speaker_id":"raa0121","room":"computer_science"}}]}"""
        self.bot.serve_as_cgi(len(req))
        v = sys.stdout.getvalue()
        self.assertTrue(v.startswith('Content-type: text/html\n'))
        ''' need some assertions '''

    @unittest.skip('no database schema')
    def test_done(self):
        req = """{"events":[{"message":{"text":"#todo done 1","speaker_id":"raa0121","room":"computer_science"}}]}"""
        self.bot.serve_as_cgi(len(req))
        v = sys.stdout.getvalue()
        self.assertTrue(v.startswith('Content-type: text/html\n'))
        ''' need some assertions '''

    @unittest.skip('no database schema')
    def test_del(self):
        req = """{"events":[{"message":{"text":"#todo del 2","speaker_id":"raa0121","room":"computer_science"}}]}"""
        self.bot.serve_as_cgi(len(req))
        v = sys.stdout.getvalue()
        self.assertTrue(v.startswith('Content-type: text/html\n'))
        ''' need some assertions '''

    @unittest.skip('no database schema')
    def test_show(self):
        req = """{"events":[{"message":{"text":"#todo show 3","speaker_id":"raa0121","room":"computer_science"}}]}"""
        self.bot.serve_as_cgi(len(req))
        v = sys.stdout.getvalue()
        self.assertTrue(v.startswith('Content-type: text/html\n'))
        ''' need some assertions '''

if __name__ == '__main__':
    unittest.main()

