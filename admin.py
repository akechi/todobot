#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys

import json

from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool
# maybe poolclass=SingletonThreadPool
from sqlalchemy.orm import sessionmaker, scoped_session
from todo import models



if sys.argv[1] == 'dumpfrom':
    fname = sys.argv[2]
    engine = create_engine('sqlite:///%s'%(fname,), poolclass=QueuePool)
    models.get_session = scoped_session(sessionmaker(bind=engine))
    for td in models.ToDo.list_all():
        print(td.to_json())


elif sys.argv[1] == 'loadto':
    fname = sys.argv[2]
    engine = create_engine('sqlite:///%s'%(fname), poolclass=QueuePool)
    models.get_session = scoped_session(sessionmaker(bind=engine))

    models.make_tables()
    for line in sys.stdin:
        td = models.ToDo.from_json(line)
        print(td.prnformat())

