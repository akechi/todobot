#!/usr/bin/python
# -*- coding: utf-8 -*-

import unittest

from datetime import datetime

from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker

from todo import models


J2000 = datetime(2000, 1, 1, 12, 00, 00)



class ToDoTestCase(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine('sqlite:///:memory:', poolclass=QueuePool)
        conn = self.engine.connect()
        self.conn = conn
        models.get_session = scoped_session(sessionmaker(bind=self.conn))
        models.make_tables()

        self.now = datetime(2000, 1, 3, 12, 00, 00)

    def test_sanity(self):
        td = models.ToDo(username='username', description='description', created_at=J2000, status=False)
        self.assertEqual("username", td.username)
        self.assertEqual("description", td.description)
        self.assertEqual(J2000, td.created_at)
        self.assertEqual(False, td.status)

    def test_prnformat(self):
        s = models.get_session()
        td = models.ToDo(username='username', description='description', created_at=J2000, status=False)
        s.add(td)
        s.commit()

        x = td.prnformat(self.now)
        self.assertEqual('[_] 0001 username 2日前 description', x)

        s = models.get_session()
        td2 = models.ToDo(username='username', description='description', created_at=J2000, status=True)
        s.add(td2)
        s.commit()

        y = td2.prnformat(self.now)
        self.assertEqual('[X] 0002 username 2日前 description', y)


    def test_add(self):
        td = models.ToDo.add(username='username', description='description', created_at=J2000, status=True)

        y = td.prnformat(self.now)
        self.assertEqual('[X] 0001 username 2日前 description', y)

    def test_get(self):
        models.ToDo.add(username='username', description='description', created_at=J2000, status=True)

        s = models.get_session()
        td = models.ToDo.get(1)

        y = td.prnformat(self.now)
        self.assertEqual('[X] 0001 username 2日前 description', y)

    def test_done(self):
        td = models.ToDo.add(username='username', description='description', created_at=J2000, status=False)
        td.done()

        y = td.prnformat(self.now)
        self.assertEqual('[X] 0001 username 2日前 description', y)

    def test_delete(self):
        td = models.ToDo.add(username='username', description='description', created_at=J2000, status=False)
        td.delete()

        self.assertIsNone(models.ToDo.get(1))

    def test_list_whose_no_kw(self):
        models.ToDo.add(username='username', description='task 1', created_at=J2000, status=False)
        models.ToDo.add(username='username', description='task 2', created_at=J2000, status=False)
        models.ToDo.add(username='username', description='task 3', created_at=J2000, status=True)
        models.ToDo.add(username='username2', description='description', created_at=J2000, status=False)

        xs = models.ToDo.list_whose('username')
        ys = [x.description for x in xs]

        self.assertIn('task 1', ys)
        self.assertIn('task 2', ys)
        self.assertIn('task 3', ys)
        self.assertNotIn('description', ys)

    def test_list_whose_status_True(self):
        models.ToDo.add(username='username', description='task 1', created_at=J2000, status=False)
        models.ToDo.add(username='username', description='task 2', created_at=J2000, status=False)
        models.ToDo.add(username='username', description='task 3', created_at=J2000, status=True)
        models.ToDo.add(username='username2', description='description', created_at=J2000, status=False)

        xs = models.ToDo.list_whose('username', status=True)
        ys = [x.description for x in xs]

        self.assertNotIn('task 1', ys)
        self.assertNotIn('task 2', ys)
        self.assertIn('task 3', ys)
        self.assertNotIn('description', ys)

    def test_list_whose_status_False(self):
        models.ToDo.add(username='username', description='task 1', created_at=J2000, status=False)
        models.ToDo.add(username='username', description='task 2', created_at=J2000, status=False)
        models.ToDo.add(username='username', description='task 3', created_at=J2000, status=True)
        models.ToDo.add(username='username2', description='description', created_at=J2000, status=False)

        xs = models.ToDo.list_whose('username', status=False)
        ys = [x.description for x in xs]

        self.assertIn('task 1', ys)
        self.assertIn('task 2', ys)
        self.assertNotIn('task 3', ys)
        self.assertNotIn('description', ys)

    def test_list_all(self):
        models.ToDo.add(username='username', description='task 1', created_at=J2000, status=False)
        models.ToDo.add(username='username', description='task 2', created_at=J2000, status=False)
        models.ToDo.add(username='username', description='task 3', created_at=J2000, status=True)
        models.ToDo.add(username='username2', description='description', created_at=J2000, status=False)

        xs = models.ToDo.list_all()
        ys = [x.description for x in xs]

        self.assertIn('task 1', ys)
        self.assertIn('task 2', ys)
        self.assertIn('task 3', ys)
        self.assertIn('description', ys)

    def test_edit(self):
        td = models.ToDo.add(username='username', description='description', created_at=J2000, status=True)
        td = td.edit(description='yet another description')

        y = td.prnformat(self.now)
        self.assertEqual('[X] 0001 username 2日前 yet another description', y)


if __name__ == '__main__':
    unittest.main()


