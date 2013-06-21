

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


if __name__ == '__main__':
    unittest.main()

