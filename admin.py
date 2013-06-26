#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys

import json

from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool
# maybe poolclass=SingletonThreadPool
from sqlalchemy.orm import sessionmaker, scoped_session
from todo import models



if sys.argv[1] == 'dump':
    engine = create_engine('sqlite:///./todo.sqlite', poolclass=QueuePool)
    models.get_session = scoped_session(sessionmaker(bind=engine))
    for td in models.ToDo.list_all():
        print(td.to_json())


elif sys.argv[1] == 'load':
    engine = create_engine('sqlite:///:memory:', poolclass=QueuePool)
    models.get_session = scoped_session(sessionmaker(bind=engine))

    models.make_tables()
    for line in sys.stdin:
        td = models.ToDo.from_json(line)
        print(td.prnformat())

